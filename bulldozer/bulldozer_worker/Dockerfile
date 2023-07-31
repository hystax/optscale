FROM optscale_python:local
MAINTAINER Hystax

RUN mkdir -p /var/lib/bulldozer
WORKDIR /usr/src/app/bulldozer_worker
ENV PYTHONPATH=/usr/src/app/

COPY bulldozer_worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY bulldozer_worker/*.py ./
COPY bulldozer_worker/.terraform .terraform
COPY bulldozer_worker/generator generator
COPY bulldozer_worker/locks locks
COPY bulldozer_worker/variables variables
COPY bulldozer_worker/terraform ./terraform
RUN chmod +x ./terraform

CMD ["python", "-u","/usr/src/app/bulldozer_worker/main.py"]
