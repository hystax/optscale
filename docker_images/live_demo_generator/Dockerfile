FROM python:3.12.3-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/live_demo_generator/requirements.txt docker_images/live_demo_generator/
RUN pip install --no-cache-dir -r docker_images/live_demo_generator/requirements.txt

COPY docker_images/live_demo_generator/scheduler.py docker_images/live_demo_generator/worker.py docker_images/live_demo_generator/

CMD ["python3", "docker_images/live_demo_generator/worker.py"]
