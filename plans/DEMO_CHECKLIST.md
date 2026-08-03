# Demo Readiness Checklist

> Quick-reference for adhoc demos of the **E2E Workflow** and **Self-Heal** flows.
> Run top-to-bottom before any demo. Each section is independent.

---

## 1. Common — Start Here (Both Demos)

### 1.1 Dashboard Server

- [ ] Start dashboard: `cd dashboard && ./start.sh`
- [ ] Confirm FastAPI is up: `curl http://localhost:8765/health` → `{"status":"ok",...}`
- [ ] Confirm frontend is up: open `http://localhost:5173` in browser
- [ ] At least 1 client connected: health response shows `"clients": 1`
- [ ] Reset any stale run state: `curl -X DELETE http://localhost:8765/reset`

### 1.2 MCP Servers (Claude Tools)

Three are loaded automatically from `.mcp.json` when `claude` runs. Verify tokens are live:

| MCP | Quick Check |
|-----|-------------|
| **GitHub** | `gh auth status` or check `.mcp.json` token hasn't expired |
| **Jira** | `curl -u email:token https://vikeshwiki9.atlassian.net/rest/api/3/myself` → 200 |
| **Playwright** | `npx @playwright/mcp --version` (should print without error) |

- [ ] GitHub token valid (check `.mcp.json` → `GITHUB_PERSONAL_ACCESS_TOKEN`)
- [ ] Jira reachable and token valid
- [ ] Playwright MCP can launch a browser: `npx playwright open about:blank` — opens and closes cleanly
- [ ] `ANTHROPIC_API_KEY` set in `.env` (needed for `claude -p` calls inside self-heal agent)
- [ ] `AUTH_USERNAME` / `AUTH_PASSWORD` set in `.env` for RevFlow Microsoft SSO login

### 1.3 Ports

- [ ] Port **8765** is free (or already held by the dashboard server)
- [ ] Port **5173** is free (or already held by the Vite client)
- [ ] If doing the real self-heal webhook flow: port **3000** needs the RevFlow frontend app running locally (TODO: confirm the real frontend repo/dev-server setup once known)

### 1.4 Repos & Git State

- [ ] Automation repo is on `main`, clean: `git status` → nothing to commit
- [ ] Latest main pulled: `git pull origin main`
- [ ] `claude` CLI is in PATH: `which claude`
- [ ] `pytest` is in PATH and resolves to the right venv: `which pytest`

---

## 2. E2E Workflow Demo Checklist

**What it does**: Simulates the full Jira-to-PR pipeline for KAN-2 (Task 2 — Payment Schedule Icon) — fetches ticket, derives test cases via Claude, generates test code, verifies collection, commits, raises PR, updates Jira, posts PR review.

**Run command**:
```bash
python dashboard/mock_run.py --fast          # ~1 min
python dashboard/mock_run.py                 # ~3 min (normal speed)
python dashboard/mock_run.py --no-hitl       # fully unattended
```
Or click **Mock Run** on the E2E tab in the dashboard.

### 2.1 Jira

- [ ] Ticket **KAN-2** exists at `https://vikeshwiki9.atlassian.net/browse/KAN-2`
- [ ] KAN-2 status is **not** already "Done" (mock run transitions it to "In Review")
- [ ] Jira API token has `read:jira-work` + `write:jira-work` scopes
- [ ] Jira base URL in `.mcp.json` → `JIRA_URL=https://vikeshwiki9.atlassian.net`

### 2.2 GitHub (Automation Repo)

- [ ] Repo `innocito/AI-Test-Workflow` is accessible with current GitHub token
- [ ] Token has scopes: `repo` (read + write), `pull_requests` (create)
- [ ] Branch `kan-2-task-2` does **not** already exist (mock re-creates it)
  - Clean up if present: `git push origin --delete kan-2-task-2`
- [ ] PR #24 is closed/merged or the mock run will fail on duplicate (check GitHub)

### 2.3 API Spec

- [ ] No Swagger/OpenAPI spec is currently configured for RevFlow — Swagger Discovery is skipped in this demo. If one becomes available, add it to `.mcp.json` and this checklist.

### 2.4 Dashboard State (E2E tab)

- [ ] Dashboard reset: `curl -X DELETE http://localhost:8765/reset`
- [ ] No active workflow running: `curl http://localhost:8765/run/status` → `{"running": false}`
- [ ] Plans dir has no stale KAN-2 files (optional cleanup):
  ```bash
  rm -f plans/manual_tests_kan-2_*.md plans/manual_tests_kan-2_*.csv
  ```

### 2.5 HITL Gates (E2E flow has 4 checkpoints)

If demoing interactively, be ready to click in the dashboard at:
1. **Test case review** — approve the 7 derived test cases
2. **API scope** — confirm UI-only (no Swagger spec configured)
3. **Naming preview** — approve function name conventions
4. **Execution scope** — collection check only, or skip straight to commit

Use `--no-hitl` to auto-approve all if demoing speed.

---

## 3. Self-Heal Demo Checklist

Two sub-modes: **Mock Run** (scripted, always works) and **Real Webhook** (live GitHub PR → actual heal).

---

### 3A. Self-Heal — Mock Run

**What it does**: Scripted 5-stage demo — simulates a failing regression test, shows DOM inspection, calls the real `self_heal_agent.py` to heal `task_list_page.py`, verifies, raises a real heal PR on GitHub.

**Run command**:
```bash
python dashboard/self_heal_run.py --fast          # ~45 sec
python dashboard/self_heal_run.py                 # ~2 min
python dashboard/self_heal_run.py --no-hitl       # unattended
```
Or click **Mock Run** on the Self-Heal tab in the dashboard.

#### 3A.1 Task List Page Locator State

The mock uses **`grid_rows`** as the locator the agent heals.

- [ ] `pages/task_list_page.py` reads: `page.locator(".arw-grid-table__row")`
  - This is the "broken" locator the mock simulates. The agent will heal it.
  - If it was left in a broken state from a prior run: `git checkout pages/task_list_page.py`

#### 3A.2 Frontend Repo (Mock reads PR diff from GitHub)

The mock agent fetches a UI PR via GitHub API — `UI_REPO` is env-var driven and not yet set to a real repo (`self_heal_agent.py` / `self_heal_run.py` fall back to an empty string with a TODO comment):

- [ ] Set `UI_REPO` env var to the real RevFlow frontend repo once known, or expect the PR-fetch step to no-op gracefully
- [ ] GitHub token in `.mcp.json` can read that repo's PR diffs once configured

#### 3A.3 GitHub — Heal PR

- [ ] Branch `heal/ui-pr-7-locators` does **not** exist on `innocito/AI-Test-Workflow`
  - If it does: delete via GitHub MCP or `gh` CLI
- [ ] No stale heal PR open for PR #7 (check GitHub, close if present)

#### 3A.4 Dashboard State

- [ ] Dashboard reset: `curl -X DELETE http://localhost:8765/reset`
- [ ] No active run: `curl http://localhost:8765/run/status` → `{"running": false}`
- [ ] Old heal summary cleaned: `rm -f reports/heal_summary.md`

#### 3A.5 HITL Gate (1 checkpoint)

- Approve or reject the heal when prompted on the dashboard
- Use `--no-hitl` to auto-approve for speed demos

---

### 3B. Self-Heal — Real Webhook Flow

**What it does**: A real PR is pushed to the RevFlow frontend repo → GitHub webhook hits the dashboard → dashboard modal appears → user approves → `self_heal_agent.py` runs the full 7-stage pipeline live.

> **Prerequisite**: the RevFlow frontend repo and its local dev-server setup are not yet confirmed (`UI_REPO`, `UI_URL` are placeholders in `scripts/self_heal_agent.py`). Fill these in before running this sub-mode.

#### 3B.1 Webhook Configuration

- [ ] Dashboard server is reachable from the internet (or via ngrok tunnel):
  ```bash
  ngrok http 8765    # Get public URL e.g. https://abc123.ngrok.app
  ```
- [ ] GitHub webhook is configured on the RevFlow frontend repo:
  - **Payload URL**: `https://<your-tunnel>/webhook/github`
  - **Content type**: `application/json`
  - **Events**: Pull requests → Opened, Synchronize, Reopened
  - **Active**: ✅
- [ ] Verify webhook delivery works: click **Redeliver** on a past delivery in GitHub webhook settings → dashboard should receive `pr_detected` event

#### 3B.2 Frontend Repo State (Breaking the Locator)

The real heal flow requires a PR that actually breaks `.arw-grid-table__row` (or another `task_list_page.py` locator):

- [ ] Frontend repo is on `main`, clean: `git status`
- [ ] Confirm the current grid row class name (baseline)
- [ ] **To break it**: create a branch, rename the grid row CSS class, push and open PR
  ```bash
  git checkout -b demo/break-locator-grid-row
  # edit the Task List grid component's row class name
  git commit -am "refactor(task-list): rename grid row class"
  git push origin demo/break-locator-grid-row
  gh pr create --title "refactor(task-list): rename grid row class" --base main
  ```
- [ ] Confirm the PR triggers the webhook (check dashboard for modal)

#### 3B.3 RevFlow Frontend App on localhost:3000

The real agent verifies the heal against the running PR branch app:

- [ ] Frontend app is running on port 3000 with the **PR branch** code checked out
- [ ] `http://localhost:3000` loads the RevFlow Task List page
- [ ] Grid row shows the new class name

#### 3B.4 Task List Page Locator State

- [ ] `pages/task_list_page.py` has the **old** (now-broken) locator: `.arw-grid-table__row`
  - If it was already healed by a prior run: `git checkout pages/task_list_page.py`

#### 3B.5 GitHub — Heal PR

- [ ] Branch `heal/ui-pr-<N>-locators` does not exist on `innocito/AI-Test-Workflow`
- [ ] Token has `repo` write scope on `innocito/AI-Test-Workflow`

#### 3B.6 Dashboard State

- [ ] Dashboard reset: `curl -X DELETE http://localhost:8765/reset`
- [ ] No active run: `curl http://localhost:8765/run/status` → `{"running": false}`
- [ ] Old heal summary cleaned: `rm -f reports/heal_summary.md`

---

## 4. Post-Demo Reset

Run these after each demo to leave the system in a clean state for the next run.

### Automation Repo
```bash
# Restore POM to original locators
git checkout pages/task_list_page.py

# Delete heal branches (if created)
git push origin --delete heal/ui-pr-7-locators 2>/dev/null || true

# Clean generated reports
rm -f reports/heal_summary.md
```

### Dashboard
```bash
curl -X DELETE http://localhost:8765/reset
```

### GitHub (via gh CLI)
```bash
# Close any open heal PRs on automation repo
gh pr list --repo innocito/AI-Test-Workflow --state open | grep "self-heal"
# gh pr close <number> --repo innocito/AI-Test-Workflow

# Delete stale remote branches
gh api -X DELETE repos/innocito/AI-Test-Workflow/git/refs/heads/heal/ui-pr-7-locators 2>/dev/null || true
```

---

## 5. Quick Smoke Tests (Sanity Before Any Demo)

Run these in under 60 seconds to confirm all systems are live:

```bash
# 1. Dashboard health
curl http://localhost:8765/health

# 2. Webhook responds
curl -s -X POST http://localhost:8765/webhook/github \
  -H "Content-Type: application/json" \
  -d '{"action":"opened","pull_request":{"number":99,"title":"smoke test","html_url":"https://github.com/test","head":{"ref":"test-branch"}}}' 
# Expected: {"ok":true,"message":"PR #99 event broadcast to dashboard"}

# 3. No active run
curl http://localhost:8765/run/status
# Expected: {"running":false}

# 4. Jira reachable (replace with actual token from .mcp.json)
curl -s "https://vikeshwiki9.atlassian.net/rest/api/3/issue/KAN-2" \
  -u "vikesh.wiki.9@gmail.com:<JIRA_TOKEN>" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Jira OK —', d.get('fields',{}).get('summary','?'))"

# 5. RevFlow reachable and login works (manual check — SSO flow can't be curl'd)
#    Open https://revflow-dev.axgsolutions.com/ and sign in with AUTH_USERNAME/AUTH_PASSWORD

# 6. POM locator is at baseline
grep "grid_rows" pages/task_list_page.py
# Should show: page.locator(".arw-grid-table__row")
```

---

## 6. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Dashboard WebSocket drops | Server restarted or port conflict | `./start.sh` again; hard-refresh browser |
| `curl /health` refused | Server not running | `python dashboard/server/main.py` |
| Webhook not triggering modal | ngrok tunnel expired | Restart ngrok, update GitHub webhook URL |
| `claude -p` times out | Anthropic API key missing or expired | Check `ANTHROPIC_API_KEY` in `.env` |
| GitHub MCP fails to create branch | Token expired or branch already exists | Rotate token in `.mcp.json`; delete stale branch |
| Jira MCP returns 401 | Token expired | Re-generate Jira API token at `id.atlassian.com` |
| Playwright browser won't launch | Missing deps | `python3 -m playwright install chromium --with-deps` |
| Self-heal patches 0 locators | Old selector string not verbatim in POM | `git checkout pages/task_list_page.py` to restore baseline |
| RevFlow login fails in tests | `AUTH_USERNAME`/`AUTH_PASSWORD` missing or SSO flow changed | Check `.env`; re-verify the Microsoft SSO steps in `pages/login_page.py` |
| Port 8765 already in use | Previous server still running | `lsof -ti:8765 | xargs kill` |
| Port 5173 already in use | Previous Vite dev server | `lsof -ti:5173 | xargs kill` |
| `pytest` not found | Wrong Python env | Use `/opt/miniconda3/bin/pytest` explicitly |
