import asyncio
import time

from dotenv import load_dotenv

from connectors import GeminiConnector, GroqConnector

load_dotenv()


async def main():
    prompt = "In one sentence, what is a black hole?"
    connectors = [GeminiConnector(), GroqConnector()]

    start = time.perf_counter()
    results = await asyncio.gather(
        *(c.generate(prompt) for c in connectors),
        return_exceptions=True,  # belt-and-suspenders; connectors shouldn't raise
    )
    total_ms = (time.perf_counter() - start) * 1000

    for r in results:
        if isinstance(r, Exception):
            print(f"\n=== unhandled exception ===")
            print(f"{type(r).__name__}: {r}")
            continue
        header = f"=== {r.provider} ({r.model}) ==="
        print(f"\n{header}")
        if r.error:
            print(f"ERROR: {r.error}")
        else:
            print(r.text)
        print(f"latency: {r.latency_ms:.0f} ms | usage: {r.usage}")

    ok = [r for r in results if not isinstance(r, Exception) and not r.error]
    sum_ms = sum(r.latency_ms for r in ok)
    print(f"\nWall clock: {total_ms:.0f} ms | Sum of successful: {sum_ms:.0f} ms")


if __name__ == "__main__":
    asyncio.run(main())