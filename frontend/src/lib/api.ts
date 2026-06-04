const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export { BASE_URL };

export type ProviderName = string;

export type EvaluateRequest = {
  prompt: string;
  providers?: ProviderName[];
};

export type EvaluateResultRow = {
  provider: string;
  model: string;
  text: string;
  latency_ms: number;
  usage: { prompt_tokens: number; completion_tokens: number };
  error: string | null;
};

export type EvaluateResponse = {
  prompt: string;
  total_latency_ms: number;
  results: EvaluateResultRow[];
};

export type BenchmarkRequest = {
  prompt: string;
  providers?: ProviderName[];
  n_runs?: number;
};

export type LatencyStats = {
  n: number;
  mean_ms: number;
  median_ms: number;
  p95_ms: number;
  min_ms: number;
  max_ms: number;
  stddev_ms: number;
};

export type BenchmarkResultRow = {
  provider: string;
  model: string;
  latency: LatencyStats;
  successes: number;
  failures: number;
  sample_text: string;
  errors: string[];
};

export type BenchmarkResponse = {
  prompt: string;
  n_runs: number;
  total_latency_ms: number;
  results: BenchmarkResultRow[];
};

export class ApiError extends Error {
  status?: number;
  detail?: unknown;
  constructor(message: string, status?: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Network request failed";
    throw new ApiError(message);
  }

  if (!res.ok) {
    let detail: unknown = null;
    try {
      detail = await res.json();
    } catch {
      try {
        detail = await res.text();
      } catch {
        // ignore
      }
    }
    throw new ApiError(
      `Request failed: ${res.status} ${res.statusText}`,
      res.status,
      detail,
    );
  }

  return (await res.json()) as T;
}

export function getHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}

export function getProviders(): Promise<ProviderName[]> {
  return request<ProviderName[]>("/providers");
}

export function evaluate(body: EvaluateRequest): Promise<EvaluateResponse> {
  return request<EvaluateResponse>("/evaluate", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function benchmark(body: BenchmarkRequest): Promise<BenchmarkResponse> {
  return request<BenchmarkResponse>("/benchmark", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
