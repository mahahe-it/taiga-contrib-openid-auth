# Repo commands. `just --list` shows them; run from the repo root.
# Tools come from .devcontainer/Dockerfile: inside the devcontainer they run
# directly, on the host they run in the `mahahe-taiga-openid` distrobox
# (`just toolbox`). Images are built and run with `cli`: podman on the host,
# docker in the devcontainer and in CI (override with CONTAINER_CLI).

set shell := ["bash", "-euo", "pipefail", "-c"]

box := "mahahe-taiga-openid"
image := "localhost/mahahe-taiga-openid:latest"
in_container := if path_exists("/run/.containerenv") == "true" { "true" } else if path_exists("/.dockerenv") == "true" { "true" } else { "false" }
# Image paths only: the host PATH (inherited by distrobox) may carry shims of
# the same tools from other toolboxes.
tb := if in_container == "true" { "" } else { "distrobox enter -n " + box + " -- env PATH=/usr/local/bin:/usr/bin:/bin" }
cli := env("CONTAINER_CLI", if in_container == "true" { "docker" } else { "podman" })
back_image := env("BACK_IMAGE", "localhost/taiga-back-openid:dev")
front_image := env("FRONT_IMAGE", "localhost/taiga-front-openid:dev")
compose := cli + " compose -f e2e/compose.yaml"

_default:
    @just --list

# Build the image and (re)create the distrobox; rerun after a Dockerfile change
toolbox:
    podman build -t {{ image }} .devcontainer
    distrobox rm -f {{ box }} 2>/dev/null || true
    distrobox create -Y -n {{ box }} -i {{ image }}
    # Image tests run in the box and drive the host podman through distrobox-host-exec
    distrobox enter -n {{ box }} -- sudo ln -sf /usr/bin/distrobox-host-exec /usr/local/bin/podman
    just hooks

# Install the git pre-commit hook (works from host, distrobox and devcontainer)
hooks:
    #!/usr/bin/env bash
    set -euo pipefail
    hook="$(git rev-parse --git-path hooks)/pre-commit"
    cat > "$hook" <<'EOF'
    #!/usr/bin/env bash
    # Installed by `just hooks`. Outside a container, run in the toolbox.
    # Branches older than the pre-commit config have nothing to run.
    [ -f .pre-commit-config.yaml ] || exit 0
    if [ -e /run/.containerenv ] || [ -e /.dockerenv ]; then
        exec pre-commit run --hook-stage pre-commit
    fi
    exec distrobox enter -n {{ box }} -- env PATH=/usr/local/bin:/usr/bin:/bin \
        pre-commit run --hook-stage pre-commit
    EOF
    chmod +x "$hook"
    echo "installed $hook"

# Shell inside the toolbox
shell:
    distrobox enter -n {{ box }}

# Run every pre-commit hook on the whole tree
precommit:
    {{ tb }} pre-commit run --all-files

# Build both images (BACK_IMAGE / FRONT_IMAGE override the local names)
build:
    {{ cli }} build -f docker/back/Dockerfile -t {{ back_image }} .
    {{ cli }} build -f docker/front/Dockerfile -t {{ front_image }} .

# End-to-end login test against Keycloak on the images from `just build`.
# Leaves the stack up when E2E_KEEP=1; logs and traces go to e2e/results.
e2e *args:
    #!/usr/bin/env bash
    set -euo pipefail
    export BACK_IMAGE={{ back_image }} FRONT_IMAGE={{ front_image }}
    rm -rf e2e/results && mkdir -p e2e/results
    cleanup() {
        {{ compose }} logs --no-color > e2e/results/compose.log 2>&1 || true
        [ "${E2E_KEEP:-0}" = 1 ] || {{ compose }} --profile test down -v --remove-orphans
    }
    trap cleanup EXIT
    {{ compose }} up -d --wait --wait-timeout 600
    {{ compose }} exec -T \
        -e DJANGO_SUPERUSER_USERNAME=admin \
        -e DJANGO_SUPERUSER_EMAIL=admin@example.test \
        -e DJANGO_SUPERUSER_PASSWORD=e2e-admin \
        taiga-back python manage.py createsuperuser --noinput
    {{ compose }} --profile test run --rm --build e2e {{ args }}

# Back unit tests, inside the back image's `test` stage
test-back *args:
    {{ cli }} build -f docker/back/Dockerfile --target test -t localhost/taiga-back-openid:test .
    {{ cli }} run --rm localhost/taiga-back-openid:test python -m pytest -c /tests/pytest.ini --rootdir /tests /tests {{ args }}

# Tests of the built images (`just build` first)
test-images *args:
    {{ tb }} env CONTAINER_CLI={{ cli }} BACK_IMAGE={{ back_image }} FRONT_IMAGE={{ front_image }} \
        pytest -p no:cacheprovider tests/images {{ args }}
