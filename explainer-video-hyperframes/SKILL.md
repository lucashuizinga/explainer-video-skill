---
name: explainer-video-hyperframes
description: >-
  Make a narrated, animated explainer video (uitlegvideo, story animation,
  explainer animatie) in a company's brand, rendered with HyperFrames (HTML to
  video) with all media through OpenRouter on one OpenRouter API key: an
  Eleven v4 voice-over with word timings, Nano Banana 2.1 illustrations, Lyria
  music and sound effects, and every move timed to a spoken word. Use this
  when someone gives an OpenRouter key for a video, or when someone asks
  for an explainer video, uitlegvideo, animated explanation or "a video that
  explains X" for a brand or product and HyperFrames is the renderer: they
  name HyperFrames, there is no Mac with Diffusion Studio (a Linux or cloud
  machine), or they ask for the HyperFrames version of the explainer skill.
  The sibling skill explainer-video does the same with Diffusion Studio and
  separate ElevenLabs and Gemini keys. Not
  for cutting recorded footage such as talking heads, podcasts or screen
  recordings.
---

# Explainer video, on HyperFrames

You make a narrated animation of one to three minutes, 1920x1080, in the client's brand. The result is an
mp4 plus a project folder that anyone can open, preview and change.

This is the HyperFrames edition of the `explainer-video` skill. The method and the rules of craft are the
same. Two things differ. The renderer: scenes are HTML and CSS moved by GSAP, and HyperFrames turns them
into video. And the media: voice, word times, illustrations and music all come through OpenRouter, on one
key.

## The idea that makes these videos good

**The voice is the clock.** The voice-over is generated first, with the start and end time of every word.
Nothing in the film has a hand-typed time. A scene asks `at("a phrase from the script")` and gets the
moment that phrase is spoken. Pictures, camera moves and sound effects all read the same times, so they
land on the word and stay there when the script changes.

**Every frame is a function of time.** HyperFrames seeks a paused timeline frame by frame. Each scene
builds one GSAP timeline whose tweens sit at moments from the voice. No clocks, no randomness, no state.
A snapshot, the preview and the render all show the same picture, which is what lets you look at any
moment and fix it.

**You look at what you made.** After every scene you take snapshots and read them like a viewer would.
Most of the quality comes from this loop, not from the first draft.

## What you need from the user

Three things. Ask once, in one message, for whatever is missing, then carry on.

1. **What the video is about**, with the source the facts come from (a document, a page, notes).
2. **The company brand**: name and website at least; a logo file and brand colours if they have them.
3. **An OpenRouter API key** (openrouter.ai). It pays for everything the film needs:

   | For | Model on OpenRouter |
   | --- | --- |
   | The voice | `elevenlabs/eleven-v4` |
   | The time of every word | `elevenlabs/scribe-v2` |
   | Illustrations | `google/gemini-nano-banana-2.1` |
   | Music | `google/lyria-3-pro-preview` |

   If the key is limited to certain models, these four must be allowed. The account needs at least $0.50
   of balance, or OpenRouter refuses voice and music.

Sensible defaults for the rest: the language of the request, 60 to 120 seconds, one narrator.

The key is the user's own and is billed to them. Put it in the project's `.env` and nowhere else. Never
echo a key, pass it as a command argument, write it in a file that gets committed, or repeat it in chat.
All calls go to OpenRouter. Do not call ElevenLabs or Google directly, and do not ask for their keys.

## Requirements

It runs on macOS, Windows and Linux. The machine needs four things: Node.js 22 or newer, Python 3.9 or
newer, `ffmpeg`, and the HyperFrames skills (`hyperframes` and `hyperframes-cli`). Many people who get
this skill have none of them yet. Check the machine first (step 0 below) and help the person install what
is missing; `references/setup.md` has the commands per system.

Commands in this skill are written with `python3`. On Windows the command is `python` (or `py -3`):
there, `python3` is often a stub that opens the Microsoft Store. Use the one that answers with a version.

## How this skill and `/hyperframes` divide the work

Load `/hyperframes` before you write any HTML. It owns the render contract (what a clip, a scene file and
a timeline must look like), the checks and the CLI. Commands are written here as `npx hyperframes ...`;
run them the way that skill says.

This skill owns everything else, and where the two differ, this one wins:

- **Story and plan.** Use the brief and the script from this skill. Skip the three storylines and
  `SPEC.md` that `/hyperframes` asks for on a new film: the script is the plan here.
- **Voice, music, pictures.** Generate them with `tools/` on the user's OpenRouter key. Do not use
  `/media-use`, HeyGen, `hyperframes tts` or the HyperFrames music catalogue for them, and do not sign the
  user in to anything. Sound effects are the twelve files that come with the project.
- **Timing.** Never write a number of seconds into `data-start`, `data-duration` or a tween position.
  Write `data-at`, `data-until` and `L(at("..."))`, and let `tools/sync.mjs` fill in the numbers.

## Workflow

Work in this order. Each step has a reason, and later steps depend on earlier ones being final.

### 0. Check the machine, once

Do this before you make a project or ask for the key. It needs nothing installed and costs nothing.

```sh
node --version        # v22 or newer
python3 --version     # Windows: python --version, or py -3 --version. 3.9 or newer
ffmpeg -version
```

Then look next to this skill's own folder for a folder named `hyperframes`: that is the HyperFrames
skill. If `/hyperframes` is in your list of skills, it is there.

When something is missing, guide the person through it. Assume they have never installed a program
from a command line:

1. Say in one message what is missing, what each thing is for in a few words, and that installing is
   free and takes a few minutes. Do not start the film, and do not spend anything on the key, yet.
2. **Node.js, Python, ffmpeg.** Ask once whether you may install them. With a yes, run the commands
   for their system from `references/setup.md` yourself and report what happened. Without a yes, give
   the commands for them to run. Never install software on someone's computer without that yes.
3. **The HyperFrames skills.** The person runs `npx hyperframes skills` themselves, after Node.js is
   there (in Claude Code they can type `! npx hyperframes skills`). HyperFrames asks that installing
   its skills stays the person's own step, so run it only when they ask you to.
4. **Start again.** A newly installed program is only found by a new terminal, and new skills only
   by a new session. Ask the person to close Claude Code, open it again and say what they wanted.
   Then run the checks again before going on.

If an install fails, show the message and the manual route from `references/setup.md`. Do not switch
to another renderer or leave a part out to get around it.

### 0b. Set up the project

```sh
python3 <this skill>/scripts/new_project.py ~/code/<name>-video "Display name"
cd ~/code/<name>-video               # then fill in .env
python3 tools/doctor.py
npx hyperframes check --json         # the template's demo film must pass
npx hyperframes snapshot --at 2,8,14,20
```

The template is a small working film with its own voice, picture and music. Seeing it pass and reading
its snapshots proves the machine works before you spend a cent. Read `index.html`, `timeline.js` and
`compositions/hook.html` once: they are the pattern you will follow.

### 1. Brief

Fill in `brief.md`: audience, the one message, what the viewer should do next, length, tone, sources. This
is the plan you check the film against. If the topic or the source is too thin to fill it in, ask.

### 2. Brand

Put the real colours and typefaces into the brand block at the top of `index.html`, and the logo into
`assets/img/`. Read `references/brand.md` first. Every colour and font in the film comes from that one
block, which is what makes the result look like the client.

### 3. Script

Write the narration into `script.json`, split into segments. Read `references/script.md` first: it covers
structure, pace, the bracketed direction tags Eleven v4 understands, and how segments and pauses work.
Next to each sentence, note the picture that goes with it in the shot list in `brief.md`. A sentence you
cannot picture is a sentence to rewrite.

Post the script in the chat before you generate the voice, then continue. Wait only if the user asked to
approve it. Everything later hangs on these words, and this is the cheapest moment to change them.

### 4. Voice

```sh
python3 tools/voices.py              # the voice names Eleven v4 offers
python3 tools/voice.py --dry         # characters that will be billed
python3 tools/voice.py               # generate; only new or changed segments; then syncs the HTML
python3 tools/times.py               # where every segment and chapter lands, and the film's length
```

`voice.py` makes each take and then has it transcribed, which is where the word times come from. It
prints every place where what was heard differs from what was written. A number read out as a word is
fine. A wrong or missing word is not: respell it in the script and regenerate that one segment
(`python3 tools/voice.py s3`). The voices have no language label, so judge the voice on its first take
in the film's language before generating the rest.

### 5. Pictures

Decide per scene: drawn in HTML, CSS and SVG, or generated as an illustration. Read
`references/images.md` first. Short version: vector for words, numbers, charts, simple icons and
diagrams. An illustration for anything that should look real or rich (people, places, bodies, objects),
moved with the camera.

```sh
python3 tools/image.py assets/img/kitchen.png "<style paragraph> <what is in the picture>"
python3 tools/image.py assets/img/kitchen-night.png "the same kitchen at night" --ref assets/img/kitchen.jpg
```

Open every generated image and look at it at full size before you use it.

### 6. Build the scenes

One scene at a time. Read `references/scenes.md` first: it explains the pattern with the template's
`compositions/` as the worked example, the building blocks in `index.html` and `lib/kit.js`, motion and
composition.

For each scene: add its start to `T` in `timeline.js`, add its host to `index.html` with `data-at` and
`data-until`, write `compositions/<id>.html`. Then:

```sh
node tools/sync.mjs                              # writes the times into the HTML
npx hyperframes check --json                     # fix every error, weigh every warning
npx hyperframes snapshot --at 12.4,13.0,14.2     # frames at the beats you just built
```

Read the contact sheet. Is the text readable, inside the frame, on the word? Is any frame empty? Fix the
biggest problem first, then snapshot again. Do not move on with a scene you have not looked at.

### 7. Sound

Read `references/sound.md`. Sound effects are `<audio>` tags in `index.html` that hang on the same word
times as the picture. The score is generated last, when the film's length is final:

```sh
python3 tools/music.py             # a new piece from tools/music.txt, cut to the film: assets/music/score.mp3
python3 tools/music.py --from 12   # the same piece, cut from 12 s in (costs nothing)
python3 tools/mix_music.py         # assets/music/bed.mp3: under the voice, up in the pauses
```

The music model decides its own length and build-up, so the score is one mood for the whole film and
cannot follow the chapters. Say that to the user if they expect music that turns with the story.

### 8. Final pass and render

1. `node tools/sync.mjs --check`, then `npx hyperframes check --json`: no errors.
2. `npx hyperframes snapshot --review` and read all three sheets (every scene, every cut, phone width),
   as `/hyperframes` describes in its `references/review.md`. Fix what you see.
3. Render: `npx hyperframes render --quality delivery -o exports/<name>.mp4`. The user asked for a video
   file, so render when your checks and review pass; you do not need to wait for an approval first.
4. `python3 tools/loudness.py exports/<name>.mp4`: aim for about -16 LUFS, peak at or below -1.5 dBFS.
5. `npx hyperframes transcribe exports/<name>.mp4 --json`: every line of the script must be there.
6. Tell the user where the file is, how long it is, what you verified, and what you did not (you measured
   the sound, you did not hear it). Offer `npx hyperframes preview --background` if they want to scrub or
   change the film themselves.

## Rules of craft

These are the lessons from earlier films. Each one exists because its opposite was tried and looked wrong.

- **Hang everything on a word.** A time typed as a number will drift the first time the voice changes. If
  you need a moment, find the phrase.
- **Video is watched, not read.** No paragraphs, no bullet slides. Text punctuates: a word, a number, a
  label. Let the voice explain.
- **Something always moves.** A frame that fades in, sits still and fades out reads as a slide. During a
  hold, keep a slow drift going. Overlap exits and entrances so the frame is never empty.
- **Choose every easing.** Never the default. Fast out for arrivals, fast in for exits, and things should
  be at their fastest at the cut. The curves are in `FILM.ease`; GSAP's own names work too.
- **Big type.** At 1080p: headlines 90 px and up, labels 56 and up, nothing under 34. Keep 100 px clear of
  the edges.
- **Real things are illustrations, not line drawings.** People, anatomy, rooms and objects drawn as SVG
  with thick strokes look amateurish. Generate them at 4K and move the camera, or keep them small and
  far away. Vector is for charts, scales, dots and simple icons.
- **Calm, dignified pictures.** No metaphors that show harm to a person, no ropes, chains or strings on
  bodies, nothing a viewer could find disturbing. A client rejected an opening like that outright. When
  in doubt, show the ordinary situation plainly.
- **Check generated pictures for nonsense.** Clocks with the wrong time, garbled lettering, extra
  fingers. Regenerate, or frame the camera so it is out of shot.
- **Only true things.** Every fact, number and quote comes from the user's source. Never invent a
  statistic, a person or a testimonial to make the story land.
- **One accent colour carries emphasis.** If everything is highlighted, nothing is.

## Pitfalls that cost hours

The full list is in `references/pitfalls.md`. Read it before your first build. The ones that bite first:

- The numbers in `data-start` and `data-duration` are written by `tools/sync.mjs`. After a new voice
  take, a changed pause or a new `data-at`, run it, or the picture runs on the old times.
- A scene file keeps its styles, markup and script inside `<template>`. Anything in its `<head>` is
  dropped without a warning.
- A scene's id is used four times and must be the same everywhere: the host's `data-composition-id`, the
  scene root's `data-composition-id`, the key in `window.__timelines` and the key in `T`.
- Tween positions inside a scene are on the scene's own clock. Wrap every film time in `L(...)`.
- Use `fromTo` for the first tween on a property and `to` for the next one on the same property.
- Do not put a CSS `transform` on an element GSAP moves. Position with an `.at` anchor and let GSAP move
  its child.
- Only the bundled fonts resolve by name. Any other family needs `python3 tools/font.py "Family"`.

## When something goes wrong

- A tool exits with OpenRouter's own error message and a hint. A 401 is the key. A 402 is the balance:
  voice and music need at least $0.50 on the account. A 404 that mentions a guardrail means the key may
  not use that model: `python3 tools/doctor.py` shows which of the four is missing. A 400 names the field
  that is wrong. Tell the user what to change at openrouter.ai; do not work around it with another service.
- No music comes back, or a 502 or 503: the music model is a preview and is sometimes unavailable. Run
  the same command again. If it stays down, the film works with its own music file in
  `assets/music/score.mp3` or without music.
- A phrase is "not found in the voice": the script and the audio differ. Run `python3 tools/times.py --words s2`
  to see the words as spoken, and match the phrase to them.
- A scene is blank, tiny or frozen: `npx hyperframes check --json` first; then the pitfalls above about
  `<template>` and ids.
- HyperFrames cannot run at all (no Node, no browser, no skills): go back to step 0 and help the
  person install what is missing. If it still cannot run, say so plainly. Do not fall back to another
  renderer without asking.
- On Windows something behaves oddly (a command is not found, letters with accents turn into other
  characters): read the Windows section of `references/pitfalls.md`.

## Reference files

| Read | When |
| --- | --- |
| `references/setup.md` | Something is missing in step 0, `doctor.py` fails, or a machine is new |
| `references/brand.md` | Before filling in the brand block |
| `references/script.md` | Before writing the narration |
| `references/images.md` | Before generating or choosing any picture |
| `references/scenes.md` | Before building the first scene |
| `references/sound.md` | Before adding effects and music |
| `references/pitfalls.md` | Before the first build, and when something behaves oddly |

For anything about HyperFrames itself (attributes, lint rules, motion blur, registry blocks, the preview),
the `/hyperframes` skill and `npx hyperframes docs <topic>` are the source. Trust them over memory.
