#!/usr/bin/env python3
"""
Check that key strings, fixture names, and assertions in SKILL.md match the
runnable copies under examples/. This prevents the documentation from
silently drifting away from code that actually passes CI.

Failure mode this guards against: a handler reply string is changed in
SKILL.md but the corresponding line in examples/handlers/start.py is
forgotten. CI then keeps passing on examples/ while users copying from
SKILL.md hit assertion failures.

Strategy: maintain a small list of (filename, must-contain) tuples. If
SKILL.md contains a substring, examples/ must contain the same substring,
and vice versa.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_MD = REPO / "skills" / "testing-aiogram-bots" / "SKILL.md"
EXAMPLES = REPO / "examples"

# (label, snippet_that_must_appear_in_BOTH_files, [paths_to_search_for_examples])
PAIRS = [
    ("greeting reply",
     '"Hello! I\'m a fitness bot."',
     [EXAMPLES / "handlers" / "start.py"]),
    ("greeting assertion",
     '"Hello" in sent.text',
     [EXAMPLES / "tests" / "test_start.py"]),
    ("router-singleton workaround",
     "router._parent_router = None",
     [EXAMPLES / "tests" / "conftest.py"]),
    ("make_message_update fixture",
     "def make_message_update():",
     [EXAMPLES / "tests" / "conftest.py"]),
    ("make_callback_update fixture",
     "def make_callback_update():",
     [EXAMPLES / "tests" / "conftest.py"]),
    ("stub_message fixture",
     "def stub_message():",
     [EXAMPLES / "tests" / "conftest.py"]),
    ("FSM Onboarding waiting_height state",
     "waiting_height = State()",
     [EXAMPLES / "handlers" / "start.py"]),
    ("middleware safe user lookup",
     'data.get("event_from_user")',
     [EXAMPLES / "middlewares" / "auth.py"]),
    ("FSM assertion uses .state",
     "Onboarding.waiting_height.state",
     [EXAMPLES / "tests" / "test_fsm.py"]),
    ("MockedBot import",
     "from tests.mocked_bot import MockedBot",
     [EXAMPLES / "tests" / "conftest.py"]),
]


def main() -> int:
    skill_md = SKILL_MD.read_text(encoding="utf-8")
    errors: list[str] = []

    for label, snippet, example_paths in PAIRS:
        if snippet not in skill_md:
            errors.append(f"[{label}] SKILL.md is missing the documented snippet:\n  {snippet!r}")
            continue
        for path in example_paths:
            if not path.exists():
                errors.append(f"[{label}] expected example file does not exist: {path}")
                continue
            if snippet not in path.read_text(encoding="utf-8"):
                rel = path.relative_to(REPO)
                errors.append(
                    f"[{label}] {rel} is missing a snippet that SKILL.md documents:\n  {snippet!r}"
                )

    if errors:
        print("::error::SKILL.md ↔ examples/ drift detected:\n")
        for e in errors:
            print(" -", e)
        print(
            "\nFix: update either SKILL.md or the example file so they match,"
            " then update this script if the documented behavior intentionally changed."
        )
        return 1

    print(f"OK: {len(PAIRS)} doc/example pairs in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
