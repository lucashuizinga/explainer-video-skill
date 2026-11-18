# Illustrations with Nano Banana 2.1 (Google) through OpenRouter, paid from your own OPENROUTER_API_KEY.
#
#   python3 tools/image.py assets/img/desk.png "a calm flat illustration of ..."
#   python3 tools/image.py assets/img/desk-later.png "the same desk at night" --ref assets/img/desk.jpg
#
# Options: --ref <file> (repeatable, up to 14: a style or subject reference, or the image to edit)
#          --size 4K|2K|1K (default 4K)   --aspect 16:9 (default)   --model <id>
#          --full  keep the full size the API returns (default: scaled down to 3840 wide, sharp up to zoom 2)
# The file is saved with the type the API returns (.png or .jpg); the final path, pixel size and price are printed.
import base64, json, os, sys
from _common import openrouter, image_size, fit_width, run, PY, IMAGE_MODEL

a = sys.argv[1:]
if len(a) < 2:
    sys.exit('usage: %s tools/image.py <out> "<prompt>" [--ref file]... [--size 4K] [--aspect 16:9] [--model id] [--full]' % PY)
out, prompt, refs, size, aspect, model = a[0], a[1], [], "4K", "16:9", IMAGE_MODEL
full = "--full" in a
a = [x for x in a if x != "--full"]
i = 2
while i < len(a):
    if i + 1 >= len(a):
        sys.exit("Option %s needs a value." % a[i])
    if a[i] == "--ref":
        refs.append(a[i + 1])
    elif a[i] == "--size":
        size = a[i + 1]
    elif a[i] == "--aspect":
        aspect = a[i + 1]
    elif a[i] == "--model":
        model = a[i + 1]
    else:
        sys.exit("Unknown option %s" % a[i])
    i += 2


def reference(file):
    """A reference as a data URL. Large files are sent 2752 px wide: enough for style and layout, and a small request."""
    ext = os.path.splitext(file)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        sys.exit("Reference %s must be png, jpg or webp." % file)
    if not os.path.exists(file):
        sys.exit("Reference %s does not exist." % file)
    data, mime = open(file, "rb").read(), {".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
    size_px = image_size(file)
    if len(data) > 3000000 or (size_px and size_px[0] > 2752):
        tmp = file + ".ref.jpg"
        r = run(["ffmpeg", "-v", "error", "-y", "-i", file, "-vf", "scale='min(2752,iw)':-2", "-q:v", "3", tmp])
        if r.returncode == 0:
            data, mime = open(tmp, "rb").read(), "image/jpeg"
            os.remove(tmp)
    return {"type": "image_url", "image_url": {"url": "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())}}


body = {"model": model, "prompt": prompt, "n": 1, "aspect_ratio": aspect, "resolution": size}
if refs:
    body["input_references"] = [reference(r) for r in refs]
d = json.loads(openrouter("/images", body, timeout=600))
item = (d.get("data") or [{}])[0]
if not item.get("b64_json"):
    sys.exit("No image came back (%s). Reword the prompt and try again." % json.dumps(d)[:300])

mime = item.get("media_type") or "image/png"
ext = ".jpg" if "jpeg" in mime else ".webp" if "webp" in mime else ".png"
out = os.path.splitext(out)[0] + ext
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "wb").write(base64.b64decode(item["b64_json"]))
got = image_size(out)
dim = got if full else fit_width(out, 3840)
cost = (d.get("usage") or {}).get("cost")
print("%s  %s  (API returned %s%s)" % (out, "%dx%d" % dim if dim else "size unknown", "%dx%d" % got if got else "?",
                                      ", $%.3f" % cost if cost is not None else ""))
if dim and dim[0] < 3000:
    print("Note: narrower than 3000 px. Keep the camera zoom on this picture at or below %.2f." % (dim[0] / 1920.0))
