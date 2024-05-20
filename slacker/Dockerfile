FROM python:3.12.3-slim
WORKDIR /src
ENV PYTHONPATH=/src

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY slacker/requirements.txt slacker/requirements.txt
RUN pip install --no-cache-dir -r slacker/requirements.txt

COPY slacker/slacker_server/swagger slacker/slacker_server/swagger
COPY slacker/slacker_server/alembic.template slacker/slacker_server/
COPY slacker/slacker_server/*.py slacker/slacker_server/
COPY slacker/slacker_server/alembic slacker/slacker_server/alembic
COPY slacker/slacker_server/models slacker/slacker_server/models
COPY slacker/slacker_server/message_templates slacker/slacker_server/message_templates
COPY slacker/slacker_server/handlers slacker/slacker_server/handlers
COPY slacker/slacker_server/controllers slacker/slacker_server/controllers
RUN python -u slacker/slacker_server/write_spec.py

CMD ["python", "/src/slacker/slacker_server/server.py"]
