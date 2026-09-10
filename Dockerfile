FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AI_HOST=0.0.0.0 \
    AI_PORT=8080

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY requirements.txt pyproject.toml ./
COPY ai_service ./ai_service

RUN pip install --no-cache-dir .

USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"

CMD ["python", "-m", "ai_service.api"]
