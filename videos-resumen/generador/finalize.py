# -*- coding: utf-8 -*-
"""Regenera subtítulos, los incrusta (sin recodificar) y publica los MP4 en el repositorio con su README."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mix import make_srt
from content import VIDEOS, MODULE
R = os.path.normpath(os.path.join(HERE, ".."))  # carpeta videos-resumen/
NAMES = {"UT1": "UT1_Digitalizacion_de_los_sectores_productivos", "UT2": "UT2_Tecnologias_digitales_habilitadoras",
         "UT3": "UT3_Sistemas_en_la_nube", "UT4": "UT4_Aplicacion_de_la_inteligencia_artificial", "UT5": "UT5_Big_data"}

def probe(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", f], capture_output=True, text=True).stdout
    d = json.loads(out)["format"]
    return float(d["duration"]), int(d["size"])

rows = []
for v in VIDEOS:
    vid, name = v["id"], NAMES[v["id"]]
    src = os.path.join(HERE, "out", vid, f"{vid}.mp4")
    if not os.path.exists(src):
        print("falta", src); continue
    tl = json.load(open(os.path.join(HERE, "out", vid, "timeline.json"), encoding="utf-8"))
    srt = os.path.join(R, f"{name}.srt")
    make_srt(tl, srt)
    dest = os.path.join(R, f"{name}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-i", srt, "-map", "0:v", "-map", "0:a", "-map", "1:s",
                    "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-map_metadata", "0",
                    "-metadata:s:s:0", "language=spa", "-metadata:s:s:0", "title=Español",
                    "-metadata:s:a:0", "language=spa", "-movflags", "+faststart", dest], check=True)
    dur, size = probe(dest)
    rows.append((vid, v["title"], name, dur, size))
    print(f"{vid}: {dest} {dur:.1f}s {size/1e6:.1f} MB")

def mmss(t):
    s = int(round(t))
    return f"{s // 60}:{s % 60:02d}"
L = [f"# Vídeos resumen · {MODULE}", "",
     "Cinco vídeos de unos **2 minutos** que resumen los apuntes de cada unidad, con el mismo estilo gráfico, "
     "voz de narrador en español, música motivadora y subtítulos.", "",
     "| Unidad | Vídeo | Duración | Guion | Subtítulos |", "|---|---|---|---|---|"]
for vid, title, name, dur, size in rows:
    L.append(f"| **{vid}** · {title} | [{name}.mp4]({name}.mp4) ({size/1e6:.0f} MB) | {mmss(dur)} | [guion](guiones/{vid}.md) | [.srt]({name}.srt) |")
L += ["", "## Características", "",
      "- **Formato:** MP4 (H.264 + AAC), 1920×1080, 30 fps. Se reproduce en cualquier móvil, ordenador, Moodle, Classroom o YouTube.",
      "- **Narración:** voz masculina en español generada con el modelo Supertonic 3; cada frase se verificó automáticamente con reconocimiento de voz (Whisper).",
      "- **Música:** pista *uplifting* original compuesta y sintetizada por código para cada vídeo (misma instrumentación, distinta tonalidad), sin derechos de autor. Baja automáticamente cuando habla el narrador.",
      "- **Gráficos:** estilo unificado (fondo tecnológico animado, tarjetas, iconos, líneas de tiempo, diagramas) con un color distinto por unidad. Cada elemento aparece justo cuando el narrador lo menciona.",
      "- **Subtítulos:** pista de subtítulos en español dentro del MP4 (se activa desde el reproductor) y archivo `.srt` con el mismo nombre del vídeo (VLC y la mayoría de reproductores lo cargan solo).",
      "", "## Contenido de cada vídeo", ""]
for v in VIDEOS:
    kick = [sc.get("title") or sc.get("term") or sc.get("quote") for sc in v["scenes"] if sc["type"] not in ("intro", "outro")]
    items = " · ".join(k for k in kick if k)
    L.append(f"- **{v['id']} · {v['title']}:** " + items + ("" if items[-1] in ".?!" else "."))
L += ["", "Los datos de «cada minuto en internet» de la UT5 proceden de la infografía de LocaliQ (2023) incluida en la presentación.",
      "", "## Regenerar o modificar los vídeos", "",
      "La carpeta [`generador/`](generador/) contiene todo el código: guion (`content.py`), voz, música, mezcla y motor gráfico. "
      "Para cambiar un texto basta con editar `content.py` y volver a ejecutar el proceso (ver [generador/README.md](generador/README.md)).", ""]
open(os.path.join(R, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("README listo")
