"""Deterministic, offline retrieval for the film-photography knowledge base.

The module deliberately uses only the Python standard library.  It implements a
small TF-IDF index with cosine similarity and a conservative bilingual concept
expansion layer.  The latter maps a limited set of Vietnamese and English
photography terms to the same index token; it is not presented as an embedding
model and makes no network calls.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence
import unicodedata


_WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)

# Function words add noise to a small corpus.  The list is intentionally short:
# domain words are retained even when they are frequent in photography prose.
_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "what",
        "with",
        "ai",
        "bị",
        "các",
        "có",
        "của",
        "cho",
        "để",
        "được",
        "gì",
        "khi",
        "là",
        "một",
        "nào",
        "nên",
        "những",
        "thế",
        "thì",
        "tôi",
        "trong",
        "và",
        "với",
    }
)

# A bounded alias table improves recall across Vietnamese and English queries.
# Each match appends one canonical token while preserving the original tokens.
_CONCEPT_ALIASES: Mapping[str, tuple[str, ...]] = {
    "blur": (
        "ảnh mờ",
        "bị mờ",
        "nhòe",
        "out nét",
        "out net",
        "độ nét",
        "blur",
        "blurry",
        "out of focus",
        "sharpness",
    ),
    "color_cast": (
        "ám màu",
        "lệch màu",
        "cân bằng trắng",
        "color cast",
        "colour cast",
        "white balance",
    ),
    "dust_scratch": (
        "bụi",
        "vết xước",
        "trầy xước",
        "dust",
        "scratch",
        "scratches",
    ),
    "exposure": (
        "phơi sáng",
        "thiếu sáng",
        "dư sáng",
        "underexposed",
        "overexposed",
        "exposure",
    ),
    "film_lab": (
        "film lab",
        "film labs",
        "minilab",
        "phòng lab",
        "lab phim",
    ),
    "film_storage": (
        "bảo quản phim",
        "lưu trữ phim",
        "film storage",
        "store film",
        "archive negatives",
    ),
    "negative_handling": (
        "âm bản",
        "negative",
        "negatives",
        "film sleeve",
        "bao phim",
    ),
    "scan_resolution": (
        "độ phân giải",
        "kích thước in",
        "scan resolution",
        "dpi",
        "ppi",
    ),
    "process_c41": ("c-41", "c41", "color negative", "âm bản màu"),
    "process_e6": ("e-6", "e6", "slide film", "phim dương bản"),
    "process_bw": (
        "đen trắng",
        "trắng đen",
        "black and white",
        "black-and-white",
        "b&w",
    ),
}


def _normalise_text(text: str) -> str:
    """Return a stable, case-folded Unicode representation of *text*."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def tokenize(text: str) -> tuple[str, ...]:
    """Tokenize Vietnamese/English text and append known concept aliases.

    Diacritics are preserved because removing them can conflate unrelated
    Vietnamese words.  Concept aliases supply the cross-language bridge for the
    small, explicitly supported photography vocabulary.
    """

    normalised = _normalise_text(text)
    tokens = [
        token.strip("'’-")
        for token in _WORD_RE.findall(normalised)
        if len(token.strip("'’-")) > 1
        and token.strip("'’-") not in _STOP_WORDS
    ]

    # Punctuation-normalised text permits exact phrase matching without partial
    # word matches (for example, "lab" must not match "label").
    phrase_text = " " + re.sub(r"[^\w]+", " ", normalised, flags=re.UNICODE).strip() + " "
    for concept, aliases in _CONCEPT_ALIASES.items():
        if any(
            " " + re.sub(r"[^\w]+", " ", alias).strip() + " " in phrase_text
            for alias in aliases
        ):
            tokens.append(f"concept_{concept}")
    return tuple(tokens)


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    """One validated, locally stored knowledge-base document."""

    id: str
    title: str
    content: str
    source: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("id", "title", "content", "source"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.tags, tuple) or any(
            not isinstance(tag, str) or not tag.strip() for tag in self.tags
        ):
            raise ValueError("tags must be a tuple of non-empty strings")

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "KnowledgeDocument":
        """Create a document from JSON-compatible data with strict validation."""

        if not isinstance(value, Mapping):
            raise ValueError("each knowledge-base document must be an object")
        required = ("id", "title", "content", "source")
        missing = [name for name in required if name not in value]
        if missing:
            raise ValueError(f"knowledge-base document is missing: {', '.join(missing)}")

        raw_tags = value.get("tags", [])
        if not isinstance(raw_tags, list) or any(
            not isinstance(tag, str) for tag in raw_tags
        ):
            raise ValueError("document tags must be an array of strings")
        try:
            return cls(
                id=value["id"],  # type: ignore[arg-type]
                title=value["title"],  # type: ignore[arg-type]
                content=value["content"],  # type: ignore[arg-type]
                source=value["source"],  # type: ignore[arg-type]
                tags=tuple(raw_tags),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid knowledge-base document: {exc}") from exc


@dataclass(frozen=True, slots=True)
class SearchResult:
    """A ranked retrieval result with an inspectable cosine score."""

    document: KnowledgeDocument
    score: float
    matched_terms: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation for API adapters."""

        return {
            "document_id": self.document.id,
            "title": self.document.title,
            "source": self.document.source,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
        }


def load_knowledge_base(path: str | Path | None = None) -> tuple[KnowledgeDocument, ...]:
    """Load and validate the bundled JSON knowledge base or a supplied file."""

    knowledge_path = (
        Path(path)
        if path is not None
        else Path(__file__).resolve().parent / "data" / "knowledge_base.json"
    )
    try:
        raw = json.loads(knowledge_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"knowledge-base file does not exist: {knowledge_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"knowledge-base JSON is invalid: {exc}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("documents"), list):
        raise ValueError("knowledge base must be an object containing a documents array")
    if not raw["documents"]:
        raise ValueError("knowledge base must contain at least one document")

    documents = tuple(KnowledgeDocument.from_mapping(item) for item in raw["documents"])
    ids = [document.id for document in documents]
    duplicate_ids = sorted({document_id for document_id in ids if ids.count(document_id) > 1})
    if duplicate_ids:
        raise ValueError(f"duplicate knowledge-base document ids: {', '.join(duplicate_ids)}")
    return documents


class TfidfRetriever:
    """A compact, deterministic TF-IDF/cosine retriever.

    Title and tag tokens are repeated in the indexed text to provide a modest,
    transparent field boost.  Results are ordered by descending cosine score,
    then by document id to make ties deterministic.
    """

    def __init__(self, documents: Sequence[KnowledgeDocument]) -> None:
        if not documents:
            raise ValueError("at least one knowledge document is required")
        if any(not isinstance(document, KnowledgeDocument) for document in documents):
            raise TypeError("documents must contain only KnowledgeDocument values")
        ids = [document.id for document in documents]
        if len(ids) != len(set(ids)):
            raise ValueError("knowledge document ids must be unique")

        self._documents = tuple(documents)
        self._document_tokens = tuple(
            tokenize(
                " ".join(
                    (
                        document.title,
                        document.title,
                        " ".join(document.tags),
                        " ".join(document.tags),
                        document.content,
                    )
                )
            )
            for document in self._documents
        )
        self._idf = self._calculate_idf(self._document_tokens)
        self._vectors = tuple(self._vectorise(tokens) for tokens in self._document_tokens)
        self._norms = tuple(self._norm(vector) for vector in self._vectors)

    @property
    def documents(self) -> tuple[KnowledgeDocument, ...]:
        """Expose the immutable indexed documents for grounding checks."""

        return self._documents

    @staticmethod
    def _calculate_idf(corpus: Iterable[Sequence[str]]) -> dict[str, float]:
        token_sets = [set(tokens) for tokens in corpus]
        document_count = len(token_sets)
        frequencies: Counter[str] = Counter()
        for token_set in token_sets:
            frequencies.update(token_set)
        return {
            term: math.log((1.0 + document_count) / (1.0 + frequency)) + 1.0
            for term, frequency in frequencies.items()
        }

    def _vectorise(self, tokens: Sequence[str]) -> dict[str, float]:
        frequencies = Counter(token for token in tokens if token in self._idf)
        return {
            term: (1.0 + math.log(count)) * self._idf[term]
            for term, count in frequencies.items()
        }

    @staticmethod
    def _norm(vector: Mapping[str, float]) -> float:
        return math.sqrt(sum(weight * weight for weight in vector.values()))

    def search(
        self,
        query: str,
        *,
        top_k: int = 3,
        min_score: float = 0.0,
    ) -> tuple[SearchResult, ...]:
        """Rank documents for *query* using cosine similarity.

        Args:
            query: A non-empty Vietnamese or English photography question.
            top_k: Maximum number of results to return.
            min_score: Inclusive cosine threshold in the ``[0, 1]`` interval.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if isinstance(min_score, bool) or not isinstance(min_score, (int, float)):
            raise ValueError("min_score must be a number between 0 and 1")
        if not 0.0 <= float(min_score) <= 1.0:
            raise ValueError("min_score must be a number between 0 and 1")

        query_tokens = tokenize(query)
        query_vector = self._vectorise(query_tokens)
        query_norm = self._norm(query_vector)
        if query_norm == 0.0:
            return ()

        query_terms = set(query_vector)
        results: list[SearchResult] = []
        for document, document_tokens, document_vector, document_norm in zip(
            self._documents,
            self._document_tokens,
            self._vectors,
            self._norms,
        ):
            if document_norm == 0.0:
                continue
            dot_product = sum(
                weight * document_vector.get(term, 0.0)
                for term, weight in query_vector.items()
            )
            score = dot_product / (query_norm * document_norm)
            if score > 0.0 and score >= float(min_score):
                results.append(
                    SearchResult(
                        document=document,
                        score=round(score, 6),
                        matched_terms=tuple(sorted(query_terms.intersection(document_tokens))),
                    )
                )

        results.sort(key=lambda result: (-result.score, result.document.id))
        return tuple(results[:top_k])


def build_default_retriever() -> TfidfRetriever:
    """Build a retriever backed by the repository's versioned knowledge base."""

    return TfidfRetriever(load_knowledge_base())
