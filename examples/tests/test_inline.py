from aiogram.methods import AnswerInlineQuery


async def test_inline_query_returns_one_result(bot, dp, make_inline_query_update):
    bot.add_result_for(AnswerInlineQuery, ok=True, result=True)

    await dp.feed_update(bot, make_inline_query_update("hello"))

    sent = bot.get_request()
    assert isinstance(sent, AnswerInlineQuery)
    assert len(sent.results) == 1
    assert "hello" in sent.results[0].title
