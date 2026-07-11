#!/usr/bin/env python3
"""PreToolUse(Bash) guard: don't let an agent default branch be pushed.

The Claude Code harness creates worktree branches named ``claude/<slug>-<hash>``.
Good practice in any project is a short descriptive branch name
(for a bug fix, one carrying the issue number),
chosen before the first push -- not the throwaway harness name.
A passive reminder proved easy to skip,
so this blocks the push outright until the branch is renamed.
Applies to every project, not just one.

Runs under system python3 (3.9); keep it dependency-free.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

# The harness default; a real work branch never starts with this.
HARNESS_BRANCH = re.compile(r"^claude/")

# A `git [env...] [-C dir] [-c k=v] push ...` segment.
PUSH_SEGMENT = re.compile(
    r"^(?:env\s+)?(?:[A-Za-z_]\w*=\S*\s+)*"
    r"git\s+(?:-\S+\s+\S+\s+)*push\b"
)


def git_c_target(segment: str) -> str | None:
    """Directory of a ``git -C <dir>`` command, else None."""
    m = re.search(r"(?:^|\s)-C\s+(\S+)", segment)
    return m.group(1).strip("'\"") if m else None


def current_branch(cwd: str) -> str:
    r = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def push_segments(cmd: str):
    """Yield (segment, target_dir) for each git-push segment in the command."""
    for seg in re.split(r"&&|\|\||;|\|", cmd):
        s = seg.strip()
        if PUSH_SEGMENT.match(s):
            yield s, git_c_target(s)


def main() -> None:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    cmd = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()

    for seg, target in push_segments(cmd):
        branch = current_branch(target or cwd)
        if HARNESS_BRANCH.match(branch):
            reason = (
                "Refusing to push the harness default branch '%s'. "
                "Rename it to a short descriptive name first "
                "(for a bug fix, carry the issue number), e.g.\n"
                "  git branch -m fix-<issue>-<slug>\n"
                "then push the renamed branch." % branch
            )
            json.dump({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }, sys.stdout)
            return


if __name__ == "__main__":
    main()
