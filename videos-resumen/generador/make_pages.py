# -*- coding: utf-8 -*-
"""Genera engine/<ID>.html + engine/data_<ID>.js a partir de content.py y out/<ID>/timeline.json."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import VIDEOS, MODULE
ICONS_DIR = os.path.join(HERE, "node_modules", "lucide-static", "icons")
INTERNAL = ["arrow-right", "timer", "quote", "circle-check", "lightbulb", "sparkles", "type", "image", "mic", "video",
            "activity", "circle", "shuffle", "cpu", "triangle-alert", "lock", "minus", "plus", "check", "x", "thumbs-up",
            "tag", "bitcoin", "apple", "heart-handshake", "link"]

def collect(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "icon" and isinstance(v, str): acc.add(v)
            else: collect(v, acc)
    elif isinstance(o, list):
        for v in o: collect(v, acc)

def load_icon(name):
    p = os.path.join(ICONS_DIR, name + ".svg")
    if not os.path.exists(p):
        raise SystemExit(f"icono inexistente: {name}")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()
    s = re.sub(r'\s(width|height)="24"', "", s)
    s = re.sub(r'\sclass="[^"]*"', "", s)
    return re.sub(r"\s+", " ", s)

TEMPLATE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{id}</title>
<link rel="stylesheet" href="engine.css"></head><body>
<canvas id="bg"></canvas><div id="stage"></div><div id="chrome"></div><div id="sweep"></div><div id="fade"></div>
<script src="../node_modules/gsap/dist/gsap.min.js"></script>
<script src="data_{id}.js"></script>
<script src="engine.js"></script>
</body></html>"""

def make(v):
    tl = json.load(open(os.path.join(HERE, "out", v["id"], "timeline.json"), encoding="utf-8"))
    tl["hit"] = round(tl["lines"][-1]["end"] + 0.15, 3)
    names = set(INTERNAL); collect(v, names)
    eng = open(os.path.join(HERE, "engine", "engine.js"), encoding="utf-8").read()
    lits = set(re.findall(r'"([a-z0-9]+(?:-[a-z0-9]+)*)"', eng))
    names |= {n for n in lits if os.path.exists(os.path.join(ICONS_DIR, n + ".svg"))}
    data = dict(v); data["module"] = MODULE; data["timeline"] = tl
    data["icons"] = {n: load_icon(n) for n in sorted(names)}
    with open(os.path.join(HERE, "engine", f"data_{v['id']}.js"), "w", encoding="utf-8") as f:
        f.write("window.VIDEO = " + json.dumps(data, ensure_ascii=False) + ";\n")
    with open(os.path.join(HERE, "engine", f"{v['id']}.html"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(id=v["id"]))
    return tl

if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else [v["id"] for v in VIDEOS]
    for v in VIDEOS:
        if v["id"] in ids and os.path.exists(os.path.join(HERE, "out", v["id"], "timeline.json")):
            tl = make(v); print(v["id"], "duración", tl["duration"], "hit", tl["hit"])
