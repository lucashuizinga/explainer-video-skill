# Loudness of a file (an export, a voice clip, the music bed).
#   python3 tools/loudness.py exports/film.mp4
# Target for the finished film: about -16 LUFS integrated, true peak at or below -1.5 dBFS.
import sys
from _common import loudness, duration

for f in sys.argv[1:]:
    i, p = loudness(f)
    if i is None:
        print("%s: could not measure" % f)
        continue
    note = []
    if i < -18.5:
        note.append("quiet: raise the levels")
    if i > -14:
        note.append("loud: lower the levels")
    if p is not None and p > -1.0:
        note.append("peaks too high: lower the levels")
    print("%s  %.1f s  %.1f LUFS  peak %s dBFS  %s" % (f, duration(f) or 0, i, "?" if p is None else "%.1f" % p, "; ".join(note) or "ok"))
