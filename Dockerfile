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

# --- Optional: QuickBooks Online MCP server (Node/stdio) --------------------
# Off by default to keep the image lean. Enable with:
#   docker build --build-arg INSTALL_QUICKBOOKS=true .
# The server is Node/ESM and speaks MCP over stdio, so it must live inside this
# image (a stdio server is a subprocess of the agent, not a sidecar).
ARG INSTALL_QUICKBOOKS=false
ARG QUICKBOOKS_MCP_REPO=https://github.com/intuit/quickbooks-online-mcp-server.git
ARG QUICKBOOKS_MCP_REF=main
ENV QUICKBOOKS_MCP_HOME=/opt/quickbooks-mcp
RUN if [ "$INSTALL_QUICKBOOKS" = "true" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends curl ca-certificates git \
        && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
        && apt-get install -y --no-install-recommends nodejs \
        && git clone "$QUICKBOOKS_MCP_REPO" "$QUICKBOOKS_MCP_HOME" \
        && cd "$QUICKBOOKS_MCP_HOME" \
        && git checkout "$QUICKBOOKS_MCP_REF" \
        && npm install \
        && npm run build \
        && chown -R agent:agent "$QUICKBOOKS_MCP_HOME" \
        && rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR ${BUILD_PREFIX}

ADD docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && chown agent:agent /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
