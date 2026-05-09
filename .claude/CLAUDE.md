Current default Python interpreter: `~/.local-py313/bin/python`

No need to ask for confirmation to execute some Python scripts, demos, test cases that you worked on.

Never add generic `except Exception: ...` error handling (except maybe in the root loop).
Avoid `try: ... except AttributeError: ...`. Check `hasattr` instead, or better even type checks.
Similarly, avoid `try: ... except ValueError: ...`. Do type or logic checks.
Basically, almost always try to avoid `try: ... except ...: ...` if possible.

Public Python functions and classes should have typing and doc strings.

Follow similar code style as remaining project.

If there are test cases, make sure they pass (or if too many, those that are relevant for the things that were changed).

Follow test-driven development: If sth does not work, write a test case, find individual issues, write simpler test cases, fix those, iterate.

Have some timeout for tests, so that you don't wait too long.
