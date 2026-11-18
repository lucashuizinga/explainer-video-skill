# Starts a new explainer video from the skill's template.
#
#   python3 <skill>/scripts/new_project.py <new project folder> ["Display name"]
#
# Copies the template (lib, tools, sound effects, a small working demo film) into a new folder,
# names the project and creates an empty .env for the two API keys.
import json, os, re, shutil, sys

if len(sys.argv) < 2:
    sys.exit('usage: python3 new_project.py <new project folder> ["Display name"]')
target = os.path.abspath(os.path.expanduser(sys.argv[1]))
name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(target)
template = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "template")

if os.path.exists(target) and os.listdir(target):
    sys.exit("%s already exists and is not empty. Choose a new folder." % target)
shutil.copytree(template, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "cache", "exports"))

pkg_file = os.path.join(target, "package.json")
pkg = json.load(open(pkg_file))
pkg["name"] = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "explainer-video"
pkg["displayName"] = name
pkg.pop("projectId", None)  # a copied projectId makes two folders open as the same project
json.dump(pkg, open(pkg_file, "w"), indent=2)

env = os.path.join(target, ".env")
if not os.path.exists(env):
    shutil.copy(os.path.join(target, ".env.example"), env)

print("Project created: %s" % target)
print("1. Put the two keys in %s" % env)
print("2. cd \"%s\" && python3 tools/doctor.py" % target)
print("3. dapi open -b \"%s\"   then   dapi capture film -t 2 6 12" % target)
