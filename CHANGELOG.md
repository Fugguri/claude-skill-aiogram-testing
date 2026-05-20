# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project follows [Semantic Versioning](https://semver.org/).

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

[0.3.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.3.0
[0.2.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.2.0
[0.1.0]: https://github.com/Fugguri/claude-skill-aiogram-testing/releases/tag/v0.1.0
