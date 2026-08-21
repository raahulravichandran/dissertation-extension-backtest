"""Render project Markdown docs to PDF (markdown -> HTML -> PDF).

Markdown stays canonical; PDFs are for sharing / for opening on machines where .md
files have no viewer association. Any local images referenced in the Markdown are
embedded as base64 (no path dependency), and a few non-Latin-1 glyphs are mapped to
ASCII so the default PDF fonts render cleanly.

Renders:
  reports/final_report.md -> reports/final_report.pdf
  INTERVIEW_NOTES.md      -> INTERVIEW_NOTES.pdf

Usage: python make_pdf.py
"""

from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path

import markdown
from xhtml2pdf import pisa

import config

# Glyphs outside Latin-1 that the default PDF fonts can't render.
GLYPHS = {"→": "->", "σ": "sigma", "²": "2", "×": "x", "≤": "<=", "≥": ">=",
          "’": "'", "“": '"', "”": '"', "•": "-", "√": "sqrt", "–": "-",
          "✅": "[OK]", "⚠️": "[!]", "❌": "[X]"}

CSS = """
@page { size: A4; margin: 1.8cm; }
body { font-family: Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #222; }
h1 { font-size: 16pt; } h2 { font-size: 12.5pt; margin-top: 13pt; border-bottom: 1px solid #ccc; }
h3 { font-size: 11pt; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 3px 6px; text-align: left; }
th { background: #f0f0f0; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 6px; font-size: 9pt; }
img { width: 16cm; }
blockquote { border-left: 3px solid #d62728; margin: 8px 0; padding: 4px 10px; color: #444; background: #faf3f3; }
code { background: #f2f2f2; padding: 0 2px; }
hr { border: none; border-top: 1px solid #ccc; }
"""


def _embed_images(text: str, base_dir: Path) -> str:
    """Replace ![alt](local.png) with a base64 data URI so the PDF is self-contained."""
    def repl(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        path = (base_dir / src).resolve()
        if not path.exists():
            return m.group(0)
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"![{alt}](data:{mime};base64,{b64})"
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, text)


def render(md_path: Path, pdf_path: Path) -> None:
    text = _embed_images(md_path.read_text(encoding="utf-8"), md_path.parent)
    html_body = markdown.markdown(text, extensions=["tables", "sane_lists", "fenced_code"])
    for g, repl in GLYPHS.items():
        html_body = html_body.replace(g, repl)
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    with open(pdf_path, "wb") as f:
        result = pisa.CreatePDF(html, dest=f, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"PDF render reported {result.err} error(s) for {md_path.name}")
    print(f"Wrote {pdf_path.relative_to(config.PROJECT_ROOT)} ({pdf_path.stat().st_size // 1024} KB)")


def main() -> None:
    render(config.PROJECT_ROOT / "reports" / "final_report.md",
           config.PROJECT_ROOT / "reports" / "final_report.pdf")
    render(config.PROJECT_ROOT / "INTERVIEW_NOTES.md",
           config.PROJECT_ROOT / "INTERVIEW_NOTES.pdf")
    render(config.PROJECT_ROOT / "README.md",
           config.PROJECT_ROOT / "README.pdf")


if __name__ == "__main__":
    main()
