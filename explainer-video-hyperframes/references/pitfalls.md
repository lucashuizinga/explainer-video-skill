# Pitfalls

Each of these cost real time on an earlier film, or is a way this setup fails silently. They are grouped
by where you meet them.

## The voice clock and the HTML

- **The HTML holds numbers, the voice holds the truth.** `data-start` and `data-duration` are written by
  `node tools/sync.mjs`. After a new take, a changed pause or chapter, an edit to `timeline.js` or a new
  `data-at`, run it. `tools/voice.py` does so itself. `node tools/sync.mjs --check` tells you when the HTML
  is behind; an old number does not fail, it just puts the picture in the wrong place.
- **Do not edit `data-start` by hand,** and do not let a timeline command do it for you
  (`npx hyperframes timeline move`): the next sync overwrites it. Change the `data-at` expression.
- **Scene time is not film time.** `at()` and `S.s1.at()` give film times; a scene's timeline starts at 0
  when the scene starts. Wrap every film time in `L(...)`. A tween that lands seconds late, or a scene
  where everything is already there in its first frame, is usually a missing `L`.
- **A scene needs an entry in `T`.** `F.local("picture")` and `sync.mjs` both stop when `T.picture` is
  missing from `timeline.js`.
- **No fetching at render time.** The page may not load `words.json` itself, which is why the data comes
  in through `assets/vo/data.js`. Do not replace that with `fetch`.

## Scene files

- **Everything inside `<template>`.** Styles, markup, scripts. The `<head>` of a scene file is dropped
  without a warning; the scene then shows tiny unstyled text in the top left corner.
- **One id, four places.** Host id and `data-composition-id`, the scene root's `data-composition-id`, the
  key in `window.__timelines`, the key in `T`. A mismatch makes the render wait and then show a still.
- **Register the timeline last,** after every tween, and wrap the script in a function so `tl`, `L` and
  `M` do not collide with the next scene's.
- **Ids are global.** Two scenes with an element `#title` break each other. Prefix: `#hook-title`.
- **The root holds only scenes and sound.** A timed `<div>` with children directly in `index.html` draws
  the warning `nested_structure_needs_subcomposition`. That is why a cut's sweep lives in the two scenes
  around it, not in the root.

## GSAP

- **`fromTo` first, `to` after.** The first tween on a property is a `fromTo`, so the scene has its start
  state when it is seeked backwards. A later tween on the same property is a `to`; a second `fromTo`
  would apply its start state from the beginning of the scene.
- **No CSS `transform` on an element GSAP moves.** Lint rejects it. Place the element with an `.at` anchor
  (or `left`/`top`) and let GSAP scale, move and turn the child.
- **Do not tween `display`, `visibility` or `autoAlpha` on a `.clip`.** Fade a child with `opacity`.
- **Two tweens, one property, one moment: they fight.** Give the second move its own wrapper element.
- **Transforms do nothing on an inline `<span>`.** `.w` is `inline-block` for that reason.
- **No `repeat: -1`, no `Math.random()`, no `Date.now()`, no timers.** A loop gets a finite repeat count;
  `F.sway` and `F.blob` take the scene's length.
- **A function ease may return any number,** which is how `F.sway` draws a sine wave. Keep it a pure
  function of its input.

## Sound

- **Every `<audio>` needs an `id`,** or it is left out of the mix without an error.
- **An `<audio>` without a length counts as playing to the end of the film.** Lint then reports overlapping
  audio on one track. `sync.mjs` writes each effect's real length; run it after adding one.
- **Levels are gain, not decibels.** `data-volume="1"` is 0 dB. Write `data-db="-14"` and let `sync.mjs`
  convert it.
- **The voice block is generated.** Whatever you write between `<!-- voice:start -->` and
  `<!-- voice:end -->` is replaced on the next sync.

## Voice

- **Eleven v4 has no SSML and no speed control.** Direction goes in square brackets, in English, and is
  not spoken. Pace comes from the tag, punctuation and the pauses in `script.json`.
- **Bracketed tags are left out of the word times,** so they never count as words in a phrase.
- **The word times come from listening, not from the voice model.** Through OpenRouter the voice comes
  back as sound only. `voice.py` has the take transcribed and lines the heard words up with the written
  ones. Read the differences it prints: "30" heard as "thirty" is fine, a word that was not heard is not.
- **Set the language code.** `language` in `script.json` goes to the transcription, which otherwise guesses.
- **Voices are names, and they carry no language.** `python3 tools/voices.py` lists them. Judge a voice
  on a short take in the film's language before generating everything.
- **A take can open with almost a second of silence.** The `gap` comes on top of it, so the pause before
  that segment is longer than you asked for. `python3 tools/times.py --words s2` shows when the first word
  starts; lower the `gap` to make up for it. Do not go so low that the take starts before the file of the
  take before it has ended, or lint reports two voice clips playing at once.
- **Takes differ, and a seed does not repeat them.** Regenerating a segment gives a new performance with
  new timings. Scenes survive that because they look up phrases. Do not regenerate a take you like.
- **Voice and music are refused below $0.50 of balance,** even when the call costs less. The error is a
  402. A text-only call to the music model still goes through and is charged without returning music, so
  always use `tools/music.py`.
- **A key can be limited to certain models.** A 404 "blocked by guardrail" means the user must allow that
  model for the key. `tools/doctor.py` shows which of the four is missing.
- **Raw takes can peak above full scale once levelled.** `voice.py` applies a limiter after the gain;
  if you level audio yourself, do the same.

## Pictures and fonts

- **Check the size you got.** A request for a large image does not always return one. `image.py` prints
  the pixel size; never zoom past `width / 1920`.
- **Generated pictures contain mistakes.** A staff-room clock showed a time that contradicted the
  narration; the fix was to frame the camera below it. Look at every picture at full size.
- **Disturbing metaphors get rejected.** See `references/images.md`, "Dignity".
- **Real-world things as thick-stroke SVG look amateurish.** Use an illustration, or keep the thing small.
- **ffmpeg may lack a WebP encoder.** Keep pictures as JPEG or PNG.
- **A font that is not bundled falls back silently.** The film renders, in the wrong typeface. Declare it
  with `tools/font.py` and look at a snapshot.
- **Asset paths start at the project folder,** in scene files too: `assets/img/desk.jpg`, no leading slash
  and no `../`.

## Music and mix

- **Generate the score after the voice is final.** A score made for an earlier cut does not line up with
  the film, and you will hear it.
- **The music model ignores the length and the sections you ask for.** Asked for 23 seconds it gave 63.
  `music.py` cuts the film's length out of a longer piece; choose the part with `--map` and `--from`.
- **A piece can contain a long silence with a stray tail after it.** `music.py` stops the piece at the
  first silence of two seconds or more.
- **Pieces come back with peaks above full scale.** Bake the level with `mix_music.py` instead of setting
  one volume in the film.
- **There is no tool for new sound effects.** Use the twelve in `assets/sfx/`, or a file from the user.
- **Re-run `mix_music.py` after any timing change.** It reads the current timeline.

## HyperFrames tools

- **`check` passing does not mean the film looks right.** It measures; it does not see. Read snapshots.
- **A full-frame element that stays in the scene can trip `check` now and then.** A cut's panel that was
  only moved off screen gave an occasional false "text is hidden" or contrast finding, on one run in
  four. Make such an element a timed clip (`class="clip"` with `data-at` and `data-until`) so it only
  exists while it is used, as the template's `.cut` does. If a finding names a time, snapshot that time
  before you believe it.
- **`check` keeps its last result.** After a change it runs again by itself; `--no-cache` forces a run.
- **`transcribe` writes `transcript.json` next to the file it was given.** Harmless; do not mistake it for
  part of the project.
- **The project gets a `.hyperframes/` folder** with snapshots, check reports and history. It is in
  `.gitignore`. Do not delete it while you work.
- **Do not render to check your work.** Use `snapshot`. Render once, at the end, or when asked.

## Windows

The tools were made safe for Windows and tested under a non-UTF-8 locale on macOS, but not on a
Windows machine. These are the places where Windows differs:

- **`python3` may open the Microsoft Store.** It is a stub. Use `python` or `py -3` wherever a command
  here says `python3`. The tools print their own hints with the right name.
- **A new program needs a new terminal.** After installing Node.js, Python or ffmpeg, "not found"
  usually means the terminal is older than the install. Close Claude Code and open it again.
- **Write text files with the file tool, not with a shell redirect.** Windows PowerShell writes
  `>` and `Out-File` output as UTF-16, which neither Python nor Node reads as JSON. `script.json`,
  `.env`, `tools/music.txt` and the HTML are UTF-8. A byte order mark in front is tolerated.
- **Letters with accents turn into two odd characters** ("Ã©" for "é"): a file was written in another
  encoding than UTF-8. Write it again as UTF-8. The tools read and write UTF-8 themselves.
- **`&&` between commands** is not accepted by the older Windows PowerShell. Run the commands one at a
  time.
- **To play the result:** `start exports\film.mp4` on Windows, `open` on macOS, `xdg-open` on Linux.

## Process

- **Do not type times.** If you find a bare number of seconds in a `data-start` you wrote or in a tween
  position (other than a small offset from a moment), replace it with a phrase lookup.
- **Do not build the whole film and then look.** Snapshot after every scene. Problems found early are
  one edit; found late they are spread over every scene.
- **Do not improvise facts.** Everything said comes from the user's source.
- **Keys stay in `.env`.** Never in a command line, a commit, the chat or a file you share.
