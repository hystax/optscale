FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/insider_api
ENV PYTHONPATH /usr/src/app/

COPY insider_api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY insider_api/controllers ./controllers
COPY insider_api/handlers ./handlers
COPY insider_api/swagger ./swagger
COPY insider_api/*.py ./
RUN python -u write_spec.py

CMD ["python", "-u","/usr/src/app/insider_api/server.py"]
EXPOSE 8945
