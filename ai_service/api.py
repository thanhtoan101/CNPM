"""Minimal, dependency-light HTTP adapter for the AI prototypes.

The adapter is deliberately small so the module can be demonstrated before the
shared ASP.NET Core/Node.js backend exists.  Production clients should call it
through an authenticated API gateway rather than expose it as an identity
provider.  No request body or image content is written to logs.
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Mapping
from urllib.parse import urlsplit
from uuid import uuid4

from . import __version__
from .assistant import GroundedPhotographyAssistant
from .recommendation import (
    FilmLab,
    RecommendationValidationError,
    load_film_labs,
    recommend_film_labs,
)
from .retrieval import TfidfRetriever, build_default_retriever
from .vision import ScanQualityError, ScanQualityValidationError, analyze_scan_quality


LOGGER = logging.getLogger("film_ai.api")
MAX_JSON_BODY_BYTES = 12 * 1024 * 1024
MAX_IMAGE_BYTES = 8 * 1024 * 1024
OPENAPI_PATH = Path(__file__).with_name("openapi.json")
ROUTE_METHODS = {
    "/health": frozenset({"GET"}),
    "/ready": frozenset({"GET"}),
    "/openapi.json": frozenset({"GET"}),
    "/v1/recommendations": frozenset({"POST"}),
    "/v1/search": frozenset({"POST"}),
    "/v1/assistant/ask": frozenset({"POST"}),
    "/v1/scan-quality": frozenset({"POST"}),
}


class ApiInputError(ValueError):
    """An input error with an HTTP-safe error code and status."""

    def __init__(self, message: str, *, code: str = "invalid_request", status: int = 400):
        super().__init__(message)
        self.code = code
        self.status = status


@dataclass(frozen=True)
class AIApplication:
    """Preloaded application services shared by all request threads."""

    labs: tuple[FilmLab, ...]
    retriever: TfidfRetriever
    assistant: GroundedPhotographyAssistant

    @classmethod
    def build_default(cls) -> "AIApplication":
        retriever = build_default_retriever()
        return cls(
            labs=load_film_labs(),
            retriever=retriever,
            assistant=GroundedPhotographyAssistant(retriever),
        )

    @property
    def ready(self) -> bool:
        return bool(self.labs and self.retriever.documents)


class AIServer(ThreadingHTTPServer):
    """HTTP server carrying immutable application state."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        application: AIApplication,
    ) -> None:
        self.application = application
        super().__init__(server_address, AIRequestHandler)


class AIRequestHandler(BaseHTTPRequestHandler):
    """JSON-only routes for recommendation, retrieval, assistant and CV."""

    server: AIServer
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_PUT(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_PATCH(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_DELETE(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._handle_request()

    def do_OPTIONS(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        request_id = uuid4().hex
        self._send_json(
            HTTPStatus.NO_CONTENT,
            None,
            request_id=request_id,
        )

    def log_message(self, format: str, *args: object) -> None:
        # Disable BaseHTTPRequestHandler's raw request log.  _handle_request
        # emits structured metadata without body/query content.
        return

    def _handle_request(self) -> None:
        started = time.perf_counter()
        request_id = uuid4().hex
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        path = urlsplit(self.path).path

        try:
            status, data = self._dispatch(path)
            payload = (
                data
                if path == "/openapi.json"
                else {"request_id": request_id, "data": data}
            )
            self._send_json(status, payload, request_id=request_id)
        except ApiInputError as exc:
            status = HTTPStatus(exc.status)
            self._send_error(status, exc.code, str(exc), request_id)
        except (RecommendationValidationError, ScanQualityValidationError, ValueError) as exc:
            status = HTTPStatus.BAD_REQUEST
            self._send_error(status, "validation_error", str(exc), request_id)
        except ScanQualityError:
            status = HTTPStatus.SERVICE_UNAVAILABLE
            self._send_error(
                status,
                "scan_analyzer_unavailable",
                "Scan-quality analysis is temporarily unavailable.",
                request_id,
            )
        except Exception:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            LOGGER.exception(
                "request_failed request_id=%s method=%s path=%s",
                request_id,
                self.command,
                path,
            )
            self._send_error(
                status,
                "internal_error",
                "The service could not process the request.",
                request_id,
            )
        finally:
            latency_ms = (time.perf_counter() - started) * 1000
            LOGGER.info(
                "request_complete request_id=%s method=%s path=%s status=%d latency_ms=%.2f",
                request_id,
                self.command,
                path,
                int(status),
                latency_ms,
            )

    def _dispatch(self, path: str) -> tuple[HTTPStatus, Any]:
        allowed_methods = ROUTE_METHODS.get(path)
        if allowed_methods is None:
            raise ApiInputError("Route not found.", code="not_found", status=404)
        if self.command not in allowed_methods:
            raise ApiInputError(
                f"Method {self.command} is not allowed for this route.",
                code="method_not_allowed",
                status=405,
            )

        if self.command == "GET" and path == "/health":
            return HTTPStatus.OK, {"status": "healthy", "version": __version__}
        if self.command == "GET" and path == "/ready":
            if self.server.application.ready:
                return HTTPStatus.OK, {
                    "status": "ready",
                    "film_lab_count": len(self.server.application.labs),
                    "knowledge_document_count": len(
                        self.server.application.retriever.documents
                    ),
                }
            return HTTPStatus.SERVICE_UNAVAILABLE, {"status": "not_ready"}
        if self.command == "GET" and path == "/openapi.json":
            return HTTPStatus.OK, json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))

        if path == "/v1/recommendations":
            payload = self._read_json_object()
            query = _require_mapping(payload.get("query"), "query")
            top_k = payload.get("top_k", 3)
            weights = payload.get("weights")
            if weights is not None:
                weights = _require_mapping(weights, "weights")
            results = recommend_film_labs(
                query,
                labs=self.server.application.labs,
                top_k=top_k,
                weights=weights,
            )
            return HTTPStatus.OK, {
                "count": len(results),
                "results": [result.to_dict() for result in results],
            }

        if path == "/v1/search":
            payload = self._read_json_object()
            query = _require_string(payload.get("query"), "query", max_length=2_000)
            results = self.server.application.retriever.search(
                query,
                top_k=payload.get("top_k", 3),
                min_score=payload.get("min_score", 0.0),
            )
            return HTTPStatus.OK, {
                "count": len(results),
                "results": [result.to_dict() for result in results],
            }

        if path == "/v1/assistant/ask":
            payload = self._read_json_object()
            question = _require_string(
                payload.get("question"), "question", max_length=2_000
            )
            return HTTPStatus.OK, self.server.application.assistant.ask(question).to_dict()

        if path == "/v1/scan-quality":
            payload = self._read_json_object()
            encoded = _require_string(
                payload.get("image_base64"),
                "image_base64",
                max_length=(MAX_IMAGE_BYTES * 4 // 3) + 256,
            )
            image_bytes = _decode_base64_image(encoded)
            if len(image_bytes) > MAX_IMAGE_BYTES:
                raise ApiInputError(
                    f"Decoded image must not exceed {MAX_IMAGE_BYTES} bytes.",
                    code="image_too_large",
                    status=413,
                )
            result = analyze_scan_quality(
                image_bytes,
                max_dimension=payload.get("max_dimension", 1024),
            )
            return HTTPStatus.OK, result

        raise RuntimeError("A declared API route has no dispatcher implementation.")

    def _read_json_object(self) -> dict[str, Any]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ApiInputError(
                "Content-Type must be application/json.",
                code="unsupported_media_type",
                status=415,
            )

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ApiInputError("Content-Length is required.", code="length_required", status=411)
        try:
            content_length = int(raw_length)
        except ValueError as exc:
            raise ApiInputError("Content-Length must be an integer.") from exc
        if content_length < 0:
            raise ApiInputError("Content-Length must not be negative.")
        if content_length > MAX_JSON_BODY_BYTES:
            raise ApiInputError(
                f"JSON body must not exceed {MAX_JSON_BODY_BYTES} bytes.",
                code="payload_too_large",
                status=413,
            )

        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiInputError("Request body must be valid UTF-8 JSON.", code="invalid_json") from exc
        if not isinstance(payload, dict):
            raise ApiInputError("Request body must be a JSON object.")
        return payload

    def _send_error(
        self,
        status: HTTPStatus,
        code: str,
        message: str,
        request_id: str,
    ) -> None:
        if status in {
            HTTPStatus.LENGTH_REQUIRED,
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        }:
            self.close_connection = True
        self._send_json(
            status,
            {
                "request_id": request_id,
                "error": {"code": code, "message": message},
            },
            request_id=request_id,
        )

    def _send_json(
        self,
        status: HTTPStatus,
        payload: object,
        *,
        request_id: str,
    ) -> None:
        if status == HTTPStatus.NO_CONTENT:
            encoded = b""
        else:
            encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Request-Id", request_id)
        self.end_headers()
        if encoded and self.command != "HEAD":
            self.wfile.write(encoded)


def _require_mapping(value: object, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ApiInputError(f"{field_name} must be a JSON object.")
    return value


def _require_string(
    value: object,
    field_name: str,
    *,
    max_length: int,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ApiInputError(f"{field_name} must be a non-empty string.")
    if len(value) > max_length:
        raise ApiInputError(
            f"{field_name} must contain at most {max_length} characters.",
            code="payload_too_large",
            status=413,
        )
    return value.strip()


def _decode_base64_image(encoded: str) -> bytes:
    value = encoded.strip()
    if value.startswith("data:"):
        prefix, separator, value = value.partition(",")
        if separator != "," or ";base64" not in prefix.casefold():
            raise ApiInputError(
                "image_base64 data URI must use base64 encoding.",
                code="invalid_base64_image",
            )
        if not prefix.casefold().startswith("data:image/"):
            raise ApiInputError(
                "image_base64 data URI must contain an image media type.",
                code="invalid_base64_image",
            )
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ApiInputError(
            "image_base64 is not valid base64 data.", code="invalid_base64_image"
        ) from exc


def create_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    *,
    application: AIApplication | None = None,
) -> AIServer:
    """Create, but do not start, an AI HTTP server."""

    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")
    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65_535:
        raise ValueError("port must be an integer between 0 and 65535")
    return AIServer((host.strip(), port), application or AIApplication.build_default())


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("AI_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    host = os.environ.get("AI_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("AI_PORT", "8080"))
    except ValueError as exc:
        raise SystemExit("AI_PORT must be an integer") from exc

    server = create_server(host, port)
    LOGGER.info("service_started host=%s port=%d version=%s", host, port, __version__)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        LOGGER.info("service_stopping")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
