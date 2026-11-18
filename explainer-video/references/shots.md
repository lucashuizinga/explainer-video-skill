# Building shots

Read `scenes/demo.ts` and `film.tsx` in the project next to this file: they are a small, complete film in
this pattern, and the fastest way to understand it.

## Contents

1. The files
2. The pattern of a shot
3. Looking up moments
4. Motion
5. Composition
6. Pictures with a camera
7. Cuts and transitions
8. Recipes
9. The check loop

## 1. The files

| File | What it is |
| --- | --- |
| `script.json` | The narration, voices, pauses. The source of all timing. |
| `timeline.ts` | Turns the script and the word times into `S` (segments), `at()`, `END`, and `T`, the shot boundaries you define. |
| `film.tsx` | The film: audio, then every shot from back to front, then the sound effects. |
| `scenes/*.ts` | The shots: functions of time that return SVG strings. One file per chapter or group of chapters, a few hundred lines at most. |
| `lib/brand.ts` | Colours and fonts. |
| `lib/motion.ts` | Easings and time helpers. |
| `lib/draw.ts` | Drawing primitives and the camera. |
| `lib/ui.tsx` | `Layer`, `Picture`, `Sfx`, `Whip`, `Card`. |
| `index.tsx` | The stage and the one scene, id `film`. |

Only `film.tsx`, `index.tsx` and `lib/ui.tsx` contain JSX. Scenes are plain `.ts`, which keeps them fast
to write and free of JSX pitfalls.

## 2. The pattern of a shot

```ts
// 1. Moments, looked up from the voice
export const HOOK = {
  title: S.s1.at("This is a template"),
  every: S.s1.at("Every move"),
  word: S.s1.at("hangs on a word", 1, 3),   // word 3 of the phrase, counting from 0
};

// 2. One function of time returns the whole shot
export function hookSvg(t: number) {
  const o: string[] = [];
  // 3. Every value is the time measured against a moment
  const up = inOut(prog(t, HOOK.every - 0.7, 0.5));            // 0 to 1 over half a second
  if (t >= HOOK.title - 0.05) {
    const sc = lerp(1.3, 1, expoOut(prog(t, HOOK.title - 0.05, 0.5)));
    o.push(g(txt(0, 60, "This is a template.", { size: 176, anchor: "middle" }), 960, lerp(520, 290, up), sc));
  }
  return svgDoc(o.join(""), undefined, C.BG);
}
```

And in `film.tsx`:

```tsx
<Layer from={0} to={T.picture + 0.05} svg={() => hookSvg(t())} name="1 the idea" />
```

`Layer` calls your function on every frame with the current time. The frame is a 1920x1080 SVG; draw in
those coordinates.

Start a move slightly before its word (0.05 to 0.15 s) so it is visible when the word lands. Start a shot
0.4 to 0.7 s before its first word.

## 3. Looking up moments

- `S.s2.at("phrase")`: when the first word of the phrase is spoken in segment `s2`.
- `S.s2.at("phrase", 1, 2)`: when word 2 of the phrase is spoken (counting from 0). Use it to hit the noun
  at the end of a sentence.
- `S.s2.at("word", 2)`: the second time it occurs.
- `S.s2.endOf("phrase")`: when the phrase has been said.
- `S.s2.t0`, `S.s2.end`: where the segment starts and ends.
- `S.s2.starts[i]`: the time of every word, for lighting up a sentence word by word. `S.s2.find("phrase")`
  gives the index of its first word.
- `at("phrase")` from `timeline.ts` searches all segments in order.

Punctuation and capitals do not matter in a phrase. If a phrase is not in the voice the film stops with
"Phrase not found", naming the phrase. That is deliberate: a silent fallback would let picture and voice
drift apart.

Shot boundaries go in `T` at the bottom of `timeline.ts`, each one a moment minus a little.

## 4. Motion

From `lib/motion.ts`. All are pure functions of time.

| Helper | Gives |
| --- | --- |
| `prog(t, a, d)` | 0 before `a`, 1 after `a + d`, linear between |
| `rise(t, a, d, ease?)` | The same, eased. For anything arriving |
| `fall(t, a, d, ease?)` | 1 down to 0 from `a`. Multiply an opacity by it to leave |
| `window_(t, a, b)` | In at `a`, out at `b` |
| `spring(p)` | 0 to 1 with a little overshoot. For things that pop |
| `lerp(a, b, p)` | Between two values |
| `shake(t, at, amp)` | A decaying judder after a hit |
| `sway(t, amp, period)` | A slow continuous drift, for holds |
| `mix(a, b, p)` | Between two hex colours |

Easings: pick one on purpose for every move.

| Easing | Use |
| --- | --- |
| `snappyOut` | Arrivals with energy that settle softly. The default for `rise` |
| `expoOut` | Reveals, scale pops, counters |
| `snappyIn` | Exits that leave at speed. The default for `fall` |
| `expoIn` | Wind-up into a hard cut |
| `outIn` | A move carried across a cut |
| `inOut` | From A to B, at rest on both ends: camera moves, things changing place |
| `softInOut` | The same, gentler: slow camera pushes |

Rules that separate motion from slides:

- **Fastest at the cut.** Ease in to leave, cut, ease out to arrive.
- **Overlap.** The next thing starts arriving while the last is still leaving. Stagger siblings by 0.08 to
  0.15 s.
- **Keep the hold alive.** While a picture stays, something drifts: a shape in the background (`blob` with
  `sway`), a slow camera push, a counter.
- **No drift slower than a pixel per frame.** Everything lands on whole pixels, so a slower move stutters.
  Ten pixels over three seconds is too slow; move further, or carry the hold with opacity or colour.
- **Durations:** arrivals 0.3 to 0.6 s, exits 0.2 to 0.3 s, camera moves as long as the sentence.

## 5. Composition

- **Budget of zero for decoration.** No frames around things, no dividers, no icons for their own sake.
  An element earns its place by carrying meaning or guiding the eye.
- **One idea per shot,** one focal point per moment. A new sentence usually means something changes.
- **Type sizes at 1080p:** headline 90 to 180, label 56 to 80, small text never under 34. Use
  `{ body: true }` for the body face.
- **Margins:** keep text 100 px from the edges.
- **Do not dim or blur a picture to make text readable.** Put the text on a solid label (`label`, `panel`)
  or in an empty part of the picture.
- **Text is short.** A word, a number, a name. If you are writing a sentence on screen, the voice should be
  saying it instead.
- **The accent colour is for emphasis,** a few times per shot.
- Label widths are estimated by `tw()`. Check long labels in a capture.

## 6. Pictures with a camera

An illustration is an `<image>`; drawings on top are a `Layer`. Give both the same camera and they move as
one.

```ts
// scenes: a slow push from the whole picture to a detail
export const deskCam = camPath([
  { t: T.desk, d: 1, z: 1.04, px: 960, py: 540 },                       // start view
  { t: T.desk + 0.2, d: T.next - T.desk + 0.6, z: 1.42, px: 1090, py: 480 },  // from here, move for d seconds
], softInOut);

export function deskSvg(t: number) {
  const cam = deskCam(t);
  // coordinates are the picture's own, so the label stays on the thing it names
  const a = spring(prog(t, DESK.mic - 0.1, 0.6));
  return svgDoc(label(1020, 405, "the microphone", { size: 56, center: true, sc: a / cam.z, opacity: a * 3 }), cam, null);
}
```

```tsx
<Picture name="Desk" src="img/desk.jpg" from={T.desk} to={T.next + 0.05} cam={() => deskCam(t())} opacity={() => rise(t(), T.desk, 0.4)} />
<Layer from={T.desk} to={T.next + 0.05} svg={() => deskSvg(t())} name="2 desk" />
```

- `z` is zoom, `(px, py)` is the point of the picture at the centre of the frame, in 1920x1080 coordinates.
- Divide a label's scale by `cam.z` to keep it the same size on screen while the camera zooms.
- Keep `z x 1920` below the picture's pixel width.
- A camera move wants a destination: push towards the thing the sentence is about.
- To find coordinates, look at the picture: a point at 40% from the left and 30% from the top is (768, 324).

## 7. Cuts and transitions

- **Hard cut on action** is the default. Let the outgoing shot move as it ends.
- **`Whip`**: a coloured panel sweeps across and hides the cut. Use it for a change of chapter, with a
  `whoosh` 0.25 s before. Put the `Whip` after the two shots in `film.tsx`, at the cut time. Give the
  outgoing shot an end 0.05 s after the cut.
- **Slide:** a shot that moves off (`svgDoc(inner, cam, bg, dx, dy)`) must carry its own background, so
  the shot under it shows as it leaves.
- **Carry:** one element (a coin, a dot, the brand shape) grows or travels from one shot into the next.
  The strongest transition, when the element is the same thing in both.
- **Cross-fade** only between two pictures of the same subject.
- Never leave a frame empty between shots. `Card` under everything guarantees a background; overlapping
  exits and entrances guarantees content.

## 8. Recipes

**A word that punches in.**
```ts
const sc = lerp(1.35, 1, expoOut(prog(t, a, 0.5)));
o.push(g(txt(0, size * 0.35, "Tired.", { size, anchor: "middle" }), 960, 500, sc, 0, clamp((t - a) / 0.1)));
```

**A sentence that lights up as it is spoken.**
```ts
const i0 = S.s1.find("Every move");
const items = ["Every", "move", "you", "see"].map((s, i) => ({ s, o: lerp(0.16, 1, rise(t, S.s1.starts[i0 + i] - 0.04, 0.16)) }));
o.push(g(words(0, 30, items, { size: 90, anchor: "middle" }), 960, 600));
```

**Cards on beats.** Each card arrives on "First" or "Then" and gets its name on the noun. See `hookSvg`.

**A counter.**
```ts
const n = Math.round(lerp(0, 7.8, rise(t, a, 1.1, expoOut)) * 10) / 10;
o.push(txt(960, 560, n.toFixed(1), { size: 160, anchor: "middle" }));
```

**A bar or scale that fills.** `bar(x, y, w, h, rise(t, a, 0.8))`, with a label that fades in at the end.

**A line that draws itself, and something travelling along it.** `arc(a, b, lift, p, colour, width)` and
`arcAt(a, b, lift, p)` for the position at `p`.

**A check mark on a done step.** `check(x, y, size, rise(t, a, 0.3))`.

**Something leaves.** Multiply its opacity by `fall(t, b, 0.25)` and move it with `inOut(prog(t, b, 0.5))`.

**A hit.** Add `shake(t, at, 10)` to an x position after a stamp lands, with `stamp.mp3` at the same time.

Add your own primitives to `lib/draw.ts` when a shape recurs: a function that returns an SVG string and
takes its animated values as parameters.

## 9. The check loop

After every chapter:

```sh
python3 tools/logs.py
dapi check film
dapi capture film -t 12.4 13.0 14.2 15.8 -o "$PWD/cache/frames"
```

`capture` takes up to twelve times and returns one contact sheet with a timecode on each frame. Capture at
the beats (a moment after each word you hung something on), and just before and after each cut. Then
read the sheet:

- Is every piece of text readable, complete and inside the frame?
- Is the right thing on screen for the words being said then?
- Is any frame empty, or any frame showing two shots at once that should not?
- Do labels sit on what they name?
- Does it look like the brand?

A warning from `dapi check` that a node has opacity 0 at its start is normal for anything that fades in.
An error about a source that failed to load is real. An error about an empty span usually is too, but
capture the span to be sure: the checker has flagged a camera-moved picture as empty when it was not.

Do not export to look at the film. `capture` shows the same frames in seconds.
