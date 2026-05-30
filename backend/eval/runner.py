import asyncio
import statistics
from dataclasses import dataclass, field

from connectors import BaseConnector, ConnectorResponse

 
@dataclass
class LatencyStats:
    """Summary statistics over a list of latency samples (in milliseconds).

    Computed only from SUCCESSFUL calls. Failed/timed-out calls are reported
    separately as `failures` on BenchmarkResult — including them here would
    pollute the latency picture with timeout durations.
    """
    n: int
    mean_ms: float
    median_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float
    stddev_ms: float

    @classmethod
    def from_samples(cls, samples: list[float]) -> "LatencyStats":
        if not samples:
            return cls(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        return cls(
            n=len(samples),
            mean_ms=statistics.mean(samples),
            median_ms=statistics.median(samples),
            p95_ms=_percentile(sorted(samples), 95),
            min_ms=min(samples),
            max_ms=max(samples),
            # stdev needs at least 2 samples; with 1 sample, variance is 0.
            stddev_ms=statistics.stdev(samples) if len(samples) > 1 else 0.0,
        )

def _percentile(sorted_samples: list[float], pct: float) -> float:
    # Linear interpolation between the two nearest ranks (NIST Method).
    if not sorted_samples:
        return 0.0
    k = (len(sorted_samples) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(sorted_samples) - 1)
    if f == c:
        return sorted_samples[f]
    
    return sorted_samples[f] + (sorted_samples[c] - sorted_samples[f]) * (k - f)

@dataclass
class BenchmarkResult:
    # Outcome of running one prompt N times against one model.
    provider: str
    model: str
    latency: LatencyStats
    successes: int
    failures: int
    sample_text: str
    errors: list[str] = field(default_factory=list)

async def run_one_model(
    connector: BaseConnector,
    prompt: str,
    n_runs: int,
) -> BenchmarkResult:
    """Run the same prompt N times against one model, sequentially.

    Sequential (not parallel) within a single model so we never have more than
    one in-flight call to that provider — keeps us inside per-provider rate
    limits without needing semaphores or token buckets.
    """
    successes: list[ConnectorResponse] = []
    failures: list[ConnectorResponse] = []

    for _ in range(n_runs):
        r = await connector.generate(prompt)
        (failures if r.error else successes).append(r)
    
    latency_samples = [r.latency_ms for r in successes]
    unique_errors = sorted({f.error for f in failures if f.error})

    return BenchmarkResult(
        provider=connector.provider,
        model=connector.model,
        latency=LatencyStats.from_samples(latency_samples),
        successes=len(successes),
        failures=len(failures),
        sample_text=successes[0].text if successes else "",
        errors=unique_errors,
    )

async def run_benchmark(
    connectors: list[BaseConnector],
    prompt: str,
    n_runs: int,
) -> list[BenchmarkResult]:
    # Fan out across models: run_one_model handles within-model serialization.
    return await asyncio.gather(
        *(run_one_model(c, prompt, n_runs) for c in connectors)
    )
