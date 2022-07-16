import subprocess
import sys


def get_cmds(paths):
    if not paths:
        return (("yapf", ".", "-ir", "-e", "venv"), )

    return (("yapf", path, "-i") for path in paths)


def main():
    files = sys.argv[1:]

    for cmd in get_cmds(files):
        print(str.join(' ', cmd))
        subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
