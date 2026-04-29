---
name: write-page-object
description: Create or extend a Page Object Model class for a new or existing application page
tags: [page-object, playwright, scaffolding, core]
---

# Skill: Write Page Object

Creates a new — or adds methods/locators to an existing — Page Object class.
Follows the project's `BasePage` inheritance pattern with `@allure.step` decorators.

> **Rules**: See `agents/rules.md` — "Page Objects" section

---

## When to invoke

- User says "add a page for X", "create a page object for the Y screen"
- A generated test has `# TODO: Implement` steps with no matching method
- A new UI section/module has been added to the app under test

---

## Workflow

### Step 1 — Understand what's needed
Ask (or infer from context):
- **Page name**: e.g., "Reports", "User Management"
- **URL path** (if known): e.g., `/reports/overview`
- **Actions needed**: list of user interactions (click, fill, select, verify)
- **Locators** (if known): CSS/XPath for key elements

If the app is running and Playwright MCP is available, use it to inspect the live page:
```
# Playwright MCP — navigate and snapshot
playwright_navigate(url="<BASE_URL>/target-page")
playwright_snapshot()  # returns accessibility tree with locators
```

### Step 2 — Check for existing page objects
Scan `pages/` directory. If a related page exists, extend it rather than creating a new file.

### Step 3 — Scaffold the page class

**Template for a new page (`pages/<module>_page.py`):**
```python
import allure
from pages.base_page import BasePage


class <ClassName>Page(BasePage):
    """
    Page object for the <Module> section.
    URL: <url-path>
    """

    def __init__(self, page):
        super().__init__(page)
        # ── Locators ──────────────────────────────────────────────────────
        self.<element>  = "<css-or-xpath-selector>"
        # Add more locators here

    # ── Actions ───────────────────────────────────────────────────────────

    @allure.step("Click <action>")
    def click_<action>(self):
        self.page.locator(self.<element>).click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Enter <value> in <field>")
    def enter_<field>(self, value: str):
        self.page.locator(self.<element>).fill(value)

    @allure.step("Verify <element> is visible")
    def verify_<element>_visible(self):
        from playwright.sync_api import expect
        expect(self.page.locator(self.<element>)).to_be_visible(
            timeout=30000
        )
```

**Adding a method to an existing page:**
```python
    @allure.step("Click <new action>")
    def click_<new_action>(self):
        self.page.locator(self.<locator>).click()
```

### Step 4 — Locator hygiene check
Before saving:
- [ ] No duplicate locator names with existing `self.*` attributes
- [ ] XPath is used only when CSS selector is genuinely insufficient
- [ ] Locators are stored in `__init__`, not scattered across methods
- [ ] No raw `page.locator(...)` strings in methods — always reference `self.*`

### Step 5 — Verify import chain
The new page must be importable:
```bash
python -c "from pages.<module>_page import <ClassName>Page; print('OK')"
```

### Step 6 — Update test imports
If tests already reference the module, verify imports are updated:
```python
from pages.<module>_page import <ClassName>Page
```

---

## Locator selection priority

1. `id` attributes: `#element-id`
2. Data attributes: `[data-testid="submit"]`
3. ARIA roles: `role=button[name="Login"]`
4. CSS class (stable ones only): `.submit-btn`
5. XPath last resort: `//button[text()='Submit']`

---

## Playwright MCP — Live Locator Discovery

If the app is running, the agent can use Playwright MCP to find locators:

**MCP Config required:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    }
  }
}
```

Use `playwright_snapshot()` to get the accessibility tree and identify stable selectors.
