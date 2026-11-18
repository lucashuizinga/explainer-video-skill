# The score, with Lyria 3 Pro (Google) through OpenRouter. Writes assets/music/score.mp3, cut to the film's length.
#
#   python3 tools/music.py                 a new piece from the description in tools/music.txt
#   python3 tools/music.py --prompt "..."  a new piece from this description
#   python3 tools/music.py --from 12       no new piece: cut the last one again, starting 12 s into it
#   python3 tools/music.py --map           no new piece: show how loud the last one is, five seconds at a time
#
# Lyria decides the length and the build-up itself: asking for 23 seconds gave 63, and timed sections in
# the description were not followed. So the tool asks for a piece longer than the film, saves it whole in
# assets/music/takes/, and cuts the film's length out of it. A piece costs a fixed price, whatever its length.
# Generate the score after the voice is final. Then run tools/mix_music.py to lower it under the voice.
import base64, json, os, re, sys, time
from _common import openrouter, path, timeline, duration, run, read_text, PY, MUSIC_MODEL

voices, END = timeline()
a = sys.argv[1:]
opt = lambda name: a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None
takes = path("assets", "music", "takes")
out = path("assets", "music", "score.mp3")
os.makedirs(takes, exist_ok=True)


def last_take():
    files = sorted(f for f in os.listdir(takes) if f.endswith(".mp3"))
    if not files:
        sys.exit("No piece yet. Run: %s tools/music.py" % PY)
    return os.path.join(takes, files[-1])


def music_span(file):
    """(start, end) of the music in a take: without silence at the ends, and stopping at the first long silence inside."""
    total = duration(file) or 0.0
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", file, "-af", "silencedetect=noise=-45dB:d=0.5", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", r.stderr)]
    begin, end = 0.0, total
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else total
        if s <= 0.05:
            begin = e                      # silence before the first note
        elif e - s >= 2.0 or e >= total - 0.05:
            end = s                        # the piece stops here; what follows a long silence is not used
            break
    return begin, end, total


def level_map(file):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", file, "-af",
             "asetnsamples=n=220500,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"])
    vals = re.findall(r"RMS_level=(-?[\d.]+|-inf)", r.stdout)
    print("Level per 5 s (dB, higher is louder):")
    print("  " + "  ".join("%d:%s" % (i * 5, "quiet" if v == "-inf" or float(v) < -60 else "%d" % round(float(v))) for i, v in enumerate(vals)))


def cut(file, start):
    begin, end, total = music_span(file)
    start = max(begin, start)
    have = end - start
    print("%s: %.1f s, music from %.1f to %.1f s. Film: %.1f s." % (os.path.basename(file), total, begin, end, END))
    level_map(file)
    if have < END - 1.0:
        sys.exit("From %.1f s there is only %.1f s of music, and the film is %.1f s. Start earlier (--from) or make a new piece." % (start, have, END))
    r = run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % start, "-i", file, "-t", "%.3f" % (END + 0.5), "-c:a", "libmp3lame", "-b:a", "192k", out])
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + r.stderr[-600:])
    print("%s  %.1f s, cut from %.1f s of the piece. The cut ends where the film ends; mix_music.py fades it out." % (out, duration(out) or 0, start))
    print("Next: %s tools/mix_music.py, then listen. A start further in often suits better: %s tools/music.py --from <seconds>" % (PY, PY))


if "--map" in a:
    f = last_take()
    print("%s: music from %.1f to %.1f s of %.1f s. Film: %.1f s." % ((os.path.basename(f),) + music_span(f) + (END,)))
    level_map(f)
    sys.exit(0)
if "--from" in a:
    cut(last_take(), float(opt("--from") or 0))
    sys.exit(0)

text = opt("--prompt")
if not text:
    f = path("tools", "music.txt")
    if not os.path.exists(f):
        sys.exit('No tools/music.txt. Write the description there (see the skill\'s references/sound.md) or use --prompt "...".')
    text = " ".join(l.strip() for l in read_text(f).splitlines() if l.strip() and not l.startswith("#"))
want = int(max(60, round((END + 20) / 10.0) * 10))
prompt = ("Instrumental only, no vocals, no singing, no spoken words.\n\n%s\n\n"
          "Create a %d-second piece. Keep the level even from start to finish, with no silent gaps, and end on a resolved chord." % (text, want))

body = {"model": MUSIC_MODEL, "messages": [{"role": "user", "content": prompt}], "modalities": ["text", "audio"],
        "audio": {"format": "mp3"}, "stream": True}
r = openrouter("/chat/completions", body, timeout=900, stream=True)
chunks, cost, err = [], None, None
for raw in r:
    line = raw.decode("utf-8", "replace").strip()
    if not line.startswith("data: ") or line == "data: [DONE]":
        continue
    try:
        ev = json.loads(line[6:])
    except ValueError:
        continue
    err = ev.get("error") or err
    cost = (ev.get("usage") or {}).get("cost", cost)
    for ch in ev.get("choices") or []:
        d = (ch.get("delta") or ch.get("message") or {}).get("audio") or {}
        if d.get("data"):
            chunks.append(d["data"])
if not chunks:
    sys.exit("No music came back (%s). The model is a preview and is not always available: run the same command again."
             % (json.dumps(err)[:300] if err else "no audio in the answer"))
take = os.path.join(takes, time.strftime("%Y%m%d-%H%M%S") + ".mp3")
open(take, "wb").write(b"".join(base64.b64decode(c) for c in chunks))
print("New piece: %s%s" % (take, "  ($%.2f)" % cost if cost is not None else ""))
cut(take, 0.0)
