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

All four are loaded automatically from `.mcp.json` when `claude` runs. Verify tokens are live:

| MCP | Quick Check |
|-----|-------------|
| **GitHub** | `gh auth status` or check `.mcp.json` token hasn't expired |
| **Jira** | `curl -u email:token https://innocito.atlassian.net/rest/api/3/myself` → 200 |
| **Playwright** | `npx @playwright/mcp --version` (should print without error) |
| **Swagger** | `curl https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs` → JSON |

- [ ] GitHub token valid (check `.mcp.json` → `GITHUB_PERSONAL_ACCESS_TOKEN`)
- [ ] Jira reachable and token valid
- [ ] Playwright MCP can launch a browser: `npx playwright open about:blank` — opens and closes cleanly
- [ ] Swagger API is reachable (no VPN / cert issues)
- [ ] `ANTHROPIC_API_KEY` set in `.env` (needed for `claude -p` calls inside self-heal agent)

### 1.3 Ports

- [ ] Port **8765** is free (or already held by the dashboard server)
- [ ] Port **5173** is free (or already held by the Vite client)
- [ ] If doing the real self-heal webhook flow: port **3000** needs the consumer app running

### 1.4 Repos & Git State

- [ ] Automation repo is on `main`, clean: `git status` → nothing to commit
- [ ] Latest main pulled: `git pull origin main`
- [ ] `claude` CLI is in PATH: `which claude`
- [ ] `pytest` is in PATH and resolves to the right venv: `which pytest`

---

## 2. E2E Workflow Demo Checklist

**What it does**: Simulates the full Jira-to-PR pipeline for JP-1 (Pre Payment Booking Flow) — fetches ticket, derives test cases via Claude, generates test code, runs AC1 tests, commits, raises PR, updates Jira, posts PR review.

**Run command**:
```bash
python dashboard/mock_run.py --fast          # ~1 min
python dashboard/mock_run.py                 # ~3 min (normal speed)
python dashboard/mock_run.py --no-hitl       # fully unattended
```
Or click **Mock Run** on the E2E tab in the dashboard.

### 2.1 Jira

- [ ] Ticket **JP-1** exists at `https://innocito.atlassian.net/browse/JP-1`
- [ ] JP-1 status is **not** already "Done" (mock run transitions it to "In Review")
- [ ] Jira API token has `read:jira-work` + `write:jira-work` scopes
- [ ] Jira base URL in `.mcp.json` → `JIRA_URL=https://innocito.atlassian.net`

### 2.2 GitHub (Automation Repo)

- [ ] Repo `innocito/AI-Test-Workflow` is accessible with current GitHub token
- [ ] Token has scopes: `repo` (read + write), `pull_requests` (create)
- [ ] Branch `jp-1-pre-payment-booking-flow-v17` does **not** already exist (mock re-creates it)
  - Clean up if present: `git push origin --delete jp-1-pre-payment-booking-flow-v17`
- [ ] PR #17 is closed/merged or the mock run will fail on duplicate (check GitHub)

### 2.3 Swagger API

- [ ] `https://beta.drivejoulez.com:8443` is reachable
- [ ] OpenAPI spec returns valid JSON: `curl -k https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs | head -5`

### 2.4 Dashboard State (E2E tab)

- [ ] Dashboard reset: `curl -X DELETE http://localhost:8765/reset`
- [ ] No active workflow running: `curl http://localhost:8765/run/status` → `{"running": false}`
- [ ] Plans dir has no stale JP-1 files (optional cleanup):
  ```bash
  rm -f plans/manual_tests_jp-1_*.md plans/manual_tests_jp-1_*.csv plans/postman_jp-1_*.json
  ```

### 2.5 HITL Gates (E2E flow has 5 checkpoints)

If demoing interactively, be ready to click in the dashboard at:
1. **Test case review** — approve the 27 derived test cases
2. **API scope** — include or skip API tests
3. **Postman scope** — include or skip Postman export
4. **Naming preview** — approve function name conventions
5. **Execution scope** — choose AC1 only, full suite, or skip

Use `--no-hitl` to auto-approve all if demoing speed.

---

## 3. Self-Heal Demo Checklist

Two sub-modes: **Mock Run** (scripted, always works) and **Real Webhook** (live GitHub PR → actual heal).

---

### 3A. Self-Heal — Mock Run

**What it does**: Scripted 5-stage demo — simulates 2 failing regression tests, shows DOM inspection, calls the real `self_heal_agent.py` to heal `booking_page.py`, verifies, raises a real heal PR on GitHub.

**Run command**:
```bash
python dashboard/self_heal_run.py --fast          # ~45 sec
python dashboard/self_heal_run.py                 # ~2 min
python dashboard/self_heal_run.py --no-hitl       # unattended
```
Or click **Mock Run** on the Self-Heal tab in the dashboard.

#### 3A.1 Booking Page Locator State

The mock uses **`pickup_location_input`** as the only locator the agent heals.

- [ ] `pages/booking_page.py` line 14 reads: `page.locator("input[placeholder='Location']")`
  - This is the "broken" locator the mock simulates. The agent will heal it.
  - If it already shows `"Pickup Location"` from a prior run: `git checkout pages/booking_page.py`

#### 3A.2 Consumer Repo (Mock reads PR diff from GitHub)

The mock agent fetches PR #7 from `innocito/consumer` via GitHub API:

- [ ] PR #7 exists on `innocito/consumer` and is accessible (mock hardcodes it)
- [ ] GitHub token in `.mcp.json` can read `innocito/consumer` PR diffs

#### 3A.3 GitHub — Heal PR

- [ ] Branch `heal/ui-pr-7-locators` does **not** exist on `innocito/AI-Test-Workflow`
  - If it does: `git push innocito/AI-Test-Workflow --delete heal/ui-pr-7-locators` (via GitHub MCP or gh CLI)
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

**What it does**: A real PR is pushed to the consumer repo → GitHub webhook hits the dashboard → dashboard modal appears → user approves → `self_heal_agent.py` runs the full 7-stage pipeline live.

#### 3B.1 Webhook Configuration

- [ ] Dashboard server is reachable from the internet (or via ngrok tunnel):
  ```bash
  ngrok http 8765    # Get public URL e.g. https://abc123.ngrok.app
  ```
- [ ] GitHub webhook is configured on `innocito/consumer`:
  - **Payload URL**: `https://<your-tunnel>/webhook/github`
  - **Content type**: `application/json`
  - **Events**: Pull requests → Opened, Synchronize, Reopened
  - **Active**: ✅
- [ ] Verify webhook delivery works: click **Redeliver** on a past delivery in GitHub webhook settings → dashboard should receive `pr_detected` event

#### 3B.2 Consumer Repo State (Breaking the Locator)

The real heal flow requires a PR that actually breaks `input[placeholder='Location']`:

- [ ] Consumer repo is on `main`, clean: `cd /Users/eswarprasadkona/Desktop/code/Innocito/joulez/consumer && git status`
- [ ] `PickupLocation.js` line 456 currently reads `placeholder="Location"` (baseline)
- [ ] **To break it**: create a branch, change `placeholder="Location"` → `placeholder="Pickup Location"`, push and open PR
  ```bash
  git checkout -b demo/break-locator-pickup
  # edit PickupLocation.js line 456
  git commit -am "refactor(search): update pickup placeholder text"
  git push origin demo/break-locator-pickup
  gh pr create --title "refactor(search): update pickup placeholder" --base main
  ```
- [ ] Confirm the PR triggers the webhook (check dashboard for modal)

#### 3B.3 Consumer App on localhost:3000

The real agent verifies the heal against the running PR branch app:

- [ ] Consumer app is running on port 3000 with the **PR branch** code checked out:
  ```bash
  cd /Users/eswarprasadkona/Desktop/code/Innocito/joulez/consumer
  git checkout demo/break-locator-pickup
  npm install && npm start    # or yarn start
  ```
- [ ] `http://localhost:3000` loads the Joulez homepage
- [ ] Pickup input field shows the new placeholder (`Pickup Location`)

#### 3B.4 Booking Page Locator State

- [ ] `pages/booking_page.py` has the **old** (now-broken) locator: `input[placeholder='Location']`
  - If it was already healed by a prior run: `git checkout pages/booking_page.py`

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
git checkout pages/booking_page.py

# Delete heal branches (if created)
git push origin --delete heal/ui-pr-7-locators 2>/dev/null || true

# Clean generated reports
rm -f reports/heal_summary.md
```

### Dashboard
```bash
curl -X DELETE http://localhost:8765/reset
```

### Consumer Repo (after webhook demo)
```bash
cd /Users/eswarprasadkona/Desktop/code/Innocito/joulez/consumer
git checkout main
# Close/delete the demo PR on GitHub if still open
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

# 4. Swagger API reachable
curl -sk https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs | python3 -c "import sys,json; d=json.load(sys.stdin); print('Swagger OK —', d.get('info',{}).get('title','?'))"

# 5. Jira reachable (replace with actual token from .mcp.json)
curl -s "https://innocito.atlassian.net/rest/api/3/issue/JP-1" \
  -u "eswarprasad.kona@innocito.com:<JIRA_TOKEN>" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Jira OK —', d.get('fields',{}).get('summary','?'))"

# 6. POM locator is at baseline
grep "pickup_location_input" pages/booking_page.py
# Should show: page.locator("input[placeholder='Location']")
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
| Self-heal patches 0 locators | Old selector string not verbatim in POM | `git checkout pages/booking_page.py` to restore baseline |
| Port 8765 already in use | Previous server still running | `lsof -ti:8765 | xargs kill` |
| Port 5173 already in use | Previous Vite dev server | `lsof -ti:5173 | xargs kill` |
| Swagger MCP returns 0 endpoints | API spec unreachable | Check VPN / network; verify `beta.drivejoulez.com:8443` is up |
| `pytest` not found | Wrong Python env | Use `/opt/miniconda3/bin/pytest` explicitly |
