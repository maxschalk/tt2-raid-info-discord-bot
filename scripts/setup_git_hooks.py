import subprocess
import sys

DEFAULT_DIR = "./.git-hooks"


def main():
    try:
        dir = sys.argv[1]
    except IndexError:
        dir = DEFAULT_DIR

    cmd = ("git", "config", "core.hooksPath", dir)

    print(str.join(' ', cmd))
    subprocess.run(cmd)


if __name__ == '__main__':
    main()
