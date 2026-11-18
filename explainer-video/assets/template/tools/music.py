# The score, with the ElevenLabs music API. Writes assets/music/score.mp3.
#
#   python3 tools/music.py                 from tools/music_plan.json (a composition plan: timed sections)
#   python3 tools/music.py --prompt "..."  one piece as long as the film, from a single description
#   python3 tools/music.py --check         compare the plan's length with the film, generate nothing
#
# Generate the score after the voice is final: the sections must land on the film's chapters.
# Then run tools/mix_music.py to lower it under the voice.
import json, os, sys
from _common import key, http, path, timeline, duration

voices, END = timeline()
out = path("assets", "music", "score.mp3")
os.makedirs(os.path.dirname(out), exist_ok=True)
a = sys.argv[1:]

if "--prompt" in a:
    body = {"prompt": a[a.index("--prompt") + 1], "music_length_ms": int(round(END * 1000)), "force_instrumental": True}
else:
    plan_file = path("tools", "music_plan.json")
    if not os.path.exists(plan_file):
        sys.exit("No tools/music_plan.json. Write one (see the skill's references/sound.md) or use --prompt.")
    plan = json.load(open(plan_file))
    for s in plan["sections"]:
        s.setdefault("lines", [])
        s.setdefault("negative_local_styles", [])
    total = sum(s["duration_ms"] for s in plan["sections"]) / 1000.0
    print("Film %.1f s, plan %.1f s in %d sections." % (END, total, len(plan["sections"])))
    t = 0.0
    for s in plan["sections"]:
        print("  %6.1f  %-22s %5.1f s" % (t, s["section_name"], s["duration_ms"] / 1000.0))
        t += s["duration_ms"] / 1000.0
    if abs(total - END) > 1.5:
        sys.exit("The plan and the film differ by more than 1.5 s. Adjust the section lengths (python3 tools/times.py shows the chapters).")
    body = {"composition_plan": plan}

if "--check" in a:
    sys.exit(0)
audio = http("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192", {"xi-api-key": key("ELEVENLABS_API_KEY")}, body)
open(out, "wb").write(audio)
print("%s  %.1f s. Next: python3 tools/mix_music.py" % (out, duration(out) or 0))
