# 🔬 AI Research Agent — Complete Setup Guide

**Stack:** React + FastAPI + Exa Search + Groq/Gemini + LangGraph + ChromaDB

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Browser)                        │
│                      React + TypeScript                       │
│     Research │ PDF Assistant │ History │ Settings            │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTP/JSON  (Vite proxy → FastAPI)
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                            │
│  POST /api/research  POST /api/pdf/upload                    │
│  GET  /api/history   GET  /api/status                        │
└──────┬──────────────┬──────────────────┬────────────────────┘
       │              │                  │
┌──────▼──────┐ ┌─────▼──────┐ ┌────────▼──────────┐
│  Exa Search │ │Groq/Gemini │ │  ChromaDB (RAG)   │
│  Neural     │ │LangGraph   │ │  sentence-         │
│  Web Search │ │8-node pipe │ │  transformers      │
└─────────────┘ └────────────┘ └────────────────────┘
```

### LangGraph Pipeline (8 Nodes)

```
exa_search → rag_retrieve → overview → key_concepts
    → facts → roadmap → summary → youtube → END
```

---

## 📁 Project Structure

```
ai_research_agent/
│
├── backend/
│   ├── main.py                      # FastAPI app factory
│   ├── requirements.txt             # Python deps
│   ├── .env.example                 # Env template
│   ├── api/
│   │   ├── schemas.py               # Pydantic request/response models
│   │   └── routes/
│   │       ├── research.py          # POST /api/research, GET /api/status
│   │       ├── pdf.py               # POST /api/pdf/upload, /pdf/question
│   │       └── history.py           # GET/DELETE /api/history, /preferences
│   ├── core/
│   │   └── config.py                # pydantic-settings config
│   ├── services/
│   │   ├── llm_service.py           # Groq + Gemini LLM factory
│   │   ├── research_chains.py       # 6 LangChain LCEL chains
│   │   ├── research_agent.py        # LangGraph StateGraph
│   │   └── pdf_service.py           # PDF upload → index → summarise
│   ├── tools/
│   │   ├── exa_search.py            # Exa neural search + highlights
│   │   ├── youtube_search.py        # YouTube recommendations
│   │   └── pdf_processor.py         # pdfplumber extraction + chunking
│   ├── rag/
│   │   └── vector_store.py          # ChromaDB + sentence-transformers
│   └── utils/
│       ├── logger.py                # Loguru logger
│       └── storage.py               # JSON history + preferences
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts               # Dev proxy → FastAPI
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx                 # React entry
│       ├── App.tsx                  # Router + Toaster
│       ├── index.css                # Tailwind + custom styles
│       ├── types/index.ts           # TypeScript interfaces
│       ├── services/api.ts          # Axios API layer
│       ├── components/
│       │   ├── ui.tsx               # Card, Button, Badge, Tabs…
│       │   ├── Sidebar.tsx          # Navigation
│       │   └── ResearchResults.tsx  # Tabbed results viewer
│       └── pages/
│           ├── ResearchPage.tsx     # Main research UI
│           ├── PDFPage.tsx          # PDF upload + RAG Q&A
│           ├── HistoryPage.tsx      # Session history browser
│           └── SettingsPage.tsx     # Status + preferences
│
├── data/                            # Runtime data (git-ignored)
├── logs/                            # Rotating log files
├── tests/backend/                   # pytest tests
├── setup.sh                         # One-command setup
├── docker-compose.yml               # Production stack
├── Dockerfile.backend
└── frontend/Dockerfile.frontend
```

---

## 🔑 API Keys Required

| Service | Key Variable | Free Tier | Link |
|---------|-------------|-----------|------|
| **Exa** | `EXA_API_KEY` | ✅ 1000 searches/mo | [exa.ai](https://exa.ai) |
| **Groq** | `GROQ_API_KEY` | ✅ Generous free tier | [console.groq.com](https://console.groq.com) |
| **Gemini** | `GEMINI_API_KEY` | ✅ Free tier | [aistudio.google.com](https://aistudio.google.com) |

> You need at least **one** LLM key (Groq or Gemini) and the **Exa** key. Both LLM providers are optional but one must be configured.

---

## 🚀 Local Setup (Step by Step)

### Step 1 — Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.9 | [python.org](https://python.org) |
| Node.js | ≥ 18 | [nodejs.org](https://nodejs.org) |
| npm | ≥ 9 | Bundled with Node |

---

### Step 2 — Extract and enter the project

```bash
cd ai_research_agent
```

---

### Step 3 — Backend setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

### Step 4 — Configure API keys

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your keys:

```env
EXA_API_KEY=your_exa_key_here
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here   # optional if using Groq
DEFAULT_LLM_PROVIDER=groq
```

---

### Step 5 — Frontend setup

```bash
cd frontend
npm install
cd ..
```

---

### Step 6 — Run both servers

**Terminal A — FastAPI backend:**
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal B — React frontend:**
```bash
cd frontend
npm run dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | React frontend |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8000/api/status | Health check |

---

### One-command setup

```bash
bash setup.sh
# Then follow the printed instructions
```

---

## 🐳 Docker Compose (Production)

```bash
# Ensure backend/.env has your API keys, then:
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

---

## 🧪 Running Tests

```bash
source .venv/bin/activate
pip install pytest pytest-asyncio
pytest tests/ -v

# With coverage
pip install pytest-cov
pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 🤗 Deploy on Hugging Face Spaces

HF Spaces supports FastAPI natively but not a dual server setup.
**Recommended approach:** Deploy backend as a FastAPI Space, host frontend separately (Vercel / Netlify).

### Backend Space (FastAPI)

1. Create a new Space → SDK: **Gradio** or **Docker**
2. Use `Dockerfile.backend`
3. In Space **Secrets**, add:
   - `EXA_API_KEY`
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
   - `CORS_ORIGINS=https://your-frontend.vercel.app`

### Frontend (Vercel — free)

```bash
cd frontend
# Set VITE_API_URL to your HF Space backend URL
echo "VITE_API_URL=https://your-space.hf.space" > .env.production
npm run build
# Deploy dist/ to Vercel or Netlify
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Health + provider config |
| `POST` | `/api/research` | Run full research pipeline |
| `POST` | `/api/pdf/upload` | Upload + index PDF |
| `POST` | `/api/pdf/question` | RAG question answering |
| `GET` | `/api/pdf/stats` | Vector store chunk count |
| `DELETE` | `/api/pdf/clear` | Clear vector store |
| `GET` | `/api/history` | List all sessions |
| `GET` | `/api/history/{id}` | Get session by ID |
| `DELETE` | `/api/history` | Clear all history |
| `GET` | `/api/preferences` | Load preferences |
| `PUT` | `/api/preferences` | Update preferences |
| `DELETE` | `/api/preferences/reset` | Reset to defaults |

Full interactive docs at **http://localhost:8000/docs**

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| `EXA_API_KEY is not set` | Add key to `backend/.env` — get one free at exa.ai |
| `GROQ_API_KEY is not set` | Add key to `backend/.env` — get one free at console.groq.com |
| `CORS error in browser` | Check `CORS_ORIGINS` in `.env` includes `http://localhost:5173` |
| `ChromaDB errors` | Delete `data/chroma_db/` and restart backend |
| Frontend shows blank page | Run `npm install` in `frontend/`, then `npm run dev` |
| `ModuleNotFoundError` | Activate venv: `source .venv/bin/activate` |
| Port 8000 in use | `uvicorn backend.main:app --port 8001` and update vite.config.ts proxy |
| Exa returns 0 results | Check API key validity; try a broader search query |
| PDF extraction empty | Try a text-based (not scanned image) PDF |

---

## 🔄 Switching LLM Provider

Change the default in `backend/.env`:
```env
DEFAULT_LLM_PROVIDER=gemini   # or groq
```

Or select per-request in the React UI provider dropdown — no restart needed.

---

## 📝 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `EXA_API_KEY` | — | **Required.** Exa neural search API key |
| `EXA_MAX_RESULTS` | `5` | Results per Exa query |
| `EXA_USE_HIGHLIGHTS` | `true` | Use Exa AI-extracted highlights |
| `GROQ_API_KEY` | — | Groq API key (need Groq or Gemini) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model ID |
| `GEMINI_API_KEY` | — | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model ID |
| `DEFAULT_LLM_PROVIDER` | `groq` | `groq` or `gemini` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local sentence-transformer model |
| `SUMMARY_MAX_TOKENS` | `2048` | LLM max output tokens |
| `BACKEND_PORT` | `8000` | FastAPI server port |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins (comma-separated) |
