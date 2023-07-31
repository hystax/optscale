FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/risp_worker
ENV PYTHONPATH=/usr/src/app/

ADD risp_worker/migrations ./migrations
COPY risp_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY risp_worker/*.py ./

CMD ["python", "-u", "/usr/src/app/risp_worker/worker.py"]
