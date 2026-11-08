# Handoff: MD-to-HTML

Read this first if you're a new session picking up the project.

## Status (2026-11-08)
- **Iteration 1 is complete.** Everything in `spec.md` is built in `md2html.py`.
- **45 tests pass:** `python3 -m unittest discover -s tests -v` (on this Windows machine, use `python`; see the environment notes below).
- Nothing is in progress.

## Read these, in this order
1. `CLAUDE.md`: the rules. Standard library only, one file, commit after major changes, test after each change, and **do not edit `problem.md`**.
2. `problem.md`: the requirements, R1 to R8.
3. `spec.md`: what to build. If the spec and the code disagree, **ask the user before changing either**.
4. `decision.md`: why things are the way they are (D1 to D14).

## Files
| File | Purpose |
|---|---|
| `md2html.py` | The whole program |
| `tests/test_v1_initial.py` | Tests for iteration 1, grouped by requirement |
| `examples/sample.md` | Sample input for manual checks and the end-to-end test |
| `README.md` | What the program does, how to run it, how to test it |
| `decision.md` | Decision records |
| `HANDOFF.md` | This file |

## How `md2html.py` works
- `main()` parses the arguments, checks that the input exists and can be read, refuses to overwrite the input, then builds the page and calls `write_atomically()`.
- `convert_markdown()` walks the lines once. Each line is checked in this order: blank, heading (`HEADING_RE`), fence (`read_code_block`), list (`read_list`), paragraph (`read_paragraph`).
- `convert_inline()` splits out code spans first, escapes the rest, then runs `format_links_and_emphasis()` (links, then bold, then italic).
- `build_page()` wraps the result in a doctype, `<html>`, `<head>` (charset and title), and `<body>`.

## Workflow for each change the user asks for
1. Check that the request fits `spec.md`. If it conflicts with the spec, ask the user first.
2. Make the change in `md2html.py`. Keep functions small and comments short.
3. Add a **new** test file, `tests/test_change_NN_<short_name>.py` (NN = 01, 02, ...), and copy the import header from `test_v1_initial.py`. Don't delete older tests. Update them only if the user has knowingly changed that behavior.
4. Run `python3 md2html.py examples/sample.md`, check the HTML, then delete `examples/sample.html` (it's in `.gitignore` anyway).
5. Run the full suite: `python3 -m unittest discover -s tests -v`.
6. Add a record to `decision.md`, update the README if usage changed, and update the Status and change log in this file.
7. Commit.

## Environment notes
- On this Windows machine, `python3` is only the Windows Store stub and doesn't run. Use `python` (Python 3.14.2 at `C:\Python314`). The code and tests don't care which name runs them, because the tests use `sys.executable`.
- Inside the Bash tool, heredocs turn `\n` inside Python strings into real newlines. Use the Edit tool for code changes.

## Open questions for the user
- `<title>` is the input file name (D8). Should it be the first heading instead?
- `- a`, a blank line, then `- b` produces two lists (D6). Is that acceptable?
- `problem.md` and `spec.md` contain backslash escapes (`\#`, `\*\*bold\*\*`) that look like copy-paste artifacts. They weren't edited, per the rules.

## Change log
| # | Date | Change | Tests |
|---|---|---|---|
| 1 | 2026-11-08 | Initial build of everything in spec.md | `tests/test_v1_initial.py` (45) |
