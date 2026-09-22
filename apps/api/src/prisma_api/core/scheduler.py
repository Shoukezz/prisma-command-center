"""In-process background scheduler for world simulation.

World ticks and deferred work run via asyncio tasks started in the FastAPI
lifespan. No external queue (Celery/Redis) is used.
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Manages cancellable asyncio background tasks."""

    def __init__(self) -> None:
        self._tasks: list[asyncio.Task[None]] = []

    def start(self, coro_factory: Callable[[], Coroutine[Any, Any, None]]) -> None:
        task = asyncio.create_task(coro_factory())
        self._tasks.append(task)
        task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        if task in self._tasks:
            self._tasks.remove(task)
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            logger.exception("Background task failed", exc_info=exc)

    async def shutdown(self) -> None:
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
