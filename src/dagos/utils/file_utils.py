import atexit
import logging
import shutil
import tarfile
import tempfile
import typing as t
import zipfile
from pathlib import Path

import requests
from loguru import logger

from dagos.exceptions import DagosException
from dagos.logging import spinner


def download_file(url: str) -> Path:
    """
    Download file from provided URL and store at provided output path.
    If no path is provided the last element in the URL is used to name
    the file and store it in the current working dir.

    Args:
        url (str): The URL to download the file from.

    Returns:
        Path: The Path of the downloaded file.
    """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger.debug(f"Sending request to '{url}'")
    # TODO: Sometimes the file name is only evident after following redirects ...
    file_name = url.split("/")[-1]
    path = Path(file_name)
    with requests.get(url, stream=True) as r:
        with spinner(
            f"Downloading '{path.name}' ...",
            f"Successfully downloaded '{path.name}'",
            "DEBUG",
        ):
            with path.open("wb") as f:
                shutil.copyfileobj(r.raw, f)
    return path


def extract_archive(
    archive: Path, output_dir: Path, strip_root_folder: bool = False
) -> None:
    """Extract provided archive to provided output folder.

    Args:
        archive (Path): The tar archive to extract.
        output_dir (Path): The output folder.
        strip_root_folder (bool, optional): If True, strip the root folder within the archive. Defaults to False.
    """
    with spinner(f"Extracting '{archive.name}' to '{output_dir.name}' ..."):
        if tarfile.is_tarfile(archive):
            _extract_tar_archive(archive, output_dir, strip_root_folder)
        elif zipfile.is_zipfile(archive):
            _extract_zip_archive(archive, output_dir, strip_root_folder)
        else:
            raise DagosException(f"Unhandled archive type: {archive.name}")


def _extract_tar_archive(
    archive: Path, output_dir: Path, strip_root_folder: bool = False
) -> None:

    with tarfile.open(archive) as tar:
        if strip_root_folder:
            for member in tar.getmembers():
                member.name = member.name.partition("/")[2]
                tar.extract(member, output_dir)
        else:
            tar.extractall(output_dir)


def _extract_zip_archive(
    archive: Path, output_dir: Path, strip_root_folder: bool = False
) -> None:
    with zipfile.ZipFile(archive) as zip:
        if strip_root_folder:
            raise NotImplementedError()
        else:
            zip.extractall(output_dir)


def create_symlink(
    from_path: t.Union[str, Path],
    to_path: t.Union[str, Path],
    force: bool = False,
    target_is_directory: bool = False,
) -> Path:
    """Create symlink from a provided path to another.

    Args:
        from_path (t.Union[str, Path]): The path where the symlink is created.
        to_path (t.Union[str, Path]): The path to where the symlink points.
        force (bool, optional): If True, existing files at from_path are overridden.
            If False, an exception is raised when the from_path already exists.
            Defaults to False.
        target_is_directory (bool, optional): Set True, if the target is a directory.
            Defaults to False.

    Raises:
        DagosException: If the from_path exists and force is not provided.
        DagosException: If the to_path does not exist.

    Returns:
        Path: The path of created symlink
    """
    if isinstance(from_path, str):
        from_path = Path(from_path)
    if isinstance(to_path, str):
        to_path = Path(to_path)
    from_path = from_path.expanduser()
    to_path = to_path.expanduser()
    if from_path.exists():
        if force:
            logger.trace(f"Removing existing file at '{from_path}'")
            from_path.unlink()
        else:
            raise DagosException(
                f"Failed to create symbolic link '{from_path}': a file with that name already exists"
            )
    if not to_path.exists():
        raise DagosException(
            f"Failed to create symbolic link '{from_path}': the target does not exist"
        )
    if not from_path.parent.exists():
        from_path.parent.mkdir(parents=True)
    from_path.symlink_to(to_path, target_is_directory)
    return from_path


def create_temp_dir(remove_at_exit: bool = True) -> Path:
    """Create a temporary directory.

    Args:
        remove_at_exit (bool, optional): If True, delete directory when
            application exists. Defaults to True.

    Returns:
        Path: The path to the created directory.
    """
    temp_dir = Path(tempfile.mkdtemp())
    if remove_at_exit:
        atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
    return temp_dir
