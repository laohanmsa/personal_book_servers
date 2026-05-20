---
description: Commit grouped changes using Conventional Commits format
category: git
status: active
safety: writes-local
---

# Git Add And Commit Workflow

Use this workflow for the commit step inside the broader delivery path. Do not
treat committing as a substitute for validation or review.

## Preconditions

1. Confirm the directory is a git repository.
2. Inspect `git status --short --branch`.
3. Identify unrelated local changes and leave them untouched.
4. Run the relevant validation for the changed surface.

## When To Commit

Commit after a logical unit of work:

- feature implementation plus tests,
- bug fix plus regression test,
- refactor plus validation,
- documentation update,
- configuration or harness cleanup.

Do not commit after every single file change.

## Message Format

Use Conventional Commits:

```text
<type>(<scope>): <description>

[optional body]
```

Common types:

- `feat`
- `fix`
- `refactor`
- `test`
- `docs`
- `style`
- `chore`
- `perf`

Choose a scope from the changed component, directory, or feature, such as
`reader`, `docs`, `agent`, `secretary`, `parser`, `api`, or `ui`.

## Steps

1. Identify related files.
2. Stage only the intended paths:

```bash
git add <path1> <path2>
```

3. Commit:

```bash
git commit -m "docs(agent): clean reusable harness rules"
```

4. Verify:

```bash
git log -1 --oneline
git status --short
```

5. Push only when the user delegated shipping or the workflow requires remote review:

```bash
git push
```

## Rules

1. Never stage unrelated user changes.
2. Ask before history rewrites, force pushes, destructive cleanup, or ambiguous conflict resolution.
3. Do not deploy or mutate runtime systems from this workflow.
4. If the repo has no git metadata, report that commit workflow is unavailable.
