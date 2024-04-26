FROM python:3.12.3-slim

ENV PYTHONPATH /usr/src/app/

WORKDIR /usr/src/app/
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY docker_images/booking_observer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY docker_images/booking_observer/scheduler.py docker_images/booking_observer/worker.py docker_images/booking_observer/

CMD ["python3", "docker_images/booking_observer/worker.py"]
