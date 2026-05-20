from aiogram.methods import SendMessage

from handlers.start import Onboarding


async def test_age_input_advances_state(bot, dp, make_message_update, stub_message):
    ctx = dp.fsm.resolve_context(bot, chat_id=1, user_id=1)
    await ctx.set_state(Onboarding.waiting_age)

    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("25"))

    new_state = await ctx.get_state()
    data = await ctx.get_data()
    assert new_state == Onboarding.waiting_height.state
    assert data["age"] == 25
