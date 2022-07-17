from contextlib import suppress

import discord
from src.bot.bot_process_messages import (factory_process_existing_messages,
                                          factory_process_message)
from src.bot.utils import full_username


def add_event_listeners(bot, get_guild, get_channel, data_provider):
    bot.add_listener(
        factory_on_ready(bot, get_guild, get_channel, data_provider))

    bot.add_listener(factory_on_message(bot, data_provider))


def factory_on_ready(bot, get_guild, get_channel, data_provider):

    process_existing_messages = factory_process_existing_messages(
        data_provider)

    async def on_ready():
        print(f'{full_username(bot.user)} has connected to Discord!')

        guild = get_guild()
        seeds_channel = get_channel(guild)

        if not guild or not seeds_channel:
            print(
                "Did not connect to guild or text channels, closing bot client."
            )
            await bot.close()
            return

        print(
            f'{full_username(bot.user)} has connected to {guild.name}.#{seeds_channel.name}'
        )

        with suppress(RuntimeError):
            await process_existing_messages(seeds_channel)

    return on_ready


def factory_on_message(bot, data_provider):

    process_message = factory_process_message(data_provider)

    async def on_message(message):
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send(
                content="I don't read my DMs, I'm really busy")

            return

        await process_message(message)

    return on_message
