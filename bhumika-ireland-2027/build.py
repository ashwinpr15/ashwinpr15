"""Render the Markdown sources in src/ to print-ready PDFs in pdf/.

Usage: python3 build.py
Requires: `pip install markdown` and a Chromium binary (CHROME env var or default path).
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC, OUT, HTML = ROOT / "src", ROOT / "pdf", ROOT / "build"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

OUTPUT_NAMES = {
    "00_briefing": "00_Read_Me_First_Briefing.pdf",
    "01_shortlist_financial_model": "01_University_Shortlist_and_Financial_Model.pdf",
    "02_cv": "02_Bhumika_Veerapura_Siddagangappa_CV.pdf",
    "03_sop": "03_Statement_of_Purpose_Galway_annotated.pdf",
    "03_sop_clean": "03_Statement_of_Purpose_Galway_SUBMIT.pdf",
    "04_lors": "04_Letters_of_Recommendation.pdf",
    "05_timeline": "05_Admissions_Visa_Funding_Timeline.pdf",
    "06_ielts_plan": "06_IELTS_Preparation_Plan.pdf",
    "07_roadmap": "07_One_Page_Roadmap.pdf",
}

BASE_CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm;
  @bottom-left { content: "Bhumika Veerapura Siddagangappa · Ireland 2027 Application Pack"; font: 7.5pt Inter, sans-serif; color: #6b7280; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font: 7.5pt Inter, sans-serif; color: #6b7280; } }
:root { --ink:#1f2937; --muted:#6b7280; --accent:#0f4c81; --accent-soft:#e8f0f8; --rule:#d1d5db;
  --warn:#9a5b00; --warn-soft:#fff6e5; --swap:#fff3b0; }
* { box-sizing: border-box; }
body { font-family: Inter, "DejaVu Sans", sans-serif; font-size: 9.6pt; line-height: 1.45; color: var(--ink);
  background: #fff; margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1 { font-size: 19pt; color: var(--accent); margin: 0 0 4pt; letter-spacing: -0.2pt; }
h2 { font-size: 12.5pt; color: var(--accent); margin: 16pt 0 6pt; padding-bottom: 3pt; border-bottom: 1.5pt solid var(--accent); break-after: avoid; }
h3 { font-size: 11pt; margin: 13pt 0 5pt; color: #111827; break-after: avoid; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 6pt; padding-left: 16pt; }
li { margin-bottom: 2pt; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.4pt; break-inside: auto; }
th { background: var(--accent); color: #fff; text-align: left; padding: 4pt 5pt; font-weight: 600; }
td { padding: 3.5pt 5pt; border-bottom: 0.6pt solid var(--rule); vertical-align: top; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) td { background: #f7f9fb; }
blockquote { margin: 6pt 0 10pt; padding: 6pt 10pt; border-left: 3pt solid var(--accent); background: var(--accent-soft); font-size: 9pt; }
.meta { color: var(--muted); font-size: 8.5pt; margin-bottom: 10pt; padding-bottom: 6pt; border-bottom: 0.6pt solid var(--rule); }
.callout { padding: 8pt 10pt; margin: 8pt 0 10pt; border-radius: 4pt; font-size: 9.2pt; break-inside: avoid; }
.callout.key { background: var(--accent-soft); border-left: 4pt solid var(--accent); }
.callout.warn { background: var(--warn-soft); border-left: 4pt solid var(--warn); }
.sources { margin-top: 14pt; padding-top: 6pt; border-top: 0.6pt solid var(--rule); font-size: 7.6pt; color: var(--muted); }
.swap { background: var(--swap); padding: 0 1pt; border-radius: 2pt; }
.opt { display: block; background: #f3f4f6; border: 0.8pt dashed #9ca3af; padding: 5pt 7pt; color: #374151; font-size: 9pt; margin: 6pt 0 8pt; }
.letter { font-family: "Liberation Serif", "DejaVu Serif", serif; font-size: 11pt; line-height: 1.5; text-align: justify; }
.letter p { margin-bottom: 8pt; }
.letter-meta { font-size: 8.5pt; color: #374151; background: #f3f4f6; padding: 6pt 8pt; border-radius: 3pt; margin-bottom: 12pt; }
.sign { margin-top: 14pt; text-align: left; }
.pagebreak { break-after: page; }
.cover-title { font-size: 9pt; text-transform: uppercase; letter-spacing: 1.5pt; color: var(--muted); margin-bottom: 2pt; }
"""

CV_CSS = """
@page { size: A4; margin: 11mm 13mm 10mm 13mm; @bottom-left { content: none; } @bottom-right { content: none; } }
body { font-size: 9.4pt; line-height: 1.4; }
.cv-head { text-align: center; margin-bottom: 4pt; }
.cv-head h1 { font-size: 20pt; margin: 0; letter-spacing: 1.5pt; text-transform: uppercase; color: #111827; }
.cv-contact { color: #374151; font-size: 8.8pt; margin: 2pt 0 0; }
h2 { font-size: 9.8pt; text-transform: uppercase; letter-spacing: 1pt; margin: 8pt 0 3pt; padding-bottom: 1.5pt; border-bottom: 1pt solid var(--accent); }
p { margin: 0 0 3pt; }
ul { margin: 1pt 0 4pt; padding-left: 12pt; }
li { margin-bottom: 1.2pt; }
.role { display: flex; justify-content: space-between; gap: 8pt; margin-top: 3pt; }
.role span:last-child { white-space: nowrap; color: #374151; }
.sub { color: #4b5563; font-size: 8.6pt; margin-top: 1pt; }
.skills { font-size: 8.8pt; }
"""

TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>{css}</style></head><body>{body}</body></html>"""


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        text = text[m.end():]
    # let Markdown inside block-level <div>/<header> be rendered
    # (.role rows hold inline spans only and must stay untouched for the flex layout)
    text = re.sub(r"<(div|header)(\s[^>]*)?>",
                  lambda x: x.group(0) if 'class="role"' in (x.group(2) or "")
                  else f"<{x.group(1)}{x.group(2) or ''} markdown=\"1\">", text)
    return meta, text


def clean_sop(text: str) -> str:
    """Submission copy of the SOP: drop swap highlights, the optional note and the appendix."""
    text = text.split('<div class="pagebreak"')[0]
    text = re.sub(r'<span class="opt">.*?</span>\n*', "", text, flags=re.S)
    text = re.sub(r'<span class="swap">\[(.*?)\]</span>', r"\1", text, flags=re.S)
    text = re.sub(r'<div class="meta"[^>]*>.*?</div>',
                  '<div class="meta">Bhumika Veerapura Siddagangappa · MSc International Accounting and Analytics (Pathway A) · '
                  'University of Galway · September 2027 intake</div>', text, flags=re.S)
    return text


def sources():
    for src in sorted(SRC.glob("*.md")):
        meta, text = parse(src)
        yield src.stem, meta, text
        if src.stem == "03_sop":
            yield "03_sop_clean", meta, clean_sop(text)


def print_pdf(html_path: Path, stem: str):
    pdf_path = OUT / OUTPUT_NAMES.get(stem, f"{stem}.pdf")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, capture_output=True)
    print(f"built {pdf_path.relative_to(ROOT)}")


def build():
    OUT.mkdir(exist_ok=True)
    HTML.mkdir(exist_ok=True)
    # hand-designed single pages are authored directly in HTML
    for page in sorted(SRC.glob("*.html")):
        print_pdf(page, page.stem)
    for stem, meta, text in sources():
        body = markdown.markdown(text, extensions=["tables", "md_in_html", "attr_list", "sane_lists"])
        css = BASE_CSS + (CV_CSS if meta.get("layout") == "cv" else "")
        html_path = HTML / f"{stem}.html"
        html_path.write_text(TEMPLATE.replace("{title}", meta.get("title", stem)).replace("{css}", css).replace("{body}", body), encoding="utf-8")
        print_pdf(html_path, stem)


if __name__ == "__main__":
    sys.exit(build())
