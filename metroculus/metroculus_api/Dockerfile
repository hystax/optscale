FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY tools/cloud_adapter tools/cloud_adapter

COPY metroculus/metroculus_api/requirements.txt metroculus/metroculus_api/requirements.txt
RUN pip install --no-cache-dir -r metroculus/metroculus_api/requirements.txt
COPY metroculus/metroculus_api/controllers metroculus/metroculus_api/controllers
COPY metroculus/metroculus_api/handlers metroculus/metroculus_api/handlers
COPY metroculus/metroculus_api/swagger metroculus/metroculus_api/swagger
COPY metroculus/metroculus_api/*.py metroculus/metroculus_api/
RUN python -u metroculus/metroculus_api/write_spec.py

CMD ["python", "-u","/usr/src/app/metroculus/metroculus_api/server.py"]
EXPOSE 8969
