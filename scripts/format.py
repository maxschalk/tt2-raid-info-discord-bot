import subprocess
import sys
from pathlib import Path

from PATHS import SCRIPTS_DIR, SRC_DIR

DEFAULT_DIRS = (SRC_DIR, SCRIPTS_DIR)


def get_cmds(paths):
    if not paths:
        return (("yapf", "-ir", dir.as_posix()) for dir in DEFAULT_DIRS)

    return (("yapf", "-i", path) for path in paths)


def main():
    files = sys.argv[1:]

    for cmd in get_cmds(files):
        print(str.join(' ', cmd))
        subprocess.run(cmd)


if __name__ == '__main__':
    main()