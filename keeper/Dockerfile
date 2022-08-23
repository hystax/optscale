FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/report_server
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt .
RUN  pip install --no-cache-dir -r /usr/src/app/report_server/requirements.txt
COPY report_server/controllers ./controllers
COPY report_server/handlers ./handlers
COPY report_server/swagger ./swagger
COPY report_server/*.py ./
RUN python -u write_spec.py

CMD ["python", "-u","/usr/src/app/report_server/server.py"]
EXPOSE 8973
