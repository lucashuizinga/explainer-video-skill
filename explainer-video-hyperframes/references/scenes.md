# Building scenes

Read `index.html`, `timeline.js` and the three files in `compositions/` in the project next to this
file: they are a small, complete film in this pattern, and the fastest way to understand it. Load
`/hyperframes` for the render contract; this file covers how the voice clock sits on top of it.

## Contents

1. The files
2. How the times get into the HTML
3. The pattern of a scene
4. Looking up moments
5. Building blocks
6. Motion
7. Composition
8. Pictures with a camera
9. Cuts and transitions
10. Recipes
11. The check loop

## 1. The files

| File | What it is |
| --- | --- |
| `script.json` | The narration, voices, pauses. The source of all timing. |
| `assets/vo/words.json` | The time of every spoken word, written by `tools/voice.py`. |
| `assets/vo/data.js` | The two above as a script the page can load. Written by `tools/sync.mjs`; never edit it. |
| `lib/clock.js` | Turns the words into film times: `FILM.S`, `FILM.at()`, `FILM.END`, `FILM.ease`. |
| `timeline.js` | `FILM.T`: where each scene starts. You edit this. |
| `lib/kit.js` | GSAP helpers: `speak`, `view`, `sway`, `cutIn`, `cutOut`, `blob`. |
| `index.html` | The brand block, the shared building blocks (CSS), one host per scene, all sound. |
| `compositions/<id>.html` | One scene: its styles, markup and timeline inside `<template>`. |

The root (`index.html`) holds only scene hosts and `<audio>`. Everything you see lives in a scene file.

## 2. How the times get into the HTML

HyperFrames reads plain numbers from `data-start` and `data-duration`. You never type them. You write
what the time *is*, and `node tools/sync.mjs` computes the number:

```html
<div id="picture" data-composition-id="picture" data-composition-src="compositions/picture.html"
  data-at="T.picture" data-until="T.close" data-start="10.42" data-duration="5.38" ...></div>

<audio id="sfx-first" class="clip" src="assets/sfx/pluck.mp3"
  data-at="at('First the voice')" data-db="-14" data-start="5.94" data-duration="0.48" data-volume="0.2" ...></audio>
```

| You write | `sync.mjs` writes |
| --- | --- |
| `data-at="<expression>"` | `data-start` |
| `data-until="<expression>"` | `data-duration` (the end minus the start) |
| `data-db="-14"` | `data-volume` (decibels to gain) |
| an `<audio>` with `data-at` and no `data-until` | `data-duration`, the length of its file |
| `<!-- voice:start -->` to `<!-- voice:end -->` | one `<audio>` per spoken part of the voice |

An expression is JavaScript with `S`, `T`, `at` and `END` in scope. Use single quotes inside it:
`data-at="at('First the voice') - 0.1"`. In a scene file the result is converted to that scene's clock
for you.

Run `node tools/sync.mjs` after changing `script.json`, `timeline.js` or any `data-at`. `tools/voice.py`
runs it after a new take. `node tools/sync.mjs --check` (and `tools/doctor.py`) tell you when the HTML is
behind.

## 3. The pattern of a scene

**a. Its start**, in `timeline.js`, a little before its first word:

```js
T.picture = S.s2.t0 - 0.5;
```

**b. Its host**, in `index.html`. The id is the same in four places: host id and `data-composition-id`,
the scene root's `data-composition-id`, the key in `window.__timelines`, and the key in `T`.

**c. The scene file.** Styles, markup and script all inside `<template>`:

```html
<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: var(--bg); }
    #hook-title { font-size: 176px; line-height: 1; }
  </style>

  <div id="root" data-composition-id="hook" data-width="1920" data-height="1080">
    <!-- the end state, written out as plain HTML: what the frame looks like when everything has arrived -->
    <div class="at" style="left: 960px; top: 520px"><h1 id="hook-title">This is a template.</h1></div>
  </div>

  <script>
    (function () {
      const F = window.FILM;
      const { S, T, ease: E } = F;
      const L = F.local("hook");                 // film time to this scene's clock
      const tl = gsap.timeline({ paused: true });

      // 1. Moments, looked up from the voice
      const M = { title: S.s1.at("This is a template") };

      // 2. Every tween sits at a moment
      tl.fromTo("#hook-title", { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "none" }, L(M.title - 0.05));
      tl.fromTo("#hook-title", { scale: 1.3 }, { scale: 1, duration: 0.5, ease: E.expoOut }, L(M.title - 0.05));

      // 3. Register the timeline last
      window.__timelines["hook"] = tl;
    })();
  </script>
</template>
```

- Write the markup as the finished frame, then animate towards it with `fromTo`. The start state lives in
  the tween, not in the CSS.
- Wrap the script in a function so its names stay out of the other scenes.
- Prefix every id with the scene's id (`hook-title`): ids must be unique across the whole film.
- Start a move slightly before its word (0.05 to 0.15 s) so it is visible when the word lands. Start a
  scene 0.4 to 0.7 s before its first word.

## 4. Looking up moments

- `S.s2.at("phrase")`: when the first word of the phrase is spoken in segment `s2`.
- `S.s2.at("phrase", 1, 2)`: when word 2 of the phrase is spoken (counting from 0). Use it to hit the noun
  at the end of a sentence.
- `S.s2.at("word", 2)`: the second time it occurs.
- `S.s2.endOf("phrase")`: when the phrase has been said.
- `S.s2.t0`, `S.s2.end`: where the segment starts and ends.
- `S.s2.starts[i]`: the time of every word. `S.s2.find("phrase")` gives the index of its first word.
- `FILM.at("phrase")` searches all segments in order.
- `FILM.END`: the last frame. `T.<scene>`: where a scene starts.

All of these are **film times**. A scene's timeline starts at 0 when the scene starts, so wrap every film
time in `L(...)` when you place a tween: `L(M.title - 0.05)`.

Punctuation and capitals do not matter in a phrase. If a phrase is not in the voice the scene stops with
"Phrase not found", naming the phrase. That is deliberate: a silent fallback would let picture and voice
drift apart.

## 5. Building blocks

CSS classes in `index.html`, shared by every scene:

| Class | What it gives |
| --- | --- |
| `.at` | A point on the frame (`style="left: 960px; top: 520px"`). Its child is centred on that point, and scales and turns around it. This is how you place something GSAP will move: GSAP may not move an element that already has a CSS `transform`. |
| `.w` | One word of a line that lights up as it is spoken. |
| `.label` | A solid rounded label in the accent colour. Set its `font-size`. |
| `.panel` | A white card with a soft shadow. Set its width and height. |
| `.cam`, `.pin` | A picture seen through a camera, and a point on it that keeps its size (section 8). |
| `.cut`, `.sweep` | A coloured panel that crosses the frame to hide a cut (section 9). |

Helpers in `lib/kit.js`, each adding tweens to the timeline you pass:

| Helper | What it does |
| --- | --- |
| `F.speak(tl, "#line", S.s1, "Every move", L)` | Lights up each `.w` in `#line` on its spoken word |
| `F.view(z, px, py)` | A camera view, as values for a `.cam` tween |
| `F.sway(tl, target, "y", 6, 5, length, { phase, t0 })` | A slow continuous drift for holds |
| `F.cutOut(tl, "#x-out .sweep", length)`, `F.cutIn(tl, "#y-in .sweep")` | The two halves of a hidden cut |
| `F.blob(tl, "#path", { r, seed, speed, duration, t0 })` | A soft shape that keeps changing |

Add your own class or helper when a shape or move recurs. Search the HyperFrames registry before
hand-building a chart, a counter or a named transition (`/hyperframes-registry`).

## 6. Motion

Easings are in `FILM.ease` (pass them as `ease: E.inOut`). GSAP's own names work as well.

| Easing | Use |
| --- | --- |
| `E.snappyOut` | Arrivals with energy that settle softly |
| `E.expoOut` | Reveals, scale pops, counters |
| `E.spring` | Things that pop in with a little overshoot. Position and size only, never opacity |
| `E.snappyIn` | Exits that leave at speed |
| `E.expoIn` | Wind-up into a hard cut |
| `E.inOut` | From A to B, at rest on both ends: things changing place |
| `E.softInOut` | The same, gentler: slow camera pushes |

Rules that separate motion from slides:

- **Fastest at the cut.** Ease in to leave, cut, ease out to arrive.
- **Overlap.** The next thing starts arriving while the last is still leaving. Stagger siblings by 0.08 to
  0.15 s.
- **Keep the hold alive.** While a picture stays, something drifts: a shape in the background (`F.blob`
  with `F.sway`), a slow camera push, a counter. A landed title itself stays still.
- **Durations:** arrivals 0.3 to 0.6 s, exits 0.2 to 0.3 s, camera moves as long as the sentence.
- **One property, one tween at a time.** Two tweens that move the same property of the same element at
  the same moment fight. Give the second move its own wrapper (the template's title has one wrapper that
  punches in and one that rises).

`/hyperframes` has more in its `references/motion.md`: blur on fast moves, title entrances, transitions
with a cause. Use them where they serve the script.

## 7. Composition

- **Budget of zero for decoration.** No frames around things, no dividers, no icons for their own sake.
  An element earns its place by carrying meaning or guiding the eye.
- **One idea per scene,** one focal point per moment. A new sentence usually means something changes.
- **Type sizes at 1080p:** headline 90 to 180, label 56 to 80, small text never under 34.
- **Margins:** keep text 100 px from the edges.
- **Do not dim or blur a picture to make text readable.** Put the text on a solid `.label` or `.panel`,
  or in an empty part of the picture.
- **Text is short.** A word, a number, a name. If you are writing a sentence on screen, the voice should be
  saying it instead.
- **The accent colour is for emphasis,** a few times per scene.

## 8. Pictures with a camera

An illustration and the things drawn on it sit in one `.cam`. Tween the camera's three variables and
everything inside moves as one:

```html
<div id="desk-cam" class="cam" data-layout-allow-overflow>
  <img id="desk-img" src="assets/img/desk.jpg" alt="" />
  <!-- a point of the picture, in 1920x1080 coordinates -->
  <div class="pin" style="left: 1020px; top: 405px"><div id="desk-mic" class="label">the microphone</div></div>
</div>
```

```js
// from the whole picture to a detail, as long as the sentence
tl.fromTo("#desk-cam", F.view(1.04, 960, 540), { ...F.view(1.42, 1090, 480), duration: 6, ease: E.softInOut }, 0.2);
tl.fromTo("#desk-mic", { scale: 0.6 }, { scale: 1, duration: 0.6, ease: E.spring }, L(M.mic - 0.1));
tl.fromTo("#desk-mic", { opacity: 0 }, { opacity: 1, duration: 0.06, ease: "none" }, L(M.mic - 0.1));
```

- `z` is zoom, `(px, py)` is the point of the picture at the centre of the frame, in 1920x1080 coordinates.
- A `.pin` stays on its point of the picture and keeps its size on screen while the camera zooms.
- Keep `z x 1920` below the picture's pixel width.
- A camera move wants a destination: push towards the thing the sentence is about. It may still be moving
  when the scene is cut.
- To find coordinates, look at the picture: a point at 40% from the left and 30% from the top is (768, 324).
- A second move on the same camera uses `tl.to("#desk-cam", { ...F.view(...), duration, ease }, time)`.

## 9. Cuts and transitions

- **Hard cut on action** is the default. Let the outgoing scene move as it ends. The next scene starts
  where this one ends: `data-until="T.next"`.
- **Sweep:** a coloured panel crosses the frame and hides the cut. Use it for a change of chapter, with
  a `whoosh` 0.25 s before the cut. Each scene carries its own half, as its last element:

  ```html
  <!-- in the scene that ends -->
  <div id="a-out" class="clip cut" data-at="T.b - 0.3" data-until="T.b" data-layout-ignore><div class="sweep"></div></div>
  <!-- in the scene that starts, same colour -->
  <div id="b-in" class="clip cut" data-at="T.b" data-until="T.b + 0.3" data-layout-ignore><div class="sweep"></div></div>
  ```
  ```js
  F.cutOut(tl, "#a-out .sweep", length);   // length: this scene's own length
  F.cutIn(tl, "#b-in .sweep");
  ```
  The `.cut` is a timed clip, so the panel only exists during the cut. Colour it with a `style` on the
  `.sweep`.
- **Carry:** one element (a coin, a dot, the brand shape) is in the same place and size at the end of one
  scene and the start of the next. The strongest transition, when the element is the same thing in both.
- **Cross-fade** only between two pictures of the same subject.
- Never leave a frame empty between scenes. Every scene root has the page colour as background;
  overlapping exits and entrances inside a scene guarantee content.

## 10. Recipes

**A word that punches in.**
```js
tl.fromTo("#x", { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "none" }, L(a));
tl.fromTo("#x", { scale: 1.35 }, { scale: 1, duration: 0.5, ease: E.expoOut }, L(a));
```

**A sentence that lights up as it is spoken.** One `.w` per spoken word, in order:
```html
<p id="x-line"><span class="w">Every</span> <span class="w">move</span> <span class="w">you</span> <span class="w">see</span></p>
```
```js
tl.fromTo("#x-line", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: E.snappyOut }, L(M.every - 0.2));
F.speak(tl, "#x-line", S.s1, "Every move", L);
```

**Cards on beats.** Each card arrives on "First" or "Then" and gets its name on the noun. See
`compositions/hook.html`.

**A counter.** Tween a plain object and write the text in `onUpdate`:
```js
const n = { v: 0 };
tl.to(n, { v: 7.8, duration: 1.1, ease: E.expoOut, onUpdate: () => (el.textContent = n.v.toFixed(1)) }, L(a));
```

**A bar that fills.** A track with a fill inside; tween the fill's `scaleX` from 0 with
`transformOrigin: "left center"`.

**A line that draws itself.** An SVG path with `pathLength="1"` and `stroke-dasharray="1"`; tween
`strokeDashoffset` from 1 to 0. The check marks in `compositions/hook.html` work this way.

**Something leaves.** `tl.to("#x", { opacity: 0, y: -40, duration: 0.25, ease: E.snappyIn }, L(b))`.

**A reveal through a shape.** Tween `clipPath` on a wrapper, for example
`{ clipPath: "circle(0% at 50% 50%)" }` to `{ clipPath: "circle(75% at 50% 50%)" }`.

## 11. The check loop

After every scene:

```sh
node tools/sync.mjs
npx hyperframes check --json
npx hyperframes snapshot --at 12.4,13.0,14.2,15.8
```

`check` runs lint, a runtime pass, a layout audit (text that overflows or overlaps), contrast and a few
craft measurements. Fix every error. A warning is a question: fix it, or keep it on purpose.

`snapshot` writes one PNG per time and a contact sheet under `.hyperframes/artifacts/snapshots/`. Take
them at the beats (a moment after each word you hung something on), and just before and after each cut.
Then read the sheet:

- Is every piece of text readable, complete and inside the frame?
- Is the right thing on screen for the words being said then?
- Is any frame empty, or any frame showing two scenes at once that should not?
- Do labels sit on what they name?
- Does it look like the brand?

Do not render to look at the film. Snapshots show the same frames in seconds.
