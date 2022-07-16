import os

from dotenv import load_dotenv

from src.model.Stage import Stage

load_dotenv()

STAGE = Stage(os.getenv('STAGE') or Stage.PRODUCTION.value)

print(f"{STAGE=}")
