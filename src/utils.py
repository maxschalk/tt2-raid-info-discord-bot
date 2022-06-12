import json
from urllib import response

from requests import JSONDecodeError

from src.constants import REGEX_CONTENT


def full_username(user):
    return f"{user.display_name}#{user.discriminator}"


def seed_data_filename(from_msg_content):
    matches = REGEX_CONTENT.match(from_msg_content)

    seed_date = matches.group(1).replace('/', '')

    suffix = ".json"

    return f"raid_seed_{seed_date}{suffix}"


def message_from_response(response):
    try:
        data = response.json()

        data = data.get("detail", json.dumps(data, indent=4))

    except JSONDecodeError:
        data = response.text

    return f"{response.status_code=}: {data}"
