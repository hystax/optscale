FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

COPY optscale_client optscale_client
COPY tools/cloud_adapter tools/cloud_adapter

COPY gemini/__init__.py gemini/
COPY gemini/gemini_worker/pyproject.toml gemini/gemini_worker/
COPY gemini/gemini_worker/uv.lock gemini/gemini_worker/

COPY gemini/gemini_worker/*.py gemini/gemini_worker/
COPY gemini/gemini_worker/duplicate_object_finder gemini/gemini_worker/duplicate_object_finder
COPY gemini/gemini_worker/migrations gemini/gemini_worker/migrations

RUN uv --project gemini/gemini_worker sync --locked --no-dev

CMD ["uv", "run", "--project", "gemini/gemini_worker", "python", "-u","/usr/src/app/gemini/gemini_worker/main.py"]
