import os

from dotenv import load_dotenv

load_dotenv()


def get_env(*, key: str, strict: bool = True) -> str:
    value = os.getenv(key)

    if strict and value is None:
        raise KeyError(f"{key} is not an environment variable")

    return value
