"""
HypoGen PDF Text Extraction Module
Handles PDF file processing and text extraction

This module provides utilities for:
- Extracting text from PDF files using PyMuPDF
- Validating PDF quality and text content
- Smart text chunking for LLM token limits

Author: Your Name
Date: 2024
"""

import fitz  # PyMuPDF library for reading PDF files


def extract_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file, page by page.
    
    Opens a PDF file and extracts all readable text from every page.
    This works best with text-based PDFs (not scanned/image-based).
    
    Args:
        pdf_path (str): Path to the PDF file to extract text from
        
    Returns:
        str: Combined text from all pages, stripped of leading/trailing whitespace
        
    Raises:
        Exception: If the PDF file cannot be opened or read
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text(sort=True)
    doc.close()
    return full_text.strip()


def is_valid_pdf(text: str) -> bool:
    """
    Check if PDF contains sufficient readable text.
    
    Validates that the PDF is text-based (not scanned/image-based)
    by checking for a minimum amount of extracted text.
    
    Args:
        text (str): Extracted text from PDF
        
    Returns:
        bool: True if PDF has sufficient text (>200 chars), False if likely scanned
    """
    return len(text.strip()) > 200


def smart_chunk(text: str, limit: int = 8000) -> str:
    """
    Intelligently chunk text to fit within token limits.
    
    Since Google Gemini has token limits, this function trims long texts
    while preserving both the beginning and end of the document.
    This helps the AI understand both the paper's introduction and conclusion.
    
    Args:
        text (str): Full text to chunk
        limit (int): Maximum character limit (default: 8000 chars ≈ 2000 tokens)
        
    Returns:
        str: Chunked text within limit, or original text if already short
    """
    if len(text) <= limit:
        return text
    
    # Split the limit in half for start and end sections
    half = limit // 2
    start = text[:half]
    end = text[-half:]
    return start + "\n\n[...middle section trimmed...]\n\n" + end
