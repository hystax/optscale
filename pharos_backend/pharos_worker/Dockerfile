FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY pharos_backend/pharos_worker/requirements.txt ./requirements.txt
COPY optscale_client/config_client optscale_client/config_client

RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /usr/src/app/pharos_backend/pharos_worker
COPY pharos_backend/pharos_worker/*.py ./

CMD ["python", "-u","/usr/src/app/pharos_backend/pharos_worker/worker.py"]
