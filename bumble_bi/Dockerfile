FROM optscale_python:local
MAINTAINER Hystax

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/src/app/

WORKDIR /usr/src/app/bumblebi
COPY requirements.txt ..

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY ./bumblebi ./

CMD ["python", "-u","/usr/src/app/bumblebi/exporter/main.py"]
