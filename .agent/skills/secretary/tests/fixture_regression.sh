#!/usr/bin/env bash
set -euo pipefail

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

mkdir -p "$TMP_ROOT/docs" "$TMP_ROOT/.agent/rules" "$TMP_ROOT/.agent/skills/example"
cat >"$TMP_ROOT/AGENTS.md" <<'EOF'
# Fixture Agents
EOF
cat >"$TMP_ROOT/docs/context.md" <<'EOF'
# Context Guide

This fixture explains the project context and indexing behavior.
EOF
cat >"$TMP_ROOT/.agent/rules/00-rule.md" <<'EOF'
# Fixture Rule

Always verify fixture behavior.
EOF
cat >"$TMP_ROOT/.agent/skills/example/SKILL.md" <<'EOF'
---
name: example
description: fixture skill
---

# Example Skill
EOF

SECRETARY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/secretary.sh"
SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" scan
grep -q "docs/context.md" "$TMP_ROOT/project_document_index.md"
grep -q ".agent/rules/00-rule.md" "$TMP_ROOT/project_document_index.md"

SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" ask "context indexing" --json >/tmp/secretary_fixture.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/secretary_fixture.json'))
assert payload['sources']
assert payload['sources'][0]['path'] == 'docs/context.md'
PY

echo "secretary fixture regression passed"
