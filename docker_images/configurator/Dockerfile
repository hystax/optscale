FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client

COPY docker_images/configurator/pyproject.toml docker_images/configurator/
COPY docker_images/configurator/uv.lock docker_images/configurator/
RUN uv --project docker_images/configurator sync --locked --no-dev

COPY docker_images/configurator/configurator.py docker_images/configurator/

CMD ["uv", "--project", "docker_images/configurator", "run", "python", "docker_images/configurator/configurator.py", "/config/config"]
