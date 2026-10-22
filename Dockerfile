FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY monitor.sh .
RUN chmod +x monitor.sh

ENV STATUS_DIR=/app/run_status
ENV POLL_INTERVAL_SEC=5

ENTRYPOINT ["./monitor.sh"]
