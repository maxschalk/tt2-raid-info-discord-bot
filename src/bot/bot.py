from contextlib import suppress
from typing import Callable

import discord
from discord.ext import commands
from src.domain.raid_seed_data_provider import RaidSeedDataProvider
from src.model.seed_type import SeedType

from . import actions
from .utils import full_username


def setup_bot(bot: commands.Bot, guild_name: str, channel_name: str,
              data_provider: RaidSeedDataProvider) -> None:

    get_guild = _create_get_guild(bot, guild_name)
    get_channel = _create_get_channel(channel_name)
    process_context = _create_process_context(get_guild, get_channel)

    # Event listeners
    bot.add_listener(
        _create_on_ready(bot, get_guild, get_channel, data_provider))
    bot.add_listener(_create_on_message(bot, data_provider))

    # Meta commands
    bot.add_command(_create_delete_recent_messages(process_context))
    bot.add_command(_create_clear_reactions(process_context))

    # Raid seed data commands
    bot.add_command(_create_process_existing(process_context, data_provider))
    bot.add_command(
        _create_get_seed_identifiers(process_context, data_provider))
    bot.add_command(_create_get_seed_data(process_context, data_provider))
    bot.add_command(_create_delete_seed(process_context, data_provider))


def _create_get_guild(bot, guild_name) -> Callable:
    return lambda: discord.utils.get(bot.guilds, name=guild_name)


def _create_get_channel(channel_name: str) -> Callable:

    def func(guild):
        if not guild:
            return None

        return discord.utils.get(guild.text_channels, name=channel_name)

    return func


def _validate_context(context, guild, target_channels) -> bool:
    if context.guild != guild:
        raise commands.CommandError("This command does not work in this guild")

    if context.channel not in target_channels:
        raise commands.CommandError(
            "This command does not work in this channel")

    return True


def _create_process_context(get_guild, get_channel):

    async def process_context(context):
        guild = get_guild()
        seeds_channel = get_channel(guild)

        if not _validate_context(context, guild, (seeds_channel, )):
            return

        await context.message.delete()

    return process_context


def _create_on_ready(bot, get_guild, get_channel, data_provider):

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
            await actions.process_existing_messages(seeds_channel,
                                                    data_provider)

    return on_ready


def _create_on_message(bot, data_provider):

    async def on_message(message):
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send(
                content="I don't read my DMs, I'm really busy")

            return

        await actions.process_message(message, data_provider)

    return on_message


def _create_delete_recent_messages(process_context):

    @commands.has_role('admin')
    @commands.command(name='delete-messages', aliases=['del'])
    async def func(context, count: int = 1):
        await process_context(context)

        await actions.delete_recent_messages(context=context, count=count)

    return func


def _create_clear_reactions(process_context):

    @commands.has_role('admin')
    @commands.command(name='clear-reactions', aliases=['cr'])
    async def func(context, count: int = 1):

        await process_context(context)

        await actions.clear_reactions(context=context, count=count)

    return func


def _create_process_existing(process_context, data_provider):

    @commands.has_role('admin')
    @commands.command(name='process', aliases=['p'])
    async def func(context):
        await process_context(context)

        await actions.process_existing_messages(context.channel, data_provider)

    return func


def _create_get_seed_identifiers(process_context, data_provider):

    @commands.has_role('admin')
    @commands.command(name='seed-identifiers', aliases=['sids'])
    async def func(context, count: int = None):
        await process_context(context)

        await actions.get_seed_identifiers(context=context,
                                           data_provider=data_provider,
                                           count=count)

    return func


def _create_get_seed_data(process_context, data_provider):

    @commands.has_role('admin')
    @commands.command(name='seed', aliases=['s'])
    async def func(context,
                   identifier: str,
                   seed_type: SeedType = SeedType.RAW):
        await process_context(context)

        await actions.get_seed_data(context=context,
                                    data_provider=data_provider,
                                    identifier=identifier,
                                    seed_type=seed_type)

    return func


def _create_delete_seed(process_context, data_provider):

    @commands.has_role('admin')
    @commands.command(name='delete-seed', aliases=['ds'])
    async def func(context, identifier: str):
        await process_context(context)

        await actions.delete_seed(context, data_provider, identifier)

    return func
