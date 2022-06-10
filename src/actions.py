import re
from itertools import takewhile
from random import randint

AUTHOR_STR = "GameHive #raid-seed-export#0000"
CONTENT_REGEX = "^Raid seed export - [0-9]{4}/[0-9]{2}/[0-9]{2}$"

EMOJI_CHECK_MARK = "✅"


async def handle_existing_seed_messages(channel):
    re_content = re.compile(CONTENT_REGEX)

    async for msg in channel.history():
        relevant = (str(msg.author) == AUTHOR_STR
                    and re_content.match(msg.content))

        if not relevant:
            continue

        handled = any(map(
            lambda reaction: reaction.me and reaction.emoji == EMOJI_CHECK_MARK, msg.reactions
        ))

        if handled:
            return

        print(msg.content)

        # await msg.add_reaction(emoji=EMOJI_CHECK_MARK)

    return

    for i, msg in enumerate(msgs):
        print(
            f"{i} | {msg.author}: {msg.content} | {msg.reactions}\nattachments: {msg.attachments}"
        )

    msg = seed_messages[0]

    print(
        f"{msg.author}: {msg.content} | {msg.reactions}\nattachments: {msg.attachments}"
    )

    await msg.add_reaction(emoji=EMOJI_CHECK_MARK)
    await msg.clear_reactions()

    # for a in msg.attachments:
    #     data = requests.get(a.url).json()
    #     print(data)
