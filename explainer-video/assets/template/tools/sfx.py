# A new sound effect with the ElevenLabs sound generation API. Writes assets/sfx/<name>.mp3.
# The template already ships pop, whoosh, tick, pluck, chime, sparkle, swell, stamp, paper, clink, coins and drip:
# make a new one only when none of those fits.
#
#   python3 tools/sfx.py zip "short fabric zipper closing, dry, close microphone" 1.0
import os, sys
from _common import key, http, path

if len(sys.argv) < 3:
    sys.exit('usage: python3 tools/sfx.py <name> "<description>" [seconds, 0.5 to 22]')
name, text = sys.argv[1], sys.argv[2]
body = {"text": text, "prompt_influence": 0.5}
if len(sys.argv) > 3:
    body["duration_seconds"] = float(sys.argv[3])
out = path("assets", "sfx", name + ".mp3")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(http("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128", {"xi-api-key": key("ELEVENLABS_API_KEY")}, body))
print(out)
