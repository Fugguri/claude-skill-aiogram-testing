---
name: testing-aiogram-bots
description: Use when writing pytest tests for aiogram 3.x bot handlers. All test files MUST be created under tests/ (never at project root). Covers MockedBot, Message/CallbackQuery/InlineQuery dispatch, FSM, middleware, error handlers — and blocks common AI hallucinations (no such module as aiogram.test_utils; aiogram-tests on PyPI is abandoned).
---

# Testing aiogram 3.x bots

> Russian version: [SKILL.ru.md](./SKILL.ru.md)

## Overview

The goal: unit- and integration-test aiogram 3.x handlers without a live bot and without network. This is the community-standard approach for aiogram (2024-2026): real `Dispatcher`, real `Router`, **fake HTTP session** through `MockedBot`. This way filters, middlewares, and FSM are exercised — routing bugs get caught.

## ⚠️ Critical: know and don't confuse

| Misconception | Truth |
|------|--------|
| `from aiogram.test_utils.mocked_bot import MockedBot` | **Doesn't exist.** There is no `aiogram.test_utils` module in aiogram. |
| Install `aiogram-tests` from PyPI | **Abandoned** (last release Oct 2022, built against alpha aiogram 3). Does not work with aiogram 3.x stable. |
| `pytest-aiogram` / `aiogram-pytest` on PyPI | **Empty package squats** (0.1.0, no description, no code). |
| `MockedBot` is importable from somewhere ready-made | **No.** You need to copy it from the `aiogram/aiogram` repo (`tests/mocked_bot.py`, `dev-3.x` branch) into your own `tests/mocked_bot.py`. |

**Rule of thumb:** if a subagent confidently writes `from aiogram.test_utils...` — it's a hallucination. Stop, verify.

## Where tests live (read this first)

**All test files go under `tests/` at the project root.** Never write `test_*.py`, `conftest.py`, or `mocked_bot.py` to the project root — even for a "quick" single test. Reasons:

- `pytest` discovery in this skill assumes `testpaths = ["tests"]`. A test placed at the project root will be silently skipped.
- `from tests.mocked_bot import MockedBot` only resolves if `mocked_bot.py` is inside `tests/`.
- Mixing source code and test files in the root makes packaging (`pip install .`, `uv build`) ship test fixtures into the wheel.

**Required layout for any new test:**
```
project_root/
├── handlers/
│   └── start.py
├── middlewares/
│   └── auth.py
├── tests/                    ← every test file lives here
│   ├── __init__.py           ← only when using import_mode=prepend
│   ├── conftest.py           ← fixtures (bot, dp, make_message_update, ...)
│   ├── mocked_bot.py         ← vendored from this skill
│   ├── test_start.py
│   ├── test_fsm.py
│   └── test_callbacks.py
└── pyproject.toml
```

If the `tests/` directory does not exist yet, create it before writing the first test. If `conftest.py` already exists at the root for some other reason, do **not** move it — append your fixtures to `tests/conftest.py` instead.

## Setup (once per project)

### 1. Dependencies
```bash
# uv
uv add --dev pytest pytest-asyncio
# or pip
pip install pytest pytest-asyncio
```

### 2. Copy MockedBot

The `tests/mocked_bot.py` file already ships with this skill — `mocked_bot.py` lives next to `SKILL.md`. Copy it into your project's `tests/`:
```bash
cp ~/.claude/skills/testing-aiogram-bots/mocked_bot.py tests/mocked_bot.py
```

Alternatively, fetch the current version directly:
```bash
curl -o tests/mocked_bot.py https://raw.githubusercontent.com/aiogram/aiogram/dev-3.x/tests/mocked_bot.py
```

### 3. pyproject.toml — pytest config

**Pytest 8+ (recommended, default `import_mode=importlib`):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
This is enough. `tests/__init__.py` is not required, `pythonpath` is not required — `importlib` mode handles it.

**Pytest <8 OR `import_mode = "prepend"` (the old default):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]   # so `from tests.mocked_bot import MockedBot` resolves
```
Plus create an empty `tests/__init__.py`:
```bash
touch tests/__init__.py
```
Without this you'll get `ModuleNotFoundError: No module named 'tests.mocked_bot'`.

## Minimal example: testing /start

**Handler:**
```python
# handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello! I'm a fitness bot.")
```

**conftest.py:**
```python
# tests/conftest.py
from datetime import datetime
from itertools import count

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

    # Router is a module-level singleton. After the first include_router its
    # _parent_router is set; the next test will fail with
    # `Router is already attached to ...`.
    router._parent_router = None  # type: ignore[attr-defined]

    d = Dispatcher(storage=MemoryStorage())
    d.include_router(router)
    return d


# --- helpers: remove boilerplate from tests ---

def _user(user_id: int = 1) -> User:
    return User(id=user_id, is_bot=False, first_name="Test")


def _chat(chat_id: int = 1) -> Chat:
    return Chat(id=chat_id, type="private")


@pytest.fixture
def make_message_update():
    """Update-with-Message factory. `update = make_message_update("/start")`."""
    ids = count(1)

    def _factory(text: str, *, user_id: int = 1, chat_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            message=Message(
                message_id=n,
                date=datetime.now(),
                chat=_chat(chat_id),
                from_user=_user(user_id),
                text=text,
            ),
        )

    return _factory


@pytest.fixture
def make_callback_update():
    """Update-with-CallbackQuery factory. `update = make_callback_update("confirm")`."""
    ids = count(1)

    def _factory(data: str, *, user_id: int = 1, chat_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            callback_query=CallbackQuery(
                id=str(n),
                from_user=_user(user_id),
                chat_instance="ci",
                data=data,
                message=Message(
                    message_id=n,
                    date=datetime.now(),
                    chat=_chat(chat_id),
                    text="prompt",
                ),
            ),
        )

    return _factory


@pytest.fixture
def make_inline_query_update():
    """Update-with-InlineQuery factory. `update = make_inline_query_update("search me")`."""
    ids = count(1)

    def _factory(query: str, *, user_id: int = 1) -> Update:
        n = next(ids)
        return Update(
            update_id=n,
            inline_query=InlineQuery(
                id=str(n),
                from_user=_user(user_id),
                query=query,
                offset="",
            ),
        )

    return _factory


@pytest.fixture
def stub_message():
    """Ready-made Message for add_result_for(SendMessage, ...)."""
    return Message(
        message_id=999,
        date=datetime.now(),
        chat=_chat(),
        text="ok",
    )
```

> Add `InlineQuery` to the `aiogram.types` import at the top of the file.
>
> **Extending the factories.** For update types not shown — `my_chat_member`, `poll`, `chat_join_request`, etc. — follow the same pattern: take the field name from the [`Update` model](https://docs.aiogram.dev/en/latest/api/types/update.html), construct the corresponding payload type with the minimal valid fields, wrap it in `Update(update_id=..., <field>=...)`, return.

**Test:**
```python
# tests/test_start.py
from aiogram.methods import SendMessage


async def test_start_replies_with_greeting(bot, dp, make_message_update, stub_message):
    # IMPORTANT: MockedBot requires you to queue the Telegram response in advance,
    # otherwise session.responses is empty and make_request raises IndexError.
    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("/start"))

    sent = bot.get_request()  # last API method called (LIFO)
    assert isinstance(sent, SendMessage)
    assert sent.chat_id == 1
    assert "Hello" in sent.text
```

Notice — thanks to `make_message_update` and `stub_message` fixtures (see conftest above), the test fits in 5 lines instead of 30. Without factories, every test drowns in `Update/Message/Chat/User` boilerplate.

**Run:** `pytest -v` (or `uv run pytest -v`).

## Quick Reference

| What you need | How |
|-----------|-----|
| Create a bot | `MockedBot()` (token defaults to `"42:TEST"`) |
| Queue a Telegram response | `bot.add_result_for(SendMessage, ok=True, result=Message(...))` — **before** `feed_update`, one per outgoing call |
| Feed an update through the dispatcher | `await dp.feed_update(bot, Update(...))` |
| Inspect the last API call | `bot.get_request()` — `.pop()` from a deque (see order table below) |
| Inspect all calls | `list(bot.session.requests)` — call order |
| Read FSM state | `ctx = dp.fsm.resolve_context(bot, chat_id=1, user_id=1)` (sync) → `await ctx.get_state()` |
| Set FSM state before a test | `await ctx.set_state(MyStates.waiting)` |
| Read FSM data | `await ctx.get_data()` |
| Feed a callback_query | `await dp.feed_update(bot, make_callback_update("confirm"))` — see the `make_callback_update` fixture above |
| Feed an inline_query | `await dp.feed_update(bot, make_inline_query_update("text"))` |
| Reset queued responses between sub-scenarios in one test | `bot.session.responses.clear()` (and `bot.session.requests.clear()` for the other side) |
| Pass a custom bot token | `MockedBot(token="123:ABC")` — the `kwargs.pop("token", ...)` accepts anything you give it; the default `"42:TEST"` is only used when omitted |

## Queue ordering in MockedSession (important)

`MockedSession` uses two `collections.deque` instances with `.append()` + `.pop()` from the right. That is **LIFO**. This produces two rules people get wrong most often:

| Queue | Access | Order | How to use |
|---------|--------|---------|------------------|
| `session.responses` (responses you queue up) | `bot.add_result_for(...)` writes on the right, `make_request` reads via `.pop()` on the right | **LIFO** | If the handler makes two calls in the order `A → B`, queue responses in reverse: first `add_result_for(B, ...)`, then `add_result_for(A, ...)`. The first `pop()` will hand back A's response (matching the first call), the second hands back B's. |
| `session.requests` (outgoing calls the handler made) | `make_request` writes on the right via `.append()` | **FIFO via `list(bot.session.requests)`** (deque iteration follows insertion order) — **LIFO via `bot.get_request()`** (`.pop()` from the right) | To check the full chronology: `list(bot.session.requests)` gives `[first, ..., last]`. To check the most recent one only: `bot.get_request()`. |

**Mnemonic:**
- *responses* — queue in reverse order ("response stack")
- *requests* — read via `list()` to see them in call order

## FSM test — example

```python
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage


class Onboarding(StatesGroup):
    waiting_age = State()
    waiting_height = State()  # next state after the user enters their age


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

> Notes:
> 1. `Onboarding.waiting_height.state` (the string `"Onboarding:waiting_height"`), not the `State` object itself. `FSMContext.get_state()` returns a string.
> 2. In real code put `Onboarding` next to the handlers (e.g., `handlers/start.py`) and `from handlers.start import Onboarding` in the test. Declaring `StatesGroup` inside a test file means the test and the handler would reference two **different** `State` objects and the assertion fails silently.

## Callback Query test — example

```python
from aiogram.methods import AnswerCallbackQuery, EditMessageText


async def test_confirm_button_edits_message(bot, dp, make_callback_update):
    # Handler does: EditMessageText (1st call), then answer() (2nd call).
    # responses is LIFO. Queue the response to the LAST call first, to the first call last:
    bot.add_result_for(AnswerCallbackQuery, ok=True, result=True)  # response to 2nd call
    bot.add_result_for(EditMessageText, ok=True, result=True)      # response to 1st call (top of stack)

    await dp.feed_update(bot, make_callback_update("confirm"))

    all_calls = list(bot.session.requests)
    assert any(isinstance(c, EditMessageText) for c in all_calls)
    assert any(isinstance(c, AnswerCallbackQuery) for c in all_calls)
```

## Inline query test

```python
from aiogram.methods import AnswerInlineQuery


async def test_inline_query_returns_one_result(bot, dp, make_inline_query_update):
    bot.add_result_for(AnswerInlineQuery, ok=True, result=True)

    await dp.feed_update(bot, make_inline_query_update("hello"))

    sent = bot.get_request()
    assert isinstance(sent, AnswerInlineQuery)
    assert len(sent.results) == 1
    assert "hello" in sent.results[0].title
```

## Error handler test

aiogram **swallows exceptions raised by handlers** when an `@router.error()` is registered — `dp.feed_update` does not re-raise. The only observable proof that recovery ran is the API call your error handler makes. Verify that, not the absence of an exception.

```python
# handlers/start.py
@router.message(Command("boom"))
async def cmd_boom(message: Message) -> None:
    raise RuntimeError("intentional crash")


@router.error()
async def on_error(event) -> bool:
    if event.update.message:
        await event.update.message.answer(f"Caught: {type(event.exception).__name__}")
    return True  # mark handled


# tests/test_error_handler.py
from aiogram.methods import SendMessage


async def test_error_handler_intercepts_crash(bot, dp, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)

    await dp.feed_update(bot, make_message_update("/boom"))

    sent = bot.get_request()
    assert isinstance(sent, SendMessage)
    assert "Caught: RuntimeError" in sent.text
```

If there is no `@router.error()` registered, the exception propagates out of `feed_update` and your test crashes with the original traceback. That is also a valid (and often clearer) assertion target:
```python
import pytest
with pytest.raises(RuntimeError, match="intentional crash"):
    await dp.feed_update(bot, make_message_update("/boom"))
```

## Middleware test

Middleware is registered on a `Dispatcher` or `Router` and fires during `feed_update` — meaning the same approach covers it. We verify: the middleware **ran** (e.g., dropped something into `data`) and the handler **received** that value.

```python
# middlewares/auth.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")  # use .get — not every update carries a user
        data["user_role"] = "admin" if user and user.id == 1 else "guest"
        return await handler(event, data)
```

```python
# tests/test_auth_middleware.py
from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import SendMessage
from aiogram.types import Message

import pytest

from middlewares.auth import AuthMiddleware


@pytest.fixture
def dp_with_auth():
    router = Router()
    seen = {}

    @router.message()
    async def capture(message: Message, user_role: str):
        seen["role"] = user_role
        await message.answer("ok")

    d = Dispatcher(storage=MemoryStorage())
    d.message.middleware(AuthMiddleware())
    d.include_router(router)
    d._captured = seen  # channel for the test to read
    return d


async def test_admin_user_gets_admin_role(bot, dp_with_auth, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)
    await dp_with_auth.feed_update(bot, make_message_update("hi", user_id=1))
    assert dp_with_auth._captured["role"] == "admin"


async def test_other_user_gets_guest_role(bot, dp_with_auth, make_message_update, stub_message):
    bot.add_result_for(SendMessage, ok=True, result=stub_message)
    await dp_with_auth.feed_update(bot, make_message_update("hi", user_id=42))
    assert dp_with_auth._captured["role"] == "guest"
```

**Key point:** don't call middleware directly as a function — you lose dispatcher integration (middleware order, outer vs inner, `event_from_user` injection). Drive it through `dp.feed_update`.

## Common Mistakes

| Mistake | Symptom | Fix |
|--------|---------|------|
| Forgot to call `add_result_for` | `IndexError: pop from an empty deque` | Queue the response BEFORE every expected outgoing call |
| Handler sends 2 messages, only one response queued | `IndexError` on the second call | Call `add_result_for` twice |
| Handler sends `SendMessage`, then `AnswerCallbackQuery` — pydantic complains "expected Message, got bool" | `session.responses` is a LIFO stack | Queue the response to the **last** call first, to the **first** call last (see "Queue ordering in MockedSession") |
| `from aiogram.test_utils.*` | `ModuleNotFoundError` | Copy `mocked_bot.py` into your project, import as `from tests.mocked_bot import MockedBot` |
| `from_user=None` in Message | `TypeError` or filter doesn't match | Always set `from_user=User(...)` |
| Calling the handler directly (`await cmd_start(message)`) | Test passes, prod breaks | Use `dp.feed_update` — otherwise you bypass filters/middleware/FSM |
| Missing `tests/__init__.py` (only in `import_mode=prepend`) | `ModuleNotFoundError: tests.mocked_bot` | Either create an empty `__init__.py` + `pythonpath = ["."]`, or use the pytest 8+ default `import_mode=importlib` (no `__init__.py`) |
| `asyncio_mode` not configured | `Async test functions are not natively supported` | `asyncio_mode = "auto"` in `pyproject.toml`, or `@pytest.mark.asyncio` on every test |
| Test thinks it caught a bug because no exception bubbled out, but `@router.error()` silently swallowed it | `dp.feed_update` swallows handler exceptions **only when an error handler is registered**. Without one, exceptions propagate | Assert on the recovery API call your error handler makes (or temporarily un-register the error handler with `dp.errors.handlers = []`). See "Error handler test". |
| Album messages (`media_group`) tested as a single update | Telegram delivers each photo as a separate `Update` with a shared `media_group_id`. aiogram does not bundle them into one event | Feed each photo with its own `Update` and the same `media_group_id`. If you need them as one event, use `aiogram.dispatcher.middlewares.user_context.UserContextMiddleware`-style buffering and test the buffer, not the raw stream. |
| Responses queued in test A leak into test B (shared `MockedBot`) | `pytest` fixtures are function-scoped by default, but if you've widened scope to `module` or `session`, the deques persist | Either keep `bot` fixture function-scoped (default), or explicitly call `bot.session.responses.clear()` + `bot.session.requests.clear()` in a teardown |
| Test files written to project root (`test_start.py` next to `main.py`) | `pytest` reports `collected 0 items`; or import errors because `from tests.mocked_bot import ...` does not resolve | All test files MUST live under `tests/`. See "Where tests live" at the top. Move the file to `tests/`, never the other way around. |
| Second test fails with `RuntimeError: Router is already attached to <Dispatcher ...>` | `Router` is imported as a module-level singleton — after the first `include_router` its `_parent_router` is set | **Preferred:** build a fresh `Router()` inside the fixture and re-register handlers via a factory (`def make_router(): ...` in your handlers module). **Quick workaround if refactoring is out of scope:** `router._parent_router = None` before `include_router`. **Last resort:** `importlib.reload(handlers.start)` (heavy, breaks identity comparisons). |

## When NOT to use this approach

- **Testing the Telegram API itself** (file uploads, rate limits) — you need a real bot or the Telegram Test Server.
- **Pure functional logic** (calorie computation, parsing) — test the function directly, no bot involved.
- **End-to-end scenarios across several bots/chats** — use aiogram + a dev token on the test server.
- **File downloads via `Bot.download_file` or similar.** `MockedSession.stream_content` returns empty bytes (`b""`); any test that exercises a download path will silently get a zero-byte file. Stub the download method directly with `unittest.mock` or use a real session for that one test.

## Alternative (quick and dirty)

`AsyncMock(spec=Bot)` plus a direct handler call. Fits when the handler is a simple function and filters/middlewares don't matter:

```python
from datetime import datetime
from unittest.mock import AsyncMock

from aiogram import Bot
from aiogram.types import Chat, Message, User

from handlers.start import cmd_start


async def test_handler_direct():
    bot = AsyncMock(spec=Bot)
    msg = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=1, type="private"),
        from_user=User(id=1, is_bot=False, first_name="T"),
        text="/start",
    )
    msg = msg.model_copy(update={"bot": bot})
    await cmd_start(msg)
    bot.send_message.assert_called_once()
```

**Downside:** doesn't go through `Dispatcher` → won't catch bugs in filters, states, or middleware. Don't use it for critical paths.

## Sources and credits

This skill **packages a community pattern**, it doesn't invent one. Credits:

**aiogram framework and MockedBot:**
- [aiogram/aiogram](https://github.com/aiogram/aiogram) — the framework (MIT)
- [`tests/mocked_bot.py`](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) — the reference `MockedBot`, vendored as-is
- [`tests/dispatcher`](https://github.com/aiogram/aiogram/tree/dev-3.x/tests/dispatcher) — real examples from the team

**aiogram maintainers:**
- [@JrooTJunior](https://github.com/JrooTJunior) (Alex Root Junior) — creator and lead maintainer
- [@Olegt0rr](https://github.com/Olegt0rr) — core maintainer, aiogram 3 architecture
- [@MrMrRobat](https://github.com/MrMrRobat) — core contributor
- [full list](https://github.com/aiogram/aiogram/graphs/contributors)

**Testing discussion:**
- [aiogram issue #378](https://github.com/aiogram/aiogram/issues/378) — community thread, open since 2020. No official API has landed — hence the need to vendor.

**Skill packaging:** [@Fugguri](https://github.com/Fugguri)
