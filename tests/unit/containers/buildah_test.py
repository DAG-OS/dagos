import subprocess
from unittest.mock import call

import pytest

import dagos.containers.buildah as buildah
from dagos.logging import LogLevel
from dagos.platform import platform_utils


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
    mocker.patch("dagos.platform.platform_utils.run_command")
    expectation = ["buildah", "from"] + expectation

    result = buildah.create_container(image, name, volumes)

    assert result
    platform_utils.run_command.assert_called_once_with(expectation, capture_stdout=True)


@pytest.mark.parametrize(
    "image_name,rm,squash,expectation",
    [
        (None, False, False, ["container"]),
        (
            "localhost/dagos-buildah-test-image",
            False,
            False,
            ["container", "localhost/dagos-buildah-test-image"],
        ),
        (None, True, False, ["--rm", "container"]),
        (None, False, True, ["--squash", "container"]),
        ("test-image", True, True, ["--rm", "--squash", "container", "test-image"]),
    ],
)
def test_commit(mocker, image_name, rm, squash, expectation):
    mocker.patch("dagos.platform.platform_utils.run_command")
    expectation = ["buildah", "commit"] + expectation

    image = buildah.commit("container", image_name=image_name, rm=rm, squash=squash)

    platform_utils.run_command.assert_called_once_with(expectation, capture_stdout=True)
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
    mocker.patch("dagos.platform.platform_utils.run_command")
    expectation = ["buildah", "config"] + expectation + ["container"]

    buildah.config("container", **args)

    platform_utils.run_command.assert_called_once_with(expectation)


def test_config_no_args(mocker):
    mocker.patch("dagos.platform.platform_utils.run_command")

    buildah.config("container")

    platform_utils.run_command.assert_not_called()


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
    mocker.patch("dagos.platform.platform_utils.run_command")
    expectation = ["buildah", "copy"] + expectation

    buildah.copy("container", src, dst, chown)

    platform_utils.run_command.assert_called_once_with(expectation)


def test_rm(mocker):
    mocker.patch("dagos.platform.platform_utils.run_command")

    buildah.rm("container")

    platform_utils.run_command.assert_called_once_with(
        ["buildah", "rm", "container"], capture_stdout=True
    )


@pytest.mark.parametrize(
    "command,user,capture_stdout,capture_stderr,encoding,ignore_failure,log_level,expectation",
    [
        ("ls -la", None, True, False, None, False, None, "container -- ls -la"),
        (
            ["ls", "-la"],
            None,
            False,
            True,
            None,
            False,
            LogLevel.DEBUG,
            ["container", "--", "ls", "-la"],
        ),
        (
            "ls",
            "d:d",
            False,
            False,
            None,
            False,
            LogLevel.ERROR,
            "--user d:d container -- ls",
        ),
        (
            ["xxxxx"],
            None,
            False,
            False,
            None,
            True,
            LogLevel.WARNING,
            ["container", "--", "xxxxx"],
        ),
    ],
)
def test_run(
    mocker,
    command,
    user,
    capture_stdout,
    capture_stderr,
    encoding,
    ignore_failure,
    log_level,
    expectation,
):
    mocker.patch("dagos.platform.platform_utils.run_command")
    if isinstance(expectation, str):
        expectation = "buildah run " + expectation
    else:
        expectation = ["buildah", "run"] + expectation

    buildah.run(
        "container",
        command,
        user=user,
        capture_stdout=capture_stdout,
        capture_stderr=capture_stderr,
        encoding=encoding,
        ignore_failure=ignore_failure,
        log_level=log_level,
    )

    platform_utils.run_command.assert_called_once_with(
        command=expectation,
        capture_stdout=capture_stdout,
        capture_stderr=capture_stderr,
        encoding=encoding,
        ignore_failure=ignore_failure,
        log_level=log_level,
    )


@pytest.mark.parametrize(
    "command,user",
    [
        ("ls", None),
        ("ls", "dev:dev"),
        ("dagos", "dev:dev"),
    ],
)
def test_check_command(mocker, command, user):
    mocker.patch(
        "dagos.containers.buildah.run",
        return_value=subprocess.CompletedProcess("cmd", returncode=0),
    )

    buildah.check_command("container", command, user)

    buildah.run.assert_has_calls(
        [
            call(
                "container",
                "command",
                user=user,
                capture_stdout=True,
                capture_stderr=True,
                ignore_failure=True,
            ),
            call(
                "container",
                f"command -v {command}",
                user=user,
                capture_stdout=True,
                capture_stderr=True,
                ignore_failure=True,
            ),
        ],
    )


def test_check_command_which(mocker):
    mock = mocker.patch("dagos.containers.buildah.run")
    mock.side_effect = [
        subprocess.CompletedProcess("cmd", returncode=1),
        subprocess.CompletedProcess("cmd", returncode=0),
    ]
    command = "ls"

    buildah.check_command("container", command)

    buildah.run.assert_has_calls(
        [
            call(
                "container",
                "command",
                capture_stdout=True,
                capture_stderr=True,
                ignore_failure=True,
                user=None,
            ),
            call(
                "container",
                f"which {command}",
                capture_stdout=True,
                capture_stderr=True,
                ignore_failure=True,
                user=None,
            ),
        ],
    )
