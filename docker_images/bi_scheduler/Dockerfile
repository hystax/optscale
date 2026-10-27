FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/bi_scheduler/pyproject.toml docker_images/bi_scheduler/
COPY docker_images/bi_scheduler/uv.lock docker_images/bi_scheduler/
RUN uv --project docker_images/bi_scheduler sync --locked --no-dev

COPY docker_images/bi_scheduler/scheduler.py docker_images/bi_scheduler/

CMD ["uv", "--project", "docker_images/bi_scheduler", "run", "python3", "docker_images/bi_scheduler/scheduler.py"]
