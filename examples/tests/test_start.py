from aiogram.methods import SendMessage


async def test_start_replies_with_greeting(bot, dp, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("/start"))

    sent = bot.get_request()
    assert isinstance(sent, SendMessage)
    assert sent.chat_id == 1
    assert "Привет" in sent.text
