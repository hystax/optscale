FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

COPY tools tools
COPY optscale_client optscale_client
COPY katara/__init__.py katara/

WORKDIR /usr/src/app/katara/katara_worker

COPY katara/katara_worker/pyproject.toml ./
COPY katara/katara_worker/uv.lock ./
COPY katara/katara_worker/reports_generators ./reports_generators
COPY katara/katara_worker/*.py ./

RUN uv --project /usr/src/app/katara/katara_worker sync --locked --no-dev

CMD ["uv", "run", "--project", "/usr/src/app/katara/katara_worker", "python", "-u", "main.py"]
