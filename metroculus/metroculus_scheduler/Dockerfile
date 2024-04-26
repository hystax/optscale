FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY metroculus/metroculus_scheduler/requirements.txt metroculus/metroculus_scheduler/requirements.txt
RUN pip install --no-cache-dir -r metroculus/metroculus_scheduler/requirements.txt
COPY metroculus/metroculus_scheduler/*.py ./metroculus/metroculus_scheduler/

CMD ["python", "-u","/usr/src/app/metroculus/metroculus_scheduler/main.py"]
