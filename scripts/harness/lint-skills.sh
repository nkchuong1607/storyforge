#!/usr/bin/env bash
# Ensure every skills/*/SKILL.md has YAML frontmatter with name and description.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
skills_dir="$ROOT/skills"
errors=0

for skill_md in "$skills_dir"/*/SKILL.md; do
  [[ -f "$skill_md" ]] || continue
  skill_name=$(basename "$(dirname "$skill_md")")

  if ! head -n 1 "$skill_md" | grep -q '^---$'; then
    echo "FAIL: $skill_name — missing frontmatter opening ---" >&2
    errors=$((errors + 1))
    continue
  fi

  if ! grep -q '^name:' "$skill_md"; then
    echo "FAIL: $skill_name — missing 'name:' in frontmatter" >&2
    errors=$((errors + 1))
  fi

  if ! grep -q '^description:' "$skill_md"; then
    echo "FAIL: $skill_name — missing 'description:' in frontmatter" >&2
    errors=$((errors + 1))
  fi
done

if [[ "$errors" -gt 0 ]]; then
  echo "Skill lint: $errors error(s)" >&2
  exit 1
fi

echo "Skill lint: all SKILL.md files have name + description"
exit 0
