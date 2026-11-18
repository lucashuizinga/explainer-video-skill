---
name: explainer-video
description: >-
  Make a narrated, animated explainer video (uitlegvideo, story animation,
  explainer animatie) in a company's brand with Diffusion Studio: an ElevenLabs
  Eleven v4 voice-over with word timings, illustrations from Google's Gemini
  image model on the user's own key, music and sound effects, and every move
  timed to a spoken word. Use this whenever someone asks for an explainer
  video, uitlegvideo, animated explanation, story animation, or "a video that
  explains X" for a brand or product, also when they only give a topic and a
  company name. Not for cutting recorded footage such as talking heads,
  podcasts or screen recordings.
---

# Explainer video

You make a narrated animation of one to three minutes, 1920x1080, in the client's brand. The result is an
mp4 plus a project folder that anyone can open and change.

## The idea that makes these videos good

**The voice is the clock.** The voice-over is generated first, with the start and end time of every word.
Nothing in the film has a hand-typed time. A shot asks `at("a phrase from the script")` and gets the moment
that phrase is spoken. Pictures, camera moves and sound effects all read the same times, so they land on
the word and stay there when the script changes.

**Every frame is a function of time.** A shot is a function that returns an SVG drawing for a given second.
No keyframe timeline, no state. Scrubbing, checking a frame and exporting all give the same picture, which
is what lets you look at any moment and fix it.

**You look at what you made.** After every chapter you render frames and read them like a viewer would.
Most of the quality comes from this loop, not from the first draft.

## What you need from the user

Four things. Ask once, in one message, for whatever is missing, then carry on.

1. **What the video is about**, with the source the facts come from (a document, a page, notes).
2. **The company brand**: name and website at least; a logo file and brand colours if they have them.
3. **An ElevenLabs API key** (voice, music, sound effects).
4. **A Gemini API key** (illustrations).

Sensible defaults for the rest: the language of the request, 60 to 120 seconds, one narrator.

Keys are the user's own and are billed to them. Put them in the project's `.env` and nowhere else. Never
echo a key, pass it as a command argument, write it in a file that gets committed, or repeat it in chat.

## Requirements

macOS with Diffusion Studio and its `dapi` command, `ffmpeg`, and Python 3.9 or newer. `tools/doctor.py`
checks all of it and both keys without spending anything. If it fails, read `references/setup.md`.

Do not use `dapi generate`. It bills Diffusion Studio credits on whoever is signed in to the app. This
skill generates through `tools/`, on the user's own keys. Diffusion Studio is only the renderer here:
`open`, `check`, `capture`, `export`, `logs`, `transcribe`.

## Workflow

Work in this order. Each step has a reason, and later steps depend on earlier ones being final.

### 0. Set up

```sh
python3 <this skill>/scripts/new_project.py ~/code/<name>-video "Display name"
cd ~/code/<name>-video        # then fill in .env
python3 tools/doctor.py
dapi open -b "$PWD"           # -b keeps the app in the background
dapi context                  # confirm projectDir is this folder
dapi capture film -t 2 8 14   # the template's demo film should render
```

The template is a small working film. Seeing it render proves the machine works before you spend a cent.
`dapi check`, `capture` and `export` act on whichever project the app has open, so run `dapi open -b` on
your folder first and confirm with `dapi context`, every session.

### 1. Brief

Fill in `brief.md`: audience, the one message, what the viewer should do next, length, tone, sources. This
is the plan you check the film against. If the topic or the source is too thin to fill it in, ask.

### 2. Brand

Put the real colours, typefaces and logo into `lib/brand.ts`. Read `references/brand.md` first. Every
colour and font in the film comes from that one file, which is what makes the result look like the client.

### 3. Script

Write the narration into `script.json`, split into segments. Read `references/script.md` first: it covers
structure, pace, the bracketed direction tags Eleven v4 understands, and how segments and pauses work.
Next to each sentence, note the picture that goes with it in the shot list in `brief.md`. A sentence you
cannot picture is a sentence to rewrite.

Post the script in the chat before you generate the voice, then continue. Wait only if the user asked to
approve it. Everything later hangs on these words, and this is the cheapest moment to change them.

### 4. Voice

```sh
python3 tools/voices.py nl           # voices this key can use, by language
python3 tools/voice.py --dry         # characters that will be billed
python3 tools/voice.py               # generate; only new or changed segments
python3 tools/times.py               # where every segment and chapter lands, and the film's length
```

Listen for mistakes before building on it: `dapi transcribe assets/vo/s1.mp3` shows what was actually
said. A mispronounced name is fixed by respelling it in the script and regenerating that one segment
(`python3 tools/voice.py s3`).

### 5. Pictures

Decide per chapter: drawn in vector, or generated as an illustration. Read `references/images.md` first.
Short version: vector for words, numbers, charts, simple icons and diagrams. An illustration for anything
that should look real or rich (people, places, bodies, objects), moved with the camera.

```sh
python3 tools/image.py assets/img/kitchen.png "<style paragraph> <what is in the picture>"
python3 tools/image.py assets/img/kitchen-night.png "the same kitchen at night" --ref assets/img/kitchen.jpg
```

Open every generated image and look at it at full size before you use it.

### 6. Build the shots

One chapter at a time. Read `references/shots.md` first: it explains the pattern with the template's
`scenes/demo.ts` as the worked example, the building blocks in `lib/`, motion and composition.

After each chapter:

```sh
python3 tools/logs.py                       # compile errors show up here, not in the terminal
dapi check film                             # empty spans, assets that do not load
dapi capture film -t 12.4 13.0 14.2 15.8    # frames at the beats you just built
```

Read the contact sheet. Is the text readable, inside the frame, on the word? Is any frame empty? Fix the
biggest problem first, then capture again. Do not move on with a chapter you have not looked at.

### 7. Sound

Read `references/sound.md`. Sound effects hang on the same word times as the picture. The score is
generated last, when the film's length is final:

```sh
python3 tools/music.py --check     # does tools/music_plan.json match the film's length?
python3 tools/music.py             # assets/music/score.mp3
python3 tools/mix_music.py         # assets/music/bed.mp3: under the voice, up in the pauses
```

Then set `MUSIC = "music/bed.mp3"` in `film.tsx`.

### 8. Final pass and export

1. Capture the whole film: a frame every two seconds, plus the frames just before and after every cut.
2. Fix what you see. Then `dapi check film` must report no errors.
3. Export: `dapi export film "$PWD/exports/<name>.mp4"`.
4. `python3 tools/loudness.py exports/<name>.mp4`: aim for about -16 LUFS, peak at or below -1.5 dBFS.
5. `dapi transcribe exports/<name>.mp4`: every line of the script must be there.
6. Tell the user where the file is, how long it is, what you verified, and what you did not.

## Rules of craft

These are the lessons from earlier films. Each one exists because its opposite was tried and looked wrong.

- **Hang everything on a word.** A time typed as a number will drift the first time the voice changes. If
  you need a moment, find the phrase.
- **Video is watched, not read.** No paragraphs, no bullet slides. Text punctuates: a word, a number, a
  label. Let the voice explain.
- **Something always moves.** A frame that fades in, sits still and fades out reads as a slide. During a
  hold, keep a slow drift going. Overlap exits and entrances so the frame is never empty.
- **Choose every easing.** Never linear. Fast out for arrivals, fast in for exits, and things should be at
  their fastest at the cut. The curves are in `lib/motion.ts`.
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

- One `<scene>` per project. Two make `dapi capture` fail a few seconds in.
- JSX files (`.tsx`) must be inside the project folder. Plain `.ts` may live anywhere.
- Import types with `import type { Cam }`. A plain import of a type is a compile error.
- In an `<html>` shot, `clipPath` is dropped. A shot that slides away must take its background with it
  (`svgDoc(..., bg, dx, dy)`), or it blanks the shot underneath.
- `dapi check`, `capture` and `export` use the project the app has open, not the folder you are in.
- A compile error does not show in the terminal. Run `python3 tools/logs.py` after every save.
- Copying a project copies its `projectId`. Use `scripts/new_project.py`, which removes it.

## When something goes wrong

- A tool exits with the API's own error message. Read it: a 401 is the key, a 402 or quota message is
  the user's credit, a 400 names the field that is wrong.
- A phrase is "not found in the voice": the script and the audio differ. Run `python3 tools/times.py --words s2`
  to see the words as spoken, and match the phrase to them.
- The film is black or a shot is missing: `python3 tools/logs.py`, then `dapi check film`.
- You cannot reach Diffusion Studio at all: say so plainly. Do not fall back to another renderer without
  asking; the look depends on this one.

## Reference files

| Read | When |
| --- | --- |
| `references/setup.md` | `doctor.py` fails, or a machine is new |
| `references/brand.md` | Before filling in `lib/brand.ts` |
| `references/script.md` | Before writing the narration |
| `references/images.md` | Before generating or choosing any picture |
| `references/shots.md` | Before building the first shot |
| `references/sound.md` | Before adding effects and music |
| `references/pitfalls.md` | Before the first build, and when something behaves oddly |

The app ships its own reference for every tag and command at
`/Applications/Diffusion Studio.app/Contents/Resources/docs` (`reference/jsx`, `reference/tools`). Trust it
over memory for tag attributes.
