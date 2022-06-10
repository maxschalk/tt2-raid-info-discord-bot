import os

from dotenv import load_dotenv

from src.api_interface.Stage import Stage

load_dotenv()

STAGE = Stage(os.getenv('STAGE') or Stage.PRODUCTION.value)
