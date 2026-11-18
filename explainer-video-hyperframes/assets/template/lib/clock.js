// The voice clock. Word times come from the voice take (assets/vo/words.json, written by tools/voice.py);
// this file turns them into film times. It runs in the browser (the scenes) and in Node (tools/sync.mjs),
// so both get the same numbers. tools/_common.py holds the same arithmetic in Python: change one, change both.
(function (root) {
  const norm = (s) =>
    s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^\p{L}\p{N}]/gu, "");

  /** One spoken segment. `chapters` cut it into parts with a pause before each: [{ at: "phrase", gap: 0.5 }]. */
  function voice(id, src, words, t0, chapters) {
    const keys = words.map((x) => norm(x.w));
    /** Index of the first word of the n-th occurrence of a phrase, or -1. */
    const index = (phrase, n = 1) => {
      const p = phrase.split(/\s+/).map(norm).filter(Boolean);
      let hit = 0;
      for (let i = 0; i + p.length <= keys.length; i++) {
        if (p.every((k, j) => keys[i + j] === k) && ++hit === n) return i;
      }
      return -1;
    };
    const find = (phrase, n = 1) => {
      const i = index(phrase, n);
      if (i < 0) throw new Error(`Phrase not found in the voice (${id}): "${phrase}" #${n}`);
      return i;
    };
    // Chapters: cut points in source time, each with the silence inserted before it.
    const cuts = (chapters || []).map((c) => {
      const i = find(c.at);
      const prevEnd = i > 0 ? words[i - 1].e : 0;
      return { src: (prevEnd + words[i].s) / 2, gap: c.gap };
    });
    /** Source time to film time. */
    const map = (s) => t0 + s + cuts.filter((c) => s >= c.src).reduce((a, c) => a + c.gap, 0);
    /** Film time of a phrase: its first word, or word k of it (counting from 0). */
    const at = (phrase, n = 1, k = 0) => map(words[find(phrase, n) + k].s);
    /** Film time at which the last word of a phrase ends. */
    const endOf = (phrase, n = 1) => {
      const i = find(phrase, n) + phrase.split(/\s+/).filter((x) => norm(x)).length - 1;
      return map(words[i].e);
    };
    /** Film start time of every word, in order. */
    const starts = words.map((x) => map(x.s));
    // One audio clip per chapter, so the pauses are real silence.
    const bounds = [0, ...cuts.map((c) => c.src), words[words.length - 1].e + 0.5];
    const clips = bounds.slice(0, -1).map((a, i) => ({ src, start: map(a), mediaStart: a, duration: bounds[i + 1] - a }));
    const end = map(words[words.length - 1].e);
    return { id, at, endOf, map, clips, end, find, index, words, starts, t0 };
  }

  /** The whole film from script.json and words.json: S (segments by id), at(), END. */
  function build(script, WORDS) {
    const S = {};
    let cursor = script.lead_in ?? 1;
    for (const s of script.segments) {
      const words = WORDS[s.id];
      if (!words || !words.length) throw new Error(`No voice yet for segment "${s.id}". Run tools/voice.py with Python.`);
      cursor += s.gap ?? 0;
      S[s.id] = voice(s.id, `assets/vo/${s.id}.mp3`, words, cursor, s.chapters);
      cursor = S[s.id].end;
    }
    const VOICES = Object.values(S);
    /** Film time of the n-th occurrence of a phrase, searched through all segments in order. Word k of it with `k`. */
    const at = (phrase, n = 1, k = 0) => {
      let left = n;
      for (const v of VOICES) {
        let c = 0;
        while (v.index(phrase, c + 1) >= 0) c++;
        if (left <= c) return v.at(phrase, left, k);
        left -= c;
      }
      throw new Error(`Phrase not found in the voice: "${phrase}" #${n}`);
    };
    const film = { S, VOICES, at, END: cursor + (script.tail ?? 4), T: {}, ease, db };
    /** Film time to the local time of a scene: `const L = FILM.local("picture")`, then `L(at("a phrase"))`. */
    film.local = (id) => {
      if (!(id in film.T)) throw new Error(`No scene start T.${id} in timeline.js`);
      return (t) => Math.max(0, t - film.T[id]);
    };
    return film;
  }

  // Easings as plain functions; GSAP takes them as `ease: FILM.ease.inOut`. GSAP's own names work too.
  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const x = (t) => ((ax * t + bx) * t + cx) * t;
    const y = (t) => ((ay * t + by) * t + cy) * t;
    return (p) => {
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
  const ease = {
    snappyOut: bezier(0, 0.6, 0.4, 1), // arrivals with energy that settle softly
    expoOut: bezier(0.16, 1, 0.3, 1), // reveals, scale pops, counters
    snappyIn: bezier(0.6, 0, 1, 0.4), // exits that leave at speed
    expoIn: bezier(0.7, 0, 0.84, 0), // wind-up into a hard cut
    inOut: bezier(0.7, 0, 0.3, 1), // from A to B, at rest on both ends
    softInOut: bezier(0.45, 0, 0.55, 1), // slow camera pushes
    spring: (p) => (p >= 1 ? 1 : 1 - Math.exp(-6 * p) * Math.cos(10 * p)), // a little overshoot
  };
  /** Decibels to the linear gain that `data-volume` takes. */
  const db = (d) => Math.pow(10, d / 20);

  root.Clock = { build, voice, ease, db };
})(typeof window !== "undefined" ? window : globalThis);
