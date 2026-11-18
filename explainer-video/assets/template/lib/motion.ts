// Motion helpers. Everything is a pure function of time, so scrubbing, capture and export all show
// the same frame. Every easing returns exactly 0 at the start and 1 at the end: "has it started" checks rely on that.

export function bezier(x1: number, y1: number, x2: number, y2: number) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const x = (t: number) => ((ax * t + bx) * t + cx) * t;
  const y = (t: number) => ((ay * t + by) * t + cy) * t;
  return (p: number) => {
    if (p <= 0) return 0;
    if (p >= 1) return 1;
    let lo = 0, hi = 1, t = p;
    for (let i = 0; i < 26; i++) {
      t = (lo + hi) / 2;
      if (x(t) < p) lo = t;
      else hi = t;
    }
    return y(t);
  };
}
export const snappyOut = bezier(0, 0.6, 0.4, 1);
export const expoOut = bezier(0.16, 1, 0.3, 1);
export const snappyIn = bezier(0.6, 0, 1, 0.4);
export const inOut = bezier(0.7, 0, 0.3, 1);
export const softInOut = bezier(0.45, 0, 0.55, 1);
/** Anticipation into a hard exit or a cut. */
export const expoIn = bezier(0.7, 0, 0.84, 0);
/** Motion carried across a cut: fast at both ends, slow in the middle. */
export const outIn = bezier(0, 0.7, 1, 0.3);
/** Damped spring with a little overshoot, 0 → 1. */
export const spring = (p: number) => (p >= 1 ? 1 : 1 - Math.exp(-6 * p) * Math.cos(10 * p));

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const prog = (t: number, a: number, d: number) => clamp((t - a) / d);
export const rise = (t: number, a: number, d: number, e = snappyOut) => e(prog(t, a, d));
export const fall = (t: number, a: number, d: number, e = snappyIn) => 1 - e(prog(t, a, d));
/** 0 before a, eases to 1 over din, stays, eases back to 0 from b over dout. */
export const window_ = (t: number, a: number, b: number, din = 0.35, dout = 0.3) => rise(t, a, din) * fall(t, b, dout);
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
/** Decaying shake after a hit. */
export const shake = (t: number, at: number, amp: number) =>
  t < at ? 0 : amp * Math.exp(-(t - at) * 9) * Math.sin((t - at) * 75);

export function mix(a: string, b: string, p: number) {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], clamp(p)))).join(",")})`;
}
export const f1 = (n: number) => n.toFixed(1);
/** A slow continuous sway for holds: amp x sin, one cycle per `period` seconds. Keep it above one pixel per frame or use opacity instead. */
export const sway = (t: number, amp: number, period: number, phase = 0) => amp * Math.sin((t / period) * Math.PI * 2 + phase);
