FROM quay.io/coreos/etcd:v3.2.13
RUN apk update
RUN apk --no-cache add curl
RUN wget $(curl -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/nexusriot/etcd-walker/releases/tags/0.0.8 | grep -Eo 'https://(.*linux_x64_static)') -O /bin/etcd-walker
RUN chmod +x /bin/etcd-walker
