#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$ROOT/server"
CLIENT_DIR="$ROOT/client"

# --- colours
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

# --- Resolve Python: prefer conda/miniconda Python over system Python 3.14
# System Python 3.14 breaks pydantic-core (pyo3 max supported = 3.13)
CONDA_PY="/opt/miniconda3/bin/python"
if [ -x "$CONDA_PY" ]; then
  PY="$CONDA_PY"
else
  # Fall back to whatever python3 is in PATH
  PY="$(which python3)"
fi
PY_VER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Joulez · E2E Workflow Dashboard    ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  Using Python $PY_VER at $PY"
echo ""

# --- Python deps
echo -e "${YELLOW}[1/3] Installing server dependencies...${NC}"
"$PY" -m pip install -q -r "$SERVER_DIR/requirements.txt"

# --- Node deps
echo -e "${YELLOW}[2/3] Installing client dependencies...${NC}"
cd "$CLIENT_DIR"
npm install --silent

# --- Start both
echo -e "${YELLOW}[3/3] Starting dashboard...${NC}"
echo ""
echo -e "  ${GREEN}API server${NC}  → http://localhost:8765"
echo -e "  ${GREEN}Dashboard${NC}   → http://localhost:5173  (opens automatically)"
echo ""
echo -e "  Then run your workflow:    ${CYAN}/e2e-workflow JP-1${NC}"
echo -e "  Or run the self-heal demo: ${CYAN}/self-heal-demo${NC}"
echo ""

# Ensure ports are free before starting
lsof -ti :8765 | xargs kill -9 2>/dev/null || true
lsof -ti :5173 | xargs kill -9 2>/dev/null || true

# Start FastAPI in background
"$PY" "$SERVER_DIR/main.py" &
SERVER_PID=$!

# Give server a moment to start
sleep 1

# Start Vite (foreground — ctrl-c stops both)
cd "$CLIENT_DIR"
npm run dev

# Cleanup on exit
kill $SERVER_PID 2>/dev/null || true
