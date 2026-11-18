# Illustrations with Google's Gemini image model (Nano Banana Pro), paid from your own GEMINI_API_KEY.
#
#   python3 tools/image.py assets/img/desk.png "a calm flat illustration of ..."
#   python3 tools/image.py assets/img/desk-later.png "the same desk at night" --ref assets/img/desk.png
#
# Options: --ref <file> (repeatable: a style or subject reference, or the image to edit)
#          --size 4K|2K|1K (default 4K)   --aspect 16:9 (default)   --model <id>
#          --full  keep the full size the API returns (default: scaled down to 3840 wide, sharp up to zoom 2)
# The file is saved with the type the API returns (.png or .jpg); the final path and pixel size are printed.
import base64, json, os, sys
from _common import key, http, image_size, fit_width

MODEL = "gemini-3-pro-image"
a = sys.argv[1:]
if len(a) < 2:
    sys.exit(__doc__ or "usage: image.py <out> <prompt> [--ref file]... [--size 4K] [--aspect 16:9]")
out, prompt, refs, size, aspect, model = a[0], a[1], [], "4K", "16:9", MODEL
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

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
parts = [{"text": prompt}]
for r in refs:
    ext = os.path.splitext(r)[1].lower()
    if ext not in MIME:
        sys.exit("Reference %s must be png, jpg or webp." % r)
    parts.append({"inline_data": {"mime_type": MIME[ext], "data": base64.b64encode(open(r, "rb").read()).decode()}})

body = {"contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect, "imageSize": size}}}
d = json.loads(http("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model,
                    {"x-goog-api-key": key("GEMINI_API_KEY")}, body, timeout=600))
img = None
for c in d.get("candidates", []):
    for p in (c.get("content") or {}).get("parts", []):
        blob = p.get("inlineData") or p.get("inline_data")
        if blob:
            img = blob
if not img:
    reason = (d.get("candidates") or [{}])[0].get("finishReason") or d.get("promptFeedback")
    sys.exit("No image came back (%s). Reword the prompt and try again." % reason)

mime = img.get("mimeType") or img.get("mime_type") or "image/png"
ext = ".jpg" if "jpeg" in mime else ".webp" if "webp" in mime else ".png"
out = os.path.splitext(out)[0] + ext
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "wb").write(base64.b64decode(img["data"]))
got = image_size(out)
dim = got if full else fit_width(out, 3840)
usage = d.get("usageMetadata") or {}
print("%s  %s  (API returned %s, %s output tokens)" % (out, "%dx%d" % dim if dim else "size unknown", "%dx%d" % got if got else "?", usage.get("candidatesTokenCount", "?")))
if dim and dim[0] < 3000:
    print("Note: narrower than 3000 px. Keep the camera zoom on this picture at or below %.2f." % (dim[0] / 1920.0))
