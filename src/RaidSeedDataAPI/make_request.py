import requests
from dotenv import load_dotenv
from src.model.Stage import Stage
from src.utils import get_env_strict

load_dotenv()

HEADERS = {"secret": get_env_strict("API_AUTH_SECRET")}


def make_request_sync(*,
                      method,
                      path,
                      data=None,
                      stage=Stage.DEV,
                      parse_response=True,
                      **kwargs):
    base_url = BASE_URLS_API[stage]

    response = method(f"{base_url}/{path}",
                      headers=HEADERS,
                      data=data,
                      **kwargs)

    if parse_response:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text

    return response


async def make_request_async(*,
                             method,
                             path,
                             data=None,
                             stage=Stage.DEV,
                             parse_response=False):
    base_url = BASE_URLS_API[stage]

    async with method(url=f"{base_url}/{path}", data=data) as response:
        if parse_response:
            return await response.json()

        return response
