\# CLAUDE.md



\## Project



MD-to-HTML: a very simple command-line program that converts a Markdown file into an HTML file.



\## Read first



\- `problem.md` says who has the problem and lists the requirements

\- `spec.md` says how the program should work. Build what the spec describes.



Do not edit `problem.md`. If the spec and the code disagree, tell me before changing either.



\## Rules



\- Use Python 3 and the standard library only. No pip packages, and no Markdown libraries.

\- Keep the program in one file, `md2html.py`.

\- It must run with one command: `python3 md2html.py INPUT.md \[-o OUTPUT.html]`.

\- No API keys, no login, no paid services, no network calls.

\- Print errors to the error output and exit with a non-zero status. Never leave a half-written output file behind.

\- Keep it simple. Do not add Markdown features that are not in the spec.



\## Code style



\- Small functions with clear names 

\- Short comments where the code is not obvious.



\## Working



\- Make a commit after every major change. After building initial project, commit. If asked to make a major change to a project, do that then commit.

\- After each change, run the program on a sample `.md` file and check the HTML output against the requirements it touches. Also test a missing input file (R10).

