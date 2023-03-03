FROM optscale_python:local
MAINTAINER Hystax

WORKDIR /usr/src/app/diproxy
ENV PYTHONPATH /usr/src/app/

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/diproxy/requirements.txt
COPY diproxy/*.py ./
COPY diproxy/swagger ./swagger

RUN python -u write_spec.py

CMD ["python", "-u","/usr/src/app/diproxy/main.py"]
EXPOSE 8935
