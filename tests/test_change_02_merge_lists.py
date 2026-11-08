"""Change 02: blank lines between items of the same kind keep one list.

Run just this file:   python -m unittest tests.test_change_02_merge_lists -v
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
    return md2html.convert_markdown(markdown)


UL_AB = "<ul>\n  <li>a</li>\n  <li>b</li>\n</ul>"
OL_AB = "<ol>\n  <li>a</li>\n  <li>b</li>\n</ol>"


class TestMergeLists(unittest.TestCase):
    def test_bullets_separated_by_blank_line_merge(self):
        self.assertEqual(convert("- a\n\n- b"), UL_AB)

    def test_numbered_separated_by_blank_line_merge(self):
        self.assertEqual(convert("1. a\n\n2. b"), OL_AB)

    def test_several_blank_lines_still_merge(self):
        self.assertEqual(convert("- a\n\n\n\n- b"), UL_AB)

    def test_whitespace_only_line_counts_as_blank(self):
        self.assertEqual(convert("- a\n   \n- b"), UL_AB)

    def test_dash_and_star_bullets_merge(self):
        self.assertEqual(convert("- a\n\n* b"), UL_AB)

    def test_mixed_tight_and_spaced_items(self):
        self.assertEqual(convert("- a\n- b\n\n- c"),
                         "<ul>\n  <li>a</li>\n  <li>b</li>\n  <li>c</li>\n</ul>")

    def test_different_kind_after_blank_starts_new_list(self):
        self.assertEqual(convert("- a\n\n1. b"),
                         "<ul>\n  <li>a</li>\n</ul>\n<ol>\n  <li>b</li>\n</ol>")

    def test_paragraph_between_items_splits_list(self):
        self.assertEqual(convert("- a\n\ntext\n\n- b"),
                         "<ul>\n  <li>a</li>\n</ul>\n<p>text</p>\n<ul>\n  <li>b</li>\n</ul>")

    def test_heading_between_items_splits_list(self):
        self.assertEqual(convert("- a\n\n# H\n\n- b"),
                         "<ul>\n  <li>a</li>\n</ul>\n<h1>H</h1>\n<ul>\n  <li>b</li>\n</ul>")

    def test_trailing_blank_lines_after_list(self):
        self.assertEqual(convert("- a\n- b\n\n\n"), UL_AB)

    def test_paragraph_after_list_and_blank(self):
        self.assertEqual(convert("- a\n- b\n\nAfter."), UL_AB + "\n<p>After.</p>")

    def test_line_right_after_item_still_ends_list(self):
        # Continuation lines are not supported (see D6); behaviour unchanged.
        self.assertEqual(convert("- a\ntext"), "<ul>\n  <li>a</li>\n</ul>\n<p>text</p>")


class TestMergeListsEndToEnd(unittest.TestCase):
    def test_spaced_list_in_written_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "todo.md"
            md.write_text("# Todo\n\n1. Buy milk\n\n2. Call **mom**\n\n3. Study\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(md)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = md.with_suffix(".html").read_text(encoding="utf-8")
        self.assertEqual(html.count("<ol>"), 1)
        self.assertEqual(html.count("<li>"), 3)
        self.assertIn("<li>Call <strong>mom</strong></li>", html)

    def test_sample_file_spaced_list_is_one_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s.html"
            subprocess.run([sys.executable, str(SCRIPT), str(ROOT / "examples" / "sample.md"),
                            "-o", str(out)], check=True, capture_output=True)
            html = out.read_text(encoding="utf-8")
        self.assertIn("<ul>\n  <li>Spaced one</li>\n  <li>Spaced two</li>\n</ul>", html)


if __name__ == "__main__":
    unittest.main()
