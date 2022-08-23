FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/trapper_worker
ENV PYTHONPATH=/usr/src/app/

COPY trapper_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY trapper_worker/*.py ./

CMD ["python", "-u","/usr/src/app/trapper_worker/main.py"]
