FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/bumi_worker
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt ./requirements.txt
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
COPY bumi_worker/modules ./modules
COPY bumi_worker/*.py ./

CMD ["python", "-u","/usr/src/app/bumi_worker/main.py"]
