---
category: experience
status: active
safety: read-only
---

# Agent Tooling Experiences

1. When a workflow enumerates files, include a dynamic-glob step so static lists do not drift.
2. Pair new rule files with updates to rule-loading workflows when those workflows maintain examples.
3. `project_document_index.md` is the fastest cold-start context entry point when Secretary is active.
4. Harness UX should be objective-only: do not ask users to invoke skills, workflows, gates, or prompt templates when the agent can infer the safe lifecycle path.
5. When replacing a canonical script entrypoint, patch active workflows, skills, helper scripts, and docs in the same change.
6. Advisory debugging guidance is not enough by itself; wire proof-status requirements through rules, workflows, evidence review, and final delivery.
7. For long passive watch loops in terminal tools, use short repeated snapshots or helper scripts instead of giant inline commands that are hard to inspect.
8. For document discussion workflows, native document version history should remain the source of truth; in-document version lists are human-readable indexes, not replacements.
