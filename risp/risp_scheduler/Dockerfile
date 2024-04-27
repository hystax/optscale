FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY risp/risp_scheduler/requirements.txt risp/risp_scheduler/requirements.txt
RUN pip install --no-cache-dir -r risp/risp_scheduler/requirements.txt
COPY risp/risp_scheduler/*.py risp/risp_scheduler/

CMD ["python", "-u","/usr/src/app/risp/risp_scheduler/scheduler.py"]
