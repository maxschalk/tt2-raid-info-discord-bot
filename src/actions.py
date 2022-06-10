import json
import re

import requests

from src.api_interface.make_request import make_request_sync
from src.STAGE import STAGE

AUTHOR_STR = "GameHive #raid-seed-export#0000"
REGEX_CONTENT = re.compile("^Raid seed export - ([0-9]{4}/[0-9]{2}/[0-9]{2})$")

EMOJI_CHECK_MARK = "✅"


async def handle_existing_seed_messages(channel):
    async for msg in channel.history():
        relevant = (
            str(msg.author) == AUTHOR_STR
            and REGEX_CONTENT.match(msg.content)
        )

        if not relevant:
            continue

        handled = any(map(
            lambda reaction: reaction.me and reaction.emoji == EMOJI_CHECK_MARK, msg.reactions
        ))

        if handled:
            return

        print(msg.content)

        if len(msg.attachments) != 1:
            # Log warning
            continue

        a, *_ = msg.attachments

        data = requests.get(a.url).json()

        filename = build_filename(msg.content)

        response = make_request_sync(
            method=requests.post,
            path=f"admin/raw_seed_file/{filename}",
            data=json.dumps(data),
            stage=STAGE,
            parse_response=False
        )

        if response.status_code == 200:
            await msg.add_reaction(emoji=EMOJI_CHECK_MARK)


def build_filename(s):
    matches = REGEX_CONTENT.match(s)

    seed_date = matches.group(1).replace('/', '')

    suffix = ".json"

    return f"raid_seed_{seed_date}{suffix}"
