---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Git And Isolation

The agent owns routine git hygiene.

1. Do not implement non-trivial feature, bugfix, refactor, or deployment-sensitive work directly on `main` unless the user explicitly requests it, the task is tiny, or safe isolation is impractical and explained.
2. Use `codex/<task-slug>` for new task branches/worktrees by default.
3. If a clean integration lane is needed, create or reuse a clearly named worktree for that task and verify its branch before using it.
4. Handle routine git work without burdening the user when the directory is a git repository: fetch, inspect deltas, safe stash/pop, merge or rebase only when appropriate, stage, commit, push, and safe destination merge when delegated.
5. If the directory is not a git repository, state that git-based isolation, diffing, and status checks are unavailable.
6. Ask before destructive commands, history rewrites, force-pushes, ambiguous branch selection, conflicts requiring judgment, or secret/compliance concerns.
7. Never revert user changes unless the user explicitly asks; work around unrelated dirty files.
