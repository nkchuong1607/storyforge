"""Fact-check Redis queue with sync fallback."""

from __future__ import annotations

import json
import uuid
from typing import Any, Protocol

from app.config import get_settings


class FactCheckQueue(Protocol):
    def enqueue(self, run_id: uuid.UUID, project_id: uuid.UUID, chapter_id: uuid.UUID) -> None: ...


class RedisFactCheckQueue:
    def __init__(self, redis_url: str, queue_name: str) -> None:
        import redis

        self._client = redis.from_url(redis_url, decode_responses=True)
        self._queue_name = queue_name

    def enqueue(self, run_id: uuid.UUID, project_id: uuid.UUID, chapter_id: uuid.UUID) -> None:
        payload = json.dumps(
            {
                "run_id": str(run_id),
                "project_id": str(project_id),
                "chapter_id": str(chapter_id),
            }
        )
        self._client.lpush(self._queue_name, payload)


class SyncFactCheckQueue:
    """In-process queue for deterministic tests."""

    def __init__(self) -> None:
        self.pending: list[dict[str, Any]] = []

    def enqueue(self, run_id: uuid.UUID, project_id: uuid.UUID, chapter_id: uuid.UUID) -> None:
        self.pending.append(
            {
                "run_id": str(run_id),
                "project_id": str(project_id),
                "chapter_id": str(chapter_id),
            }
        )


_queue: FactCheckQueue | None = None


def get_fact_check_queue() -> FactCheckQueue:
    global _queue
    if _queue is None:
        settings = get_settings()
        if settings.fact_check_sync:
            _queue = SyncFactCheckQueue()
        else:
            _queue = RedisFactCheckQueue(settings.redis_url, settings.fact_check_queue_name)
    return _queue


def reset_fact_check_queue() -> None:
    global _queue
    _queue = None
