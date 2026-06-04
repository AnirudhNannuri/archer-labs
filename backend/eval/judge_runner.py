import asyncio
from judges import BaseJudge, JudgeVerdict
from connectors import ConnectorResponse

async def judge_all(
    judge: BaseJudge,
    prompt: str,
    responses: list[ConnectorResponse],
) -> list[JudgeVerdict]:
    # Fan out — Ollama is local, one model loaded, so calls serialize on the server
    # anyway. We still gather() so the orchestration shape matches run_benchmark.
    return await asyncio.gather(
        *(
            judge.judge(prompt, r.text, provider = r.provider, model = r.model)
            for r in responses if not r.error 
        )
    )