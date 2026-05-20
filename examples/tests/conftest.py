from datetime import datetime
from itertools import count

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, InlineQuery, Message, Update, User

from tests.mocked_bot import MockedBot


@pytest.fixture
def bot() -> MockedBot:
    return MockedBot()


@pytest.fixture
def dp() -> Dispatcher:
    from handlers.start import router

    # Router is a module-level singleton. After the first include_router its
    # _parent_router is set; the next test would fail with
    # `Router is already attached to ...`. Reset before attaching.
    router._parent_router = None  # type: ignore[attr-defined]

    d = Dispatcher(storage=MemoryStorage())
    d.include_router(router)
    return d


def _user(user_id: int = 1) -> User:
    return User(id=user_id, is_bot=False, first_name="Test")


def _chat(chat_id: int = 1) -> Chat:
    return Chat(id=chat_id, type="private")


@pytest.fixture
def make_message_update():
    ids = count(1)

    def _factory(text: str, *, user_id: int = 1, chat_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            message=Message(
                message_id=n,
                date=datetime.now(),
                chat=_chat(chat_id),
                from_user=_user(user_id),
                text=text,
            ),
        )

    return _factory


@pytest.fixture
def make_callback_update():
    ids = count(1)

    def _factory(data: str, *, user_id: int = 1, chat_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            callback_query=CallbackQuery(
                id=str(n),
                from_user=_user(user_id),
                chat_instance="ci",
                data=data,
                message=Message(
                    message_id=n,
                    date=datetime.now(),
                    chat=_chat(chat_id),
                    text="prompt",
                ),
            ),
        )

    return _factory


@pytest.fixture
def make_inline_query_update():
    """Update-with-InlineQuery factory. `update = make_inline_query_update("search me")`."""
    ids = count(1)

    def _factory(query: str, *, user_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            inline_query=InlineQuery(
                id=str(n),
                from_user=_user(user_id),
                query=query,
                offset="",
            ),
        )

    return _factory


@pytest.fixture
def stub_message():
    return Message(
        message_id=999,
        date=datetime.now(),
        chat=_chat(),
        text="ok",
    )
