import subprocess
import sys
from typing import Callable


def run_script(get_cmds: Callable):
    files = sys.argv[1:]

    for cmd in get_cmds(files):
        print(str.join(' ', cmd), flush=True)
        subprocess.run(cmd, check=True)
