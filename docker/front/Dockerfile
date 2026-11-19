ARG NODE_VERSION=26.13.1-alpine
ARG TAIGA_FRONT_VERSION=6.10.3

# The plugin's dist/ (CoffeeScript/Pug through gulp), never committed
FROM docker.io/library/node:${NODE_VERSION} AS build
WORKDIR /build
COPY front/package.json front/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY front/ ./
RUN npx gulp copy-config copy-images compile

FROM docker.io/taigaio/taiga-front:${TAIGA_FRONT_VERSION}
# Keep in step with the Alpine release of the base image
RUN apk add --no-cache jq=1.6-r2
COPY --from=build /build/dist/ /usr/share/nginx/html/plugins/openid-auth/
# Around upstream's 30_config_env_subst.sh: see the scripts
COPY docker/front/29_openid_marker.sh docker/front/40_openid_config.sh /docker-entrypoint.d/
