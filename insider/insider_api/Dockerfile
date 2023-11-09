FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/cloud_adapter tools/cloud_adapter

COPY insider/insider_api/requirements.txt insider/insider_api/requirements.txt
RUN pip install --no-cache-dir -r insider/insider_api/requirements.txt
COPY insider/insider_api/controllers insider/insider_api/controllers
COPY insider/insider_api/handlers insider/insider_api/handlers
COPY insider/insider_api/swagger insider/insider_api/swagger
COPY insider/insider_api/*.py insider/insider_api/
COPY insider/*.py insider/
RUN python -u insider/insider_api/write_spec.py

CMD ["python", "-u","/usr/src/app/insider/insider_api/server.py"]
EXPOSE 8945
