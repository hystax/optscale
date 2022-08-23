FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/metroculus_worker
ENV PYTHONPATH=/usr/src/app/

COPY metroculus_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY metroculus_worker/*.py ./
COPY metroculus_worker/migrations migrations

CMD ["python", "-u","/usr/src/app/metroculus_worker/main.py"]
