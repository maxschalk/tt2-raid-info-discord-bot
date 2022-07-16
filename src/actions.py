import io
import json
from contextlib import suppress

import discord
import requests
from discord.ext import commands

from src.api_interface.make_request import make_request_sync
from src.api_interface.SeedType import SeedType
from src.STAGE import STAGE
from src.utils import (BOT_AUTHOR, BOT_USER, EMOJI_CHECK_MARK, EMOJI_RED_CROSS,
                       full_username, is_relevant_message,
                       message_from_response, seed_data_filename)


async def _is_handled(reaction):
    if reaction.emoji not in {EMOJI_CHECK_MARK, EMOJI_RED_CROSS}:
        return False

    if reaction.me:
        return True

    async for user in reaction.users():
        if full_username(user) == BOT_AUTHOR:
            return True

    return False


async def _throw_err_on_msg(msg, text=""):
    await msg.add_reaction(emoji=EMOJI_RED_CROSS)

    if text:
        await msg.reply(text)

    raise RuntimeError(
        f"Something went wrong, please check individual {EMOJI_RED_CROSS} message replies"
    )


async def _clear_all_reactions(channel):
    async for msg in channel.history():
        await msg.clear_reactions()


async def process_existing_messages(channel):
    async for msg in channel.history():

        for r in msg.reactions:
            if await _is_handled(r):
                return

        if full_username(msg.author) == BOT_USER:
            await msg.delete()

        with suppress(RuntimeError):
            await process_message(msg)


async def process_message(msg):

    if not is_relevant_message(msg):
        return

    print("relevant message found:", msg.content)

    if len(msg.attachments) != 1:
        await msg.add_reaction(emoji=EMOJI_RED_CROSS)

        await _throw_err_on_msg(
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
        await _throw_err_on_msg(msg, message_from_response(response))

    response_data = response.json()

    if not response_data.get("created", False):
        await _throw_err_on_msg(msg, message_from_response(response))

    await msg.add_reaction(emoji=EMOJI_CHECK_MARK)


async def get_server_filenames(context, count: int = None) -> list[str] | str:

    response = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=STAGE,
        parse_response=False)

    if response.status_code != 200:
        await context.channel.send(message_from_response(response))
        return

    response_data = response.json()

    count = count or len(response_data)

    filenames = response_data[-count:]

    text = str.join('\n', filenames)

    await context.channel.send(f"_ _\n{text}")


async def download_server_file(context, filename: str,
                               seed_type: SeedType) -> tuple[str, str]:

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    response = make_request_sync(
        method=requests.get,
        path=f"admin/seed_file/{seed_type.value}/{filename}",
        stage=STAGE,
        parse_response=False)

    if response.status_code != 200:
        await context.channel.send(message_from_response(response))

    response_data = response.json()

    f = io.StringIO(json.dumps(response_data, indent=4))
    await context.channel.send(
        file=discord.File(fp=f, filename=f"{seed_type.value}_{filename}"))


async def delete_server_file(context, filename: str):

    response = make_request_sync(method=requests.delete,
                                 path=f"admin/raw_seed_file/{filename}",
                                 stage=STAGE,
                                 parse_response=False)

    await context.channel.send(message_from_response(response))


async def delete_recent_messages(context, count: int = 1):
    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.delete()

    print(f"Deleted {count} messages in #{context.channel.name}")


async def clear_reactions(context, count: int = 1):

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.clear_reactions()

    print(f"Cleared reactions on {count} messages in #{context.channel.name}")
