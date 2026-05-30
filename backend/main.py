import asyncio
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from connectors import GeminiConnector, GroqConnector

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup
    # SDK Clients are reused across requests
    # Test code can swap registries without import-time side effects

    load_dotenv()
    app.state.connectors = {
        "gemini": GeminiConnector(),
        "groq": GroqConnector(),
    }
    yield

app = FastAPI(
    title  = "Archer Labs",
    description="AI model evaluation platform — Layer 1 connectors exposed via HTTP.",
    version="0.1.0",
    lifespan=lifespan,
)

# Pydantic Schemas
class EvaluateRequest(BaseModel):
    prompt: str = Field(..., min_length = 1, description = "The prompt sent to every selected model.")
    providers: list[str] | None = Field(
        default = None,
        description = "Provider names to call. If omitted, calls every registred provider."
    )

class EvaluateResult(BaseModel):
    provider: str
    model: str
    text: str
    latency_ms: float
    usage: dict
    error: str | None = None

class EvaluateResponse(BaseModel):
    prompt: str
    total_latency_ms: float
    results: list[EvaluateResult]


# Endpoints
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/providers")
async def list_providers() -> list[str]:
    return list(app.state.connectors.keys())

@app.post("/evaluate", response_model = EvaluateResponse)
async def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    registry: dict = app.state.connectors

    # Default to all providers if none specified
    chosen_names = req.providers or list(registry.keys())

    # Distinguish "you asked for a bad name" (400) from "the model errored" (200 + error field).
    unknown = [p for p in chosen_names if p not in registry]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown providers: {unknown}. Available: {list(registry.keys())}",
        )
    
    chosen = [registry[name] for name in chosen_names]

    start = time.perf_counter()
    raw_results = await asyncio.gather(
        *(c.generate(req.prompt) for c in chosen),
        return_exceptions = True # defensive — connectors shouldn't raise, but if they do, don't kill the eval
    )
    total_ms = (time.perf_counter() - start) * 1000

    results: list[EvaluateResult] = []
    for name, r in zip(chosen_names, raw_results):
        if isinstance(r, Exception):
            # Unexpected: connector itself blew up. Synthesize a row so the response stays uniform.
            results.append(EvaluateResult(
                provider=name,
                model="unknown",
                text="",
                latency_ms=0.0,
                usage={},
                error=f"{type(r).__name__}: {r}",
            ))
        else:
            results.append(EvaluateResult(
                provider=r.provider,
                model=r.model,
                text=r.text,
                latency_ms=r.latency_ms,
                usage=r.usage,
                error=r.error,
            ))
    
    return EvaluateResponse(
        prompt = req.prompt,
        total_latency_ms = total_ms,
        results=results,
    )