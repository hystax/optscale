FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/
COPY katara/katara_worker/requirements.txt .


COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY optscale_client/katara_client optscale_client/katara_client

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/katara/katara_worker

COPY katara/katara_worker/reports_generators ./reports_generators
COPY katara/katara_worker/*.py ./

CMD ["python", "-u","/usr/src/app/katara/katara_worker/main.py"]
