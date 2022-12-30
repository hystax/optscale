FROM python:3.9.1-alpine3.12

RUN set -ex \
    && apk add --no-cache ca-certificates openssl apache2-utils bash wget curl \
    && wget -O /bin/registry https://github.com/docker/distribution-library-image/raw/0b6ea3ba50b65563600a717f07db4cfa6f18f957/amd64/registry \
    && chmod 755 /bin/registry \
    && wget -O helm_install.sh https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get \
    && bash helm_install.sh -v v2.17.0 \
    && helm init -c

COPY docker_images/optscale_registry/config.yaml /etc/docker/registry/config.yml
COPY docker_images/optscale_registry/pip.conf /etc/pip.conf
COPY docker_images/optscale_registry/docker-entrypoint.sh /entrypoint.sh

COPY runkube_requirements.txt .

RUN pip3 install -r runkube_requirements.txt

COPY optscale /optscale
COPY overlay /overlay
COPY runkube.py cluster_info.py /

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/etc/docker/registry/config.yml"]
