# The last warnings and errors from Diffusion Studio, without the thousands of export progress lines.
# Run it after every save: a compile error shows up here, not in the terminal.
#   python3 tools/logs.py [how many, default 6]
import json, subprocess, sys

n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
r = subprocess.run(["dapi", "logs"], capture_output=True, text=True)
try:
    entries = json.loads(r.stdout)["entries"]
except Exception:
    sys.exit("Could not read the app log. Is Diffusion Studio running? Try: dapi open -b <project folder>")
keep = [e for e in entries if e.get("level") in ("error", "warn") or "compile" in e.get("message", "").lower()]
if not keep:
    print("No warnings or errors in the log.")
for e in keep[-n:]:
    print(e.get("ts"), e.get("level"), e.get("message", "")[:900])
