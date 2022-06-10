import os

import requests
from dotenv import load_dotenv
from src.api_interface.BASE_URLS import BASE_URLS
from src.api_interface.Stage import Stage

load_dotenv()

ENV_AUTH_SECRET = os.getenv("AUTH_SECRET")

HEADERS = {"secret": ENV_AUTH_SECRET}


def make_request_sync(
    *, method, path, data=None, stage=Stage.DEV, parse_response=True, **kwargs
):
    base_url = BASE_URLS[stage]

    response = method(
        f"{base_url}/{path}",
        headers=HEADERS,
        data=data,
        **kwargs
    )

    if not parse_response:
        return response

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text


async def make_request_async(
    *, method, path, data=None, stage=Stage.DEV, parse_response=False
):
    base_url = BASE_URLS[stage]

    async with method(url=f"{base_url}/{path}", data=data) as response:
        if parse_response:
            return await response.json()

        return response
