import asyncio
from dataclasses import dataclass
from typing import Iterable
from unittest.mock import MagicMock

import pytest

from .utils import (BOT_AUTHOR_USERNAME, BOT_USERNAME, EMOJI_CHECK_MARK,
                    EMOJI_RED_CROSS, USERNAME_SEPARATOR, _has_relevant_author,
                    _is_raid_seed_message, full_username, is_relevant_message,
                    msg_is_handled, seed_identifier_from_msg, throw_err_on_msg)


class AsyncIterator:

    def __init__(self, iterable) -> None:
        self.iterable = iterable
        self.iterator = None

    def __aiter__(self):
        self.iterator = iter(self.iterable)

        return self

    async def __anext__(self):
        try:
            return next(self.iterator)
        except StopIteration:
            raise StopAsyncIteration


@dataclass
class MockUser:
    display_name: str = ""
    discriminator: str = ""


@dataclass
class MockReaction:
    emoji: str = "X"

    me: bool = False

    _users: tuple[MockUser] = tuple()

    def users(self):
        return AsyncIterator(self._users)


@dataclass
class MockMessage:
    author: MockUser = None
    content: str = ""
    reactions: Iterable[MockReaction] = None

    async def add_reaction(self, *args, **kwargs):
        return _async_return(None)

    async def reply(self, *args, **kwargs):
        return _async_return(None)


def _async_return(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


def test_full_username():
    cases = (
        ("name", "id"),
        ("", "id"),
        ("name", ""),
        ("", ""),
    )

    for display_name, discriminator in cases:
        user = MockUser(display_name=display_name, discriminator=discriminator)

        actual = full_username(user=user)
        expected = f"{display_name}{USERNAME_SEPARATOR}{discriminator}"

        assert actual == expected


def test_message_relevance():

    author_cases = (
        (BOT_AUTHOR_USERNAME.split(USERNAME_SEPARATOR), True),
        (("GameHive #raid-seed-export", "0000"), True),
        (BOT_USERNAME.split(USERNAME_SEPARATOR), False),
        (("name", "id"), False),
        (("", "id"), False),
        (("name", ""), False),
        (("", ""), False),
    )

    message_cases = (
        ("Raid seed export - 0000/00/00", True),
        ("Raid seed export - 1234/56/78", True),
        ("SRaid seed export - 1234/56/78", False),
        ("S Raid seed export - 1234/56/78", False),
        ("Raid seed export - 1234/56/78E", False),
        ("Raid seed export - 1234/56/78 E", False),
        ("Raid seed export", False),
        ("1234/56/78", False),
        ("Raid seed export - abcd/ef/gh", False),
    )

    for (display_name, discriminator), expected_author in author_cases:

        user = MockUser(display_name=display_name, discriminator=discriminator)
        msg = MockMessage(author=user)

        actual = _has_relevant_author(msg=msg)

        assert actual == expected_author

        for content, expected_message in message_cases:
            msg = MockMessage(content=content)

            actual = _is_raid_seed_message(msg=msg)

            assert actual == expected_message

            msg = MockMessage(author=user, content=content)

            actual = is_relevant_message(msg=msg)
            expected = expected_author and expected_message

            assert actual == expected


def test_seed_identifier_from_msg():
    cases = (
        ("Raid seed export - 0000/00/00", "raid_seed_00000000"),
        ("Raid seed export - 1234/56/78", "raid_seed_12345678"),
    )

    for content, expected in cases:
        actual = seed_identifier_from_msg(from_msg_content=content)

        assert actual == expected


@pytest.mark.asyncio
async def test_msg_is_handled():

    @dataclass
    class Case:
        expected: bool

        reactions: tuple[MockReaction] = tuple()

    cases = (
        # no reactions
        Case(expected=False),

        # irrelevant reaction by bot
        Case(
            expected=False,
            reactions=(MockReaction(me=True), ),
        ),

        # relevant reaction by irrelevant user
        Case(
            expected=False,
            reactions=(MockReaction(emoji=EMOJI_CHECK_MARK), ),
        ),

        # relevant reaction by bot
        Case(
            expected=True,
            reactions=(MockReaction(emoji=EMOJI_CHECK_MARK, me=True), ),
        ),

        # relevant reaction by bot as number 2
        Case(
            expected=True,
            reactions=(
                MockReaction(),
                MockReaction(emoji=EMOJI_CHECK_MARK, me=True),
            ),
        ),

        # relevant reaction by bot author
        Case(
            expected=True,
            reactions=(MockReaction(
                emoji=EMOJI_CHECK_MARK,
                _users=(MockUser(
                    *BOT_AUTHOR_USERNAME.split(USERNAME_SEPARATOR)), )), ),
        ),

        # relevant reaction by bot author as number 2
        Case(
            expected=True,
            reactions=(MockReaction(
                emoji=EMOJI_CHECK_MARK,
                _users=(
                    MockUser(),
                    MockUser(*BOT_AUTHOR_USERNAME.split(USERNAME_SEPARATOR)),
                )), ),
        ),
    )

    for case in cases:
        msg = MockMessage(reactions=case.reactions)

        actual = await msg_is_handled(msg=msg)

        assert actual == case.expected


@pytest.mark.asyncio
async def test_throw_err_on_msg():
    cases = (
        {
            "text": "error text"
        },
        {
            "text": ""
        },
        {},
    )

    for kwargs in cases:
        msg = MockMessage()

        msg.add_reaction = MagicMock(return_value=_async_return(None))
        msg.reply = MagicMock(return_value=_async_return(None))

        await throw_err_on_msg(msg=msg, **kwargs)

        msg.add_reaction.assert_called_once_with(emoji=EMOJI_RED_CROSS)

        if text := kwargs.get("text", None):
            msg.reply.assert_called_once_with(text)
        else:
            msg.reply.assert_not_called()
