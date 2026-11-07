\# Spec: MD-to-HTML



A very simple command-line program that converts a Markdown file into an HTML file. It meets the requirements in `problem.md`.



\## How it is built



\- One Python 3 script, `md2html.py`, using only the standard library.

\- The converter reads the file line by line and handles each kind of Markdown in turn. It does not use a Markdown library.



\## How to run



```

python3 md2html.py INPUT.md

python3 md2html.py INPUT.md -o OUTPUT.html

```



\## Behavior



\- The first argument is the path to a Markdown file. 

\- The result is written to an HTML file. Without `-o`, the output has the same name as the input with a `.html` extension (`notes.md` becomes `notes.html`). With `-o`, it uses the name given. 

\- The output is a complete HTML page: `<html>`, `<head>` with a `<title>`, and a `<body>` holding the converted content.



\### Supported Markdown



| Markdown | HTML | Requirement |

|---|---|---|

| `# Heading` up to `###### Heading` | `<h1>` to `<h6>` |

| Lines of text separated by blank lines | `<p>` |

| `\*\*bold\*\*` and `\*italic\*` | `<strong>` and `<em>` |

| `- item` or `\* item` | `<ul>` with `<li>` |

| `1. item` | `<ol>` with `<li>` |

| `\[text](url)` | `<a href="url">text</a>` |

| `` `code` `` | `<code>` |

| Fenced block with three backticks | `<pre><code>` |



\- Characters like `<`, `>`, and `\&` in the text are escaped so they show as text in the browser.

\- Inside code, nothing else is converted.



\### Errors



\- If the input file does not exist or cannot be read, the program prints a clear message to the error output, exits with a non-zero status, and does not create an output file.



