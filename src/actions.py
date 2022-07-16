import json
import re
from contextlib import suppress

import requests

from src.api_interface.make_request import make_request_sync
from src.STAGE import STAGE
from src.utils import full_username, message_from_response, seed_data_filename

BOT_AUTHOR = "pingu#4195"
BOT_USER = "TT2RaidSeedBot#1932"
SEED_AUTHOR = "GameHive #raid-seed-export#0000"
REGEX_CONTENT = re.compile("^Raid seed export - ([0-9]{4}/[0-9]{2}/[0-9]{2})$")

EMOJI_CHECK_MARK = "✅"
EMOJI_RED_CROSS = "❌"
EMOJI_PENGUIN = "🐧"


async def _is_handled(reaction):
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
            if await _is_handled(r):
                return

        if full_username(msg.author) == BOT_USER:
            await msg.delete()

        with suppress(RuntimeError):
            await handle_message(msg)


async def handle_message(msg):
    author_name = full_username(msg.author)

    relevant = ((author_name in {SEED_AUTHOR, BOT_AUTHOR})
                and REGEX_CONTENT.match(msg.content))

    if not relevant:
        return

    print("relevant message found:", msg.content)

    if len(msg.attachments) != 1:
        await msg.add_reaction(emoji=EMOJI_RED_CROSS)

        await throw_err_on_msg(
            msg,
            f"Message fits criteria (author, content format), but has {len(msg.attachments)} (!= 1) attachments"
        )

    a, *_ = msg.attachments

    data = requests.get(a.url).json()

    filename = seed_data_filename(from_msg_content=msg.content)

    response = make_request_sync(method=requests.post,
                                 path=f"admin/raw_seed_file/{filename}",
                                 data=json.dumps(data),
                                 stage=STAGE,
                                 parse_response=False)

    if response.status_code != 201:
        await throw_err_on_msg(msg, message_from_response(response))

    response_data = response.json()

    if not response_data.get("created", False):
        await throw_err_on_msg(msg, message_from_response(response))

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
