FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/herald_client optscale_client/herald_client
COPY optscale_client/report_client optscale_client/report_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/keeper_executor/pyproject.toml docker_images/keeper_executor/
COPY docker_images/keeper_executor/uv.lock docker_images/keeper_executor/
RUN uv --project docker_images/keeper_executor sync --locked --no-dev

COPY docker_images/keeper_executor/*.py docker_images/keeper_executor/
COPY docker_images/keeper_executor/executors/*.py docker_images/keeper_executor/executors/

CMD ["uv", "--project", "docker_images/keeper_executor", "run", "python3", "docker_images/keeper_executor/worker.py"]
