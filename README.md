# claude-skill-aiogram-testing

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill for writing pytest tests for **aiogram 3.x** Telegram bot handlers — without launching a live bot and without network.

## What it does

Guides Claude through the community-standard aiogram 3.x testing pattern:

- Real `Dispatcher` + `Router` + **fake HTTP session** via `MockedBot`
- Dispatching `Update` objects through actual filters/middlewares
- Asserting outgoing Telegram API calls (`SendMessage`, `EditMessageText`, ...)
- Verifying FSM state transitions
- Catches routing bugs that mock-everything tests miss

## Why this skill exists

There is a lot of misinformation about aiogram testing:

| Common AI hallucination | Reality |
|------|--------|
| `from aiogram.test_utils.mocked_bot import MockedBot` | Module does not exist |
| `pip install aiogram-tests` | Abandoned since Oct 2022, alpha-aiogram-3 only |
| `pytest-aiogram` / `aiogram-pytest` on PyPI | Empty squats |

The actual canonical approach: copy `MockedBot` from `aiogram/aiogram` repo (`tests/mocked_bot.py`, `dev-3.x` branch) into your project. This skill ships that file and the full TDD workflow.

## Installation

### Option A: Claude Code plugin (recommended)

```
/plugin marketplace add Fugguri/claude-skill-aiogram-testing
/plugin install testing-aiogram-bots@fugguri-aiogram-testing
```

### Option B: Manual

```bash
git clone https://github.com/Fugguri/claude-skill-aiogram-testing.git
cp -r claude-skill-aiogram-testing/skills/testing-aiogram-bots ~/.claude/skills/
```

## Usage

When working on an aiogram project, ask Claude to "write tests for this handler" or "add pytest coverage for the FSM flow" — the skill auto-activates and follows the included workflow.

## Demo (what installation + a test loop looks like)

```text
$ claude plugin marketplace add Fugguri/claude-skill-aiogram-testing
Adding marketplace…
Cloning via SSH: git@github.com:Fugguri/claude-skill-aiogram-testing.git
✔ Successfully added marketplace: fugguri-aiogram-testing

$ claude plugin install testing-aiogram-bots@fugguri-aiogram-testing
✔ Successfully installed plugin: testing-aiogram-bots@fugguri-aiogram-testing

$ claude
> write me a pytest test for the /start handler in handlers/start.py

  [skill: testing-aiogram-bots activated]
  Following the documented layout — creating tests/conftest.py with the
  MockedBot + factory fixtures, then tests/test_start.py.

  ✓ tests/mocked_bot.py        (vendored from this skill)
  ✓ tests/__init__.py
  ✓ tests/conftest.py          (bot, dp, make_message_update, stub_message)
  ✓ tests/test_start.py        (asserts SendMessage call, chat_id, reply text)

  Running pytest -v tests/test_start.py …
  tests/test_start.py::test_start_replies_with_greeting PASSED
  1 passed in 0.21s
```

The skill instructs the model to (a) always place tests under `tests/`,
(b) copy `mocked_bot.py` from the plugin into the project, (c) use the
factory fixtures instead of building `Update`/`Message`/`Chat`/`User`
objects manually, and (d) flag the typical hallucinations (`aiogram.test_utils`,
`aiogram-tests`) before they reach the code.

## Languages

- `SKILL.md` — English (primary)
- `SKILL.ru.md` — Russian translation, kept in sync

Both files are equivalent in content. Pick whichever you prefer; the AI consumes either fine.

## Contents

- `skills/testing-aiogram-bots/SKILL.md` — the skill instructions (English, primary)
- `skills/testing-aiogram-bots/SKILL.ru.md` — Russian mirror, kept in sync via `scripts/check_doc_sync.py`
- `skills/testing-aiogram-bots/mocked_bot.py` — vendored `MockedBot` from `aiogram/aiogram` `dev-3.x`, pinned to a specific SHA (CI verifies it stays in sync)
- `skills/testing-aiogram-bots/AIOGRAM-LICENSE` — MIT license of upstream aiogram, shipped next to the vendored file
- `skills/testing-aiogram-bots/.claude-plugin/plugin.json` — plugin manifest (per [Claude Code plugin spec](https://code.claude.com/docs/en/plugins-reference))
- `.claude-plugin/marketplace.json` — marketplace registration
- `examples/` — runnable copy of the SKILL.md examples, exercised by CI on Python 3.10/3.11/3.12 × aiogram 3.13/3.20/3.28
- `scripts/check_doc_sync.py` — lint that pins critical snippets between `SKILL.md`, `SKILL.ru.md`, and `examples/`

## Credits

This skill packages a community testing pattern — it does not invent it. All credit for the underlying approach and `mocked_bot.py` belongs to the aiogram team and community.

**aiogram framework and `mocked_bot.py`:**
- [aiogram/aiogram](https://github.com/aiogram/aiogram) — the framework (MIT)
- [`tests/mocked_bot.py`](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) — vendored verbatim, copyright aiogram contributors

**aiogram maintainers & key contributors:**
- [@JrooTJunior](https://github.com/JrooTJunior) (Alex Root Junior) — aiogram creator and lead maintainer
- [@Olegt0rr](https://github.com/Olegt0rr) — core maintainer, aiogram 3 architecture
- [@MrMrRobat](https://github.com/MrMrRobat) — core contributor
- [aiogram contributors](https://github.com/aiogram/aiogram/graphs/contributors) — full list

**Reference discussion:**
- [aiogram issue #378](https://github.com/aiogram/aiogram/issues/378) — community thread on testing strategy, open since 2020

**This skill packaging:** [@Fugguri](https://github.com/Fugguri) — wrote the SKILL.md instructions, AI-specific hallucination guardrails, examples, and packaged everything as a Claude Code plugin.

## License

MIT — see [LICENSE](LICENSE).
