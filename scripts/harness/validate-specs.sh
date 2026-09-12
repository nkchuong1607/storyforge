#!/usr/bin/env bash
# Validate Phase spec artifacts (OpenAPI YAML parse).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

validate_openapi() {
  local label="$1"
  local relpath="$2"
  local openapi="$ROOT/$relpath"

  echo "==> Validating $label OpenAPI YAML"
  if [[ ! -f "$openapi" ]]; then
    echo "FAIL: missing $openapi" >&2
    exit 1
  fi

  python3 - "$relpath" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    import yaml  # type: ignore
except ImportError:
    text = path.read_text()
    if "openapi:" not in text or "paths:" not in text:
        print(f"FAIL: {path} missing required top-level keys", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {path} structure (PyYAML not installed; basic check only)")
    sys.exit(0)

data = yaml.safe_load(path.read_text())
assert data.get("openapi", "").startswith("3."), f"{path}: expected OpenAPI 3.x"
assert "paths" in data, f"{path}: missing paths"
assert "/health" in data["paths"], f"{path}: missing /health path"
print(f"OK: OpenAPI {data.get('openapi')} with {len(data['paths'])} paths")
PY
}

validate_openapi "Phase 1" "docs/specs/phase-1/openapi.yaml"
validate_openapi "Phase 2" "docs/specs/phase-2/openapi.yaml"

echo "Spec validation passed"
