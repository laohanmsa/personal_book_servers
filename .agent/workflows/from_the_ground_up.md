---
description: Systematic debugging methodology — clarify objective, pinpoint the break, gather context, then probe efficiently
category: debugging
status: active
safety: read-only
---

# From the Ground Up

A 4-phase debugging workflow. Do NOT skip phases. Each phase gates the next.

Use this workflow for bug, root-cause, inconsistency, incident, and verification-failure tasks. It is the default debugging path when the user is asking why something is broken.

---

## Phase 1 — Clear the Objective

**What is the user actually trying to accomplish?**

1. Re-read the last few user prompts. Identify the **single user-facing goal** (not the technical symptom, the *outcome* they want).
2. State it in one sentence, e.g.: "User wants the imported text to render correctly in the reader."
3. Rate your confidence (0–100%).
4. **If confidence < 90%, STOP and ask the user** to confirm the objective before proceeding. Do NOT guess.

Output: A single sentence starting with "Objective:" followed by confidence %.

---

## Phase 2 — Pinpoint the Breaking Point

**There is ONE immediate problem. Find the exact break in the calling chain.**

1. Trace the full call chain from the user-facing symptom back to the data source:
   - UI → View/API → Client → Service → External API / DB
2. At each hop, verify: "Does this step behave as expected?"
   - Run the actual command, curl the actual endpoint, read the actual log line.
   - Do NOT speculate — produce hard evidence at every hop.
3. Stop at the **first hop that does NOT behave as expected**. That is the breaking point.
4. State the breaking point clearly: "`X` should return `Y`, but instead returns `Z`."
5. Treat the proved breaking point as the **minimum proof bar** before any user-facing diagnosis. A breaking point alone does not close the task if deeper safe checks remain.

Output: The breaking point in one sentence, with the exact evidence (command + output).

> [!IMPORTANT]
> If the breaking point reveals a deeper issue (e.g. the service is misconfigured, not just the caller), this triggers a **sub-investigation** — repeat Phase 2 from the breaking point downward until you reach the root.

---

## Phase 3 — Prepare Context

**Before solving, gather the specs and implementation details needed to understand WHY the break exists.**

1. **Official specs** — Read the relevant protocol, API, framework, or file-format documentation.
2. **Implementation** — Read the actual source code at and around the breaking point. Understand the design intent, not just what the code does.
3. **Related memory** — Check `.agent/experiences/` and project docs for known patterns, gotchas, or prior fixes related to this area.
4. **Summarise** the context in ≤5 bullet points that are directly relevant to the break.

Output: A short context summary. Only facts, no speculation.

> [!TIP]
> If external docs are needed (e.g. API specs), use web search / browser tools to fetch them. Do not rely on cached knowledge that may be outdated.

---

## Phase 4 — Probe and Fix

**Now — and only now — design and execute the fix.**

1. **Hypothesis**: Based on Phase 2 (break) + Phase 3 (context), state your hypothesis for the root cause.
2. **Smallest possible test**: Design a test that confirms or refutes the hypothesis. Run it.
3. **Fix**: If confirmed, implement the minimal fix. If refuted, return to Phase 2 and switch evidence dimension.
4. **Verify**: Re-run the original failing scenario end-to-end. Does the user-facing symptom resolve?
5. **Evidence**: Capture the before/after evidence (command outputs, screenshots, logs).

Output: The fix + end-to-end verification evidence.

## Checkpoint Contract

If you must update the user before root cause proof is complete, report only a checkpoint:

```markdown
Checkpoint
- Objective: ...
- Breaking point proved: yes/no
- Root cause proved: yes/no
- Remaining decisive checks: ...
```

Do not present a midpoint explanation as a final diagnosis. A debugging task is only complete when the root cause is proved or when the remaining decisive checks have been exhausted and explicitly named.

---

## Rules

- **No skipping phases.** Phase 3 before Phase 2 = wasted context. Phase 4 before Phase 3 = blind fix.
- **One problem at a time.** If you discover multiple issues, handle them sequentially, each with its own Phase 2→4 cycle.
- **Evidence at every hop.** "It should work" is not evidence. Run the command, show the output.
- **Ask when unsure.** Asking the user is always better than a wrong assumption cascading through 3 phases.
- **No final diagnosis before proof status is explicit.** Until root cause is proved, use the checkpoint contract or state that the trace is inconclusive.
- **A refuted hypothesis changes the next move.** The next cycle must use a different evidence dimension, control, or trace layer instead of repeating the same style of guess.
