FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/resource_observer/pyproject.toml docker_images/resource_observer/
COPY docker_images/resource_observer/uv.lock docker_images/resource_observer/
RUN uv --project docker_images/resource_observer sync --locked --no-dev

COPY docker_images/resource_observer/scheduler.py docker_images/resource_observer/worker.py docker_images/resource_observer/

CMD ["uv", "--project", "docker_images/resource_observer", "run", "python3", "docker_images/resource_observer/worker.py"]
