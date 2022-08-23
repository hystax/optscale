FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/insider_worker
ENV PYTHONPATH=/usr/src/app/

COPY insider_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY insider_worker/*.py ./
COPY insider_worker/migrations migrations
COPY insider_worker/processors processors
COPY insider_worker/http_client http_client

CMD ["python", "-u","/usr/src/app/insider_worker/main.py"]
