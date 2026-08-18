# CLAUDE.md — Playwright Automation Project (JavaScript)

> This file configures **Claude Code** for this project.
> Rules are summarized below. Commands live in `.claude/commands/`.

---

































## Project Rules

Follow these conventions for the Playwright JavaScript automation project (`@playwright/test`):

- **Page Objects**: All page classes extend `BasePage` (`pages/base_page.js`), wrap public methods in `test.step(...)` for reporting, define locators in the constructor
- **Locator sourcing**: Always check the existing `pages/*.js` codebase for a matching locator/method first (`grep -n "this\.\w* = " pages/*.js`) and reuse it. Only fall back to Playwright MCP live DOM inspection for elements that genuinely don't exist yet anywhere in `pages/` — never use MCP as the default way to (re)write locators that are already defined in the codebase.
- **Tests**: Use the built-in `page` fixture from `@playwright/test`, wrap steps in `test.step(...)`, use `settings.*_TIMEOUT` for timeouts, tag titles with `pos:`/`err:`/`perm:` prefixes per scenario type
- **Configuration**: Load settings from `config/settings.js`, use `.env` (via `dotenv`) for environment variables, no hardcoded credentials
- **Timeouts**: Never use raw integers; always use `settings.*_TIMEOUT` or environment variables
- **Commits**: Use Conventional Commits format (`feat|fix|test|refactor|chore|docs`)
- **Dependencies**: Install from `package.json` (`npm ci`), run `npx playwright install --with-deps` for browsers
- **Execution**: Use `npx playwright test` for running tests, control parallelism via `playwright.config.js` `workers` / `--workers`
- **Reporting**: Generate Allure (`allure-playwright`) and Playwright HTML reports in `reports/`, capture screenshots/videos on failure
- **Structure**: Keep tests in `tests/` (`*.spec.js`), pages in `pages/`, config in `config/`, data in `data/`
- **CI/CD**: Tests run via GitHub Actions on push/PR (`.github/workflows/playwright.yml`), matrix for multiple browsers via `--project`

---

## Commands

The following slash commands are available.
Each command file in `.claude/commands/` contains the full workflow.

| Slash Command | File | Description |
|--------------|------|-------------|
| `/e2e-workflow` | `.claude/commands/e2e-workflow.md` | Full Jira-to-PR workflow (takes ticket ID as argument) |
| `/generate-tests` | `.claude/commands/generate-tests.md` | Generate tests from Excel |
| `/write-page-object` | `.claude/commands/write-page-object.md` | Scaffold page object class |
| `/run-tests` | `.claude/commands/run-tests.md` | Run Playwright suite + Allure |
| `/commit-changes` | `.claude/commands/commit-changes.md` | Review staged diff + commit |
| `/raise-pr` | `.claude/commands/raise-pr.md` | Create GitHub PR |
| `/review-pr` | `.claude/commands/review-pr.md` | Fetch + review open PR |
| `/github-mcp-operations` | `.claude/commands/github-mcp-operations.md` | Execute GitHub/Git MCP tool actions |
| `/jira-ticket` | `.claude/commands/jira-ticket.md` | Work from Jira ticket |
| `/project-review` | `.claude/commands/project-review.md` | Full codebase audit |
| `/debug-test` | `.claude/commands/debug-test.md` | Diagnose + fix failing test |
| `/self-heal-demo` | `.claude/commands/self-heal-demo.md` | Live 6-stage self-heal demo — breaks + auto-heals task_list_page.js locators |

---

## MCP Servers

Three MCP servers are active via `.mcp.json` (loaded automatically — `enableAllProjectMcpServers: true`):

| Server | Package | Commands that use it |
|--------|---------|---------------------|
| **GitHub** | `@modelcontextprotocol/server-github` | `/raise-pr`, `/review-pr`, `/github-mcp-operations` |
| **Jira** | `mcp-atlassian` (via `uvx`) | `/jira-ticket`, `/e2e-workflow` |
| **Playwright** | `@playwright/mcp` | Browser automation, interactive testing, debugging |

**Jira MCP tools available**: `jira_get_issue`, `jira_search`, `jira_create_issue`, `jira_update_issue`, `jira_transition_issue`

**Playwright MCP tools available**: 150+ browser automation tools including `browser_navigate`, `browser_click`, `browser_fill_form`, `browser_take_screenshot`, `browser_network_request`, `browser_evaluate`, and more

**Configuration**: credentials are stored inline in `.mcp.json` (git-ignored). Restart Claude Code after any changes to `.mcp.json`. No OpenAPI/Swagger spec is currently known for the application under test — if one becomes available, add a Swagger MCP server here and wire it into `/e2e-workflow`'s Swagger Discovery step.

---

## Application Under Test

**RevFlow** (`https://revflow-dev.axgsolutions.com/`) — a healthcare accounts-receivable / billing case-management app. Login is via Microsoft Azure AD SSO ("Sign in with Microsoft"), modeled by `pages/login_page.js`. The Task List grid (`/tasks`, `pages/task_list_page.js`) lists resident/payer cases in a custom `arw-grid-table` component.

## Context hints for Claude

- The main page hierarchy: `BasePage` ← all page classes (`LoginPage`, `CaseDetailPage`, `BillerActivityPage`, `TaskListPage`, …)
- Playwright Test opens a fresh `page` per test by default (function-scoped); screenshot/video/trace capture on failure is configured centrally in `playwright.config.js`'s `use` block, not per-file
- `config/settings.js` reads `.env` via `dotenv` — prefer `settings.*` in tests (`settings.BASE_URL`, `settings.AUTH_USERNAME`, `settings.AUTH_PASSWORD`)
- Generated reports at: `reports/html/`, `reports/allure-results/`, `test-results/` (screenshots/videos/traces)
