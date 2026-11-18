# Shared helpers for the tools: keys, HTTP, ffmpeg and the timeline arithmetic.
# Standard library only, Python 3.9+.
import json, os, re, shutil, subprocess, sys, unicodedata, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Windows does not use UTF-8 for its console, its pipes or its text files unless told to. Without the lines
# below a word like "één" is written to disk in another encoding than Node reads it in, and a message with
# an accent or an arrow stops the tool. So: every text file goes through read_text and write_text, and the
# output is UTF-8 everywhere.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# How Python is started on this machine, for the commands the tools print. On Windows "python3" is often
# a stub that opens the Store; "python" (or "py -3") is the real one.
PY = "python" if os.name == "nt" else "python3"


def read_text(file):
    """A text file as UTF-8. A byte order mark at the start (Notepad writes one) is dropped."""
    with open(file, encoding="utf-8-sig") as f:
        return f.read()


def write_text(file, text):
    """Write UTF-8 with plain line ends, the same on every system."""
    with open(file, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(file):
    return json.loads(read_text(file))


def write_json(file, data, **kw):
    write_text(file, json.dumps(data, ensure_ascii=False, **kw))


def path(*parts):
    return os.path.join(ROOT, *parts)


def key(name, required=True):
    """An API key from the environment, else from .env in the project folder. Never printed."""
    v = os.environ.get(name, "").strip()
    if not v and os.path.exists(path(".env")):
        for line in read_text(path(".env")).splitlines():
            line = line.strip()
            if line.startswith(name + "="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not v and required:
        sys.exit("Missing %s. Put it in %s (see .env.example) or export it." % (name, path(".env")))
    return v


def script():
    return read_json(path("script.json"))


def http(url, headers, body=None, timeout=900):
    """POST json (or GET when body is None). Returns bytes; exits with the API's own message on an error."""
    data = None if body is None else json.dumps(body).encode()
    h = dict(headers)
    if data is not None:
        h["Content-Type"] = "application/json"
    try:
        return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=timeout).read()
    except urllib.error.HTTPError as e:
        sys.exit("FAILED %s %s\n%s" % (e.code, url.split("?")[0], e.read()[:800].decode("utf-8", "replace")))
    except urllib.error.URLError as e:
        sys.exit("FAILED to reach %s: %s" % (url.split("?")[0], e.reason))


# ---------------------------------------------------------------------------------------------
# OpenRouter: one key (OPENROUTER_API_KEY) for the voice, the word times, the illustrations and the music.
# ---------------------------------------------------------------------------------------------
OPENROUTER = "https://openrouter.ai/api/v1"
VOICE_MODEL = "elevenlabs/eleven-v4"            # speech            POST /audio/speech
WORDS_MODEL = "elevenlabs/scribe-v2"            # word times        POST /audio/transcriptions
IMAGE_MODEL = "google/gemini-nano-banana-2.1"   # illustrations     POST /images
MUSIC_MODEL = "google/lyria-3-pro-preview"      # music             POST /chat/completions (streamed)
MODELS = [("voice", VOICE_MODEL), ("word times", WORDS_MODEL), ("illustrations", IMAGE_MODEL), ("music", MUSIC_MODEL)]

HINTS = {
    401: "The key was refused. Check OPENROUTER_API_KEY in .env.",
    402: "Not enough balance. Audio (voice and music) needs at least $0.50 on the account: add credits at openrouter.ai/settings/credits.",
    403: "The key may not do this. If it has a spending limit or guardrail, check it at openrouter.ai/settings/keys.",
    404: "The key may not use this model. If the key is limited to certain models, allow this one too (%s tools/doctor.py lists what is missing)." % PY,
    429: "Too many requests or the provider is busy. Wait a minute and run the same command again.",
    502: "The provider failed. Nothing was charged. Run the same command again.",
    503: "The provider is not available right now. Run the same command again in a few minutes.",
}


def openrouter(route, body=None, timeout=900, stream=False, fatal=True):
    """POST json to OpenRouter (GET when body is None). Returns the response bytes, or the open response when
    stream is True. On an error: exits with OpenRouter's own message and a hint, or returns (status, text) when not fatal."""
    k = key("OPENROUTER_API_KEY")
    data = None if body is None else json.dumps(body).encode()
    h = {"Authorization": "Bearer " + k, "X-Title": "explainer-video"}
    if data is not None:
        h["Content-Type"] = "application/json"
    try:
        r = urllib.request.urlopen(urllib.request.Request(OPENROUTER + route, data=data, headers=h), timeout=timeout)
        return r if stream else r.read()
    except urllib.error.HTTPError as e:
        text = e.read()[:900].decode("utf-8", "replace").replace(k, "<key>")
        if not fatal:
            return e.code, text
        model = (body or {}).get("model", "")
        sys.exit("FAILED %s %s %s\n%s\n%s" % (e.code, route, model, text, HINTS.get(e.code, "")))
    except urllib.error.URLError as e:
        if not fatal:
            return 0, str(e.reason)
        sys.exit("FAILED to reach OpenRouter: %s" % e.reason)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def loudness(file):
    """(integrated LUFS, true peak dBFS) of an audio or video file, or (None, None)."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", file, "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else ""
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None, float(p.group(1)) if p else None)


def image_size(file):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", file])
    try:
        w, h = r.stdout.strip().split("x")[:2]
        return int(w), int(h)
    except ValueError:
        return None


def fit_width(file, width=3840):
    """Scale a picture down to `width` pixels wide, in place. Returns its (width, height) afterwards."""
    size = image_size(file)
    if not size or size[0] <= width:
        return size
    ext = os.path.splitext(file)[1].lower()
    tmp = file + ".tmp" + ext
    quality = ["-q:v", "3"] if ext in (".jpg", ".jpeg") else []
    r = run(["ffmpeg", "-v", "error", "-y", "-i", file, "-vf", "scale=%d:-2" % width] + quality + [tmp])
    if r.returncode != 0:
        return size
    os.replace(tmp, file)
    return image_size(file)


def hf_cmd():
    """The HyperFrames CLI: through the launcher of the installed hyperframes skill when there is one, else npx."""
    for base in ("~/.claude/skills", "~/.agents/skills", "~/.codex/skills", "~/.cursor/skills", "~/.gemini/skills"):
        f = os.path.expanduser(base + "/hyperframes/scripts/plugin-cli.mjs")
        if os.path.exists(f):
            return ["node", f]
    return [shutil.which("npx") or "npx", "--yes", "hyperframes"]  # on Windows npx is npx.cmd, found by its full path


def duration(file):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------
# The timeline: the same arithmetic as lib/clock.js. Change one, change the other.
# Scene starts (T in timeline.js) are not known here; the Python tools only need the voice and the film's length.
# ---------------------------------------------------------------------------------------------
def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c) and c.isalnum())


class Voice:
    def __init__(self, sid, words, t0, chapters):
        self.id, self.words, self.t0 = sid, words, t0
        self.keys = [norm(w["w"]) for w in words]
        self.cuts = []
        for c in chapters or []:
            i = self.find(c["at"])
            prev_end = words[i - 1]["e"] if i > 0 else 0
            self.cuts.append(((prev_end + words[i]["s"]) / 2, c["gap"]))
        self.end = self.map(words[-1]["e"])
        bounds = [0] + [c[0] for c in self.cuts] + [words[-1]["e"] + 0.5]
        # (video start, video end, source in, source out) per chapter
        self.clips = [(self.map(a), self.map(a) + (b - a), a, b) for a, b in zip(bounds[:-1], bounds[1:])]

    def index(self, phrase, n=1):
        p = [k for k in (norm(x) for x in phrase.split()) if k]
        hit = 0
        for i in range(len(self.keys) - len(p) + 1):
            if self.keys[i:i + len(p)] == p:
                hit += 1
                if hit == n:
                    return i
        return -1

    def find(self, phrase, n=1):
        i = self.index(phrase, n)
        if i < 0:
            sys.exit('Phrase not found in the voice (%s): "%s" #%d' % (self.id, phrase, n))
        return i

    def map(self, s):
        return self.t0 + s + sum(g for c, g in self.cuts if s >= c)

    def at(self, phrase, n=1, k=0):
        return self.map(self.words[self.find(phrase, n) + k]["s"])


def timeline():
    """Returns (voices, END) for the current script.json and assets/vo/words.json."""
    sc = script()
    wp = path("assets", "vo", "words.json")
    words = read_json(wp) if os.path.exists(wp) else {}
    voices, cursor = [], sc.get("lead_in", 1.0)
    for s in sc["segments"]:
        if not words.get(s["id"]):
            sys.exit('No voice yet for segment "%s". Run: %s tools/voice.py' % (s["id"], PY))
        cursor += s.get("gap", 0)
        v = Voice(s["id"], words[s["id"]], cursor, s.get("chapters"))
        voices.append(v)
        cursor = v.end
    return voices, cursor + sc.get("tail", 4.0)


def at(voices, phrase, n=1, k=0):
    left = n
    for v in voices:
        c = 0
        while v.index(phrase, c + 1) >= 0:
            c += 1
        if left <= c:
            return v.at(phrase, left, k)
        left -= c
    sys.exit('Phrase not found in the voice: "%s" #%d' % (phrase, n))


def mmss(t):
    return "%d:%05.2f" % (int(t // 60), t % 60)
