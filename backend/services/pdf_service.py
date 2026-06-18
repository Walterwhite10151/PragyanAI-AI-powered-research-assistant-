"""
backend/services/pdf_service.py
---------------------------------
Orchestrates the PDF workflow: save → extract → index → summarise → Q&A.
"""

from __future__ import annotations

from backend.services.research_chains import pdf_summary_chain, rag_qa_chain
from backend.services.llm_service import get_llm, LLMProvider
from backend.tools.pdf_processor import process_pdf, save_uploaded_pdf
from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger


def handle_pdf_upload(
    file_bytes: bytes,
    filename: str,
    provider: str = "groq",
) -> dict:
    """Save, extract, index and summarise an uploaded PDF."""
    result = {"filename": filename, "pages": 0, "chunks": 0, "summary": "", "error": None}
    try:
        path = save_uploaded_pdf(file_bytes, filename)
        doc = process_pdf(path)
        result["pages"] = doc.total_pages
        result["chunks"] = len(doc.chunks)

        vs = get_vector_store()
        vs.index_pdf(doc)

        llm = get_llm(provider)
        summary = pdf_summary_chain(llm).invoke({
            "filename": filename,
            "content": doc.raw_text[:6000],
        })
        result["summary"] = summary.strip()
    except Exception as exc:
        result["error"] = str(exc)
        logger.exception("PDF pipeline failed")
    return result


def answer_pdf_question(question: str, provider: str = "groq") -> str:
    """Answer a question using the RAG knowledge base."""
    vs = get_vector_store()
    chunks = vs.retrieve(question, top_k=5)
    if not chunks:
        return "No relevant content found. Upload a PDF or research a topic first."
    try:
        llm = get_llm(provider)
        return rag_qa_chain(llm).invoke({
            "question": question,
            "context": "\n\n---\n\n".join(chunks),
        }).strip()
    except Exception as exc:
        logger.error(f"RAG Q&A failed: {exc}")
        return f"Error while answering: {exc}"
