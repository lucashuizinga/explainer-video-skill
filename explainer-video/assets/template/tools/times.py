# The timeline as the film sees it: where every segment and chapter starts, and how long the film is.
#   python3 tools/times.py                      segments, chapters, end
#   python3 tools/times.py "a phrase" ["..."]   the video time of phrases
#   python3 tools/times.py --words s2           every word of a segment with its video time
import sys
from _common import timeline, at, mmss

voices, END = timeline()
args = sys.argv[1:]
if args and args[0] == "--words":
    for v in voices:
        if len(args) > 1 and v.id != args[1]:
            continue
        print(v.id)
        for w in v.words:
            print("  %7.2f  %s" % (v.map(w["s"]), w["w"]))
elif args:
    for p in args:
        print("%7.2f  %s" % (at(voices, p), p))
else:
    for v in voices:
        first = " ".join(w["w"] for w in v.words[:6])
        print("%-5s %7.2f to %7.2f  (%s)  %s ..." % (v.id, v.t0, v.end, mmss(v.t0), first))
        for i, (a, b, si, so) in enumerate(v.clips[1:], 1):
            print("      chapter %d starts at %7.2f" % (i + 1, a))
    print("END   %7.2f  (%s)" % (END, mmss(END)))
