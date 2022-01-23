import logging
import os
import shutil
import tarfile
from pathlib import Path

import requests

from dagos.console import console


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

    logging.debug(f"Sending request to '{url}'")
    # TODO: Sometimes the file name is only evident after following redirects ...
    file_name = url.split("/")[-1]
    path = Path(file_name)
    with requests.get(url, stream=True) as r:
        with console.status(f"Downloading '{path.name}' ...", spinner="material"):
            with path.open("wb") as f:
                shutil.copyfileobj(r.raw, f)

    logging.debug(f"Successfully downloaded '{path.name}'")
    return path


def extract_tar_archive(
    archive: Path, output_dir: Path, strip_root_folder: bool = False
) -> None:
    """Extract provided archive to provided output folder.

    Args:
        archive (Path): The tar archive to extract.
        output_dir (Path): The output folder.
        strip_root_folder (bool, optional): If True, strip the root folder within the archive. Defaults to False.
    """
    with console.status(
        f"Extracting '{archive.name}' to '{output_dir.name}' ...", spinner="material"
    ):
        with tarfile.open(archive) as tar:
            if strip_root_folder:
                for member in tar.getmembers():
                    member.name = member.name.partition("/")[2]
                    tar.extract(member, output_dir)
            else:
                tar.extractall(output_dir)


def add_executable_to_path(
    executable: Path, dir_on_path: Path, exists_ok: bool = True
) -> None:
    """Add a symlink to provided executable to provided dir on path.

    Args:
        executable (Path): The executable to link into provided dir.
        dir_on_path (Path): A directory that is already on the PATH.
        exists_ok (bool, optional): If False, fails when the target file already exists. Defaults to True.
    """
    symlink_target = dir_on_path / executable.name
    if symlink_target.exists():
        if exists_ok:
            logging.trace(
                f"Replacing existing '{executable.name}' symlink in '{symlink_target}'"
            )
            symlink_target.unlink()
        else:
            logging.error(
                f"A '{executable.name}' executable is already in '{symlink_target}'..."
            )
            exit(1)
    os.symlink(executable, symlink_target)
