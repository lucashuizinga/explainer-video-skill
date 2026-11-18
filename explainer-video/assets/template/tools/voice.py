# The voice-over: ElevenLabs Eleven v4 with character timestamps.
# Reads script.json. For each segment writes assets/vo/<id>.mp3 (levelled to -17 LUFS) and adds its
# word times to assets/vo/words.json. A segment is only generated when its text or voice changed.
#
#   python3 tools/voice.py            every new or changed segment
#   python3 tools/voice.py s2 s5      these segments again (a new take)
#   python3 tools/voice.py --dry      show what would be generated and how many characters it costs
#   python3 tools/voice.py --relevel  level the existing takes again (no API calls)
import base64, hashlib, json, os, subprocess, sys
from _common import key, script, path, http, loudness

TARGET_LUFS = -17.0
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dry = "--dry" in sys.argv

sc = script()
model = sc.get("model", "eleven_v4")
os.makedirs(path("assets", "vo", "raw"), exist_ok=True)
words_file, meta_file = path("assets", "vo", "words.json"), path("assets", "vo", "meta.json")
words = json.load(open(words_file)) if os.path.exists(words_file) else {}
meta = json.load(open(meta_file)) if os.path.exists(meta_file) else {}

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


if "--relevel" in sys.argv:  # level the takes that are already there again, without new API calls
    for sid in ids:
        raw = path("assets", "vo", "raw", sid + ".mp3")
        if os.path.exists(raw):
            print("%s  gain %+.1f dB" % (sid, level(raw, path("assets", "vo", sid + ".mp3"))))
    sys.exit(0)


def spoken_words(alignment):
    """Words with start and end times; [bracketed] direction tags are not spoken and are left out."""
    out, cur, start, end, tag = [], "", None, None, False
    for c, b, e in zip(alignment["characters"], alignment["character_start_times_seconds"], alignment["character_end_times_seconds"]):
        if c == "[":
            tag = True
            continue
        if tag:
            tag = c != "]"
            continue
        if c.isspace():
            if cur:
                out.append({"w": cur, "s": round(start, 3), "e": round(end, 3)})
                cur = ""
            continue
        if not cur:
            start = b
        cur += c
        end = e
    if cur:
        out.append({"w": cur, "s": round(start, 3), "e": round(end, 3)})
    return out


todo, chars = [], 0
for seg in sc["segments"]:
    voice_id = sc["voices"].get(seg["voice"])
    if not voice_id:
        sys.exit('Segment %s uses voice "%s", which is not in "voices".' % (seg["id"], seg["voice"]))
    sig = hashlib.sha1(json.dumps([seg["text"], voice_id, model, sc.get("language"), seg.get("seed")]).encode()).hexdigest()
    have = os.path.exists(path("assets", "vo", seg["id"] + ".mp3")) and seg["id"] in words
    if seg["id"] in args or (not args and (not have or meta.get(seg["id"]) != sig)):
        todo.append((seg, voice_id, sig))
        chars += len(seg["text"])

if not todo:
    print("Voice is up to date: nothing to generate.")
    sys.exit(0)
print("%d segment(s), %d characters: %s" % (len(todo), chars, " ".join(s["id"] for s, _, _ in todo)))
if dry:
    sys.exit(0)

k = key("ELEVENLABS_API_KEY")
for seg, voice_id, sig in todo:
    body = {"text": seg["text"], "model_id": model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    if sc.get("language"):
        body["language_code"] = sc["language"]
    if "seed" in seg:
        body["seed"] = seg["seed"]
    d = json.loads(http("https://api.elevenlabs.io/v1/text-to-speech/%s/with-timestamps?output_format=mp3_44100_192" % voice_id, {"xi-api-key": k}, body))
    raw = path("assets", "vo", "raw", seg["id"] + ".mp3")
    out = path("assets", "vo", seg["id"] + ".mp3")
    open(raw, "wb").write(base64.b64decode(d["audio_base64"]))
    w = spoken_words(d["alignment"])
    if not w:
        sys.exit("Segment %s came back without words." % seg["id"])
    gain = level(raw, out)
    words[seg["id"]] = w
    meta[seg["id"]] = sig
    json.dump(words, open(words_file, "w"), ensure_ascii=False)
    json.dump(meta, open(meta_file, "w"), indent=1)
    print("%s  %d words, %.2f s, gain %+.1f dB" % (seg["id"], len(w), w[-1]["e"], gain))

# drop segments that left the script
for sid in [s for s in list(words) if s not in ids]:
    del words[sid]
    meta.pop(sid, None)
json.dump(words, open(words_file, "w"), ensure_ascii=False)
json.dump(meta, open(meta_file, "w"), indent=1)
print("Done. See the new times with: python3 tools/times.py")
