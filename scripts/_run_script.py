import subprocess
import sys
from typing import Callable


def run_script(*, get_cmds: Callable, check: bool = True) -> None:
    paths = sys.argv[1:]

    for cmd in get_cmds(paths=paths):
        print(str.join(' ', cmd), flush=True)
        subprocess.run(cmd, check=check)
