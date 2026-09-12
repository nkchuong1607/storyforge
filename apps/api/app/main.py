"""StoryForge FastAPI application entrypoint."""

from fastapi import FastAPI

app = FastAPI(
    title="StoryForge API",
    description="AI long-form fiction — canon, continuity, ledgers",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check for harness and orchestration."""
    return {"status": "ok"}
