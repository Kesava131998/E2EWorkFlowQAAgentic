---
name: self-heal
description: After any session (test run, test generation, debug, review), scan for new patterns or deviations and automatically update the most relevant skill file to keep the playbook current.
tags: [meta, self-healing, learning, maintenance]
---

# Skill: Self-Heal — Continuous Skill Improvement

Runs at the **end of any significant session** to detect new patterns, anti-patterns, or
failures that are not yet captured in any skill. Then surgically updates the single most
relevant skill file so future sessions benefit immediately.

> **Skill files live in**: `.claude/commands/`
> **Rules baseline**: `agents/rules.md`
> **Output log**: `plans/self-heal-log.md` (append-only)

---

## When to invoke

- After a `run-tests` session completes (pass or fail)
- After `generate-tests` produces new test files
- After `debug-test` resolves (or fails to resolve) a failure
- After `write-page-object` adds new patterns
- After `project-review` surface new findings
- User says: "learn from this session", "update the skills", "self-heal"
- **Automatically at session end** — this skill SHOULD be chained as the last step in long sessions

---

## Observations taxonomy

Categorise every observation into one of these signal types before deciding what to update:

| Signal Type | Description | Target skill |
|-------------|-------------|--------------|
| 🟠 **New locator pattern** | A new stable selector strategy worked well | `write-page-object`, `debug-test` |
| 🔴 **Recurring failure** | Same error class appeared ≥2 times | `debug-test`, `run-tests` |
| 🟡 **New timeout sensitivity** | A page/action needed a different timeout tier | `run-tests`, `debug-test` |
| 🟢 **New Excel column alias** | Generator encountered unmapped column name | `generate-tests` |
| 🔵 **New test pattern** | Test structure diverged from template but worked | `generate-tests`, `write-page-object` |
| ⚪ **New known-issue** | A skip/xfail pattern was added for a Jira bug | `debug-test` |
| 🟣 **Commit/PR convention** | A new commit type or PR label was used | `commit-changes`, `raise-pr` |
| ⚫ **Architecture deviation** | Something violated `agents/rules.md` but worked | `agents/rules.md` directly |

---

## Workflow

### Step 1 — Collect session evidence

Gather context from the just-completed session. Check the following in order:

**From test runs (`run-tests` / `debug-test`):**
```bash
# Last pytest output summary
tail -50 pytestdebug.log

# Any new skip/xfail markers added
grep -r "pytest.skip\|pytest.xfail" tests/ --include="*.py" -n

# Timeout values used
grep -r "wait_for_timeout\|TIMEOUT" tests/ pages/ --include="*.py" -n | grep -v "settings\."
```

**From test generation (`generate-tests`):**
```bash
# Newest test files
ls -lt tests/ | head -10

# TODO stubs left (unresolved steps)
grep -r "# TODO: Implement" tests/ --include="*.py" -n

# Column aliases that got fuzzy-matched (not in standard schema)
# (read from the test generator's output or user conversation)
```

**From page object work (`write-page-object`):**
```bash
# Recently modified page files
ls -lt pages/ | head -5

# New locator strategies
grep -r "data-testid\|aria-\|role=" pages/ --include="*.py" -n
```

**From project review (`project-review`):**
```bash
# Latest review file
ls -t plans/review-*.md | head -1
# Read its "Action Plan" section for patterns to bake in
```

---

### Step 2 — Pattern detection

For each piece of evidence, apply these detection rules:

#### 2a. Detect recurring failures
```bash
# Count how many distinct sessions had TimeoutError
grep -c "TimeoutError" pytestdebug.log
```
- If ≥ 2 TimeoutErrors on the **same element/page**: → add to `debug-test.md` "Common root causes" table
- If all in same module: → add a module-specific note in `run-tests.md` "Common failure patterns"

#### 2b. Detect new locator patterns
- If a new `data-testid`, `aria-label`, or role-based locator was introduced and worked: 
  → elevate its priority in `write-page-object.md` "Locator selection priority"
- If a fragile XPath was the only option available:
  → add a note to `debug-test.md` module-specific table

#### 2c. Detect new Excel column aliases
- If `generate-tests` fuzzy-matched a new column name:
  → add the alias to the "Expected columns" table in `generate-tests.md`

#### 2d. Detect TODO leftovers
- If `# TODO: Implement` stubs were NOT resolved:
  → add a note to `generate-tests.md` "Step 5 — Fix TODOs" about this class of unresolvable step

#### 2e. Detect new known issues
- If a `pytest.skip("Known issue")` was added referencing a Jira ticket:
  → record in `debug-test.md` "Common root causes" with the ticket and module

#### 2f. Detect architecture deviation
- If code that violated `agents/rules.md` was written but worked (e.g., assertion in a page object method for a very specific reason):
  → propose adding a documented exception to `agents/rules.md` — ask the user first before writing

---

### Step 3 — Score and select ONE skill to update

For each detected signal, score the **impact** and **frequency**:

| Score | Criterion |
|-------|-----------|
| +3 | Signal appeared in this session AND in a previous session |
| +2 | Signal would have prevented a failure if captured earlier |
| +1 | Signal is novel (first time seen) |
| -1 | Signal is already partially documented in the target skill |

Pick the **single highest-scoring skill file** to update. Do NOT update multiple files in one run — one targeted, high-quality update beats scattered noise.

> **Exception**: If an `agents/rules.md` violation is detected (⚫ signal), always ask the user before editing that file.

---

### Step 4 — Draft the update

Before writing, read the target skill file in full to:
1. Find the exact section to update (table row, bullet, etc.)
2. Ensure no duplication with existing content
3. Match the writing style and format of the surrounding content

Draft the update as a **minimal, surgical change**:
- Add one table row → do not rewrite the table
- Add one bullet → do not restructure the list
- Add one example → do not change existing examples

Show the diff to the user:
```
File: .claude/commands/<target-skill>.md
Section: <section name>

--- Before ---
<existing relevant snippet>

+++ After ---
<updated snippet with new row/bullet/example>
```

Ask: **"Shall I apply this update? (yes / no / tweak)"**

---

### Step 5 — Apply the update (on approval)

Write the change to `.claude/commands/<target-skill>.md`.

Then verify the file is still valid:
```bash
# Markdown should parse — check for unclosed blocks
grep -c "^\`\`\`" .claude/commands/<target-skill>.md
# Count of opening/closing backtick fences should be even
```

---

### Step 6 — Append to the self-heal log

Always append a record to `plans/self-heal-log.md` (create if missing):

```markdown
## <YYYY-MM-DD HH:MM> — Self-Heal Session

**Triggered by**: <run-tests / generate-tests / debug-test / manual>
**Observations**:
- <Signal type emoji> <one-line description of what was observed>
- ...

**Action taken**: Updated `<skill-file>.md` → Section: `<section name>`
**Change summary**: <one sentence>
**Approved by**: User / Auto (no-risk change)

---
```

If no update was made (no strong signal / user declined):
```markdown
## <YYYY-MM-DD> — Self-Heal Session (No Update)
**Triggered by**: <skill>
**Reason**: No new patterns detected / Low confidence / User declined
---
```

---

### Step 7 — Report to user

Summarise in 3–5 lines:
- What was observed
- Which skill was updated (or why nothing was updated)
- Link to the self-heal log: `plans/self-heal-log.md`

---

## Guardrails — what this skill MUST NOT do

| ❌ Forbidden | Reason |
|-------------|--------|
| Update more than one skill file per session | Keeps changes reviewable and reversible |
| Rewrite an entire skill section | Too destructive; use surgical edits |
| Update `agents/rules.md` without user approval | Rules file is the ground truth |
| Add unverified information (guesses) | Only document what was directly observed |
| Delete existing content from a skill | Only add; removal requires deliberate human decision |
| Trigger itself recursively | This skill does not self-update |

---

## Chaining guidance

This skill is designed to be the **last step** in a chain. Invoke it after:

```
run-tests → self-heal
generate-tests → self-heal
debug-test → self-heal
project-review → self-heal
write-page-object → self-heal
```

It can also be invoked standalone at any time:
> "Review the last session and update the skills if needed."

---

## Notes

- `plans/self-heal-log.md` is the **audit trail** — never delete it
- If the log doesn't exist yet, create it with a `# Self-Heal Log` header before appending
- Updates accumulate over time; the skills evolve as new patterns emerge
- If the same section of a skill is updated in 3+ consecutive sessions, consider proposing a larger refactor of that skill to the user
