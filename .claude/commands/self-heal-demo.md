---
name: self-heal-demo
description: 6-stage live demo — breaks real task_list_page.py locators, auto-heals them via Playwright MCP DOM inspection, streams every step to the dashboard
tags: [self-heal, demo, playwright-mcp, dashboard, regression]
---

# Skill: Self-Heal Demo

Runs a live, client-facing demonstration of AI-driven self-healing automation.

The demo targets **real production page objects** — not dummy code. It:
1. Proves the regression suite works (baseline)
2. Injects a realistic locator decay (simulating a UI refactor)
3. Detects the failures automatically
4. Uses Playwright MCP to inspect the live DOM and discover correct selectors
5. Patches `pages/task_list_page.py` in place
6. Re-runs the regression suite to confirm healing

Every stage streams live to the dashboard at http://localhost:5173 with purple self-heal theming.

> **MCP Required**: `@playwright/mcp` (DOM inspection in Stage 4)
> **Dashboard Required**: `dashboard/server/main.py` running on port 8765

---

## Usage

```
/self-heal-demo
```

No arguments needed — everything is self-contained.

---

## Dashboard Integration

All events are **fire-and-forget** (`|| true`) except the opening health check.
The `workflow_start` event with `mode: "self_heal"` switches the pipeline sidebar to self-heal stages and applies purple theming throughout.

**Event helper**:
```bash
python dashboard/utils/client.py event --type stage_start    --stage <id> --message "<text>" 2>/dev/null || true
python dashboard/utils/client.py event --type stage_complete --stage <id> --message "<text>" --level success --data '<json>' 2>/dev/null || true
python dashboard/utils/client.py event --type stage_error    --stage <id> --message "<text>" --level error 2>/dev/null || true
python dashboard/utils/client.py event --type log            --stage <id> --message "<text>" 2>/dev/null || true
```

**HITL gate**:
```bash
python dashboard/utils/hitl_gate.py --id "<id>" --message "<question>" --context '<json>' 2>/dev/null || true
```
`hitl_gate.py` exits 0 (Approve / Proceed) or 1 (Reject / Abort). Default to continue on failure (`|| true`).

**Self-heal stage IDs**: `baseline_run`, `inject_decay`, `detect_failure`, `inspect_dom`, `apply_heal`, `verify_heal`

**`locator_diff` event** (the visual "wow moment" — renders as an animated purple diff in the log stream):
```bash
python dashboard/utils/client.py event \
  --type locator_diff \
  --stage apply_heal \
  --message "Healed: <selector_name>" \
  --data '{"file":"pages/task_list_page.py","line":<N>,"selector_name":"<name>","broken":"<broken_selector>","healed":"<healed_selector>"}' \
  2>/dev/null || true
```

---

## Pre-flight

```bash
# ✅ Dashboard health check — REQUIRED (no || true — must pass before demo starts)
python dashboard/utils/client.py check
```

If the health check fails, stop and tell the user:
> "Dashboard is not running. Start it with `./dashboard/start.sh` before running `/self-heal-demo`."

Also verify the regression test file and break script exist:
```bash
ls tests/ui/test_task_list_regression.py scripts/break_locators.py
```

If either is missing, stop with a clear error message.

---

## Workflow Start

Emit the workflow start event with `mode: "self_heal"` to switch the dashboard to self-heal pipeline view:

```bash
python dashboard/utils/client.py event \
  --type workflow_start \
  --message "Self-Heal Demo — task_list_page.py regression cycle" \
  --data '{"mode":"self_heal"}' \
  2>/dev/null || true
```

---

## Stage 1 — Baseline Run (`baseline_run`)

**Goal**: Confirm all 2 regression tests pass before any decay is injected.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage baseline_run \
  --message "Running Task List regression suite (baseline)..." 2>/dev/null || true
```

Run the regression suite (no parallelism — keep output readable for demo):
```bash
python -m pytest tests/ui/test_task_list_regression.py -v -p no:xdist \
  --tb=short 2>&1 | tee /tmp/baseline_run.txt
BASELINE_EXIT=${PIPESTATUS[0]}
```

Parse the summary line:
```bash
PASS_COUNT=$(grep -E "passed" /tmp/baseline_run.txt | tail -1 | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+")
FAIL_COUNT=$(grep -E "failed" /tmp/baseline_run.txt | tail -1 | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
```

Emit a log line per test result so the stream shows individual test names:
```bash
grep -E "PASSED|FAILED" /tmp/baseline_run.txt | while IFS= read -r line; do
  LEVEL="success"
  [[ "$line" == *FAILED* ]] && LEVEL="error"
  TEST_NAME=$(echo "$line" | awk '{print $1}')
  python dashboard/utils/client.py event --type log --stage baseline_run \
    --message "$line" --level "$LEVEL" 2>/dev/null || true
done
```

**If baseline fails** (any test failed before decay was injected):
```bash
python dashboard/utils/client.py event --type stage_error --stage baseline_run \
  --message "Baseline failed — $FAIL_COUNT test(s) already broken. Fix before running self-heal demo." \
  --level error 2>/dev/null || true
```
Stop the demo. Tell the user the regression suite is not in a clean state and to run `/debug-test` first.

**If baseline passes**:
```bash
python dashboard/utils/client.py event --type stage_complete --stage baseline_run \
  --message "Baseline confirmed — $PASS_COUNT/2 tests passing ✓" \
  --level success \
  --data "{\"passed\":$PASS_COUNT,\"failed\":0}" \
  2>/dev/null || true
```

### ⏸ HITL CHECKPOINT — Confirm Decay Injection

```bash
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "baseline-confirmed" \
  --message "Baseline confirmed — $PASS_COUNT/2 tests passing. Inject locator decay into task_list_page.py to begin the self-heal cycle?" \
  --context "{\"passed\":\"$PASS_COUNT\",\"target_file\":\"pages/task_list_page.py\",\"locators_to_break\":\"grid_rows, grid_cells\"}" \
  2>/dev/null || true)
HITL_EXIT=$?
```

- **Exit 0 (Proceed)**: continue to Stage 2.
- **Exit 1 (Abort)**: emit `workflow_complete` with `{"mode":"self_heal","aborted":true}` and stop.

---

## Stage 2 — Inject Decay (`inject_decay`)

**Goal**: Break two locators in `task_list_page.py` to simulate a UI refactor that invalidated selectors.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage inject_decay \
  --message "Injecting locator decay into pages/task_list_page.py..." 2>/dev/null || true
```

Run the break script:
```bash
python scripts/break_locators.py --break-locators 2>&1 | tee /tmp/break_output.txt
BREAK_EXIT=${PIPESTATUS[0]}
```

If the script fails (non-zero exit), emit `stage_error` and stop:
```bash
python dashboard/utils/client.py event --type stage_error --stage inject_decay \
  --message "break_locators.py failed — $(tail -1 /tmp/break_output.txt)" --level error 2>/dev/null || true
```

On success, emit one log line per broken locator to make the decay visible in the stream:
```bash
python dashboard/utils/client.py event --type log --stage inject_decay \
  --message "  ✗ grid_rows → .arw-broken-grid-table__row" \
  --level error 2>/dev/null || true

python dashboard/utils/client.py event --type log --stage inject_decay \
  --message "  ✗ grid_cells → .arw-broken-grid-table__cell" \
  --level error 2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type stage_complete --stage inject_decay \
  --message "Decay injected — 2 locators broken in task_list_page.py" \
  --level warning \
  --data '{"broken_locators":["grid_rows","grid_cells"]}' \
  2>/dev/null || true
```

---

## Stage 3 — Detect Failure (`detect_failure`)

**Goal**: Re-run regression suite against the broken selectors. Expect failures. Capture exactly which tests and selectors failed.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage detect_failure \
  --message "Re-running regression suite against broken selectors..." 2>/dev/null || true
```

```bash
python -m pytest tests/ui/test_task_list_regression.py -v -p no:xdist \
  --tb=short 2>&1 | tee /tmp/detect_run.txt
DETECT_EXIT=${PIPESTATUS[0]}
```

Parse results:
```bash
FAIL_COUNT=$(grep -E "failed" /tmp/detect_run.txt | tail -1 | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
PASS_COUNT=$(grep -E "passed" /tmp/detect_run.txt | tail -1 | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
```

Stream each test result line:
```bash
grep -E "PASSED|FAILED" /tmp/detect_run.txt | while IFS= read -r line; do
  LEVEL="success"
  [[ "$line" == *FAILED* ]] && LEVEL="error"
  python dashboard/utils/client.py event --type log --stage detect_failure \
    --message "$line" --level "$LEVEL" 2>/dev/null || true
done
```

**If no failures detected** (decay script may have failed silently):
```bash
python dashboard/utils/client.py event --type stage_error --stage detect_failure \
  --message "Expected failures but all tests passed — decay may not have been applied correctly." \
  --level error 2>/dev/null || true
```
Stop demo and advise user to check `pages/task_list_page.py` manually.

**If failures detected as expected**:
```bash
python dashboard/utils/client.py event --type stage_error --stage detect_failure \
  --message "$FAIL_COUNT test(s) failed — broken selectors confirmed" \
  --level error \
  --data "{\"failed\":$FAIL_COUNT,\"passed\":$PASS_COUNT}" \
  2>/dev/null || true
```
> Note: `stage_error` here is intentional — it's the expected "decay detected" signal that makes the demo dramatic.

### ⏸ HITL CHECKPOINT — Proceed with Self-Heal

```bash
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "failure-detected" \
  --message "$FAIL_COUNT test(s) failed due to broken locators. Proceed with AI self-heal? (Playwright MCP will inspect the live DOM and patch task_list_page.py)" \
  --context "{\"failed\":\"$FAIL_COUNT\",\"broken_selectors\":\"grid_rows, grid_cells\"}" \
  2>/dev/null || true)
HITL_EXIT=$?
```

- **Exit 0 (Proceed)**: continue to Stage 4.
- **Exit 1 (Abort)**: restore locators and stop cleanly:
  ```bash
  python scripts/break_locators.py --restore 2>/dev/null || true
  python dashboard/utils/client.py event --type workflow_complete \
    --message "Demo aborted — locators restored" \
    --data '{"mode":"self_heal","aborted":true}' 2>/dev/null || true
  ```

---

## Stage 4 — Inspect DOM (`inspect_dom`)

**Goal**: Use Playwright MCP to navigate to the live Task List page and discover the correct selectors by inspecting the real DOM. This is the AI "seeing" the broken UI and figuring out the fix.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage inspect_dom \
  --message "Launching browser — inspecting live DOM at revflow-dev.axgsolutions.com..." 2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  → Playwright MCP: navigating to Task List page..." 2>/dev/null || true
```

**Use Playwright MCP tools** (these are real MCP tool calls, not bash):

1. Log in via Microsoft SSO and navigate to the Task List page:
   - Tool: `mcp__playwright__browser_navigate`
   - URL: `https://revflow-dev.axgsolutions.com/tasks` (login flow: click "Sign in with Microsoft", complete the Azure AD prompts using `AUTH_USERNAME`/`AUTH_PASSWORD` from `.env`)

2. Wait for the page to load and capture a DOM snapshot:
   - Tool: `mcp__playwright__browser_snapshot`
   - This returns the accessibility tree / DOM structure

3. Analyse the snapshot to find:
   - The grid row wrapper — look for `<div>` elements with a class containing "grid" and "row", `role="link"`, wrapping resident/payer case data
   - The grid cell wrapper — look for `<div>` elements with a class containing "grid" and "cell" nested inside each row

4. If the snapshot is not conclusive, use targeted evaluation:
   - Tool: `mcp__playwright__browser_evaluate`
   - Script: `[...document.querySelectorAll('[class*="grid"][class*="row"]')].map(e => e.className)` to find row container class names
   - Script: `[...document.querySelectorAll('[class*="grid"][class*="cell"]')].map(e => e.className)` to find cell container class names

5. Close the browser when done:
   - Tool: `mcp__playwright__browser_close`

Emit discovery results to the log stream as you find them:
```bash
# After identifying the correct grid row class:
CORRECT_ROW_SELECTOR=".arw-grid-table__row"  # replace with actual discovered value
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  ✓ Found grid row: $CORRECT_ROW_SELECTOR" \
  --level success 2>/dev/null || true

# After identifying the correct grid cell class:
CORRECT_CELL_SELECTOR=".arw-grid-table__cell"  # replace with actual discovered value
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  ✓ Found grid cell: $CORRECT_CELL_SELECTOR" \
  --level success 2>/dev/null || true
```

Store the discovered selectors as variables for Stage 5:
- `$CORRECT_ROW_SELECTOR` — the real CSS class or selector for the grid row
- `$CORRECT_CELL_SELECTOR` — the real CSS class or selector for the grid cell

```bash
python dashboard/utils/client.py event --type stage_complete --stage inspect_dom \
  --message "DOM inspection complete — correct selectors identified" \
  --level success \
  --data "{\"row_selector\":\"$CORRECT_ROW_SELECTOR\",\"cell_selector\":\"$CORRECT_CELL_SELECTOR\"}" \
  2>/dev/null || true
```

---

## Stage 5 — Apply Heal (`apply_heal`)

**Goal**: Patch `pages/task_list_page.py` with the correct selectors discovered in Stage 4. Emit a `locator_diff` event for each fix so the dashboard renders the animated purple diff block.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage apply_heal \
  --message "Patching pages/task_list_page.py with healed selectors..." 2>/dev/null || true
```

**Read the current state of `task_list_page.py`** (use the Read tool, not bash cat).

Find the line numbers of the two broken locators. They will contain the broken strings injected by `break_locators.py`:
- `.arw-broken-grid-table__row`
- `.arw-broken-grid-table__cell`

**Fix 1 — grid_rows**:

Use the Edit tool to replace the broken selector with `$CORRECT_ROW_SELECTOR`.

After applying the edit, emit the `locator_diff` event:
```bash
LINE_NUM=<line number from your Read>
python dashboard/utils/client.py event \
  --type locator_diff \
  --stage apply_heal \
  --message "Healed: grid_rows" \
  --data "{\"file\":\"pages/task_list_page.py\",\"line\":$LINE_NUM,\"selector_name\":\"grid_rows\",\"broken\":\".arw-broken-grid-table__row\",\"healed\":\"$CORRECT_ROW_SELECTOR\"}" \
  2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type log --stage apply_heal \
  --message "  ✓ grid_rows healed on line $LINE_NUM" --level success 2>/dev/null || true
```

**Fix 2 — grid_cells**:

Use the Edit tool to replace `.arw-broken-grid-table__cell` with `$CORRECT_CELL_SELECTOR`.

After applying the edit, emit the `locator_diff` event:
```bash
LINE_NUM_2=<line number from your Read>
python dashboard/utils/client.py event \
  --type locator_diff \
  --stage apply_heal \
  --message "Healed: grid_cells" \
  --data "{\"file\":\"pages/task_list_page.py\",\"line\":$LINE_NUM_2,\"selector_name\":\"grid_cells\",\"broken\":\".arw-broken-grid-table__cell\",\"healed\":\"$CORRECT_CELL_SELECTOR\"}" \
  2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type log --stage apply_heal \
  --message "  ✓ grid_cells healed on line $LINE_NUM_2" --level success 2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type stage_complete --stage apply_heal \
  --message "2 locators healed in pages/task_list_page.py" \
  --level success \
  --data '{"healed_count":2,"file":"pages/task_list_page.py"}' \
  2>/dev/null || true
```

---

## Stage 6 — Verify Heal (`verify_heal`)

**Goal**: Re-run the full regression suite. All 2 tests must pass to confirm the heal was successful.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage verify_heal \
  --message "Re-running regression suite to verify healing..." 2>/dev/null || true
```

```bash
python -m pytest tests/ui/test_task_list_regression.py -v -p no:xdist \
  --tb=short 2>&1 | tee /tmp/verify_run.txt
VERIFY_EXIT=${PIPESTATUS[0]}
```

Parse results:
```bash
VERIFY_PASS=$(grep -E "passed" /tmp/verify_run.txt | tail -1 | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
VERIFY_FAIL=$(grep -E "failed" /tmp/verify_run.txt | tail -1 | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
```

Stream each test result:
```bash
grep -E "PASSED|FAILED" /tmp/verify_run.txt | while IFS= read -r line; do
  LEVEL="success"
  [[ "$line" == *FAILED* ]] && LEVEL="error"
  python dashboard/utils/client.py event --type log --stage verify_heal \
    --message "$line" --level "$LEVEL" 2>/dev/null || true
done
```

**If any test still fails**:
```bash
python dashboard/utils/client.py event --type stage_error --stage verify_heal \
  --message "Heal incomplete — $VERIFY_FAIL test(s) still failing. Manual inspection required." \
  --level error \
  --data "{\"passed\":$VERIFY_PASS,\"failed\":$VERIFY_FAIL}" \
  2>/dev/null || true

python dashboard/utils/client.py event --type workflow_complete \
  --message "Self-heal cycle incomplete" \
  --data '{"mode":"self_heal","success":false}' 2>/dev/null || true
```
Restore original locators as safety net:
```bash
python scripts/break_locators.py --restore 2>/dev/null || true
```
Stop and tell the user which tests are still failing so they can investigate manually.

**If all tests pass**:

Generate a brief heal summary and save it:
```bash
SUMMARY_PATH="reports/heal-summary-$(date +%Y%m%d-%H%M%S).md"
mkdir -p reports
cat > "$SUMMARY_PATH" << EOF
# Self-Heal Summary

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Target file**: pages/task_list_page.py
**Locators healed**: 2 (grid_rows, grid_cells)
**Regression tests**: $VERIFY_PASS/2 passing
**DOM inspection**: Live revflow-dev.axgsolutions.com

## Healed Selectors

| Locator | Broken | Healed |
|---------|--------|--------|
| grid_rows | .arw-broken-grid-table__row | $CORRECT_ROW_SELECTOR |
| grid_cells | .arw-broken-grid-table__cell | $CORRECT_CELL_SELECTOR |
EOF
```

```bash
python dashboard/utils/client.py event --type stage_complete --stage verify_heal \
  --message "All $VERIFY_PASS/2 tests passing — self-heal complete ✓" \
  --level success \
  --data "{\"passed\":$VERIFY_PASS,\"failed\":0,\"artifacts\":[{\"label\":\"Heal Summary\",\"type\":\"markdown\",\"path\":\"$SUMMARY_PATH\"}]}" \
  2>/dev/null || true
```

---

## Workflow Complete

```bash
python dashboard/utils/client.py event \
  --type workflow_complete \
  --message "Self-heal cycle complete — $VERIFY_PASS/2 regression tests passing" \
  --data '{"mode":"self_heal","success":true}' \
  2>/dev/null || true
```

Tell the user:
> **Self-heal demo complete.**
> - 2 locators in `pages/task_list_page.py` were broken and healed automatically
> - All 2 regression tests are passing
> - Heal summary saved to `$SUMMARY_PATH`
> - Dashboard at http://localhost:5173 shows the full cycle with locator diffs

---

## Error Recovery

At any point if the demo aborts unexpectedly, restore `task_list_page.py` to its clean state:
```bash
python scripts/break_locators.py --restore 2>/dev/null || true
```

This is safe to run multiple times (idempotent — no-ops if locators are already correct).

---

## Wiring into e2e-workflow

When the e2e-workflow's **HITL Checkpoint 2 — Test Failure Gate** fires (tests failed during `run_tests` stage), offer self-heal as a third option:

> - **[C] Continue** — commit and raise PR as draft
> - **[F] Fix** — diagnose and fix failures manually (`/debug-test`)
> - **[H] Self-Heal** — run `/self-heal-demo` to demonstrate AI-driven locator healing

If the user selects **Self-Heal**, the e2e-workflow pauses, `/self-heal-demo` runs, and on success the e2e-workflow resumes from Stage 6 (commit & push) with `$DRAFT = false`.
