FROM python:3.9.16-slim

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY docker_images/calendar_observer/requirements.txt docker_images/calendar_observer/
RUN pip install --no-cache-dir -r docker_images/calendar_observer/requirements.txt

COPY docker_images/calendar_observer/scheduler.py docker_images/calendar_observer/worker.py docker_images/calendar_observer/

CMD ["python3", "docker_images/calendar_observer/worker.py"]
