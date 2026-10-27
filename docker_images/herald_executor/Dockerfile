FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY optscale_client/herald_client optscale_client/herald_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/herald_executor/pyproject.toml docker_images/herald_executor/
COPY docker_images/herald_executor/uv.lock docker_images/herald_executor/
RUN uv --project docker_images/herald_executor sync --locked --no-dev

COPY docker_images/herald_executor/worker.py docker_images/herald_executor/

CMD ["uv", "--project", "docker_images/herald_executor", "run", "python3", "docker_images/herald_executor/worker.py"]
