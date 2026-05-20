#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${SECRETARY_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
SECRETARY="$PROJECT_ROOT/.agent/skills/secretary/secretary.sh"

bash "$SECRETARY" scan
test -s "$PROJECT_ROOT/project_document_index.md"
test -s "$PROJECT_ROOT/project_document_index.json"
test -s "$PROJECT_ROOT/project_document_index.tsv"
test -s "$PROJECT_ROOT/project_document_snapshot.tsv"

bash "$SECRETARY" ask "agent rules" --level L1 --top-k 3 >/tmp/secretary_ask.txt
grep -q "path:" /tmp/secretary_ask.txt

bash "$SECRETARY" ask "agent rules" --json --top-k 3 >/tmp/secretary_ask.json
python3 -m json.tool /tmp/secretary_ask.json >/dev/null

bash "$SECRETARY" pack "agent harness" --json --top-k 5 >/tmp/secretary_pack.json
python3 -m json.tool /tmp/secretary_pack.json >/dev/null

bash "$SECRETARY" doctor

echo "secretary verification passed"
