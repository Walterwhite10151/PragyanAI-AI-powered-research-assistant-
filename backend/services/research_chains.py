"""
backend/services/research_chains.py
-------------------------------------
All LangChain LCEL prompt chains used by the research agent.
Each chain is a pure function: (inputs dict) → string.
The LLM is injected at call time so Groq/Gemini can be swapped per request.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_parser = StrOutputParser()


def _chain(llm: BaseChatModel, system: str, human: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])
    return prompt | llm | _parser


# ── Overview ───────────────────────────────────────────────────────────────────

_OVERVIEW_SYS = "You are a knowledgeable research assistant. Write clear, engaging prose."
_OVERVIEW_HUMAN = """Write a detailed OVERVIEW of the following topic based on the search results.

Topic: {topic}

Search Results from Exa:
{search_results}

RAG Context (from uploaded documents):
{rag_context}

Instructions:
- Write 3-5 well-structured paragraphs.
- Begin with a compelling hook.
- Cover: what it is, why it matters, current state/trends.
- Use plain language for a curious non-expert.
- No bullet points in this section.

Overview:"""

def overview_chain(llm: BaseChatModel):
    return _chain(llm, _OVERVIEW_SYS, _OVERVIEW_HUMAN)


# ── Key Concepts ───────────────────────────────────────────────────────────────

_CONCEPTS_SYS = "You are an expert educator creating a precise technical glossary."
_CONCEPTS_HUMAN = """Identify and explain the KEY CONCEPTS for this topic.

Topic: {topic}

Context:
{search_results}

RAG Context:
{rag_context}

Instructions:
- List 6-10 key concepts.
- Format: **Concept Name**: Clear 1-2 sentence explanation.
- Order: foundational → advanced.

Key Concepts:"""

def key_concepts_chain(llm: BaseChatModel):
    return _chain(llm, _CONCEPTS_SYS, _CONCEPTS_HUMAN)


# ── Important Facts ────────────────────────────────────────────────────────────

_FACTS_SYS = "You are a precise fact-extractor. Only state verifiable, specific information."
_FACTS_HUMAN = """Extract the most IMPORTANT FACTS about this topic from the sources below.

Topic: {topic}

Sources:
{search_results}

RAG Context:
{rag_context}

Instructions:
- Provide 8-12 factual bullet points.
- Include statistics, dates, names, and figures where available.
- Prioritise surprising or non-obvious facts.
- Cite the source title inline: (Source: <title>)
- Format: • [Fact] (Source: ...)

Important Facts:"""

def important_facts_chain(llm: BaseChatModel):
    return _chain(llm, _FACTS_SYS, _FACTS_HUMAN)


# ── Learning Roadmap ───────────────────────────────────────────────────────────

_ROADMAP_SYS = "You are a senior curriculum designer building actionable learning paths."
_ROADMAP_HUMAN = """Build a structured LEARNING ROADMAP for mastering this topic.

Topic: {topic}

Context:
{search_results}

RAG Context:
{rag_context}

Instructions:
- Four phases: Beginner → Intermediate → Advanced → Expert.
- Each phase: 3-5 specific, actionable items.
- Include resource types (books, courses, projects, communities).
- Add estimated time investment per phase.
- Keep it realistic and encouraging.

Learning Roadmap:"""

def roadmap_chain(llm: BaseChatModel):
    return _chain(llm, _ROADMAP_SYS, _ROADMAP_HUMAN)


# ── Final Summary ──────────────────────────────────────────────────────────────

_SUMMARY_SYS = "You are a senior analyst writing crisp executive summaries."
_SUMMARY_HUMAN = """Synthesise the research below into a tight FINAL SUMMARY.

Topic: {topic}

Overview:
{overview}

Key Concepts:
{key_concepts}

Important Facts:
{important_facts}

Instructions:
- 2-3 paragraphs maximum.
- Lead with the single most important insight.
- End with exactly one sentence starting "Bottom line:".
- No bullet points.

Final Summary:"""

def summary_chain(llm: BaseChatModel):
    return _chain(llm, _SUMMARY_SYS, _SUMMARY_HUMAN)


# ── PDF Summary ────────────────────────────────────────────────────────────────

_PDF_SYS = "You are a thorough document analyst. Provide structured, complete summaries."
_PDF_HUMAN = """Summarise this PDF document.

Filename: {filename}

Content:
{content}

Structure your response as:
1. **Document Overview** – What is this about?
2. **Main Topics Covered** – Key themes.
3. **Critical Findings** – Most important points and arguments.
4. **Conclusions & Recommendations** – What does it conclude?

Summary:"""

def pdf_summary_chain(llm: BaseChatModel):
    return _chain(llm, _PDF_SYS, _PDF_HUMAN)


# ── RAG Q&A ────────────────────────────────────────────────────────────────────

_RAG_SYS = "You are a precise assistant. Answer ONLY from the provided context chunks. If the answer isn't in the context, say so clearly."
_RAG_HUMAN = """Answer the question using ONLY the context below.

Question: {question}

Context:
{context}

Answer:"""

def rag_qa_chain(llm: BaseChatModel):
    return _chain(llm, _RAG_SYS, _RAG_HUMAN)