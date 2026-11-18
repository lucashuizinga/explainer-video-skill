# Script and voice

The script is the film. Every picture, move and sound is hung on its words, so time spent here is repaid
in every later step.

## Writing it

**Structure.** Most explainers that work follow this arc:

1. A hook the viewer recognises from their own life (a situation, a frustration, a question). Not a
   definition.
2. The one idea, said plainly.
3. How it works, in two to four steps. One mental model, introduced once and reused.
4. Why it matters for the viewer.
5. What to do next, and the brand.

**Pace.** Count on about 2.5 spoken words per second, pauses included. A 90 second film is roughly 200 to
230 words. Write short and let the pictures breathe; a script that fills every second leaves no room for
a camera move.

**Sentences.** Short. One idea each. Spoken language: "you", contractions, the words the audience uses.
Fragments are fine ("Tired. For months."). Read it aloud in your head; if you would not say it to someone
across a table, rewrite it.

**Write for pictures.** For every sentence, ask what is on screen while it is spoken, and note it in the
shot list in `brief.md`. Prefer sentences that name things you can show. One good metaphor that can be
drawn (a current account and a savings account for iron in the blood and iron in storage) carries a whole
film; five different metaphors confuse it.

**Truth.** Every fact, number, name and quote comes from the user's source. Do not invent a statistic, a
customer, a testimonial or a first-person experience to make the story stronger. If the source does not
say it, leave it out or ask. For medical, legal and financial topics, keep the source's own caveats.

**How it will be spoken.** Write numbers, abbreviations and web addresses the way they should sound
("voorbeeld punt en el", "one to two milligrams"). A name the voice gets wrong is fixed by respelling it
phonetically in the script.

## `script.json`

```json
{
  "language": "nl",
  "model": "eleven_v4",
  "voices": { "N": "<voice id>", "A": "<second voice id>" },
  "lead_in": 1.0,
  "tail": 4.5,
  "segments": [
    { "id": "s1", "voice": "N", "text": "[warm, unhurried] Je bent moe. Al maanden. ..." },
    { "id": "s2", "voice": "N", "gap": 1.5, "text": "[clear] IJzer is een klein metaal met een grote taak. ...",
      "chapters": [{ "at": "Je lichaam heeft ijzer", "gap": 0.9 }] },
    { "id": "s3", "voice": "A", "gap": 0.4, "text": "[friendly, calm] ..." }
  ]
}
```

- `language`: the ISO code sent to ElevenLabs, so the model knows which language the text is in.
- `voices`: short names for voice ids. Find ids with `python3 tools/voices.py <language>`. Premade voices
  exist on every account. Other voices exist only on the account that added them, so a script handed to
  someone else may need a different id; `tools/doctor.py` checks this.
- `lead_in`: seconds of picture before the first word. `tail`: seconds after the last word, for the logo.
- A **segment** is one generated take. Start a new segment when the speaker changes, when the tone
  changes, or at a natural break of the film. Segments are generated and regenerated on their own, so six
  segments of four sentences are easier to work with than one long take.
- `gap`: silence before the segment, in seconds.
- `chapters`: pauses inside a segment. `{ "at": "phrase", "gap": 0.9 }` cuts the take just before that
  phrase and inserts 0.9 seconds of silence. Use it where the picture needs time to change. The voice is
  not regenerated when you change a gap or a chapter: only the timeline moves.

## Directing Eleven v4

Eleven v4 takes direction as short English phrases in square brackets. They are not spoken and do not
appear in the word times.

- Open each segment with the delivery: `[warm, calm narrator, unhurried]`, `[clear, confident]`,
  `[matter-of-fact, a little weary]`.
- Change it mid-segment where the feeling turns: `... the result? [quieter] All normal.`
- Keep tags few and plain. One at the start, one or two inside.
- There is no SSML and no speed setting. Pace comes from the direction tag, from punctuation, and from
  `gap` and `chapters`.
- Punctuation is direction too. A full stop gives a beat. An ellipsis or a new sentence gives a longer one.

## Generating and checking

```sh
python3 tools/voice.py --dry      # what will be generated, and the character count
python3 tools/voice.py            # new and changed segments only
python3 tools/voice.py s4         # another take of one segment
python3 tools/times.py            # segment and chapter times, film length
python3 tools/times.py --words s4 # every word of a segment as it was spoken
```

`voice.py` levels every take to the same loudness (about -17 LUFS) with one fixed gain, so the word times
stay exact. The untouched takes are in `assets/vo/raw/`.

Check each take before you build on it:

- **Was everything said?** `dapi transcribe assets/vo/s2.mp3` and compare with the script.
- **Does it sound right?** Names, numbers, the brand. If you cannot listen yourself, ask the user to play
  the files in `assets/vo/`.
- **Is the take alive?** If a take is flat or rushed, change the direction tag and run that segment again.
  Each take is a new performance. To keep a good one stable, add `"seed": 12345` to the segment.

Changing a segment's text makes it regenerate on the next run, and every later time moves with it. That
is safe: shots look up phrases, not seconds. A shot that looked up a phrase you removed fails with
"Phrase not found", which tells you exactly what to update.
