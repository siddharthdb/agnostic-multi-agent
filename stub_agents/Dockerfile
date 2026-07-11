FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# The module (cam_stub.main:app / fsr_stub.main:app / bsa_stub.main:app) is chosen
# per-service via the `command:` override in docker-compose.yml — this image is shared.
CMD ["uv", "run", "uvicorn", "cam_stub.main:app", "--host", "0.0.0.0", "--port", "8000"]
