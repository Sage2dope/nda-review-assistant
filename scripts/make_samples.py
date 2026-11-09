"""Build the sample NDAs in samples/ from plain text sources.

Usage: python scripts/make_samples.py <source.txt> <output.docx|output.pdf>
Needs python-docx (in requirements.txt) and, for PDF output only, reportlab.
"""

import re
import sys
from pathlib import Path

HEADING = re.compile(r"^\d+\.\s+\S")


def build_docx(lines: list[str], out: Path) -> None:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run(lines[0]).bold = True
    for line in lines[1:]:
        p = doc.add_paragraph()
        p.add_run(line).bold = bool(HEADING.match(line))
    doc.save(out)


def build_pdf(lines: list[str], out: Path) -> None:
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    story = [Paragraph(escape(lines[0]), styles["Title"]), Spacer(1, 12)]
    for line in lines[1:]:
        text = escape(line)
        story.append(Paragraph(f"<b>{text}</b>" if HEADING.match(line) else text, styles["BodyText"]))
        story.append(Spacer(1, 6))
    SimpleDocTemplate(str(out), pagesize=A4).build(story)


if __name__ == "__main__":
    source, out = Path(sys.argv[1]), Path(sys.argv[2])
    lines = [l.strip() for l in source.read_text(encoding="utf-8").splitlines() if l.strip()]
    out.parent.mkdir(parents=True, exist_ok=True)
    (build_pdf if out.suffix.lower() == ".pdf" else build_docx)(lines, out)
    print(f"Wrote {out}")
