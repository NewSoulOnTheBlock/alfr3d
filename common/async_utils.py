"""Run async coroutines safely from sync tool/agent code.

``asyncio.run`` raises when a loop is already running (web/Discord/async
channels). This helper falls back to a short-lived worker thread with its
own event loop in that case.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Execute *coro* and return its result from either sync or async contexts."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: list = []
    error: list = []

    def _runner() -> None:
        try:
            result.append(asyncio.run(coro))
        except Exception as exc:  # noqa: BLE001 — re-raised to caller
            error.append(exc)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()
    if error:
        raise error[0]
    if not result:
        raise RuntimeError("async work produced no result")
    return result[0]
