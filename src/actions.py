import asyncio
import json
import re

import requests

from src.api_interface.make_request import make_request_sync
from src.STAGE import STAGE

BOT_AUTHOR = "pingu#4195"
SEED_AUTHOR = "GameHive #raid-seed-export#0000"
REGEX_CONTENT = re.compile("^Raid seed export - ([0-9]{4}/[0-9]{2}/[0-9]{2})$")

EMOJI_CHECK_MARK = "✅"
EMOJI_RED_CROSS = "❌"


async def reaction_handled(reaction):
    if reaction.emoji not in {EMOJI_CHECK_MARK, EMOJI_RED_CROSS}:
        return False

    if reaction.me:
        return True

    async for user in reaction.users():
        if full_username(user) == BOT_AUTHOR:
            return True

    return False


async def handle_existing_seed_messages(channel):
    async for msg in channel.history():

        for r in msg.reactions:
            if await reaction_handled(r):
                return

        # handled = any([await reaction_handled(r) for r in msg.reactions])

        # if handled:
        #     return

        try:
            await handle_message(msg)
        except RuntimeError as e:
            await msg.add_reaction(emoji=EMOJI_RED_CROSS)
            await msg.reply(e)

            continue

            error_msg = f"Bot startup: Erroneous existing messages, error details as replies to {EMOJI_RED_CROSS} messages"
            raise RuntimeError(error_msg)


async def handle_message(msg):
    author_name = full_username(msg.author)

    relevant = (
        (author_name in {SEED_AUTHOR, BOT_AUTHOR})
        and
        REGEX_CONTENT.match(msg.content)
    )

    if not relevant:
        return

    print("relevant message found:", msg.content)

    if len(msg.attachments) != 1:
        await msg.add_reaction(emoji=EMOJI_RED_CROSS)

        await throw_err_on_msg(
            msg, f"Message fits criteria (author, content format), but has {len(msg.attachments)} attachments: {msg.attachments}"
        )

    a, *_ = msg.attachments

    data = requests.get(a.url).json()

    filename = build_filename(msg.content)

    response = make_request_sync(
        method=requests.post,
        path=f"admin/raw_seed_file/{filename}",
        data=json.dumps(data),
        stage=STAGE,
        parse_response=False
    )

    response_data = response.json()

    if response.status_code == 200:

        if response_data["file_created"]:
            await msg.add_reaction(emoji=EMOJI_CHECK_MARK)
            return

        await throw_err_on_msg(
            msg, f"File could not be created on server: {response_data}"
        )

    await throw_err_on_msg(
        msg, f"Server returned status code {response.status_code}: {response_data}"
    )


async def throw_err_on_msg(msg, text=""):
    await msg.add_reaction(emoji=EMOJI_RED_CROSS)

    if text:
        await msg.reply(text)

    raise RuntimeError(
        f"File could not be created on server: {response_data}"
    )


async def clear_all_reactions(channel):
    async for msg in channel.history():
        await msg.clear_reactions()


def full_username(user):
    return f"{user.display_name}#{user.discriminator}"


def build_filename(s):
    matches = REGEX_CONTENT.match(s)

    seed_date = matches.group(1).replace('/', '')

    suffix = ".json"

    return f"raid_seed_{seed_date}{suffix}"
