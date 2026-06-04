import os, time, json, httpx
from .base import BaseJudge, JudgeVerdict, JudgeScores

JUDGE_SYSTEM_PROMPT = """You are an impartial evaluator of LLM responses.
Given a user prompt and a candidate response, score the response on:
- accuracy (factual correctness)
- helpfulness (does it solve the user's need)
- clarity (well-organized, easy to read)
- conciseness (no padding)
- overall (your holistic judgment)

Each score is an integer 1-10. Respond ONLY with JSON of this shape:
{"accuracy": int, "helpfulness": int, "clarity": int, "conciseness": int, "overall": int, "reasoning": "one or two sentences"}
"""

class OllamaJudge(BaseJudge):
    def __init__(
            self,
            model: str = "llama3.2:3b",
            base_url: str | None = None,
            timeout_s: float = 60.0,
    ):
        self.judge_model = model
        self.base_url = base_url or os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self.timeout_s = timeout_s
        self.client = httpx.AsyncClient(
            base_url=self.base_url, 
            timeout=timeout_s,
            )

    async def judge(self, prompt, response, *, provider, model):
        start = time.perf_counter()
        user_msg = f"USER PROMPT:\n{prompt}\n\nCANDIDATE RESPONSE:\n{response}"
        try:
            r = await self.client.post(
                "/api/chat",
                json= {
                    "model": self.judge_model,
                "messages": [
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
                # Ollama-native JSON mode — huge for small models
                "format": "json",
                "stream": False,
                }
            )
            r.raise_for_status()
            payload = json.loads(r.json()["message"]["content"])
        except Exception as e:
            return JudgeVerdict(
                provider = provider, model = model,
                scores = JudgeScores(0,0,0,0,0),
                reasoning = "",
                judge_model = self.judge_model,
                latency_ms = (time.perf_counter() - start) * 1000,
                error = f"{type(e).__name__}: {e}",
            )
        
        return JudgeVerdict(
            provider = provider,
            model = model,
            scores = JudgeScores(
                accuracy = payload["accuracy"],
                helpfulness = payload["helpfulness"],
                clarity = payload["clarity"],
                conciseness = payload["conciseness"],
                overall = payload["overall"],
            ),
            reasoning = payload.get("reasoning", ""),
            judge_model = self.judge_model,
            latency_ms = (time.perf_counter() - start) * 1000,
            raw = payload,
        )