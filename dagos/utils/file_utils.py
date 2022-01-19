import logging
import shutil
from pathlib import Path

import requests

from dagos.console import console


def download_file(url: str) -> Path:
    """
    Download file from provided URL and store at provided output path.
    If no path is provided the last element in the URL is used to name
    the file and store it in the current working dir.
    """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.debug(f"Sending request to '{url}'")
    with requests.get(url, stream=True) as r:
        path = Path(r.url.split("/")[-1])
        with console.status(f"Downloading '{path.name}' ...", spinner="material"):
            with path.open("wb") as f:
                shutil.copyfileobj(r.raw, f)

    logging.debug(f"Successfully downloaded '{path.name}'")

    return path
