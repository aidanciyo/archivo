# -*- coding: utf-8 -*-
"""Genera la narración (Supertonic 3, voz masculina) de cada vídeo.

Para cada línea del guion: normaliza el texto para el TTS, sintetiza varias
tomas, las verifica con Whisper y conserva la mejor. Después monta la pista
de voz completa y un timeline.json con tiempos de escenas, líneas y marcas.
"""
import json, os, re, sys, unicodedata
import numpy as np
import soundfile as sf
import sherpa_onnx
import librosa

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = os.environ.get("TTS_MODELS", os.path.join(HERE, "..", "voices"))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
from content import VIDEOS

SR = 44100
SID = 6                 # voz masculina grave y expresiva
STEPS = 12
TAKES = 4

# ───────────────────────────── normalización de texto para el TTS
_U = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
      "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve",
      "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis",
      "veintisiete", "veintiocho", "veintinueve"]
_T = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_H = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
      6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def num_es(n: int) -> str:
    if n < 30:
        return _U[n]
    if n < 100:
        t, u = divmod(n, 10)
        return _T[t] + ("" if u == 0 else " y " + _U[u])
    if n < 1000:
        h, r = divmod(n, 100)
        if n == 100:
            return "cien"
        return _H[h] + ("" if r == 0 else " " + num_es(r))
    if n < 1_000_000:
        k, r = divmod(n, 1000)
        head = "mil" if k == 1 else num_es(k).replace("uno", "un") + " mil"
        return head + ("" if r == 0 else " " + num_es(r))
    raise ValueError(n)


REPL = [
    (r"\b4\.0\b", "cuatro punto cero"),
    (r"\b5G\b", "cinco ge"),
    (r"\b4G\b", "cuatro ge"),
    (r"\b3D\b", "tres de"),
    (r"\bXVIII\b", "dieciocho"),
    (r"…", "..."),
]


def tts_text(s: str) -> str:
    for a, b in REPL:
        s = re.sub(a, b, s)
    s = re.sub(r"\d+", lambda m: num_es(int(m.group())), s)
    return s


MARK = re.compile(r"\{([A-Za-z0-9_]+)\}")


def split_marks(s: str):
    """Devuelve (texto_sin_marcas, [(clave, posición_relativa)])."""
    marks, clean, pos = [], [], 0
    for m in MARK.finditer(s):
        clean.append(s[pos:m.start()])
        marks.append((m.group(1), sum(len(c) for c in clean)))
        pos = m.end()
    clean.append(s[pos:])
    text = "".join(clean)
    n = max(1, len(text))
    return text, [(k, p / n) for k, p in marks]


# ───────────────────────────── ASR para verificar cada toma
def norm_words(s):
    s = tts_text(s).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9ñ ]", " ", s)
    return s.split()


def wer(ref, hyp):
    r, h = norm_words(ref), norm_words(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), dtype=int)
    d[:, 0] = range(len(r) + 1)
    d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1, -1] / max(1, len(r))


class Engine:
    def __init__(self):
        d = os.path.join(VOICES, "sherpa-onnx-supertonic-3-tts-int8-2026-05-11")
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
                duration_predictor=f"{d}/duration_predictor.int8.onnx", text_encoder=f"{d}/text_encoder.int8.onnx",
                vector_estimator=f"{d}/vector_estimator.int8.onnx", vocoder=f"{d}/vocoder.int8.onnx",
                tts_json=f"{d}/tts.json", unicode_indexer=f"{d}/unicode_indexer.bin", voice_style=f"{d}/voice.bin"),
            num_threads=4, provider="cpu"))
        self.tts = sherpa_onnx.OfflineTts(cfg)
        w = os.path.join(VOICES, "sherpa-onnx-whisper-small")
        self.asr = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=f"{w}/small-encoder.int8.onnx", decoder=f"{w}/small-decoder.int8.onnx",
            tokens=f"{w}/small-tokens.txt", language="es", task="transcribe", num_threads=4)

    def synth(self, text, speed):
        gc = sherpa_onnx.GenerationConfig()
        gc.sid, gc.speed, gc.num_steps = SID, speed, STEPS
        gc.extra["lang"] = "es"
        a = self.tts.generate(text, gc)
        x = np.asarray(a.samples, dtype=np.float32)
        if a.sample_rate != SR:
            x = librosa.resample(x, orig_sr=a.sample_rate, target_sr=SR)
        return trim(x)

    def transcribe(self, x):
        y = librosa.resample(x, orig_sr=SR, target_sr=16000)
        s = self.asr.create_stream()
        s.accept_waveform(16000, y)
        self.asr.decode_stream(s)
        return s.result.text.strip()


def trim(x, thr_db=-42, pad=0.04):
    hop = 256
    rms = librosa.feature.rms(y=x, frame_length=1024, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-9)
    idx = np.where(db > thr_db)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] * hop - int(pad * SR))
    b = min(len(x), (idx[-1] + 1) * hop + int(pad * SR * 2))
    y = x[a:b].copy()
    f = int(0.01 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    return y


def gap_after(text, same_scene):
    if not same_scene:
        return 0.80
    t = text.rstrip()
    if t.endswith("?"):
        return 0.40
    if t.endswith("!"):
        return 0.40
    return 0.28


def build(video, eng, speed, cache):
    vid = video["id"]
    os.makedirs(os.path.join(OUT, vid, "lines"), exist_ok=True)
    lines = []
    for si, sc in enumerate(video["scenes"]):
        for li, raw in enumerate(sc["lines"]):
            disp, marks = split_marks(raw)
            say = tts_text(disp)
            key = f"{speed:.3f}|{say}"
            path = os.path.join(OUT, vid, "lines", f"s{si:02d}_l{li:02d}.wav")
            if key in cache and os.path.exists(path):
                info = cache[key]
            else:
                best = None
                for take in range(TAKES):
                    x = eng.synth(say, speed)
                    hyp = eng.transcribe(x)
                    e = wer(say, hyp)
                    cand = (e, take, x, hyp)
                    if best is None or e < best[0] - 1e-9:
                        best = cand
                    if e == 0:
                        break
                e, take, x, hyp = best
                sf.write(path, x, SR)
                info = {"wer": round(float(e), 3), "hyp": hyp, "dur": len(x) / SR}
                cache[key] = info
            lines.append({"scene": si, "line": li, "text": disp, "say": say, "marks": marks,
                          "path": path, **info})
            flag = "  <-- revisar" if info["wer"] > 0.12 else ""
            print(f"  {vid} s{si} l{li} {info['dur']:5.2f}s wer={info['wer']:.2f}{flag}", flush=True)
    return lines


def assemble(video, lines, lead_in=1.0, tail=4.2):
    t = lead_in
    for i, ln in enumerate(lines):
        ln["start"] = round(t, 3)
        ln["end"] = round(t + ln["dur"], 3)
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        t = ln["end"] + (gap_after(ln["text"], nxt is not None and nxt["scene"] == ln["scene"]) if nxt else 0)
        if nxt is not None and ln["scene"] == 0 and nxt["scene"] == 1:
            t = max(t, 5.6)  # la portada se ve al menos ~5 s
    total = lines[-1]["end"] + tail
    return total


def write_outputs(video, lines, total):
    vid = video["id"]
    n = int(round(total * SR))
    track = np.zeros(n, dtype=np.float32)
    for ln in lines:
        x, _ = sf.read(ln["path"], dtype="float32")
        a = int(round(ln["start"] * SR))
        track[a:a + len(x)] += x[: max(0, n - a)]
    peak = np.abs(track).max()
    track *= 0.89 / max(peak, 1e-6)
    sf.write(os.path.join(OUT, vid, "narration.wav"), track, SR)

    scenes = []
    for si, sc in enumerate(video["scenes"]):
        ls = [ln for ln in lines if ln["scene"] == si]
        scenes.append({"index": si, "type": sc["type"], "first": ls[0]["start"], "last": ls[-1]["end"]})
    for i, s in enumerate(scenes):
        s["start"] = 0.0 if i == 0 else round(s["first"] - 0.55, 3)
    for i, s in enumerate(scenes):
        s["end"] = round(scenes[i + 1]["start"], 3) if i + 1 < len(scenes) else round(total, 3)
    cues = {}
    for ln in lines:
        for k, r in ln["marks"]:
            cues.setdefault(str(ln["scene"]), {})[k] = round(ln["start"] + r * ln["dur"], 3)
    tl = {"id": vid, "duration": round(total, 3), "scenes": scenes, "cues": cues,
          "lines": [{k: ln[k] for k in ("scene", "line", "text", "start", "end")} for ln in lines]}
    with open(os.path.join(OUT, vid, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    return tl


if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else [v["id"] for v in VIDEOS]
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.1
    os.makedirs(OUT, exist_ok=True)
    cpath = os.path.join(OUT, "tts_cache.json")
    cache = json.load(open(cpath)) if os.path.exists(cpath) else {}
    eng = Engine()
    for v in VIDEOS:
        if v["id"] not in ids:
            continue
        print(f"== {v['id']} (speed {speed})", flush=True)
        lines = build(v, eng, speed, cache)
        json.dump(cache, open(cpath, "w"), ensure_ascii=False, indent=0)
        total = assemble(v, lines)
        tl = write_outputs(v, lines, total)
        words = sum(len(ln["text"].split()) for ln in lines)
        print(f"== {v['id']}: {words} palabras, duración total {total:.1f}s", flush=True)
