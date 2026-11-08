# Decision Records

Each record says what was decided, why, and what else was considered.
Add new records at the bottom and don't rewrite old ones. If a decision is reversed, add a new record that points back to the old one.

---

## D1. Test with `unittest` from the standard library
- **Date:** 2026-11-08
- **Decision:** Tests use Python's built-in `unittest`. Run them all with `python3 -m unittest discover -s tests -v`.
- **Why:** CLAUDE.md allows only the standard library. `unittest` needs no install, and one command runs everything.
- **Considered:** `pytest` reads better, but it's a pip package.

## D2. One test file per iteration or change
- **Date:** 2026-11-08
- **Decision:** `tests/test_v1_initial.py` covers the first build. Each change the user asks for later gets a new file, `tests/test_change_NN_<short_name>.py`. Older test files stay in place and keep passing.
- **Why:** The user asked for a test after the first build and a test for each change. Separate files let you run one change's tests (`python3 -m unittest tests.test_change_01_x`), and `discover` still runs all of them.

## D3. Block parsing: one pass over the lines
- **Date:** 2026-11-08
- **Decision:** `convert_markdown` walks the lines once. Each line is checked in this order: blank, heading, code fence, list item, paragraph. Each kind of block has a small `read_*` function that returns `(html, next_index)`.
- **Why:** The spec says "reads the file line by line and handles each kind of Markdown in turn". This is the simplest code that does it.

## D4. Inline order: code spans, then escaping, then links, then bold, then italic
- **Date:** 2026-11-08
- **Decision:** Code spans are split out first and only escaped, so nothing inside them is converted. The remaining text is escaped, then links are found, then `**bold**`, then `*italic*`. Bold runs before italic so that `**x**` doesn't turn into nested `<em>`. Link URLs are kept out of bold/italic so `*` in a URL stays as it is.
- **Why:** This meets the spec rules "Inside code, nothing else is converted" and "`<`, `>`, `&` are escaped".
- **Limitation:** `***both***` and nesting bold inside italic aren't handled cleanly. That isn't in the spec.

## D5. Paragraph lines are joined with a newline
- **Date:** 2026-11-08
- **Decision:** Lines that touch each other form one `<p>`, joined with `\n`. The browser shows that newline as a space.
- **Why:** This is the same as standard Markdown and keeps the HTML easy to read.

## D6. List rules
- **Date:** 2026-11-08
- **Decision:** A list is a run of consecutive items of the same kind (`-`/`*` makes `<ul>`, `N.` makes `<ol>`). A blank line, any other line, or a change of kind ends the list. Nested lists and indented continuation lines aren't supported. `1.` items accept any number (`3.` works too), and the numbers in the file are ignored.
- **Why:** Nested lists and continuation lines aren't in the spec. CLAUDE.md says not to add features the spec doesn't list.
- **Known effect:** `- a`, then a blank line, then `- b` produces two separate `<ul>` lists.

## D7. Fenced code details
- **Date:** 2026-11-08
- **Decision:** Any line that starts with three backticks opens or closes a fence. Text after the opening backticks (such as `python`) is ignored. A fence that never closes runs to the end of the file.
- **Why:** This is the simplest behavior, and nothing is lost: the reader still sees all the code.

## D8. Page title is the input file name
- **Date:** 2026-11-08
- **Decision:** `<title>` is the input file name without its extension (`notes.md` gives `notes`).
- **Why:** The spec requires a `<title>` but doesn't say what goes in it. The file name always exists and needs no extra parsing.
- **Considered:** Using the first heading. This could be changed if the user prefers it (see Open Questions in HANDOFF.md).

## D9. Page skeleton includes a doctype and UTF-8 charset
- **Date:** 2026-11-08
- **Decision:** The output starts with `<!DOCTYPE html>` and includes `<meta charset="utf-8">`. Input is read as UTF-8 and output is written as UTF-8.
- **Why:** Without a doctype, browsers use quirks mode. Without the charset, non-ASCII text can show up garbled. Both go beyond the spec's `<html>/<head>/<title>/<body>` without contradicting it.

## D10. No half-written output files (atomic write)
- **Date:** 2026-11-08
- **Decision:** The whole page is built in memory first. It's then written to a temporary file in the target folder and moved into place with `os.replace`. On any error, the temp file is deleted. Input errors are found before anything is written.
- **Why:** CLAUDE.md says: "Never leave a half-written output file behind."

## D11. Errors and exit codes
- **Date:** 2026-11-08
- **Decision:** Errors print `md2html: error: ...` to stderr. Exit code 1 means a missing or unreadable input, input that isn't UTF-8, or output that can't be written. Exit code 2 means a usage error (from `argparse`). Exit code 0 means success, and the program prints `Wrote <path>` to stdout.
- **Why:** The spec and CLAUDE.md require a clear message on stderr and a non-zero exit.

## D12. Refuse to overwrite the input file
- **Date:** 2026-11-08
- **Decision:** If the output path is the same file as the input (for example, the input is `page.html`, or the user passes `-o` with the input's own name), the program exits with an error.
- **Why:** Overwriting the user's source would destroy their work. This is an error check, not a new Markdown feature.

## D13. The `-o` option also accepts `--output`
- **Date:** 2026-11-08
- **Decision:** `argparse` provides `-o` and the long form `--output`.
- **Why:** It costs nothing, and `-o` works exactly as the spec says.

## D14. Requirement "R10" in CLAUDE.md
- **Date:** 2026-11-08
- **Observation:** CLAUDE.md says to test a missing input file "(R10)", but `problem.md` only lists R1 to R8, and the "Requirement" column in the spec table is empty.
- **Decision:** The "Errors" section of the spec is treated as R10, and the missing-file tests are tagged `# R10`. `problem.md` and `spec.md` weren't edited.

## D15. Page title is the first heading (replaces D8)
- **Date:** 2026-11-08
- **Decision:** `<title>` is the text of the first non-empty heading of any level, with inline markup removed (`# A **big** deal` gives `A big deal`). If there's no heading, the title falls back to the input file name without its extension, as in D8.
- **Why:** The user chose this. A heading describes the document better than its file name.
- **How:** `page_title()` searches the *converted* HTML for the first `<hN>` tag. All code is escaped and contains no real tags, so a `# line` inside a code block can never become the title. The heading HTML is already escaped, so removing the tags leaves correctly escaped text.
- **Tests:** `tests/test_change_01_title_from_heading.py`. One v1 test that expected the file name as the title was updated.

## D16. Overwrite protection kept (confirms D12)
- **Date:** 2026-11-08
- **Decision:** The user confirmed that refusing to overwrite the input file stays in.

## D17. CLAUDE.md no longer mentions "R10" (follows up D14)
- **Date:** 2026-11-08
- **Observation:** CLAUDE.md now says "Also test a missing input file" without the "(R10)" label. The `# R10` comments in `tests/test_v1_initial.py` now just mark the spec's "Errors" section. Missing-file tests still run as part of the full test suite.
