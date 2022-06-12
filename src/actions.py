import asyncio
import json
import re
from contextlib import suppress

import requests

from src.api_interface.make_request import make_request_sync
from src.constants import (BOT_AUTHOR, BOT_USER, EMOJI_CHECK_MARK,
                           EMOJI_PENGUIN, EMOJI_RED_CROSS, REGEX_CONTENT,
                           SEED_AUTHOR)
from src.STAGE import STAGE
from src.utils import full_username, seed_data_filename


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

        if full_username(msg.author) == BOT_USER:
            await msg.delete()

        with suppress(RuntimeError):
            await handle_message(msg)


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

    filename = seed_data_filename(from_msg_content=msg.content)

    response = make_request_sync(
        method=requests.post,
        path=f"admin/raw_seed_file/{filename}",
        data=json.dumps(data),
        stage=STAGE,
        parse_response=False
    )

    response_data = response.json()

    if response.status_code != 201:
        await throw_err_on_msg(
            msg, f"Server returned status code {response.status_code}: {response_data}"
        )

    if not response_data.get("created", False):
        await throw_err_on_msg(
            msg, f"File could not be created on server: {response_data.get('detail', response_data)}"
        )

    await msg.add_reaction(emoji=EMOJI_CHECK_MARK)


async def throw_err_on_msg(msg, text=""):
    await msg.add_reaction(emoji=EMOJI_RED_CROSS)

    if text:
        await msg.reply(text)

    raise RuntimeError(
        f"Something went wrong, please check individual {EMOJI_RED_CROSS} message replies"
    )


async def clear_all_reactions(channel):
    async for msg in channel.history():
        await msg.clear_reactions()
