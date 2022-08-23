FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/metroculus_scheduler
ENV PYTHONPATH=/usr/src/app/

COPY metroculus_scheduler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY metroculus_scheduler/*.py ./

CMD ["python", "-u","/usr/src/app/metroculus_scheduler/main.py"]
