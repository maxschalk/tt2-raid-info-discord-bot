import json
from contextlib import suppress

import requests
from src.bot.utils import (BOT_USER, EMOJI_CHECK_MARK, EMOJI_RED_CROSS,
                           full_username, is_handled, is_relevant_message,
                           seed_identifier, throw_err_on_msg)
from src.domain.raid_seed_data_provider import RaidSeedDataProvider


def factory_process_message(data_provider: RaidSeedDataProvider):

    async def process_message(msg):
        if not is_relevant_message(msg):
            return

        print("relevant message found:", msg.content)

        if len(msg.attachments) != 1:
            await msg.add_reaction(emoji=EMOJI_RED_CROSS)

            await throw_err_on_msg(
                msg, f"Message fits criteria (author, content format), \
                but has {len(msg.attachments)} (!= 1) attachments")

        attachment = msg.attachments[0]

        data = requests.get(attachment.url).json()

        identifier = seed_identifier(from_msg_content=msg.content)

        try:
            data_provider.save_seed(identifier=identifier,
                                    data=json.dumps(data))
        except Exception as error:
            await throw_err_on_msg(msg, f"Error saving seed: {error}")

        await msg.add_reaction(emoji=EMOJI_CHECK_MARK)

    return process_message


def factory_process_existing_messages(data_provider: RaidSeedDataProvider):

    process_message = factory_process_message(data_provider)

    async def process_existing_messages(channel):
        async for msg in channel.history():

            if await is_handled(msg):
                return

            if full_username(msg.author) == BOT_USER:
                await msg.delete()

            with suppress(RuntimeError):
                await process_message(msg)

    return process_existing_messages
