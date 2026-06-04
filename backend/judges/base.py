from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class JudgeScores:
    # Rubric for one response. 1-10 scale.
    accuracy: int
    helpfulness: int
    clarity: int
    conciseness: int
    overall: int

@dataclass
class JudgeVerdict:
    # Judge's output for one (prompt, response) pair.
    provider: str
    model: str
    scores: JudgeScores
    reasoning: str
    judge_model: str
    latency_ms: float
    error: str | None = None
    raw: object = None

class BaseJudge(ABC):
    judge_model: str = "base"

    @abstractmethod
    async def judge(
        self, prompt: str, response: str, *, provider: str, model: str
    ) -> JudgeVerdict:
        ...