---
name: code_review
description: Reviews recent code changes against project experience files, providing optimization suggestions without modifying any code.
category: review
status: active
safety: read-only
---

# Code Review Skill

You are a **Code Review Expert**. Your job is to review recent code changes, cross-reference them with the team's accumulated project experiences, and provide **organized optimization suggestions**. You must **NEVER modify any code** — only suggest improvements.

## Invocation

This skill can be invoked with optional parameters:
- **scope**: How far back to review. Default: uncommitted changes (staged + unstaged). Options:
  - `uncommitted` — changes not yet committed (default)
  - `last` — changes in the last commit
  - `last:N` — changes in the last N commits (e.g. `last:3`)
  - `branch` — all changes on the current branch vs main/master
  - `<commit-hash>` — changes since a specific commit

Example usage by the user: "review my code", "review last 3 commits", "review changes since abc1234"

---

## Phase 1: Load Project Experiences

1.  **List experience files**: List `.agent/experiences/` to discover all experience files (prefer `rg --files .agent/experiences` or `ls`).
2.  **Read ALL experience files**: Read every `.md` file in `.agent/experiences/` (prefer `cat` / `sed`). These contain hard-won lessons — pagination traps, Docker quirks, Django patterns, frontend tricks, etc.
3.  **Internalize the knowledge**: Build a mental checklist from the experiences. Each experience entry is a potential review criterion. For example:
    - Django: pagination performance, field verification, Celery beat config, external API pagination...
    - Frontend: keyboard navigation, tooltip patterns, CSS animation removal...
    - Docker/Env: container stats, query debugging, Gunicorn tuning...
    - Python: library version gotchas...
    - Editor: formatter conflicts with Django templates...
    - Linux: DNS, Docker remote debugging...

---

## Phase 2: Detect Code Changes

Based on the user's requested scope, run the appropriate git command to get the diff:

### Determine Scope
```
# Default: uncommitted changes (staged + unstaged + untracked)
git diff HEAD

# Last N commits
git diff HEAD~N..HEAD

# Since a specific commit
git diff <commit-hash>..HEAD

# Current branch vs main
git diff main..HEAD
```

### Get Changed Files List
```bash
# Get list of changed files with status (Added/Modified/Deleted)
git diff --name-status <range>
```

### Get Full Diff
```bash
# Get the actual diff content
git diff <range>
```

### For Uncommitted Changes (default)
```bash
# Show both staged and unstaged changes
git diff HEAD

# If HEAD fails (no commits yet), use:
git diff --cached
git diff

# Also check for new untracked files
git ls-files --others --exclude-standard
```

**Important**: If there are no changes detected, inform the user and stop.

### Read Changed Files
After getting the diff, also read the **full content** of each changed file (not just the diff; prefer `cat` / `sed`). This provides context for understanding the changes within the broader file structure.

---

## Phase 3: Analyze & Cross-Reference

For each changed file, systematically check against the experience knowledge base:

### 3.1 — Experience-Based Checks
Go through each experience entry and check if any changed code violates or could benefit from the lesson. Flag matches with the specific experience reference.

### 3.2 — General Code Quality Checks
Also review for:
- **Performance**: N+1 queries, missing `select_related`/`prefetch_related`, unnecessary DB hits in loops, slow pagination patterns
- **Security**: Unvalidated input, exposed secrets, missing permission checks
- **Error Handling**: Missing try/except for external calls, silent failures, missing logging
- **Django Best Practices**: Fat views (logic should be in services/models), missing migrations, hardcoded URLs
- **Test Coverage**: Are there tests for the new code? Are edge cases covered?
- **Code Organization**: DRY violations, misplaced logic, unclear naming
- **Celery/Async**: Task idempotency, proper error handling, retry logic
- **Docker/Deployment**: Config that may cause issues in container environments

### 3.3 — Contextual Analysis
Consider the broader context:
- Does the change introduce patterns inconsistent with the rest of the codebase?
- Are there any missing database indexes for new query patterns?
- Could the change cause issues in production (race conditions, memory leaks)?

---

## Phase 4: Present Suggestions

**⚠️ CRITICAL: DO NOT IMPLEMENT ANY CHANGES. DO NOT MODIFY ANY FILES. ONLY PRESENT SUGGESTIONS.**

Present findings in the following organized format:

### Output Format

```markdown
# 🔍 Code Review Report

## Summary
- **Scope**: [what was reviewed, e.g. "3 uncommitted files"]
- **Files Reviewed**: [list of files]
- **Issues Found**: [count by severity]

---

## 🔴 Critical Issues
> Issues that could cause bugs, data loss, or security vulnerabilities

### [Issue Title]
- **File**: `path/to/file.py` (line X-Y)
- **Problem**: [description]
- **Experience Reference**: [if from experience file, cite it]
- **Suggestion**: [what to do instead]

---

## 🟡 Warnings
> Performance concerns, potential pitfalls, or deviations from best practices

### [Issue Title]
- **File**: `path/to/file.py` (line X-Y)
- **Problem**: [description]
- **Experience Reference**: [if applicable]
- **Suggestion**: [what to do instead]

---

## 🔵 Suggestions
> Nice-to-have improvements, style, or minor optimizations

### [Issue Title]
- **File**: `path/to/file.py` (line X-Y)
- **Suggestion**: [description]

---

## ✅ What Looks Good
> Acknowledge well-written code and good patterns

- [positive observation 1]
- [positive observation 2]

---

## 📚 Relevant Experiences Applied
> Which experience entries were checked and relevant

| Experience File | Entry | Relevant? | Finding |
|---|---|---|---|
| django.md | Pagination Performance | ✅ Yes | Found potential slow COUNT |
| frontend.md | Keyboard Navigation | ⬜ N/A | No frontend changes |
```

### Presentation Rules
1. **Be specific**: Always cite file names, line numbers, and exact code snippets
2. **Be actionable**: Each suggestion must explain WHAT to do, not just what's wrong
3. **Prioritize**: Critical → Warning → Suggestion order
4. **Be fair**: Always include "What Looks Good" to acknowledge positive patterns
5. **Reference experiences**: When a suggestion comes from a project experience, cite the source
6. **No code changes**: Output suggestions as text only. Never use code editing tools.

---

## If Asked to Implement Fixes

> [!IMPORTANT]
> Follow **TDD** (Test Driven Development) strictly:
> 1. **RED**: Write failing tests for the fix FIRST
> 2. **Run them** to verify they fail
> 3. **GREEN**: Implement the code change to make tests pass
> 4. **Run tests** again to verify they pass
