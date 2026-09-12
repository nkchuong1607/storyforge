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

# Vendored AAS stack (curated implementation-craft skills)
require_path "aas-stack.json"
require_path "skills/storyforge-aas-stack/SKILL.md"
require_path "vendor/aas-skills"

if [[ -f "aas-stack.json" ]]; then
  aas_count=$(python3 -c "import json; d=json.load(open('aas-stack.json')); print(len(d.get('skills', [])))" 2>/dev/null || echo "0")
  echo "OK: aas-stack.json lists $aas_count skill(s)"
fi

if [[ -d "vendor/aas-skills" ]]; then
  vendored_count=$(find vendor/aas-skills -mindepth 1 -maxdepth 1 -type d ! -name '.*' | wc -l)
  echo "OK: $vendored_count skill directories under vendor/aas-skills/"
fi

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
