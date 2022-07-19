import sys
from subprocess import CalledProcessError

from .run_script import run_script


def get_cmds(*, paths):
    if not paths:
        return (("pylint", ".", "--recursive", "y", "--ignore-patterns",
                 "venv"), )

    return (("pylint", path) for path in paths)


def main():
    try:
        run_script(get_cmds=get_cmds, check=True)
    except CalledProcessError:
        sys.exit(1)


if __name__ == '__main__':
    main()
