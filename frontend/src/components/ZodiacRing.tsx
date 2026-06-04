import { CONSTELLATIONS, type Constellation } from "@/lib/constellations";

export default function ZodiacRing() {
  const radiusPercent = 65;

  return (
    <div
      aria-hidden
      className="pointer-events-none absolute"
      style={{
        right: "-90vmin",
        bottom: "-90vmin",
        width: "180vmin",
        height: "180vmin",
      }}
    >
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle at center, rgba(120, 80, 220, 0.14) 0%, rgba(80, 50, 180, 0.05) 35%, rgba(0, 0, 0, 0) 70%)",
        }}
      />
      <div className="animate-cosmos-spin relative h-full w-full">
        <div
          className="absolute rounded-full border border-violet-300/10"
          style={{
            top: `${50 - radiusPercent}%`,
            left: `${50 - radiusPercent}%`,
            width: `${radiusPercent * 2}%`,
            height: `${radiusPercent * 2}%`,
          }}
        />
        {CONSTELLATIONS.map((c, i) => {
          const angleRad = (i * Math.PI) / 6;
          const x = 50 + radiusPercent * Math.cos(angleRad);
          const y = 50 + radiusPercent * Math.sin(angleRad);
          return (
            <div
              key={c.name}
              className="absolute -translate-x-1/2 -translate-y-1/2"
              style={{ top: `${y}%`, left: `${x}%` }}
            >
              <div className="animate-cosmos-spin-reverse">
                <ConstellationSvg data={c} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ConstellationSvg({ data }: { data: Constellation }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className="h-[14vmin] w-[14vmin]"
      style={{ overflow: "visible" }}
    >
      <title>{data.name}</title>
      {data.edges.map(([a, b], idx) => {
        const s1 = data.stars[a];
        const s2 = data.stars[b];
        return (
          <line
            key={idx}
            x1={s1.x}
            y1={s1.y}
            x2={s2.x}
            y2={s2.y}
            stroke="rgba(180, 150, 255, 0.45)"
            strokeWidth={1.1}
            strokeLinecap="round"
          />
        );
      })}
      {data.stars.map((s, idx) => {
        const r = s.r ?? 1.6;
        return (
          <g key={idx}>
            <circle
              cx={s.x}
              cy={s.y}
              r={r * 2.6}
              fill="rgba(210, 190, 255, 0.18)"
            />
            <circle
              cx={s.x}
              cy={s.y}
              r={r * 1.6}
              fill="rgba(230, 215, 255, 0.35)"
            />
            <circle cx={s.x} cy={s.y} r={r} fill="white" />
          </g>
        );
      })}
    </svg>
  );
}
