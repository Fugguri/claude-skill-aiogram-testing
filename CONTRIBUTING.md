# Contributing

Thanks for considering a contribution!

## Scope

This repo packages a single Claude Code skill: `testing-aiogram-bots`. It is intentionally narrow:
- Targets **aiogram 3.x** (not aiogram 2.x; not python-telegram-bot; not pyTelegramBotAPI).
- Focuses on **pytest** + the community `MockedBot` pattern.
- AI-specific guardrails (hallucination warnings) are a first-class feature, not a side note.

If your change broadens scope (different framework, different test runner, full E2E with real Telegram), please open an issue first — it may belong in a separate plugin.

## Setup

```bash
git clone https://github.com/Fugguri/claude-skill-aiogram-testing
cd claude-skill-aiogram-testing
python -m venv .venv && source .venv/bin/activate
pip install -r examples/requirements.txt
pytest examples/
```

CI runs the same `pytest examples/` against the documented `aiogram` + `pytest-asyncio` versions on every push.

## What we need

- **Better examples.** Edge cases, real-world patterns from your own bots.
- **English translation** of `SKILL.md` (as `SKILL.en.md`). Keep examples identical; translate prose.
- **Upstream sync.** When `aiogram/aiogram` updates `tests/mocked_bot.py`, refresh:
  ```bash
  curl -o skills/testing-aiogram-bots/mocked_bot.py \
    https://raw.githubusercontent.com/aiogram/aiogram/dev-3.x/tests/mocked_bot.py
  ```
  Then bump the `Pinned SHA` header in `mocked_bot.py`, bump version in `plugin.json` + `.claude-plugin/marketplace.json`, and add a `CHANGELOG.md` entry.
- **Bug reports** with a minimal reproduction.

## PR rules

1. One concern per PR.
2. Bump version in **both** `plugin.json` and `.claude-plugin/marketplace.json` if the skill content changes.
3. Update `CHANGELOG.md` under `## [Unreleased]` (create the section if missing).
4. If you change `SKILL.md` examples, make sure the matching runnable copy under `examples/` still passes `pytest examples/`.
5. Keep AI-hallucination guardrail wording sharp — those are the most-valuable parts.

## Style

- Markdown: GitHub-flavored.
- Python: black-formatted, 100-column line limit.
- Comments in `SKILL.md` examples are in Russian; comments in `examples/` may be in either language.

## License

By contributing, you agree your code is released under the [MIT License](LICENSE) of this repository.
