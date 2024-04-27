FROM python:3.12.3-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /src
RUN mkdir -p /src/archive

COPY optscale_client/config_client optscale_client/config_client
COPY docker_images/cleanmongodb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_images/cleanmongodb/clean-mongo-db.py .

CMD ["python", "/src/clean-mongo-db.py"]
