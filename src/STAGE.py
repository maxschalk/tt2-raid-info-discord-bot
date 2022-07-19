from enum import Enum

from src.utils.get_env import get_env


class Stage(Enum):
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


STAGE = Stage(get_env(key='STAGE', strict=False) or Stage.PRODUCTION.value)
