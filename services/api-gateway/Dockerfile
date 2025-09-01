# Stage 1: Build etcdctl
FROM debian:stable-slim as etcdctl-builder

RUN apt-get update && apt-get install -y curl tar gzip && \
    curl -L https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-amd64.tar.gz -o etcd-v3.5.0-linux-amd64.tar.gz && \
    tar xzvf etcd-v3.5.0-linux-amd64.tar.gz --strip-components=1 etcd-v3.5.0-linux-amd64/etcdctl && \
    mv etcdctl /usr/local/bin/etcdctl && \
    rm etcd-v3.5.0-linux-amd64.tar.gz

# Stage 2: Final APISIX image
FROM apache/apisix:3.5.0-debian

COPY --from=etcdctl-builder /usr/local/bin/etcdctl /usr/local/bin/etcdctl

COPY config.yaml /usr/local/apisix/conf/config.yaml
