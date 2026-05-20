#!/usr/bin/env bash
set -euo pipefail

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

mkdir -p "$TMP_ROOT/docs" "$TMP_ROOT/.agent/rules" "$TMP_ROOT/.agent/skills/example" "$TMP_ROOT/.pytest_cache"
cat >"$TMP_ROOT/AGENTS.md" <<'EOF'
# Fixture Agents
EOF
cat >"$TMP_ROOT/docs/context.md" <<'EOF'
# Context Guide

This fixture explains the project context and indexing behavior.
EOF
cat >"$TMP_ROOT/docs/chinese.md" <<'EOF'
# 中文索引指南

这个文档说明中文索引查询流程。
EOF
cat >"$TMP_ROOT/docs/maintenance.md" <<'EOF'
# Maintenance Notes

This document explains maintain checks for the harness.
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
cat >"$TMP_ROOT/.pytest_cache/README.md" <<'EOF'
# pytest cache directory

This generated cache should not be indexed as project documentation.
EOF

SECRETARY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/secretary.sh"
SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" scan
grep -q "docs/context.md" "$TMP_ROOT/project_document_index.md"
grep -q ".agent/rules/00-rule.md" "$TMP_ROOT/project_document_index.md"
if grep -Fq ".pytest_cache/README.md" "$TMP_ROOT/project_document_index.md"; then
  echo "generated pytest cache was indexed" >&2
  exit 1
fi

SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" ask "context indexing" --json >/tmp/secretary_fixture.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/secretary_fixture.json'))
assert payload['sources']
assert payload['sources'][0]['path'] == 'docs/context.md'
PY

SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" ask "索引 查询" --json >/tmp/secretary_fixture_chinese.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/secretary_fixture_chinese.json'))
assert payload['sources']
assert payload['sources'][0]['path'] == 'docs/chinese.md'
PY

SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" ask "zzzz_nomatch" --json >/tmp/secretary_fixture_nomatch.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/secretary_fixture_nomatch.json'))
assert payload['coverage'] == 'none'
assert payload['sources'] == []
PY

SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" ask "ai" --json >/tmp/secretary_fixture_short_ascii.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/secretary_fixture_short_ascii.json'))
assert payload['coverage'] == 'none'
assert payload['sources'] == []
PY

cat >>"$TMP_ROOT/docs/context.md" <<'EOF'

Changed after indexing.
EOF
set +e
SECRETARY_PROJECT_ROOT="$TMP_ROOT" bash "$SECRETARY" doctor >/tmp/secretary_fixture_doctor_changed.txt
doctor_code=$?
set -e
test "$doctor_code" -eq 1
grep -q "changed_indexed_paths: 1" /tmp/secretary_fixture_doctor_changed.txt

echo "secretary fixture regression passed"
