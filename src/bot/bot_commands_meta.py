from discord.ext import commands


def add_meta_commands(*, bot, process_context):
    bot.add_command(
        factory_delete_recent_messages(process_context=process_context))
    bot.add_command(factory_clear_reactions(process_context=process_context))


def factory_delete_recent_messages(*, process_context):

    @commands.has_role('admin')
    @commands.command(name='delete-messages', aliases=['del'])
    async def func(context, count: int = 1):
        await process_context(context=context)

        await _delete_recent_messages(context=context, count=count)

    return func


def factory_clear_reactions(*, process_context):

    @commands.has_role('admin')
    @commands.command(name='clear-reactions', aliases=['cr'])
    async def func(context, count: int = 1):

        await process_context(context=context)

        await _clear_reactions(context=context, count=count)

    return func


async def _delete_recent_messages(*, context, count: int = 1):
    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.delete()

    print(f"Deleted {count} messages in #{context.channel.name}")


async def _clear_reactions(*, context, count: int = 1):

    if count <= 0:
        raise commands.BadArgument("Argument [count] must be greater than 0")

    messages = await context.channel.history(limit=count).flatten()

    for message in messages:
        await message.clear_reactions()

    print(f"Cleared reactions on {count} messages in #{context.channel.name}")
