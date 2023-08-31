FROM python:3.9.16-slim
MAINTAINER Hystax

RUN mkdir -p /var/lib/bulldozer
WORKDIR /usr/src/app/bulldozer/bulldozer_worker
ENV PYTHONPATH=/usr/src/app/

COPY bulldozer/bulldozer_worker/.terraform .terraform
RUN tar xvzf .terraform/providers/registry.terraform.io/hashicorp/aws/4.60.0/linux_amd64/terraform-provider-aws_v4.60.0_x5.tar.gz --directory .terraform/providers/registry.terraform.io/hashicorp/aws/4.60.0/linux_amd64/
RUN rm .terraform/providers/registry.terraform.io/hashicorp/aws/4.60.0/linux_amd64/terraform-provider-aws_v4.60.0_x5.tar.gz
COPY bulldozer/bulldozer_worker/terraform ./terraform
RUN chmod +x ./terraform

COPY bulldozer/bulldozer_worker/requirements.txt ./requirements.txt

WORKDIR /usr/src/app/
COPY optscale_client/arcee_client optscale_client/arcee_client
COPY optscale_client/bulldozer_client optscale_client/bulldozer_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

RUN pip install --no-cache-dir -r bulldozer/bulldozer_worker/requirements.txt
COPY bulldozer/bulldozer_worker/*.py bulldozer/bulldozer_worker/
COPY bulldozer/bulldozer_worker/generator bulldozer/bulldozer_worker/generator
COPY bulldozer/bulldozer_worker/locks bulldozer/bulldozer_worker/locks
COPY bulldozer/bulldozer_worker/variables bulldozer/bulldozer_worker/variables

CMD ["python", "-u","/usr/src/app/bulldozer/bulldozer_worker/main.py"]
