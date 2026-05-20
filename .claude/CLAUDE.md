# CLAUDE.md — Playwright Automation Project

> This file configures **Claude Code** for this project.
> Rules are summarized below. Commands live in `.claude/commands/`.

---

































## Project Rules

Follow these conventions for the Playwright Python automation project:

- **Page Objects**: All page classes inherit from `BasePage`, use `@allure.step` decorators on all public methods, define locators in `__init__`
- **Tests**: Use the `page` fixture from `tests/conftest.py`, wrap steps in `with allure.step(...)`, use `settings.*_TIMEOUT` for timeouts
- **Configuration**: Load settings from `config/settings.py`, use `.env` for environment variables, no hardcoded credentials
- **Timeouts**: Never use raw integers; always use `settings.*_TIMEOUT` or environment variables
- **Commits**: Use Conventional Commits format (`feat|fix|test|refactor|chore|docs`)
- **Dependencies**: Install from `requirements.txt`, run `playwright install --with-deps` for browsers
- **Execution**: Use `pytest` for running tests, support parallel execution with `-n auto`
- **Reporting**: Generate Allure and HTML reports in `reports/`, capture screenshots/videos on failure
- **Structure**: Keep tests in `tests/`, pages in `pages/`, utilities in `utils/`, data in `data/`
- **CI/CD**: Tests run via GitHub Actions on push/PR, matrix for multiple browsers

---

## Commands

The following slash commands are available.
Each command file in `.claude/commands/` contains the full workflow.

| Slash Command | File | Description |
|--------------|------|-------------|
| `/e2e-workflow` | `.claude/commands/e2e-workflow.md` | Full Jira-to-PR workflow (takes ticket ID as argument) |
| `/generate-tests` | `.claude/commands/generate-tests.md` | Generate tests from Excel |
| `/write-page-object` | `.claude/commands/write-page-object.md` | Scaffold page object class |
| `/run-tests` | `.claude/commands/run-tests.md` | Run pytest suite + Allure |
| `/commit-changes` | `.claude/commands/commit-changes.md` | Review staged diff + commit |
| `/raise-pr` | `.claude/commands/raise-pr.md` | Create GitHub PR |
| `/review-pr` | `.claude/commands/review-pr.md` | Fetch + review open PR |
| `/github-mcp-operations` | `.claude/commands/github-mcp-operations.md` | Execute GitHub/Git MCP tool actions |
| `/jira-ticket` | `.claude/commands/jira-ticket.md` | Work from Jira ticket |
| `/project-review` | `.claude/commands/project-review.md` | Full codebase audit |
| `/debug-test` | `.claude/commands/debug-test.md` | Diagnose + fix failing test |

---

## MCP Servers

Four MCP servers are active via `.mcp.json` (loaded automatically — `enableAllProjectMcpServers: true`):

| Server | Package | Commands that use it |
|--------|---------|---------------------|
| **GitHub** | `@modelcontextprotocol/server-github` | `/raise-pr`, `/review-pr`, `/github-mcp-operations` |
| **Jira** | `mcp-atlassian` (via `uvx`) | `/jira-ticket`, `/e2e-workflow` |
| **Playwright** | `@playwright/mcp` | Browser automation, interactive testing, debugging |
| **Swagger** | `@ivotoby/openapi-mcp-server` | Joulez API integration, endpoint testing |

**Jira MCP tools available**: `jira_get_issue`, `jira_search`, `jira_create_issue`, `jira_update_issue`, `jira_transition_issue`

**Playwright MCP tools available**: 150+ browser automation tools including `browser_navigate`, `browser_click`, `browser_fill_form`, `browser_take_screenshot`, `browser_network_request`, `browser_evaluate`, and more

**Swagger MCP tools available**: 250+ Joulez API endpoints including booking operations (`crt-booking-using-pst`, `cancel-booking-using-del`), user management (`get-usr-using-get`, `upd-usr-using-put`), payment processing, car inventory, and location services. Base URL: `https://beta.drivejoulez.com:8443/joulez-service/`

**Configuration**: credentials are stored inline in `.mcp.json` (git-ignored). Restart Claude Code after any changes to `.mcp.json`.

---

## Context hints for Claude

- The main page hierarchy: `BasePage` ← all page classes
- Test sessions do NOT open new browsers per-test; see `tests/conftest.py` scope=`module`
- Root `conftest.py` handles screenshot capture on failure and Allure cleanup
- `config/settings.py` reads `.env` — prefer `settings.*` in tests
- Generated reports at: `reports/html/`, `reports/allure-results/`, `reports/videos/`
