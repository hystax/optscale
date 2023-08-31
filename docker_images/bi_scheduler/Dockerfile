FROM python:3.9.16-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY docker_images/bi_scheduler/requirements.txt docker_images/bi_scheduler/
RUN pip install --no-cache-dir -r docker_images/bi_scheduler/requirements.txt

WORKDIR /usr/src/app/docker_images/bi_scheduler/
COPY docker_images/bi_scheduler/scheduler.py .

CMD ["python3", "scheduler.py"]
