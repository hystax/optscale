FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY optscale_client/slacker_client optscale_client/slacker_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/slacker_executor/pyproject.toml docker_images/slacker_executor/
COPY docker_images/slacker_executor/uv.lock docker_images/slacker_executor/
RUN uv --project docker_images/slacker_executor sync --locked --no-dev

COPY docker_images/slacker_executor/worker.py docker_images/slacker_executor/

CMD ["uv", "--project", "docker_images/slacker_executor", "run", "python3", "docker_images/slacker_executor/worker.py"]
