import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")

@dataclass
class ConnectorResponse:
    text: str
    model: str
    provider: str
    latency_ms: float
    usage: dict = field(default_factory=dict)
    error: str | None = None
    raw: Any = None

async def with_retry(
    call: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    timeout_s: float = 30.0,
    backoff_s: float = 1.0,
) -> T:
    """Run an async call with a per-attempt timeout and exponential backoff.

    `call` is a zero-arg function returning a fresh awaitable each invocation
    (we can't reuse a single awaitable across retries — coroutines are one-shot).
    """
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return await asyncio.wait_for(call(), timeout=timeout_s)
        except Exception as e:
            last_exc = e
            if attempt == retries - 1:
                raise
            # 1s, 2s, 4s, ...
            await asyncio.sleep(backoff_s * (2 ** attempt))
    assert last_exc is not None  # unreachable
    raise last_exc

class BaseConnector(ABC):
    provider: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> ConnectorResponse:
        ...