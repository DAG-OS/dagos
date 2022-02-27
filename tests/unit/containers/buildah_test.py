import subprocess

import pytest

import dagos.containers.buildah as buildah


@pytest.mark.parametrize(
    "command,shell,capture_stdout,capture_stderr,stdout,stderr",
    [
        ("command", True, None, None, None, None),
        (["command"], False, None, None, None, None),
        (["command"], False, True, None, subprocess.PIPE, None),
        (["command"], False, False, True, None, subprocess.PIPE),
        (["command"], False, True, True, subprocess.PIPE, subprocess.PIPE),
    ],
)
def test_private_run(
    mocker,
    command,
    shell,
    capture_stdout,
    capture_stderr,
    stdout,
    stderr,
):
    mocker.patch("subprocess.run")

    buildah._run(command, capture_stdout, capture_stderr)

    subprocess.run.assert_called_once_with(
        command,
        shell=shell,
        stdout=stdout,
        stderr=stderr,
        text=True,
    )


@pytest.mark.parametrize(
    "image,name,volumes,expectation",
    [
        ("alpine", None, None, ["alpine"]),
        ("busybox", "test-container", None, ["--name", "test-container", "busybox"]),
        ("busybox", None, [".:/root/"], ["--volume", ".:/root/", "busybox"]),
        (
            "alpine",
            "test",
            [".:/root/"],
            ["--name", "test", "--volume", ".:/root/", "alpine"],
        ),
    ],
)
def test_create_container(mocker, image, name, volumes, expectation):
    mocker.patch("dagos.containers.buildah._run")
    expectation = ["buildah", "from"] + expectation

    result = buildah.create_container(image, name, volumes)

    assert result
    buildah._run.assert_called_once_with(expectation, capture_stdout=True)


@pytest.mark.parametrize(
    "command,user,capture_stdout,capture_stderr,expectation",
    [
        ("ls -la", None, True, False, ["container", "--", "ls", "-la"]),
        (["ls", "-la"], None, False, True, ["container", "--", "ls", "-la"]),
        ("ls", "dev:dev", False, False, ["--user", "dev:dev", "container", "--", "ls"]),
    ],
)
def test_run(mocker, command, user, capture_stdout, capture_stderr, expectation):
    mocker.patch("dagos.containers.buildah._run")
    expectation = ["buildah", "run"] + expectation

    buildah.run(
        "container",
        command,
        user=user,
        capture_stdout=capture_stdout,
        capture_stderr=capture_stderr,
    )

    buildah._run.assert_called_once_with(expectation, capture_stdout, capture_stderr)


@pytest.mark.parametrize(
    "src,dst,chown,expectation",
    [
        (
            "README.md",
            None,
            None,
            ["container", "README.md"],
        ),
        (
            "README.md",
            "/root/README.md",
            None,
            ["container", "README.md", "/root/README.md"],
        ),
        (
            "README.md",
            "/root/README.md",
            "root:root",
            ["--chown", "root:root", "container", "README.md", "/root/README.md"],
        ),
    ],
)
def test_copy(mocker, src, dst, chown, expectation):
    mocker.patch("dagos.containers.buildah._run")
    expectation = ["buildah", "copy"] + expectation

    buildah.copy("container", src, dst, chown)

    buildah._run.assert_called_once_with(expectation)


@pytest.mark.parametrize(
    "image_name,expectation",
    [
        (None, []),
        ("localhost/dagos-buildah-test-image", ["localhost/dagos-buildah-test-image"]),
    ],
)
def test_commit(mocker, image_name, expectation):
    mocker.patch("dagos.containers.buildah._run")
    expectation = ["buildah", "commit", "container"] + expectation

    image = buildah.commit("container", image_name)

    buildah._run.assert_called_once_with(expectation, capture_stdout=True)
    assert image


@pytest.mark.parametrize(
    "args,expectation",
    [
        ({"annotations": {"bla": "bla"}}, ["--annotation", "bla=bla"]),
        ({"author": "max"}, ["--author", "max"]),
        ({"cmd": "ls"}, ["--cmd", "ls"]),
        ({"created_by": "max"}, ["--created-by", "max"]),
        ({"entrypoint": "/bin/bash"}, ["--entrypoint", "/bin/bash"]),
        ({"env_vars": {"PATH": "/usr/local/bin"}}, ["--env", "PATH=/usr/local/bin"]),
        ({"labels": {"name": "test"}}, ["--label", "name=test"]),
        ({"ports": ["8080", "12345"]}, ["--port", "8080", "--port", "12345"]),
        ({"shell": "zsh"}, ["--shell", "zsh"]),
        ({"user": "dagos"}, ["--user", "dagos"]),
        ({"volumes": [".:/root/"]}, ["--volume", ".:/root/"]),
        ({"working_dir": "/home/dev"}, ["--workingdir", "/home/dev"]),
    ],
)
def test_config(mocker, args, expectation):
    mocker.patch("dagos.containers.buildah._run")
    expectation = ["buildah", "config"] + expectation + ["container"]

    buildah.config("container", **args)

    buildah._run.assert_called_once_with(expectation)


def test_config_no_args(mocker):
    mocker.patch("dagos.containers.buildah._run")

    buildah.config("container")

    buildah._run.assert_not_called()


def test_rm(mocker):
    mocker.patch("dagos.containers.buildah._run")

    buildah.rm("container")

    buildah._run.assert_called_once_with(["buildah", "rm", "container"])
