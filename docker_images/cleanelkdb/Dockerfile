FROM python:3.12.11-slim
LABEL org.opencontainers.image.authors="Hystax"

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y jq curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY docker_images/cleanelkdb/clean-elk-db.sh /src/clean-elk-db.sh

CMD ["sh", "/src/clean-elk-db.sh"]