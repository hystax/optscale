FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY diproxy/requirements.txt diproxy/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/diproxy/requirements.txt
COPY diproxy/*.py ./diproxy/
COPY diproxy/diproxy/*.py ./diproxy/diproxy/
COPY diproxy/diproxy/swagger diproxy/diproxy/swagger

RUN python -u diproxy/diproxy/write_spec.py

CMD ["python", "-u","/usr/src/app/diproxy/diproxy/main.py"]
EXPOSE 8935
