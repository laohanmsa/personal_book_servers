---
description: Legacy wrapper for creating a new local skill in this repo
category: skills
status: deprecated
replaced_by: system skill `skill-creator`
safety: writes-local
---

## Status

Deprecated workflow. Prefer the system skill `skill-creator` for new skill creation and updates.

## Minimal Replacement Flow

1. Ask what the skill is for and what user prompts should trigger it.
2. Clarify scope (repo-local `.agent/skills` vs global Codex skill).
3. Use the system `skill-creator` guidance to plan reusable contents (helper scripts, reference files, or templates only if needed).
4. Create the skill under `.agent/skills/{skill_name}/`.
5. Write `SKILL.md` with clear `name` + `description` frontmatter and concise instructions.
6. Validate by trying one realistic invocation and refine.
7. Report the created/updated skill path to the user.

## Notes

- The old version hardcoded an unrelated "antigravity"/"code review skill" flow and is retained only as a compatibility alias.
- Keep this workflow as a redirect until all callers use `skill-creator` directly.
