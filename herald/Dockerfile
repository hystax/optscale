FROM python:3.12.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

RUN apt-get update && apt-get install \
    && apt-get install -y libsodium-dev libssl-dev sendmail \
    && apt-get remove -y libssl-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY herald/pyproject.toml herald/pyproject.toml
COPY herald/uv.lock herald/uv.lock
COPY herald/__init__.py herald/__init__.py
COPY tools tools
COPY optscale_client optscale_client

RUN uv --project herald sync --locked --no-dev

WORKDIR /usr/src/app/herald/herald_server

COPY herald/herald_server/alembic ./alembic
COPY herald/herald_server/controllers ./controllers
COPY herald/herald_server/handlers ./handlers
COPY herald/herald_server/processors ./processors
COPY herald/herald_server/models ./models
COPY herald/herald_server/worker ./worker
COPY herald/herald_server/*.py herald/run.py ./
COPY herald/herald_server/alembic.template .
COPY herald/modules/email_generator ../modules/email_generator
COPY herald/modules/email_sender ../modules/email_sender

CMD ["uv", "run", "--project", "/usr/src/app/herald", "python", "-u", "run.py"]
EXPOSE 8906
