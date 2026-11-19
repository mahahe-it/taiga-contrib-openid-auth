# renovate: datasource=docker depName=taigaio/taiga-back
ARG TAIGA_BACK_VERSION=6.10.2
FROM docker.io/taigaio/taiga-back:${TAIGA_BACK_VERSION}
ENV OPENID_SCOPE="openid email"
COPY docker/back/config.py.snippet /tmp
COPY back/. /tmp/

RUN pip install --no-cache-dir /tmp \
 && cat /tmp/config.py.snippet >> /taiga-back/settings/config.py
