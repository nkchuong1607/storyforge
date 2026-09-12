"""LLM provider factory — FakeLLM default, LiteLLM opt-in."""

from __future__ import annotations

from app.config import get_settings
from app.exceptions import LLMProviderError
from app.services.llm.fake_llm import LLMCompletionResult, fake_complete, sanitize_instruction


async def complete_prose_edit(*, prose: str, instruction: str) -> LLMCompletionResult:
    """Run prose edit completion via configured provider."""
    settings = get_settings()
    safe_instruction = sanitize_instruction(instruction)
    if settings.llm_provider == "litellm":
        return await _litellm_complete(prose=prose, instruction=safe_instruction)
    return fake_complete(prose=prose, instruction=safe_instruction)


async def _litellm_complete(*, prose: str, instruction: str) -> LLMCompletionResult:
    import time

    settings = get_settings()
    if not settings.litellm_model:
        raise LLMProviderError("LITELLM_MODEL is required when STORYFORGE_LLM_PROVIDER=litellm")
    try:
        import litellm
    except ImportError as exc:
        raise LLMProviderError("litellm package not installed") from exc

    prompt = (
        "You are StoryForge Editor. Revise the chapter prose per author instruction.\n"
        "Preserve canon facts. Output full revised chapter text only.\n"
        f"Instruction: {instruction}\n"
        f"Current prose:\n{prose}"
    )
    start = time.perf_counter()
    try:
        response = await litellm.acompletion(
            model=settings.litellm_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.llm_max_output_tokens,
            timeout=settings.llm_timeout_sec,
            api_base=settings.litellm_api_base or None,
        )
    except Exception as exc:
        raise LLMProviderError(str(exc)) from exc

    content = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    token_usage = {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
    }
    elapsed = int((time.perf_counter() - start) * 1000)
    return LLMCompletionResult(
        content=content,
        model=settings.litellm_model,
        provider="litellm",
        latency_ms=elapsed,
        token_usage=token_usage,
    )
