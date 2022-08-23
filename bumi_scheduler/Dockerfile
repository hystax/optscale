FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/bumi_scheduler
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/bumi_scheduler/requirements.txt
COPY bumi_scheduler/controllers ./controllers
COPY bumi_scheduler/*.py ./

CMD ["python", "-u","/usr/src/app/bumi_scheduler/main.py"]
