import subprocess
import sys

DEFAULT_DIR = "./.git-hooks"


def main():
    try:
        hooks_dir = sys.argv[1]
    except IndexError:
        hooks_dir = DEFAULT_DIR

    cmd = ("git", "config", "core.hooksPath", hooks_dir)

    print(str.join(' ', cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
