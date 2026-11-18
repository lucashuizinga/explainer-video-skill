# Setup

Everything the film needs on a new machine, and how to help someone install it who has never done
that. Once a project exists, `python3 tools/doctor.py` (Windows: `python tools/doctor.py`) tells you
which of these is missing. Before that, use the checks in step 0 of `SKILL.md`.

## What to install, per system

| What | What it is for | Windows | macOS | Linux (Debian, Ubuntu) |
| --- | --- | --- | --- | --- |
| Node.js 22 or newer | runs HyperFrames, the renderer | `winget install OpenJS.NodeJS.LTS` | `brew install node` | the installer for your system from nodejs.org |
| Python 3.9 or newer | runs this skill's tools | `winget install Python.Python.3.12` | usually there as `python3`; else `brew install python` | `sudo apt install python3` |
| ffmpeg | sound levels, picture sizes, the final video | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| HyperFrames skills | the renderer's own instructions and launcher | `npx hyperframes skills` | the same | the same |

Order: Node.js first, because the HyperFrames skills are installed with it. The check for each one is
in step 0 of `SKILL.md`.

How to guide someone through it:

- **Ask before you install.** One question for the three programs is enough. With a yes, run the
  commands yourself, one at a time, and say after each whether it worked. When you run `winget`
  yourself, add `--accept-package-agreements --accept-source-agreements`, or it waits for an answer
  nobody can give.
- **The HyperFrames skills are the person's own step.** Give them the command, say that it adds the
  HyperFrames skills to their coding tools, and wait. In Claude Code they can type
  `! npx hyperframes skills` in the prompt. Run it yourself only when they ask you to. If the
  HyperFrames command cannot be reached, `npx skills add heygen-com/hyperframes --all` installs the
  same set.
- **Then a new start.** Windows and macOS only show a new program to terminals opened after the
  install, and new skills only load in a new session. Ask the person to close Claude Code and open it
  again, then run the checks again. If a program is still "not found" after that, it is not on the
  PATH: see below.
- **Plain words.** Say what to type and what they should see ("you will see a version number such as
  v24.1.0"). One step per message when the person is unsure.

When the short command is not available:

- **Windows without `winget`** (older Windows 10): install "App Installer" from the Microsoft Store,
  which brings `winget`. Or use the installers: nodejs.org (LTS), python.org (tick "Add python.exe to
  PATH" on the first screen), and for ffmpeg the "release full" build from gyan.dev, unpacked, with
  its `bin` folder added to the PATH.
- **macOS without Homebrew:** `brew` comes from brew.sh (one command, shown on that page). Node.js
  also has an installer on nodejs.org. The first use of `python3` may offer to install Apple's
  command line tools; say yes.
- **Windows: `python3` opens the Microsoft Store.** That is a stub, not Python. Use `python` or
  `py -3`. Wherever this skill writes `python3`, use the one that works.

The Windows commands above come from each program's own documentation. This skill was built and tested
on macOS; the tools were made safe for Windows (UTF-8 everywhere, the right Python name in every hint,
`npx` found as `npx.cmd`) and tested on macOS under a non-UTF-8 locale, but not run on a Windows
machine. If something fails there, read the message, fix the cause, and tell the user what you found.

## HyperFrames

HyperFrames is the renderer: it opens the project's HTML in a headless browser, seeks it frame by frame
and encodes the video. It runs on this machine and needs no account.

1. **Node.js 22 or newer.** `node --version`.
2. **The HyperFrames skills.** This skill builds on `hyperframes` and `hyperframes-cli`. If they are not
   installed, the person installs them once with `npx hyperframes skills`, then starts a new session
   (see above for how to guide them).
3. **The browser.** The first `check` or `render` downloads a headless Chrome into
   `~/.cache/hyperframes`. If it is missing or will not start: `npx hyperframes browser ensure`.

`npx hyperframes doctor` lists what the CLI itself needs. Lines about Docker, Kokoro or MusicGen can
fail: this skill does not use them.

Commands are written as `npx hyperframes ...` everywhere. Run them the way the `hyperframes` skill says
(through its launcher), from the project folder.

This skill was built and tested with HyperFrames CLI 0.9.64 and 0.9.65 on macOS. HyperFrames also
runs on Windows and Linux; neither was tested here.

## ffmpeg and Python

- `ffmpeg` and `ffprobe` come together in one install (table above). This skill's tools start them
  by name, so they must be on the PATH: `ffmpeg -version` has to answer in a new terminal. HyperFrames
  itself can also be pointed at them with `HYPERFRAMES_FFMPEG_PATH` and `HYPERFRAMES_FFPROBE_PATH`
  (on Windows the paths of `ffmpeg.exe` and `ffprobe.exe`), but that does not help the tools here.
- Python 3.9 or newer. The tools use only the standard library, so there is nothing to `pip install`.

## The OpenRouter key

One key, in `.env` in the project folder:

```
OPENROUTER_API_KEY=...
```

`.env` is in `.gitignore`. The tools read the key from the environment first, then from this file, and
never print it. The user makes the key at openrouter.ai under Keys.

Every media call goes to OpenRouter (`https://openrouter.ai/api/v1`) with this key:

| For | Model | Route |
| --- | --- | --- |
| The voice | `elevenlabs/eleven-v4` | `/audio/speech` |
| The time of every word | `elevenlabs/scribe-v2` | `/audio/transcriptions` |
| Illustrations | `google/gemini-nano-banana-2.1` | `/images` |
| Music | `google/lyria-3-pro-preview` | `/chat/completions`, streamed |

The model ids live in one place, the top of `tools/_common.py`.

Three things on the user's side decide whether it works. `doctor.py` checks all three:

- **Allowed models.** A key can be limited to certain models (a guardrail). Then all four above must be
  allowed. A missing one shows as a 404 that says "blocked by guardrail".
- **Balance.** OpenRouter refuses voice and music when the account holds less than $0.50, whatever the
  call itself costs. The error is a 402.
- **Spending limit and end date.** A key can carry a daily limit and an expiry date. `doctor.py` prints both.

If a model is not available, tell the user which one and where to allow it. Do not switch to another
model or another service without asking.

HyperFrames has its own sign-in (HeyGen) for hosted rendering and generated media. This skill does not
use it and never signs the user in.

## What it costs, roughly

Tell the user before you spend, in their own units:

- Voice: billed per character. `python3 tools/voice.py --dry` prints the count and `python3 tools/voices.py`
  the price. A two minute film is around 2,000 characters. The word times add a small amount per second
  of audio.
- Music: a fixed price per piece, whatever its length. Count on two or three pieces.
- Illustrations: billed per image, more for a larger size. `image.py` prints what each one cost. A film
  uses about five to ten.
- Rendering and checking are local and free.

On 17 November 2026 that was $0.08 per 1,000 characters of voice, $0.08 per piece of music and $0.12 per
4K illustration. Prices change: OpenRouter shows the current ones on each model's page, and every tool
prints what its call cost.

## A first run that proves the machine

```sh
python3 <skill>/scripts/new_project.py ~/code/test-video "Test"
cd ~/code/test-video
python3 tools/doctor.py              # Windows: python. Works without the key for the local checks; the key line will fail
npx hyperframes check --json         # no errors expected
npx hyperframes snapshot --at 2,8,14,20     # a title, three cards, a desk illustration, the close
npx hyperframes render --quality draft -o exports/test.mp4
```

The template carries its own voice, picture and music, so this costs nothing.
