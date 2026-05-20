---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Plan Mode Criteria Gate

Plan Mode plans must be milestone-based and independently reviewable before
implementation begins.

1. Every Plan Mode plan must be structured as stages or milestones.
2. Every stage or milestone must include:
   - Target: the concrete state to reach.
   - Criteria: clear checks that prove the target was reached.
   - Evidence path: how each criterion will be verified, such as tests, logs,
     files, screenshots, docs, runtime checks, command output, or review output.
   - Exit condition: the minimum standard required before moving to the next
     stage.
3. Criteria must be clear, objective, and verifiable. Vague criteria such as
   "works", "good enough", "clean", or "done" are invalid unless converted into
   concrete checks.
4. A critic subagent must review the plan's stages, targets, criteria, evidence
   paths, and exit conditions before implementation begins when subagents are
   available and higher-priority tool policy permits subagent use.
5. If a critic subagent is unavailable or blocked by higher-priority policy,
   state the blocker and perform the same critic review explicitly before
   implementation.
6. The critic review must classify each criterion as exactly one of:
   `Clear And Verifiable`, `Unclear`, `Not Verifiable`, or `Missing`.
7. Implementation must not begin while any stage criterion is `Unclear`,
   `Not Verifiable`, or `Missing`.
8. If the plan materially changes mid-mission, rerun the same criteria review
   before executing the changed stage.
