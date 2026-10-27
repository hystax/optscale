FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app
RUN mkdir -p /src/archive

COPY optscale_client/config_client optscale_client/config_client

COPY docker_images/cleanmongodb/pyproject.toml docker_images/cleanmongodb/
COPY docker_images/cleanmongodb/uv.lock docker_images/cleanmongodb/
RUN uv --project docker_images/cleanmongodb sync --locked --no-dev

COPY docker_images/cleanmongodb/*.py docker_images/cleanmongodb/

CMD ["uv", "--project", "docker_images/cleanmongodb", "run", "python", "docker_images/cleanmongodb/clean-mongo-db.py"]
