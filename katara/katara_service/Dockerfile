FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/
COPY katara/katara_service/requirements.txt .

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client


RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/katara/katara_service

COPY katara/katara_service/alembic ./alembic
COPY katara/katara_service/controllers ./controllers
COPY katara/katara_service/handlers ./handlers
COPY katara/katara_service/models ./models
COPY katara/katara_service/*.py ./
COPY katara/katara_service/alembic.template .
COPY katara/katara_service/swagger ./swagger
WORKDIR /usr/src/app/
RUN python -u katara/katara_service/write_spec.py


CMD ["python", "-u","/usr/src/app/katara/katara_service/main.py"]
EXPOSE 8935
