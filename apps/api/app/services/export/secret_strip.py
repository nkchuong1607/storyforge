"""Strip unrevealed secrets from export payloads."""

from typing import Any


def strip_secrets_from_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Remove secret_truth and unrevealed twist content from bible snapshot."""
    cleaned = dict(snapshot)
    entries = cleaned.get("entries", [])
    if isinstance(entries, list):
        cleaned["entries"] = [
            {k: v for k, v in entry.items() if k != "secret_truth"}
            for entry in entries
            if isinstance(entry, dict)
        ]
    twists = cleaned.get("twists", [])
    if isinstance(twists, list):
        cleaned["twists"] = [
            {k: v for k, v in twist.items() if k not in ("secret_truth", "unrevealed")}
            for twist in twists
            if isinstance(twist, dict)
        ]
    if "secret_truth" in cleaned:
        del cleaned["secret_truth"]
    return cleaned


def strip_secrets_from_text(text: str) -> str:
    if "secret_truth:" in text.lower():
        lines = [line for line in text.splitlines() if "secret_truth" not in line.lower()]
        return "\n".join(lines)
    return text
