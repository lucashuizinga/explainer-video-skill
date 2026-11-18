# The voice-over, through OpenRouter: Eleven v4 speaks the text, Scribe v2 then listens to the take and
# gives the time of every word. Reads script.json. For each segment writes assets/vo/<id>.mp3 (levelled to
# -17 LUFS) and adds its word times to assets/vo/words.json. A segment is only generated when its text or
# voice changed. Afterwards it runs tools/sync.mjs, which writes the new times into the HTML.
#
#   python3 tools/voice.py            every new or changed segment
#   python3 tools/voice.py s2 s5      these segments again (a new take)
#   python3 tools/voice.py --dry      show what would be generated and how many characters it costs
#   python3 tools/voice.py --relevel  level the existing takes again (no API calls)
#   python3 tools/voice.py --retime   listen to the existing takes again for their word times (no new voice)
#
# The words in words.json are the words of the script, in the script's spelling. Scribe hears "thirty" where
# the script says "30"; the tool lines the two up and prints every place where they differ, so you can
# check that the voice said what was written.
import base64, difflib, hashlib, json, os, re, subprocess, sys
from _common import script, path, openrouter, loudness, norm, read_json, write_json, PY, VOICE_MODEL, WORDS_MODEL

TARGET_LUFS = -17.0
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dry = "--dry" in sys.argv

sc = script()
model = sc.get("model") or VOICE_MODEL
os.makedirs(path("assets", "vo", "raw"), exist_ok=True)
words_file, meta_file = path("assets", "vo", "words.json"), path("assets", "vo", "meta.json")
words = read_json(words_file) if os.path.exists(words_file) else {}
meta = read_json(meta_file) if os.path.exists(meta_file) else {}

ids = [s["id"] for s in sc["segments"]]
if len(set(ids)) != len(ids):
    sys.exit("Segment ids in script.json must be unique.")
for a in args:
    if a not in ids:
        sys.exit('No segment "%s" in script.json.' % a)


def level(raw, out):
    """One fixed gain per segment plus a limiter: every voice sits at the same level, the word times stay exact."""
    lufs, _ = loudness(raw)
    gain = 0.0 if lufs is None else max(-12.0, min(12.0, TARGET_LUFS - lufs))
    af = "volume=%.2fdB,alimiter=limit=0.84:attack=5:release=60:level=disabled" % gain
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-c:a", "libmp3lame", "-b:a", "192k", out])
    if r.returncode != 0:
        sys.exit("ffmpeg failed on %s" % raw)
    return gain


def script_words(text):
    """The words of a segment as written; [bracketed] direction tags are not spoken and are left out."""
    return [w for w in re.sub(r"\[[^\]]*\]", " ", text).split() if norm(w)]


def heard_words(raw):
    """What Scribe hears in a take: [{"w", "s", "e"}] in seconds."""
    body = {"model": WORDS_MODEL, "response_format": "verbose_json", "timestamp_granularities": ["word"],
            "input_audio": {"data": base64.b64encode(open(raw, "rb").read()).decode(), "format": "mp3"}}
    if sc.get("language"):
        body["language"] = sc["language"]
    d = json.loads(openrouter("/audio/transcriptions", body))
    out = []
    for w in d.get("words") or []:
        t = (w.get("word") or w.get("text") or "").strip()
        if t and norm(t) and w.get("start") is not None and w.get("end") is not None:
            out.append({"w": t, "s": float(w["start"]), "e": float(w["end"])})
    if not out:
        sys.exit("Scribe returned no word times for %s (text heard: %r). Run the same command again." % (raw, (d.get("text") or "")[:120]))
    return out


def line_up(written, heard, sid):
    """Give every written word a start and an end from the heard words. Returns (words, notes, share that matched)."""
    a, b = [norm(w) for w in written], [norm(h["w"]) for h in heard]
    res, notes, same = [None] * len(written), [], 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                res[i1 + k] = (heard[j1 + k]["s"], heard[j1 + k]["e"])
            same += i2 - i1
        elif tag == "replace":
            # the same stretch of sound, written differently ("30" and "thirty"): share its time by word length
            t0, t1 = heard[j1]["s"], heard[j2 - 1]["e"]
            if i2 - i1 == j2 - j1:
                for k in range(i2 - i1):
                    res[i1 + k] = (heard[j1 + k]["s"], heard[j1 + k]["e"])
            else:
                total = float(sum(max(1, len(x)) for x in a[i1:i2]))
                at = t0
                for k in range(i1, i2):
                    d = (t1 - t0) * max(1, len(a[k])) / total
                    res[k] = (at, at + d)
                    at += d
            notes.append('written "%s", heard "%s" at %.2f s' % (" ".join(written[i1:i2]), " ".join(h["w"] for h in heard[j1:j2]), t0))
        elif tag == "delete":
            notes.append('written "%s" was not heard' % " ".join(written[i1:i2]))
        elif tag == "insert":
            notes.append('heard "%s" at %.2f s, which is not in the script' % (" ".join(h["w"] for h in heard[j1:j2]), heard[j1]["s"]))
    # words that were not heard: place them evenly between their neighbours
    i = 0
    while i < len(res):
        if res[i] is not None:
            i += 1
            continue
        j = i
        while j < len(res) and res[j] is None:
            j += 1
        left = res[i - 1][1] if i > 0 else 0.0
        right = res[j][0] if j < len(res) else heard[-1]["e"]
        step = (right - left) / (j - i)
        for k in range(i, j):
            res[k] = (left + step * (k - i), left + step * (k - i + 1))
        i = j
    out = [{"w": w, "s": round(s, 3), "e": round(max(e, s + 0.02), 3)} for w, (s, e) in zip(written, res)]
    return out, notes, same / float(max(1, len(written)))


def time_take(seg):
    raw = path("assets", "vo", "raw", seg["id"] + ".mp3")
    written = script_words(seg["text"])
    if not written:
        sys.exit("Segment %s has no spoken words." % seg["id"])
    w, notes, share = line_up(written, heard_words(raw), seg["id"])
    for n in notes:
        print("      %s" % n)
    if share < 0.8:
        print("      WARNING: only %d%% of the words of %s were heard as written. Listen to assets/vo/%s.mp3; "
              "make a new take with: %s tools/voice.py %s" % (round(share * 100), seg["id"], seg["id"], PY, seg["id"]))
    return w


def save():
    write_json(words_file, words)
    write_json(meta_file, meta, indent=1)


def sync():
    r = subprocess.run(["node", path("tools", "sync.mjs")])
    if r.returncode != 0:
        sys.exit("The voice is saved, but writing its times into the HTML failed. Fix the message above, then run: node tools/sync.mjs")
    print("Done. See the new times with: %s tools/times.py" % PY)


if "--relevel" in sys.argv:  # level the takes that are already there again, without new API calls
    for sid in ids:
        raw = path("assets", "vo", "raw", sid + ".mp3")
        if os.path.exists(raw):
            print("%s  gain %+.1f dB" % (sid, level(raw, path("assets", "vo", sid + ".mp3"))))
    sys.exit(0)

if "--retime" in sys.argv:  # the same takes, word times again
    for seg in sc["segments"]:
        if (args and seg["id"] not in args) or not os.path.exists(path("assets", "vo", "raw", seg["id"] + ".mp3")):
            continue
        words[seg["id"]] = time_take(seg)
        print("%s  %d words, %.2f s" % (seg["id"], len(words[seg["id"]]), words[seg["id"]][-1]["e"]))
        save()
    sync()
    sys.exit(0)

todo, chars = [], 0
for seg in sc["segments"]:
    voice = (sc.get("voices") or {}).get(seg["voice"])
    if not voice:
        sys.exit('Segment %s uses voice "%s", which is not in "voices".' % (seg["id"], seg["voice"]))
    sig = hashlib.sha1(json.dumps([seg["text"], voice, model, sc.get("language"), seg.get("seed")]).encode()).hexdigest()
    have = os.path.exists(path("assets", "vo", seg["id"] + ".mp3")) and seg["id"] in words
    if seg["id"] in args or (not args and (not have or meta.get(seg["id"]) != sig)):
        todo.append((seg, voice, sig))
        chars += len(seg["text"])

if not todo:
    print("Voice is up to date: nothing to generate.")
    sys.exit(0)
print("%d segment(s), %d characters: %s" % (len(todo), chars, " ".join(s["id"] for s, _, _ in todo)))
if dry:
    sys.exit(0)

for seg, voice, sig in todo:
    body = {"model": model, "input": seg["text"], "voice": voice, "response_format": "mp3"}
    audio = openrouter("/audio/speech", body)
    raw = path("assets", "vo", "raw", seg["id"] + ".mp3")
    out = path("assets", "vo", seg["id"] + ".mp3")
    open(raw, "wb").write(audio)
    w = time_take(seg)
    gain = level(raw, out)
    words[seg["id"]] = w
    meta[seg["id"]] = sig
    save()
    print("%s  %d words, %.2f s, gain %+.1f dB" % (seg["id"], len(w), w[-1]["e"], gain))

# drop segments that left the script
for sid in [s for s in list(words) if s not in ids]:
    del words[sid]
    meta.pop(sid, None)
save()
# the film reads its times from the HTML, so write the new ones straight away
sync()
