---
name: testing-aiogram-bots
description: Use when writing pytest tests for aiogram 3.x bot handlers without launching a live bot — covers MockedBot setup, dispatching Update objects, asserting outgoing API calls, and FSM state checks
---

# Testing aiogram 3.x bots

## Overview

Цель — тестировать хендлеры aiogram 3.x юнит/интеграционно, без живого бота и без сети. Подход стандартный для сообщества aiogram (2024-2026): настоящий `Dispatcher`, настоящий `Router`, **фейковая HTTP-сессия** через `MockedBot`. Так проверяются filters, middlewares, FSM — баги в роутинге ловятся.

## ⚠️ Критично: знать и не путать

| Заблуждение | Правда |
|------|--------|
| `from aiogram.test_utils.mocked_bot import MockedBot` | **Не существует.** Модуля `aiogram.test_utils` в aiogram нет. |
| Поставить `aiogram-tests` с PyPI | **Заброшен** (последний релиз окт 2022, под alpha aiogram 3). Не работает с aiogram 3.x stable. |
| `pytest-aiogram` / `aiogram-pytest` на PyPI | **Пустые package squats** (0.1.0, без описания, без кода). |
| `MockedBot` импортируется откуда-то готовым | **Нет.** Его нужно скопировать из репо `aiogram/aiogram` (`tests/mocked_bot.py`, ветка `dev-3.x`) к себе в `tests/mocked_bot.py`. |

**Rule of thumb:** если subagent уверенно пишет `from aiogram.test_utils...` — это галлюцинация. Стоп, проверь.

## Setup (один раз на проект)

### 1. Зависимости
```bash
# uv
uv add --dev pytest pytest-asyncio
# или pip
pip install pytest pytest-asyncio
```

### 2. Скопировать MockedBot

Файл `tests/mocked_bot.py` уже есть в этом скилле — `mocked_bot.py` рядом с `SKILL.md`. Скопируй его в `tests/` твоего проекта:
```bash
cp ~/.claude/skills/testing-aiogram-bots/mocked_bot.py tests/mocked_bot.py
```

Альтернативно — скачать актуальную версию напрямую:
```bash
curl -o tests/mocked_bot.py https://raw.githubusercontent.com/aiogram/aiogram/dev-3.x/tests/mocked_bot.py
```

### 3. pyproject.toml — конфиг pytest
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]   # ВАЖНО: чтобы `from tests.mocked_bot import MockedBot` резолвилось
```

Без `pythonpath = ["."]` получишь `ModuleNotFoundError: No module named 'tests.mocked_bot'` — pytest не добавит корень проекта в sys.path автоматически (поведение `import_mode=prepend` смотрит на `rootdir`/`conftest.py`, не на корень проекта).

### 4. tests/__init__.py — пустой файл (чтобы pytest нашёл `mocked_bot`)
```bash
touch tests/__init__.py
```

## Минимальный пример: тест /start

**Хендлер:**
```python
# handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я фитнес-бот.")
```

**conftest.py:**
```python
# tests/conftest.py
from datetime import datetime

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from tests.mocked_bot import MockedBot


@pytest.fixture
def bot() -> MockedBot:
    return MockedBot()


@pytest.fixture
def dp() -> Dispatcher:
    from handlers.start import router
    d = Dispatcher(storage=MemoryStorage())
    d.include_router(router)
    return d


# --- helpers: убирают бойлерплейт из тестов ---

def _user(user_id: int = 1) -> User:
    return User(id=user_id, is_bot=False, first_name="Test")


def _chat(chat_id: int = 1) -> Chat:
    return Chat(id=chat_id, type="private")


@pytest.fixture
def make_message_update():
    """Фабрика Update с Message. `update = make_message_update("/start")`."""
    counter = {"n": 0}

    def _factory(text: str, *, user_id: int = 1, chat_id: int = 1) -> Update:
        counter["n"] += 1
        return Update(
            update_id=counter["n"],
            message=Message(
                message_id=counter["n"],
                date=datetime.now(),
                chat=_chat(chat_id),
                from_user=_user(user_id),
                text=text,
            ),
        )

    return _factory


@pytest.fixture
def make_callback_update():
    """Фабрика Update с CallbackQuery. `update = make_callback_update("confirm")`."""
    counter = {"n": 0}

    def _factory(data: str, *, user_id: int = 1, chat_id: int = 1, message_id: int = 1) -> Update:
        counter["n"] += 1
        return Update(
            update_id=counter["n"],
            callback_query=CallbackQuery(
                id=str(counter["n"]),
                from_user=_user(user_id),
                chat_instance="ci",
                data=data,
                message=Message(
                    message_id=message_id,
                    date=datetime.now(),
                    chat=_chat(chat_id),
                    text="prompt",
                ),
            ),
        )

    return _factory


@pytest.fixture
def stub_message():
    """Готовый Message для add_result_for(SendMessage, ...)."""
    return Message(
        message_id=999,
        date=datetime.now(),
        chat=_chat(),
        text="ok",
    )
```

**Тест:**
```python
# tests/test_start.py
from aiogram.methods import SendMessage


async def test_start_replies_with_greeting(bot, dp, make_message_update, stub_message):
    # ВАЖНО: MockedBot требует подготовить ответ Telegram заранее,
    # иначе session.responses пуст и make_request упадёт IndexError.
    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("/start"))

    sent = bot.get_request()  # последний вызванный метод API (LIFO)
    assert isinstance(sent, SendMessage)
    assert sent.chat_id == 1
    assert "Привет" in sent.text
```

Видишь — благодаря фикстурам `make_message_update` и `stub_message` (см. conftest выше) тест помещается в 5 строк вместо 30. Без фабрик каждый тест тонет в `Update/Message/Chat/User`-бойлерплейте.

**Запуск:** `pytest -v` (или `uv run pytest -v`).

## Quick Reference

| Что нужно | Как |
|-----------|-----|
| Создать бот | `MockedBot()` (токен подставится "42:TEST") |
| Подготовить ответ Telegram | `bot.add_result_for(SendMessage, ok=True, result=Message(...))` — **до** `feed_update`, по одному на каждый исходящий вызов |
| Прокачать апдейт через диспатчер | `await dp.feed_update(bot, Update(...))` |
| Проверить последний вызов API | `bot.get_request()` — возвращает объект `TelegramMethod` (`SendMessage`, `EditMessageText`, etc.), `.pop()` из deque |
| Проверить все вызовы | `list(bot.session.requests)` — deque всех вызовов в порядке поступления |
| Получить state в FSM | `ctx = dp.fsm.resolve_context(bot, chat_id=1, user_id=1)` (синхронно) → `await ctx.get_state()` |
| Установить state до теста | `await ctx.set_state(MyStates.waiting)` |
| Проверить data в FSM | `await ctx.get_data()` |
| Прокачать callback_query | `Update(update_id=1, callback_query=CallbackQuery(...))` |

## FSM-тест — пример

```python
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage


class Onboarding(StatesGroup):
    waiting_age = State()
    waiting_height = State()  # следующее состояние после ввода возраста


async def test_age_input_advances_state(bot, dp, make_message_update, stub_message):
    ctx = dp.fsm.resolve_context(bot, chat_id=1, user_id=1)
    await ctx.set_state(Onboarding.waiting_age)

    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("25"))

    new_state = await ctx.get_state()
    data = await ctx.get_data()
    assert new_state == Onboarding.waiting_height.state
    assert data["age"] == 25
```

> Заметь: `Onboarding.waiting_height.state` (строка `"Onboarding:waiting_height"`), не сам объект `State`. `FSMContext.get_state()` возвращает строку.

## Callback Query тест — пример

```python
from aiogram.methods import AnswerCallbackQuery, EditMessageText


async def test_confirm_button_edits_message(bot, dp, make_callback_update):
    # Ответы — в обратном порядке вызовов (deque LIFO!):
    # хендлер сначала EditMessageText, потом answer() callback → готовим в обратке
    bot.add_result_for(AnswerCallbackQuery, ok=True, result=True)
    bot.add_result_for(EditMessageText, ok=True, result=True)

    await dp.feed_update(bot, make_callback_update("confirm"))

    all_calls = list(bot.session.requests)
    assert any(isinstance(c, EditMessageText) for c in all_calls)
    assert any(isinstance(c, AnswerCallbackQuery) for c in all_calls)
```

## Common Mistakes

| Ошибка | Симптом | Фикс |
|--------|---------|------|
| Не подготовил `add_result_for` | `IndexError: pop from an empty deque` | Готовь ответ ПЕРЕД каждым ожидаемым вызовом |
| Хендлер шлёт 2 сообщения, ответ один | `IndexError` на втором вызове | `add_result_for` дважды |
| Хендлер шлёт `SendMessage`, потом `AnswerCallbackQuery` — pydantic ругается «expected Message, got bool» | `MockedSession.responses` это deque, `.pop()` справа = **LIFO** | Добавляй ответы в **обратном** порядке вызовов: сначала ответ на последний вызов, в конце — на первый |
| `from aiogram.test_utils.*` | `ModuleNotFoundError` | Скопировать `mocked_bot.py` к себе, импорт `from tests.mocked_bot import MockedBot` |
| `from_user=None` в Message | `TypeError` или фильтр не срабатывает | Всегда заполняй `from_user=User(...)` |
| Вызов хендлера напрямую (`await cmd_start(message)`) | Тест проходит, а на проде баг | Используй `dp.feed_update` — иначе обходишь filters/middleware/FSM |
| Нет `tests/__init__.py` | `ModuleNotFoundError: tests.mocked_bot` | Создать пустой `__init__.py` |
| `asyncio_mode` не настроен | `Async test functions are not natively supported` | `asyncio_mode = "auto"` в `pyproject.toml` или `@pytest.mark.asyncio` на каждый тест |

## Когда НЕ использовать этот подход

- **Тестируешь сам Telegram API** (загрузка файлов, лимиты) — нужен реальный бот / Telegram Test Server.
- **Чисто функциональная логика** (расчёт калорий, парсинг) — тестируй прямую функцию, без бота вообще.
- **End-to-end сценарий через несколько ботов/чатов** — лучше aiogram + ботовый dev-токен на тестовом сервере.

## Альтернатива (быстро, грубо)

`AsyncMock(spec=Bot)` + прямой вызов хендлера. Подходит, когда хендлер — простая функция и filters/middlewares не важны:

```python
from unittest.mock import AsyncMock

async def test_handler_direct():
    bot = AsyncMock(spec=Bot)
    msg = Message(message_id=1, date=datetime.now(),
                  chat=Chat(id=1, type="private"),
                  from_user=User(id=1, is_bot=False, first_name="T"),
                  text="/start")
    msg = msg.model_copy(update={"bot": bot})
    await cmd_start(msg)
    bot.send_message.assert_called_once()
```

**Минус:** не проходит через `Dispatcher` → не ловит баги фильтров, состояний, middleware. Не используй для критичных сценариев.

## Источники и кредиты

Этот скил **упаковывает community-паттерн**, а не изобретает его. Кредиты:

**aiogram framework и MockedBot:**
- [aiogram/aiogram](https://github.com/aiogram/aiogram) — фреймворк (MIT)
- [`tests/mocked_bot.py`](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) — эталонный `MockedBot`, vendored as-is
- [`tests/dispatcher`](https://github.com/aiogram/aiogram/tree/dev-3.x/tests/dispatcher) — реальные примеры от команды

**Мейнтейнеры aiogram:**
- [@JrooTJunior](https://github.com/JrooTJunior) (Alex Root Junior) — создатель и lead-мейнтейнер
- [@Olegt0rr](https://github.com/Olegt0rr) — core-мейнтейнер, архитектура aiogram 3
- [@MrMrRobat](https://github.com/MrMrRobat) — core-контрибьютор
- [full list](https://github.com/aiogram/aiogram/graphs/contributors)

**Обсуждение тестирования:**
- [aiogram issue #378](https://github.com/aiogram/aiogram/issues/378) — community thread, открыт с 2020, официального API так и нет — отсюда необходимость vendoring

**Упаковка в скил:** [@fugguri](https://github.com/Fugguri)
