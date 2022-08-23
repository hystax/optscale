FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/herald_server

COPY requirements.txt .
RUN apt-get update && apt-get install \
    && apt-get install -y libsodium-dev libssl-dev sendmail \
    && pip install --no-cache-dir -r /usr/src/app/herald_server/requirements.txt \
    && apt-get remove -y libssl-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY herald_server/alembic ./alembic
COPY herald_server/controllers ./controllers
COPY herald_server/handlers ./handlers
COPY herald_server/processors ./processors
COPY herald_server/models ./models
COPY herald_server/worker ./worker
COPY herald_server/*.py run.py ./
COPY herald_server/alembic.template .
COPY modules ../modules

ENV PYTHONPATH /usr/src/app/
CMD ["python", "-u", "run.py"]
EXPOSE 8906
