FROM python:3.9.16-slim
MAINTAINER Hystax

ENV PYTHONPATH /usr/src/app/
WORKDIR /usr/src/app/

COPY pharos_backend/pharos_receiver/requirements.txt ./requirements.txt

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client

RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /usr/src/app/pharos_backend/pharos_receiver

COPY pharos_backend/pharos_receiver/controllers ./controllers
COPY pharos_backend/pharos_receiver/handlers ./handlers
COPY pharos_backend/pharos_receiver/*.py ./

CMD ["python", "-u", "/usr/src/app/pharos_backend/pharos_receiver/server.py"]
EXPOSE 8946
