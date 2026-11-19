# Contributing

Thanks for helping with the Taiga OpenID Connect plugin! Bug reports, fixes and
new features are all welcome. By taking part you agree to follow our
[Code of Conduct](https://github.com/mahahe-it/.github/blob/main/CODE_OF_CONDUCT.md).
Security problems go through the [Security Policy](https://github.com/mahahe-it/.github/blob/main/SECURITY.md),
not public issues.

## Reporting a bug or asking for a feature

Open an [issue](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/new/choose)
and pick the template. For a bug, the image tags, your identity provider, the
`OPENID_*` variables you set (without secrets) and the taiga-back logs help a lot.

## Development environment

Tools are pinned in `.devcontainer/Dockerfile`: open the repo in the
devcontainer, or run `just toolbox` to build the same image as a distrobox.
Images are built and run with podman on the host and docker in the
devcontainer and CI (`CONTAINER_CLI` overrides it). `just --list` shows the
common tasks:

| Recipe | What it does |
|---|---|
| `just build` | build both images (`BACK_IMAGE` / `FRONT_IMAGE` override the local names) |
| `just test-back` | back unit tests, inside the back image's `test` stage |
| `just test-images` | tests of the built images: generated `conf.json`, served plugin, settings |
| `just e2e` | OpenID login end to end: Taiga, Keycloak and a Playwright browser in compose (`E2E_KEEP=1` leaves the stack up, logs and traces in `e2e/results`) |
| `just precommit` | every pre-commit hook on the whole tree |
| `just hooks` | install the git pre-commit hook |
| `just shell` | a shell in the toolbox |

Files must use LF line endings (`git config --global core.autocrlf false` on Windows).

## Pull requests

Changes go through pull requests against `main`, merged by squash. The PR
title becomes the commit on `main`, so it must follow
[Conventional Commits](https://www.conventionalcommits.org/) (the `PR Title`
check enforces it), and it decides the release:

| PR title | Release |
|---|---|
| `fix(back): ...` | patch |
| `feat(front): ...` | minor |
| `feat!: ...` (breaking change) | major |
| `docs`, `chore`, `ci`, `test`, ... | none |

A breaking change also needs a note in the README on how to upgrade. Do not
bump versions by hand: release-please keeps a release PR open with the next
version and its `CHANGELOG.md`. Commits on `main` must be signed. A bug fix
comes with the test that would have caught it.

CI runs pre-commit, the unit and image tests and the end-to-end test on every
pull request; all of them must pass before merging.
