"""Smoke-check a service; run as ``python -m scripts.smoke_test [base_url]``."""

from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def fetch_json(base_url: str, path: str, payload: object | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + path,
        data=data,
        headers={} if data is None else {"Content-Type": "application/json"},
        method="GET" if data is None else "POST",
    )
    with urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8080")
    args = parser.parse_args()

    health = fetch_json(args.base_url, "/health")
    ready = fetch_json(args.base_url, "/ready")
    recommendation = fetch_json(
        args.base_url,
        "/v1/recommendations",
        {
            "query": {
                "film_format": "35mm",
                "required_services": ["developing", "scanning"],
            },
            "top_k": 1,
        },
    )
    answer = fetch_json(
        args.base_url,
        "/v1/assistant/ask",
        {"question": "Nên bảo quản âm bản phim như thế nào?"},
    )

    if health["data"]["status"] != "healthy":
        raise RuntimeError("health check did not report healthy")
    if ready["data"]["status"] != "ready":
        raise RuntimeError("readiness check did not report ready")
    if recommendation["data"]["count"] < 1:
        raise RuntimeError("recommendation smoke test returned no Film Lab")
    if answer["data"]["status"] != "grounded" or not answer["data"]["citations"]:
        raise RuntimeError("assistant smoke test did not return grounded citations")

    print("PASS: health, readiness, recommendation and grounded assistant")


if __name__ == "__main__":
    main()
