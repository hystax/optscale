FROM python:3.12.3-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/slacker_client optscale_client/slacker_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/slacker_executor/requirements.txt docker_images/slacker_executor/
RUN pip install --no-cache-dir -r docker_images/slacker_executor/requirements.txt

COPY docker_images/slacker_executor/worker.py docker_images/slacker_executor/

CMD ["python3", "docker_images/slacker_executor/worker.py"]
