FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY bumischeduler/requirements.txt ./bumischeduler/requirements.txt
RUN pip install --no-cache-dir -r bumischeduler/requirements.txt
COPY bumischeduler/*.py ./bumischeduler/
COPY bumischeduler/bumischeduler/controllers bumischeduler/bumischeduler/controllers
COPY bumischeduler/bumischeduler/*.py ./bumischeduler/bumischeduler/

CMD ["python", "-u","/usr/src/app/bumischeduler/bumischeduler/main.py"]
