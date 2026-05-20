---
name: Prepare Session
description: Prepare a new agent session by loading project rules, reading reusable harness instructions, querying Secretary, and internalizing available experience files.
category: ops
status: active
safety: read-only
---

# Prepare Session

Run this skill at the start of a non-trivial session when the agent needs fresh
project context.

## When To Use

- At the start of complex work.
- When the user says "load context" or equivalent.
- Before cross-file coding, debugging, review, research, or harness cleanup.

## Steps

### 1. Load Entry Instructions

Read:

- `AGENTS.md`
- `basicagents.md` when referenced by `AGENTS.md`

Apply the project-specific instructions after the base instructions.

### 2. Load Rules

List and read every rule file dynamically:

```bash
rg --files .agent/rules
```

Do not rely on a static rule list.

### 3. Query Secretary

If Secretary exists, run a task-relevant lookup:

```bash
bash .agent/skills/secretary/secretary.sh ask "<task keywords>" --level L1
```

If the index is missing or stale, run:

```bash
bash .agent/skills/secretary/secretary.sh scan --incremental
```

### 4. Load Experiences

If `.agent/experiences/` exists, read the files relevant to the task. For broad
harness work, read all remaining experience files. Treat experiences as memory,
not as stronger instructions than rules.

### 5. Summarize Readiness

Report briefly:

- rules loaded,
- docs/index status,
- relevant experience files,
- important constraints,
- missing context or unavailable git/runtime support.

## Rules

1. Read actual file content, not just filenames.
2. Apply rules immediately.
3. Keep bootstrap concise; do not flood the user with per-file narration.
4. If inherited old-project content is discovered, identify it and avoid using it as active project context.
