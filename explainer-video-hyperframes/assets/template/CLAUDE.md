# Explainer video project (HyperFrames)

This folder is a narrated explainer video made with the `explainer-video-hyperframes` skill, rendered
with HyperFrames. Load that skill before changing anything, and `/hyperframes` for the render contract
and the CLI.

## How it fits together

| File | What it is |
| --- | --- |
| `script.json` | The narration, voices and pauses. The source of all timing. |
| `assets/vo/` | The voice per segment and `words.json`, the time of every spoken word. |
| `timeline.js` | Where each scene starts (`T`), as moments from the voice. |
| `index.html` | The brand (colours, fonts), the scene hosts and all sound. |
| `compositions/*.html` | One scene per file. Its tweens are placed with `at("a phrase")`. |
| `lib/clock.js`, `lib/kit.js` | The voice clock and a few GSAP helpers. |
| `tools/` | Voice, pictures, music and checks, all through OpenRouter. The key comes from `.env`. |

## The rules that keep it working

- **Never type a time.** In HTML write `data-at="..."` and `data-until="..."`; in a scene script use
  `L(at("a phrase"))`. `data-start` and `data-duration` are written by `node tools/sync.mjs`.
- **After any change to `script.json`, the voice, `timeline.js` or a `data-at`:** `node tools/sync.mjs`.
  `python3 tools/voice.py` runs it for you. (On Windows the command is `python`, or `py -3`.)
- **After every edit:** `npx hyperframes check --json`, then `npx hyperframes snapshot --at <seconds>` and
  look at the frames.
- The OpenRouter key stays in `.env`. Never print it. Media calls go to OpenRouter only.
