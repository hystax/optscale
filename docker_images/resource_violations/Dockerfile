FROM python:3.12.3-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/resource_violations/requirements.txt docker_images/resource_violations/
RUN pip install --no-cache-dir -r docker_images/resource_violations/requirements.txt

COPY docker_images/resource_violations/scheduler.py docker_images/resource_violations/worker.py docker_images/resource_violations/

CMD ["python3", "docker_images/resource_violations/worker.py"]
