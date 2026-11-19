# renovate: datasource=docker depName=taigaio/taiga-front
ARG TAIGA_FRONT_VERSION=6.10.3
FROM docker.io/taigaio/taiga-front:${TAIGA_FRONT_VERSION}
ENV OPENID_SCOPE="openid email"

COPY docker/front/conf.json.template /usr/share/nginx/html/conf.json.template
COPY docker/front/30_config_env_subst.sh /docker-entrypoint.d/30_config_env_subst.sh
COPY front/dist/. /tmp/

RUN mkdir -p /usr/share/nginx/html/plugins/openid-auth \
 && cp -r /tmp/* /usr/share/nginx/html/plugins/openid-auth
