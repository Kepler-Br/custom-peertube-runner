FROM node:18

RUN npm install -g @peertube/peertube-runner

RUN apt update && apt install ffmpeg -y && rm -rf /var/lib/apt/lists/*

COPY ffmpeg_wrapper.py /usr/local/bin/ffmpeg

ENV PATH="/usr/local/bin:$PATH"

COPY ca.crt /home/node/localhost.ca.crt

RUN cp /home/node/localhost.ca.crt /usr/local/share/ca-certificates && update-ca-certificates

USER 1000
ENV NODE_OPTIONS=--use-openssl-ca
USER 0
ENV NODE_OPTIONS=--use-openssl-ca
