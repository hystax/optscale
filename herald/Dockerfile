FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/

RUN apt-get update && apt-get install \
    && apt-get install -y libsodium-dev libssl-dev sendmail \
    && apt-get remove -y libssl-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY herald/requirements.txt .
COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/herald/herald_server

COPY herald/herald_server/alembic ./alembic
COPY herald/herald_server/controllers ./controllers
COPY herald/herald_server/handlers ./handlers
COPY herald/herald_server/processors ./processors
COPY herald/herald_server/models ./models
COPY herald/herald_server/worker ./worker
COPY herald/herald_server/*.py herald/run.py ./
COPY herald/herald_server/alembic.template .
COPY herald/modules ../modules

ENV PYTHONPATH /usr/src/app/
CMD ["python", "-u", "run.py"]
EXPOSE 8906
