import pytest
from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import SendMessage
from aiogram.types import Message

from middlewares.auth import AuthMiddleware


@pytest.fixture
def dp_with_auth():
    router = Router()
    seen: dict[str, str] = {}

    @router.message()
    async def capture(message: Message, user_role: str):
        seen["role"] = user_role
        await message.answer("ok")

    d = Dispatcher(storage=MemoryStorage())
    d.message.middleware(AuthMiddleware())
    d.include_router(router)
    d._captured = seen  # type: ignore[attr-defined]
    return d


async def test_admin_user_gets_admin_role(bot, dp_with_auth, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)
    await dp_with_auth.feed_update(bot, make_message_update("hi", user_id=1))
    assert dp_with_auth._captured["role"] == "admin"


async def test_other_user_gets_guest_role(bot, dp_with_auth, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)
    await dp_with_auth.feed_update(bot, make_message_update("hi", user_id=42))
    assert dp_with_auth._captured["role"] == "guest"
