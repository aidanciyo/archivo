# -*- coding: utf-8 -*-
"""Orquesta la producción: página → mezcla → fotogramas (en paralelo) → MP4 final."""
import json, math, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FPS, WORKERS = 30, 3
TITLES = {"UT1": "Digitalización de los sectores productivos", "UT2": "Tecnologías digitales habilitadoras",
          "UT3": "Sistemas en la nube", "UT4": "Aplicación de la inteligencia artificial", "UT5": "Big data"}
env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH") or subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())

def produce(vid):
    t0 = time.time()
    subprocess.run([sys.executable, "make_pages.py", vid], check=True, cwd=HERE)
    subprocess.run([sys.executable, "mix.py", vid], check=True, cwd=HERE)
    tl = json.load(open(os.path.join(OUT, vid, "timeline.json"), encoding="utf-8"))
    N = math.ceil(tl["duration"] * FPS)
    fdir = os.path.join(OUT, vid, "frames")
    os.makedirs(fdir, exist_ok=True)
    bounds = [round(N * k / WORKERS) for k in range(WORKERS + 1)]
    procs = [subprocess.Popen(["node", "render.js", f"engine/{vid}.html", fdir, str(FPS), str(bounds[k]), str(bounds[k + 1])],
                              cwd=HERE, env=env) for k in range(WORKERS)]
    codes = [p.wait() for p in procs]
    have = len([f for f in os.listdir(fdir) if f.endswith(".jpg")])
    if any(codes) or have < N:
        raise SystemExit(f"{vid}: render incompleto ({have}/{N}, códigos {codes})")
    t1 = time.time()
    final = os.path.join(OUT, vid, f"{vid}.mp4")
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.jpg"),
           "-i", os.path.join(OUT, vid, "mix.wav"), "-i", os.path.join(OUT, vid, f"{vid}.srt"),
           "-map", "0:v", "-map", "1:a", "-map", "2:s",
           "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-x264-params", "aq-mode=3", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-c:s", "mov_text", "-metadata:s:s:0", "language=spa", "-metadata:s:a:0", "language=spa",
           "-metadata", f"title={vid} · {TITLES[vid]} (resumen)", "-metadata", "language=spa",
           "-movflags", "+faststart", final]
    subprocess.run(cmd, check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", final],
                               capture_output=True, text=True).stdout)
    if abs(dur - tl["duration"]) > 0.25:
        raise SystemExit(f"{vid}: duración {dur:.2f}s distinta de la esperada {tl['duration']:.2f}s (fotogramas conservados)")
    shutil.rmtree(fdir)
    mb = os.path.getsize(final) / 1e6
    print(f"== {vid} listo: {final} ({mb:.1f} MB) render {t1 - t0:.0f}s, encode {time.time() - t1:.0f}s", flush=True)

if __name__ == "__main__":
    for vid in (sys.argv[1].split(",") if len(sys.argv) > 1 else list(TITLES)):
        produce(vid)
