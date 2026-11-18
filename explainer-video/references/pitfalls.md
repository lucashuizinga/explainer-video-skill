# Pitfalls

Each of these cost real time on an earlier film. They are grouped by where you meet them.

## Diffusion Studio and the project

- **One `<scene>` per project.** With two, `dapi capture` failed with "Cannot read properties of undefined
  (reading 'add')" a few seconds into the film. A second film is a second project folder.
- **JSX must live inside the project folder.** A `.tsx` file outside it is not compiled the right way
  ("DOM content must be inside `<html>`"). Plain `.ts` modules outside the folder import fine.
- **Type-only imports need `import type`.** `import { Cam } from "./lib/draw"` fails with "No matching
  export". Write `import type { Cam } from "./lib/draw"`.
- **A copied `package.json` carries a `projectId`.** Two folders with the same id open as the same
  project. `scripts/new_project.py` removes it; if you copy a project by hand, delete that line first.
- **The tools act on the open project.** `dapi check film` and `dapi capture film` run against whatever
  folder the app has open, which may be someone's other project with a scene of the same id. Run
  `dapi open -b "<your folder>"` at the start of every session and confirm with `dapi context`.
- **Compile errors are silent in the terminal.** Saving a broken file leaves the last good version on
  screen. `python3 tools/logs.py` shows the error. Plain `dapi logs` dumps thousands of export progress
  lines; do not read it raw.
- **"Error drawing HtmlPaint content ... No cached paint record"** in the log right after opening or
  saving is harmless if the captures look right.
- **A new file in `assets/` is not found.** Name assets by their path under `assets/` (`"img/desk.jpg"`,
  `"vo/s1.mp3"`). If a new file does not resolve, run `dapi open -b` on the folder again.
- **`dapi check` can report black frames that are not there.** A stretch where the only visual is an
  `<image>` moved by a camera was flagged as "no visuals scheduled" while the frames were fine. The `Card`
  under everything in `film.tsx` prevents the report. If you still get one, capture the span before you
  believe it.
- **Do not export to check your work.** Use `dapi capture`. Export once, at the end, or when asked.

## Drawing in `<html>` shots

- **`clipPath` is dropped** when the SVG is rasterised. Do not design anything that needs clipping: use
  shapes that cover instead, or a round `<image>` for a lens.
- **A shot that slides must move its background too.** Give `svgDoc` a `bg` and the `dx`/`dy`. Without a
  background the layer is transparent; with a background that stays put, it blanks the shot underneath.
- **An easing must return exactly 0 at the start and 1 at the end.** Code checks `> 0` to decide whether
  something has started. The `bezier` in `lib/motion.ts` guarantees it; keep that if you add curves.
- **Text is not measured.** `tw()` estimates widths. Long labels and anything in a tight box need a look
  in a capture. A panel that overflowed its text, and a card that was empty for a few frames during a
  page switch, were both only found by capturing.
- **Escape text.** `txt()` and `words()` escape `&` and `<` for you. Raw SVG strings you build yourself do
  not.
- **Sub-pixel motion stutters.** Nothing renders between pixels, so a drift slower than about one pixel
  per frame sits still and jumps.

## JSX attributes

- **Array props are read once.** Animated corner radii passed as an array stayed at their first value.
  Read each value inside the attribute expression (`cornerRadiusTopLeft={r(t())}`), not from a prebuilt
  array.
- **`<video>` has no playback rate.** Slow or speed a clip with ffmpeg before using it.
- **Reused ids are fine** in components that render many times (`Layer`, `Sfx`); the app handles them.

## Voice

- **A take can open with almost a second of silence.** The `gap` comes on top of it, so the pause before
  that segment is longer than you asked for. `python3 tools/times.py --words s2` shows when the first word
  starts; lower the `gap` to make up for it. Do not go so low that the take starts before the file of the
  take before it has ended, or the two takes play over each other.
- **Eleven v4 has no SSML and no speed control.** Direction goes in square brackets, in English, and is
  not spoken. Pace comes from the tag, punctuation and the pauses in `script.json`.
- **Bracketed tags are left out of the word times,** so they never count as words in a phrase.
- **Send the language code.** `language` in `script.json` tells the model what language the text is in.
- **A voice id may not exist on another account.** Premade voices are everywhere; library and cloned
  voices are per account. `tools/doctor.py` checks the ids in `script.json`.
- **Takes differ.** Regenerating a segment gives a new performance with new timings. Shots survive that
  because they look up phrases. Add a `seed` to keep a take reproducible.
- **Raw takes can peak above full scale once levelled.** `voice.py` applies a limiter after the gain;
  if you level audio yourself, do the same.

## Pictures

- **Check the size you got.** A request for a large image does not always return one. `image.py` prints
  the pixel size; never zoom past `width / 1920`.
- **Generated pictures contain mistakes.** A staff-room clock showed a time that contradicted the
  narration; the fix was to frame the camera below it. Look at every picture at full size.
- **Disturbing metaphors get rejected.** See `references/images.md`, "Dignity".
- **Real-world things as thick-stroke SVG look amateurish.** Use an illustration, or keep the thing small.
- **ffmpeg may lack a WebP encoder.** Keep pictures as JPEG or PNG.

## Music and mix

- **Generate the score after the voice is final.** A score made for an earlier cut does not line up with
  the film, and you will hear it.
- **Use a composition plan for anything over half a minute.** One prompt gives one mood; a plan gives the
  film's shape.
- **Scores get louder section by section.** Bake the level with `mix_music.py` instead of setting one
  volume in the film.
- **Re-run `mix_music.py` after any timing change.** It reads the current timeline.

## Process

- **Do not type times.** If you find a bare number of seconds in a shot (other than a small offset from a
  moment), replace it with a phrase lookup.
- **Do not build the whole film and then look.** Capture after every chapter. Problems found early are
  one edit; found late they are spread over every shot.
- **Do not improvise facts.** Everything said comes from the user's source.
- **Keys stay in `.env`.** Never in a command line, a commit, the chat or a file you share.
