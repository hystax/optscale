FROM optscale_python:local
WORKDIR /src
ENV PYTHONPATH=/src

COPY requirements.txt .
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
COPY diworker diworker

CMD ["/src/diworker/main.py"]
