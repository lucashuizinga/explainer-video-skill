# Checks that this machine and this project can make the film. Costs nothing: no generation calls.
#   python3 tools/doctor.py
import json, os, shutil, sys, urllib.error, urllib.request
from _common import key, path, script, run

ok = True


def line(good, what, hint=""):
    global ok
    if not good:
        ok = False
    print("%s %s%s" % ("ok  " if good else "FAIL", what, "" if good or not hint else "\n       " + hint))


def get(url, headers):
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30).read()), None
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:
        return None, str(e)[:120]


line(sys.version_info >= (3, 9), "Python %d.%d" % sys.version_info[:2], "Python 3.9 or newer is needed.")
line(bool(shutil.which("ffmpeg")) and bool(shutil.which("ffprobe")), "ffmpeg and ffprobe", "Install ffmpeg (macOS: brew install ffmpeg).")

app = os.path.exists("/Applications/Diffusion Studio.app")
dapi = shutil.which("dapi")
line(bool(dapi), "dapi command line tool",
     "Link it: sudo ln -sf \"/Applications/Diffusion Studio.app/Contents/Resources/cli/bin/dapi\" /usr/local/bin/dapi" if app
     else "Install Diffusion Studio: brew install --cask diffusionstudio/tap/editor")
if dapi:
    r = run(["dapi", "context"])
    line(r.returncode == 0, "Diffusion Studio answers", "Start it with: dapi open -b \"%s\"" % path())

ek = key("ELEVENLABS_API_KEY", required=False)
line(bool(ek), "ELEVENLABS_API_KEY is set", "Put it in %s" % path(".env"))
if ek:
    d, err = get("https://api.elevenlabs.io/v1/voices", {"xi-api-key": ek})
    line(d is not None, "ElevenLabs key works", "The voices request failed (%s). Check the key and that it may read voices." % err)
    if d:
        have = set(v["voice_id"] for v in d.get("voices", []))
        try:
            for name, vid in script()["voices"].items():
                line(vid in have, 'voice "%s" is available on this account' % name,
                     "Pick another with: python3 tools/voices.py <language code>")
        except Exception as e:
            line(False, "script.json is readable", str(e)[:200])

gk = key("GEMINI_API_KEY", required=False)
line(bool(gk), "GEMINI_API_KEY is set", "Put it in %s" % path(".env"))
if gk:
    d, err = get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", {"x-goog-api-key": gk})
    line(d is not None, "Gemini key works", "The models request failed (%s)." % err)
    if d:
        names = [m["name"] for m in d.get("models", [])]
        line("models/gemini-3-pro-image" in names, "Gemini image model (gemini-3-pro-image) is available",
             "Image models on this key: %s. Pass one with --model to tools/image.py." % (", ".join(n.split("/")[1] for n in names if "image" in n) or "none"))

print("\nAll good." if ok else "\nFix the FAIL lines first.")
sys.exit(0 if ok else 1)
