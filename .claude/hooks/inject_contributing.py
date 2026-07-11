from __future__ import annotations

# SessionStart hook: auto-load the OpenLieroX CONTRIBUTING.md into context,
# because this harness does not expand the @CONTRIBUTING.md import in CLAUDE.md.
# Gated to the OLX repo by a marker in the file,
# so it stays a no-op in other projects.
# Runs under system python3 (3.9); keep it dependency-free.

import json
import os
import re
import subprocess
import sys

MARKER = "Contributing to OpenLieroX"


def project_dir(data: dict) -> str:
    """Session project root: the worktree for worktree sessions, else the repo."""
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def harness_branch(cwd: str) -> str:
    """Current branch if it is still the harness default (``claude/...``), else ""."""
    r = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    branch = r.stdout.strip() if r.returncode == 0 else ""
    return branch if branch.startswith("claude/") else ""


def main() -> None:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}

    path = os.path.join(project_dir(data), "CONTRIBUTING.md")
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as f:
        text = f.read()
    if MARKER not in text:  # not the OLX repo; leave other projects untouched
        return

    context = (
        "Auto-loaded CONTRIBUTING.md (the binding contributor rules for this repo; "
        "follow it without needing a reminder):\n\n" + text
    )

    branch = harness_branch(project_dir(data))
    if branch:
        context = (
            "ACTION REQUIRED before you start: you are on the harness default "
            "branch '" + branch + "'. Rename it now to a short descriptive name "
            "carrying the issue number, e.g.\n"
            "  git branch -m fix-<issue>-<slug>\n"
            "(a push of a 'claude/...' branch is blocked until you do). "
            "Then proceed.\n\n" + context
        )
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }, sys.stdout)


if __name__ == "__main__":
    main()
