import io
import json

import discord
from discord.ext import commands
from src.bot.bot_process_messages import factory_process_existing_messages
from src.model.seed_type import SeedType


def add_domain_commands(*, bot, process_context, data_provider):

    bot.add_command(
        factory_process_existing(process_context=process_context,
                                 data_provider=data_provider))
    bot.add_command(
        factory_get_seed_identifiers(process_context=process_context,
                                     data_provider=data_provider))
    bot.add_command(
        factory_get_seed_data(process_context=process_context,
                              data_provider=data_provider))
    bot.add_command(
        factory_delete_seed(process_context=process_context,
                            data_provider=data_provider))


def factory_process_existing(*, process_context, data_provider):

    process_existing_messages = factory_process_existing_messages(
        data_provider=data_provider)

    @commands.has_role('admin')
    @commands.command(name='process', aliases=['p'])
    async def func(context):
        await process_context(context=context)

        await process_existing_messages(channel=context.channel)

    return func


def factory_get_seed_identifiers(*, process_context, data_provider):

    async def get_seed_identifiers(*,
                                   context,
                                   count: int = None) -> list[str] | str:

        try:
            data = data_provider.list_seed_identifiers()
        except Exception as error:
            await context.channel.send(
                f"Error getting seed identifiers: {error}")

        count = count or len(data)

        seed_ids = data[-count:]

        text = str.join('\n', seed_ids)

        await context.channel.send(f"_ _\n{text}")

    @commands.has_role('admin')
    @commands.command(name='seed-identifiers', aliases=['sids'])
    async def func(context, count: int = None):
        await process_context(context=context)

        await get_seed_identifiers(context=context, count=count)

    return func


def factory_get_seed_data(*, process_context, data_provider):

    async def get_seed_data(*, context, identifier: str,
                            seed_type: SeedType) -> tuple[str, str]:

        try:
            data = data_provider.get_seed(identifier=identifier,
                                          seed_type=seed_type)
        except Exception as error:
            await context.channel.send(f"Error getting seed: {error}")

        file_obj = io.StringIO(json.dumps(data, indent=4))
        await context.channel.send(file=discord.File(
            fp=file_obj, filename=f"{seed_type.value}_{identifier}.json"))

    @commands.has_role('admin')
    @commands.command(name='seed', aliases=['s'])
    async def func(context,
                   identifier: str,
                   seed_type: SeedType = SeedType.RAW):
        await process_context(context=context)

        await get_seed_data(context=context,
                            identifier=identifier,
                            seed_type=seed_type)

    return func


def factory_delete_seed(*, process_context, data_provider):

    async def _delete_seed(*, context, identifier: str):

        try:
            data_provider.delete_seed(identifier=identifier)
        except Exception as error:
            await context.channel.send(f"Error deleting seed: {error}")
            return

        await context.channel.send(f"Deleted seed {identifier}")

    @commands.has_role('admin')
    @commands.command(name='delete-seed', aliases=['ds'])
    async def func(context, identifier: str):
        await process_context(context=context)

        await _delete_seed(context=context, identifier=identifier)

    return func