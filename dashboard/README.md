# E2E Workflow Dashboard

Real-time visualization for the RevFlow e2e test automation workflow.

## Quick Start

```bash
cd dashboard
./start.sh
```

Then open http://localhost:5173 and run `/e2e-workflow JP-1` in Claude Code.

## Architecture

- **Server** — FastAPI + WebSocket (`server/main.py`, port 8765)
- **Client** — React + Vite + Tailwind + Framer Motion (port 5173)
- **Utilities** — `utils/client.py` (send events), `utils/hitl_gate.py` (HITL checkpoints)

## Sending Events from Workflow

```python
# CLI
python dashboard/utils/client.py event \
  --type stage_complete \
  --stage jira_fetch \
  --message "JP-1 fetched successfully" \
  --level success \
  --data '{"ticket":"JP-1","summary":"Pre-payment booking flow"}'

# Python import
import sys; sys.path.insert(0, '.')
from dashboard.utils.client import send_event
send_event("stage_complete", stage="jira_fetch", message="Done", level="success", data={"ticket": "JP-1"})
```

## HITL Checkpoints

```bash
python dashboard/utils/hitl_gate.py \
  --id "test-case-review" \
  --message "6 test cases derived from JP-1 — approve to proceed?" \
  --context '{"cases": 6, "ticket": "JP-1"}'
# Blocks here until user clicks in the browser
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DASHBOARD_URL` | `http://localhost:8765` | Server URL for utilities |
