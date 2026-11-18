# Sound

Three layers: the voice (already done), sound effects on the beats, and a score underneath. Sound is half
of why a move feels like it lands.

## Sound effects

The template ships twelve short effects in `assets/sfx/`:

| File | Use it for |
| --- | --- |
| `pop.mp3` | Something appears: a card, a word, an icon |
| `pluck.mp3` | A step, a count, a selection |
| `tick.mp3` | A small confirmation, a clock, a list item |
| `whoosh.mp3` | A cut or a fast move. Start it about 0.25 s before the cut |
| `swell.mp3` | A build-up into a big change. Start it about 1.6 s before |
| `chime.mp3` | An answer, a notification, the logo |
| `sparkle.mp3` | Something good happens, a result |
| `stamp.mp3` | A verdict, a hard stop, a seal |
| `paper.mp3` | A document, a page, a form |
| `clink.mp3`, `coins.mp3` | Money, a token dropping, counting up |
| `drip.mp3` | A loss, a leak, something draining |

Place them in `film.tsx` with the same times the picture uses:

```tsx
<Sfx src="sfx/pop.mp3" at={HOOK.title} db={-13} />
<Sfx src="sfx/whoosh.mp3" at={T.picture - 0.25} db={-13} />
```

- Levels between -12 and -18 dB. Loud effects (`stamp`, `clink`) can go to -8 when they are the point.
- One effect per beat. If three things appear on three words, three plucks are right; five effects in one
  second are noise.
- Not every move needs a sound. Give them to the moments the viewer should notice.

Need one that is not there? `python3 tools/sfx.py zip "short fabric zipper closing, dry, close microphone" 1.0`
writes `assets/sfx/zip.mp3`. Describe the sound, its length and that it is dry and close.

## The score

Generate it last. Its sections have to line up with the film's chapters, and those only stop moving when
the voice is final.

`python3 tools/times.py` prints where each segment and chapter starts and the film's length. Turn that
into `tools/music_plan.json`: one section per part of the film, lengths in milliseconds adding up to the
film's length.

```json
{
  "positive_global_styles": ["instrumental cinematic film score", "felt piano", "warm strings", "hopeful", "modern"],
  "negative_global_styles": ["vocals", "singing", "harsh synths", "electric guitar"],
  "sections": [
    { "section_name": "Restless", "duration_ms": 24500,
      "positive_local_styles": ["sparse", "ticking pizzicato", "lonely low piano", "quiet tension"],
      "negative_local_styles": ["drums", "big"] },
    { "section_name": "The turn", "duration_ms": 47500,
      "positive_local_styles": ["starts with a deep warm swell", "hopeful piano theme", "gentle pulse"],
      "negative_local_styles": ["loud drums"] },
    { "section_name": "Finale", "duration_ms": 20000,
      "positive_local_styles": ["uplifting climax", "full strings", "warm brass"],
      "negative_local_styles": ["quiet"] },
    { "section_name": "Resolve", "duration_ms": 6000,
      "positive_local_styles": ["one soft chord ringing out", "peaceful ending"],
      "negative_local_styles": ["drums"] }
  ]
}
```

- Give the score the film's emotional shape: where it is tense, where it turns, where it lifts, how it
  ends. Name instruments and feelings, not genres alone.
- Always exclude vocals. A voice in the music fights the narrator.
- Put a section boundary on every big change of the film, and say how the new section starts ("starts
  with a swell") so the change is audible.
- End with a short section that resolves and rings out, as long as the `tail`.

```sh
python3 tools/music.py --check    # plan length against film length, nothing generated
python3 tools/music.py            # assets/music/score.mp3
python3 tools/mix_music.py        # assets/music/bed.mp3
```

For a short or simple film, one description is enough: `python3 tools/music.py --prompt "light, warm,
curious felt piano and soft strings, instrumental"`.

## The mix

`mix_music.py` brings the score to the level of the voice and then shapes it: 15 dB below the voice while
someone speaks, 6 dB below in pauses longer than 1.6 seconds, a fade in at the start and a fade out at the
end. The result, `bed.mp3`, plays at 0 dB in the film (`MUSIC = "music/bed.mp3"` in `film.tsx`).

The level is baked in on purpose. Generated scores grow louder from section to section, so one volume
number in the film is right at the start and too loud by the end.

Adjust by ear: `--under -18` if the music crowds the voice, `--under -12` if it disappears, `--open -4`
for more lift in the pauses, `--pause 1.0` to let it open in shorter gaps. If you changed the voice or the
gaps, run `mix_music.py` again: it reads the current timeline.

## Checking the sound

- `python3 tools/loudness.py exports/<name>.mp4`: about -16 LUFS, peak at or below -1.5 dBFS. A point or
  two either way is fine.
- `dapi transcribe exports/<name>.mp4`: if words are missing from the transcript, the music or an effect
  is covering the voice there.
- If you cannot listen, say so in your report and ask the user to check the balance of voice and music.
  That judgement needs ears.
