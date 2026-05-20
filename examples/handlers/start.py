from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

router = Router()


class Onboarding(StatesGroup):
    waiting_age = State()
    waiting_height = State()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("Hello! I'm a fitness bot.")


@router.message(Onboarding.waiting_age)
async def on_age(message: Message, state: FSMContext) -> None:
    age = int(message.text)
    await state.update_data(age=age)
    await state.set_state(Onboarding.waiting_height)
    await message.answer("How tall are you?")


@router.callback_query(F.data == "confirm")
async def on_confirm(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text("Confirmed")
    await callback.answer()


@router.inline_query()
async def on_inline(query: InlineQuery) -> None:
    result = InlineQueryResultArticle(
        id="1",
        title=f"Result for {query.query}",
        input_message_content=InputTextMessageContent(message_text=f"You searched: {query.query}"),
    )
    await query.answer(results=[result], cache_time=1)


@router.message(Command("boom"))
async def cmd_boom(message: Message) -> None:
    raise RuntimeError("intentional crash for the error-handler test")


@router.error()
async def on_error(event) -> bool:
    # aiogram passes ErrorEvent here; we acknowledge it and notify the user.
    if event.update.message:
        await event.update.message.answer(f"Caught: {type(event.exception).__name__}")
    return True  # mark error as handled
