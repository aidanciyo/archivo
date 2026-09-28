import json, sys, subprocess, numpy as np, soundfile as sf, io
sys.argv_saved = list(sys.argv)
from narration import Engine, wer
vid = sys.argv_saved[1]
tl = json.load(open(f"out/{vid}/timeline.json", encoding="utf-8"))
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f"out/{vid}/{vid}.mp4", "-map", "0:a", "-ac", "1", "-ar", "44100", "-f", "wav", "-"], capture_output=True).stdout
x, sr = sf.read(io.BytesIO(raw), dtype="float32")
eng = Engine()
errs, words = 0.0, 0
for ln in tl["lines"]:
    a, b = int((ln["start"] - 0.05) * sr), int((ln["end"] + 0.1) * sr)
    hyp = eng.transcribe(x[a:b])
    e = wer(ln["text"], hyp); n = len(ln["text"].split())
    errs += e * n; words += n
    if e > 0.2: print(f"  [{ln['start']:6.1f}] WER {e:.2f} | {ln['text']}\n           -> {hyp}")
print(f"{vid}: WER global sobre el audio final (voz + música) = {errs/words:.3f} ({words} palabras)")
