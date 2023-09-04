FROM python:3.9.16-slim
MAINTAINER Hystax

WORKDIR /src

RUN apt-get update \
    && apt-get install -y jq \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY docker_images/cleanelkdb/clean-elk-db.sh .

CMD ["sh", "/src/clean-elk-db.sh"]
