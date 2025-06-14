import os
import subprocess

from ..types import Variables
from .config import RunConfig


def run_command(command: str, env: Variables) -> subprocess.Popen:
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=0,
    )
    os.set_blocking(proc.stdout.fileno(), False)
    os.set_blocking(proc.stderr.fileno(), False)
    return proc


def run_script(script: str) -> subprocess.Popen: ...


def run(config: RunConfig):
    if config.command:
        proc = run_command(config.command, config.env)
    elif config.script:
        proc = run_script(config.script)
    else:
        raise ValueError

    return stdout, stderr
