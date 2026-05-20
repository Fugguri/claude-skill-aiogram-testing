from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

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
