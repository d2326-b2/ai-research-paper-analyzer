# pdf_extractor.py
# Handles all PDF text extraction and preprocessing tasks

import fitz  # PyMuPDF library for reading PDF files


def extract_text(pdf_path: str) -> str:
    """Opens a PDF file and extracts all text from every page."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text(sort=True)
    doc.close()
    return full_text.strip()


def is_valid_pdf(text: str) -> bool:
    """Checks if the PDF contains readable text."""
    return len(text.strip()) > 200


def smart_chunk(text: str, limit: int = 8000) -> str:
    """Trims long text to fit within Gemini token limit."""
    if len(text) <= limit:
        return text
    half = limit // 2
    start = text[:half]
    end = text[-half:]
    return start + "\n\n[...middle section trimmed...]\n\n" + end