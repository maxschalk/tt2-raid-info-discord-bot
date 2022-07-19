import os
import stat
import subprocess
import sys

DEFAULT_DIR = "./.git-hooks"


def main():
    try:
        hooks_dir = sys.argv[1]
    except IndexError:
        hooks_dir = DEFAULT_DIR

    # unix: make hooks executable
    if 'darwin' in sys.platform or 'linux' in sys.platform:
        for file in os.listdir(hooks_dir):
            path = os.path.join(hooks_dir, file)
            file_stat = os.stat(path)
            os.chmod(path, file_stat.st_mode | stat.S_IEXEC)

    cmd = ("git", "config", "core.hooksPath", hooks_dir)

    print(str.join(' ', cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
