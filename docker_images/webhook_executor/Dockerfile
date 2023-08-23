FROM python:3.9.16-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/webhook_executor/requirements.txt docker_images/webhook_executor/
RUN pip install --no-cache-dir -r docker_images/webhook_executor/requirements.txt

COPY docker_images/webhook_executor/worker.py docker_images/webhook_executor/

CMD ["python3", "docker_images/webhook_executor/worker.py"]
