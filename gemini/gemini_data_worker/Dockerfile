FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

COPY optscale_client optscale_client
COPY gemini/__init__.py gemini/
COPY gemini/gemini_data_worker/pyproject.toml gemini/gemini_data_worker/
COPY gemini/gemini_data_worker/uv.lock gemini/gemini_data_worker/
COPY gemini/gemini_data_worker/*.py gemini/gemini_data_worker/

RUN uv --project gemini/gemini_data_worker sync --locked --no-dev

CMD ["uv", "run", "--project", "gemini/gemini_data_worker", "python", "-u","/usr/src/app/gemini/gemini_data_worker/main.py"]
