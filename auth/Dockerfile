FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

RUN apt-get update && apt-get install -y libsodium-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY tools tools
COPY optscale_client optscale_client

COPY auth/__init__.py auth/__init__.py
COPY auth/pyproject.toml auth/pyproject.toml
COPY auth/uv.lock auth/uv.lock

COPY auth/auth_server/alembic auth/auth_server/alembic
COPY auth/auth_server/controllers auth/auth_server/controllers
COPY auth/auth_server/handlers auth/auth_server/handlers
COPY auth/auth_server/auth_token auth/auth_server/auth_token
COPY auth/auth_server/models auth/auth_server/models
COPY auth/auth_server/*.py ./auth/auth_server/
COPY auth/auth_server/alembic.template auth/auth_server/alembic.template
COPY auth/auth_server/swagger auth/auth_server/swagger

COPY auth/pyproject.toml auth/pyproject.toml
COPY auth/uv.lock auth/uv.lock

RUN uv --project auth sync --locked --no-dev
RUN uv --project auth run python -u auth/auth_server/write_spec.py

CMD ["uv", "--project", "auth", "run", "python", "-u", "/usr/src/app/auth/auth_server/server.py"]
EXPOSE 8905
