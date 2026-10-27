FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/layout_cleaner/pyproject.toml docker_images/layout_cleaner/
COPY docker_images/layout_cleaner/uv.lock docker_images/layout_cleaner/
RUN uv --project docker_images/layout_cleaner sync --locked --no-dev

COPY docker_images/layout_cleaner/*.py docker_images/layout_cleaner/

CMD ["uv", "--project", "docker_images/layout_cleaner", "run", "python3", "docker_images/layout_cleaner/worker.py"]
