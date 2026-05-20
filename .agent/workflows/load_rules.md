---
description: Load all project rules from .agent/rules/*.md and apply them for this session
category: ops
status: active
safety: read-only
---

# Load Rules Workflow

This workflow ensures the agent reads and internalises every rule file in `.agent/rules/` before proceeding with any task.

## Steps

1. List all rule files:

```
ls .agent/rules/
```

2. Read **every** `.md` file found in `.agent/rules/`.

Example grouped files:
- `.agent/rules/00-rule-enforcement.md`
- `.agent/rules/10-agent-ownership.md`
- `.agent/rules/15-plan-mode-criteria.md`
- `.agent/rules/20-evidence-debugging.md`
- `.agent/rules/25-information-integrity.md`
- `.agent/rules/30-safety-authorization.md`
- `.agent/rules/40-git-isolation.md`
- `.agent/rules/50-validation-delivery.md`
- `.agent/rules/60-runtime-ops.md`
- `.agent/rules/70-style-code.md`

> Read them in parallel where possible to save time.

3. After reading all files, **confirm internalization** by briefly summarising each rule in chat (one-liner per rule), so the user can verify coverage.

4. Apply all rules immediately and for the remainder of this session. Rules take precedence over default agent behavior.

> Always glob the directory dynamically before reading; the list above is descriptive, not authoritative.
