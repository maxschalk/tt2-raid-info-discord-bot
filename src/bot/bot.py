from typing import Callable

import discord
from discord.ext import commands
from src.bot.bot_commands_domain import add_domain_commands
from src.bot.bot_commands_meta import add_meta_commands
from src.bot.bot_event_listeners import add_event_listeners
from src.domain.raid_seed_data_provider import RaidSeedDataProvider


def setup_bot(*, bot: commands.Bot, guild_name: str, channel_name: str,
              data_provider: RaidSeedDataProvider) -> None:

    get_guild = factory_get_guild(bot=bot, guild_name=guild_name)
    get_channel = factory_get_channel(channel_name=channel_name)
    process_context = factory_process_context(get_guild=get_guild,
                                              get_channel=get_channel)

    add_event_listeners(bot=bot,
                        get_guild=get_guild,
                        get_channel=get_channel,
                        data_provider=data_provider)

    add_meta_commands(bot=bot, process_context=process_context)

    add_domain_commands(bot=bot,
                        process_context=process_context,
                        data_provider=data_provider)


def factory_get_guild(*, bot, guild_name) -> Callable:
    return lambda: discord.utils.get(bot.guilds, name=guild_name)


def factory_get_channel(*, channel_name: str) -> Callable:

    def get_channel(*, guild: discord.Guild):
        if not guild:
            return None

        return discord.utils.get(guild.text_channels, name=channel_name)

    return get_channel


def factory_process_context(*, get_guild: Callable,
                            get_channel: Callable) -> Callable:

    async def process_context(*, context):
        guild = get_guild()
        seeds_channel = get_channel(guild=guild)

        if not _validate_context(context=context,
                                 guild=guild,
                                 target_channels=(seeds_channel, )):
            return

        await context.message.delete()

    return process_context


def _validate_context(*, context, guild, target_channels) -> bool:
    if context.guild != guild:
        raise commands.CommandError("This command does not work in this guild")

    if context.channel not in target_channels:
        raise commands.CommandError(
            "This command does not work in this channel")

    return True
