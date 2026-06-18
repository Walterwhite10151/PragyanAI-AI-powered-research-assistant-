#!/usr/bin/env bash
# setup.sh — Bootstrap the AI Research Agent (Windows/Mac/Linux compatible)
set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔬  AI Research Agent — Setup  (Exa + Groq/Gemini)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Detect OS ──────────────────────────────────────────────────
IS_WINDOWS=false
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  IS_WINDOWS=true
fi

# ── Python check ───────────────────────────────────────────────
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
if [ -z "$PYTHON" ]; then
  echo "  ❌ Python not found. Install from https://python.org"; exit 1
fi
echo "  Python: $($PYTHON --version)"
if ! $PYTHON -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)"; then
  echo "  ❌ Python 3.9+ required"; exit 1
fi
echo "  ✅ Python OK"

# ── Node check ─────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  echo "  ❌ Node.js not found. Install from https://nodejs.org"; exit 1
fi
echo "  ✅ Node $(node --version)"

# ── Backend venv ───────────────────────────────────────────────
echo ""
echo "  Setting up Python backend…"

if [ ! -d ".venv" ]; then
  echo "  Creating virtual environment…"
  $PYTHON -m venv .venv
fi

# Activate venv — Windows (Git Bash) vs Unix path
if [ "$IS_WINDOWS" = true ]; then
  ACTIVATE=".venv/Scripts/activate"
else
  ACTIVATE=".venv/bin/activate"
fi

if [ ! -f "$ACTIVATE" ]; then
  echo "  ❌ Virtual environment creation failed."
  echo "     Try manually: $PYTHON -m venv .venv"
  exit 1
fi

# shellcheck disable=SC1090
source "$ACTIVATE"
echo "  ✅ Virtual environment active: $(which python)"

pip install --upgrade pip --quiet
pip install -r backend/requirements.txt
echo "  ✅ Backend dependencies installed"

# ── Backend .env ───────────────────────────────────────────────
if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  echo "  ✅ Created backend/.env — EDIT IT with your API keys!"
else
  echo "  ℹ️  backend/.env already exists"
fi

# ── Frontend deps ──────────────────────────────────────────────
echo ""
echo "  Setting up React frontend…"
cd frontend
npm install
cd ..
echo "  ✅ Frontend dependencies installed"

# ── Data dirs ──────────────────────────────────────────────────
mkdir -p data/chroma_db data/conversation_history data/uploads logs
echo "  ✅ Data directories ready"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Setup complete!"
echo ""
echo "  Before running, add your API keys to backend/.env:"
echo "    EXA_API_KEY    → https://exa.ai         (free)"
echo "    GROQ_API_KEY   → https://console.groq.com (free)"
echo "    GEMINI_API_KEY → https://aistudio.google.com (optional)"
echo ""

if [ "$IS_WINDOWS" = true ]; then
echo "  ── Windows (Git Bash) ────────────────────────────────"
echo ""
echo "  Terminal 1 — Backend:"
echo "    source .venv/Scripts/activate"
echo "    uvicorn backend.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 — Frontend:"
echo "    cd frontend && npm run dev"
else
echo "  ── macOS / Linux ─────────────────────────────────────"
echo ""
echo "  Terminal 1 — Backend:"
echo "    source .venv/bin/activate"
echo "    uvicorn backend.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 — Frontend:"
echo "    cd frontend && npm run dev"
fi

echo ""
echo "    Frontend → http://localhost:5173"
echo "    API Docs → http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"