FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors = "Hystax"

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY tools/cloud_adapter tools/cloud_adapter
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY docker_images/power_schedule/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY docker_images/power_schedule/*.py docker_images/power_schedule/

CMD ["python3", "docker_images/power_schedule/worker.py"]
