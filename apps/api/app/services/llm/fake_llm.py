"""Deterministic FakeLLM provider for tests and local dev."""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass


@dataclass
class LLMCompletionResult:
    content: str
    model: str
    provider: str
    latency_ms: int
    token_usage: dict[str, int]


def sanitize_instruction(instruction: str) -> str:
    """Strip template injection patterns from author instruction."""
    cleaned = instruction.strip()
    cleaned = re.sub(r"<\s*/?\s*(system|assistant|user)\s*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\{\{.*?\}\}", "", cleaned)
    return cleaned[:4000]


def _instruction_hash(instruction: str) -> str:
    return hashlib.sha256(instruction.encode()).hexdigest()[:12]


def fake_complete(
    *,
    prose: str,
    instruction: str,
    craft_context: dict | None = None,
) -> LLMCompletionResult:
    """Deterministic prose transformation — no network."""
    start = time.perf_counter()
    safe_instruction = sanitize_instruction(instruction)
    edit_hash = _instruction_hash(safe_instruction)

    revised = prose
    lower = safe_instruction.lower()
    if "tension" in lower or "căng thẳng" in lower:
        revised = prose.replace("。", "！").replace(".", "!")
    if "ngắn" in lower or "short" in lower:
        revised = prose[: max(len(prose) // 2, 50)]
    if craft_context and craft_context.get("craft_checklist_open"):
        revised = f"{revised}\n\n[CRAFT_CONTEXT: injected]"

    marker = f"\n\n[AI_EDIT: {edit_hash}]"
    if marker not in revised:
        revised = revised + marker

    elapsed = int((time.perf_counter() - start) * 1000)
    prompt_tokens = max(1, len(prose.split()) // 4)
    completion_tokens = max(1, len(revised.split()) // 4)
    return LLMCompletionResult(
        content=revised,
        model="fake-llm",
        provider="fake",
        latency_ms=max(elapsed, 1),
        token_usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    )
