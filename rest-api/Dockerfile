FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/rest_api_server
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt .
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir \
    -r /usr/src/app/rest_api_server/requirements.txt

COPY live_demo.json ./
COPY rest_api_server/alembic ./alembic
COPY rest_api_server/controllers ./controllers
COPY rest_api_server/handlers ./handlers
COPY rest_api_server/models ./models
COPY rest_api_server/*.py ./
COPY rest_api_server/alembic.template .
COPY rest_api_server/swagger ./swagger
COPY rest_api_server/recommendation_cleanup_scripts ./recommendation_cleanup_scripts
RUN python -u write_spec.py

CMD ["python", "-u","/usr/src/app/rest_api_server/server.py"]
EXPOSE 8999
