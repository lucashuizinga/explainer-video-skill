# Shared helpers for the tools: keys, HTTP, ffmpeg and the timeline arithmetic.
# Standard library only, Python 3.9+.
import json, os, re, subprocess, sys, unicodedata, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(*parts):
    return os.path.join(ROOT, *parts)


def key(name, required=True):
    """An API key from the environment, else from .env in the project folder. Never printed."""
    v = os.environ.get(name, "").strip()
    if not v and os.path.exists(path(".env")):
        for line in open(path(".env")):
            line = line.strip()
            if line.startswith(name + "="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not v and required:
        sys.exit("Missing %s. Put it in %s (see .env.example) or export it." % (name, path(".env")))
    return v


def script():
    return json.load(open(path("script.json")))


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


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


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


def duration(file):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------
# The timeline: the same arithmetic as lib/vo.ts and timeline.ts. Change one, change the other.
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
    words = json.load(open(wp)) if os.path.exists(wp) else {}
    voices, cursor = [], sc.get("lead_in", 1.0)
    for s in sc["segments"]:
        if not words.get(s["id"]):
            sys.exit('No voice yet for segment "%s". Run: python3 tools/voice.py' % s["id"])
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
