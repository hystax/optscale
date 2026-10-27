FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/live_demo_generator/pyproject.toml docker_images/live_demo_generator/
COPY docker_images/live_demo_generator/uv.lock docker_images/live_demo_generator/
RUN uv --project docker_images/live_demo_generator sync --locked --no-dev

COPY docker_images/live_demo_generator/scheduler.py docker_images/live_demo_generator/worker.py docker_images/live_demo_generator/

CMD ["uv", "--project", "docker_images/live_demo_generator", "run", "python3", "docker_images/live_demo_generator/worker.py"]
