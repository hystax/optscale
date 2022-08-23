FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/auth_server
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt .
RUN apt-get update && apt-get install -y libsodium-dev \
    && pip install --no-cache-dir -r /usr/src/app/auth_server/requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY auth_server/alembic ./alembic
COPY auth_server/controllers ./controllers
COPY auth_server/handlers ./handlers
COPY auth_server/auth_token ./auth_token
COPY auth_server/models ./models
COPY auth_server/*.py ./
COPY auth_server/alembic.template .
COPY auth_server/swagger ./swagger
RUN python -u write_spec.py

CMD ["python", "-u","/usr/src/app/auth_server/server.py"]
EXPOSE 8905
