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
    r"^git\s+(?:-\S+\s+\S+\s+)*(?:status|log|diff|show|branch|remote|describe|rev-parse|ls-files|ls-tree|stash|tag|blame|grep|shortlog|reflog|for-each-ref|cat-file|config)\b",
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
    r"^timeout\b",
    r"^true\b",
    r"^false\b",
    r"^(?:\S+/)?python[23]?\b",   # python / python3 / /path/to/python3 / ~/.venv/bin/python
    # Debugger / binary inspection -- read-only with respect to source.
    r"^lldb\b",
    r"^gdb\b",
    r"^nm\b",
    r"^otool\b",
    r"^objdump\b",
    r"^readelf\b",
    r"^file\b",
    r"^strings\b",
    r"^dsymutil\b",
    # Process inspection / control (kill is process-targeted, not files).
    r"^ps\b",
    r"^kill\b",
    r"^pkill\b",
    r"^pgrep\b",
    r"^sleep\b",
    r"^xargs\b",
    # Environment-prefixed commands: ``FOO=bar cmd args``.  Allow the
    # prefix and recurse on the rest.  Simpler: accept any sequence of
    # ``WORD=VALUE`` env assignments followed by any safe command.
    r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)+(?:lldb|gdb|nm|otool|ps|kill|sleep|xargs|head|tail|grep|cat|awk|sed|find|ls|wc|sort|uniq|tr|cut|tee|timeout|true|false|echo|printf|(?:\S+/)?python[23]?)\b",
    # Shell control flow / pure compounds (no destructive subcommands).
    r"^while\b",
    r"^until\b",
    r"^for\b",
    r"^if\b",
    r"^do\b",
    r"^done\b",
    r"^fi\b",
    r"^then\b",
    r"^else\b",
]


def is_safe_rm(segment: str) -> bool:
    """Allow ``rm`` only when every target lives under /tmp or /private/tmp.

    Flags are ignored; every non-flag token must be a literal path under one of
    those roots, with no shell expansion ($ ` ) and no parent traversal (..).
    Anything else falls through to normal permission handling.
    """
    toks = segment.split()
    if not toks or toks[0] != "rm":
        return False
    paths = [t.strip("'\"") for t in toks[1:] if not t.startswith("-")]
    if not paths:
        return False
    for p in paths:
        if any(ch in p for ch in "$`") or ".." in p:
            return False
        if not (p.startswith("/tmp/") or p.startswith("/private/tmp/")):
            return False
    return True


def is_safe(segment: str) -> bool:
    segment = segment.strip()
    if not segment or is_safe_rm(segment):
        return True
    return any(re.match(p, segment) for p in SAFE)


if all(is_safe(p) for p in parts):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }))
