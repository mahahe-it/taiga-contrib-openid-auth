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

_default:
    @just --list

# Build the image and (re)create the distrobox; rerun after a Dockerfile change
toolbox:
    podman build -t {{ image }} .devcontainer
    distrobox rm -f {{ box }} 2>/dev/null || true
    distrobox create -Y -n {{ box }} -i {{ image }}
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
