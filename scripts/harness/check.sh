#!/usr/bin/env bash
# StoryForge harness — run all available checks (exit non-zero on failure).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "==> StoryForge harness check"
failures=0

run_step() {
  local name="$1"
  shift
  echo ""
  echo "--- $name"
  if "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name" >&2
    failures=$((failures + 1))
  fi
}

# Skill frontmatter lint (always)
run_step "skill frontmatter lint" bash "$ROOT/scripts/harness/lint-skills.sh"

# Phase spec validation (OpenAPI YAML)
run_step "phase spec validation" bash "$ROOT/scripts/harness/validate-specs.sh"

# API: ruff + pytest when venv or tools available
if [[ -d "$ROOT/apps/api/.venv" ]] || command -v ruff >/dev/null 2>&1; then
  (
    cd "$ROOT/apps/api"
    if [[ -d .venv ]]; then
      # shellcheck disable=SC1091
      source .venv/bin/activate
    fi
    if command -v ruff >/dev/null 2>&1; then
      ruff check app tests
      ruff format --check app tests
    else
      echo "SKIP: ruff not installed"
    fi
    if command -v pytest >/dev/null 2>&1; then
      pytest -q
    else
      echo "SKIP: pytest not installed"
    fi
  )
else
  echo ""
  echo "--- API checks"
  echo "SKIP: apps/api/.venv not found (run make setup)"
fi

# Web: typecheck + lint + i18n key parity when node_modules present
if [[ -d "$ROOT/apps/web/node_modules" ]]; then
  (
    cd "$ROOT/apps/web"
    npm run typecheck
    npm run lint
  )
  run_step "i18n key parity" node "$ROOT/scripts/check-i18n-keys.js"
else
  echo ""
  echo "--- Web checks"
  echo "SKIP: apps/web/node_modules not found (run make setup)"
fi

echo ""
if [[ "$failures" -gt 0 ]]; then
  echo "Harness finished with $failures failure(s)" >&2
  exit 1
fi
echo "Harness check passed"
exit 0
