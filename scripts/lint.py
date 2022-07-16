from .run_script import run_script


def get_cmds(paths):
    if not paths:
        return (("pylint", ".", "--recursive", "y", "--ignore-patterns",
                 "venv"), )

    return (("pylint", path) for path in paths)


def main():
    run_script(get_cmds)


if __name__ == '__main__':
    main()
