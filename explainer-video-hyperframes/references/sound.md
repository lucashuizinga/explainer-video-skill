# Sound

Three layers: the voice (already done), sound effects on the beats, and a score underneath. Sound is half
of why a move feels like it lands.

The voice and the score come from this skill's tools, through OpenRouter on the user's key. The sound
effects are files that come with the project. Do not use the HyperFrames music catalogue or its text to
speech here.

The voice needs no work in the HTML: `tools/sync.mjs` writes one `<audio>` per spoken part between
`<!-- voice:start -->` and `<!-- voice:end -->` in `index.html`.

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

Place them in `index.html`, next to the others, with the same moments the picture uses:

```html
<audio id="sfx-title" class="clip" src="assets/sfx/pop.mp3" data-at="at('This is a template')" data-db="-13" data-track-index="12"></audio>
<audio id="sfx-cut-1" class="clip" src="assets/sfx/whoosh.mp3" data-at="T.picture - 0.25" data-db="-13" data-track-index="12"></audio>
```

Then `node tools/sync.mjs`, which writes the start, the length and the volume. Every `<audio>` needs its
own `id`, or HyperFrames leaves it out of the mix. `data-track-index` is only the lane in the editor: put
effects on 12, and on 13 when two overlap.

- Levels between -12 and -18 dB. Loud effects (`stamp`, `clink`) can go to -8 when they are the point.
- One effect per beat. If three things appear on three words, three plucks are right; five effects in one
  second are noise.
- Not every move needs a sound. Give them to the moments the viewer should notice.

These twelve are what there is: OpenRouter has no model that makes sound effects, so there is no tool to
generate a new one. If the film needs a sound that is not here, use the nearest of the twelve, or ask the
user for a file and put it in `assets/sfx/`. Only use a sound the user has the right to use.

## The score

Generate it last, when the voice is final and the film's length no longer moves.

The music comes from Lyria 3 Pro (`google/lyria-3-pro-preview`). Know what it can and cannot do before
you promise anything:

- **It decides its own length.** Asked for 23 seconds it returned 63; asked for 90 it returned 67 seconds
  of music. `music.py` therefore asks for a piece longer than the film and cuts the film's length out of it.
- **It does not follow timed sections.** Time blocks in the description were ignored in every test. The
  score is one mood for the whole film. It cannot turn where the story turns.
- **It cannot change a piece.** Every run is a new piece. A piece has a fixed price, whatever its length.
- **It is a preview model** and is sometimes unavailable. Run the command again.

Describe the music in `tools/music.txt`, in plain words:

```
A light, modern score for an explainer film. Felt piano and soft pizzicato strings. Warm and curious.
No harsh synths, no heavy drums. 96 BPM, C major. It sits quietly under a narrator, so keep the
arrangement sparse and leave room in the midrange.
```

- Name instruments, tempo, key and feeling, not a genre alone.
- Say that it plays under a narrator and should stay sparse. `music.py` itself adds that the piece is
  instrumental, how long it should be, and that the level should stay even.
- Do not name artists or existing songs. Google's documentation says such requests are blocked.

```sh
python3 tools/music.py              # a new piece, saved whole in assets/music/takes/, cut to assets/music/score.mp3
python3 tools/music.py --map        # how loud the last piece is, five seconds at a time
python3 tools/music.py --from 12    # cut the last piece again, starting 12 s into it (costs nothing)
python3 tools/mix_music.py          # assets/music/bed.mp3
```

In the tests a piece was about a minute long, so for a short film you can choose which part to use. The map shows
where the piece is quiet and where it is full. Pick a start where the level suits the opening of the
film, cut with `--from`, mix, and listen or ask the user to listen. For a film longer than the piece,
`music.py` says so: make a new piece, or ask for a longer one with `--prompt`.

The cut stops where the film stops, in the middle of the music; `mix_music.py` fades it out. A real
ending on the last chord only happens by luck.

## The mix

`mix_music.py` brings the score to the level of the voice and then shapes it: 15 dB below the voice while
someone speaks, 6 dB below in pauses longer than 1.6 seconds, a fade in at the start and a fade out at the
end. The result, `bed.mp3`, plays at full volume in the film: the `<audio id="music">` in `index.html`
points at it with `data-volume="1"`. The bed in a new project still belongs to the template's demo film;
`mix_music.py` replaces it. Until then the demo music plays under your film, which is harmless while you
build.

The level is baked in on purpose. Generated pieces come back loud, with peaks above full scale, and their
level wanders, so one volume number in the film does not hold.

Adjust by ear: `--under -18` if the music crowds the voice, `--under -12` if it disappears, `--open -4`
for more lift in the pauses, `--pause 1.0` to let it open in shorter gaps. If you changed the voice or the
gaps, run `mix_music.py` again: it reads the current timeline.

## Checking the sound

- `python3 tools/loudness.py exports/<name>.mp4`: about -16 LUFS, peak at or below -1.5 dBFS. A point or
  two either way is fine.
- `npx hyperframes transcribe exports/<name>.mp4 --json`: if words are missing from the transcript, the
  music or an effect is covering the voice there.
- `npx hyperframes audio exports/<name>.mp4 --json` shows where the sound hits and how loud it is.
- If you cannot listen, say so in your report and ask the user to check the balance of voice and music.
  That judgement needs ears.
