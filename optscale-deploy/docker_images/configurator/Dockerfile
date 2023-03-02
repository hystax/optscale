FROM hystax/optscale_python:94098b67b949e2fabcc2404becf90a25f77496e6
MAINTAINER Hystax

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY configurator.py .

CMD ["python", "/src/configurator.py", "/config/config"]
