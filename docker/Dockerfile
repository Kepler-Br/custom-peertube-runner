FROM prv.docker.dw/node:18

RUN npm install -g @peertube/peertube-runner

RUN apt update && apt install ffmpeg -y && rm -rf /var/lib/apt/lists/*

COPY ffmpeg_wrapper.py /usr/local/bin/ffmpeg

ENV PATH="/usr/local/bin:$PATH"
