import json
import re

import discord
from requests import JSONDecodeError, Response

BOT_AUTHOR = "pingu#4195"
BOT_USER = "TT2RaidSeedBot#1932"
SEED_AUTHOR = "GameHive #raid-seed-export#0000"

REGEX_CONTENT = re.compile("^Raid seed export - ([0-9]{4}/[0-9]{2}/[0-9]{2})$")

EMOJI_CHECK_MARK = "✅"
EMOJI_RED_CROSS = "❌"
EMOJI_PENGUIN = "🐧"


def full_username(user: discord.User) -> str:
    return f"{user.display_name}#{user.discriminator}"


def is_relevant_message(message: discord.Message) -> bool:
    return has_relevant_author(message) and is_raid_seed_message(message)


def has_relevant_author(message: discord.Message) -> bool:
    author_name = full_username(message.author)

    return author_name in {SEED_AUTHOR, BOT_AUTHOR}


def is_raid_seed_message(message: discord.Message) -> bool:
    return REGEX_CONTENT.match(message.content)


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
