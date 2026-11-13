# Handoff: MD-to-HTML

Read this first if you're a new session picking up the project.

## Status (2026-11-08)
- **Iteration 1 and changes 01 and 02 are complete.** Everything in `spec.md` is built in `md2html.py`. The page title now comes from the first heading, and blank lines between list items no longer split the list.
- **73 tests pass:** `python3 -m unittest discover -s tests -v` (on this Windows machine, use `python`; see the environment notes below).
- Nothing is in progress.

## Read these, in this order
1. `CLAUDE.md`: the rules. Standard library only, one file, commit after major changes, test after each change, and **do not edit `problem.md`**.
2. `problem.md`: the requirements, R1 to R8.
3. `spec.md`: what to build. If the spec and the code disagree, **ask the user before changing either**.
4. `decision.md`: why things are the way they are (D1 to D18). Later records replace earlier ones (D15 replaces D8, D18 amends D6).

## Files
| File | Purpose |
|---|---|
| `md2html.py` | The whole program |
| `tests/test_v1_initial.py` | Tests for iteration 1, grouped by requirement |
| `tests/test_change_01_title_from_heading.py` | Change 01: the title comes from the first heading |
| `tests/test_change_02_merge_lists.py` | Change 02: blank lines between items keep one list |
| `examples/sample.md` | Sample input for manual checks and the end-to-end test |
| `README.md` | What the program does, how to run it, how to test it |
| `decision.md` | Decision records |
| `HANDOFF.md` | This file |

## How `md2html.py` works
- `main()` parses the arguments, checks that the input exists and can be read, refuses to overwrite the input, then builds the page and calls `write_atomically()`.
- `convert_markdown()` walks the lines once. Each line is checked in this order: blank, heading (`HEADING_RE`), fence (`read_code_block`), list (`read_list`), paragraph (`read_paragraph`).
- `read_list()` looks past blank lines. If the next non-blank line is an item of the same kind, the list continues (D18).
- `page_title()` takes the first non-empty `<hN>` from the converted body, with tags stripped. If there's none, it uses the input file name (D15).
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
- Resolved 2026-11-08: the title comes from the first heading (D15), spaced-out lists merge (D18), and overwrite protection stays (D16).
- `problem.md` and `spec.md` contain backslash escapes (`\#`, `\*\*bold\*\*`) that look like copy-paste artifacts. They weren't edited, per the rules.

## Change log
| # | Date | Change | Tests |
|---|---|---|---|
| 1 | 2026-11-08 | Initial build of everything in spec.md | `tests/test_v1_initial.py` (45) |
| 2 | 2026-11-08 | Change 01: `<title>` comes from the first heading, falling back to the file name | `tests/test_change_01_title_from_heading.py` (14) |
| 3 | 2026-11-08 | Change 02: blank lines between list items of the same kind keep one list | `tests/test_change_02_merge_lists.py` (14) |
