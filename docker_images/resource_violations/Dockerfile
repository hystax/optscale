FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/resource_violations/pyproject.toml docker_images/resource_violations/
COPY docker_images/resource_violations/uv.lock docker_images/resource_violations/
RUN uv --project docker_images/resource_violations sync --locked --no-dev

COPY docker_images/resource_violations/scheduler.py docker_images/resource_violations/worker.py docker_images/resource_violations/

CMD ["uv", "--project", "docker_images/resource_violations", "run", "python3", "docker_images/resource_violations/worker.py"]
