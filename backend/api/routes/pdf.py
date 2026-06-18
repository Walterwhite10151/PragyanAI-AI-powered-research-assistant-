"""
backend/api/routes/pdf.py
--------------------------
POST /api/pdf/upload   — Upload and process a PDF.
POST /api/pdf/question — Ask a question against the RAG knowledge base.
GET  /api/pdf/stats    — Vector store statistics.
DELETE /api/pdf/clear  — Clear the vector store.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.api.schemas import (
    PDFUploadResponse, QuestionRequest, QuestionResponse,
    VectorStoreStats, ClearResponse,
)
from backend.services.pdf_service import handle_pdf_upload, answer_pdf_question
from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

_MAX_PDF_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    provider: str = Form(default="groq"),
):
    """Upload a PDF, extract text, index into ChromaDB, and return a summary."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF exceeds 50 MB limit.")

    logger.info(f"PDF upload: {file.filename!r} ({len(content):,} bytes), provider={provider}")
    result = handle_pdf_upload(content, file.filename, provider=provider)

    if result.get("error"):
        raise HTTPException(status_code=422, detail=result["error"])

    return PDFUploadResponse(**result)


@router.post("/question", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest):
    """Answer a question using the RAG knowledge base (indexed PDFs + Exa content)."""
    answer = answer_pdf_question(req.question, provider=req.provider)
    return QuestionResponse(question=req.question, answer=answer)


@router.get("/stats", response_model=VectorStoreStats)
async def get_stats():
    vs = get_vector_store()
    return VectorStoreStats(total_chunks=vs.doc_count)


@router.delete("/clear", response_model=ClearResponse)
async def clear_vector_store():
    vs = get_vector_store()
    vs.clear()
    return ClearResponse(message="Vector store cleared successfully.")
