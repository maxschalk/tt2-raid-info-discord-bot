import io
import json
import os
from contextlib import suppress

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

from src.actions import handle_existing_seed_messages, handle_message
from src.api_interface.make_request import make_request_sync
from src.api_interface.SeedType import SeedType
from src.STAGE import STAGE
from src.utils import full_username, message_from_response

load_dotenv()

GUILD_NAME = os.getenv("GUILD_NAME")
SEEDS_CHANNEL_NAME = os.getenv("SEEDS_CHANNEL_NAME")

bot = commands.Bot(command_prefix='!')


def _get_guild_seeds_channel():
    guild = discord.utils.get(bot.guilds, name=GUILD_NAME)
    seeds_channel = discord.utils.get(guild.text_channels,
                                      name=SEEDS_CHANNEL_NAME)

    return guild, seeds_channel


def _validate_context(context, guild, target_channels) -> bool:
    if context.guild != guild:
        raise commands.CommandError("This command does not work in this guild")

    if context.channel not in target_channels:
        raise commands.CommandError(
            "This command does not work in this channel")

    return True


@bot.event
async def on_ready():
    print(f'{full_username(bot.user)} has connected to Discord!')

    guild, seeds_channel = _get_guild_seeds_channel()

    if not guild or not seeds_channel:
        print("Did not connect to guild or text channels, closing bot client.")
        await bot.close()
        return

    print(
        f'{full_username(bot.user)} has connected to {GUILD_NAME}.#{seeds_channel.name}'
    )

    with suppress(RuntimeError):
        await handle_existing_seed_messages(seeds_channel)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(
            content="I don't read my DMs, I'm really busy")

    await bot.process_commands(message)

    with suppress(RuntimeError):
        await handle_message(message)


@bot.command(name='server-filenames', aliases=['sfs'])
@commands.has_role('admin')
async def get_server_files(context, count: int = None):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    await context.message.delete()

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

    text = str.join('\n', response_data[-count:])
    await context.channel.send(f"_ _\n{text}")


@bot.command(name='server-file', aliases=['sf'])
@commands.has_role('admin')
async def download_server_file(context,
                               filename: str,
                               seed_type: SeedType = SeedType.RAW):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    await context.message.delete()

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    response = make_request_sync(
        method=requests.get,
        path=f"admin/seed_file/{seed_type.value}/{filename}",
        stage=STAGE,
        parse_response=False)

    if response.status_code != 200:
        await context.channel.send(message_from_response(response))
        return

    response_data = response.json()

    try:
        f = io.StringIO(json.dumps(response_data, indent=4))
        await context.channel.send(
            file=discord.File(fp=f, filename=f"{seed_type.value}_{filename}"))

    except Exception as e:
        print(f"Error when fetching a file at command !server-file: {e}")
        await context.channel.send(message_from_response(response))


@bot.command(name='delete-server-file', aliases=['dsf'])
@commands.has_role('admin')
async def delete_server_files(context, filename: str):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    await context.message.delete()

    response = make_request_sync(method=requests.delete,
                                 path=f"admin/raw_seed_file/{filename}",
                                 stage=STAGE,
                                 parse_response=False)

    await context.channel.send(message_from_response(response))


@bot.command(name='process', aliases=['p'])
@commands.has_role('admin')
async def handle_existing(context):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    await context.message.delete()

    with suppress(RuntimeError):
        await handle_existing_seed_messages(context.channel)


@bot.command(name='delete-messages', aliases=['del'])
@commands.has_role('admin')
async def delete_recent_messages(context, count: int = 1):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    await context.message.delete()

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.delete()

    print(f"Deleted {count} messages in #{context.channel.name}")


@bot.command(name='clear-reactions', aliases=['cr'])
@commands.has_role('admin')
async def clear_reactions(context, count: int = 1):
    guild, seeds_channel = _get_guild_seeds_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    await context.message.delete()

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.clear_reactions()

    print(f"Cleared reactions on {count} messages in #{context.channel.name}")


def main():
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()
