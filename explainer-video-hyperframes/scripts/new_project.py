# Starts a new explainer video from the skill's template.
#
#   python3 <skill>/scripts/new_project.py <new project folder> ["Display name"]
#
# Copies the template (the voice clock, tools, sound effects, a small working demo film) into a new
# folder, names the project and creates an empty .env for the OpenRouter key.
import datetime, json, os, re, shutil, sys

for _stream in (sys.stdout, sys.stderr):  # Windows: print paths and names with accents without stopping
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if len(sys.argv) < 2:
    sys.exit('usage: python new_project.py <new project folder> ["Display name"]')
target = os.path.abspath(os.path.expanduser(sys.argv[1]))
name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(target)
template = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "template")

if os.path.exists(target) and os.listdir(target):
    sys.exit("%s already exists and is not empty. Choose a new folder." % target)
shutil.copytree(template, target, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", ".hyperframes", "exports", "renders", "node_modules"))

slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "explainer-video"
pkg_file = os.path.join(target, "package.json")
pkg = json.load(open(pkg_file, encoding="utf-8"))
pkg["name"] = slug
json.dump(pkg, open(pkg_file, "w", encoding="utf-8", newline="\n"), indent=2, ensure_ascii=False)

meta_file = os.path.join(target, "meta.json")
meta = {"id": slug, "name": name, "createdAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")}
json.dump(meta, open(meta_file, "w", encoding="utf-8", newline="\n"), indent=2, ensure_ascii=False)

env = os.path.join(target, ".env")
if not os.path.exists(env):
    shutil.copy(os.path.join(target, ".env.example"), env)

print("Project created: %s" % target)
print("1. Put the OpenRouter key in %s" % env)
print("2. cd \"%s\" && %s tools/doctor.py" % (target, "python" if os.name == "nt" else "python3"))
print("3. npx hyperframes check --json   then   npx hyperframes snapshot --at 2,8,14,20")
