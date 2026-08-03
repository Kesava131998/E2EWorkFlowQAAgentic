import asyncio
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Project root is three levels up from dashboard/server/main.py
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
ALLOWED_DIRS = {"plans", "tests", "reports"}

app = FastAPI(title="E2E Workflow Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve reports/ as static files so Allure HTML report is accessible at /reports/allure-html/
# Directory is created eagerly so the mount never fails on first run
(PROJECT_ROOT / "reports").mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(PROJECT_ROOT / "reports"), html=True), name="reports")

# In-memory state
connected_clients: list[WebSocket] = []
event_log: list[dict] = []
hitl_responses: dict[str, asyncio.Future] = {}


class Event(BaseModel):
    id: str | None = None
    type: str
    timestamp: str | None = None
    stage: str | None = None
    message: str = ""
    level: str = "info"
    data: dict[str, Any] = {}
    checkpoint_id: str | None = None
    options: list[dict] | None = None


class HitlResponse(BaseModel):
    choice: str
    feedback: str | None = None


async def broadcast(event: dict):
    event_log.append(event)
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected_clients.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    # Replay history to new client
    for event in event_log:
        await websocket.send_json(event)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.post("/event")
async def receive_event(event: Event):
    payload = event.model_dump()
    payload["id"] = payload["id"] or str(uuid.uuid4())
    payload["timestamp"] = payload["timestamp"] or datetime.utcnow().isoformat()

    # New workflow — wipe previous run's state before broadcasting
    if event.type == "workflow_start":
        event_log.clear()
        hitl_responses.clear()

    # Register HITL future BEFORE broadcasting so the frontend can respond immediately
    if event.type == "hitl_checkpoint" and event.checkpoint_id:
        loop = asyncio.get_event_loop()
        hitl_responses[event.checkpoint_id] = loop.create_future()

    await broadcast(payload)
    return {"ok": True, "id": payload["id"]}


@app.post("/hitl/{checkpoint_id}/respond")
async def hitl_respond(checkpoint_id: str, response: HitlResponse):
    future = hitl_responses.get(checkpoint_id)
    if future and not future.done():
        future.set_result({"choice": response.choice, "feedback": response.feedback})
        label = response.choice
        if response.feedback:
            label += f' — "{response.feedback[:60]}{"…" if len(response.feedback) > 60 else ""}"'
        await broadcast({
            "id": str(uuid.uuid4()),
            "type": "hitl_response",
            "timestamp": datetime.utcnow().isoformat(),
            "checkpoint_id": checkpoint_id,
            "choice": response.choice,
            "feedback": response.feedback,
            "message": f"HITL: {label}",
            "level": "success" if response.choice == "approve" else "warning",
        })
        return {"ok": True}
    return {"ok": False, "error": "No pending checkpoint"}


@app.get("/hitl/{checkpoint_id}/wait")
async def hitl_wait(checkpoint_id: str, timeout: float = 300):
    future = hitl_responses.get(checkpoint_id)
    if not future:
        return {"error": "Unknown checkpoint"}
    try:
        result = await asyncio.wait_for(asyncio.shield(future), timeout=timeout)
        # result is {"choice": ..., "feedback": ...}
        if isinstance(result, dict):
            return result
        return {"choice": result}
    except asyncio.TimeoutError:
        return {"choice": "timeout", "feedback": None}


@app.delete("/reset")
async def reset():
    global _active_run
    if _active_run is not None and _active_run.returncode is None:
        try:
            _active_run.terminate()
        except Exception as e:
            print(f"[Reset] Failed to terminate active run: {e}")
        _active_run = None

    event_log.clear()
    hitl_responses.clear()
    await broadcast({"type": "reset", "id": str(uuid.uuid4()), "timestamp": datetime.utcnow().isoformat()})
    return {"ok": True}


@app.get("/artifact")
async def get_artifact(path: str):
    parts = Path(path).parts
    if not parts or parts[0] not in ALLOWED_DIRS:
        raise HTTPException(status_code=403, detail="Only plans/, tests/, reports/ paths are allowed")
    resolved = (PROJECT_ROOT / path).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT)):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return PlainTextResponse(resolved.read_text(encoding="utf-8", errors="replace"))


@app.get("/health")
async def health():
    return {"status": "ok", "clients": len(connected_clients), "events": len(event_log)}


def _text_block(text: str, size: str = "Default", weight: str = "Default",
                color: str = "Default", wrap: bool = True) -> dict:
    return {"type": "TextBlock", "text": text, "size": size,
            "weight": weight, "color": color, "wrap": wrap}


def _fact_set(facts: list[tuple[str, str]]) -> dict:
    return {"type": "FactSet", "facts": [{"title": k, "value": v} for k, v in facts]}


def _separator() -> dict:
    return {"type": "TextBlock", "text": " ", "separator": True, "spacing": "Small"}


def _stat_tile(label: str, value: str, color: str) -> dict:
    return {
        "type": "Column", "width": "stretch", "verticalContentAlignment": "Center",
        "items": [
            {"type": "TextBlock", "text": value, "size": "ExtraLarge", "weight": "Bolder",
             "color": color, "horizontalAlignment": "Center", "wrap": False},
            {"type": "TextBlock", "text": label, "size": "Small", "weight": "Bolder",
             "color": "Subtle", "horizontalAlignment": "Center", "wrap": False},
        ],
    }


def _build_teams_payload(log: list[dict]) -> dict:
    """Build a Teams Adaptive Card from the current event log."""
    ticket = branch = pr_url = None
    stages_done: list[str] = []
    stages_failed: list[str] = []
    passed = failed = skipped = duration = None

    stage_labels = {
        "jira_fetch": "Jira Fetch", "branch_create": "Branch",
        "swagger_discovery": "Swagger", "test_cases": "Test Cases",
        "generate_tests": "Generate Tests", "run_tests": "Run Tests",
        "postman_export": "Postman", "commit_push": "Commit",
        "raise_pr": "Raise PR", "update_jira": "Update Jira", "pr_review": "PR Review",
    }

    for ev in log:
        d = ev.get("data", {})
        if ev.get("type") == "stage_complete":
            sid = ev.get("stage", "")
            stages_done.append(stage_labels.get(sid, sid))
            if sid == "jira_fetch":
                ticket = d.get("ticket") or ticket
            if sid == "branch_create":
                branch = d.get("branch") or branch
            if sid == "raise_pr":
                pr_url = d.get("pr_url") or pr_url
            if sid == "run_tests":
                passed   = d.get("passed",   passed)
                failed   = d.get("failed",   failed)
                skipped  = d.get("skipped",  skipped)
                duration = d.get("duration_s", duration)
        if ev.get("type") == "stage_error":
            sid = ev.get("stage", "")
            stages_failed.append(stage_labels.get(sid, sid))

    has_failures = bool(stages_failed)
    overall_emoji = "❌" if has_failures else "✅"
    overall_label = f"FAILED — {', '.join(stages_failed)}" if has_failures else "PASSED"
    overall_color = "Attention" if has_failures else "Good"
    header_color  = "Attention" if has_failures else "Accent"

    now_str = datetime.utcnow().strftime("%d %b %Y  %H:%M UTC")
    title   = ticket or "E2E Workflow"

    body: list[dict] = [
        # ── Header ──────────────────────────────────────────────────────────
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column", "width": "stretch", "verticalContentAlignment": "Center",
                    "items": [
                        _text_block("🎭  E2E Workflow Update", "Large", "Bolder", "Default", False),
                        _text_block(title, "Medium", "Bolder", header_color, False),
                        _text_block(f"Run  ·  {now_str}", "Small", "Default", "Subtle", False),
                    ],
                },
                {
                    "type": "Column", "width": "auto", "verticalContentAlignment": "Center",
                    "items": [{
                        "type": "Container",
                        "style": "attention" if has_failures else "good",
                        "spacing": "Small",
                        "items": [
                            {"type": "TextBlock", "text": f"{overall_emoji}  {overall_label}",
                             "size": "Small", "weight": "Bolder", "color": "Default",
                             "horizontalAlignment": "Center", "wrap": False},
                            {"type": "TextBlock", "text": "Overall Status",
                             "size": "Small", "weight": "Default", "color": "Subtle",
                             "horizontalAlignment": "Center", "wrap": False},
                        ],
                    }],
                },
            ],
        },
    ]

    # ── Test results tiles (if tests ran) ────────────────────────────────────
    if passed is not None:
        body += [
            _separator(),
            _text_block("TEST RESULTS", "Small", "Bolder", "Subtle", False),
            {
                "type": "ColumnSet",
                "columns": [
                    _stat_tile("PASSED",  str(passed),  "Good"),
                    _stat_tile("FAILED",  str(failed),  "Attention" if failed else "Subtle"),
                    _stat_tile("SKIPPED", str(skipped), "Warning" if skipped else "Subtle"),
                    *([_stat_tile("DURATION", f"{duration}s", "Default")] if duration else []),
                ],
            },
        ]

    # ── Stage progress ───────────────────────────────────────────────────────
    body += [
        _separator(),
        _text_block("STAGES COMPLETED", "Small", "Bolder", "Subtle", False),
        _text_block(", ".join(stages_done) if stages_done else "None yet",
                    "Default", "Default", "Default", True),
    ]

    if stages_failed:
        body += [
            _text_block("STAGES FAILED", "Small", "Bolder", "Attention", False),
            _text_block(", ".join(stages_failed), "Default", "Default", "Attention", True),
        ]

    # ── Key details ──────────────────────────────────────────────────────────
    facts: list[tuple[str, str]] = []
    if branch:
        facts.append(("Branch", branch))
    if pr_url:
        facts.append(("Pull Request", pr_url))
    facts.append(("Triggered", now_str))

    body += [_separator(), _fact_set(facts)]

    # ── Footer ───────────────────────────────────────────────────────────────
    body += [
        _separator(),
        _text_block("Powered by **RevFlow Automation** — E2E Workflow Dashboard",
                    "Small", "Default", "Subtle", True),
    ]

    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type":    "AdaptiveCard",
        "version": "1.5",
        "body":    body,
    }

    return {
        "type": "message",
        "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}],
    }


@app.post("/teams/notify")
async def teams_notify():
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL", "").strip()
    if not webhook_url:
        raise HTTPException(status_code=503, detail="TEAMS_WEBHOOK_URL not configured")

    payload = _build_teams_payload(event_log)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Teams webhook returned {exc.response.status_code}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    title = payload["attachments"][0]["content"]["body"][0]["columns"][0]["items"][1]["text"]
    return {"ok": True, "message": f"Teams card sent for: {title}"}


# ── Workflow trigger endpoints ─────────────────────────────────────────────────

# Track the currently running subprocess so we don't fire two at once
_active_run: asyncio.subprocess.Process | None = None


async def _spawn_runner(script_path: str, extra_args: list[str] = None):
    """Run a dashboard mock-runner script as a background subprocess.

    The runner itself posts events to /event, so we don't need to capture its
    stdout — we just let it stream into the WebSocket pipeline naturally.
    """
    global _active_run
    cmd = [sys.executable, script_path] + (extra_args or [])
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
        )
        _active_run = proc
        await proc.wait()
    except Exception as exc:
        print(f"[runner] error: {exc}", file=sys.stderr)
    finally:
        _active_run = None


@app.post("/run/e2e")
async def trigger_e2e(background_tasks: BackgroundTasks):
    """Launch the E2E workflow mock runner from the dashboard UI."""
    global _active_run
    if _active_run is not None and _active_run.returncode is None:
        raise HTTPException(status_code=409, detail="A workflow is already running")
    script = str(PROJECT_ROOT / "dashboard" / "mock_run.py")
    if not Path(script).exists():
        raise HTTPException(status_code=404, detail=f"Runner not found: {script}")
    background_tasks.add_task(_spawn_runner, script)
    return {"ok": True, "mode": "e2e", "script": "dashboard/mock_run.py"}


class SelfHealRequest(BaseModel):
    pr_number: str | None = None
    pr_title:  str | None = None
    pr_branch: str | None = None
    pr_url:    str | None = None


@app.post("/run/self-heal")
async def trigger_self_heal(background_tasks: BackgroundTasks, body: SelfHealRequest = None):
    """Launch self-heal.

    - No PR data (Mock Run button): spawns self_heal_run.py (scripted demo)
    - PR data present (webhook modal): spawns self_heal_agent.py standalone (100% real)
    """
    global _active_run
    if _active_run is not None and _active_run.returncode is None:
        raise HTTPException(status_code=409, detail="A workflow is already running")

    if body and body.pr_number:
        # Webhook-sourced run — use the real agent (no mocks)
        script = str(PROJECT_ROOT / "scripts" / "self_heal_agent.py")
        if not Path(script).exists():
            raise HTTPException(status_code=404, detail="self_heal_agent.py not found")
        extra_args = ["--pr-number", body.pr_number]
        if body.pr_branch: extra_args += ["--pr-branch", body.pr_branch]
        if body.pr_title:  extra_args += ["--pr-title",  body.pr_title]
        if body.pr_url:    extra_args += ["--pr-url",    body.pr_url]
        background_tasks.add_task(_spawn_runner, script, extra_args)
        return {"ok": True, "mode": "self_heal", "runner": "real"}
    else:
        # Mock Run button — scripted visualisation
        script = str(PROJECT_ROOT / "dashboard" / "self_heal_run.py")
        if not Path(script).exists():
            raise HTTPException(status_code=404, detail="self_heal_run.py not found")
        background_tasks.add_task(_spawn_runner, script)
        return {"ok": True, "mode": "self_heal", "runner": "mock"}


from fastapi import Request


@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Receive a GitHub PR webhook and broadcast a pr_detected event to the dashboard.

    The dashboard will show a modal. The user confirms → the frontend calls
    POST /run/self-heal with the PR data, spawning the mock runner.
    """
    try:
        payload = await request.json()
    except Exception:
        return {"ok": False, "error": "Invalid JSON"}

    pr_action = payload.get("action")
    if "pull_request" not in payload or pr_action not in ("opened", "synchronize", "reopened"):
        return {"ok": True, "message": "Ignored — not a relevant PR event"}

    pr = payload.get("pull_request", {})
    pr_number = str(pr.get("number", ""))
    pr_title  = pr.get("title", "Unknown PR")
    pr_url    = pr.get("html_url", "")
    pr_branch = pr.get("head", {}).get("ref", "unknown-branch")

    print(f"[Webhook] PR #{pr_number} ({pr_action}): {pr_title}")

    await broadcast({
        "id":        str(uuid.uuid4()),
        "type":      "pr_detected",
        "timestamp": datetime.utcnow().isoformat(),
        "message":   f"PR #{pr_number}: {pr_title}",
        "level":     "warning",
        "data": {
            "pr_number": pr_number,
            "pr_title":  pr_title,
            "pr_branch": pr_branch,
            "pr_url":    pr_url,
        },
    })

    return {"ok": True, "message": f"PR #{pr_number} event broadcast to dashboard"}

@app.get("/run/status")
async def run_status():
    """Check whether a workflow runner subprocess is currently active."""
    global _active_run
    running = _active_run is not None and _active_run.returncode is None
    return {"running": running}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="warning")
