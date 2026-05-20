---
name: Task Orchestrator
description: Agent-owned entrypoint for non-trivial work. Aligns intent, bootstraps context, creates or updates task briefs, selects isolation, validation, review, and delivery paths.
category: ops
status: active
safety: writes-local
---

# Task Orchestrator

Use this skill as the default entrypoint for non-trivial feature, bugfix,
refactor, review, docs, harness cleanup, or cross-file process work.

The user's ordinary request is enough. Do not ask the user to name workflows,
skills, gate scripts, or prompt templates before safe work can begin.

## Lifecycle

### 1. Align Intent

Identify:

- surface request,
- deeper objective,
- success metric,
- constraints and non-goals,
- affected files or systems,
- risk level,
- whether the task is analysis-only or implementation.

Ask only if ambiguity materially changes risk or implementation.

### 2. Select Debug Contract

For bugs, incidents, root-cause questions, or verification failures:

- load `.agent/workflows/from_the_ground_up.md`,
- use `.agent/workflows/show_me_evidence.md` before causal conclusions,
- report one of the allowed debug statuses from `.agent/rules/20-evidence-debugging.md`.

### 3. Bootstrap Context

If no fresh context has been loaded:

- use `Prepare Session`,
- run a Secretary lookup with task keywords when Secretary is present.

### 4. Create Or Update A Task Brief

For non-trivial work, use `.agent/workflows/task_brief.md` when present.

Skip only for tiny edits, direct answers, or cases where no docs area exists and a
brief would add process noise. If skipped, state why in final delivery.

### 5. Select Git Isolation

If git is available and the work is substantial:

- use `Git Autopilot`,
- prefer a `codex/<task-slug>` branch or worktree,
- preserve unrelated local edits.

If the directory is not a git repository, continue with file-level safeguards and
state that git isolation is unavailable.

### 6. Select Validation

Choose validation from the changed surface:

- docs: reopen files, check links/references, run Secretary scan when applicable,
- scripts: run help/smoke tests and focused unit tests,
- application code: run focused tests, build/type/lint checks, and relevant smoke tests,
- runtime work: verify against the named runtime only after explicit authorization.

Never run inherited old-project gates by default.

### 7. Review

For non-trivial programming, debugging, or research:

- run an adversarial review when tool policy permits,
- otherwise do an explicit self-review and say independent review was not used.

### 8. Delivery

Final delivery must state:

- what changed,
- what was verified,
- what was not verified,
- risks and mitigations,
- user next move.

For debugging tasks, include the exact debug status.

## Rules

1. Keep the lifecycle proportional to the task.
2. Do not use old-project paths, runtimes, services, or gates unless the user explicitly asks.
3. Do not claim completion without evidence.
4. If a lifecycle step is unavailable, name the blocker and use the closest safe path.
