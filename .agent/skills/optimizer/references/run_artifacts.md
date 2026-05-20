# Optimizer Run Artifacts

Use these files to make each optimization run restartable and reviewable.

## Directory Layout

Default path:

```text
docs/optimizer_runs/YYYY-MM-DD_<slug>/
  optimizer_brief.md
  ideas.tsv
  results.tsv
  report.md
```

Use a different path only when the repo already has an established experiment or benchmark directory.

## optimizer_brief.md

Required sections:

- Target: exact symbol/path allowed to change.
- Goal: user-facing objective.
- Scope in/out: target code, harness files, docs, runtime paths.
- Safety: live data, database, privacy, network, billing, external-write, or performance risks.
- Metrics: primary, guard, secondary, direction, source, threshold.
- Baseline plan: commands, corpus, repeat count, environment.
- Round plan: round count, experiment count, stop conditions.
- Review path: self-review or subagent review when allowed.

## ideas.tsv

Header:

```text
idea_id	round	status	hypothesis	expected_metric_effect	risk	touched_paths	notes
```

Statuses:

- `proposed`
- `selected`
- `running`
- `kept`
- `discarded`
- `blocked`

## results.tsv

Header:

```text
experiment_id	round	idea_id	status	guard_status	primary_metric	secondary_metrics	benchmark_command	verify_command	evidence_path	decision	notes
```

Use `baseline` as the first experiment id.

Decision values:

- `baseline`
- `keep`
- `discard`
- `combine_candidate`
- `needs_user`

## report.md

Required final sections:

- Objective
- Target
- Baseline
- Best Result
- Result Table
- Kept Changes
- Discarded Experiments
- Algorithm Explanation
- Validation Evidence
- Risks And Mitigations
- Next Ideas

Keep raw metric values visible. Do not replace them with only prose.
