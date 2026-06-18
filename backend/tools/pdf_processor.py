"""
backend/tools/pdf_processor.py
--------------------------------
PDF text extraction (pdfplumber primary, pypdf fallback) and chunking.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pdfplumber
import pypdf

from backend.core.config import settings
from backend.utils.logger import logger


@dataclass
class PDFDocument:
    filename: str
    file_hash: str
    total_pages: int
    raw_text: str
    chunks: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def _compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _extract_pdfplumber(path: Path) -> tuple[str, int]:
    with pdfplumber.open(path) as pdf:
        texts = [p.extract_text() or "" for p in pdf.pages]
        return "\n\n".join(texts), len(pdf.pages)


def _extract_pypdf(path: Path) -> tuple[str, int]:
    reader = pypdf.PdfReader(str(path))
    texts = [p.extract_text() or "" for p in reader.pages]
    return "\n\n".join(texts), len(reader.pages)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        chunk = text[start: start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def process_pdf(file_path: str | Path) -> PDFDocument:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    logger.info(f"Processing PDF: {path.name}")
    file_hash = _compute_hash(path)

    try:
        raw_text, n_pages = _extract_pdfplumber(path)
        if not raw_text.strip():
            raise ValueError("pdfplumber returned empty text")
    except Exception as exc:
        logger.warning(f"pdfplumber failed ({exc}), trying pypdf…")
        raw_text, n_pages = _extract_pypdf(path)

    if not raw_text.strip():
        raise ValueError(f"Could not extract text from {path.name}")

    chunks = chunk_text(raw_text)
    logger.info(f"Extracted {n_pages} pages → {len(chunks)} chunks")

    return PDFDocument(
        filename=path.name,
        file_hash=file_hash,
        total_pages=n_pages,
        raw_text=raw_text,
        chunks=chunks,
        metadata={"source": str(path), "pages": n_pages},
    )


def save_uploaded_pdf(file_bytes: bytes, filename: str) -> Path:
    dest = Path(settings.uploads_path) / filename
    dest.write_bytes(file_bytes)
    logger.info(f"Saved PDF: {dest}")
    return dest
