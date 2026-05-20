---
description: Evidence-first workflow for direct user questions that require a grounded answer and confidence level
category: reasoning
status: active
safety: read-only
---

# Question Answering Workflow

Use this workflow when the user is primarily asking a question rather than requesting implementation.

## Steps

1. Clarify the real objective with `.agent/workflows/from_the_ground_up.md` Phase 1.
2. If the question is really a bug, root-cause, inconsistency, or incident question, switch to the normal task lifecycle and follow `.agent/workflows/from_the_ground_up.md` as the debugging contract instead of giving a quick direct answer.
3. If the answer depends on material claims, diagnostics, or disputed facts, run `.agent/workflows/show_me_evidence.md`.
4. Answer directly, using the strongest available evidence.
5. Append a confidence percentage at the end of the answer.
6. If confidence is below `90%`, say what evidence is missing and suggest the safest next checks.

## Notes

- Use this only for question-answering missions.
- Do not force the full workflow for tiny conversational replies that do not need heavy evidence.
- When a question turns into implementation or debugging work, switch to the normal task lifecycle.
- A question that asks "why is this broken?" is often debugging-critical even if phrased as a question.
