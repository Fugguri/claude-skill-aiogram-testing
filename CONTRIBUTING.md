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

CI runs `pytest examples/` against a matrix of Python 3.10/3.11/3.12 × aiogram 3.13/3.20/3.28.2 on every push, plus `claude plugin validate --strict`, plus `scripts/check_doc_sync.py`.

## What we need

- **Better examples.** Edge cases, real-world patterns from your own bots (album messages, inline queries, error handlers, custom storage).
- **Coverage of additional update types.** `make_message_update` and `make_callback_update` exist; factories for `inline_query`, `my_chat_member`, `poll`, etc. are welcome.
- **Russian-side improvements.** `SKILL.md` is the primary (English) source. `SKILL.ru.md` is a 1:1 translation kept in sync. If you update one, update the other. (PRs that update only `SKILL.ru.md` to fix translation bugs are also welcome.)
- **Upstream sync.** When `aiogram/aiogram` updates `tests/mocked_bot.py`, refresh:
  ```bash
  curl -o skills/testing-aiogram-bots/mocked_bot.py \
    https://raw.githubusercontent.com/aiogram/aiogram/dev-3.x/tests/mocked_bot.py
  ```
  Then add back the vendored-pin header (preserve the `--- BEGIN VENDORED CONTENT ---` sentinel), bump `Pinned SHA` and `Date`, bump version in `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, and add a `CHANGELOG.md` entry.
- **Bug reports** with a minimal reproduction (see `.github/ISSUE_TEMPLATE/bug_report.md`).

## PR rules

1. One concern per PR.
2. Bump version in **both** `skills/testing-aiogram-bots/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` if the skill content changes. CI cross-checks they match.
3. Add a `## [Unreleased]` section to `CHANGELOG.md` (or extend it if it already exists). The maintainer will rename it to the release version.
4. If you change snippets in `SKILL.md`, mirror the change in `SKILL.ru.md` and in the matching file under `examples/`. Run `python scripts/check_doc_sync.py` locally — CI runs the same script.
5. Run `pytest examples/` locally; all 5 tests must pass.
6. Run `claude plugin validate skills/testing-aiogram-bots --strict` locally if you touched `plugin.json`, `SKILL.md` frontmatter, or directory layout.
7. Keep AI-hallucination guardrail wording sharp — those are the most-valuable parts.

## Style

- Markdown: GitHub-flavored.
- Python: black-formatted, 100-column line limit.
- Code comments in `SKILL.md`, `SKILL.ru.md`, and `examples/` are written in **English** so the runnable code and the primary documentation match exactly. (Prose in `SKILL.ru.md` is Russian; code blocks inside it are identical to the English version.)

## License

By contributing, you agree your code is released under the [MIT License](LICENSE) of this repository. The vendored `mocked_bot.py` retains its upstream MIT license (see `AIOGRAM-LICENSE`).
