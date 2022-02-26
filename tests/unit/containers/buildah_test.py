from contextlib import contextmanager
from subprocess import CalledProcessError

import pytest

import dagos.containers.buildah as buildah


@contextmanager
def does_not_raise():
    yield


@pytest.fixture
def container():
    container = buildah.create_container("alpine")
    yield container
    buildah.rm(container)


@pytest.mark.parametrize(
    "command,user,capture_stdout,capture_stderr,expectation",
    [
        ("ls -la", None, True, False, does_not_raise()),
        (["ls", "-la"], None, False, True, does_not_raise()),
        ("ls", "dev:dev", False, False, pytest.raises(CalledProcessError)),
    ],
)
def test_run(container, command, user, capture_stdout, capture_stderr, expectation):
    with expectation:
        result = buildah.run(
            container,
            command,
            user=user,
            capture_stdout=capture_stdout,
            capture_stderr=capture_stderr,
        )
        assert result.returncode == 0
        if capture_stdout:
            assert result.stdout != None
        if capture_stderr:
            assert result.stderr != None


@pytest.mark.parametrize(
    "src,dst,chown,expectation",
    [
        ("README.md", None, None, does_not_raise()),
        ("README.md", "/root/README.md", None, does_not_raise()),
        ("README.md", "/root/README.md", "root:root", does_not_raise()),
        ("README.md", "/root/README.md", "dev:dev", pytest.raises(CalledProcessError)),
    ],
)
def test_copy(container, src, dst, chown, expectation):
    with expectation:
        buildah.copy(container, src, dst, chown)


@pytest.mark.parametrize(
    "image_name,expectation",
    [
        (None, does_not_raise()),
        ("localhost/dagos-buildah-test-image", does_not_raise()),
        ("README.md", pytest.raises(CalledProcessError)),
    ],
)
def test_commit(container, image_name, expectation):
    with expectation:
        image = buildah.commit(container, image_name)
        assert image


@pytest.mark.parametrize(
    "annotations,ports,shell,working_dir,expectation",
    [
        (None, None, None, None, does_not_raise()),
        ({"bla": "bla"}, None, None, None, does_not_raise()),
        (None, ["8080", "12345"], None, None, does_not_raise()),
        (None, None, "/bin/zsh", None, does_not_raise()),
        (None, None, None, "/root", does_not_raise()),
    ],
)
def test_config(container, annotations, ports, shell, working_dir, expectation):
    with expectation:
        buildah.config(
            container,
            annotations=annotations,
            ports=ports,
            shell=shell,
            working_dir=working_dir,
        )
