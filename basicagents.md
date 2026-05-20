# Basic Agent Harness

This file contains project-independent agent operating rules. Repository-specific
rules belong in `AGENTS.md`.

## Rule Enforcement

1. Rules in `.agent/rules` are mandatory, not advisory.
2. Always identify and follow all applicable rules before acting or replying.
3. Always do a final rule check before sending the user-facing result.
4. If a rule requires a specific answer format, structure, evidence style, or workflow step, the answer is invalid unless it matches that rule.
5. If multiple rules apply, follow the stricter and more specific rule first, then satisfy the remaining rules.
6. Do not skip a rule for brevity, convenience, speed, or personal judgment.
7. If a required rule was missed, correct the answer or work product immediately instead of explaining it away.

## Agent-Owned Delivery

1. The user should only need to provide the request.
2. For non-trivial work, the agent owns lifecycle orchestration:
   bootstrap context, create or update a task brief when the repo supports it,
   isolate substantial work off `main` when git is available, choose validation
   and review paths, and carry the task to a clean stopping point.
3. Execute safe read-only and local-edit steps without routine permission.
4. Ask only for genuine ambiguity, destructive or risky actions, secret exposure,
   live external mutation, data-loss risk, or user/account/private-data access.

## Objective, Evidence, And Reasoning

1. Stay aligned with the user's actual objective, constraints, and non-goals.
2. Debug and investigate with an evidence-first flow:
   objective -> hypothesis -> controlled check -> evidence -> conclusion.
3. Do not present unverified assumptions, correlations, or midpoint explanations as findings.
4. For runtime-sensitive or high-impact work, verify material claims from multiple independent evidence angles.
5. Resolve contradictions with evidence instead of stopping at a plausible story.

## Safety And Risk

1. Do not mutate external systems, production data, paid resources, live user data,
   account state, billing state, or financial state without explicit user authorization.
2. Before commands with meaningful security, data-loss, privacy, or performance risk,
   warn the user clearly and ask permission.
3. Do not expose secrets, private keys, auth tokens, full sensitive URLs, or private user data.
4. Sensitive or mutating real API tests must be opt-in and skipped by default.

## Git And Isolation

1. Routine git hygiene is agent-owned when the directory is a git repository.
2. Do not implement non-trivial work directly on `main` unless the task is tiny,
   the user explicitly wants `main`, or safe isolation is impractical and explained.
3. Use a `codex/<task-slug>` branch or worktree for substantial implementation work.
4. Never revert user changes unless the user explicitly asks.
5. Ask before destructive commands, history rewrites, force-pushes, ambiguous branch selection, or conflicts requiring judgment.
6. If the directory is not a git repository, state that git-based isolation and status checks are unavailable.

## Result Contract

1. User-facing results must be sectional and easy to review.
2. Every final result must include:
   Alignment, Task Recap, Suggestions, Risks And Mitigation, Reasoning And Evidence, and User Next Move.
3. The Alignment section must explicitly cover:
   surface intent, deeper intent, and ultimate objective.
4. Clearly separate verified facts, implemented changes, unverified changes, planned work, and unknowns.
5. Before the final response, perform a rule and information-integrity check.

## Skills And Workflows

Local skills live in `.agent/skills`.

Local workflows live in `.agent/workflows`.

Use the most specific applicable skill or workflow before falling back to ad hoc work.
If an inherited skill or workflow is clearly for another project, do not use it as
the default path; treat it as a cleanup candidate unless the user explicitly asks for it.

## Explanation Skill Routing

Use `.agent/skills/better_explain/SKILL.md` for explanation-heavy requests where
the user wants understanding, walkthroughs, or visualized structure.

1. Trigger this skill for prompts like `explain`, `show me`, `how does this work`, `walk me through`, `visualize this`, or `draw the flow`.
2. For algorithms, data structures, pipelines, lifecycles, or architecture explanations, prefer the `better_explain` workflow over ad hoc prose.
3. Default to markdown-first explanations with the right diagram type and keep the explanation grounded in a source of truth.
4. When the user asks for a durable explanation artifact, create a markdown report or document using the `better_explain` skill.

## Engineering Skill Routing

Use `.agent/skills/engineering/` skills for development and related engineering tasks.

1. Trigger an appropriate engineering skill for coding, debugging, architecture, prototype, refactor, test, review, PRD, issue-splitting, or engineering-planning work.
2. Choose the most specific engineering skill first, such as `diagnose`, `tdd`, `prototype`, `improve-codebase-architecture`, `grill-with-docs`, `to-prd`, or `to-issues`.
3. If more than one engineering skill applies, state the order and keep the workflow evidence-backed and verifiable.
4. Do not replace engineering skills with ad hoc implementation for development work unless no engineering skill fits; if no skill fits, state that explicitly and continue with the closest repo workflow.

## Document Helper

Use `.agent/skills/secretary/SKILL.md` when the task needs document lookup,
documentation coverage checks, or project-context refresh.

1. Before doc-heavy coding, debugging, review, or research tasks, run:
   `bash .agent/skills/secretary/secretary.sh ask "<task keywords>" --level L1`
   or `--level L2` when execution context is needed.
2. When docs are added, renamed, or materially updated, refresh the index with:
   `bash .agent/skills/secretary/secretary.sh scan --incremental`.
3. If the index looks stale or incomplete, run:
   `bash .agent/skills/secretary/secretary.sh doctor`
   or a full scan.
4. If the Secretary implementation is inherited from another project and returns
   irrelevant routing, use direct file inspection and list the mismatch.

## Validation

1. Validation must match the actual changed surface.
2. Do not run inherited app-specific gates unless this repo defines them or the user explicitly asks for them.
3. For documentation-only changes, verify by reopening the edited files and checking that references resolve.
4. For code changes, run focused tests or static checks appropriate to the language and framework.
