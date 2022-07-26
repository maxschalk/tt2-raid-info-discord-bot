from contextlib import suppress
from typing import Callable

import discord
from discord.ext import commands
from src.bot.bot_process_messages import (factory_process_existing_messages,
                                          factory_process_message)
from src.bot.utils import full_username
from src.domain.raid_seed_data_provider import RaidSeedDataProvider


def add_event_listeners(*, bot: commands.bot, get_guild: Callable,
                        get_channel: Callable,
                        data_provider: RaidSeedDataProvider) -> None:
    bot.add_listener(
        factory_on_ready(bot=bot,
                         get_guild=get_guild,
                         get_channel=get_channel,
                         data_provider=data_provider))

    bot.add_listener(factory_on_message(bot=bot, data_provider=data_provider))


def factory_on_ready(*, bot: commands.bot, get_guild: Callable,
                     get_channel: Callable,
                     data_provider: RaidSeedDataProvider) -> Callable:

    process_existing_messages = factory_process_existing_messages(
        data_provider=data_provider)

    async def on_ready():
        print(f'{full_username(user=bot.user)} has connected to Discord!')

        guild = get_guild()
        seeds_channel = get_channel(guild=guild)

        if not guild or not seeds_channel:
            print(
                "Did not connect to guild or text channels, closing bot client."
            )
            await bot.close()
            return

        print(
            f'{full_username(user=bot.user)} has connected to {guild.name}.#{seeds_channel.name}'
        )

        with suppress(RuntimeError):
            await process_existing_messages(channel=seeds_channel)

    return on_ready


def factory_on_message(*, bot: commands.bot,
                       data_provider: RaidSeedDataProvider) -> Callable:

    process_message = factory_process_message(data_provider=data_provider)

    async def on_message(message):
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send(
                content="I don't read my DMs, I'm really busy")

            return

        await process_message(msg=message)

    return on_message
