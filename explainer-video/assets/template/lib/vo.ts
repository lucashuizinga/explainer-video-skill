// Voice-over timing. Word times come from ElevenLabs (assets/vo/words.json, written by tools/voice.py).
// A segment can be cut into chapters with a pause before each one; `at()` returns the time on the video timeline.
// tools/_common.py holds the same arithmetic in Python: change one, change the other.

export type Word = { w: string; s: number; e: number };
export type Chapter = { at: string; gap: number };

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^\p{L}\p{N}]/gu, "");

export function voice(src: string, words: Word[], t0: number, chapters?: Chapter[]) {
  const keys = words.map((x) => norm(x.w));
  /** Index of the first word of the n-th occurrence of a phrase, or -1. */
  const index = (phrase: string, n = 1) => {
    const p = phrase.split(/\s+/).map(norm).filter(Boolean);
    let hit = 0;
    for (let i = 0; i + p.length <= keys.length; i++) {
      if (p.every((k, j) => keys[i + j] === k) && ++hit === n) return i;
    }
    return -1;
  };
  const find = (phrase: string, n = 1) => {
    const i = index(phrase, n);
    if (i < 0) throw new Error(`Phrase not found in the voice (${src}): "${phrase}" #${n}`);
    return i;
  };
  // Chapters: cut points in source time, each with the silence inserted before it.
  const cuts = (chapters ?? []).map((c) => {
    const i = find(c.at);
    const prevEnd = i > 0 ? words[i - 1].e : 0;
    return { src: (prevEnd + words[i].s) / 2, gap: c.gap };
  });
  /** Source time to video time. */
  const map = (s: number) => t0 + s + cuts.filter((c) => s >= c.src).reduce((a, c) => a + c.gap, 0);
  /** Video time of a phrase: its first word, or word k of it. */
  const at = (phrase: string, n = 1, k = 0) => map(words[find(phrase, n) + k].s);
  /** Video time at which the last word of a phrase ends. */
  const endOf = (phrase: string, n = 1) => {
    const i = find(phrase, n) + phrase.split(/\s+/).filter((x) => norm(x)).length - 1;
    return map(words[i].e);
  };
  /** Video start time of every word, in order. */
  const starts = words.map((x) => map(x.s));
  // One audio clip per chapter, so the pauses are real silence.
  const bounds = [0, ...cuts.map((c) => c.src), words[words.length - 1].e + 0.5];
  const clips = bounds.slice(0, -1).map((a, i) => ({ src, start: map(a), sourceIn: a, sourceOut: bounds[i + 1] }));
  const end = map(words[words.length - 1].e);
  return { at, endOf, map, clips, end, find, index, words, starts, t0 };
}
export type Voice = ReturnType<typeof voice>;
