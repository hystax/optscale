FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/arcee_receiver
ENV PYTHONPATH /usr/src/app/

COPY arcee/arcee_receiver/requirements.txt .
COPY optscale_client/aconfig_cl optscale_client/aconfig_cl

RUN pip install --no-cache-dir -r /usr/src/app/arcee_receiver/requirements.txt

COPY arcee/arcee_receiver/migrations ./migrations
COPY arcee/arcee_receiver/*.py ./

CMD ["python", "-u","/usr/src/app/arcee_receiver/server.py"]
EXPOSE 8891
