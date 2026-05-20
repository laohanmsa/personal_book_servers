---
description: Create a task worktree and codex branch for isolated implementation and review
category: git
status: active
safety: writes-local
---

# Task Worktree Workflow

Use this workflow for non-trivial git-backed work that should not happen directly
on `main`.

## Preconditions

1. Confirm the directory is a git repository.
2. Inspect existing worktrees and branch ownership.
3. Preserve unrelated local changes.

## Steps

1. Update local refs:

```bash
git fetch origin
```

2. Choose a slug and create a branch/worktree:

```bash
TASK_SLUG="<task-slug>"
WORKTREE_PATH="../$(basename "$PWD")-${TASK_SLUG}"
BRANCH_NAME="codex/${TASK_SLUG}"

git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" origin/main
```

3. Prepare context in the new worktree:

```bash
cd "$WORKTREE_PATH"
bash .agent/skills/secretary/secretary.sh ask "$TASK_SLUG" --level L1
```

4. Do the work on the task branch:

- implement,
- validate,
- review,
- commit logical units,
- push if remote review or shipping is delegated.

5. Merge only after validation and review.

6. Clean up only when safe:

```bash
git worktree remove "$WORKTREE_PATH"
git branch -d "$BRANCH_NAME"
```

## Notes

1. Keep one logical task per worktree.
2. Use a second worktree when independent review or integration isolation helps.
3. Do not deploy or mutate runtime systems from a task branch unless the user explicitly authorizes that path.
4. If the current work is already isolated on a suitable branch/worktree, reuse it.
