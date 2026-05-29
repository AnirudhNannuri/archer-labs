import os
import time

from groq import AsyncGroq

from .base import BaseConnector, ConnectorResponse, with_retry


class GroqConnector(BaseConnector):
    provider = "groq"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.3-70b-versatile",
        timeout_s: float = 30.0,
        retries: int = 3,
    ):
        self.api_key = api_key or os.environ["GROQ_API_KEY"]
        self.model = model
        self.timeout_s = timeout_s
        self.retries = retries
        self.client = AsyncGroq(api_key=self.api_key)

    async def generate(self, prompt: str, **kwargs) -> ConnectorResponse:
        start = time.perf_counter()

        try:
            resp = await with_retry(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                ),
                retries=self.retries,
                timeout_s=self.timeout_s,
            )
        except Exception as e:
            return ConnectorResponse(
                text="",
                model=self.model,
                provider=self.provider,
                latency_ms=(time.perf_counter() - start) * 1000,
                error=f"{type(e).__name__}: {e}",
            )

        latency_ms = (time.perf_counter() - start) * 1000

        return ConnectorResponse(
            text=resp.choices[0].message.content or "",
            model=self.model,
            provider=self.provider,
            latency_ms=latency_ms,
            usage={
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
            },
            raw=resp,
        )