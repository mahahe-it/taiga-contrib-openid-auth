ARG TAIGA_BACK_VERSION=6.10.2
FROM docker.io/taigaio/taiga-back:${TAIGA_BACK_VERSION} AS base
COPY back/ /tmp/taiga-contrib-openid-auth/
RUN pip install --no-cache-dir /tmp/taiga-contrib-openid-auth \
 && rm -rf /tmp/taiga-contrib-openid-auth
COPY docker/back/openid.py /taiga-back/settings/openid.py
ENV DJANGO_SETTINGS_MODULE=settings.openid

# Unit tests against the installed plugin and taiga-back: `just test-back`
FROM base AS test
# Keep in step with taiga-back's requirements-devel.txt
RUN pip install --no-cache-dir pytest==9.0.1 pytest-django==4.11.1
# taiga-back refuses to load settings without a secret key (a dummy one here)
# hadolint ignore=DL3064
ENV TAIGA_SECRET_KEY=unit-tests
COPY back/tests /tests
ENTRYPOINT []
CMD ["python", "-m", "pytest", "-c", "/tests/pytest.ini", "--rootdir", "/tests", "/tests"]

FROM base
