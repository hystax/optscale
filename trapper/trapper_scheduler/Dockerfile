FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/trapper_scheduler
ENV PYTHONPATH=/usr/src/app/

COPY trapper_scheduler/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY trapper_scheduler/*.py ./

CMD ["python", "-u","/usr/src/app/trapper_scheduler/main.py"]
