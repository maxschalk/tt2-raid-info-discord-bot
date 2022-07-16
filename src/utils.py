import os


def get_env_strict(key: str) -> str:
    value = os.getenv(key)

    if value is None:
        raise KeyError(f"{key} is not an environment variable")

    return value
