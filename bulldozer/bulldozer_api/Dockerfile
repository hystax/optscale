FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/bulldozer_api
ENV PYTHONPATH /usr/src/app/

COPY bulldozer_api/requirements.txt .
RUN pip install --no-cache-dir -r /usr/src/app/bulldozer_api/requirements.txt

COPY bulldozer_api/* ./

CMD ["python", "-u","/usr/src/app/bulldozer_api/server.py"]
EXPOSE 8896
