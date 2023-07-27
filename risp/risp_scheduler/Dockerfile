FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/risp_scheduler
ENV PYTHONPATH=/usr/src/app/

COPY risp_scheduler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY risp_scheduler/*.py ./

CMD ["python", "-u","/usr/src/app/risp_scheduler/scheduler.py"]
