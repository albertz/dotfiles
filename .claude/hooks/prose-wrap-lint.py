#!/usr/bin/env python3
"""PostToolUse linter for the semantic-line-break rule.

Flags prose (comments, docstrings, Markdown) in freshly written text
that looks wrapped to a fixed column
instead of broken at clause boundaries.
It reads the hook JSON on stdin,
lints only the text just written (Edit new_string / Write content),
and emits additionalContext back to the model when it finds something.

Heuristic: a run of three or more consecutive prose lines
whose non-last lines are all "full" (a straight, high right edge)
is width-wrapped; clause-wrapped prose has a ragged edge,
so a short line lands in the middle of the run.
It catches the obvious paragraphs, not every subtlety.
"""
import json
import re
import sys

FULL = 64   # a "full" prose line ends at least this many columns in
PEAK = 72   # ... and at least one non-last line reaches here (a real near-wrap edge)

_MARKER = re.compile(r"^(//+|#+|\*+|--+|;;+)\s?")


def _is_prose(line):
    s = line.strip()
    m = _MARKER.match(s)
    if m:
        s = s[m.end():].strip()
    if len(s) < 24:
        return False
    if len(re.findall(r"[A-Za-z][A-Za-z'-]+", s)) < 5:
        return False
    codey = sum(c in "{}()[]<>;=|&\\" for c in s)
    letters = sum(c.isalpha() or c == " " for c in s)
    return codey <= 2 and letters >= 0.7 * len(s)


def _findings(text):
    lines = text.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        if not _is_prose(lines[i]):
            i += 1
            continue
        j = i
        while j < n and _is_prose(lines[j]):
            j += 1
        run = lines[i:j]
        head = run[:-1]  # all but the (possibly short) last line
        cols = [len(ln.rstrip()) for ln in head]
        if len(head) >= 2 and all(c >= FULL for c in cols) and max(cols) >= PEAK:
            out.append(run)
        i = j
    return out


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    ti = data.get("tool_input") or {}
    text = ti.get("new_string") or ti.get("content")
    if not isinstance(text, str):
        return
    runs = _findings(text)
    if not runs:
        return
    msg = [
        "Prose you just wrote looks wrapped to a fixed width "
        "(full lines with a straight right edge), not broken at clause "
        "boundaries. Rewrap it one clause per line, ragged right, per the "
        "semantic-line-break rule. Offending run(s):"
    ]
    for run in runs:
        for ln in run:
            msg.append("  | " + ln.rstrip())
        msg.append("")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "\n".join(msg).rstrip()}}))


if __name__ == "__main__":
    main()
