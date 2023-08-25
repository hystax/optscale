FROM python:3.9.16-slim
MAINTAINER Hystax

WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY optscale_client/config_client optscale_client/config_client

COPY insider/insider_scheduler/requirements.txt insider/insider_scheduler/requirements.txt
RUN pip install --no-cache-dir -r insider/insider_scheduler/requirements.txt
COPY insider/insider_scheduler/*.py ./insider/insider_scheduler/

CMD ["python", "-u","/usr/src/app/insider/insider_scheduler/main.py"]
