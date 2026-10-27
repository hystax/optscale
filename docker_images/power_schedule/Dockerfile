FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/cloud_adapter tools/cloud_adapter

COPY docker_images/power_schedule/pyproject.toml docker_images/power_schedule/
COPY docker_images/power_schedule/uv.lock docker_images/power_schedule/
RUN uv --project docker_images/power_schedule sync --locked --no-dev

COPY docker_images/power_schedule/*.py docker_images/power_schedule/

CMD ["uv", "--project", "docker_images/power_schedule", "run", "python3", "docker_images/power_schedule/worker.py"]
