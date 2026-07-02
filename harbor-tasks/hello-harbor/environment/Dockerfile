FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY data.json /app/data.json