---
name: optimizer
description: Optimize a specific function, method, module, algorithm, or performance/quality-critical workflow through evidence-first, bounded experiment rounds. Use when the user asks to improve, optimize, tune, speed up, refactor, or increase quality/coverage/reliability for an algorithm, search/discovery/scoring/ranking/parser/scheduler, or any function where measurable quality, correctness, coverage, speed, cost, memory, or reliability goals can be defined and compared against a baseline.
category: engineering
status: active
safety: writes-local
---

# Optimizer

## Overview

Use this skill to improve code by running controlled optimization experiments, not by guessing. The optimizer owns the loop: define measurable success, record the baseline, generate non-overlapping ideas, implement focused experiments, verify each result, keep only proven improvements, and deliver an explanation of what changed and why.

The default posture is quiet execution after the contract is clear. Do not interrupt the user mid-run unless a safety boundary, missing objective, missing oracle/harness, destructive action, live-state mutation, or repeated decisive failure blocks progress.

## Non-Negotiables

1. Do not optimize without a frozen target, frozen evaluator, baseline, and guard checks.
2. Do not change the benchmark, tests, labels, fixtures, or metric extraction during optimization unless the user explicitly asks for harness work.
3. Do not accept a faster result that fails correctness, safety, or regression guards.
4. Do not hide raw metrics behind a single opaque score. Show the raw result table.
5. Do not mutate production data, live user data, billing state, external systems, queues, caches, or databases without explicit authorization.
6. Use subagents only when the current tool policy and user authorization allow them. If blocked, run the same roles sequentially and state that independent subagent review was not used.

## Quick Start

When durable run artifacts are useful, initialize them before the baseline:

```bash
python3 .agent/skills/optimizer/scripts/init_optimizer_run.py \
  --slug "<task-slug>" \
  --target "<path or symbol>" \
  --goal "<optimization objective>" \
  --primary-metric "<metric name and direction>" \
  --guard-metric "<must-not-regress check>" \
  --benchmark-command "<command that measures metrics>" \
  --verify-command "<command that proves correctness>"
```

The script creates:

- `optimizer_brief.md`
- `ideas.tsv`
- `results.tsv`
- `report.md`

Read `references/metric_patterns.md` when the user's metric is vague or the task needs quality, coverage, ranking, or no-oracle measurement design. Read `references/run_artifacts.md` when creating or filling optimizer artifacts manually.

## Workflow

### 1. Lock The Optimization Contract

Capture:

- Target: exact function, method, module, route, command, or algorithm boundary allowed to change.
- Goal: user-visible improvement.
- Non-goals: behavior, APIs, data formats, or files that must not change.
- Safety boundaries: live state, user data, data stores, external writes, billing, privacy, and runtime performance risk.
- Budget: default to 3 rounds, 2-4 experiments per round, and a fixed maximum runtime per benchmark run.

If the target or success metric is ambiguous enough to change the implementation strategy, ask one concise question. Otherwise infer conservatively from code and tests.

### 2. Define The Measurement Contract

Define metrics before proposing ideas:

- Primary metric: the main thing to improve.
- Guard metrics: correctness, invariants, API compatibility, data safety, and user-facing behavior that must not regress.
- Secondary metrics: runtime, p95/p99 latency, memory, query count, cost, code complexity, or maintainability.
- Noise rule: minimum improvement threshold and repeat count needed before a metric is treated as real.

For discovery/search/set algorithms, make quality concrete with precision, recall/coverage, false negative count, duplicate rate, invalid result rate, and value-weighted missed coverage when applicable.

If no oracle exists, build one safely from golden examples, synthetic seeded cases, metamorphic tests, invariant checks, sampled manual labels, and shadow comparison against the current algorithm. State the limitation clearly.

### 3. Establish The Baseline

Run the current implementation before changing target code.

Record:

- command and environment
- input corpus or fixtures
- random seed, sample size, and run count
- raw metric values
- median/p95 when measuring speed
- failed checks or warnings

The baseline row is experiment `baseline`. All later claims compare to it.

### 4. Build And Maintain The Idea Ledger

Generate optimization ideas only after the baseline is known. Each idea needs:

- stable id
- hypothesis
- expected metric effect
- expected risk
- touched files
- validation command
- status: `proposed`, `selected`, `running`, `kept`, `discarded`, or `blocked`

Avoid overlap by checking the ledger before starting a new experiment. Prefer diverse ideas across algorithmic pruning, data structures, caching, batching, search order, approximate prefilters, query shape, allocation reduction, and concurrency only where safe.

### 5. Run Bounded Experiment Rounds

Each round:

1. Select the most promising non-overlapping ideas.
2. Implement one idea per experiment branch/worktree or one carefully isolated patch at a time.
3. Run correctness guards first.
4. Run the benchmark enough times to satisfy the noise rule.
5. Review the diff for maintainability, hidden harness changes, and behavior drift.
6. Keep only experiments that improve the primary metric without guard regressions.
7. Revert or discard losing patches.
8. Update the result table before starting the next round.

Default stopping conditions:

- 3 completed rounds.
- No real improvement after 2 consecutive rounds.
- Best result reaches the target.
- Further work requires user authorization or a new benchmark/labeling task.

### 6. Select The Winner

Rank candidates lexicographically:

1. All guard checks pass.
2. Primary metric improves beyond the noise threshold.
3. Quality/coverage regressions are absent or explicitly accepted.
4. Runtime/cost/memory improves or stays within limits.
5. Simpler, smaller, more maintainable code wins ties.

If two candidates improve different objectives, do not merge them blindly. Combine only after a controlled combined experiment proves the interaction.

### 7. Deliver The Report

The final result must include:

- target and objective
- baseline vs best result table
- experiments kept and discarded
- exact validation commands
- explanation of the algorithmic improvement
- residual risks and next optimization ideas
- files changed

For user-facing explanation, focus on what changed in the function/algorithm, why it improves the measured objective, and what guardrails prevent metric overfitting.

## Role Pattern

When subagents are allowed:

- Coordinator: owns target, metric contract, ledger, result table, and final merge.
- Metric Designer: makes vague objectives concrete and designs oracle/proxy checks.
- Idea Proposer: proposes non-overlapping hypotheses against the ledger.
- Implementer: applies one selected idea in a bounded write scope.
- Reviewer: checks diff, harness integrity, regression risk, and metric interpretation.
- Benchmark Analyst: compares raw outputs, noise, and tradeoffs.

When subagents are not allowed, execute the same roles sequentially and record the role outputs in the artifacts.

## Validation Checklist

Before claiming success:

- baseline was captured before target edits
- harness and target changes are separated
- all guard checks passed
- metric improvement exceeds the noise rule
- result table includes both losers and winner
- diff was reviewed for hidden behavior drift
- app-specific post-change gates were run when touched paths require them
- docs/index updates were completed when repo rules require them
