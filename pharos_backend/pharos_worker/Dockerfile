FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/pharos_worker
ENV PYTHONPATH=/usr/src/app/

COPY pharos_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY pharos_worker/*.py ./

CMD ["python", "-u","/usr/src/app/pharos_worker/worker.py"]
