import logging
import subprocess
from io import StringIO


def run_as_admin(
    command: str, pause_after: bool = False
) -> subprocess.CompletedProcess:
    """Run provided command as an administrator.

    Args:
        command (str): The command to run.
        pause_after (bool, optional): If True, pause after the command has run. Defaults to False.

    Returns:
        subprocess.CompletedProcess[str]: The command result.
    """
    # TODO: Find a way to retrieve output from the started process
    logging.debug("Building PowerShell command")
    command_wrapper = StringIO()
    command_wrapper.write(
        "powershell Start-Process powershell -Verb runAs -Wait -ArgumentList '"
    )
    command_wrapper.write(command)
    if pause_after:
        command_wrapper.write(";pause")
    command_wrapper.write("'")

    logging.debug(f"Running command: {command_wrapper.getvalue()}")
    logging.info("Running a PowerShell command as admin")
    logging.info("Windows may prompt you for permission")
    return subprocess.run(command_wrapper.getvalue(), shell=True)
