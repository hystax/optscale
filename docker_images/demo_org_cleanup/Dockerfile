FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/demo_org_cleanup/pyproject.toml docker_images/demo_org_cleanup/
COPY docker_images/demo_org_cleanup/uv.lock docker_images/demo_org_cleanup/
RUN uv --project docker_images/demo_org_cleanup sync --locked --no-dev

COPY docker_images/demo_org_cleanup/cleanup.py docker_images/demo_org_cleanup/

CMD ["uv", "--project", "docker_images/demo_org_cleanup", "run", "python3", "docker_images/demo_org_cleanup/cleanup.py"]
