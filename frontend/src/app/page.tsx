"use client";

import { useEffect, useState } from "react";
import { BASE_URL, getProviders, type ProviderName } from "@/lib/api";

type FetchState =
  | { kind: "loading" }
  | { kind: "ok"; providers: ProviderName[] }
  | { kind: "error"; message: string; hint?: string };

export default function Home() {
  const [state, setState] = useState<FetchState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getProviders()
      .then((providers) => {
        if (!cancelled) setState({ kind: "ok", providers });
      })
      .catch((err: Error) => {
        if (cancelled) return;
        const lower = err.message.toLowerCase();
        const looksLikeNetworkOrCors =
          lower.includes("fetch") ||
          lower.includes("network") ||
          lower.includes("load failed");
        setState({
          kind: "error",
          message: err.message,
          hint: looksLikeNetworkOrCors
            ? `Browser likely blocked the request. If the backend is running at ${BASE_URL}, CORS isn't enabled yet — add CORSMiddleware to backend/main.py allowing http://localhost:3000.`
            : undefined,
        });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="relative z-0 flex min-h-screen flex-1 flex-col items-center justify-center px-6 py-16 sm:px-12">
      <div className="w-full max-w-2xl">
        <p className="mb-3 text-xs font-medium uppercase tracking-[0.3em] text-violet-300/70">
          AI Model Evaluation
        </p>
        <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">
          Archer Labs
        </h1>
        <p className="mt-4 max-w-md text-slate-300">
          A platform for comparing, benchmarking, and observing large language
          models — under the stars.
        </p>

        <section className="mt-12 rounded-2xl border border-violet-300/10 bg-violet-950/30 p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-medium uppercase tracking-[0.25em] text-violet-200/70">
              Connected providers
            </h2>
            <StatusDot state={state} />
          </div>

          {state.kind === "loading" && (
            <p className="mt-4 text-sm text-slate-400">
              Reaching the backend…
            </p>
          )}

          {state.kind === "ok" && (
            <>
              {state.providers.length > 0 ? (
                <ul className="mt-4 flex flex-wrap gap-2">
                  {state.providers.map((p) => (
                    <li
                      key={p}
                      className="rounded-full border border-violet-300/20 bg-violet-500/10 px-3 py-1 text-sm text-violet-100"
                    >
                      {p}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-sm text-slate-400">
                  Backend reachable, but no providers are registered.
                </p>
              )}
            </>
          )}

          {state.kind === "error" && (
            <div className="mt-4 space-y-3 text-sm">
              <p className="font-medium text-rose-300">
                Couldn&apos;t reach the backend.
              </p>
              <p className="text-slate-300">
                <code className="rounded bg-black/40 px-1.5 py-0.5 text-rose-200">
                  {state.message}
                </code>
              </p>
              {state.hint && (
                <p className="text-slate-400">{state.hint}</p>
              )}
              <p className="text-xs text-slate-500">
                Tried <code>{BASE_URL}/providers</code>.
              </p>
            </div>
          )}
        </section>

        <p className="mt-10 text-xs text-slate-500">
          Backend:{" "}
          <code className="text-slate-400">{BASE_URL}</code>
        </p>
      </div>
    </main>
  );
}

function StatusDot({ state }: { state: FetchState }) {
  const cls =
    state.kind === "loading"
      ? "bg-amber-400/80 animate-pulse"
      : state.kind === "ok"
        ? "bg-emerald-400/90"
        : "bg-rose-400/90";
  return (
    <span
      aria-hidden
      className={`inline-block h-2 w-2 rounded-full ${cls}`}
    />
  );
}
