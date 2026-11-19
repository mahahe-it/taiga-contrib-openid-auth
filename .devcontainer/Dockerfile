FROM mcr.microsoft.com/devcontainers/base:trixie

# One image, two uses: the VS Code devcontainer and the `mahahe-taiga-openid`
# distrobox (`just toolbox`). Bump a version here, then rebuild.
# Images are built and run with the host's podman (or docker in the
# devcontainer and CI), not from this image.

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# apt (Debian-packaged)
ARG PIPX_VERSION=1.7.1*
ARG JQ_VERSION=1.7.1*
# single-file release binaries
# renovate: datasource=github-releases depName=casey/just
ARG JUST_VERSION=1.59.0
# renovate: datasource=github-releases depName=cli/cli extractVersion=^v(?<version>.+)$
ARG GH_VERSION=2.105.0
# pipx (global: /opt/pipx, bins in /usr/local/bin, so the host user finds
# them too when the image runs as a distrobox)
# renovate: datasource=pypi depName=pre-commit
ARG PRE_COMMIT_VERSION=4.7.0
# renovate: datasource=pypi depName=pytest
ARG PYTEST_VERSION=9.2.0

RUN apt-get update && apt-get -y install --no-install-recommends \
    pipx=${PIPX_VERSION} \
    jq=${JQ_VERSION} \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    curl -fsSL https://github.com/casey/just/releases/download/${JUST_VERSION}/just-${JUST_VERSION}-x86_64-unknown-linux-musl.tar.gz \
      | tar -xz -C /usr/local/bin just; \
    curl -fsSL https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz \
      | tar -xz -C /usr/local/bin --strip-components=2 gh_${GH_VERSION}_linux_amd64/bin/gh

RUN set -eux; \
    pipx install --global pre-commit==${PRE_COMMIT_VERSION}; \
    pipx install --global pytest==${PYTEST_VERSION}; \
    rm -rf /root/.cache
