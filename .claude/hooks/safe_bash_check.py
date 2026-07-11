#!/usr/bin/env python3
"""
Auto-allow bash commands so Claude Code stops prompting for the routine ones.

Two tiers:
  1. Read-only / harmless commands,
     allowed anywhere (any project, any branch).
  2. OpenLieroX dev commands,
     allowed only when the cwd is inside the OLX repo.
     Non-destructive OLX commands (build, test, run, read-only git/gh)
     are allowed on any branch;
     history/outbound writes (git commit/push/checkout, gh pr, ...)
     are allowed only when the current branch is not master/main --
     i.e. when we are on an own working branch, never on the protected trunk.

Compound commands are split on &&, ;, | and every segment must pass.
Prints a PreToolUse "allow" decision if all segments pass;
prints nothing (falls through to normal permission handling) otherwise.
"""
from __future__ import annotations
import json, sys, re, os, subprocess


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


SAFE = [
    r"^cd\b",
    # git read-only subcommands
    r"^git\s+(?:-\S+(?:\s+\S+)?\s+)*(?:status|log|diff|show|branch|remote|describe|rev-parse|ls-files|ls-tree|stash|tag|blame|grep|shortlog|reflog|for-each-ref|cat-file|config)\b",
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

# OpenLieroX dev commands that are non-destructive: safe on any branch, so long
# as the cwd is inside the OLX repo.  Build, test, run, and local-only git/gh.
OLX_SAFE = [
    r"^cmake\b",
    r"^ninja\b",
    r"^make\b",
    r"^ctest\b",
    r"^meson\b",
    r"^chmod\b",
    r"^mkdir\b",
    r"^cp\b",
    r"^mv\b",
    r"^ln\b",
    r"^touch\b",
    r"^patchelf\b",
    r"^install_name_tool\b",
    r"^dylibbundler\b",
    r"^sdl2-config\b",
    r"^pkg-config\b",
    r"^bash\s+-n\b",
    r"^brew\s+(?:list|--prefix|info)\b",
    # OLX build products and headless harness (relative or worktree-absolute).
    # openlierox is the game; olx_tests is the unit-test binary.
    r"^(?:\S*/)?build[\w./-]*/bin/(?:openlierox|olx_tests)\b",
    r"^(?:\./)?tests/headless/\S+\.sh\b",
    r"^(?:\S*/)?tests/headless/\S+\.sh\b",
    r"^(?:\S*/)?pytest\b",
    # local-only git (no history rewrite, nothing leaves the machine).
    # Tolerate leading global options, valued (-C <dir>, -c k=v)
    # or bare (--no-pager, --paginate), like the read matcher,
    # so cross-worktree ``git -C <path> restore`` etc. auto-approve too.
    r"^git\s+(?:-\S+(?:\s+\S+)?\s+)*(?:fetch|add|stash|restore|merge-base|worktree)\b",
    # gh read paths
    r"^gh\s+(?:issue|run|api|search|repo|auth\s+status|release\s+view|release\s+list)\b",
]

# OpenLieroX git/gh writes: allowed only on an own branch (never master/main).
OLX_WRITE = [
    # Tolerate leading global options, valued (-C <dir>, -c k=v)
    # or bare (--no-pager), like the read matcher,
    # so cross-worktree ``git -C <path> commit/apply/checkout`` auto-approve too.
    # The branch gate below uses the -C target's branch, so master stays protected.
    r"^git\s+(?:-\S+(?:\s+\S+)?\s+)*(?:commit|push|checkout|switch|merge|rebase|reset|cherry-pick|branch|tag|rm|mv|apply|clean|pull)\b",
    r"^gh\s+(?:pr|release)\b",
]

PROTECTED_BRANCHES = {"master", "main", "HEAD"}


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


def strip_env(segment: str) -> str:
    """Drop a leading ``env`` and any ``WORD=VALUE`` assignment prefixes."""
    s = segment.strip()
    m = re.match(r"^env\s+", s)
    if m:
        s = s[m.end():]
    while True:
        m = re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", s)
        if not m:
            break
        s = s[m.end():]
    return s


def strip_script(segment: str) -> str:
    """Drop a leading ``script [flags] /dev/null `` pty wrapper, leaving the run command.

    ``script -q /dev/null <cmd>`` just runs <cmd> on a pty (to exercise the
    interactive stdin path); the safety is entirely that of <cmd>, so peel the
    wrapper and let the inner command be judged on its own.
    """
    s = segment.strip()
    m = re.match(r"^script\s+(?:-\S+\s+)*/dev/null\s+", s)
    return s[m.end():] if m else s


def unwrap(segment: str) -> str:
    """Peel ``env``/``WORD=VALUE`` and ``script .. /dev/null`` wrappers until stable."""
    s = segment.strip()
    while True:
        stripped = strip_script(strip_env(s))
        if stripped == s:
            return s
        s = stripped


def in_olx(cwd: str) -> bool:
    """True when the working directory is inside the OpenLieroX repo (or a worktree)."""
    return "/Programmierung/openlierox" in (cwd or "")


def git_c_target(segment: str) -> str | None:
    """The directory of a ``git -C <dir>`` command, else None.

    A ``git -C <dir>`` command acts on <dir>, not the shell's cwd,
    so its OLX-ness and branch must be judged there.
    """
    s = strip_env(segment)
    if not re.match(r"^git\b", s):
        return None
    m = re.search(r"(?:^|\s)-C\s+(\S+)", s)
    return m.group(1).strip("'\"") if m else None


def git_branch(cwd: str) -> str | None:
    """Current branch name, or None if it can't be determined (treated as protected)."""
    r = subprocess.run(
        ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def is_olx_dev_safe(segment: str, branch: str | None) -> bool:
    """Whether an OLX dev command may auto-run given the current branch."""
    s = unwrap(segment)
    if is_safe(s):
        return True
    if not s:
        return True
    if any(re.match(p, s) for p in OLX_SAFE):
        return True
    on_own_branch = branch is not None and branch not in PROTECTED_BRANCHES
    if on_own_branch and any(re.match(p, s) for p in OLX_WRITE):
        return True
    return False


def decide(cmd: str, cwd: str) -> bool:
    """Return True if every segment of ``cmd`` may be auto-allowed."""
    parts = split_shell(cmd)
    if all(is_safe(p) for p in parts):
        return True
    # Judge each segment against the repo it acts on: a ``git -C <dir>``
    # command targets <dir>, everything else targets the shell's cwd.
    for p in parts:
        target = git_c_target(p) or cwd
        if not in_olx(target):
            return False
        if not is_olx_dev_safe(p, git_branch(target)):
            return False
    return True


def main() -> None:
    data = json.load(sys.stdin)
    cmd = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()
    if decide(cmd, cwd):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        }))


if __name__ == "__main__":
    main()
