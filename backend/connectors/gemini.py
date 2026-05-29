import os
import time

from google import genai

from .base import BaseConnector, ConnectorResponse, with_retry


class GeminiConnector(BaseConnector):
    provider = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        timeout_s: float = 30.0,
        retries: int = 3,
    ):
        self.api_key = api_key or os.environ["GEMINI_API_KEY"]
        self.model = model
        self.timeout_s = timeout_s
        self.retries = retries
        self.client = genai.Client(api_key=self.api_key)

    async def generate(self, prompt: str, **kwargs) -> ConnectorResponse:
        start = time.perf_counter()

        try:
            resp = await with_retry(
                lambda: self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
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

        usage = {}
        if resp.usage_metadata is not None:
            usage = {
                "prompt_tokens": resp.usage_metadata.prompt_token_count or 0,
                "completion_tokens": resp.usage_metadata.candidates_token_count or 0,
            }

        return ConnectorResponse(
            text=resp.text or "",
            model=self.model,
            provider=self.provider,
            latency_ms=latency_ms,
            usage=usage,
            raw=resp,
        )