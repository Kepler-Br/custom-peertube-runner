FROM node:18

ENV NODE_OPTIONS=--use-openssl-ca

RUN npm install -g @peertube/peertube-runner

RUN apt update && apt install ffmpeg -y && rm -rf /var/lib/apt/lists/*

COPY ffmpeg_wrapper.py /usr/local/bin/ffmpeg

ENV PATH="/usr/local/bin:$PATH"

COPY ./ca.crt /usr/local/share/ca-certificates/custom.ca.crt

RUN update-ca-certificates
