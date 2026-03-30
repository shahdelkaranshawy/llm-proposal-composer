import os
from io import BytesIO
from typing import Optional, Dict, Any
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file: BytesIO) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF: {e}")

def extract_text_from_docx(file: BytesIO) -> str:
    """Extract text from a Word (.docx) file."""
    try:
        doc = Document(file)
        text = "\n".join(p.text for p in doc.paragraphs)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read DOCX: {e}")

def extract_text_from_txt(file: BytesIO) -> str:
    """Extract text from a plain text file."""
    try:
        return file.read().decode("utf-8").strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read TXT: {e}")

def extract_text(uploaded_file: Optional[BytesIO], filename: str) -> str:
    """Detect file type and extract text."""
    if not uploaded_file:
        return ""

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(uploaded_file)
    elif ext == ".docx":
        return extract_text_from_docx(uploaded_file)
    elif ext == ".txt":
        return extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_and_extract_documents(
    rfp_file: Optional[BytesIO],
    rfp_name: Optional[str],
    template_file: Optional[BytesIO],
    template_name: Optional[str],
    additional_files: Optional[list[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Extract text from RFP, Template, and optional additional documents."""
    data = {
        "rfp_text": extract_text(rfp_file, rfp_name) if rfp_file else "",
        "template_text": extract_text(template_file, template_name) if template_file else "",
        "additional_docs": []
    }

    if additional_files:
        for file_info in additional_files:
            file = file_info["file"]
            name = file_info["name"]
            text = extract_text(file, name)
            data["additional_docs"].append({"filename": name, "text": text})

    return data
