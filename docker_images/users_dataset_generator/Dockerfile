FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY tools/optscale_data tools/optscale_data

COPY docker_images/users_dataset_generator/pyproject.toml docker_images/users_dataset_generator/
COPY docker_images/users_dataset_generator/uv.lock docker_images/users_dataset_generator/
RUN uv --project docker_images/users_dataset_generator sync --locked --no-dev

COPY docker_images/users_dataset_generator/users_dataset_generator.py docker_images/users_dataset_generator/

CMD ["uv", "--project", "docker_images/users_dataset_generator", "run", "python3", "docker_images/users_dataset_generator/users_dataset_generator.py"]
