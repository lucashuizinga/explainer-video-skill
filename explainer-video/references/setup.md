# Setup

Everything the film needs on a new machine. `python3 tools/doctor.py` in the project tells you which of
these is missing.

## Diffusion Studio and dapi

Diffusion Studio is the renderer. The `dapi` command ships inside the app.

Check in this order:

1. Is the app there? `ls "/Applications/Diffusion Studio.app"`
2. If yes but `dapi` is not found, link it. Either the app menu **Diffusion Studio > Install dapi Command
   Line Tool**, or:
   ```sh
   sudo ln -sf "/Applications/Diffusion Studio.app/Contents/Resources/cli/bin/dapi" /usr/local/bin/dapi
   ```
   `sudo` needs the user's password, so ask them to run it.
3. If the app is not installed: `brew install --cask diffusionstudio/tap/editor` (macOS 11 or newer, Apple
   silicon). This installs the app and links `dapi`.

Then `dapi --help` should list commands and `dapi open -b <project folder>` should start the app in the
background.

Rendering, checking and exporting run on this machine. `dapi generate` runs on Diffusion Studio's own
service and spends the credits of whoever is signed in to the app; this skill does not use it.
`dapi transcribe`, used here to check the voice, may also need a signed-in app. If it is not available,
ask the user to listen to the files instead.

This skill was built and tested with dapi 0.211.0.

## ffmpeg and Python

- `ffmpeg` and `ffprobe`: `brew install ffmpeg`.
- Python 3.9 or newer. The tools use only the standard library, so there is nothing to `pip install`.

## The two keys

Both go in `.env` in the project folder:

```
ELEVENLABS_API_KEY=...
GEMINI_API_KEY=...
```

`.env` is in `.gitignore`. The tools read the keys from the environment first, then from this file, and
never print them.

**ElevenLabs** (elevenlabs.io, under API keys). The key needs access to text to speech, voices (read),
music and sound effects. The voice model is Eleven v4 (`eleven_v4`), set in `script.json`. If the account
has no access to v4, the API says so in its error; tell the user, do not silently switch models.

**Gemini** (aistudio.google.com, under API keys). The image model is `gemini-3-pro-image`, also known as
Nano Banana Pro. It needs a project with billing enabled. `doctor.py` checks that the model is listed for
the key and names the image models that are, in case this one is not.

## What it costs, roughly

Tell the user before you spend, in their own units:

- Voice: billed per character. `python3 tools/voice.py --dry` prints the count. A two minute film is
  around 2,000 characters.
- Music: billed by length. One score as long as the film, sometimes a second take.
- Illustrations: billed per image. A film uses about five to ten.

Prices change. Do not quote amounts from memory; point the user to the pricing pages of ElevenLabs and
Google, or look them up.

## A first run that proves the machine

```sh
python3 <skill>/scripts/new_project.py ~/code/test-video "Test"
cd ~/code/test-video
python3 tools/doctor.py            # works without keys for the local checks; the key lines will fail
dapi open -b "$PWD"
dapi check film                    # no errors expected
dapi capture film -t 2 8 14 20     # a title, three cards, a desk illustration, the close
```

The template carries its own voice, picture and music, so this costs nothing.
