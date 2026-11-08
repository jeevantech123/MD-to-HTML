# MD-to-HTML

A very simple command-line program that converts a Markdown file into a complete HTML page.
It is one Python 3 file (`md2html.py`) that uses only the standard library: no installs, no network, no accounts.

## What it converts

| Markdown | HTML |
|---|---|
| `# Heading` to `###### Heading` | `<h1>` to `<h6>` |
| Lines of text separated by blank lines | `<p>` |
| `**bold**` and `*italic*` | `<strong>` and `<em>` |
| `- item` or `* item` | `<ul>` with `<li>` |
| `1. item` | `<ol>` with `<li>` |
| `[text](url)` | `<a href="url">text</a>` |
| `` `code` `` | `<code>` |
| Fenced block with three backticks | `<pre><code>` |

`<`, `>` and `&` in your text are escaped so they show as text in the browser, and nothing inside code is converted.

## Run it

```
python3 md2html.py INPUT.md                  # writes INPUT.html next to the input
python3 md2html.py INPUT.md -o OUTPUT.html   # writes OUTPUT.html
```

On Windows, if `python3` is not set up, use `python` instead (for example, `python md2html.py notes.md`).

Try it on the included sample:

```
python3 md2html.py examples/sample.md
```

If the input file is missing or unreadable, or the output can't be written, the program prints an error to stderr, exits with status 1, and leaves no output file behind.

## Run the tests

All tests, in one command (run it from the project folder):

```
python3 -m unittest discover -s tests -v
```

Only the first-iteration tests:

```
python3 -m unittest tests.test_v1_initial -v
```

The tests use only Python's built-in `unittest`, so there's nothing to install. Each later change to the project gets its own `tests/test_change_NN_<name>.py` file, and the "all tests" command above runs those too.
