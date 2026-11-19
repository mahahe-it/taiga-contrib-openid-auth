"""Run the built images with $CONTAINER_CLI (docker in CI, podman on the host)."""

import os
import shlex
import subprocess
import time
import uuid

import pytest

CLI = shlex.split(os.environ.get("CONTAINER_CLI", "docker"))
BACK_IMAGE = os.environ.get("BACK_IMAGE", "localhost/taiga-back-openid:dev")
FRONT_IMAGE = os.environ.get("FRONT_IMAGE", "localhost/taiga-front-openid:dev")
CONF = "/usr/share/nginx/html/conf.json"


def cli(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([*CLI, *args], capture_output=True, text=True, check=check)


class Container:
    def __init__(self, image: str, env: dict, volumes: tuple[str, ...] = ()):
        self.name = f"openid-test-{uuid.uuid4().hex[:8]}"
        args = ["run", "-d", "--name", self.name]
        for key, value in env.items():
            args += ["-e", f"{key}={value}"]
        for volume in volumes:
            args += ["-v", volume]
        cli(*args, image)

    def exec(self, *command: str, check: bool = True) -> subprocess.CompletedProcess:
        return cli("exec", self.name, *command, check=check)

    def wait_http(self, path: str = "/", timeout: float = 30) -> None:
        deadline = time.monotonic() + timeout
        while self.exec("wget", "-qO", "/dev/null", f"http://127.0.0.1{path}", check=False).returncode:
            if time.monotonic() > deadline:
                logs = cli("logs", self.name, check=False)
                pytest.fail(f"{self.name} not ready:\n{logs.stdout}\n{logs.stderr}")
            time.sleep(0.5)

    def read(self, path: str) -> str:
        return self.exec("cat", path).stdout

    def restart(self) -> None:
        cli("restart", self.name)

    def remove(self) -> None:
        cli("rm", "-f", self.name, check=False)


@pytest.fixture
def start_front():
    containers = []

    def start(env: dict, volumes: tuple[str, ...] = ()) -> Container:
        container = Container(FRONT_IMAGE, env, volumes)
        containers.append(container)
        container.wait_http()
        return container

    yield start
    for container in containers:
        container.remove()
