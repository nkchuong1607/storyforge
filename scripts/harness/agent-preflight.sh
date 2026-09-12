#!/usr/bin/env bash
# Verify agent harness layout and print AGENTS.md reminder.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

errors=0

require_path() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "MISSING: $path" >&2
    errors=$((errors + 1))
  else
    echo "OK: $path"
  fi
}

echo "==> StoryForge agent preflight"
echo ""

require_path "AGENTS.md"
require_path "docs/architecture.md"
require_path "docs/domain-model.md"
require_path "skills"
require_path ".cursor/rules"

skill_count=$(find skills -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "OK: $skill_count skill directories under skills/"

echo ""
echo "--- AGENTS.md reminder ---"
head -n 20 AGENTS.md
echo "..."

echo ""
if [[ "$errors" -gt 0 ]]; then
  echo "Preflight failed with $errors error(s)" >&2
  exit 1
fi
echo "Preflight passed. Read AGENTS.md, then run: make check"
exit 0
