"""Export job Redis queue with sync fallback."""

from __future__ import annotations

import json
import uuid
from typing import Any, Protocol

from app.config import get_settings


class ExportQueue(Protocol):
    def enqueue(self, job_id: uuid.UUID, project_id: uuid.UUID, job_type: str) -> None: ...


class RedisExportQueue:
    def __init__(self, redis_url: str, queue_name: str) -> None:
        import redis

        self._client = redis.from_url(redis_url, decode_responses=True)
        self._queue_name = queue_name

    def enqueue(self, job_id: uuid.UUID, project_id: uuid.UUID, job_type: str) -> None:
        payload = json.dumps(
            {"job_id": str(job_id), "project_id": str(project_id), "job_type": job_type}
        )
        self._client.lpush(self._queue_name, payload)


class SyncExportQueue:
    """In-process queue for deterministic tests."""

    def __init__(self) -> None:
        self.pending: list[dict[str, Any]] = []

    def enqueue(self, job_id: uuid.UUID, project_id: uuid.UUID, job_type: str) -> None:
        self.pending.append(
            {"job_id": str(job_id), "project_id": str(project_id), "job_type": job_type}
        )


_queue: ExportQueue | None = None


def get_export_queue() -> ExportQueue:
    global _queue
    if _queue is None:
        settings = get_settings()
        if settings.export_sync:
            _queue = SyncExportQueue()
        else:
            _queue = RedisExportQueue(settings.redis_url, settings.export_queue_name)
    return _queue


def reset_export_queue() -> None:
    global _queue
    _queue = None
