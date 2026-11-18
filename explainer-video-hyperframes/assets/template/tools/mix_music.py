# Bakes the level of the score into assets/music/bed.mp3: low while the voice speaks, up in the pauses,
# with a fade in and out. The film then plays bed.mp3 at 0 dB.
#
#   python3 tools/mix_music.py                     defaults: 15 dB below the voice while it speaks, 6 dB below in pauses
#   python3 tools/mix_music.py --under -18 --open -5 --pause 1.6
#
# The score is first brought to the level of the voice (-17 LUFS), so --under and --open mean
# "this many dB below the voice" whatever the loudness of the generated piece.
# Generated scores get louder from section to section, which is why the level is fixed here and not
# with one volume number in the film. Listen to the result and adjust the two levels.
import sys
from _common import path, timeline, duration, run, loudness

a = sys.argv[1:]
opt = lambda name, d: float(a[a.index(name) + 1]) if name in a else d
UNDER, OPEN, PAUSE = opt("--under", -15.0), opt("--open", -6.0), opt("--pause", 1.6)
src = a[a.index("--in") + 1] if "--in" in a else path("assets", "music", "score.mp3")
out = path("assets", "music", "bed.mp3")

voices, END = timeline()
# stretches where someone speaks; a silence shorter than PAUSE does not open the music
spans = []
for v in voices:
    for (s, e, _, _) in v.clips:
        e = min(e, v.end + 0.3)
        if spans and s - spans[-1][1] < PAUSE:
            spans[-1][1] = e
        else:
            spans.append([s, e])

pts = [(0.0, -60.0), (1.2, UNDER if spans and spans[0][0] < PAUSE else OPEN)]
for s, e in spans:
    if s - 0.9 > pts[-1][0]:
        pts.append((s - 0.9, OPEN))
        pts.append((s - 0.2, UNDER))
    pts.append((e + 0.2, UNDER))
    pts.append((e + 0.9, OPEN))
# the tail: stay open after the last word, then fade out
pts = [p for p in pts if p[0] < END - 1.9]
pts.append((END - 1.8, pts[-1][1]))
pts.append((END - 0.05, -60.0))
pts.sort()

lufs, _ = loudness(src)
pre = 0.0 if lufs is None else max(-15.0, min(15.0, -17.0 - lufs))

# piecewise linear dB curve as one ffmpeg expression
expr = "%.2f" % pts[0][1]
for (t0, d0), (t1, d1) in zip(pts[:-1], pts[1:]):
    if t1 - t0 < 0.01 or d1 == d0:
        continue
    expr += "+(%.2f)*clip((t-%.3f)/%.3f,0,1)" % (d1 - d0, t0, t1 - t0)
af = "apad,volume=%.2fdB,volume=eval=frame:volume='pow(10,(%s)/20)',alimiter=limit=0.84:attack=5:release=80:level=disabled" % (pre, expr)
r = run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-t", "%.3f" % END, "-c:a", "libmp3lame", "-b:a", "192k", out])
if r.returncode != 0:
    sys.exit("ffmpeg failed:\n" + r.stderr[-800:])
print("%s  %.1f s  (score %.1f s at %s LUFS, film %.1f s)" % (out, duration(out) or 0, duration(src) or 0, lufs, END))
for t, d in pts:
    print("  %7.2f  %6.1f dB" % (t, d))
