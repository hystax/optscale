FROM python:3.9.16-slim
MAINTAINER Hystax

WORKDIR /usr/src/app/bulldozer_api
ENV PYTHONPATH /usr/src/app/

COPY bulldozer/bulldozer_api/requirements.txt .

COPY optscale_client/aconfig_cl optscale_client/aconfig_cl
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/insider_client optscale_client/insider_client

RUN pip install --no-cache-dir -r /usr/src/app/bulldozer_api/requirements.txt

COPY bulldozer/bulldozer_api/* ./

CMD ["python", "-u","/usr/src/app/bulldozer_api/server.py"]
EXPOSE 8896
