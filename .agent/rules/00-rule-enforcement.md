---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Rule Enforcement

Rules in `.agent/rules` are mandatory.

1. Load all applicable rules before acting; use `rg --files .agent/rules` and read each file.
2. Follow the stricter and more specific rule when rules overlap.
3. Higher-priority system/developer instructions win; state the blocker when a repo rule cannot be executed because of them.
4. Do not skip rules for speed, brevity, convenience, or personal judgment.
5. Before every user-facing result, run a final rule check and fix any missed requirement.
6. If a workflow or skill requires a stricter format, follow it and still satisfy these rules as far as possible.
