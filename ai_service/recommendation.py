"""Bộ gợi ý Film Lab có thể giải thích, chạy hoàn toàn ngoại tuyến.

Thuật toán dùng sáu nhóm tiêu chí đã nêu trong đề tài: định dạng phim,
dịch vụ, vị trí, ngân sách, thời gian xử lý và điểm đánh giá. Định dạng
phim cùng các dịch vụ bắt buộc được dùng làm điều kiện lọc cứng trước khi
tính điểm; các giới hạn ngân sách và thời gian có thể được chuyển thành
điều kiện lọc cứng bằng hai cờ tương ứng.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence
import unicodedata


SCORING_FACTORS = (
    "format",
    "services",
    "location",
    "budget",
    "turnaround",
    "rating",
)

DEFAULT_WEIGHTS: dict[str, float] = {
    "format": 0.18,
    "services": 0.22,
    "location": 0.16,
    "budget": 0.16,
    "turnaround": 0.14,
    "rating": 0.14,
}

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "film_labs.json"


class RecommendationValidationError(ValueError):
    """Đầu vào truy vấn, dữ liệu Film Lab hoặc trọng số không hợp lệ."""


def _normalise(value: str) -> str:
    """Chuẩn hoá chuỗi để so khớp không phân biệt hoa, dấu và khoảng trắng."""

    vietnamese_ascii = value.strip().replace("Đ", "D").replace("đ", "d")
    decomposed = unicodedata.normalize("NFKD", vietnamese_ascii)
    without_marks = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(without_marks.casefold().split())


_SERVICE_ALIASES = {
    "develop": "develop",
    "developing": "develop",
    "film developing": "develop",
    "trang phim": "develop",
    "scan": "scan",
    "scanning": "scan",
    "film scanning": "scan",
    "quet phim": "scan",
    "print": "print",
    "printing": "print",
    "photo printing": "print",
    "in anh": "print",
}


def _normalise_service(value: str) -> str:
    """Map common Vietnamese/English labels to stable service identifiers."""

    normalised = _normalise(value)
    return _SERVICE_ALIASES.get(normalised, normalised.replace(" ", "_"))


_LOCATION_ALIASES = {
    "hcm": "ho chi minh",
    "hcmc": "ho chi minh",
    "sai gon": "ho chi minh",
    "thanh pho ho chi minh": "ho chi minh",
    "tp hcm": "ho chi minh",
    "tp ho chi minh": "ho chi minh",
    "hn": "ha noi",
    "thanh pho ha noi": "ha noi",
    "tp ha noi": "ha noi",
    "dn": "da nang",
    "thanh pho da nang": "da nang",
    "tp da nang": "da nang",
}


def _normalise_location(value: str) -> str:
    normalised = re.sub(r"[^a-z0-9\s]", " ", _normalise(value))
    normalised = " ".join(normalised.split())
    district = re.fullmatch(r"q(?:uan)?\s*(\d+)", normalised)
    if district:
        return f"quan {district.group(1)}"
    return _LOCATION_ALIASES.get(normalised, normalised)


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecommendationValidationError(
            f"{field_name} phải là chuỗi không rỗng."
        )
    return value.strip()


def _normalised_unique_strings(
    values: Iterable[str], field_name: str, *, allow_empty: bool
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes, Mapping)):
        raise RecommendationValidationError(
            f"{field_name} phải là một danh sách chuỗi, không phải một chuỗi đơn."
        )

    try:
        raw_values = tuple(values)
    except TypeError as exc:
        raise RecommendationValidationError(
            f"{field_name} phải là một danh sách chuỗi."
        ) from exc

    result: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        cleaned = _require_text(raw_value, field_name)
        key = _normalise(cleaned)
        if key not in seen:
            seen.add(key)
            result.append(cleaned)

    if not result and not allow_empty:
        raise RecommendationValidationError(
            f"{field_name} phải có ít nhất một giá trị."
        )
    return tuple(result)


def _positive_number(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RecommendationValidationError(f"{field_name} phải là một số dương.")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise RecommendationValidationError(f"{field_name} phải là một số dương.")
    return number


@dataclass(frozen=True)
class FilmLab:
    """Thông tin tối thiểu của một Film Lab dùng trong bộ gợi ý."""

    lab_id: str
    name: str
    city: str
    district: str
    formats: tuple[str, ...]
    services: tuple[str, ...]
    base_price_vnd: int
    turnaround_hours: int
    rating: float
    review_count: int = 0
    is_synthetic: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "lab_id", _require_text(self.lab_id, "lab_id"))
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        object.__setattr__(self, "city", _require_text(self.city, "city"))
        object.__setattr__(self, "district", _require_text(self.district, "district"))
        object.__setattr__(
            self,
            "formats",
            _normalised_unique_strings(self.formats, "formats", allow_empty=False),
        )
        object.__setattr__(
            self,
            "services",
            _normalised_unique_strings(self.services, "services", allow_empty=False),
        )

        price = _positive_number(self.base_price_vnd, "base_price_vnd")
        turnaround = _positive_number(self.turnaround_hours, "turnaround_hours")
        if not price.is_integer() or not turnaround.is_integer():
            raise RecommendationValidationError(
                "base_price_vnd và turnaround_hours phải là số nguyên dương."
            )
        object.__setattr__(self, "base_price_vnd", int(price))
        object.__setattr__(self, "turnaround_hours", int(turnaround))

        if isinstance(self.rating, bool) or not isinstance(self.rating, (int, float)):
            raise RecommendationValidationError("rating phải là số từ 0 đến 5.")
        rating = float(self.rating)
        if not math.isfinite(rating) or not 0 <= rating <= 5:
            raise RecommendationValidationError("rating phải là số từ 0 đến 5.")
        object.__setattr__(self, "rating", rating)

        if (
            isinstance(self.review_count, bool)
            or not isinstance(self.review_count, int)
            or self.review_count < 0
        ):
            raise RecommendationValidationError(
                "review_count phải là số nguyên không âm."
            )
        if not isinstance(self.is_synthetic, bool):
            raise RecommendationValidationError("is_synthetic phải là boolean.")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FilmLab":
        """Tạo ``FilmLab`` từ dữ liệu JSON và báo lỗi rõ khi thiếu trường."""

        if not isinstance(value, Mapping):
            raise RecommendationValidationError("Mỗi Film Lab phải là một object.")
        try:
            return cls(
                lab_id=value["id"],
                name=value["name"],
                city=value["city"],
                district=value["district"],
                formats=value["formats"],
                services=value["services"],
                base_price_vnd=value["base_price_vnd"],
                turnaround_hours=value["turnaround_hours"],
                rating=value["rating"],
                review_count=value.get("review_count", 0),
                is_synthetic=value.get("is_synthetic", False),
            )
        except KeyError as exc:
            raise RecommendationValidationError(
                f"Film Lab thiếu trường bắt buộc: {exc.args[0]}."
            ) from exc
        except (TypeError, ValueError) as exc:
            if isinstance(exc, RecommendationValidationError):
                raise
            raise RecommendationValidationError(
                "formats và services của Film Lab phải là danh sách."
            ) from exc


@dataclass(frozen=True)
class RecommendationQuery:
    """Tiêu chí tìm Film Lab của khách hàng.

    ``film_format`` và ``required_services`` luôn là điều kiện lọc cứng.
    ``preferred_services`` chỉ góp phần xếp hạng. ``strict_budget`` và
    ``strict_turnaround`` cho phép biến hai ngưỡng tương ứng thành điều kiện
    lọc cứng; mặc định chúng vẫn là tiêu chí mềm để không làm mất hết kết quả.
    ``budget_vnd`` so với giá cơ bản trong catalogue, không phải báo giá cuối
    cho một tổ hợp nhiều dịch vụ.
    """

    film_format: str
    required_services: tuple[str, ...]
    preferred_services: tuple[str, ...] = ()
    city: str | None = None
    district: str | None = None
    budget_vnd: int | None = None
    max_turnaround_hours: int | None = None
    minimum_rating: float | None = None
    strict_budget: bool = False
    strict_turnaround: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "film_format", _require_text(self.film_format, "film_format")
        )
        object.__setattr__(
            self,
            "required_services",
            _normalised_unique_strings(
                self.required_services, "required_services", allow_empty=False
            ),
        )
        object.__setattr__(
            self,
            "preferred_services",
            _normalised_unique_strings(
                self.preferred_services, "preferred_services", allow_empty=True
            ),
        )

        if self.city is not None:
            object.__setattr__(self, "city", _require_text(self.city, "city"))
        if self.district is not None:
            object.__setattr__(
                self, "district", _require_text(self.district, "district")
            )

        if self.budget_vnd is not None:
            budget = _positive_number(self.budget_vnd, "budget_vnd")
            if not budget.is_integer():
                raise RecommendationValidationError("budget_vnd phải là số nguyên dương.")
            object.__setattr__(self, "budget_vnd", int(budget))

        if self.max_turnaround_hours is not None:
            turnaround = _positive_number(
                self.max_turnaround_hours, "max_turnaround_hours"
            )
            if not turnaround.is_integer():
                raise RecommendationValidationError(
                    "max_turnaround_hours phải là số nguyên dương."
                )
            object.__setattr__(self, "max_turnaround_hours", int(turnaround))

        if self.minimum_rating is not None:
            if isinstance(self.minimum_rating, bool) or not isinstance(
                self.minimum_rating, (int, float)
            ):
                raise RecommendationValidationError(
                    "minimum_rating phải là số từ 0 đến 5."
                )
            minimum_rating = float(self.minimum_rating)
            if not math.isfinite(minimum_rating) or not 0 <= minimum_rating <= 5:
                raise RecommendationValidationError(
                    "minimum_rating phải là số từ 0 đến 5."
                )
            object.__setattr__(self, "minimum_rating", minimum_rating)

        if not isinstance(self.strict_budget, bool) or not isinstance(
            self.strict_turnaround, bool
        ):
            raise RecommendationValidationError(
                "strict_budget và strict_turnaround phải là boolean."
            )
        if self.strict_budget and self.budget_vnd is None:
            raise RecommendationValidationError(
                "strict_budget chỉ dùng được khi có budget_vnd."
            )
        if self.strict_turnaround and self.max_turnaround_hours is None:
            raise RecommendationValidationError(
                "strict_turnaround chỉ dùng được khi có max_turnaround_hours."
            )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RecommendationQuery":
        if not isinstance(value, Mapping):
            raise RecommendationValidationError("query phải là một object.")
        try:
            return cls(**dict(value))
        except TypeError as exc:
            raise RecommendationValidationError(
                f"Cấu trúc query không hợp lệ: {exc}."
            ) from exc


@dataclass(frozen=True)
class RecommendationResult:
    """Một kết quả đã xếp hạng cùng bằng chứng giải thích điểm số."""

    lab: FilmLab
    score: float
    factor_scores: dict[str, float]
    weighted_scores: dict[str, float]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Chuyển kết quả thành cấu trúc có thể mã hoá JSON trực tiếp."""

        return {
            "lab": {
                "id": self.lab.lab_id,
                "name": self.lab.name,
                "city": self.lab.city,
                "district": self.lab.district,
                "formats": list(self.lab.formats),
                "services": list(self.lab.services),
                "base_price_vnd": self.lab.base_price_vnd,
                "turnaround_hours": self.lab.turnaround_hours,
                "rating": self.lab.rating,
                "review_count": self.lab.review_count,
                "is_synthetic": self.lab.is_synthetic,
            },
            "score": self.score,
            "factor_scores": dict(self.factor_scores),
            "weighted_scores": dict(self.weighted_scores),
            "reasons": list(self.reasons),
        }


def load_film_labs(path: str | Path | None = None) -> tuple[FilmLab, ...]:
    """Đọc và kiểm tra danh mục Film Lab từ tệp JSON."""

    data_path = Path(path) if path is not None else DEFAULT_DATA_PATH
    try:
        with data_path.open("r", encoding="utf-8") as source:
            payload = json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise RecommendationValidationError(
            f"Không thể đọc dữ liệu Film Lab tại {data_path}: {exc}."
        ) from exc

    if not isinstance(payload, list):
        raise RecommendationValidationError("Tệp Film Lab phải chứa một danh sách.")

    labs = tuple(FilmLab.from_mapping(item) for item in payload)
    identifiers = [_normalise(lab.lab_id) for lab in labs]
    if len(identifiers) != len(set(identifiers)):
        raise RecommendationValidationError("Mã Film Lab không được trùng nhau.")
    return labs


def _normalised_weights(weights: Mapping[str, float] | None) -> dict[str, float]:
    raw = DEFAULT_WEIGHTS if weights is None else weights
    if not isinstance(raw, Mapping) or set(raw) != set(SCORING_FACTORS):
        raise RecommendationValidationError(
            "weights phải chứa đúng sáu tiêu chí: " + ", ".join(SCORING_FACTORS) + "."
        )

    cleaned: dict[str, float] = {}
    for factor in SCORING_FACTORS:
        value = raw[factor]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise RecommendationValidationError(
                f"Trọng số {factor} phải là số không âm."
            )
        number = float(value)
        if not math.isfinite(number) or number < 0:
            raise RecommendationValidationError(
                f"Trọng số {factor} phải là số không âm."
            )
        cleaned[factor] = number

    total = sum(cleaned.values())
    if total <= 0:
        raise RecommendationValidationError("Tổng trọng số phải lớn hơn 0.")
    return {factor: value / total for factor, value in cleaned.items()}


def _threshold_score(actual: int, target: int | None) -> float:
    """Điểm mềm quanh một ngưỡng: đạt ngưỡng được >= 0.8, vượt ngưỡng giảm dần."""

    if target is None:
        return 0.5
    ratio = actual / target
    if ratio <= 1:
        return 0.8 + 0.2 * (1 - ratio)
    return max(0.0, 0.8 * (2 - ratio))


def _location_score(lab: FilmLab, query: RecommendationQuery) -> float:
    if query.city is None and query.district is None:
        return 0.5

    city_matches = query.city is None or _normalise_location(
        lab.city
    ) == _normalise_location(query.city)
    district_matches = query.district is None or _normalise_location(
        lab.district
    ) == _normalise_location(query.district)
    if city_matches and district_matches:
        return 1.0
    if query.city is not None and city_matches:
        return 0.7
    if query.city is None and district_matches:
        return 1.0
    return 0.0


def _service_score(lab: FilmLab, query: RecommendationQuery) -> float:
    requested = {
        _normalise_service(service)
        for service in (*query.required_services, *query.preferred_services)
    }
    available = {_normalise_service(service) for service in lab.services}
    return len(requested & available) / len(requested)


def _is_eligible(lab: FilmLab, query: RecommendationQuery) -> bool:
    formats = {_normalise(film_format) for film_format in lab.formats}
    services = {_normalise_service(service) for service in lab.services}
    if _normalise(query.film_format) not in formats:
        return False
    if not {_normalise_service(service) for service in query.required_services} <= services:
        return False
    if query.minimum_rating is not None and lab.rating < query.minimum_rating:
        return False
    if query.strict_budget and lab.base_price_vnd > query.budget_vnd:
        return False
    if query.strict_turnaround and lab.turnaround_hours > query.max_turnaround_hours:
        return False
    return True


def _explain(
    lab: FilmLab, query: RecommendationQuery, factor_scores: Mapping[str, float]
) -> tuple[str, ...]:
    reasons = [
        f"Hỗ trợ định dạng {query.film_format} và toàn bộ dịch vụ bắt buộc.",
        (
            f"Mức phù hợp dịch vụ đạt {factor_scores['services'] * 100:.0f}%"
            " (tính cả dịch vụ ưu tiên)."
        ),
    ]
    if query.city is not None or query.district is not None:
        if factor_scores["location"] == 1:
            reasons.append(f"Vị trí phù hợp: {lab.district}, {lab.city}.")
        elif factor_scores["location"] > 0:
            reasons.append(f"Cùng thành phố, khác khu vực: {lab.district}, {lab.city}.")
        else:
            reasons.append(f"Vị trí khác lựa chọn: {lab.district}, {lab.city}.")
    if query.budget_vnd is not None:
        status = "trong" if lab.base_price_vnd <= query.budget_vnd else "vượt"
        reasons.append(
            f"Giá cơ bản {lab.base_price_vnd:,} VND {status} ngưỡng tham khảo "
            f"{query.budget_vnd:,} VND; cần báo giá đơn hàng cuối."
        )
    if query.max_turnaround_hours is not None:
        status = "đạt" if lab.turnaround_hours <= query.max_turnaround_hours else "chậm hơn"
        reasons.append(
            f"Thời gian xử lý {lab.turnaround_hours} giờ, {status} mốc "
            f"{query.max_turnaround_hours} giờ."
        )
    reasons.append(f"Điểm cộng đồng {lab.rating:.1f}/5 từ {lab.review_count} đánh giá.")
    return tuple(reasons)


def recommend_film_labs(
    query: RecommendationQuery | Mapping[str, Any],
    *,
    labs: Sequence[FilmLab | Mapping[str, Any]] | None = None,
    top_k: int = 3,
    weights: Mapping[str, float] | None = None,
) -> list[RecommendationResult]:
    """Lọc, chấm điểm và trả tối đa ``top_k`` Film Lab tốt nhất.

    Việc phá hoà luôn cố định theo: điểm tổng, rating, số lượt đánh giá, giá,
    rồi tên và mã Lab. Vì vậy cùng một đầu vào luôn cho cùng một thứ tự.
    """

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
        raise RecommendationValidationError("top_k phải là số nguyên dương.")
    if isinstance(query, Mapping):
        query = RecommendationQuery.from_mapping(query)
    if not isinstance(query, RecommendationQuery):
        raise RecommendationValidationError(
            "query phải là RecommendationQuery hoặc một object tương ứng."
        )

    scoring_weights = _normalised_weights(weights)
    if labs is None:
        lab_catalogue = load_film_labs()
    else:
        if isinstance(labs, (str, bytes)) or not isinstance(labs, Sequence):
            raise RecommendationValidationError("labs phải là một danh sách Film Lab.")
        lab_catalogue = tuple(
            lab if isinstance(lab, FilmLab) else FilmLab.from_mapping(lab)
            for lab in labs
        )
        identifiers = [_normalise(lab.lab_id) for lab in lab_catalogue]
        if len(identifiers) != len(set(identifiers)):
            raise RecommendationValidationError("Mã Film Lab không được trùng nhau.")

    ranked: list[RecommendationResult] = []
    for lab in lab_catalogue:
        if not _is_eligible(lab, query):
            continue

        factors = {
            "format": 1.0,
            "services": _service_score(lab, query),
            "location": _location_score(lab, query),
            "budget": _threshold_score(lab.base_price_vnd, query.budget_vnd),
            "turnaround": _threshold_score(
                lab.turnaround_hours, query.max_turnaround_hours
            ),
            "rating": lab.rating / 5,
        }
        weighted = {
            factor: factors[factor] * scoring_weights[factor]
            for factor in SCORING_FACTORS
        }
        rounded_factors = {key: round(value, 4) for key, value in factors.items()}
        rounded_weighted = {key: round(value, 4) for key, value in weighted.items()}
        score = round(max(0.0, min(1.0, sum(weighted.values()))), 4)
        ranked.append(
            RecommendationResult(
                lab=lab,
                score=score,
                factor_scores=rounded_factors,
                weighted_scores=rounded_weighted,
                reasons=_explain(lab, query, factors),
            )
        )

    ranked.sort(
        key=lambda result: (
            -result.score,
            -result.lab.rating,
            -result.lab.review_count,
            result.lab.base_price_vnd,
            _normalise(result.lab.name),
            _normalise(result.lab.lab_id),
        )
    )
    return ranked[:top_k]


__all__ = [
    "DEFAULT_WEIGHTS",
    "FilmLab",
    "RecommendationQuery",
    "RecommendationResult",
    "RecommendationValidationError",
    "load_film_labs",
    "recommend_film_labs",
]
