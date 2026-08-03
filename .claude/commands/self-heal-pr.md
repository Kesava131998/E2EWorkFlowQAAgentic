---
name: self-heal-pr
description: Full self-healing regression cycle — runs baseline, detects PR-triggered locator failures, inspects DOM via Playwright MCP, calls Claude to reason new selectors, patches the POM, verifies, and raises a heal PR.
tags: [self-heal, pr, github, regression, playwright, mcp, orchestration]
---

# Skill: Self-Heal PR

Runs the complete locator self-heal lifecycle from a single command.
Mirrors the depth of `/e2e-workflow` — every stage uses real tools.

> **MCP Required**: GitHub MCP (`mcp__github__*`) + Playwright MCP (`mcp__playwright__*`)
> **Dashboard**: Stream events to http://localhost:5173 via `dashboard/utils/client.py`

---

## Usage

```
/self-heal-pr [UI_PR_NUMBER]
```

If `UI_PR_NUMBER` is omitted, look up the latest open PR on the frontend repo automatically.

---

## Dashboard Integration

Post events at every stage boundary — fire-and-forget, workflow continues even if server is down.

```bash
# Stage start
python dashboard/utils/client.py event --type stage_start  --stage <id> --message "<text>" 2>/dev/null || true
# Stage complete
python dashboard/utils/client.py event --type stage_complete --stage <id> --message "<text>" --level success --data '<json>' 2>/dev/null || true
# Stage error
python dashboard/utils/client.py event --type stage_error --stage <id> --message "<text>" --level error 2>/dev/null || true
# Log line
python dashboard/utils/client.py event --type log --stage <id> --message "<text>" 2>/dev/null || true
# Log error line
python dashboard/utils/client.py event --type log --stage <id> --message "<text>" --level error 2>/dev/null || true
# Log success line
python dashboard/utils/client.py event --type log --stage <id> --message "<text>" --level success 2>/dev/null || true

# AI activity (ClaudePane) — use heredoc for multi-line content
python dashboard/utils/ai_event.py --phase <phase> --stage apply_heal << 'EOF'
<content>
EOF
2>/dev/null || true
```

**HITL gate** (blocks until the user responds in the browser):
```bash
python dashboard/utils/hitl_gate.py --id "<checkpoint-id>" --message "<question>" --context '<json>' 2>/dev/null || true
# exits 0 = Approve, 1 = Reject. Default to continue on error.
```

**Self-heal stage IDs** (must match exactly):
`baseline_run`, `inject_decay`, `detect_failure`, `inspect_dom`, `apply_heal`, `verify_heal`, `raise_heal_pr`

---

## Runtime Context Resolution

Resolve all values once before any stage runs:

```bash
# Automation repo (this repo)
REMOTE=$(git remote get-url origin)
# e.g. https://github.com/innocito/AI-Test-Workflow.git
AUTO_OWNER="innocito"
AUTO_REPO="AI-Test-Workflow"

# RevFlow frontend repo (where UI PRs come from) — TODO: confirm the real repo once known
UI_OWNER="${UI_OWNER:-}"
UI_REPO="${UI_REPO:-}"

# Heal branch naming
HEAL_BRANCH="heal/ui-pr-${UI_PR_NUMBER}-locators"

# POM file to patch
POM_FILE="pages/task_list_page.py"
```

---

## Workflow Start

Post this **before Stage 1** to make the dashboard switch to the self-heal pipeline view:

```bash
python dashboard/utils/client.py event \
  --type workflow_start \
  --message "Self-Heal: UI PR #${UI_PR_NUMBER}" \
  --data "{\"mode\":\"self_heal\",\"ui_pr\":\"https://github.com/${UI_OWNER}/${UI_REPO}/pull/${UI_PR_NUMBER}\"}" \
  2>/dev/null || true
```

---

## Stage 1 — Baseline Run (`baseline_run`)

**Goal**: Confirm all regression tests pass before any PR changes are applied.

```bash
python dashboard/utils/client.py event --type stage_start --stage baseline_run \
  --message "Running baseline regression suite…" 2>/dev/null || true

python dashboard/utils/client.py event --type log --stage baseline_run \
  --message "pytest tests/ -k 'regression' -v --timeout=30" 2>/dev/null || true
```

Run the regression suite:
```bash
pytest tests/ -k "regression" -v --timeout=30 2>&1 | tee /tmp/baseline_result.txt
BASELINE_EXIT=$?
```

Parse the result and log it:
```bash
# Extract summary line
SUMMARY=$(grep -E "passed|failed|error" /tmp/baseline_result.txt | tail -1 || echo "No test summary found")
python dashboard/utils/client.py event --type log --stage baseline_run \
  --message "${SUMMARY}" --level success 2>/dev/null || true
```

If baseline fails (exit code != 0):
```bash
python dashboard/utils/client.py event --type stage_error --stage baseline_run \
  --message "Baseline already failing — fix existing failures before running self-heal" \
  2>/dev/null || true
```
Stop and tell the user to fix existing failures before proceeding.

On success:
```bash
python dashboard/utils/client.py event --type stage_complete --stage baseline_run \
  --message "Baseline passed ✓" --level success \
  --data '{"passed":true}' 2>/dev/null || true
```

---

## Stage 2 — PR Detected (`inject_decay`)

**Goal**: Fetch the UI PR diff to understand what changed in the frontend.

```bash
python dashboard/utils/client.py event --type stage_start --stage inject_decay \
  --message "Fetching UI PR #${UI_PR_NUMBER} diff from ${UI_OWNER}/${UI_REPO}…" 2>/dev/null || true
```

Use **GitHub MCP** to get the PR details and changed files:

```
mcp__github__get_pull_request(owner=UI_OWNER, repo=UI_REPO, pull_number=UI_PR_NUMBER)
mcp__github__get_pull_request_files(owner=UI_OWNER, repo=UI_REPO, pull_number=UI_PR_NUMBER)
```

Log each changed file to the dashboard:
```bash
python dashboard/utils/client.py event --type log --stage inject_decay \
  --message "PR #${UI_PR_NUMBER}: <PR_TITLE>" 2>/dev/null || true
python dashboard/utils/client.py event --type log --stage inject_decay \
  --message "Branch: <PR_BRANCH>  |  Base: main" 2>/dev/null || true
# For each changed file:
python dashboard/utils/client.py event --type log --stage inject_decay \
  --message "  Changed: <filename>  (+N / -M lines)" 2>/dev/null || true
```

Store the PR diff summary in a shell variable `PR_DIFF_SUMMARY` — you will need it in Stage 5.

```bash
python dashboard/utils/client.py event --type stage_complete --stage inject_decay \
  --message "PR #${UI_PR_NUMBER} — <N> files changed" --level success \
  --data "{\"pr_title\":\"<PR_TITLE>\",\"files_changed\":<N>}" \
  2>/dev/null || true
```

---

## Stage 3 — Detect Failures (`detect_failure`)

**Goal**: Run regression tests and capture which ones fail and what locators they use.

```bash
python dashboard/utils/client.py event --type stage_start --stage detect_failure \
  --message "Running regression suite against PR changes…" 2>/dev/null || true

python dashboard/utils/client.py event --type log --stage detect_failure \
  --message "pytest tests/ -k 'regression' -v --timeout=30" 2>/dev/null || true
```

Run regression:
```bash
pytest tests/ -k "regression" -v --timeout=30 2>&1 | tee /tmp/regression_result.txt
REGRESSION_EXIT=$?
```

Parse failures from the output:
```bash
# Extract FAILED lines
grep "FAILED" /tmp/regression_result.txt | while read line; do
  python dashboard/utils/client.py event --type log --stage detect_failure \
    --message "  ${line}" --level error 2>/dev/null || true
done
```

If no failures (exit 0):
```bash
python dashboard/utils/client.py event --type log --stage detect_failure \
  --message "No test failures — locators may already be compatible with this PR." \
  --level success 2>/dev/null || true
python dashboard/utils/client.py event --type stage_complete --stage detect_failure \
  --message "0 failures — nothing to heal" --level success 2>/dev/null || true
```
Tell the user and stop.

If failures found, extract broken locator information from the test output and POM file. Store as `BROKEN_LOCATORS_JSON` (a JSON array of `{id, old_locator, error}`).

```bash
# Log summary
FAIL_COUNT=$(grep -c "FAILED" /tmp/regression_result.txt || echo 0)
python dashboard/utils/client.py event --type log --stage detect_failure \
  --message "${FAIL_COUNT} tests failed — locator decay detected. Invoking self-heal…" \
  --level warning 2>/dev/null || true

python dashboard/utils/client.py event --type stage_complete --stage detect_failure \
  --message "${FAIL_COUNT} tests FAILED — self-heal triggered" --level success \
  --data "{\"failed\":${FAIL_COUNT},\"passed\":0}" 2>/dev/null || true
```

---

## HITL Gate — Approve Self-Heal

```bash
python dashboard/utils/hitl_gate.py \
  --id "approve-heal" \
  --message "${FAIL_COUNT} regression tests failed after UI PR #${UI_PR_NUMBER}. Approve to run self-heal agent?" \
  --context "{\"ui_pr\":\"https://github.com/${UI_OWNER}/${UI_REPO}/pull/${UI_PR_NUMBER}\",\"failed_tests\":${FAIL_COUNT}}" \
  2>/dev/null || true
HITL_EXIT=$?

if [ $HITL_EXIT -ne 0 ]; then
  python dashboard/utils/client.py event --type log --stage detect_failure \
    --message "Self-heal rejected by operator." --level warning 2>/dev/null || true
  # Stop workflow
fi
```

---

## Stage 4 — Inspect DOM (`inspect_dom`)

**Goal**: Use Playwright MCP to get a live DOM snapshot of the elements that are failing.

```bash
python dashboard/utils/client.py event --type stage_start --stage inspect_dom \
  --message "Playwright inspecting live DOM…" 2>/dev/null || true
```

Use **Playwright MCP** to navigate to the application and snapshot the DOM:

```
mcp__playwright__browser_navigate(url="https://revflow-dev.axgsolutions.com/tasks")
mcp__playwright__browser_snapshot()
```

Note: RevFlow requires Microsoft Azure AD SSO login first (click "Sign in with Microsoft", then
complete the Microsoft-hosted email/password prompts using `AUTH_USERNAME`/`AUTH_PASSWORD` from `.env`)
before the Task List page is reachable.

Log what you find:
```bash
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "Navigating to https://revflow-dev.axgsolutions.com/tasks…" 2>/dev/null || true
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "Page loaded ✓ — taking accessibility snapshot of search area" \
  --level success 2>/dev/null || true
```

For each broken locator, search the snapshot for the element:
```bash
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  → Scanning for element matching: <OLD_LOCATOR>…" 2>/dev/null || true
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  → Element NOT found with old selector" --level error 2>/dev/null || true
python dashboard/utils/client.py event --type log --stage inspect_dom \
  --message "  → Candidate found: <NEW_ELEMENT_DESCRIPTION>" --level success 2>/dev/null || true
```

Store the DOM snapshot or relevant snippet as `DOM_SNAPSHOT` for Stage 5.

```bash
python dashboard/utils/client.py event --type stage_complete --stage inspect_dom \
  --message "DOM inspected — <N> candidate replacements identified" --level success \
  --data '{"selectors_found":["<new_sel_1>","<new_sel_2>"]}' \
  2>/dev/null || true
```

---

## Stage 5 — Claude Heals (`apply_heal`)

**Goal**: Reason about the correct locator replacements from the combined context, then patch the POM.

### 5a — Post the prompt to ClaudePane

Before you start reasoning, post what you're about to analyse:

```bash
python dashboard/utils/ai_event.py --phase prompt --stage apply_heal << EOF
Healing broken locators in ${POM_FILE}

## Broken Locators
${BROKEN_LOCATORS_JSON}

## UI PR Diff Summary
${PR_DIFF_SUMMARY}

## DOM Snapshot (search area)
${DOM_SNAPSHOT}

Task: For each broken locator, derive the corrected Playwright selector
using evidence from the PR diff and live DOM snapshot.
EOF
2>/dev/null || true
```

### 5b — Post thinking phase

```bash
python dashboard/utils/ai_event.py --phase thinking --stage apply_heal << 'EOF'
Step 1 — PR diff: identifying renamed classes and changed attributes…
Step 2 — DOM snapshot: locating each element in the live page to confirm…
Step 3 — Deriving stable replacement selectors verified against both sources…
EOF
2>/dev/null || true
```

### 5c — Reason and generate healed selectors

Now **you** (Claude) analyse — follow all three steps for every locator, even when
the PR diff alone makes the answer obvious:
1. PR diff: identify what changed (class names, placeholders, IDs, data-* attrs)
2. DOM snapshot: locate the element in the live snapshot and **confirm** the new value is present there
3. Derive the replacement selector, citing both the diff evidence and the DOM confirmation

### 5d — Post response to ClaudePane

After reasoning, post your conclusions:

```bash
python dashboard/utils/ai_event.py --phase response --stage apply_heal << EOF
Healed selectors:

$(for each heal: "  ${id}: '${old_locator}' → '${new_locator}'\n  Reason: ${reasoning}\n")
EOF
2>/dev/null || true
```

### 5e — Apply the patch

Log before patching:
```bash
python dashboard/utils/client.py event --type log --stage apply_heal \
  --message "Applying patches to ${POM_FILE}…" 2>/dev/null || true
```

Use the **Edit tool** to apply each locator replacement directly in `${POM_FILE}`.
For each heal, replace the old locator string with the new one.

Log each patch:
```bash
python dashboard/utils/client.py event --type log --stage apply_heal \
  --message "  ✓ ${id}: '${OLD}' → '${NEW}'" --level success 2>/dev/null || true
```

```bash
python dashboard/utils/client.py event --type stage_complete --stage apply_heal \
  --message "Patch applied — <N> selectors healed" --level success \
  --data "{\"selectors_healed\":<N>,\"file\":\"${POM_FILE}\",\"artifacts\":[{\"path\":\"${POM_FILE}\",\"type\":\"python\",\"label\":\"Heal Patch\"}]}" \
  2>/dev/null || true
```

---

## Stage 6 — Verify Heal (`verify_heal`)

**Goal**: Re-run the same regression suite to confirm all previously failing tests now pass.

```bash
python dashboard/utils/client.py event --type stage_start --stage verify_heal \
  --message "Re-running regression with healed locators…" 2>/dev/null || true

python dashboard/utils/client.py event --type log --stage verify_heal \
  --message "pytest tests/ -k 'regression' -v --timeout=30" 2>/dev/null || true
```

Run regression:
```bash
pytest tests/ -k "regression" -v --timeout=30 2>&1 | tee /tmp/verify_result.txt
VERIFY_EXIT=$?
```

Log each test result:
```bash
grep -E "PASSED|FAILED" /tmp/verify_result.txt | while read line; do
  LEVEL="success"
  echo "$line" | grep -q "FAILED" && LEVEL="error"
  python dashboard/utils/client.py event --type log --stage verify_heal \
    --message "  ${line}" --level $LEVEL 2>/dev/null || true
done
```

If verify fails:
```bash
python dashboard/utils/client.py event --type stage_error --stage verify_heal \
  --message "Heal did not fully resolve failures — manual review needed" \
  2>/dev/null || true
```
Tell the user and stop.

On success:
```bash
PASS_COUNT=$(grep -c "PASSED" /tmp/verify_result.txt || echo 0)
python dashboard/utils/client.py event --type log --stage verify_heal \
  --message "${PASS_COUNT} passed, 0 failed 🎉" --level success 2>/dev/null || true

python dashboard/utils/client.py event --type stage_complete --stage verify_heal \
  --message "Heal confirmed: ${PASS_COUNT}/${PASS_COUNT} passed ✅" --level success \
  --data "{\"passed\":${PASS_COUNT},\"failed\":0}" 2>/dev/null || true
```

---

## Stage 7 — Raise Heal PR (`raise_heal_pr`)

**Goal**: Commit the patched POM to a heal branch and open a PR against the automation repo.

```bash
python dashboard/utils/client.py event --type stage_start --stage raise_heal_pr \
  --message "Raising heal PR to ${AUTO_OWNER}/${AUTO_REPO}…" 2>/dev/null || true
```

Use **GitHub MCP** to create the branch, commit, and PR:

```
# Create heal branch
mcp__github__create_branch(owner=AUTO_OWNER, repo=AUTO_REPO, branch=HEAL_BRANCH, from_branch="main")

# Push the patched POM
mcp__github__create_or_update_file(
  owner=AUTO_OWNER, repo=AUTO_REPO,
  path=POM_FILE,
  message="heal(locators): fix selectors broken by UI PR #${UI_PR_NUMBER}",
  content=<base64 of patched file>,
  branch=HEAL_BRANCH
)

# Create PR
mcp__github__create_pull_request(
  owner=AUTO_OWNER, repo=AUTO_REPO,
  title="[self-heal] fix locators for UI PR #${UI_PR_NUMBER}",
  body=<PR body — see below>,
  head=HEAL_BRANCH, base="main"
)
```

PR body template:
```markdown
## 🩹 Self-Heal: Locator fix for UI PR #${UI_PR_NUMBER}

**Triggered by:** [${PR_TITLE}](https://github.com/${UI_OWNER}/${UI_REPO}/pull/${UI_PR_NUMBER})
**Root cause:** CSS class / attribute names changed in the UI PR

### Selectors Healed

| Variable | Old | New | Reason |
|---|---|---|---|
<one row per healed locator>

### Verification
All regression tests pass with healed locators ✅

---
*Auto-generated by the RevFlow Self-Heal Agent*
```

Log the result:
```bash
python dashboard/utils/client.py event --type log --stage raise_heal_pr \
  --message "PR #<HEAL_PR_NUMBER> created: ${HEAL_PR_URL}" --level success 2>/dev/null || true
```

Write the heal summary report:
```bash
cat > reports/heal_summary.md << REPORT
# Self-Heal Summary

**UI PR:** [${PR_TITLE}](https://github.com/${UI_OWNER}/${UI_REPO}/pull/${UI_PR_NUMBER})
**Heal Branch:** \`${HEAL_BRANCH}\`
**Heal PR:** [PR #<NUMBER>](${HEAL_PR_URL})

## Selectors Healed
<one section per heal with old/new/reason>

## Test Results After Heal
| Test | Result |
|---|---|
<one row per test — all PASSED>
REPORT
```

```bash
python dashboard/utils/client.py event --type stage_complete --stage raise_heal_pr \
  --message "Heal PR raised ✅" --level success \
  --data "{\"pr_number\":\"<N>\",\"branch\":\"${HEAL_BRANCH}\",\"selectors_fixed\":<N>,\"artifacts\":[{\"path\":\"reports/heal_summary.md\",\"type\":\"markdown\",\"label\":\"Heal Summary\"}]}" \
  2>/dev/null || true
```

---

## Workflow Complete

```bash
python dashboard/utils/client.py event \
  --type workflow_complete \
  --message "Self-heal complete — all regression tests passing ✅" \
  --level success \
  --data "{\"heal_pr\":\"${HEAL_PR_URL}\",\"ui_pr\":\"https://github.com/${UI_OWNER}/${UI_REPO}/pull/${UI_PR_NUMBER}\"}" \
  2>/dev/null || true
```

Tell the user: self-heal complete, heal PR URL, number of selectors fixed, all tests passing.
