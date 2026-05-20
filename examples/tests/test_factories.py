"""Smoke tests for the conftest factories themselves.

If aiogram tightens validation on Update/Message/CallbackQuery/InlineQuery
in a future release (e.g., a previously-optional field becomes required),
these tests fail with a clear pydantic message instead of every downstream
handler test failing for an obscure reason.
"""
from aiogram.types import CallbackQuery, InlineQuery, Message, Update


def test_make_message_update_produces_valid_update(make_message_update):
    update = make_message_update("/start")
    assert isinstance(update, Update)
    assert isinstance(update.message, Message)
    assert update.message.text == "/start"
    assert update.message.from_user is not None
    assert update.message.chat.id == 1


def test_make_message_update_increments_ids(make_message_update):
    u1 = make_message_update("a")
    u2 = make_message_update("b")
    assert u1.update_id != u2.update_id
    assert u1.message.message_id != u2.message.message_id


def test_make_callback_update_produces_valid_update(make_callback_update):
    update = make_callback_update("confirm")
    assert isinstance(update, Update)
    assert isinstance(update.callback_query, CallbackQuery)
    assert update.callback_query.data == "confirm"
    assert update.callback_query.message is not None


def test_make_inline_query_update_produces_valid_update(make_inline_query_update):
    update = make_inline_query_update("search me")
    assert isinstance(update, Update)
    assert isinstance(update.inline_query, InlineQuery)
    assert update.inline_query.query == "search me"
    assert update.inline_query.offset == ""


def test_stub_message_is_valid_message(stub_message):
    assert isinstance(stub_message, Message)
    assert stub_message.chat.id == 1
