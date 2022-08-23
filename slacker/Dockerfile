FROM optscale_python:local
WORKDIR /src
ENV PYTHONPATH=/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY slacker_server/swagger slacker_server/swagger
COPY slacker_server/alembic.template slacker_server/
COPY slacker_server/*.py slacker_server/
COPY slacker_server/alembic slacker_server/alembic
COPY slacker_server/models slacker_server/models
COPY slacker_server/message_templates slacker_server/message_templates
COPY slacker_server/handlers slacker_server/handlers
COPY slacker_server/controllers slacker_server/controllers
RUN python -u slacker_server/write_spec.py

CMD ["python", "/src/slacker_server/server.py"]
