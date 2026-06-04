"use client";

import { useEffect, useRef, useState } from "react";
import ZodiacRing from "./ZodiacRing";

type Star = {
  top: string;
  left: string;
  size: number;
  opacity: number;
  bright: boolean;
};

function generateStars(count: number): Star[] {
  return Array.from({ length: count }, () => {
    const bright = Math.random() < 0.08;
    return {
      top: `${Math.random() * 100}%`,
      left: `${Math.random() * 100}%`,
      size: bright ? 1.6 + Math.random() * 1.2 : 0.5 + Math.random() * 1.1,
      opacity: bright ? 0.75 + Math.random() * 0.25 : 0.18 + Math.random() * 0.5,
      bright,
    };
  });
}

export default function CosmosBackground() {
  const [stars, setStars] = useState<Star[]>([]);
  const parallaxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setStars(generateStars(180));
  }, []);

  useEffect(() => {
    let rafId = 0;
    const target = { mx: 0, my: 0 };

    const apply = () => {
      const el = parallaxRef.current;
      if (!el) return;
      const scrollOffset = window.scrollY * -0.04;
      el.style.transform = `translate3d(${target.mx}px, ${target.my + scrollOffset}px, 0)`;
    };

    const onMove = (e: MouseEvent) => {
      target.mx = (e.clientX / window.innerWidth - 0.5) * 28;
      target.my = (e.clientY / window.innerHeight - 0.5) * 28;
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(apply);
    };

    const onScroll = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(apply);
    };

    apply();
    window.addEventListener("mousemove", onMove);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-gradient-to-br from-[#050314] via-[#1a0b3d] to-[#2a1158]"
    >
      <div
        ref={parallaxRef}
        className="absolute inset-0 will-change-transform"
      >
        {stars.map((s, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              top: s.top,
              left: s.left,
              width: `${s.size}px`,
              height: `${s.size}px`,
              opacity: s.opacity,
              boxShadow: s.bright
                ? `0 0 ${s.size * 3}px rgba(220, 210, 255, 0.55)`
                : undefined,
            }}
          />
        ))}
        <ZodiacRing />
      </div>
    </div>
  );
}
