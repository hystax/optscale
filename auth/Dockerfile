FROM python:3.12.3-slim
#test
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

RUN apt-get update && apt-get install -y libsodium-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY auth/zoho_integrator auth/zoho_integrator

COPY auth/requirements.txt auth/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/auth/requirements.txt

COPY auth/auth_server/alembic auth/auth_server/alembic
COPY auth/auth_server/controllers auth/auth_server/controllers
COPY auth/auth_server/handlers auth/auth_server/handlers
COPY auth/auth_server/auth_token auth/auth_server/auth_token
COPY auth/auth_server/models auth/auth_server/models
COPY auth/auth_server/*.py ./auth/auth_server/
COPY auth/auth_server/alembic.template auth/auth_server/alembic.template
COPY auth/auth_server/swagger auth/auth_server/swagger
RUN python -u auth/auth_server/write_spec.py

CMD ["python", "-u","/usr/src/app/auth/auth_server/server.py"]
EXPOSE 8905
