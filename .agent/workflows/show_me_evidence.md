---
description: Verify agent's last reply has hard evidence for every assumption and conclusion; dig deeper if not
category: debugging
status: active
safety: read-only
---

# Show Me Evidence

This workflow is a quality-control pass on the agent's **most recent reply**. It ensures every assumption or conclusion is backed by **hard, verifiable evidence** — not speculation, not "it should work", not "probably".

Use this workflow as a blocking gate when:

- a debugging-critical task is about to present a causal conclusion
- the user has pushed back on missing proof or asked again for the real cause
- a previous hypothesis was refuted and the next diagnosis needs a fresh evidence check

---

## Step 1 — Extract Claims

Re-read the agent's last reply and list every:

- **Assumption** — something taken as true without explicit proof in the reply.
- **Conclusion** — a statement presented as a finding or diagnosis.

For each item, note:

| #   | Claim (verbatim or paraphrased) | Type (assumption / conclusion) | Evidence provided? | Evidence quality   |
| --- | ------------------------------- | ------------------------------ | ------------------ | ------------------ |
| 1   | …                               | …                              | Yes / No           | Hard / Soft / None |

### Evidence quality definitions

| Quality  | Meaning                                                                                                                                                    |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hard** | Direct, reproducible proof: command output, log line, source code snippet, API response, official doc quote. The evidence **logically entails** the claim. |
| **Soft** | Indirect or circumstantial: "it's likely because…", pattern matching, analogy, or a single data point that doesn't rule out alternatives.                  |
| **None** | No supporting data at all; pure speculation or assertion.                                                                                                  |

---

## Step 2 — Demand Hard Evidence for Soft / None

For every claim rated **Soft** or **None**:

1. **Design a test or investigation** that can produce Hard evidence.
   - Run the actual command / query / API call.
   - Read the actual source code (don't paraphrase from memory).
   - Inspect actual logs, database rows, or config files.
   - Capture the **exact output** — copy-paste, not summarise.

2. **Execute the investigation** and record results.

3. **Re-evaluate the claim**:
   - Does the hard evidence **directly support** the claim? → Keep the claim, attach proof.
   - Does the hard evidence **contradict** the claim? → Retract or correct the claim.
   - Is the evidence still **inconclusive**? → State so explicitly; do NOT upgrade to "confirmed".

If a claim is central to the root-cause story and still rates **Soft**, **None**, or **Inconclusive**, the user-facing result cannot present that story as the diagnosis. Continue the investigation or downgrade the status to a checkpoint.

---

## Step 3 — Deep Research

Regardless of whether evidence was found internally, do a **deep research pass** on the topic / problem:

1. **Official documentation** — Search for and read the relevant official docs (framework docs, API specs, protocol references). Quote the specific section that applies.

2. **Community discussion** — Search for GitHub issues, Stack Overflow threads, Discord/forum posts, or Reddit discussions related to the problem. Note any consensus or common pitfalls.

3. **Expert blogs / articles** — Look for in-depth technical blog posts or articles from recognized experts that discuss the topic, best practices, or known gotchas.

4. **Synthesise findings** — Summarise what the external sources say and how it aligns (or conflicts) with the agent's original claims.

---

## Step 4 — Deliver Verdict

Present a final summary:

### Evidence Report

For each original claim:

| #   | Claim | Verdict                                  | Hard Evidence              |
| --- | ----- | ---------------------------------------- | -------------------------- |
| 1   | …     | ✅ Confirmed / ❌ Refuted / ⚠️ Inconclusive | [exact evidence reference] |

### Key Corrections
List any claims that were wrong or misleading, with the corrected understanding.

### External Research Summary
Bullet-point summary of insights from official docs, community, and expert sources.

### Revised Conclusion
A corrected, evidence-backed conclusion that replaces or refines the agent's original reply.

### Root Cause Gate
State one of:

- `Root cause proved`
- `Breaking point proved but root cause not yet proved`
- `Inconclusive after safe decisive checks exhausted`

Only `Root cause proved` allows a final causal diagnosis. The other two statuses must include the remaining decisive checks or the concrete blocker.

---

## Rules

- **No hand-waving.** "It probably works" is not evidence.
- **No confirmation bias.** Actively look for evidence that **contradicts** the claim, not just evidence that supports it.
- **Show your work.** Every piece of hard evidence must be accompanied by the exact command, query, or file path that produced it.
- **Admit uncertainty.** If you cannot find hard evidence either way, say "inconclusive" — do not fabricate confidence.
- **No final diagnosis with soft evidence.** If any key causal claim is still Soft or None, the verdict cannot be a final diagnosis.
- **Retract bad narratives explicitly.** If the evidence audit overturns the previous explanation, say so directly instead of silently shifting the story.

## Evidence Requirements by Claim Type

| Claim Type                  | Required Evidence         | Command                                                     |
| --------------------------- | ------------------------- | ----------------------------------------------------------- |
| "Connection is warm/alive"  | `ESTAB` in socket state   | `ss -tnp \| grep "pid=PID"`                                 |
| "Thread is running"         | Thread visible in `/proc` | `ls /proc/PID/task/ \| wc -l` + `cat /proc/PID/task/*/comm` |
| "Process is running"        | Process in `ps` output    | `pgrep -af "binary_name"`                                   |
| "Port is open"              | Listener in socket table  | `ss -tlnp \| grep :PORT`                                    |
| "API returns X"             | Actual response body      | `curl -s URL` with full output                              |
| "Library does X internally" | Source code line          | `grep -n "pattern" source_file.cpp`                         |
| "Config is set to X"        | File content              | `cat config_file \| grep KEY`                               |
