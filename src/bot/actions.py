import io
import json
from contextlib import suppress
from http.client import HTTPException

import discord
import requests
from discord.ext import commands
from src.model.SeedType import SeedType
from src.RaidSeedDataAPI.raid_seed_data_api import RaidSeedDataAPI
from src.utils import get_env_strict

from .utils import (BOT_AUTHOR, BOT_USER, EMOJI_CHECK_MARK, EMOJI_RED_CROSS,
                    full_username, is_relevant_message, seed_identifier)

provider = RaidSeedDataAPI(
    base_url=get_env_strict("RAID_SEED_DATA_API_BASE_URL"),
    auth_key=get_env_strict("RAID_SEED_DATA_API_AUTH_SECRET"))


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

        for reaction in msg.reactions:
            if await _is_handled(reaction):
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
            msg, f"Message fits criteria (author, content format), \
            but has {len(msg.attachments)} (!= 1) attachments")

    attachment, *_ = msg.attachments

    data = requests.get(attachment.url).json()

    identifier = seed_identifier(from_msg_content=msg.content)

    try:
        provider.save_seed(identifier=identifier, data=json.dumps(data))
    except HTTPException as error:
        await _throw_err_on_msg(msg, f"Error saving seed: {error}")

    await msg.add_reaction(emoji=EMOJI_CHECK_MARK)


async def get_seed_identifiers(context, count: int = None) -> list[str] | str:

    try:
        data = provider.list_seed_identifiers()
    except HTTPException as error:
        await context.channel.send(f"Error getting seed identifiers: {error}")

    count = count or len(data)

    seed_ids = data[-count:]

    text = str.join('\n', seed_ids)

    await context.channel.send(f"_ _\n{text}")


async def get_seed_data(context, identifier: str,
                        seed_type: SeedType) -> tuple[str, str]:

    try:
        data = provider.get_seed(identifier=identifier, seed_type=seed_type)
    except HTTPException as error:
        await context.channel.send(f"Error getting seed: {error}")

    file_obj = io.StringIO(json.dumps(data, indent=4))
    await context.channel.send(file=discord.File(
        fp=file_obj, filename=f"{seed_type.value}_{identifier}"))


async def delete_seed(context, identifier: str):

    try:
        provider.delete_seed(identifier=identifier)
    except HTTPException as error:
        await context.channel.send(f"Error deleting seed: {error}")
        return

    await context.channel.send(f"Deleted seed {identifier}")


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
