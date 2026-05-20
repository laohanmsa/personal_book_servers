---
name: Git Autopilot
description: Own git planning and execution for this repo. Use when a task needs branch/worktree isolation, clean integration, stash/restore, merge, push, or delegated git handling.
category: ops
status: active
safety: writes-local
---

# Git Autopilot

Use this skill whenever git handling is part of the mission, not as a last-minute cleanup step.

The user should not need to manage routine branch, worktree, stash, merge, or
push chores. Ask only before destructive operations, ambiguous branch choices,
history rewrites, force-pushes, risky conflict resolution, or secret/compliance concerns.

## Preflight

If the directory is not a git repository, report that git automation is unavailable
and continue with file-level validation.

When git is available, inspect:

```bash
git status --short --branch
git branch --show-current
git worktree list --porcelain
git stash list
git rev-parse HEAD
git rev-parse --verify origin/main 2>/dev/null || true
```

Then decide:

- implementation lane
- integration lane
- dirt protection plan
- validation and review path
- cleanup plan

## Defaults

1. Non-trivial implementation belongs on a dedicated `codex/<slug>` branch or worktree.
2. Reuse a suitable task worktree if it already exists.
3. Keep unrelated local changes untouched.
4. Stage and commit coherent units only.
5. Do not deploy or mutate runtime systems as part of git handling unless the user explicitly authorized that work.
6. If docs changed and Secretary is active, refresh the index before final delivery.

## Dirty Workspace Strategy

Choose the lowest-risk option:

- scoped stage/commit when unrelated changes can remain untouched,
- temporary stash with restore when local dirt is clearly unrelated,
- clean worktree plus selective copy/cherry-pick when the current lane is too noisy.

Never revert user changes without explicit instruction.

## Reporting

Name the git actions taken:

- fetched refs,
- created or reused branch/worktree,
- stashed/restored unrelated edits,
- committed logical units,
- pushed branches,
- merged integration branch,
- skipped git because the directory is not a repository.
