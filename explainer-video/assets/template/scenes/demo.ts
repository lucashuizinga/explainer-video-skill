// The demo film: three shots that show the pattern. Replace this file with your own scenes.
//
// The pattern in every shot:
//   1. Look up the moments from the voice (an object of times, one per beat).
//   2. Write one function of time that returns the whole shot as an SVG string.
//   3. Inside it, every value is `rise`, `fall`, `spring` or `lerp` of the time against those moments.

import { S, T, END } from "../timeline";
import * as C from "../lib/brand";
import { clamp, prog, rise, fall, lerp, spring, expoOut, inOut, softInOut, sway } from "../lib/motion";
import { svgDoc, camPath, g, txt, words, label, panel, shadowDef, blob, check } from "../lib/draw";
import type { Cam } from "../lib/draw";

// =====================================================================
// 1. The idea: a title, a sentence that lights up word by word, three cards
// =====================================================================
export const HOOK = {
  title: S.s1.at("This is a template"),
  every: S.s1.at("Every move"),
  word: S.s1.at("hangs on a word", 1, 3), // the fourth word of the phrase
  first: S.s1.at("First the voice"),
  voice: S.s1.at("First the voice", 1, 2),
  then: S.s1.at("Then the timing"),
  timing: S.s1.at("Then the timing", 1, 2),
  last: S.s1.at("Then the shots"),
  shots: S.s1.at("Then the shots", 1, 2),
};

export function hookSvg(t: number) {
  const o: string[] = [];
  // something always moves, also while the picture holds
  o.push(blob(1480 + sway(t, 40, 9), 330 + sway(t, 26, 7, 1), 430, C.ACCENT_SOFT, t * 0.55, 1.1));

  // the title punches in, then rises to make room
  const up = inOut(prog(t, HOOK.every - 0.7, 0.5));
  const away = inOut(prog(t, HOOK.first - 0.3, 0.5));
  if (t >= HOOK.title - 0.05) {
    const sc = lerp(1.3, 1, expoOut(prog(t, HOOK.title - 0.05, 0.5))) * lerp(1, 0.52, up);
    o.push(g(txt(0, 60, "This is a template.", { size: 176, anchor: "middle" }), 960, lerp(520, 290, up) - away * 900, sc, 0, clamp((t - HOOK.title + 0.05) / 0.1) * (1 - away)));
  }

  // the sentence: each word lights up at the moment it is spoken
  const i0 = S.s1.find("Every move");
  const line = ["Every", "move", "you", "see", "hangs", "on", "a", "word."];
  if (t >= HOOK.every - 0.2) {
    const items = line.map((s, i) => ({
      s,
      o: lerp(0.16, 1, rise(t, S.s1.starts[i0 + i] - 0.04, 0.16)),
      fill: i === line.length - 1 ? C.ACCENT : C.INK,
    }));
    o.push(g(words(0, 30, items, { size: 90, anchor: "middle" }), 960, 600 - away * 900, 1, 0, rise(t, HOOK.every - 0.2, 0.25) * (1 - away)));
  }

  // three cards: each arrives on "First" or "Then" while the sentence is still leaving,
  // and gets its name on the noun. Entrances and exits overlap, so the frame is never empty.
  const steps = [
    { a: HOOK.first, b: HOOK.voice, n: "1", s: "the voice" },
    { a: HOOK.then, b: HOOK.timing, n: "2", s: "the timing" },
    { a: HOOK.last, b: HOOK.shots, n: "3", s: "the shots" },
  ];
  o.push(shadowDef);
  steps.forEach((st, i) => {
    if (t < st.a - 0.12) return;
    const p = spring(prog(t, st.a - 0.12, 0.7));
    const inner =
      g(`<circle r="56" fill="${C.ACCENT}"/>` + txt(0, 24, st.n, { size: 68, fill: C.ON_ACCENT, anchor: "middle" }), 0, -76) +
      txt(0, 96 + (1 - rise(t, st.b - 0.05, 0.3)) * 24, st.s, { size: 70, anchor: "middle", opacity: rise(t, st.b - 0.05, 0.2) }) +
      g(`<circle r="30" fill="${C.ACCENT_2}"/>` + check(0, 0, 34, rise(t, st.b + 0.3, 0.3)), 186, -146, rise(t, st.b + 0.25, 0.25, expoOut));
    o.push(panel(430 + i * 530, 560 + (1 - p) * 140 + sway(t, 6, 5, i), 480, 390, inner, { sc: lerp(0.7, 1, p), opacity: clamp(p * 3) }));
  });
  return svgDoc(o.join(""), undefined, C.BG);
}

// =====================================================================
// 2. A picture with a camera: the illustration is an <image>, the labels ride on the same camera
// =====================================================================
export const PIC = {
  illustration: S.s2.at("illustrations"),
  camera: S.s2.at("the camera", 1, 1),
};

/** A slow push into the picture. Zoom times 1920 must stay below the picture's pixel width. */
export const pictureCam = camPath(
  [
    { t: T.picture, d: 1, z: 1.04, px: 960, py: 540 },
    { t: T.picture + 0.2, d: T.close - T.picture + 0.6, z: 1.42, px: 1090, py: 480 },
  ],
  softInOut,
);

export function pictureSvg(t: number) {
  const cam: Cam = pictureCam(t);
  // labels in picture coordinates, so they stay on what they name while the camera moves
  const a = spring(prog(t, PIC.illustration - 0.1, 0.6));
  const b = spring(prog(t, PIC.camera - 0.1, 0.6));
  const out = fall(t, T.close - 0.3, 0.25);
  const inner =
    label(1020, 405, "an illustration", { size: 56, center: true, sc: lerp(0.6, 1, a) / cam.z, opacity: clamp(a * 3) * out }) +
    label(1520, 478, "the same camera", { size: 56, center: true, fill: C.ACCENT_2, sc: lerp(0.6, 1, b) / cam.z, opacity: clamp(b * 3) * out });
  return svgDoc(inner, cam, null);
}

// =====================================================================
// 3. The close: the brand, one line, and a hold that keeps moving
// =====================================================================
const CLOSE = {
  line: S.s3.at("your own story"),
};

export function closeSvg(t: number) {
  const o: string[] = [];
  o.push(blob(430 + sway(t, 34, 8), 760 + sway(t, 22, 6, 2), 380, C.ACCENT_SOFT, t * 0.5, 2.3));
  const p = spring(prog(t, T.close + 0.3, 0.8));
  // replace this label with the real logo (see references/brand.md)
  o.push(label(960, 440, "Your brand", { size: 120, center: true, sc: lerp(0.5, 1, p), opacity: clamp(p * 3) }));
  const i0 = S.s3.find("your own story");
  const items = ["Your", "own", "story."].map((s, i) => ({ s, o: lerp(0.14, 1, rise(t, S.s3.starts[i0 + i] - 0.04, 0.18)) }));
  o.push(g(words(0, 0, items, { size: 88, anchor: "middle" }), 960, 690, 1, 0, rise(t, CLOSE.line - 0.4, 0.3)));
  o.push(txt(960, 790, "Replace script.json, lib/brand.ts and scenes/demo.ts", { size: 34, weight: 500, fill: C.INK_SOFT, anchor: "middle", body: true, opacity: rise(t, CLOSE.line + 0.9, 0.5) * fall(t, END - 0.6, 0.5) }));
  return svgDoc(o.join(""), undefined, C.BG);
}
