"""Tests for the first iteration of md2html (everything in spec.md).

Run just this file:   python -m unittest tests.test_v1_initial -v
Run every test:       python -m unittest discover -s tests -v
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import md2html  # noqa: E402

SCRIPT = ROOT / "md2html.py"


def convert(markdown):
    """Body HTML for a Markdown string."""
    return md2html.convert_markdown(markdown)


def run_cli(*args, cwd=None):
    """Run md2html.py as a real command and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=cwd,
    )


class TestHeadings(unittest.TestCase):  # R4
    def test_all_six_levels(self):
        for level in range(1, 7):
            md = "#" * level + " Title"
            self.assertEqual(convert(md), f"<h{level}>Title</h{level}>")

    def test_seven_hashes_is_not_a_heading(self):
        self.assertEqual(convert("####### Title"), "<p>####### Title</p>")

    def test_hash_without_space_is_not_a_heading(self):
        self.assertEqual(convert("#tag"), "<p>#tag</p>")

    def test_heading_with_inline_formatting(self):
        self.assertEqual(convert("## A **big** deal"),
                         "<h2>A <strong>big</strong> deal</h2>")


class TestParagraphs(unittest.TestCase):  # R5
    def test_single_paragraph(self):
        self.assertEqual(convert("Hello world."), "<p>Hello world.</p>")

    def test_blank_line_separates_paragraphs(self):
        self.assertEqual(convert("One.\n\nTwo."), "<p>One.</p>\n<p>Two.</p>")

    def test_consecutive_lines_join_one_paragraph(self):
        self.assertEqual(convert("Line one\nline two"), "<p>Line one\nline two</p>")

    def test_heading_ends_paragraph(self):
        self.assertEqual(convert("Text\n# Head"), "<p>Text</p>\n<h1>Head</h1>")

    def test_empty_document(self):
        self.assertEqual(convert(""), "")


class TestEmphasis(unittest.TestCase):  # R6
    def test_bold(self):
        self.assertEqual(convert("**hi**"), "<p><strong>hi</strong></p>")

    def test_italic(self):
        self.assertEqual(convert("*hi*"), "<p><em>hi</em></p>")

    def test_bold_and_italic_in_one_line(self):
        self.assertEqual(convert("a **b** c *d* e"),
                         "<p>a <strong>b</strong> c <em>d</em> e</p>")

    def test_lone_star_is_left_alone(self):
        self.assertEqual(convert("2 * 3"), "<p>2 * 3</p>")


class TestLists(unittest.TestCase):  # R7
    def test_dash_bullets(self):
        self.assertEqual(convert("- a\n- b"),
                         "<ul>\n  <li>a</li>\n  <li>b</li>\n</ul>")

    def test_star_bullets(self):
        self.assertEqual(convert("* a\n* b"),
                         "<ul>\n  <li>a</li>\n  <li>b</li>\n</ul>")

    def test_numbered(self):
        self.assertEqual(convert("1. a\n2. b"),
                         "<ol>\n  <li>a</li>\n  <li>b</li>\n</ol>")

    def test_switching_kind_starts_new_list(self):
        self.assertEqual(convert("- a\n1. b"),
                         "<ul>\n  <li>a</li>\n</ul>\n<ol>\n  <li>b</li>\n</ol>")

    def test_list_item_inline_formatting(self):
        self.assertEqual(convert("- **x** and [y](z)"),
                         '<ul>\n  <li><strong>x</strong> and <a href="z">y</a></li>\n</ul>')

    def test_star_bullet_is_not_italic(self):
        self.assertIn("<ul>", convert("* item"))


class TestLinks(unittest.TestCase):  # R8
    def test_link(self):
        self.assertEqual(convert("[DePaul](https://depaul.edu)"),
                         '<p><a href="https://depaul.edu">DePaul</a></p>')

    def test_link_in_sentence_with_bold_label(self):
        self.assertEqual(convert("See [**this**](a.html) now"),
                         '<p>See <a href="a.html"><strong>this</strong></a> now</p>')

    def test_ampersand_in_url_is_escaped(self):
        self.assertIn('href="x?a=1&amp;b=2"', convert("[q](x?a=1&b=2)"))

    def test_stars_in_url_are_not_emphasis(self):
        self.assertIn('href="a*b*c"', convert("[t](a*b*c)"))


class TestCode(unittest.TestCase):
    def test_inline_code(self):
        self.assertEqual(convert("use `ls -la` here"),
                         "<p>use <code>ls -la</code> here</p>")

    def test_nothing_converted_inside_inline_code(self):
        self.assertEqual(convert("`**x** [a](b) <i>`"),
                         "<p><code>**x** [a](b) &lt;i&gt;</code></p>")

    def test_fenced_block(self):
        self.assertEqual(convert("```\nx = 1\ny = 2\n```"),
                         "<pre><code>x = 1\ny = 2</code></pre>")

    def test_fenced_block_with_language_tag(self):
        self.assertEqual(convert("```python\nprint(1)\n```"),
                         "<pre><code>print(1)</code></pre>")

    def test_nothing_converted_inside_fenced_block(self):
        md = "```\n# not heading\n- not list\n**not bold** a < b & c\n```"
        self.assertEqual(
            convert(md),
            "<pre><code># not heading\n- not list\n**not bold** a &lt; b &amp; c</code></pre>",
        )

    def test_unclosed_fence_runs_to_end(self):
        self.assertEqual(convert("```\ncode"), "<pre><code>code</code></pre>")

    def test_fence_ends_paragraph(self):
        self.assertEqual(convert("text\n```\nc\n```"),
                         "<p>text</p>\n<pre><code>c</code></pre>")


class TestEscaping(unittest.TestCase):
    def test_special_characters_escaped(self):
        self.assertEqual(convert("a < b > c & d"),
                         "<p>a &lt; b &gt; c &amp; d</p>")

    def test_raw_html_is_shown_as_text(self):
        self.assertEqual(convert("<script>x</script>"),
                         "<p>&lt;script&gt;x&lt;/script&gt;</p>")


class TestPage(unittest.TestCase):
    def test_complete_page_structure(self):
        page = md2html.build_page("<p>x</p>", title="notes")
        for part in ("<!DOCTYPE html>", "<html>", "<head>", "<title>notes</title>",
                     "</head>", "<body>", "<p>x</p>", "</body>", "</html>"):
            self.assertIn(part, page)
        self.assertLess(page.index("</head>"), page.index("<body>"))


class TestCommandLine(unittest.TestCase):  # R1, R2, R3, errors
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write_md(self, name="notes.md", text="# Hi\n\nSome *text*.\n"):
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_default_output_name(self):  # R1, R2
        md = self.write_md()
        result = run_cli(str(md))
        self.assertEqual(result.returncode, 0, result.stderr)
        out = self.dir / "notes.html"
        self.assertTrue(out.exists())
        html = out.read_text(encoding="utf-8")
        self.assertIn("<h1>Hi</h1>", html)
        # Title comes from the first heading since change 01 (was the file name).
        self.assertIn("<title>Hi</title>", html)

    def test_custom_output_name(self):  # R3
        md = self.write_md()
        out = self.dir / "custom.html"
        result = run_cli(str(md), "-o", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(out.exists())
        self.assertFalse((self.dir / "notes.html").exists())

    def test_long_output_option(self):  # R3
        md = self.write_md()
        out = self.dir / "long.html"
        self.assertEqual(run_cli(str(md), "--output", str(out)).returncode, 0)
        self.assertTrue(out.exists())

    def test_missing_input_file(self):  # R10
        result = run_cli("does_not_exist.md", cwd=self.dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse((self.dir / "does_not_exist.html").exists())
        self.assertEqual(list(self.dir.iterdir()), [])

    def test_missing_input_with_output_option(self):  # R10
        out = self.dir / "out.html"
        result = run_cli(str(self.dir / "nope.md"), "-o", str(out))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(out.exists())

    def test_unreadable_input_directory(self):
        folder = self.dir / "folder.md"
        folder.mkdir()
        result = run_cli(str(folder))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot read", result.stderr)
        self.assertFalse((self.dir / "folder.html").exists())

    def test_input_not_utf8(self):
        bad = self.dir / "bad.md"
        bad.write_bytes(b"\xff\xfe\xfa bad bytes")
        result = run_cli(str(bad))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.dir / "bad.html").exists())

    def test_output_folder_missing_leaves_no_file(self):
        md = self.write_md()
        out = self.dir / "no_such_folder" / "out.html"
        result = run_cli(str(md), "-o", str(out))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot write", result.stderr)
        self.assertFalse(out.exists())

    def test_refuses_to_overwrite_input(self):
        md = self.write_md(name="page.html", text="# Keep me\n")
        result = run_cli(str(md))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(md.read_text(encoding="utf-8"), "# Keep me\n")

    def test_no_temp_files_left_after_success(self):
        md = self.write_md()
        run_cli(str(md))
        names = sorted(p.name for p in self.dir.iterdir())
        self.assertEqual(names, ["notes.html", "notes.md"])

    def test_no_arguments_is_a_usage_error(self):
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage", result.stderr.lower())


class TestSampleFile(unittest.TestCase):
    """End-to-end check on examples/sample.md."""

    def test_sample_converts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample.html"
            result = run_cli(str(ROOT / "examples" / "sample.md"), "-o", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            html = out.read_text(encoding="utf-8")
        for part in ("<h1>Sample Notes</h1>", "<strong>bold</strong>", "<em>italic</em>",
                     "<ul>", "<ol>", '<a href="https://example.com/?a=1&amp;b=2">link</a>',
                     "<code>inline &lt;code&gt; &amp; **stars**</code>",
                     "<pre><code>if a &lt; b", "<h6>Smallest heading</h6>"):
            self.assertIn(part, html)


if __name__ == "__main__":
    unittest.main()
