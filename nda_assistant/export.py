"""Export review results to CSV and Word."""

from datetime import date
from io import BytesIO

import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Pt

DISCLAIMER = (
    "LLMs are AI and can make mistakes. Please have this output reviewed by a qualified "
    "lawyer before it is relied on."
)

COLUMNS = ["Topic", "Status", "Risk", "Clause", "Quoted clause", "Issue",
           "Suggested fallback wording", "Quote check"]


def to_csv(rows: list[dict]) -> bytes:
    # utf-8-sig so Excel opens it with the right encoding.
    return pd.DataFrame(rows, columns=COLUMNS).to_csv(index=False).encode("utf-8-sig")


def to_docx(rows: list[dict], nda_name: str, parties: str, summary: str) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width

    doc.add_heading("NDA playbook review", level=1)
    doc.add_paragraph(f"Document: {nda_name}\nDate: {date.today():%d %B %Y}\nParties: {parties}")
    doc.add_paragraph(DISCLAIMER).runs[0].italic = True
    doc.add_heading("Summary", level=2)
    doc.add_paragraph(summary)
    doc.add_heading("Findings", level=2)

    table = doc.add_table(rows=1, cols=len(COLUMNS))
    table.style = "Table Grid"
    for cell, name in zip(table.rows[0].cells, COLUMNS):
        cell.text = name
        cell.paragraphs[0].runs[0].bold = True
    for row in rows:
        cells = table.add_row().cells
        for cell, name in zip(cells, COLUMNS):
            cell.text = str(row.get(name, ""))
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(8)

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
