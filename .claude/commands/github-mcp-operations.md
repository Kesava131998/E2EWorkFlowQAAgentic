---
name: github-mcp-operations
description: Master reference for performing all Git and GitHub related operations using exclusively MCP tools rather than raw CLI commands.
tags: [github, git, mcp, workflow]
---

# Skill: GitHub MCP Operations

This skill serves as the single source of truth for interacting with Git and GitHub. **All Git-related actions and GitHub interactions MUST follow MCP tool usage rather than using the `gh` or `git` CLI whenever possible.**

> **MCP Required**: GitHub MCP server (`@modelcontextprotocol/server-github`)

---

## When to invoke

- "Check GitHub"
- "Any PRs open?"
- "Merge this PR"
- "Push my changes to GitHub"
- Whenever you need to submit reviews, read repository state, or manage branches/PRs.

---

## Available GitHub MCP Tools Reference

Below is the definitive list of tools exposed by the GitHub MCP server, based on the **Code Review Workflow**, which you should invoke directly:

| Tool                         | Purpose                                      | Example Usage / Parameters |
| ---------------------------- | -------------------------------------------- | ------------------------------------------------------------------ |
| `mcp_github_list_pull_requests`         | List PRs (open/closed/all)                   | `owner, repo, state="open"` |
| `mcp_github_get_pull_request`           | Get PR metadata (title, author, branch)      | `owner, repo, pull_number` |
| `mcp_github_get_pull_request_files`     | Get changed files with diffs / patches       | `owner, repo, pull_number` |
| `mcp_github_get_pull_request_status`    | Get CI / status check results                | `owner, repo, pull_number` |
| `mcp_github_get_pull_request_reviews`   | Get existing reviews                         | `owner, repo, pull_number` |
| `mcp_github_create_pull_request_review` | Submit review (APPROVE, COMMENT, etc.)       | `owner, repo, pull_number, body, event` |
| `mcp_github_merge_pull_request`         | Merge the PR                                 | `owner, repo, pull_number, merge_method="squash"` |
| `mcp_github_create_pull_request`        | Open a new Pull Request                      | `owner, repo, title, head, base, body, draft` |

*Note: Depending on the exact MCP server version, additional file system level Git operations (like `mcp_github_get_file_contents`, `mcp_github_create_or_update_file`, `mcp_github_push_files`) might also be available for direct repository mutations.*

---

## Default Patterns & Usage

### 1. No More `gh` CLI
Never drop into bash and run `gh pr list` or `gh pr review`. You **must** invoke the semantic tool (e.g. `mcp_github_list_pull_requests` -> `mcp_github_get_pull_request_files` -> `mcp_github_create_pull_request_review`).

### 2. Parallel Processing
When reviewing PR details, fetch context concurrently. Do not fetch status linearly after PR files:
- Get `mcp_github_get_pull_request` inside your thought process
- Simultaneously trigger `mcp_github_get_pull_request_files`, `mcp_github_get_pull_request_status`, and `mcp_github_get_pull_request_reviews`.

### 3. Merging
If a PR review yields an `APPROVE` and all tests have passed successfully, immediately execute `mcp_github_merge_pull_request`. Prefer squash-merging (`merge_method="squash"`) to keep the history clean.

### 4. Bypassing Local Git for Quick Fixes
For extremely small typo fixes and direct documentation changes, consider whether the MCP tools (like `mcp_github_push_files` or `mcp_github_create_or_update_file` if available) can be used to mutate the remote directly, skipping the `git add`, `git commit`, `git push` dance. If not, follow the `commit-changes` skill but remember that the PR orchestration must be via MCP.
