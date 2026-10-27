FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/organization_violations/pyproject.toml docker_images/organization_violations/
COPY docker_images/organization_violations/uv.lock docker_images/organization_violations/
RUN uv --project docker_images/organization_violations sync --locked --no-dev

COPY docker_images/organization_violations/scheduler.py docker_images/organization_violations/worker.py docker_images/organization_violations/

CMD ["uv", "--project", "docker_images/organization_violations", "run", "python3", "docker_images/organization_violations/worker.py"]
