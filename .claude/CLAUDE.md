Current default Python interpreter: `~/.local-py313/bin/python`

No need to ask for confirmation to execute some Python scripts, demos, test cases that you worked on.

Have some timeout for tests, so that you don't wait too long. Some tests or scripts might run into infinite loops.

Follow similar code style as in the remaining project.

When writing prose (code comments, docstrings, multi-line strings, commit messages, PR/issue bodies, chat): break lines at clause/sentence boundaries (semantic line breaks), never wrap to a fixed column width -- the right edge must be visibly ragged. Before finalizing any such text, glance at its right edge; if consecutive lines end near the same column you wrapped by width, so rewrap. No em-dashes anywhere (use `--`).

If there are test cases, make sure they pass (or if too many, those that are relevant for the things that were changed).

Follow test-driven development: If sth does not work, write a test case, find individual issues, write simpler test cases, fix those, iterate.
When adding a test, follow the same style as existing tests.
Don't add some file with a generic name like `test_new_fixes.py`. See where tests would fit, in existing files, and otherwise add new files, following the same style as existing ones.

If you see some code is not well structured, or has some issues, you can also fix those, even if they are not directly related to the things that were changed. But try to keep the changes small and focused, and avoid changing too many files at once.

Never add generic `except Exception: ...` error handling (except maybe in the root loop).
Avoid `try: ... except AttributeError: ...`. Check `hasattr` instead, or better even type checks.
Similarly, avoid `try: ... except ValueError: ...`. Do type or logic checks.
Basically, almost always try to avoid `try: ... except ...: ...` if possible.

Public Python functions and classes should have typing and doc strings.
