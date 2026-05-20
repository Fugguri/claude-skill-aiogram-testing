from aiogram.methods import AnswerCallbackQuery, EditMessageText


async def test_confirm_button_edits_message(bot, dp, make_callback_update):
    bot.add_result_for(AnswerCallbackQuery, ok=True, result=True)
    bot.add_result_for(EditMessageText, ok=True, result=True)

    await dp.feed_update(bot, make_callback_update("confirm"))

    all_calls = list(bot.session.requests)
    assert any(isinstance(c, EditMessageText) for c in all_calls)
    assert any(isinstance(c, AnswerCallbackQuery) for c in all_calls)
