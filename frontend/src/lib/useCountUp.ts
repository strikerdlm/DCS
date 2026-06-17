import { useEffect, useRef, useState } from "react";

/**
 * Animated count-up hook for hero numerals. Eases the displayed value from its
 * previous render value to the new `value` target over `durationMs` using an
 * ease-out cubic on requestAnimationFrame. Respects `prefers-reduced-motion`
 * (snaps to target instantly). Rounds to `decimals` so the tabular-numeral
 * display does not jitter mid-flight.
 *
 * Used on the P(DCS) hero numerals so the number visibly "settles" on tab load
 * and on every scenario change — a perceptual anchor, not decoration.
 */
export function useCountUp(value: number, durationMs = 700, decimals = 2): number {
  const [display, setDisplay] = useState(value);
  // Always holds the latest animated value so an interrupted animation
  // resumes smoothly from wherever it stopped, not from a stale `value`.
  const currentRef = useRef(value);
  const rafRef = useRef<number | null>(null);
  const shouldSnap =
    durationMs <= 0 ||
    (typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);

  useEffect(() => {
    if (shouldSnap) {
      currentRef.current = value;
      return;
    }
    const from = currentRef.current;
    const to = value;
    if (Math.abs(to - from) < 1e-9) return;
    const start = performance.now();
    const ease = (t: number) => 1 - Math.pow(1 - t, 3); // ease-out cubic
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const v = from + (to - from) * ease(t);
      currentRef.current = v;
      setDisplay(v);
      if (t < 1) {
        rafRef.current = requestAnimationFrame(step);
      } else {
        currentRef.current = to;
      }
    };
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [value, durationMs, shouldSnap]);

  const p = Math.pow(10, decimals);
  return Math.round((shouldSnap ? value : display) * p) / p;
}
