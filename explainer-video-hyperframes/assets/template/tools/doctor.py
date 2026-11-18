# Checks that this machine and this project can make the film. Costs nothing: no generation calls.
#   python3 tools/doctor.py
import json, os, re, shutil, subprocess, sys, urllib.error, urllib.request
from _common import key, path, script, run, hf_cmd, PY, OPENROUTER, MODELS, VOICE_MODEL

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
WIN, MAC = os.name == "nt", sys.platform == "darwin"
line(bool(shutil.which("ffmpeg")) and bool(shutil.which("ffprobe")), "ffmpeg and ffprobe",
     "Install ffmpeg: %s. Then open a new terminal." % ("winget install Gyan.FFmpeg" if WIN else "brew install ffmpeg" if MAC else "sudo apt install ffmpeg"))

node = shutil.which("node")
ver = re.search(r"v(\d+)", run(["node", "--version"]).stdout) if node else None
line(bool(ver) and int(ver.group(1)) >= 22, "Node.js %s" % (run(["node", "--version"]).stdout.strip() if node else "is missing"),
     "HyperFrames needs Node.js 22 or newer: %s. Then open a new terminal."
     % ("winget install OpenJS.NodeJS.LTS" if WIN else "brew install node" if MAC else "see nodejs.org for your system"))
if node:
    cmd = hf_cmd()
    line(cmd[0] == "node", "the hyperframes skill is installed",
         "Not found in the usual skill folders. The person installs it once with: npx hyperframes skills   and then starts a new session.")
    try:
        r = subprocess.run(cmd + ["doctor", "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, cwd=os.path.expanduser("~"))
        d = json.loads(r.stdout[r.stdout.index("{"):])
        checks = {c["name"]: c for c in d.get("checks", [])}
        line(True, "HyperFrames CLI %s" % d.get("_meta", {}).get("version", ""))
        chrome = checks.get("Chrome", {})
        line(bool(chrome.get("ok")), "the browser HyperFrames renders with", "Run: npx hyperframes browser ensure")
    except Exception as e:
        line(False, "HyperFrames CLI answers", "Could not run it (%s). Check the network and try: npx hyperframes doctor" % str(e)[:120])
    if os.path.exists(path("assets", "vo", "words.json")):
        r = run(["node", path("tools", "sync.mjs"), "--check"])
        line(r.returncode == 0, "the HTML matches the voice", "Run: node tools/sync.mjs")

ok_key = key("OPENROUTER_API_KEY", required=False)
line(bool(ok_key), "OPENROUTER_API_KEY is set", "Put it in %s" % path(".env"))
if ok_key:
    auth = {"Authorization": "Bearer " + ok_key}
    d, err = get(OPENROUTER + "/key", auth)
    line(d is not None, "the OpenRouter key works", "The key request failed (%s). Check the key at openrouter.ai/settings/keys." % err)
    if d:
        info = d.get("data") or {}
        left = info.get("limit_remaining")
        if left is not None:
            line(left >= 0.5, "the key's spending limit has room ($%.2f left)" % left,
                 "The key has reached its limit. Raise it at openrouter.ai/settings/keys.")
        if info.get("expires_at"):
            print("     the key expires on %s" % str(info["expires_at"])[:10])
        # which of the four models this key may use (a key can be limited to certain models)
        m, err = get(OPENROUTER + "/models/user?output_modalities=all", auth)
        line(m is not None, "OpenRouter lists the models for this key", "The models request failed (%s)." % err)
        if m:
            have = set(x.get("id") for x in m.get("data", []))
            for what, mid in MODELS:
                line(mid in have, "%s: %s" % (what, mid),
                     "This key may not use it. Allow the model for this key at openrouter.ai/settings/keys (guardrails)."
                     + (" Without it you can still make the film with the demo music or your own music file." if what == "music" else ""))
            speech = [x for x in m.get("data", []) if x.get("id") == VOICE_MODEL]
            names = (speech[0].get("supported_voices") or []) if speech else []
            try:
                for name, v in (script().get("voices") or {}).items():
                    known = v in names or bool(re.match(r"^[A-Za-z0-9]{20}$", v))
                    line(known, 'voice "%s" (%s)' % (name, v), "Not a voice name of Eleven v4. See: %s tools/voices.py" % PY)
            except Exception as e:
                line(False, "script.json is readable", str(e)[:200])
        c, err = get(OPENROUTER + "/credits", auth)
        if c and c.get("data"):
            bal = c["data"].get("total_credits", 0) - c["data"].get("total_usage", 0)
            line(bal >= 0.5, "balance on the account: $%.2f" % bal,
                 "Voice and music are refused below $0.50. Add credits at openrouter.ai/settings/credits.")
        else:
            print("     balance: this key may not read it (%s). Voice and music need at least $0.50 on the account." % err)

print("\nAll good." if ok else "\nFix the FAIL lines first.")
sys.exit(0 if ok else 1)
