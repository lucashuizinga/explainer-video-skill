# The voices this ElevenLabs key can use.
#   python3 tools/voices.py           all voices
#   python3 tools/voices.py nl        voices labelled or verified for a language code
#   python3 tools/voices.py nl warm   and matching a word in the name or description
import json, sys
from _common import key, http

lang = sys.argv[1].lower() if len(sys.argv) > 1 else None
word = sys.argv[2].lower() if len(sys.argv) > 2 else None
d = json.loads(http("https://api.elevenlabs.io/v1/voices", {"xi-api-key": key("ELEVENLABS_API_KEY")}))
rows = []
for v in d.get("voices", []):
    labels = v.get("labels") or {}
    langs = set([labels.get("language")] + [x.get("language") for x in (v.get("verified_languages") or [])]) - {None}
    text = " ".join([v.get("name") or "", v.get("description") or "", " ".join(str(x) for x in labels.values())]).lower()
    if lang and lang not in langs:
        continue
    if word and word not in text:
        continue
    rows.append((v["voice_id"], v.get("name", "")[:46], v.get("category", ""), labels.get("gender", ""), labels.get("age", ""), ",".join(sorted(langs))[:24]))
for r in rows:
    print("%-22s %-46s %-12s %-8s %-12s %s" % r)
print("%d voice(s). Premade voices exist on every account; others only on this one." % len(rows))
