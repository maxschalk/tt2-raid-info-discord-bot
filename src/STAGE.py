from dotenv import load_dotenv

from src.model.stage import Stage
from src.utils import get_env

load_dotenv()

STAGE = Stage(get_env(key='STAGE', strict=False) or Stage.PRODUCTION.value)

print(f"{STAGE=}")
