from dotenv import load_dotenv

from src.model.Stage import Stage
from src.utils import get_env

load_dotenv()

STAGE = Stage(get_env('STAGE', strict=False) or Stage.PRODUCTION.value)

print(f"{STAGE=}")
