---
description: Create a one-page task brief before non-trivial feature, bugfix, refactor, docs, or ops work
category: docs
status: active
safety: writes-local
---

# Task Brief Workflow

Use this workflow before non-trivial work that touches runtime behavior, multiple
files, external APIs, documentation architecture, or deployment-sensitive paths.

Skip only for tiny doc/style edits, direct factual answers, or when no durable
docs area exists and a brief would add noise.

## Steps

1. Load context:

```bash
bash .agent/skills/secretary/secretary.sh ask "<task keywords>" --level L1
```

2. Pick a brief filename:

```text
docs/task_briefs/YYYY-MM-DD_<task_slug>.md
```

3. If `docs/templates/task_brief.md` exists, use it. Otherwise create a concise brief with:

- timestamp,
- goal,
- scope in/out,
- affected paths,
- risks and rollback,
- validation plan,
- review path,
- delivery criteria.

4. Keep the brief to one page. If the task grows, update the brief instead of
keeping decisions only in chat.

## Notes

1. Name project-specific gates only when this repository actually defines them.
2. Every generated brief must include an ISO-8601 timestamp.
3. Reuse and update the current brief when continuing the same task.
