FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/insider_scheduler
ENV PYTHONPATH=/usr/src/app/

COPY insider_scheduler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY insider_scheduler/*.py ./

CMD ["python", "-u","/usr/src/app/insider_scheduler/main.py"]
