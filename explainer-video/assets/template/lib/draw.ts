// SVG drawing primitives, returned as strings and drawn through one <html> layer per shot.
// Clip paths are dropped by the rasterizer, so nothing here relies on them.

import { f1, clamp } from "./motion";
import * as C from "./brand";

export type Cam = { z: number; px: number; py: number };
export const CAM0: Cam = { z: 1, px: 960, py: 540 };

/**
 * A full 1920x1080 SVG document. `cam` zooms by z around world point (px, py).
 * `bg` paints a background that travels with dx/dy: a shot that slides away must take its background
 * along, or it blanks the shot underneath.
 */
export function svgDoc(inner: string, cam: Cam = CAM0, bg: string | null = null, dx = 0, dy = 0) {
  const tx = 960 - cam.px * cam.z;
  const ty = 540 - cam.py * cam.z;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><g transform="translate(${f1(dx)} ${f1(dy)})">
    ${bg ? `<rect x="-40" y="-40" width="2000" height="1160" fill="${bg}"/>` : ""}
    <g transform="translate(${f1(tx)} ${f1(ty)}) scale(${cam.z.toFixed(4)})">${inner}</g></g></svg>`;
}

/** Where a full-frame <image> goes when seen through `cam`. Lets a picture and its overlay share one camera. */
export const imgBox = (cam: Cam) => ({ x: 960 - cam.px * cam.z, y: 540 - cam.py * cam.z, width: 1920 * cam.z, height: 1080 * cam.z });

/** Eased camera between keyframes { t, d, z, px, py }: from time t, move over d seconds to that view. */
export function camPath(keys: { t: number; d: number; z: number; px: number; py: number }[], ease: (p: number) => number) {
  return (t: number): Cam => {
    let z = keys[0].z, px = keys[0].px, py = keys[0].py;
    for (const k of keys.slice(1)) {
      if (t < k.t) break;
      const p = ease(clamp((t - k.t) / k.d));
      z = z + (k.z - z) * p;
      px = px + (k.px - px) * p;
      py = py + (k.py - py) * p;
    }
    return { z, px, py };
  };
}

/** A group: translate, rotate, scale, fade. Returns nothing when invisible. */
export const g = (inner: string, tx = 0, ty = 0, s = 1, rot = 0, opacity = 1) =>
  opacity <= 0.003 || s <= 0.003
    ? ""
    : `<g transform="translate(${f1(tx)} ${f1(ty)}) rotate(${f1(rot)}) scale(${s.toFixed(4)})"${opacity < 1 ? ` opacity="${opacity.toFixed(3)}"` : ""}>${inner}</g>`;

export const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

type TextOpts = { size: number; weight?: number; fill?: string; anchor?: "start" | "middle" | "end"; opacity?: number; spacing?: number; body?: boolean };
const family = (o: TextOpts) => (o.body ? C.FONT_BODY : C.FONT_DISPLAY);

/** One line of text. `body: true` uses the body face. */
export function txt(x: number, y: number, s: string, o: TextOpts) {
  if ((o.opacity ?? 1) <= 0.003) return "";
  return `<text x="${f1(x)}" y="${f1(y)}" font-family="${family(o)}" font-size="${o.size}" font-weight="${o.weight ?? 700}" fill="${o.fill ?? C.INK}" text-anchor="${o.anchor ?? "start"}"${o.spacing ? ` letter-spacing="${o.spacing}"` : ""}${(o.opacity ?? 1) < 1 ? ` opacity="${(o.opacity ?? 1).toFixed(3)}"` : ""}>${esc(s)}</text>`;
}

/** A line whose words each have their own opacity (0..1) and colour: light them up as they are spoken. */
export function words(x: number, y: number, items: { s: string; o: number; fill?: string }[], o: TextOpts) {
  const spans = items.map((it, i) => `<tspan fill="${it.fill ?? o.fill ?? C.INK}" fill-opacity="${clamp(it.o).toFixed(3)}">${i ? " " : ""}${esc(it.s)}</tspan>`).join("");
  return `<text x="${f1(x)}" y="${f1(y)}" font-family="${family(o)}" font-size="${o.size}" font-weight="${o.weight ?? 700}" text-anchor="${o.anchor ?? "start"}" xml:space="preserve"${o.spacing ? ` letter-spacing="${o.spacing}"` : ""}>${spans}</text>`;
}

/** Rough width of a string in the display face. An estimate: check long labels in a capture. */
export function tw(s: string, size: number) {
  let w = 0;
  for (const ch of s) {
    if (" .,:;'il!|".includes(ch)) w += 0.55;
    else if ("jtfr()-".includes(ch)) w += 0.72;
    else if ("mwMW".includes(ch)) w += 1.5;
    else if (ch >= "A" && ch <= "Z") w += 1.17;
    else w += 1;
  }
  return w * size * C.GLYPH;
}

/** A solid rounded label. x is the left edge (or the centre with `center`), y the centre. */
export function label(x: number, y: number, s: string, o: { size?: number; fill?: string; color?: string; rot?: number; sc?: number; opacity?: number; center?: boolean } = {}) {
  const size = o.size ?? 48;
  const w = tw(s, size) + size * 1.15;
  const h = size * 1.72;
  const cx = o.center ? x : x + w / 2;
  const inner = `<rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}" rx="${f1(size * 0.3)}" fill="${o.fill ?? C.ACCENT}"/>
    ${txt(0, size * 0.345, s, { size, fill: o.color ?? C.ON_ACCENT, anchor: "middle" })}`;
  return g(inner, cx, y, o.sc ?? 1, o.rot ?? 0, o.opacity ?? 1);
}
export const labelW = (s: string, size: number) => tw(s, size) + size * 1.15;

/** A white panel with a soft shadow, centred on (x, y). Put `shadowDef` once in the same svgDoc. */
export const shadowDef = `<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="22" stdDeviation="24" flood-color="${C.INK}" flood-opacity="0.14"/></filter></defs>`;
export function panel(x: number, y: number, w: number, h: number, inner = "", o: { fill?: string; r?: number; sc?: number; rot?: number; opacity?: number; shadow?: boolean } = {}) {
  const body = `<rect x="${f1(-w / 2)}" y="${f1(-h / 2)}" width="${f1(w)}" height="${f1(h)}" rx="${o.r ?? 28}" fill="${o.fill ?? C.SURFACE}"${o.shadow === false ? "" : ` filter="url(#sh)"`}/>${inner}`;
  return g(body, x, y, o.sc ?? 1, o.rot ?? 0, o.opacity ?? 1);
}

/** Organic blob outline around (0,0); `wob` animates it. A quiet moving shape for holds. */
export function blobPath(r: number, seed = 0, wob = 0, k = 0.13) {
  const n = 56;
  let d = "";
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rad = r * (1 + k * Math.sin(2 * a + seed) + k * 0.6 * Math.sin(3 * a + seed * 1.7 + wob) + k * 0.35 * Math.sin(5 * a + seed * 2.3 - wob * 1.3));
    d += `${i ? "L" : "M"}${f1(Math.cos(a) * rad)} ${f1(Math.sin(a) * rad * 0.86)}`;
  }
  return d + "Z";
}
export const blob = (x: number, y: number, r: number, fill: string, wob = 0, seed = 0, opacity = 1) =>
  g(`<path d="${blobPath(r, seed, wob)}" fill="${fill}" stroke-linejoin="round"/>`, x, y, 1, 0, opacity);

/** A person: a dot with an optional ring. Use for people in diagrams; real people belong in illustrations. */
export function person(x: number, y: number, r: number, fill: string, ring: string | null = null, s = 1, opacity = 1) {
  return g(`${ring ? `<circle r="${f1(r + 9)}" fill="none" stroke="${ring}" stroke-width="5"/>` : ""}<circle r="${f1(r)}" fill="${fill}"/>`, x, y, s, 0, opacity);
}

/** A speech bubble centred on (x, y) with a short mark inside. */
export function bubble(x: number, y: number, mark: string, s = 1, fill = C.ACCENT, color = C.ON_ACCENT, opacity = 1) {
  const inner = `<path d="M-30 -32 H30 A14 14 0 0 1 44 -18 V12 A14 14 0 0 1 30 26 H2 L-16 44 L-12 26 H-30 A14 14 0 0 1 -44 12 V-18 A14 14 0 0 1 -30 -32 Z" fill="${fill}"/>
    ${txt(0, 12, mark, { size: 44, fill: color, anchor: "middle" })}`;
  return g(inner, x, y, s, 0, opacity);
}

/** A check mark that draws itself, p 0..1. */
export function check(x: number, y: number, size: number, p: number, color = C.ON_ACCENT, width = 0.16) {
  if (p <= 0) return "";
  return `<path d="M${f1(x - size * 0.42)} ${f1(y + size * 0.02)} L${f1(x - size * 0.1)} ${f1(y + size * 0.32)} L${f1(x + size * 0.45)} ${f1(y - size * 0.3)}" fill="none" stroke="${color}" stroke-width="${f1(size * width)}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="${clamp(p).toFixed(3)} 1"/>`;
}

/** Quadratic arc from a to b, lifted by `lift` x distance; drawn up to p. */
export function arc(a: [number, number], b: [number, number], lift: number, p: number, stroke: string, width: number, opacity = 1, dash = "") {
  if (p <= 0 || opacity <= 0.003) return "";
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const cx = mx, cy = my - d * lift;
  const da = dash ? ` stroke-dasharray="${dash}"` : ` pathLength="1" stroke-dasharray="${clamp(p).toFixed(4)} 1"`;
  return `<path d="M${f1(a[0])} ${f1(a[1])} Q${f1(cx)} ${f1(cy)} ${f1(b[0])} ${f1(b[1])}" fill="none" stroke="${stroke}" stroke-width="${f1(width)}" stroke-linecap="round"${da}${opacity < 1 ? ` opacity="${opacity.toFixed(3)}"` : ""}/>`;
}
/** Point at p along the same arc, for something that travels along it. */
export function arcAt(a: [number, number], b: [number, number], lift: number, p: number): [number, number] {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  const d = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const cx = mx, cy = my - d * lift;
  const q = 1 - p;
  return [q * q * a[0] + 2 * q * p * cx + p * p * b[0], q * q * a[1] + 2 * q * p * cy + p * p * b[1]];
}

/** A bar that fills from the left, p 0..1: for scales, progress and simple charts. */
export function bar(x: number, y: number, w: number, h: number, p: number, fill = C.ACCENT, track = C.LINE) {
  return `<rect x="${f1(x)}" y="${f1(y)}" width="${f1(w)}" height="${f1(h)}" rx="${f1(h / 2)}" fill="${track}"/>
    ${p > 0.001 ? `<rect x="${f1(x)}" y="${f1(y)}" width="${f1(Math.max(h, w * clamp(p)))}" height="${f1(h)}" rx="${f1(h / 2)}" fill="${fill}"/>` : ""}`;
}
