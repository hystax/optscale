FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

COPY optscale_client optscale_client
COPY tools tools

COPY bumiworker/pyproject.toml bumiworker/pyproject.toml
COPY bumiworker/uv.lock bumiworker/uv.lock
COPY bumiworker/requirements-azure.txt bumiworker/requirements-azure.txt
COPY bumiworker/bumiworker/modules ./bumiworker/bumiworker/modules
COPY bumiworker/bumiworker/*.py ./bumiworker/bumiworker/
COPY bumiworker/*.py ./bumiworker/

RUN uv --project bumiworker sync --locked --no-dev
# Install the fork's net-new Azure SDK pins (see header in
# requirements-azure.txt) into the bumiworker venv. Kept separate from
# the upstream pyproject so monthly upstream rebases don't churn this
# list. All other azure-mgmt-* + azure-identity versions resolve
# transitively from tools/cloud_adapter.
RUN uv pip install --python bumiworker/.venv/bin/python --no-cache-dir -r bumiworker/requirements-azure.txt

CMD ["uv", "run", "--project", "bumiworker", "python", "-u","/usr/src/app/bumiworker/bumiworker/main.py"]
