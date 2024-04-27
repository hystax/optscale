FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /src

COPY docker_images/cleaninfluxdb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_images/cleaninfluxdb/clean-influx-db.py .

CMD ["python", "/src/clean-influx-db.py"]
