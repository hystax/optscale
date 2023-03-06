FROM acura-dr.dts.loc/optscale_python:94098b67b949e2fabcc2404becf90a25f77496e6
MAINTAINER Hystax

WORKDIR /usr/src/app/pharos_receiver
ENV PYTHONPATH /usr/src/app/

COPY pharos_receiver/requirements.txt ./requirements.txt
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
COPY pharos_receiver/controllers ./controllers
COPY pharos_receiver/handlers ./handlers
COPY pharos_receiver/*.py ./

CMD ["python", "-u", "/usr/src/app/pharos_receiver/server.py"]
EXPOSE 8946