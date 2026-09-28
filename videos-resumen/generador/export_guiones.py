# -*- coding: utf-8 -*-
"""Exporta los guiones narrados (con tiempos) a Markdown."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import VIDEOS, MODULE
from narration import split_marks

NAMES = {"intro": "Portada", "timeline": "Línea de tiempo", "grid": "Tarjetas", "flow": "Proceso", "quote": "Idea clave",
         "cycle": "Ciclo", "compare": "Comparativa", "definition": "Definición", "stats": "Datos", "stack": "Niveles",
         "tiers": "Capas", "chain": "Cadena de bloques", "proscons": "Ventajas e inconvenientes", "outro": "Cierre"}

def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"

def export(outdir):
    os.makedirs(outdir, exist_ok=True)
    for v in VIDEOS:
        tl = json.load(open(os.path.join(HERE, "out", v["id"], "timeline.json"), encoding="utf-8"))
        L = [f"# {v['id']} · {v['title']}", "", f"*{MODULE}* — guion del vídeo resumen (duración {mmss(tl['duration'])}).", ""]
        for si, sc in enumerate(v["scenes"]):
            S = tl["scenes"][si]
            head = sc.get("title") or sc.get("term") or sc.get("quote") or ("Portada" if sc["type"] == "intro" else "")
            kick = sc.get("kicker", "")
            label = f"{kick} — {head}" if kick else head
            L.append(f"## [{mmss(S['start'])}] {label}  ")
            L.append(f"<sub>Escena: {NAMES.get(sc['type'], sc['type'])}</sub>")
            L.append("")
            for raw in sc["lines"]:
                L.append(f"> {split_marks(raw)[0]}")
                L.append(">")
            L.pop()
            L.append("")
        open(os.path.join(outdir, f"{v['id']}.md"), "w", encoding="utf-8").write("\n".join(L))
        print("guion", v["id"])

if __name__ == "__main__":
    export(sys.argv[1])
