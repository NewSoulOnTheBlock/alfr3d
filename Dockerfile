# alfr3d — clean-room image built from source (no upstream base image).
FROM python:3.10-slim-bullseye

ARG TZ='UTC'
ENV BUILD_PREFIX=/app

ADD . ${BUILD_PREFIX}

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ffmpeg espeak libavcodec-extra \
    && cd ${BUILD_PREFIX} \
    && cp config-template.json config.json \
    && /usr/local/bin/python -m pip install --no-cache --upgrade pip \
    && pip install --no-cache -r requirements.txt \
    && pip install --no-cache -e . \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /home/agent/alfr3d \
    && groupadd -r agent \
    && useradd -r -g agent -s /bin/bash -d /home/agent agent \
    && chown -R agent:agent /home/agent ${BUILD_PREFIX}

WORKDIR ${BUILD_PREFIX}

ADD docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && chown agent:agent /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
