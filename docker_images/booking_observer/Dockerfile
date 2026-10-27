FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/booking_observer/pyproject.toml docker_images/booking_observer/
COPY docker_images/booking_observer/uv.lock docker_images/booking_observer/
RUN uv --project docker_images/booking_observer sync --locked --no-dev

COPY docker_images/booking_observer/scheduler.py docker_images/booking_observer/worker.py docker_images/booking_observer/

CMD ["uv", "--project", "docker_images/booking_observer", "run", "python3", "docker_images/booking_observer/worker.py"]
