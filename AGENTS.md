# Project Template Agent Instructions

First load and apply the project-independent harness rules in `basicagents.md`.
Then apply this file's project-specific instructions. If the two files conflict,
the more specific `AGENTS.md` rule wins unless a higher-priority system or
developer instruction says otherwise.

Also load all applicable rules in `.agent/rules` before acting or replying.
Pay special attention to `.agent/rules/50-validation-delivery.md` for every
user-facing result.

## Project Identity

This repository is a reusable Agent Harness template. It can be copied into a
concrete project and then specialized through `AGENTS.md`.

Current committed project content should stay lightweight:

1. Agent harness files under `.agent/`.
2. Root agent entry files: `AGENTS.md`, `basicagents.md`, and `README.md`.
3. Generic harness references, workflows, skills, rules, and experiences.

No application runtime, deployment target, database, or app-specific post-change
gate has been established in this template yet.

Local source texts, datasets, generated indexes, runtime outputs, and
project-specific private materials should remain untracked unless the user
explicitly decides they belong in a concrete project repository.

## Inherited Harness Cleanup

This harness was adapted from another repository. Treat remaining inherited
runtime, deployment, account, or domain-specific references as cleanup targets,
not active template instructions, unless the user explicitly asks to preserve or
adapt them.

## Project-Specific Validation

For documentation-only harness changes:

1. Re-open the edited files.
2. Verify `AGENTS.md` points to `basicagents.md`.
3. Verify old-project deployment/runtime gates are not present in active
   instructions unless intentionally documented as inactive legacy context.

For future code or app changes, choose validation based on the actual project
stack once it exists. Do not substitute inherited old-project gates.

## Document Index

`project_document_index.md` and related `project_document_index.*`,
`project_context.sqlite`, and `project_document_snapshot.tsv` files are
Secretary-generated artifacts.

They may be refreshed when documentation changes are meant to be durable, but
they should not be treated as hand-authored source files or committed template
content by default.
