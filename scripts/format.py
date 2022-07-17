from .run_script import run_script


def get_cmds(*, paths):
    if not paths:
        return (("yapf", ".", "-ir", "-e", "venv"), )

    return (("yapf", path, "-i") for path in paths)


def main():
    run_script(get_cmds=get_cmds)


if __name__ == '__main__':
    main()
