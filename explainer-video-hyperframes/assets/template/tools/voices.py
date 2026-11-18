# The voices Eleven v4 offers through OpenRouter. Costs nothing and needs no key.
#   python3 tools/voices.py
#
# Put a name from this list in "voices" in script.json. A voice id from the ElevenLabs voice library
# (20 letters and digits) is accepted in the same place; an unknown one is refused with an error.
# OpenRouter gives no description or language per voice: these are the ElevenLabs premade voices, which
# speak every language Eleven v4 supports. Judge a voice by a short take in the film's own language.
import json, urllib.request
from _common import OPENROUTER, VOICE_MODEL

d = json.loads(urllib.request.urlopen(OPENROUTER + "/models?output_modalities=speech", timeout=60).read())
m = [x for x in d.get("data", []) if x.get("id") == VOICE_MODEL]
if not m:
    raise SystemExit("%s is not in OpenRouter's list of speech models." % VOICE_MODEL)
names = m[0].get("supported_voices") or []
print("%s, %d voices:" % (VOICE_MODEL, len(names)))
print("  " + "  ".join(names))
price = (m[0].get("pricing") or {}).get("prompt")
if price:
    print("Price: $%.2f per 1000 characters of text." % (float(price) * 1000))
