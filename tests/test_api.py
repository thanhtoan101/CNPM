"""Contract and integration tests for the dependency-light REST adapter."""

from __future__ import annotations

import base64
import io
import json
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image

from ai_service.api import create_server


class AIServiceApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def _request(
        self,
        path: str,
        *,
        payload: object | None = None,
        content_type: str = "application/json",
        method: str | None = None,
    ) -> tuple[int, dict[str, object], object]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {} if data is None else {"Content-Type": content_type}
        request = Request(
            self.base_url + path,
            data=data,
            headers=headers,
            method=method or ("GET" if data is None else "POST"),
        )
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            decoded = json.loads(response.read().decode("utf-8"))
            return response.status, dict(response.headers), decoded

    def test_health_and_readiness_contracts(self) -> None:
        health_status, health_headers, health = self._request("/health")
        ready_status, _, ready = self._request("/ready")

        self.assertEqual(200, health_status)
        self.assertEqual("healthy", health["data"]["status"])
        self.assertTrue(health_headers["X-Request-Id"])
        self.assertEqual("nosniff", health_headers["X-Content-Type-Options"])
        self.assertEqual(200, ready_status)
        self.assertGreater(ready["data"]["film_lab_count"], 0)
        self.assertGreater(ready["data"]["knowledge_document_count"], 0)

    def test_openapi_contract_is_machine_readable(self) -> None:
        status, _, body = self._request("/openapi.json")

        self.assertEqual(200, status)
        self.assertEqual("3.1.0", body["openapi"])
        self.assertIn("/v1/recommendations", body["paths"])
        self.assertIn("/v1/scan-quality", body["paths"])

    def test_recommendation_endpoint_respects_hard_constraints(self) -> None:
        status, _, body = self._request(
            "/v1/recommendations",
            payload={
                "query": {
                    "film_format": "120",
                    "required_services": ["developing", "scanning"],
                    "city": "TP. Hồ Chí Minh",
                },
                "top_k": 2,
            },
        )

        self.assertEqual(200, status)
        self.assertGreater(body["data"]["count"], 0)
        for item in body["data"]["results"]:
            self.assertIn("120", item["lab"]["formats"])
            self.assertGreater(item["score"], 0)
            self.assertTrue(item["reasons"])

    def test_search_and_assistant_return_traceable_sources(self) -> None:
        search_status, _, search = self._request(
            "/v1/search", payload={"query": "Cách xử lý ảnh scan bị ám màu?"}
        )
        answer_status, _, answer = self._request(
            "/v1/assistant/ask",
            payload={"question": "Cách xử lý ảnh scan bị ám màu?"},
        )

        self.assertEqual(200, search_status)
        self.assertGreater(search["data"]["count"], 0)
        self.assertEqual(200, answer_status)
        self.assertEqual("grounded", answer["data"]["status"])
        self.assertTrue(answer["data"]["citations"])
        returned_ids = {
            item["document_id"] for item in search["data"]["results"]
        }
        self.assertIn(answer["data"]["citations"][0]["document_id"], returned_ids)

    def test_assistant_declines_out_of_domain_question(self) -> None:
        status, _, body = self._request(
            "/v1/assistant/ask",
            payload={"question": "Dự báo thời tiết ngày mai là gì?"},
        )

        self.assertEqual(200, status)
        self.assertEqual("insufficient_knowledge", body["data"]["status"])
        self.assertFalse(body["data"]["grounded"])
        self.assertEqual([], body["data"]["citations"])

    def test_scan_quality_accepts_base64_image(self) -> None:
        image = Image.new("RGB", (64, 64), (3, 3, 3))
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        encoded = base64.b64encode(stream.getvalue()).decode("ascii")

        status, _, body = self._request(
            "/v1/scan-quality", payload={"image_base64": encoded}
        )

        self.assertEqual(200, status)
        self.assertIn("underexposed", {item["code"] for item in body["data"]["issues"]})
        self.assertGreaterEqual(body["data"]["overall_score"], 0)
        self.assertLessEqual(body["data"]["overall_score"], 1)

    def test_validation_error_is_structured_and_does_not_expose_trace(self) -> None:
        status, headers, body = self._request(
            "/v1/recommendations",
            payload={"query": {"film_format": "35mm"}},
        )

        self.assertEqual(400, status)
        self.assertEqual(headers["X-Request-Id"], body["request_id"])
        self.assertEqual("validation_error", body["error"]["code"])
        self.assertNotIn("Traceback", body["error"]["message"])

    def test_wrong_media_type_and_unknown_route_are_rejected(self) -> None:
        media_status, _, media = self._request(
            "/v1/search", payload={"query": "film"}, content_type="text/plain"
        )
        route_status, _, route = self._request(
            "/v1/unknown", payload={"query": "film"}
        )

        self.assertEqual(415, media_status)
        self.assertEqual("unsupported_media_type", media["error"]["code"])
        self.assertEqual(404, route_status)
        self.assertEqual("not_found", route["error"]["code"])

    def test_invalid_base64_and_size_limits_return_structured_errors(self) -> None:
        invalid_status, _, invalid = self._request(
            "/v1/scan-quality", payload={"image_base64": "not@@base64"}
        )
        with patch("ai_service.api.MAX_IMAGE_BYTES", 8):
            large_status, _, large = self._request(
                "/v1/scan-quality",
                payload={"image_base64": base64.b64encode(b"012345678").decode("ascii")},
            )
        with patch("ai_service.api.MAX_JSON_BODY_BYTES", 24):
            body_status, _, body = self._request(
                "/v1/search", payload={"query": "x" * 50}
            )

        self.assertEqual(400, invalid_status)
        self.assertEqual("invalid_base64_image", invalid["error"]["code"])
        self.assertEqual(413, large_status)
        self.assertEqual("image_too_large", large["error"]["code"])
        self.assertEqual(413, body_status)
        self.assertEqual("payload_too_large", body["error"]["code"])

    def test_unsupported_method_returns_json_405(self) -> None:
        status, _, body = self._request(
            "/v1/search", payload={"query": "film"}, method="PUT"
        )

        self.assertEqual(405, status)
        self.assertEqual("method_not_allowed", body["error"]["code"])


if __name__ == "__main__":
    unittest.main()
