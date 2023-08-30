FROM python:3.9.16-slim

WORKDIR /usr/src/app/
ENV PYTHONPATH /usr/src/app/

COPY tools/cloud_adapter tools/cloud_adapter
COPY tools/optscale_exceptions tools/optscale_exceptions
COPY tools/optscale_types tools/optscale_types

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/herald_client optscale_client/herald_client
COPY optscale_client/katara_client optscale_client/katara_client
COPY optscale_client/metroculus_client optscale_client/metroculus_client
COPY optscale_client/arcee_client optscale_client/arcee_client
COPY optscale_client/insider_client optscale_client/insider_client
COPY optscale_client/bulldozer_client optscale_client/bulldozer_client

COPY rest_api/live_demo.json rest_api/live_demo.json
COPY rest_api/google_calendar_client rest_api/google_calendar_client
COPY rest_api/rest_api_server/alembic rest_api/rest_api_server/alembic
COPY rest_api/rest_api_server/controllers rest_api/rest_api_server/controllers
COPY rest_api/rest_api_server/handlers rest_api/rest_api_server/handlers
COPY rest_api/rest_api_server/models rest_api/rest_api_server/models
COPY rest_api/rest_api_server/*.py rest_api/rest_api_server/
COPY rest_api/rest_api_server/alembic.template rest_api/rest_api_server/alembic.template
COPY rest_api/rest_api_server/swagger rest_api/rest_api_server/swagger
COPY rest_api/rest_api_server/recommendation_cleanup_scripts rest_api/rest_api_server/recommendation_cleanup_scripts

COPY rest_api/*.py rest_api/
COPY rest_api/requirements.txt rest_api/requirements.txt

RUN pip install --use-deprecated=legacy-resolver --no-cache-dir \
    -r rest_api/requirements.txt

RUN python -u rest_api/rest_api_server/write_spec.py

CMD ["python", "-u","/usr/src/app/rest_api/rest_api_server/server.py"]
EXPOSE 8999
