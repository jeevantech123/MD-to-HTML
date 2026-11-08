"""Change 01: the page <title> is the first heading, else the file name.

Run just this file:   python -m unittest tests.test_change_01_title_from_heading -v
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


def title_for(markdown, fallback="file"):
    return md2html.page_title(md2html.convert_markdown(markdown), fallback)


class TestPageTitle(unittest.TestCase):
    def test_first_h1(self):
        self.assertEqual(title_for("# My Notes\n\ntext"), "My Notes")

    def test_first_heading_of_any_level(self):
        self.assertEqual(title_for("intro\n\n### Third level\n\n# Later h1"), "Third level")

    def test_first_of_several_headings(self):
        self.assertEqual(title_for("# One\n## Two\n# Three"), "One")

    def test_no_heading_uses_file_name(self):
        self.assertEqual(title_for("just text", fallback="notes"), "notes")

    def test_inline_markdown_is_stripped(self):
        self.assertEqual(title_for("# A **big** [link](x.html) and `code`"),
                         "A big link and code")

    def test_special_characters_are_escaped(self):
        self.assertEqual(title_for("# Tom & Jerry <3"), "Tom &amp; Jerry &lt;3")

    def test_file_name_fallback_is_escaped(self):
        self.assertEqual(title_for("text", fallback="a&b"), "a&amp;b")

    def test_heading_inside_code_block_is_ignored(self):
        self.assertEqual(title_for("```\n# not a title\n```\n\n## Real", fallback="f"), "Real")

    def test_only_code_block_heading_uses_file_name(self):
        self.assertEqual(title_for("```\n# not a title\n```", fallback="f"), "f")

    def test_empty_heading_is_skipped(self):
        self.assertEqual(title_for("# \n\n## Second"), "Second")

    def test_hashtag_line_is_not_a_title(self):
        self.assertEqual(title_for("#tag", fallback="f"), "f")


class TestTitleEndToEnd(unittest.TestCase):
    def run_on(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / name
            md.write_text(text, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(md)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return md.with_suffix(".html").read_text(encoding="utf-8")

    def test_title_from_heading_in_written_file(self):
        html = self.run_on("notes.md", "# Week 1 *Summary*\n\nBody.")
        self.assertIn("<title>Week 1 Summary</title>", html)
        self.assertIn("<h1>Week 1 <em>Summary</em></h1>", html)

    def test_title_falls_back_to_file_name(self):
        html = self.run_on("diary.md", "No headings here.")
        self.assertIn("<title>diary</title>", html)

    def test_sample_file_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s.html"
            subprocess.run([sys.executable, str(SCRIPT), str(ROOT / "examples" / "sample.md"),
                            "-o", str(out)], check=True, capture_output=True)
            self.assertIn("<title>Sample Notes</title>", out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
