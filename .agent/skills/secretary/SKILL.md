---
name: Secretary
description: Project context maintainer that indexes repository documentation, checks index health, and retrieves ranked context at multiple detail levels.
category: ops
status: active
safety: read-only
---

# Secretary

Secretary is the repository context maintainer. It is intentionally project-generic.

It provides:

1. Documentation indexing across common repository documentation locations.
2. Fast ranked lookup for task-specific context.
3. Health checks for missing or stale index artifacts.
4. Agent-ready context packs grouped by priority.

## When To Use

Use this skill when you need to:

1. Find relevant docs before coding, debugging, review, or research.
2. Refresh documentation context after docs, rules, skills, or workflows change.
3. Check whether the index is fresh enough to trust.
4. Prepare a compact context bundle for another agent step.

## Commands

### Scan

```bash
bash .agent/skills/secretary/secretary.sh scan
bash .agent/skills/secretary/secretary.sh scan --incremental
```

Builds:

- `project_document_index.md`
- `project_document_index.json`
- `project_document_index.tsv`
- `project_document_snapshot.tsv`

### Ask

```bash
bash .agent/skills/secretary/secretary.sh ask "<query>" --level L1
```

Options:

- `--level L0|L1|L2|L3`
- `--json`
- `--top-k N`
- `--component <label>`
- `--type <doc_type>`

### Pack

```bash
bash .agent/skills/secretary/secretary.sh pack "<query>" --level L2
```

Returns:

- `must_read`
- `supporting`
- `historical`

### Doctor

```bash
bash .agent/skills/secretary/secretary.sh doctor
```

Checks:

- index file presence
- document count
- stale document count
- missing indexed paths

### Maintain

```bash
bash .agent/skills/secretary/secretary.sh maintain
```

Runs incremental scan, doctor, and writes `project_context_health.md`.

## Indexed Locations

Secretary discovers documentation from generic locations:

- root `README*`, `AGENTS.md`, `basicagents.md`
- `docs/`
- `document/`
- `research/`
- `.agent/rules/`
- `.agent/workflows/`
- `.agent/references/`
- `.agent/experiences/`
- `.agent/skills/*/SKILL.md`

It avoids generated caches, dependency directories, VCS internals, and large raw
source assets by default.

## Output Contract

`ask --json` returns:

- `query`
- `level`
- `summary`
- `coverage`
- `sources[]`

Each source includes:

- `path`
- `title`
- `score`
- `why_matched`
- `freshness`
- `component`
- `doc_type`
- `mtime`

## Workflow Guidance

Before doc-heavy work:

1. Run `ask` with task keywords.
2. Read the top ranked docs.
3. If results look stale or incomplete, run `doctor` then `scan`.
4. After material docs/rules/skills/workflows updates, run `scan --incremental`.

## Safety

Secretary is read-only with respect to source documents. It writes only index and
health artifacts at the project root.
