# etcd is a distroless image starting from v3.5, meaning we don't have access to a shell or package manager.
# this is why we use multi-stage builds to build and copy the binary into the final image.
# ref: https://github.com/GoogleContainerTools/distroless?tab=readme-ov-file#docker

FROM golang:1.24.6 AS build-etcd-walker

RUN git clone https://github.com/nexusriot/etcd-walker/ /tmp/etcd-walker-src

WORKDIR /tmp/etcd-walker-src
RUN git checkout 0.6.0
RUN go build -ldflags "-linkmode external -extldflags -static" -o etcd-walker cmd/etcd-walker/main.go

RUN mv etcd-walker /bin/etcd-walker
RUN chmod +x /bin/etcd-walker

# NOTE: v3.6+ require significant changes as they removed support for the V2 API, see https://etcd.io/docs/v3.6/upgrades/upgrade_3_6/
FROM gcr.io/etcd-development/etcd:v3.2.13

# newer etcd walker versions have v3  protocol by default
RUN mkdir -p /etc/etcd-walker && tee /etc/etcd-walker/config.json >/dev/null <<'EOF'
{
  "host": "127.0.0.1",
  "port": "2379",
  "protocol": "v2",
  "debug": false
}
EOF
COPY --from=build-etcd-walker /bin/etcd-walker /bin/etcd-walker
