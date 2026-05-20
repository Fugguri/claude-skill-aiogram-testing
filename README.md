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

## Language note

The `SKILL.md` body is written in **Russian** (the AI consumes Markdown of any language equally well, and the author writes in Russian). Code examples are language-neutral Python. The frontmatter `description`, this README, and `CHANGELOG.md` are in English. PRs translating `SKILL.md` to English (as `SKILL.en.md`) are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Contents

- `skills/testing-aiogram-bots/SKILL.md` — the skill instructions (TDD workflow, setup, examples)
- `skills/testing-aiogram-bots/mocked_bot.py` — vendored `MockedBot` from `aiogram/aiogram` `dev-3.x`
- `skills/testing-aiogram-bots/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — marketplace registration

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

**This skill packaging:** [@fugguri](https://github.com/Fugguri) — wrote the SKILL.md instructions, AI-specific hallucination guardrails, examples, and packaged everything as a Claude Code plugin.

## License

MIT — see [LICENSE](LICENSE).
