import os
from collections import namedtuple
from contextlib import suppress
from random import seed
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.actions import (EMOJI_RED_CROSS, handle_existing_seed_messages,
                         handle_message)

load_dotenv()


BOT_TOKEN = os.getenv('DISCORD_TOKEN')

GUILD_NAME = "pingu's arctic funhouse"
SEEDS_CHANNEL_NAME = "tt2-raid-rolls"

CommandArgument = namedtuple(
    "CommandArgument", ["name", "description", "type", "optional"],
    defaults=["", "", "Any", False]
)

COMMAND_PREFIX = '!'

bot = commands.Bot(command_prefix=COMMAND_PREFIX)


def get_guild_seeds_channel():
    guild = discord.utils.get(bot.guilds, name=GUILD_NAME)
    seeds_channel = discord.utils.get(
        guild.text_channels, name=SEEDS_CHANNEL_NAME
    )

    return guild, seeds_channel


def validate_context(context, guild, target_channels) -> bool:
    if context.guild != guild:
        raise commands.CommandError(
            "This command does not work in this guild"
        )

    if context.channel not in target_channels:
        raise commands.CommandError(
            "This command does not work in this channel"
        )

    return True


@bot.event
async def on_ready():
    print(f'{bot.user.name}#{bot.user.discriminator} has connected to Discord!')

    guild, seeds_channel = get_guild_seeds_channel()

    await seeds_channel.send("Hello there")

    if not guild or not seeds_channel:
        print("Did not connect to guild or text channels, closing bot client.")
        await bot.close()
        return

    print(f'{bot.user.name}#{bot.user.discriminator} has connected to {GUILD_NAME}.#{seeds_channel.name}')

    print("checking existing messages")

    try:
        await handle_existing_seed_messages(seeds_channel)
    except RuntimeError as e:
        await seeds_channel.send(e)

    print("done | bot is listening")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(content="I don't read my DMs, I'm really busy")

    await bot.process_commands(message)

    with suppress(RuntimeError):
        await handle_message(message)


@bot.command(
    name='delete-messages', aliases=['del'],
)
@commands.has_role('admin')
async def delete_recent_messages(context, count: int = 1):
    guild, seeds_channel = get_guild_seeds_channel()

    if not validate_context(context, guild, (seeds_channel, )):
        return

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    await context.message.delete()

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.delete()

    print(f"Deleted {count} messages in #{context.channel.name}")


@bot.command(
    name='clear-reactions', aliases=['cr'],
)
@commands.has_role('admin')
async def clear_reactions(context, count: int = 1):
    guild, seeds_channel = get_guild_seeds_channel()

    if not validate_context(context, guild, (seeds_channel, )):
        return

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    await context.message.delete()

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.clear_reactions()

    print(f"Cleared reactions on {count} messages in #{context.channel.name}")


def main():
    bot.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
