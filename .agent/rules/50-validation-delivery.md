---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Validation And Delivery

Work is not complete until it is verified and reviewable.

1. For code changes, write or update focused tests before or with the fix when practical; use mocks, fakes, fixtures, or dry-run modes when real calls are unsafe.
2. Choose validation based on the actual changed surface: unit tests, integration tests, linters, type checks, build checks, rendered screenshots, command smoke tests, or document review.
3. Do not run inherited app-specific gates unless this repository defines them or the user explicitly asks for that old project path.
4. Do not start local or remote app stacks unless the user explicitly asks for runtime work or the project workflow requires it and the risk is understood.
5. Material feature/bugfix/code changes require a corresponding durable doc update when behavior, APIs, operations, or user workflows change.
6. When docs are added, renamed, or materially updated, refresh the document index if the project uses one.
7. When valuable reusable knowledge is learned, append one concise line to the relevant `.agent/experiences/` file if that experience system is active for the repo.
8. For programming, debugging, or research, run an adversarial review round when tool policy permits; if subagents are unavailable or disallowed, perform an explicit self-review and do not claim independent review.
9. User-facing final results must be sectional with `---` between major sections.
10. Normal final results must include: Alignment, Task Recap, Suggestions, Risks And Mitigation, Reasoning And Evidence, and User Next Move.
11. Debugging final results must include Debug Status using the exact allowed status strings from `20-evidence-debugging.md`.
12. Direct question-answering missions must follow `.agent/workflows/question_answering.md` and end with a confidence percentage.
13. If the user explicitly asks to close/end the session, follow `.agent/skills/session_close/SKILL.md` when present.
