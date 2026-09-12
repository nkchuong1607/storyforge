# StoryForge API

FastAPI backend for canon, ledgers, continuity, and agent orchestration.

## Status

Bootstrap stub — health endpoint only. See `docs/roadmap.md` for Phase 1.

## Develop

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Or from repo root: `make api-dev`

## Conventions

See `skills/storyforge-api-python/SKILL.md`.
