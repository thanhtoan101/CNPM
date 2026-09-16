"""Reproducible information-retrieval metrics for the AI baselines."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Callable, Iterable, Mapping, Sequence

from .recommendation import recommend_film_labs
from .retrieval import TfidfRetriever, build_default_retriever


DEFAULT_EVALUATION_PATH = Path(__file__).resolve().parent / "data" / "evaluation_cases.json"


def _unique_ids(values: Iterable[str], name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be an iterable of identifiers")
    result = tuple(values)
    if not result or any(not isinstance(value, str) or not value.strip() for value in result):
        raise ValueError(f"{name} must contain non-empty string identifiers")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} must not contain duplicate identifiers")
    return result


def precision_at_k(ranked_ids: Iterable[str], relevant_ids: Iterable[str], k: int) -> float:
    """Return binary relevance precision for the first *k* ranked items."""

    ranked = _unique_ids(ranked_ids, "ranked_ids")
    relevant = set(_unique_ids(relevant_ids, "relevant_ids"))
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    selected = ranked[:k]
    return sum(item in relevant for item in selected) / k


def recall_at_k(ranked_ids: Iterable[str], relevant_ids: Iterable[str], k: int) -> float:
    """Return binary relevance recall for the first *k* ranked items."""

    ranked = _unique_ids(ranked_ids, "ranked_ids")
    relevant = set(_unique_ids(relevant_ids, "relevant_ids"))
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    return sum(item in relevant for item in ranked[:k]) / len(relevant)


def reciprocal_rank(ranked_ids: Iterable[str], relevant_ids: Iterable[str]) -> float:
    """Return reciprocal rank of the first relevant result, or zero."""

    ranked = _unique_ids(ranked_ids, "ranked_ids")
    relevant = set(_unique_ids(relevant_ids, "relevant_ids"))
    for index, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1.0 / index
    return 0.0


def ndcg_at_k(ranked_ids: Iterable[str], relevant_ids: Iterable[str], k: int) -> float:
    """Return normalized discounted cumulative gain using binary relevance."""

    ranked = _unique_ids(ranked_ids, "ranked_ids")
    relevant = set(_unique_ids(relevant_ids, "relevant_ids"))
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    dcg = sum(
        (1.0 / math.log2(index + 1)) if item in relevant else 0.0
        for index, item in enumerate(ranked[:k], start=1)
    )
    ideal_count = min(k, len(relevant))
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, ideal_count + 1))
    return dcg / ideal if ideal else 0.0


@dataclass(frozen=True)
class EvaluationSummary:
    component: str
    case_count: int
    k: int
    precision_at_k: float
    recall_at_k: float
    mean_reciprocal_rank: float
    ndcg_at_k: float

    def to_dict(self) -> dict[str, object]:
        return {
            "component": self.component,
            "case_count": self.case_count,
            "k": self.k,
            "precision_at_k": round(self.precision_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "mean_reciprocal_rank": round(self.mean_reciprocal_rank, 4),
            "ndcg_at_k": round(self.ndcg_at_k, 4),
        }


def load_evaluation_cases(path: str | Path | None = None) -> dict[str, list[dict[str, Any]]]:
    source_path = Path(path) if path is not None else DEFAULT_EVALUATION_PATH
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read evaluation cases at {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("evaluation data must be a JSON object")
    result: dict[str, list[dict[str, Any]]] = {}
    for component in ("recommendation", "retrieval"):
        cases = payload.get(component)
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"evaluation data requires a non-empty {component} array")
        if any(not isinstance(case, dict) for case in cases):
            raise ValueError(f"every {component} case must be an object")
        result[component] = cases
    return result


def _summarize(
    component: str,
    cases: Sequence[Mapping[str, Any]],
    ranker: Callable[[Mapping[str, Any], int], Sequence[str]],
    *,
    k: int,
) -> EvaluationSummary:
    measurements: list[tuple[float, float, float, float]] = []
    for case in cases:
        relevant = _unique_ids(case.get("relevant_ids", ()), "relevant_ids")
        ranked = tuple(ranker(case, k))
        if not ranked:
            # A metric can legitimately measure an empty retrieval outcome, but
            # helper functions require a non-empty ranked sequence for misuse
            # detection.  The four values for this case are therefore all zero.
            measurements.append((0.0, 0.0, 0.0, 0.0))
            continue
        measurements.append(
            (
                precision_at_k(ranked, relevant, k),
                recall_at_k(ranked, relevant, k),
                reciprocal_rank(ranked, relevant),
                ndcg_at_k(ranked, relevant, k),
            )
        )
    return EvaluationSummary(
        component=component,
        case_count=len(cases),
        k=k,
        precision_at_k=mean(row[0] for row in measurements),
        recall_at_k=mean(row[1] for row in measurements),
        mean_reciprocal_rank=mean(row[2] for row in measurements),
        ndcg_at_k=mean(row[3] for row in measurements),
    )


def evaluate_baselines(
    path: str | Path | None = None,
    *,
    k: int = 3,
    retriever: TfidfRetriever | None = None,
) -> dict[str, object]:
    """Evaluate bundled synthetic relevance cases and return JSON-ready metrics.

    The bundled cases are software fixtures, not production evidence.  The
    returned metadata makes that limitation explicit so the numbers are not
    presented as accuracy on real users or real scans.
    """

    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    cases = load_evaluation_cases(path)
    search = retriever or build_default_retriever()

    recommendation = _summarize(
        "recommendation",
        cases["recommendation"],
        lambda case, limit: [
            result.lab.lab_id
            for result in recommend_film_labs(case["query"], top_k=limit)
        ],
        k=k,
    )
    retrieval = _summarize(
        "retrieval",
        cases["retrieval"],
        lambda case, limit: [
            result.document.id
            for result in search.search(str(case["query"]), top_k=limit)
        ],
        k=k,
    )
    return {
        "dataset": "bundled synthetic relevance fixtures",
        "production_claim": False,
        "limitations": (
            "These cases verify reproducibility and metric wiring only; "
            "representative expert-reviewed data is required for a production claim."
        ),
        "results": [recommendation.to_dict(), retrieval.to_dict()],
    }


__all__ = [
    "EvaluationSummary",
    "evaluate_baselines",
    "load_evaluation_cases",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
]
