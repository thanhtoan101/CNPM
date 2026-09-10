"""Kiểm thử bộ gợi ý Film Lab bằng thư viện chuẩn unittest."""

from __future__ import annotations

import unittest

from ai_service.recommendation import (
    FilmLab,
    RecommendationQuery,
    RecommendationValidationError,
    load_film_labs,
    recommend_film_labs,
)


class FilmLabRecommendationTests(unittest.TestCase):
    def test_ranking_prefers_best_location_and_turnaround_fit(self) -> None:
        query = RecommendationQuery(
            film_format="35MM",
            required_services=("develop", "scan"),
            preferred_services=("high_res_scan",),
            city="Ho Chi Minh",
            district="Quan 3",
            budget_vnd=200_000,
            max_turnaround_hours=24,
        )

        results = recommend_film_labs(query, top_k=3)

        self.assertEqual(results[0].lab.lab_id, "retrocam-lab")
        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(results[0].score, results[1].score)
        self.assertGreaterEqual(results[1].score, results[2].score)

    def test_format_and_required_services_are_hard_constraints(self) -> None:
        four_by_five = recommend_film_labs(
            RecommendationQuery(
                film_format="sheet_4x5",
                required_services=("develop", "scan"),
            ),
            top_k=10,
        )
        unavailable_service = recommend_film_labs(
            RecommendationQuery(
                film_format="35mm",
                required_services=("develop", "drum_scan"),
            ),
            top_k=10,
        )

        self.assertEqual(
            [result.lab.lab_id for result in four_by_five], ["hanoi-film-lab"]
        )
        self.assertEqual(unavailable_service, [])

    def test_common_service_labels_are_normalised(self) -> None:
        results = recommend_film_labs(
            RecommendationQuery(
                film_format="35mm",
                required_services=("developing", "scanning"),
            )
        )

        self.assertTrue(results)
        self.assertTrue(
            all(
                {"develop", "scan"}.issubset(set(result.lab.services))
                for result in results
            )
        )

    def test_location_aliases_and_vietnamese_d_are_normalised(self) -> None:
        hcm = recommend_film_labs(
            RecommendationQuery(
                film_format="120",
                required_services=("develop", "scan"),
                city="TP. Hồ Chí Minh",
                district="Q.3",
            ),
            top_k=1,
        )
        danang = recommend_film_labs(
            RecommendationQuery(
                film_format="35mm",
                required_services=("develop", "scan"),
                city="Da Nang",
            ),
            top_k=1,
        )

        self.assertEqual("retrocam-lab", hcm[0].lab.lab_id)
        self.assertEqual("danang-analog", danang[0].lab.lab_id)

    def test_scores_remain_normalized_with_custom_weights(self) -> None:
        weights = {factor: 1.0 for factor in (
            "format", "services", "location", "budget", "turnaround", "rating"
        )}
        results = recommend_film_labs(
            RecommendationQuery("35mm", ("develop", "scan")),
            weights=weights,
            top_k=10,
        )

        self.assertTrue(results)
        self.assertTrue(all(0.0 <= result.score <= 1.0 for result in results))

    def test_optional_strict_constraints_remove_over_limit_labs(self) -> None:
        results = recommend_film_labs(
            RecommendationQuery(
                film_format="35mm",
                required_services=("develop", "scan"),
                budget_vnd=145_000,
                max_turnaround_hours=48,
                minimum_rating=4.5,
                strict_budget=True,
                strict_turnaround=True,
            ),
            top_k=10,
        )

        self.assertEqual(
            {result.lab.lab_id for result in results}, {"danang-analog"}
        )

    def test_result_contains_complete_explanation_and_is_json_ready(self) -> None:
        result = recommend_film_labs(
            {
                "film_format": "35mm",
                "required_services": ("develop", "scan"),
                "city": "Hồ Chí Minh",
                "budget_vnd": 170_000,
                "max_turnaround_hours": 48,
            },
            top_k=1,
        )[0]
        serialised = result.to_dict()

        expected_factors = {
            "format",
            "services",
            "location",
            "budget",
            "turnaround",
            "rating",
        }
        self.assertEqual(set(result.factor_scores), expected_factors)
        self.assertEqual(set(result.weighted_scores), expected_factors)
        self.assertAlmostEqual(
            result.score, sum(result.weighted_scores.values()), places=3
        )
        self.assertTrue(any("dịch vụ" in reason for reason in result.reasons))
        self.assertTrue(any("VND" in reason for reason in result.reasons))
        self.assertIsInstance(serialised["lab"]["services"], list)
        self.assertIsInstance(serialised["reasons"], list)

    def test_loading_seed_catalogue_is_deterministic(self) -> None:
        first = load_film_labs()
        second = load_film_labs()

        self.assertEqual(first, second)
        self.assertGreaterEqual(len(first), 5)

    def test_invalid_queries_and_configuration_raise_clear_errors(self) -> None:
        invalid_factories = (
            lambda: RecommendationQuery("", ("scan",)),
            lambda: RecommendationQuery("35mm", ()),
            lambda: RecommendationQuery.from_mapping(
                {"film_format": "35mm", "required_services": {"scan": True}}
            ),
            lambda: RecommendationQuery("35mm", ("scan",), budget_vnd=0),
            lambda: RecommendationQuery("35mm", ("scan",), minimum_rating=5.1),
            lambda: RecommendationQuery("35mm", ("scan",), strict_budget=True),
            lambda: recommend_film_labs(
                RecommendationQuery("35mm", ("scan",)), top_k=0
            ),
            lambda: recommend_film_labs(
                RecommendationQuery("35mm", ("scan",)),
                weights={"rating": 1.0},
            ),
        )

        for factory in invalid_factories:
            with self.subTest(factory=factory):
                with self.assertRaises(RecommendationValidationError):
                    factory()

    def test_invalid_lab_data_is_rejected(self) -> None:
        with self.assertRaises(RecommendationValidationError):
            FilmLab(
                lab_id="bad-lab",
                name="Bad Lab",
                city="Hà Nội",
                district="Ba Đình",
                formats=("35mm",),
                services=("scan",),
                base_price_vnd=-1,
                turnaround_hours=24,
                rating=4.0,
            )

        malformed_mapping = {
            "id": "bad-list",
            "name": "Bad List Lab",
            "city": "Hà Nội",
            "district": "Ba Đình",
            "formats": "35mm",
            "services": ["scan"],
            "base_price_vnd": 100_000,
            "turnaround_hours": 24,
            "rating": 4.0,
        }
        with self.assertRaises(RecommendationValidationError):
            FilmLab.from_mapping(malformed_mapping)

    def test_duplicate_lab_identifiers_are_rejected(self) -> None:
        lab = load_film_labs()[0]
        with self.assertRaises(RecommendationValidationError):
            recommend_film_labs(
                RecommendationQuery("35mm", ("scan",)),
                labs=(lab, lab),
            )


if __name__ == "__main__":
    unittest.main()
