---
title: AI Research Agent
emoji: 🔬
colorFrom: emerald
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: FastAPI + React + Exa + Groq/Gemini + LangGraph + ChromaDB
---

# 🔬 AI Research Agent

**Stack:** React · FastAPI · Exa Neural Search · Groq/Gemini · LangGraph · ChromaDB RAG

## Features
- Neural web research via **Exa** (semantic search + full-page content)
- **Groq** (llama-3.3-70b) and **Google Gemini** LLMs — switch per request
- **LangGraph** 8-node pipeline: search → RAG → overview → concepts → facts → roadmap → summary → YouTube
- PDF upload with **ChromaDB** RAG and Q&A
- Session history + user preferences
- React TypeScript frontend with dark UI
- Full REST API with Swagger docs at `/docs`
