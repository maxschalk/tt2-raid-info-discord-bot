import re

import discord
from src.utils.get_env import get_env

BOT_AUTHOR_USERNAME = get_env(key="DISCORD_BOT_AUTHOR_USERNAME")
BOT_USERNAME = get_env(key="DISCORD_BOT_USERNAME")
RAID_SEED_AUTHOR_USERNAME = get_env(key="DISCORD_RAID_SEED_AUTHOR_USERNAME")

REGEX_CONTENT = re.compile("^Raid seed export - ([0-9]{4}/[0-9]{2}/[0-9]{2})$")

EMOJI_CHECK_MARK = "✅"
EMOJI_RED_CROSS = "❌"
EMOJI_PENGUIN = "🐧"


def full_username(*, user: discord.User) -> str:
    return f"{user.display_name}#{user.discriminator}"


def is_relevant_message(*, msg: discord.Message) -> bool:
    return _has_relevant_author(msg=msg) and _is_raid_seed_message(msg=msg)


def _has_relevant_author(*, msg: discord.Message) -> bool:
    author_name = full_username(user=msg.author)

    return author_name in {RAID_SEED_AUTHOR_USERNAME, BOT_AUTHOR_USERNAME}


def _is_raid_seed_message(*, msg: discord.Message) -> bool:
    return REGEX_CONTENT.match(msg.content)


def seed_identifier_from_msg(*, from_msg_content: str) -> str:
    matches = REGEX_CONTENT.match(from_msg_content)

    seed_date = matches.group(1).replace('/', '')

    return f"raid_seed_{seed_date}"


async def msg_is_handled(*, msg: discord.Message):
    for reaction in msg.reactions:
        if reaction.emoji not in {EMOJI_CHECK_MARK, EMOJI_RED_CROSS}:
            return False

        if reaction.me:
            return True

        if any(
                full_username(user=user) == BOT_AUTHOR_USERNAME
                async for user in reaction.users()):
            return True

        return False


async def throw_err_on_msg(*, msg, text=None):
    await msg.add_reaction(emoji=EMOJI_RED_CROSS)

    if text:
        await msg.reply(text)
