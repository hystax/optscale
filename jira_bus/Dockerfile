FROM optscale_python:local
WORKDIR /src
ENV PYTHONPATH=/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jira_bus_server/swagger jira_bus_server/swagger
COPY jira_bus_server/alembic.template jira_bus_server/
COPY jira_bus_server/*.py jira_bus_server/
COPY jira_bus_server/alembic jira_bus_server/alembic
COPY jira_bus_server/models jira_bus_server/models
COPY jira_bus_server/ui jira_bus_server/ui
COPY jira_bus_server/handlers jira_bus_server/handlers
COPY jira_bus_server/controllers jira_bus_server/controllers
COPY jira_bus_server/atlassian_client jira_bus_server/atlassian_client
RUN python -u jira_bus_server/write_spec.py

CMD ["python", "/src/jira_bus_server/server.py"]
