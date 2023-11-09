FROM python:3.9.16-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY keeper/requirements.txt .

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
RUN  pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/keeper/report_server
COPY keeper/report_server/controllers ./controllers
COPY keeper/report_server/handlers ./handlers
COPY keeper/report_server/swagger ./swagger
COPY keeper/report_server/*.py ./

WORKDIR /usr/src/app/
RUN python -u keeper/report_server/write_spec.py

CMD ["python", "-u","/usr/src/app/keeper/report_server/server.py"]
EXPOSE 8973
