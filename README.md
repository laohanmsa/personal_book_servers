# Project Template Agent Harness

This repository is a reusable Agent Harness template for Codex-style project
work. It provides shared rules, skills, workflows, references, and a Secretary
indexer that can be copied into a new project and then specialized locally.

## Repository Layout

- `AGENTS.md`: project-specific entrypoint. Keep concrete project identity,
  runtime facts, and validation notes here after copying the template.
- `basicagents.md`: project-independent harness rules and routing.
- `.agent/rules/`: mandatory operating rules.
- `.agent/skills/`: reusable local skills, including Secretary.
- `.agent/workflows/`: reusable local workflows.
- `.agent/references/`: style and writing references used by rules or skills.
- `.agent/experiences/`: short reusable lessons for future work.

## First Steps In A New Project

1. Copy this repository or use it as a template.
2. Edit `AGENTS.md` to describe the concrete project.
3. Keep generic behavior in `basicagents.md`; keep project-specific behavior in
   `AGENTS.md`.
4. Refresh the document index:

   ```bash
   bash .agent/skills/secretary/secretary.sh scan
   ```

5. Check index health:

   ```bash
   bash .agent/skills/secretary/secretary.sh doctor
   ```

## Generated Files

Secretary writes these root-level artifacts when it scans the repository:

- `project_document_index.md`
- `project_document_index.json`
- `project_document_index.tsv`
- `project_document_snapshot.tsv`
- `project_context_health.md`

These files are ignored by Git because they can be regenerated from source
documents.

## Validation

For harness-only edits, use focused validation:

```bash
python3 .agent/scripts/lint_agent_docs.py
bash .agent/skills/secretary/tests/verify_secretary.sh
bash .agent/skills/secretary/tests/fixture_regression.sh
```

For future application code, choose tests and build checks based on the actual
project stack instead of inherited workflows.
