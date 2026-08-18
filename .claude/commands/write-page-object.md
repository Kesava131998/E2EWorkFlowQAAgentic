---
name: write-page-object
description: Create or extend a Page Object Model class for a new or existing application page
tags: [page-object, playwright, scaffolding, core]
---

# Skill: Write Page Object

Creates a new — or adds methods/locators to an existing — Page Object class.
Follows the project's `BasePage` inheritance pattern with `test.step(...)` wrapping for reporting.

> **Rules**: See `agents/rules.md` — "Page Objects" section

---

## When to invoke

- User says "add a page for X", "create a page object for the Y screen"
- A generated test has `// TODO: Implement` steps with no matching method
- A new UI section/module has been added to the app under test

---

## Workflow

### Step 1 — Check the existing codebase first

**This is the primary source of locators — not Playwright MCP.** Scan the `pages/` directory before anything else:
```bash
ls pages/*.js
grep -n "this\.\w* = " pages/*.js   # list every existing locator across all page objects
```
- If a page object for this module already exists, extend it — reuse its existing `this.*` locators/methods for any action that already has one, and only add new locators for elements genuinely not covered yet.
- If a *different* page object already has a locator/method for the same shared component (e.g. a common modal, nav bar, grid), reuse that pattern/selector convention rather than reinventing it.
- Only once the existing codebase has been checked and a needed locator truly isn't there should you move to Step 2.

### Step 2 — Live DOM inspection (fallback only, when the app is running)

Use this **only** for elements that Step 1 didn't find anywhere in `pages/` — never as the default way of sourcing locators, and never to re-derive a locator that already exists in the codebase.

Ask (or infer from context) what's still missing:
- **Page name**: e.g., "Reports", "User Management"
- **URL path** (if known): e.g., `/reports/overview`
- **Actions needed**: list of user interactions (click, fill, select, verify)

If Playwright MCP is available, use it to inspect the live page for just those missing elements:
```
# Playwright MCP — navigate and snapshot
browser_navigate(url="<BASE_URL>/target-page")
browser_snapshot()  # returns accessibility tree with locators
```
If the app/MCP isn't available, ask the user directly for the CSS/data-testid/XPath of the missing element instead of guessing.

### Step 3 — Scaffold the page class

**Template for a new page (`pages/<module>_page.js`):**
```js
const { test } = require('@playwright/test');
const { BasePage } = require('./base_page');

class <ClassName>Page extends BasePage {
  /**
   * Page object for the <Module> section.
   * URL: <url-path>
   */
  constructor(page) {
    super(page);
    // ── Locators ──────────────────────────────────────────────────────
    this.<element> = page.locator("<css-or-xpath-selector>");
    // Add more locators here
  }

  // ── Actions ───────────────────────────────────────────────────────────

  async click<Action>() {
    await test.step('Click <action>', async () => {
      await this.<element>.click();
      await this.page.waitForLoadState('domcontentloaded');
    });
  }

  async enter<Field>(value) {
    await test.step('Enter <value> in <field>', async () => {
      await this.<element>.fill(value);
    });
  }

  async verify<Element>Visible() {
    const { expect } = require('@playwright/test');
    await expect(this.<element>).toBeVisible({ timeout: 30000 });
  }
}

module.exports = { <ClassName>Page };
```

**Adding a method to an existing page:**
```js
  async click<NewAction>() {
    await test.step('Click <new action>', async () => {
      await this.<locator>.click();
    });
  }
```

### Step 4 — Locator hygiene check
Before saving:
- [ ] No duplicate locator names with existing `this.*` properties
- [ ] XPath is used only when CSS selector is genuinely insufficient
- [ ] Locators are stored in the constructor, not scattered across methods
- [ ] No raw `this.page.locator(...)` strings inside action methods — always reference `this.*`

### Step 5 — Verify import chain
The new page must be importable:
```bash
node -e "const { <ClassName>Page } = require('./pages/<module>_page.js'); console.log('OK')"
```

### Step 6 — Update test imports
If tests already reference the module, verify imports are updated:
```js
const { <ClassName>Page } = require('../pages/<module>_page');
```

---

## Locator selection priority

1. `id` attributes: `#element-id`
2. Data attributes: `[data-testid="submit"]`
3. ARIA roles: `page.getByRole('button', { name: 'Login' })`
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

Use `browser_snapshot()` to get the accessibility tree and identify stable selectors.
