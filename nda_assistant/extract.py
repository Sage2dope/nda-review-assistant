"""Text extraction from uploaded NDAs (PDF or DOCX)."""

from io import BytesIO

from docx import Document
from pypdf import PdfReader

# Roughly 50,000 words. Far beyond any real NDA, so anything larger is rejected
# rather than silently truncated.
MAX_CHARS = 300_000
MIN_CHARS = 200


class ExtractionError(Exception):
    """Raised with a user-facing message when a document cannot be read."""


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        text = _from_pdf(data)
    elif name.endswith(".docx"):
        text = _from_docx(data)
    else:
        raise ExtractionError("Unsupported file type. Please upload a PDF or DOCX file.")

    text = text.strip()
    if len(text) < MIN_CHARS:
        raise ExtractionError(
            "Very little text could be read from this file. It may be a scanned "
            "image. OCR is not supported in this prototype, so please upload a "
            "text-based PDF or a DOCX."
        )
    if len(text) > MAX_CHARS:
        raise ExtractionError(
            f"This document is too long for the prototype ({len(text):,} characters, "
            f"limit {MAX_CHARS:,}). It has not been truncated or reviewed."
        )
    return text


def _from_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ExtractionError("This PDF is password protected. Please upload an unlocked copy.")
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"The PDF could not be read ({exc}).") from exc


def _from_docx(data: bytes) -> str:
    try:
        doc = Document(BytesIO(data))
    except Exception as exc:
        raise ExtractionError(f"The DOCX could not be read ({exc}).") from exc

    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts)
