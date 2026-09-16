"""Tests for deterministic baseline metric calculation and fixtures."""

from __future__ import annotations

import math
import unittest

from ai_service.evaluation import (
    evaluate_baselines,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class RankingMetricTests(unittest.TestCase):
    def test_binary_ranking_metrics_match_hand_calculation(self) -> None:
        ranked = ("a", "x", "b", "y")
        relevant = ("a", "b")

        self.assertAlmostEqual(2 / 3, precision_at_k(ranked, relevant, 3))
        self.assertAlmostEqual(1.0, recall_at_k(ranked, relevant, 3))
        self.assertAlmostEqual(1.0, reciprocal_rank(ranked, relevant))
        expected_dcg = 1.0 + (1.0 / math.log2(4))
        expected_ideal = 1.0 + (1.0 / math.log2(3))
        self.assertAlmostEqual(expected_dcg / expected_ideal, ndcg_at_k(ranked, relevant, 3))

    def test_metrics_reject_invalid_inputs(self) -> None:
        calls = [
            lambda: precision_at_k([], ["a"], 1),
            lambda: recall_at_k(["a"], [], 1),
            lambda: reciprocal_rank(["a", "a"], ["a"]),
            lambda: ndcg_at_k(["a"], ["a"], 0),
        ]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises(ValueError):
                    call()

    def test_bundled_evaluation_is_json_ready_and_explicitly_non_production(self) -> None:
        report = evaluate_baselines(k=3)

        self.assertFalse(report["production_claim"])
        self.assertEqual(2, len(report["results"]))
        components = {item["component"] for item in report["results"]}
        self.assertEqual({"recommendation", "retrieval"}, components)
        for result in report["results"]:
            self.assertGreater(result["case_count"], 0)
            for field in (
                "precision_at_k",
                "recall_at_k",
                "mean_reciprocal_rank",
                "ndcg_at_k",
            ):
                self.assertGreaterEqual(result[field], 0.0)
                self.assertLessEqual(result[field], 1.0)


if __name__ == "__main__":
    unittest.main()
