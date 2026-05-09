#!/usr/bin/env python3
"""
Auto-allow bash commands that are composed entirely of safe read-only operations.
Splits compound commands on &&, ;, | and checks each segment against an allowlist.
Prints {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
if safe; prints nothing to fall through to normal permission handling otherwise.
"""
import json, sys, re

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")


def split_shell(cmd: str) -> list[str]:
    """Split on &&, |, ; while respecting single/double-quoted strings and heredocs."""
    parts, current = [], []
    in_single = in_double = False
    i = 0
    while i < len(cmd):
        c = cmd[i]
        # Heredoc (<<word or <<'word'): everything after << is the delimiter + body;
        # stop splitting and absorb the rest into the current segment.
        if not in_single and not in_double and cmd[i:i+2] == "<<" and cmd[i:i+3] != "<<<":
            current.extend(cmd[i:])
            break
        if c == "'" and not in_double:
            in_single = not in_single
            current.append(c)
        elif c == '"' and not in_single:
            in_double = not in_double
            current.append(c)
        elif not in_single and not in_double:
            if cmd[i:i+2] == "&&":
                parts.append("".join(current)); current = []; i += 2; continue
            elif c == "|" and cmd[i:i+2] != "||" and (i == 0 or cmd[i-1] != "\\"):
                parts.append("".join(current)); current = []
            elif c == ";" and cmd[max(0,i-2):i] != "2>":
                parts.append("".join(current)); current = []
            else:
                current.append(c)
        else:
            current.append(c)
        i += 1
    parts.append("".join(current))
    return parts


parts = split_shell(cmd)

SAFE = [
    r"^cd\b",
    # git read-only subcommands
    r"^git\s+(?:status|log|diff|show|branch|remote|describe|rev-parse|ls-files|ls-tree|stash|tag|blame|grep|shortlog|reflog|for-each-ref|cat-file|config)\b",
    # sed without -i (read/parse only)
    r"^sed\s+(?!-i\b)",
    # common read-only unix tools
    r"^head\b",
    r"^tail\b",
    r"^echo\b",
    r"^printf\b",
    r"^grep\b",
    r"^egrep\b",
    r"^find\b",
    r"^ls\b",
    r"^wc\b",
    r"^sort\b",
    r"^uniq\b",
    r"^awk\b",
    r"^cat\b",
    r"^true\b",
    r"^false\b",
    r"^python3\b",
    r"^python\b",
]


def is_safe(segment: str) -> bool:
    segment = segment.strip()
    return not segment or any(re.match(p, segment) for p in SAFE)


if all(is_safe(p) for p in parts):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }))
