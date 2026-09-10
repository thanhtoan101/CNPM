"""Grounded, extractive photography assistant built on local retrieval.

This assistant does not impersonate a generative model.  It selects relevant
sentences from versioned knowledge documents, labels each statement with a
citation, and declines when retrieval evidence is insufficient.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from .retrieval import (
    KnowledgeDocument,
    SearchResult,
    TfidfRetriever,
    build_default_retriever,
    tokenize,
)


AnswerStatus = Literal["grounded", "insufficient_knowledge"]

# A specialised assistant should not treat incidental word overlap as evidence.
# At least one domain marker (or a bilingual concept token from retrieval.py) is
# required before a response can be considered.  This is an explicit out-of-
# domain guard, not an attempt to infer unsupported knowledge.
_DOMAIN_TERMS = frozenset(
    {
        "35mm",
        "120",
        "archive",
        "camera",
        "developing",
        "dpi",
        "film",
        "histogram",
        "lab",
        "lens",
        "metadata",
        "minilab",
        "negative",
        "photography",
        "ppi",
        "scan",
        "scanner",
        "ảnh",
        "âm",
        "bản",
        "cuộn",
        "hóa",
        "máy",
        "nét",
        "phim",
        "scan",
        "tráng",
    }
)

# Generic words can identify the photography domain, but they do not establish
# that a document answers the specific question.  Excluding them from the
# coverage gate prevents incidental overlap such as "camera" or "film" from
# producing an unrelated yet confident-looking answer.
_GENERIC_DOMAIN_TERMS = frozenset(
    {
        "ai",
        "anh",
        "ảnh",
        "camera",
        "film",
        "lab",
        "may",
        "máy",
        "minilab",
        "photography",
        "phim",
        "scan",
    }
)


@dataclass(frozen=True, slots=True)
class Citation:
    """Traceability metadata for one extractive answer statement."""

    number: int
    document_id: str
    title: str
    source: str
    excerpt: str
    retrieval_score: float

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable citation."""

        return {
            "number": self.number,
            "document_id": self.document_id,
            "title": self.title,
            "source": self.source,
            "excerpt": self.excerpt,
            "retrieval_score": self.retrieval_score,
        }


@dataclass(frozen=True, slots=True)
class GroundedAnswer:
    """Assistant output suitable for a REST/JSON adapter."""

    status: AnswerStatus
    answer: str
    confidence: float
    citations: tuple[Citation, ...]

    @property
    def grounded(self) -> bool:
        """Whether every returned claim is backed by a listed citation."""

        return self.status == "grounded" and bool(self.citations)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable response without framework dependencies."""

        return {
            "status": self.status,
            "answer": self.answer,
            "confidence": self.confidence,
            "grounded": self.grounded,
            "citations": [citation.to_dict() for citation in self.citations],
        }


class GroundedPhotographyAssistant:
    """Answer supported questions using only retrieved local evidence."""

    _DECLINE_MESSAGE = (
        "Chưa đủ kiến thức trong cơ sở dữ liệu để trả lời câu hỏi này một cách "
        "đáng tin cậy. Hãy hỏi cụ thể hơn về Film Lab, quy trình tráng phim, "
        "chất lượng ảnh scan hoặc cách bảo quản phim."
    )

    def __init__(
        self,
        retriever: TfidfRetriever,
        *,
        confidence_threshold: float = 0.12,
        max_citations: int = 3,
    ) -> None:
        if not isinstance(retriever, TfidfRetriever):
            raise TypeError("retriever must be a TfidfRetriever")
        if (
            isinstance(confidence_threshold, bool)
            or not isinstance(confidence_threshold, (int, float))
            or not 0.0 < float(confidence_threshold) <= 1.0
        ):
            raise ValueError("confidence_threshold must be greater than 0 and at most 1")
        if (
            isinstance(max_citations, bool)
            or not isinstance(max_citations, int)
            or max_citations < 1
        ):
            raise ValueError("max_citations must be a positive integer")

        self._retriever = retriever
        self._confidence_threshold = float(confidence_threshold)
        self._max_citations = max_citations

    def ask(self, question: str) -> GroundedAnswer:
        """Return a cited extractive answer or an explicit knowledge-boundary reply."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if len(question) > 2_000:
            raise ValueError("question must contain at most 2000 characters")

        question_terms = set(tokenize(question))
        has_domain_marker = bool(question_terms.intersection(_DOMAIN_TERMS)) or any(
            term.startswith("concept_") for term in question_terms
        )
        if not has_domain_marker:
            return GroundedAnswer(
                status="insufficient_knowledge",
                answer=self._DECLINE_MESSAGE,
                confidence=0.0,
                citations=(),
            )

        results = self._retriever.search(question, top_k=self._max_citations)
        if not results or results[0].score < self._confidence_threshold:
            best_score = results[0].score if results else 0.0
            return GroundedAnswer(
                status="insufficient_knowledge",
                answer=self._DECLINE_MESSAGE,
                confidence=best_score,
                citations=(),
            )

        answerable_results = tuple(
            result
            for result in results
            if _answerability_score(result.document, question) >= 0.34
        )
        if not answerable_results:
            return GroundedAnswer(
                status="insufficient_knowledge",
                answer=self._DECLINE_MESSAGE,
                confidence=results[0].score,
                citations=(),
            )

        # Do not cite weak or unanswerable tail results simply because top_k
        # permits them.
        evidence_floor = max(
            self._confidence_threshold,
            answerable_results[0].score * 0.55,
        )
        evidence = tuple(
            result for result in answerable_results if result.score >= evidence_floor
        )
        citations = tuple(
            self._make_citation(number, result, question)
            for number, result in enumerate(evidence, start=1)
        )
        answer_lines = [
            "Câu trả lời dựa trên cơ sở tri thức nội bộ của bản mẫu:",
            *(f"[{citation.number}] {citation.excerpt}" for citation in citations),
        ]
        return GroundedAnswer(
            status="grounded",
            answer="\n".join(answer_lines),
            confidence=answerable_results[0].score,
            citations=citations,
        )

    @staticmethod
    def _make_citation(number: int, result: SearchResult, question: str) -> Citation:
        excerpt = _best_supported_sentence(result.document, question)
        return Citation(
            number=number,
            document_id=result.document.id,
            title=result.document.title,
            source=result.document.source,
            excerpt=excerpt,
            retrieval_score=result.score,
        )


def _best_supported_sentence(document: KnowledgeDocument, question: str) -> str:
    """Select the sentence with the largest query-token overlap."""

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", document.content.strip())
        if sentence.strip()
    ]
    if not sentences:
        # KnowledgeDocument validation guarantees non-empty content, but retaining
        # this fallback makes the grounding contract robust to unusual punctuation.
        return document.content.strip()

    query_terms = set(tokenize(question))
    ranked = [
        (len(query_terms.intersection(tokenize(sentence))), -index, sentence)
        for index, sentence in enumerate(sentences)
    ]
    return max(ranked)[2]


def _answerability_score(document: KnowledgeDocument, question: str) -> float:
    """Estimate whether *document* covers the substance of *question*.

    A shared bilingual concept token is strong evidence.  Without one, at least
    two non-generic query terms must occur in the document.  This conservative
    gate is intentionally separate from cosine ranking.
    """

    question_terms = {
        token for token in tokenize(question) if token not in _GENERIC_DOMAIN_TERMS
    }
    if not question_terms:
        return 0.0
    document_terms = set(
        tokenize(
            " ".join(
                (document.title, " ".join(document.tags), document.content)
            )
        )
    )
    matched = question_terms.intersection(document_terms)
    shared_concepts = {
        token for token in matched if token.startswith("concept_")
    }
    lexical_matches = matched - shared_concepts
    coverage = len(matched) / len(question_terms)
    if shared_concepts:
        return max(0.75, coverage)
    if len(lexical_matches) < 2:
        return 0.0
    return coverage


def build_default_assistant(
    *,
    confidence_threshold: float = 0.12,
    max_citations: int = 3,
) -> GroundedPhotographyAssistant:
    """Construct the offline assistant with bundled, versioned knowledge."""

    return GroundedPhotographyAssistant(
        build_default_retriever(),
        confidence_threshold=confidence_threshold,
        max_citations=max_citations,
    )
