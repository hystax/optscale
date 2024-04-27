FROM python:3.12.3-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY docker_images/demo_org_cleanup/requirements.txt docker_images/demo_org_cleanup/
RUN pip install --no-cache-dir -r docker_images/demo_org_cleanup/requirements.txt

COPY docker_images/demo_org_cleanup/cleanup.py docker_images/demo_org_cleanup/

CMD ["python3", "docker_images/demo_org_cleanup/cleanup.py"]
