# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project follows [Semantic Versioning](https://semver.org/).

## [0.5.1] — 2026-05-20

### Added
- **"Where tests live" section** at the top of both `SKILL.md` and `SKILL.ru.md`. Hard rule: all test files (incl. `conftest.py`, `mocked_bot.py`) MUST be placed under `tests/`, never at project root. Includes the required directory layout diagram.
- Common Mistakes table now has a row for "Test files written to project root" with the symptom (`pytest collected 0 items`) and the fix.
- `scripts/check_doc_sync.py` gained an 11th pair: presence of the tests/-directory directive in `SKILL.md` is now linted.

### Changed
- Frontmatter `description` (both files) now explicitly says: "All test files MUST be created under tests/ (never at project root)." This helps the AI route requests like "write a test" to the correct directory from the first turn.

### Why
- Coding agents (including Claude Code in less-careful modes) default to writing `test_*.py` next to whatever file they were editing, which often ends up at the project root. `pytest` with `testpaths = ["tests"]` then silently collects zero tests, and the user thinks the agent did the work. The directive + linted check eliminate that failure mode.

## [0.5.0] — 2026-05-20

### Added
- **aiogram matrix in CI** — `pytest examples/` now runs on the cross product of Python `[3.10, 3.11, 3.12]` × aiogram `[3.13, 3.20, 3.28.2]`. Total: 9 environments. Locally verified all 9 green before pushing.
- **`scripts/check_doc_sync.py`** — lint that pins 10 critical snippets (handler reply strings, fixture names, FSM assertions, middleware safety pattern) between `SKILL.md` and `examples/`. CI fails if either side drifts. This guards against the v0.4.0 → v0.4.1 regression (Russian handler vs English docs) reoccurring.
- New CI job `doc-example-sync` runs the lint above on every push.

### Changed
- CI job `claude plugin validate` no longer uses `continue-on-error: true`. The Node.js setup step is now explicit so `npm install -g @anthropic-ai/claude-code` is reliable. A failed validation now actually fails the build.

### Verified
- Manual install loop reproduced end-to-end:
  - `claude plugin marketplace add Fugguri/claude-skill-aiogram-testing` → marketplace registered as `fugguri-aiogram-testing`
  - `claude plugin install testing-aiogram-bots@fugguri-aiogram-testing` → installed at scope `user`, version `0.5.0` read from manifest
  - `claude plugin list` lists the skill correctly
- All 9 aiogram × Python combos pass locally.
- `claude plugin validate --strict` passes locally.
- `scripts/check_doc_sync.py` reports 10/10 pairs in sync.

## [0.4.2] — 2026-05-20

### Fixed (blocker)
- `plugin.json` moved from `skills/testing-aiogram-bots/plugin.json` to `skills/testing-aiogram-bots/.claude-plugin/plugin.json`. Per [Claude Code plugin spec](https://code.claude.com/docs/en/plugins-reference), the manifest **must** live in `<plugin-root>/.claude-plugin/plugin.json`. With the old location Claude Code did not load it as a manifest — falling back to directory-name and skipping author/repository metadata. `claude plugin validate --strict` now passes.
- Removed `"strict": false` from `marketplace.json` — it was a misuse. `strict: false` only matters when the marketplace entry and `plugin.json` declare overlapping components; ours never did.

### Changed
- CI: replaced fragile "skip first 13 lines" diff with a `--- BEGIN VENDORED CONTENT` sentinel marker in `mocked_bot.py`. Header can now grow/shrink freely without breaking the upstream-drift check.
- CI: added a `Cross-check version sync` step — fails the build if `plugin.json` and `marketplace.json` disagree on version.
- CI: added a `claude plugin validate --strict` job (soft-fail until the CLI is reliably available in Actions runners).
- SKILL.md + SKILL.ru.md Common Mistakes: the router-singleton row now recommends building a fresh `Router()` via a factory **first**, before the `_parent_router = None` workaround. Pokes-private-attributes was the lead recommendation; it shouldn't be.
- SKILL.md + SKILL.ru.md FSM section: added a note that `StatesGroup` must live next to handlers (not inline in tests), or assertions compare two different `State` objects.
- Credits in SKILL.md, SKILL.ru.md, README: `@fugguri` link text → `@Fugguri` (canonical case).
- `.github/ISSUE_TEMPLATE/bug_report.md`: Russian section name (`Порядок очередей в MockedSession`) → English (`Queue ordering in MockedSession`) — matches the EN-primary SKILL.md.

## [0.4.1] — 2026-05-20

### Fixed
- `examples/handlers/start.py`: replies were still in Russian (`"Привет!..."`, `"Сколько ты ростом?"`, `"Подтверждено"`) after the English-primary switch in 0.4.0. Translated to English so docs and runnable examples match.
- `examples/tests/test_start.py`: assertion updated to `"Hello" in sent.text` to match the now-English handler.
- `examples/tests/conftest.py`: Russian comment on the router-singleton workaround translated to English.
- `SKILL.md` middleware example: `data["event_from_user"].id` → `data.get("event_from_user")` with `None`-guard. Original was KeyError-prone for updates without a user (poll, my_chat_member, etc.). The runnable `examples/middlewares/auth.py` already used the safe form; docs now match.
- `SKILL.ru.md`: middleware example mirrored with the same safe `.get()` pattern.

### Changed
- `plugin.json` + `.claude-plugin/marketplace.json`: GitHub URL casing normalized to `Fugguri` (canonical).
- `SKILL.md` + `SKILL.ru.md` Quick Reference: the `callback_query` row now points to the `make_callback_update` fixture instead of a raw `Update(...)` constructor.

## [0.4.0] — 2026-05-20

### Changed
- **`SKILL.md` is now English** (primary). The full Russian text moved to `SKILL.ru.md` (kept in sync).
- README "Language note" updated to describe both files.

### Added
- Cross-link in `SKILL.ru.md` pointing back to the English `SKILL.md` as primary.

## [0.3.0] — 2026-05-20

### Added
- `tests/__init__.py` discussion now scoped to legacy `import_mode=prepend`; modern pytest 8+ (`import_mode=importlib`, default) is covered explicitly.
- Middleware testing mini-example (FSM-aware, scoped to `Dispatcher`-level middleware).
- Explicit ordering rules table for `MockedSession.responses` (LIFO) vs `MockedSession.requests` (FIFO via `list()`, LIFO via `bot.get_request()`).
- `vendor/aiogram-LICENSE` (renamed `AIOGRAM-LICENSE`) shipped alongside `mocked_bot.py`.
- Pin header in `mocked_bot.py` with upstream SHA `ec7da0f6788c11c1c2d9609292de289de67c7f76` and refresh instructions.
- `CHANGELOG.md` (this file).
- `CONTRIBUTING.md` with PR guidance.
- `.github/ISSUE_TEMPLATE/` (bug, feature).
- GitHub Actions CI: runs `pytest` against the runnable examples in `examples/` and validates JSON manifests.
- Runnable copy of the SKILL.md examples under `examples/` so CI proves the documented code actually executes against pinned `aiogram` + `pytest-asyncio` versions.

### Changed
- Unified LIFO terminology in `Common Mistakes` and the callback test comment.
- `make_callback_update` uses `itertools.count()` and includes per-call `message_id` increment.
- `Альтернатива` (AsyncMock) example now imports `cmd_start` explicitly for copy-paste safety.
- Frontmatter `description` mentions callback_query and AI-hallucination guardrails.
- README install command uses correct GitHub case: `Fugguri/claude-skill-aiogram-testing`.

### Fixed
- (carried from 0.2.0) FSM example: `Onboarding.waiting_height` now declared; assertion uses `.state` string.

## [0.2.0] — 2026-05-20

### Added
- `conftest.py` fixtures: `make_message_update`, `make_callback_update`, `stub_message` — remove `Update/Message/Chat/User` boilerplate from tests.
- Callback Query test example.
- Explicit attribution to aiogram maintainers (JrooTJunior, Olegt0rr, MrMrRobat) in both README and SKILL.md.

### Fixed
- Broken FSM example referencing undefined `Onboarding.waiting_height`.

### Changed
- Minimal `/start` test rewritten using new fixtures (30 lines → 5).
- Clarified that `FSMContext.get_state()` returns a string, not a `State` object.

## [0.1.0] — 2026-05-20

### Added
- Initial release.
- `SKILL.md` with TDD workflow, MockedBot setup, FSM testing pattern.
- Vendored `mocked_bot.py` from aiogram `dev-3.x`.
- `plugin.json` and `.claude-plugin/marketplace.json`.
- MIT license.

[0.5.1]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.5.1
[0.5.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.5.0
[0.4.2]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.4.2
[0.4.1]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.4.1
[0.4.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.4.0
[0.3.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.3.0
[0.2.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.2.0
[0.1.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.1.0
