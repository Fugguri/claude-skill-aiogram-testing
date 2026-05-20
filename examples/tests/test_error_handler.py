from aiogram.methods import SendMessage


async def test_error_handler_intercepts_crash(bot, dp, make_message_update, stub_message):
    # Handler raises; error-handler then sends a follow-up message.
    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    # Important: without an error handler this would NOT raise out of feed_update —
    # aiogram swallows it. With the error handler registered, the recovery
    # message is the only observable proof.
    await dp.feed_update(bot, make_message_update("/boom"))

    sent = bot.get_request()
    assert isinstance(sent, SendMessage)
    assert "Caught: RuntimeError" in sent.text
