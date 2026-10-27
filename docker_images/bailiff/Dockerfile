FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY optscale_client/subspector_async_client optscale_client/subspector_async_client

COPY docker_images/bailiff/pyproject.toml docker_images/bailiff/
COPY docker_images/bailiff/uv.lock docker_images/bailiff/
RUN uv --project docker_images/bailiff sync --locked --no-dev

COPY docker_images/bailiff/*.py docker_images/bailiff/

CMD ["uv", "--project", "docker_images/bailiff", "run", "python3", "docker_images/bailiff/worker.py"]
