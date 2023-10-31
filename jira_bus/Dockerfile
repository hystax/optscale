FROM python:3.9.16-slim
WORKDIR /usr/src/app/
ENV PYTHONPATH=/usr/src/app/

COPY jira_bus/requirements.txt .

COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/auth_client optscale_client/auth_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client
COPY tools/optscale_exceptions tools/optscale_exceptions

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app/jira_bus/jira_bus_server

COPY jira_bus/jira_bus_server/swagger ./swagger
COPY jira_bus/jira_bus_server/alembic.template ./
COPY jira_bus/jira_bus_server/*.py ./
COPY jira_bus/jira_bus_server/alembic ./alembic
COPY jira_bus/jira_bus_server/models ./models
COPY jira_bus/jira_bus_server/ui ./ui
COPY jira_bus/jira_bus_server/handlers ./handlers
COPY jira_bus/jira_bus_server/controllers ./controllers
COPY jira_bus/jira_bus_server/atlassian_client ./atlassian_client

WORKDIR /usr/src/app/
RUN python -u jira_bus/jira_bus_server/write_spec.py


CMD ["python", "/usr/src/app/jira_bus/jira_bus_server/server.py"]
