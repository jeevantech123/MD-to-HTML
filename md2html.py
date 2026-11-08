"""md2html: convert a Markdown file into a complete HTML page.

Usage:
    python3 md2html.py INPUT.md [-o OUTPUT.html]

Standard library only. Supports the Markdown listed in spec.md:
headings, paragraphs, bold, italic, bulleted and numbered lists,
links, inline code, and fenced code blocks.
"""

import argparse
import html
import os
import re
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Line patterns (block level)
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BULLET_RE = re.compile(r"^[-*]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\d+\.\s+(.*)$")
FENCE_RE = re.compile(r"^```")

# ---------------------------------------------------------------------------
# Inline patterns
# ---------------------------------------------------------------------------

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"\*(.+?)\*")


def escape(text):
    """Escape <, > and & so they show as text in the browser."""
    return html.escape(text, quote=False)


def format_emphasis(text):
    """Turn **bold** and *italic* into <strong> and <em>. Text is already escaped."""
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    return ITALIC_RE.sub(r"<em>\1</em>", text)


def format_links_and_emphasis(text):
    """Convert links, then bold/italic, without touching characters inside URLs."""
    parts = []
    last = 0
    for match in LINK_RE.finditer(text):
        parts.append(format_emphasis(text[last:match.start()]))
        label = format_emphasis(match.group(1))
        url = match.group(2).replace('"', "&quot;")
        parts.append(f'<a href="{url}">{label}</a>')
        last = match.end()
    parts.append(format_emphasis(text[last:]))
    return "".join(parts)


def convert_inline(text):
    """Convert inline Markdown in one piece of text to HTML.

    Code spans are split out first so that nothing inside them is converted.
    """
    parts = []
    last = 0
    for match in CODE_SPAN_RE.finditer(text):
        parts.append(format_links_and_emphasis(escape(text[last:match.start()])))
        parts.append(f"<code>{escape(match.group(1))}</code>")
        last = match.end()
    parts.append(format_links_and_emphasis(escape(text[last:])))
    return "".join(parts)


# ---------------------------------------------------------------------------
# Block-level conversion
# ---------------------------------------------------------------------------


def list_item(line):
    """Return (list_tag, item_text) if the line is a list item, else None."""
    match = BULLET_RE.match(line)
    if match:
        return "ul", match.group(1)
    match = NUMBERED_RE.match(line)
    if match:
        return "ol", match.group(1)
    return None


def starts_new_block(line):
    """True if the line starts something other than a paragraph."""
    return bool(
        not line.strip()
        or HEADING_RE.match(line)
        or FENCE_RE.match(line)
        or list_item(line)
    )


def read_code_block(lines, i):
    """Read a fenced code block starting at the opening fence lines[i].

    Returns (html, next_index). An unclosed fence runs to the end of the file.
    """
    i += 1
    body = []
    while i < len(lines) and not FENCE_RE.match(lines[i]):
        body.append(escape(lines[i]))
        i += 1
    i += 1  # skip the closing fence (harmless if we hit the end)
    code = "\n".join(body)
    return f"<pre><code>{code}</code></pre>", i


def read_list(lines, i):
    """Read consecutive list items of the same kind starting at lines[i]."""
    tag, _ = list_item(lines[i])
    items = []
    while i < len(lines):
        item = list_item(lines[i])
        if not item or item[0] != tag:
            break
        items.append(f"  <li>{convert_inline(item[1].strip())}</li>")
        i += 1
    return "\n".join([f"<{tag}>", *items, f"</{tag}>"]), i


def read_paragraph(lines, i):
    """Read lines of text until a blank line or another kind of block."""
    text = [lines[i].strip()]
    i += 1
    while i < len(lines) and not starts_new_block(lines[i]):
        text.append(lines[i].strip())
        i += 1
    joined = "\n".join(text)
    return f"<p>{convert_inline(joined)}</p>", i


def convert_markdown(markdown):
    """Convert a whole Markdown document to the HTML that goes inside <body>."""
    lines = markdown.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{convert_inline(heading.group(2))}</h{level}>")
            i += 1
        elif FENCE_RE.match(line):
            block, i = read_code_block(lines, i)
            blocks.append(block)
        elif list_item(line):
            block, i = read_list(lines, i)
            blocks.append(block)
        else:
            block, i = read_paragraph(lines, i)
            blocks.append(block)
    return "\n".join(blocks)


HEADING_HTML_RE = re.compile(r"<h[1-6]>(.*?)</h[1-6]>")
TAG_RE = re.compile(r"<[^>]+>")


def page_title(body, fallback):
    """Text of the first non-empty heading in the converted body, else fallback.

    Searching the HTML (not the Markdown) means a "# line" inside a code block
    is never picked, because code is escaped and holds no real tags. The
    result is already escaped, so tags are stripped but entities kept.
    """
    for match in HEADING_HTML_RE.finditer(body):
        text = TAG_RE.sub("", match.group(1)).strip()
        if text:
            return text
    return escape(fallback)


def build_page(body, title):
    """Wrap converted content in a complete HTML page. title must be escaped."""
    return (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{title}</title>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


# ---------------------------------------------------------------------------
# Files and command line
# ---------------------------------------------------------------------------


def default_output_path(input_path):
    """notes.md -> notes.html, in the same folder as the input."""
    return input_path.with_suffix(".html")


def write_atomically(path, text):
    """Write text to path so that a failure never leaves a half-written file.

    The page is written to a temporary file in the same folder and then
    renamed over the target in one step.
    """
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".md2html-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(text)
        os.chmod(tmp_name, 0o644)  # mkstemp makes the file private; use normal permissions
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def fail(message):
    """Print an error to stderr and exit with status 1."""
    print(f"md2html: error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="md2html.py",
        description="Convert a Markdown file into an HTML file.",
    )
    parser.add_argument("input", help="path to the Markdown file")
    parser.add_argument(
        "-o", "--output",
        help="name of the HTML file to write (default: INPUT with .html)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else default_output_path(input_path)

    if not input_path.exists():
        fail(f"input file not found: {input_path}")
    try:
        markdown = input_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read input file {input_path}: {exc}")

    # Guard against overwriting the Markdown source (e.g. INPUT is notes.html).
    if output_path.exists() and output_path.resolve() == input_path.resolve():
        fail(f"output file would overwrite the input file: {output_path}")

    body = convert_markdown(markdown)
    page = build_page(body, title=page_title(body, fallback=input_path.stem))
    try:
        write_atomically(output_path, page)
    except OSError as exc:
        fail(f"cannot write output file {output_path}: {exc}")

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
