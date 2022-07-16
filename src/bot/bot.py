import os
from contextlib import suppress

import discord
from discord.ext import commands
from src.api_interface.SeedType import SeedType
from src.utils import full_username, get_env_strict

from . import actions

GUILD_NAME = get_env_strict("GUILD_NAME")
SEEDS_CHANNEL_NAME = get_env_strict("SEEDS_CHANNEL_NAME")

bot = commands.Bot(command_prefix='!')


def _get_guild_channel():
    guild = discord.utils.get(bot.guilds, name=GUILD_NAME)

    if not guild:
        return None, None

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

    guild, seeds_channel = _get_guild_channel()

    if not guild or not seeds_channel:
        print("Did not connect to guild or text channels, closing bot client.")
        await bot.close()
        return

    print(
        f'{full_username(bot.user)} has connected to {GUILD_NAME}.#{seeds_channel.name}'
    )

    with suppress(RuntimeError):
        await actions.process_existing_messages(seeds_channel)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(
            content="I don't read my DMs, I'm really busy")

    await bot.process_commands(message)

    await actions.process_message(message)


async def _process_context(context):
    guild, seeds_channel = _get_guild_channel()

    if not _validate_context(context, guild, (seeds_channel, )):
        return

    await context.message.delete()


@bot.command(name='process', aliases=['p'])
@commands.has_role('admin')
async def process_existing(context):
    await _process_context(context)

    await actions.process_existing_messages(context.channel)


@bot.command(name='server-filenames', aliases=['sfs'])
@commands.has_role('admin')
async def get_server_files(context, count: int = None):
    await _process_context(context)

    await actions.get_server_filenames(context=context, count=count)


@bot.command(name='server-file', aliases=['sf'])
@commands.has_role('admin')
async def download_server_file(context,
                               filename: str,
                               seed_type: SeedType = SeedType.RAW):
    await _process_context(context)

    await actions.download_server_file(context=context,
                                       filename=filename,
                                       seed_type=seed_type)


@bot.command(name='delete-server-file', aliases=['dsf'])
@commands.has_role('admin')
async def delete_server_file(context, filename: str):
    await _process_context(context)

    await actions.delete_server_file(context=context, filename=filename)


@bot.command(name='delete-messages', aliases=['del'])
@commands.has_role('admin')
async def delete_recent_messages(context, count: int = 1):
    await _process_context(context)

    await actions.delete_recent_messages(context=context, count=count)


@bot.command(name='clear-reactions', aliases=['cr'])
@commands.has_role('admin')
async def clear_reactions(context, count: int = 1):
    await _process_context(context)

    await actions.clear_reactions(context=context, count=count)


def main():
    token = get_env_strict('DISCORD_TOKEN')
    bot.run(token)


if __name__ == '__main__':
    main()
