FROM python:3.9.16-slim
MAINTAINER Hystax

RUN mkdir -p /var/lib/bulldozer
WORKDIR /usr/src/app/bulldozer_worker
ENV PYTHONPATH=/usr/src/app/

COPY bulldozer/bulldozer_worker/requirements.txt ./requirements.txt

COPY optscale_client/arcee_client optscale_client/arcee_client
COPY optscale_client/bulldozer_client optscale_client/bulldozer_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/restapi_client



RUN pip install --no-cache-dir -r requirements.txt
COPY bulldozer/bulldozer_worker/*.py ./
COPY bulldozer/bulldozer_worker/.terraform .terraform
COPY bulldozer/bulldozer_worker/generator generator
COPY bulldozer/bulldozer_worker/locks locks
COPY bulldozer/bulldozer_worker/variables variables
COPY bulldozer/bulldozer_worker/terraform ./terraform
RUN chmod +x ./terraform

CMD ["python", "-u","/usr/src/app/bulldozer_worker/main.py"]
