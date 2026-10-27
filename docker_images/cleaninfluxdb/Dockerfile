FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app

COPY docker_images/cleaninfluxdb/pyproject.toml docker_images/cleaninfluxdb/
COPY docker_images/cleaninfluxdb/uv.lock docker_images/cleaninfluxdb/
RUN uv --project docker_images/cleaninfluxdb sync --locked --no-dev

COPY docker_images/cleaninfluxdb/*.py docker_images/cleaninfluxdb/

CMD ["uv", "--project", "docker_images/cleaninfluxdb", "run", "python", "docker_images/cleaninfluxdb/clean-influx-db.py"]
