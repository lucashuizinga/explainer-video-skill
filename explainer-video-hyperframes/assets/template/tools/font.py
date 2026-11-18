#!/usr/bin/env python3
"""Download a typeface from Google Fonts into assets/fonts and declare it in index.html.

HyperFrames resolves only its bundled families by name (Inter, Montserrat, Outfit, Poppins, Roboto and
a few more). Any other family needs a font file in the project and an @font-face rule.

    python3 tools/font.py "Space Grotesk"               the variable weight range when there is one
    python3 tools/font.py "Fraunces" 400,700            fixed weights
    python3 tools/font.py "Fraunces" 400,700 --italic   with italics

The rules go between /* fonts:start */ and /* fonts:end */ in index.html. A brand font that is not on
Google Fonts: put its .woff2 in assets/fonts and write the @font-face rule there by hand.
"""
import re, sys, urllib.parse, urllib.request
from _common import path, read_text, write_text

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SUBSETS = ("latin", "latin-ext")


def css(family, axis):
    url = "https://fonts.googleapis.com/css2?family=%s%s&display=block" % (urllib.parse.quote_plus(family), axis)
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode()
    except Exception:
        return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    family, italic = args[0], "--italic" in sys.argv
    weights = args[1] if len(args) > 1 else None
    tries = []
    if weights:
        w = weights.replace(",", ";")
        tries.append((":ital,wght@" + ";".join(["0,%s" % x for x in w.split(";")] + ["1,%s" % x for x in w.split(";")])) if italic else ":wght@" + w)
    else:
        tries += [":wght@100..900", ":wght@200..900", ":wght@300..700", ":wght@300..800", ":wght@400..700", ":wght@400..800", ":wght@400..900", ":wght@400;700", ""]
    sheet = None
    for axis in tries:
        sheet = css(family, axis)
        if sheet:
            break
    if not sheet:
        sys.exit('FAILED: Google Fonts has no "%s" with those weights. Check the name at fonts.google.com.' % family)

    slug = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    rules, seen = [], {}
    for subset, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}", sheet):
        if subset not in SUBSETS:
            continue
        src = re.search(r"url\((https://[^)]+)\)", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        weight = re.search(r"font-weight:\s*([\d ]+)", body).group(1).strip()
        rng = re.search(r"unicode-range:\s*([^;]+);", body)
        if src not in seen:
            name = "%s-%s%s-%s.woff2" % (slug, weight.replace(" ", "-"), "-italic" if style == "italic" else "", subset)
            data = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=120).read()
            import os
            os.makedirs(path("assets", "fonts"), exist_ok=True)
            open(path("assets", "fonts", name), "wb").write(data)
            seen[src] = name
            print("saved assets/fonts/%s (%d kB)" % (name, len(data) // 1024))
        rules.append(
            "      @font-face { font-family: \"%s\"; font-style: %s; font-weight: %s; font-display: block; src: url(\"assets/fonts/%s\") format(\"woff2\");%s }"
            % (family, style, weight, seen[src], (" unicode-range: %s;" % rng.group(1).strip()) if rng else "")
        )
    if not rules:
        sys.exit("FAILED: no latin subset found for %s" % family)

    index = path("index.html")
    html = read_text(index)
    m = re.search(r"/\* fonts:start \*/(.*?)/\* fonts:end \*/", html, re.S)
    if not m:
        print("\nindex.html has no /* fonts:start */ ... /* fonts:end */ block. Paste these rules into its <style>:\n")
        print("\n".join(rules))
        return
    kept = [l for l in m.group(1).split("\n") if l.strip() and ('font-family: "%s"' % family) not in l]
    block = "/* fonts:start */\n" + "\n".join(kept + rules) + "\n      /* fonts:end */"
    write_text(index, html[: m.start()] + block + html[m.end():])
    print('declared "%s" in index.html. Use it as: font-family: "%s", sans-serif' % (family, family))


if __name__ == "__main__":
    main()
