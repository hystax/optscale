FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY tools/optscale_time tools/optscale_time

COPY docker_images/failed_imports_dataset_generator/pyproject.toml docker_images/failed_imports_dataset_generator/
COPY docker_images/failed_imports_dataset_generator/uv.lock docker_images/failed_imports_dataset_generator/
RUN uv --project docker_images/failed_imports_dataset_generator sync --locked --no-dev

COPY docker_images/failed_imports_dataset_generator/failed_imports_dataset_generator.py docker_images/failed_imports_dataset_generator/

CMD ["uv", "--project", "docker_images/failed_imports_dataset_generator", "run", "python", "docker_images/failed_imports_dataset_generator/failed_imports_dataset_generator.py"]
