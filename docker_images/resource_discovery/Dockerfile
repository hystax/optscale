FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/insider_client optscale_client/insider_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/cloud_adapter tools/cloud_adapter
COPY tools/optscale_time tools/optscale_time

COPY docker_images/resource_discovery/pyproject.toml docker_images/resource_discovery/
COPY docker_images/resource_discovery/uv.lock docker_images/resource_discovery/
RUN uv --project docker_images/resource_discovery sync --locked --no-dev

COPY docker_images/resource_discovery/scheduler.py docker_images/resource_discovery/worker.py docker_images/resource_discovery/

CMD ["uv", "--project", "docker_images/resource_discovery", "run", "python3", "docker_images/resource_discovery/worker.py"]
