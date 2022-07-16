import json

import discord
from requests import JSONDecodeError, Response

from src.actions import REGEX_CONTENT


def full_username(user: discord.User) -> str:
    return f"{user.display_name}#{user.discriminator}"


def seed_data_filename(from_msg_content: str) -> str:
    matches = REGEX_CONTENT.match(from_msg_content)

    seed_date = matches.group(1).replace('/', '')

    return f"raid_seed_{seed_date}.json"


def message_from_response(response: Response) -> str:
    try:
        data = response.json()

        data = data.get("detail", json.dumps(data, indent=4))

    except JSONDecodeError:
        data = response.text

    return f"{response.status_code=}: {data}"
