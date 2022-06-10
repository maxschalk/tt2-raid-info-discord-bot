import os
from random import seed
from typing import Optional

import discord
import requests
from discord import Emoji
from discord.ext import commands
from dotenv import load_dotenv

from src.actions import handle_existing_seed_messages
from src.api_interface.Stage import Stage

load_dotenv()

STAGE = os.getenv('STAGE') or Stage.PRODUCTION

API_AUTH_SECRET = os.getenv('API_AUTH_SECRET')

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')

GUILD: Optional[discord.Guild] = None
SEEDS_CHANNEL: Optional[discord.TextChannel] = None

COMMAND_PREFIX = '!'

bot = commands.Bot(command_prefix=COMMAND_PREFIX)


@bot.event
async def on_ready():
    print(f'{bot.user.name}#{bot.user.discriminator} has connected to Discord!')

    guild = discord.utils.get(bot.guilds, name=GUILD_NAME)
    seeds_channel = discord.utils.get(
        guild.text_channels, name="tt2-raid-rolls"
    )

    if not guild or not seeds_channel:
        print("Did not connect to guild or text channels, closing bot client.")
        await bot.close()
        return

    print(f'{bot.user.name}#{bot.user.discriminator} has connected to {GUILD_NAME}.#{seeds_channel.name}')

    global GUILD, SEEDS_CHANNEL
    GUILD = guild
    SEEDS_CHANNEL = seeds_channel

    print("checking existing messages")

    await handle_existing_seed_messages(seeds_channel)

    await bot.close()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(content="I don't read my DMs, I'm really busy")

    print(message)


def main():
    bot.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
