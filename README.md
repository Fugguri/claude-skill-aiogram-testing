# claude-skill-aiogram-testing

[![CI](https://github.com/Fugguri/claude-skill-aiogram-testing/actions/workflows/ci.yml/badge.svg)](https://github.com/Fugguri/claude-skill-aiogram-testing/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![aiogram](https://img.shields.io/badge/aiogram-3.13%20%7C%203.20%20%7C%203.28-blue.svg)](https://github.com/aiogram/aiogram)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-orange.svg)](https://code.claude.com/docs/en/plugins-reference)
[![Version](https://img.shields.io/github/v/tag/Fugguri/claude-skill-aiogram-testing?label=version&sort=semver)](CHANGELOG.md)

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

## Installation flow

Verified `claude plugin marketplace add` + `claude plugin install` output (recorded against Claude Code locally):

```text
$ claude plugin marketplace add Fugguri/claude-skill-aiogram-testing
Adding marketplace…Cloning via SSH: git@github.com:Fugguri/claude-skill-aiogram-testing.git
Refreshing marketplace cache (timeout: 120s)…
Clone complete, validating marketplace…
✔ Successfully added marketplace: fugguri-aiogram-testing (declared in user settings)

$ claude plugin install testing-aiogram-bots@fugguri-aiogram-testing
Installing plugin "testing-aiogram-bots@fugguri-aiogram-testing"...
✔ Successfully installed plugin: testing-aiogram-bots@fugguri-aiogram-testing (scope: user)

$ claude plugin list | grep -A2 aiogram
  ❯ testing-aiogram-bots@fugguri-aiogram-testing
    Version: 0.6.0
    Scope: user
```

Once installed, the skill auto-activates when you ask Claude to write or extend pytest tests in an aiogram project. The expected behavior (not a guarantee, since model output is not deterministic): tests get created **under `tests/`** rather than at the project root, the documented factory fixtures are used instead of hand-built `Update`/`Message`/`Chat`/`User` objects, and the common AI hallucinations about aiogram testing (`aiogram.test_utils`, `aiogram-tests`) are flagged before they reach the code.

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
