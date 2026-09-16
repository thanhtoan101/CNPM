"""Unit tests for deterministic retrieval and grounded assistant behaviour."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from ai_service.assistant import GroundedPhotographyAssistant, build_default_assistant
from ai_service.retrieval import (
    KnowledgeDocument,
    TfidfRetriever,
    build_default_retriever,
    load_knowledge_base,
)


class RetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.retriever = build_default_retriever()

    def test_vietnamese_blur_query_ranks_focus_document_first(self) -> None:
        results = self.retriever.search("Ảnh scan của tôi bị mờ, làm sao kiểm tra độ nét?")

        self.assertTrue(results)
        self.assertEqual("scan-blur-focus", results[0].document.id)
        self.assertGreater(results[0].score, 0.12)

    def test_english_query_uses_bilingual_concept_aliases(self) -> None:
        results = self.retriever.search("How do I diagnose a blurry film scan?")

        self.assertTrue(results)
        self.assertEqual("scan-blur-focus", results[0].document.id)
        self.assertIn("concept_blur", results[0].matched_terms)

    def test_search_order_and_scores_are_deterministic(self) -> None:
        first = self.retriever.search("bụi và vết xước trên ảnh scan")
        second = self.retriever.search("bụi và vết xước trên ảnh scan")

        self.assertEqual(first, second)
        self.assertEqual("scan-dust-scratches", first[0].document.id)

    def test_search_validates_query_and_limits(self) -> None:
        with self.assertRaises(ValueError):
            self.retriever.search("   ")
        with self.assertRaises(ValueError):
            self.retriever.search("scan", top_k=0)
        with self.assertRaises(ValueError):
            self.retriever.search("scan", min_score=1.1)

    def test_loader_rejects_duplicate_document_ids(self) -> None:
        payload = {
            "documents": [
                {
                    "id": "duplicate",
                    "title": "One",
                    "content": "First valid knowledge record.",
                    "source": "kb://one",
                },
                {
                    "id": "duplicate",
                    "title": "Two",
                    "content": "Second valid knowledge record.",
                    "source": "kb://two",
                },
            ]
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "invalid.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_knowledge_base(path)


class AssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = build_default_assistant()

    def test_grounded_answer_contains_traceable_citations(self) -> None:
        response = self.assistant.ask(
            "Ảnh scan bị ám màu thì nguyên nhân và cách kiểm tra là gì?"
        )

        self.assertTrue(response.grounded)
        self.assertEqual("grounded", response.status)
        self.assertTrue(response.citations)
        documents = {document.id: document for document in build_default_retriever().documents}
        for citation in response.citations:
            self.assertIn(f"[{citation.number}]", response.answer)
            self.assertIn(citation.document_id, documents)
            self.assertIn(citation.excerpt, documents[citation.document_id].content)

    def test_unknown_subject_is_explicitly_declined_without_citations(self) -> None:
        response = self.assistant.ask(
            "Hãy chứng minh định lý phân loại nhóm hữu hạn đơn trong toán học."
        )

        self.assertFalse(response.grounded)
        self.assertEqual("insufficient_knowledge", response.status)
        self.assertIn("Chưa đủ kiến thức", response.answer)
        self.assertEqual((), response.citations)

    def test_in_domain_but_unsupported_questions_are_declined(self) -> None:
        questions = (
            "Máy ảnh phim của tôi hết pin, nên dùng pin nào?",
            "Cách tráng phim bằng nước rửa chén?",
        )

        for question in questions:
            with self.subTest(question=question):
                response = self.assistant.ask(question)
                self.assertEqual("insufficient_knowledge", response.status)
                self.assertFalse(response.grounded)
                self.assertEqual((), response.citations)

    def test_assistant_validation_and_configuration(self) -> None:
        with self.assertRaises(ValueError):
            self.assistant.ask("")
        with self.assertRaises(ValueError):
            self.assistant.ask("x" * 2_001)
        with self.assertRaises(ValueError):
            GroundedPhotographyAssistant(self.assistant._retriever, max_citations=0)

    def test_retriever_rejects_invalid_documents(self) -> None:
        with self.assertRaises(ValueError):
            KnowledgeDocument("", "Title", "Content", "kb://source")
        with self.assertRaises(ValueError):
            TfidfRetriever([])


if __name__ == "__main__":
    unittest.main()
