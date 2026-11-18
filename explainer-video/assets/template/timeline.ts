// The timeline. The voice is the clock: every time in the film is looked up from a spoken word.
// Segments, pauses and chapters live in script.json, so the Python tools compute the same times.

import script from "./script.json";
import WORDS from "./assets/vo/words.json";
import { voice } from "./lib/vo";
import type { Voice, Word, Chapter } from "./lib/vo";

type Seg = { id: string; voice: string; text: string; gap?: number; chapters?: Chapter[] };

const segs: Record<string, Voice> = {};
let cursor = script.lead_in;
for (const s of script.segments as Seg[]) {
  const words = (WORDS as Record<string, Word[]>)[s.id];
  if (!words || !words.length) throw new Error(`No voice yet for segment "${s.id}". Run: python3 tools/voice.py`);
  cursor += s.gap ?? 0;
  segs[s.id] = voice(`vo/${s.id}.mp3`, words, cursor, s.chapters);
  cursor = segs[s.id].end;
}

/** Each segment by id: S.s1.at("a phrase"), S.s1.t0, S.s1.end. */
export const S = segs;
export const VOICES = Object.values(segs);
/** Last frame: the end of the voice plus the tail from script.json. */
export const END = cursor + script.tail;

/** Video time of the n-th occurrence of a phrase, searched through all segments in order. Word k of it with `k`. */
export function at(phrase: string, n = 1, k = 0) {
  let left = n;
  for (const v of VOICES) {
    let c = 0;
    while (v.index(phrase, c + 1) >= 0) c++;
    if (left <= c) return v.at(phrase, left, k);
    left -= c;
  }
  throw new Error(`Phrase not found in the voice: "${phrase}" #${n}`);
}

// ---------------------------------------------------------------------------------------------
// Shot boundaries. A shot starts a little before its first word, so the picture is there when
// the voice begins. Edit this block for your film; keep everything else as it is.
// ---------------------------------------------------------------------------------------------
export const T = {
  picture: S.s2.t0 - 0.5,
  close: S.s3.t0 - 0.5,
};
