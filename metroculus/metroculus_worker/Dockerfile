FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/cloud_adapter tools/cloud_adapter

COPY metroculus/metroculus_worker/requirements.txt metroculus/metroculus_worker/requirements.txt
RUN pip install --no-cache-dir -r metroculus/metroculus_worker/requirements.txt
COPY metroculus/metroculus_worker/*.py ./metroculus/metroculus_worker/
COPY metroculus/metroculus_worker/migrations metroculus/metroculus_worker/migrations

CMD ["python", "-u","/usr/src/app/metroculus/metroculus_worker/main.py"]
