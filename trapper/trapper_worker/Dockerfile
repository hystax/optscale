FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/cloud_adapter tools/cloud_adapter
COPY trapper/trapper_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY trapper/trapper_worker/*.py ./trapper/trapper_worker/

CMD ["python", "-u","/usr/src/app/trapper/trapper_worker/main.py"]
