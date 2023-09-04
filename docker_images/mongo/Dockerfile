FROM mongo:3.6

RUN set -x \
  && apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates wget \
  && rm -rf /var/lib/apt/lists/* \
  && wget -O /usr/local/bin/peer-finder https://storage.googleapis.com/kubernetes-release/pets/peer-finder \
  && chmod +x /usr/local/bin/peer-finder \
  && apt-get purge -y --auto-remove ca-certificates wget

COPY docker_images/mongo/on-start.sh /on-start.sh
