FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/subspector_async_client optscale_client/subspector_async_client
COPY tools/stripe_client tools/stripe_client

COPY docker_images/subsyncer/pyproject.toml docker_images/subsyncer/
COPY docker_images/subsyncer/uv.lock docker_images/subsyncer/
RUN uv --project docker_images/subsyncer sync --locked --no-dev

COPY docker_images/subsyncer/subsyncer.py docker_images/subsyncer/

CMD ["uv", "--project", "docker_images/subsyncer", "run", "python3", "docker_images/subsyncer/subsyncer.py"]
