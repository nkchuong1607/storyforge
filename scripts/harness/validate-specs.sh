#!/usr/bin/env bash
# Validate Phase spec artifacts (OpenAPI YAML parse).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OPENAPI="$ROOT/docs/specs/phase-1/openapi.yaml"

echo "==> Validating Phase 1 OpenAPI YAML"
if [[ ! -f "$OPENAPI" ]]; then
  echo "FAIL: missing $OPENAPI" >&2
  exit 1
fi

python3 - <<'PY'
import sys
from pathlib import Path

path = Path("docs/specs/phase-1/openapi.yaml")
try:
    import yaml  # type: ignore
except ImportError:
    # PyYAML optional — stdlib-only fallback: basic structure check
    text = path.read_text()
    if "openapi:" not in text or "paths:" not in text:
        print("FAIL: openapi.yaml missing required top-level keys", file=sys.stderr)
        sys.exit(1)
    print("OK: openapi.yaml structure (PyYAML not installed; basic check only)")
    sys.exit(0)

data = yaml.safe_load(path.read_text())
assert data.get("openapi", "").startswith("3."), "expected OpenAPI 3.x"
assert "paths" in data, "missing paths"
assert "/health" in data["paths"], "missing /health path"
print(f"OK: OpenAPI {data.get('openapi')} with {len(data['paths'])} paths")
PY

echo "Spec validation passed"
