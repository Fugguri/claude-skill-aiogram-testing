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
import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
```

**Тест:**
```python
# tests/test_start.py
from datetime import datetime

from aiogram.methods import SendMessage
from aiogram.types import Chat, Message, Update, User


async def test_start_replies_with_greeting(bot, dp):
    # ВАЖНО: MockedBot требует подготовить ответ Telegram заранее,
    # иначе session.responses будет пуст и make_request упадёт IndexError.
    bot.add_result_for(
        SendMessage,
        ok=True,
        result=Message(
            message_id=2,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            text="ok",
        ),
    )

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            from_user=User(id=1, is_bot=False, first_name="Test"),
            text="/start",
        ),
    )

    await dp.feed_update(bot, update)

    sent = bot.get_request()  # последний вызванный метод API
    assert isinstance(sent, SendMessage)
    assert sent.chat_id == 1
    assert "Привет" in sent.text
```

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

class Onboarding(StatesGroup):
    waiting_age = State()

async def test_age_input_advances_state(bot, dp):
    # Поставить начальное состояние
    ctx = dp.fsm.resolve_context(bot, chat_id=1, user_id=1)
    await ctx.set_state(Onboarding.waiting_age)

    bot.add_result_for(SendMessage, ok=True, result=Message(
        message_id=2, date=datetime.now(),
        chat=Chat(id=1, type="private"), text="ok"))

    update = Update(update_id=1, message=Message(
        message_id=1, date=datetime.now(),
        chat=Chat(id=1, type="private"),
        from_user=User(id=1, is_bot=False, first_name="T"),
        text="25"))

    await dp.feed_update(bot, update)

    new_state = await ctx.get_state()
    data = await ctx.get_data()
    assert new_state == Onboarding.waiting_height
    assert data["age"] == 25
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

## Источники

- [aiogram/aiogram dev-3.x — tests/mocked_bot.py](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) — эталонный `MockedBot`, обновляется командой aiogram
- [aiogram/aiogram tests/dispatcher](https://github.com/aiogram/aiogram/tree/dev-3.x/tests/dispatcher) — реальные примеры от мейнтейнеров
- [aiogram issue #378](https://github.com/aiogram/aiogram/issues/378) — обсуждение тестирования (открыто с 2020, официального решения нет)
