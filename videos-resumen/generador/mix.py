# -*- coding: utf-8 -*-
"""Mezcla final: voz procesada + música original con ducking + efectos + subtítulos SRT."""
import json, os, re, sys
import numpy as np, numba, soundfile as sf, pyloudnorm as pyln
from scipy import signal as sg
from music import compose, SR, svf, peq, hp, lp, bp, reverb_ir, Rng

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
STYLE = {  # tonalidad, progresión y semilla: misma instrumentación para todos (estilo unificado)
    "UT1": ("D", (1, 5, 6, 4), 11), "UT2": ("C", (6, 4, 1, 5), 22), "UT3": ("F", (1, 6, 4, 5), 33),
    "UT4": ("G", (4, 1, 5, 6), 44), "UT5": ("Eb", (1, 3, 6, 4), 55)}


def shelf_hi(x, f0, gain_db, S=0.8):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; cw, sw = np.cos(w0), np.sin(w0)
    al = sw / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2)
    b = [A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * al)]
    a = [(A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * al]
    return sg.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


@numba.njit(cache=True)
def follower(x, att, rel):
    y = np.empty_like(x); e = 0.0
    aa = np.exp(-1.0 / (att * SR)); ar = np.exp(-1.0 / (rel * SR))
    for i in range(x.shape[0]):
        v = x[i]
        c = aa if v > e else ar
        e = c * e + (1 - c) * v
        y[i] = e
    return y


def compress(x, thr_db=-24, ratio=3.0, att=0.004, rel=0.12):
    env = np.sqrt(follower(x * x, att, rel) + 1e-12)
    lvl = 20 * np.log10(env + 1e-9)
    over = np.maximum(0, lvl - thr_db)
    gain_db = -over * (1 - 1 / ratio)
    return x * 10 ** (gain_db / 20)


def voice_chain(v):
    v = hp(v, 75)
    v = peq(v, 260, -2.0, 1.0)
    v = peq(v, 3300, 2.5, 0.9)
    v = shelf_hi(v, 9500, 1.5)
    v = compress(v, -26, 3.0)
    R = Rng(5)
    irL, irR = reverb_ir(R, rt60=0.45, length=0.6, pre=0.008)
    wet = sg.fftconvolve(v, irL)[: len(v)] * 0.05
    return v + wet


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def whoosh(R, length=0.8):
    n = int(length * SR); t = np.arange(n) / SR; k = t / length
    fc = 350 + 3800 * np.sin(np.pi * np.clip(k * 1.1, 0, 1)) ** 1.5
    y = svf(R.g.standard_normal(n), fc, 1.4, 1)
    env = np.sin(np.pi * k) ** 1.6
    y *= env
    pan = -0.8 + 1.6 * k
    return np.stack([y * np.sqrt(0.5 * (1 - pan)), y * np.sqrt(0.5 * (1 + pan))]) * 0.5


def pop(R, f=1150.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    ff = f * (1 + 0.5 * np.exp(-t / 0.01))
    y = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.03) * np.minimum(1, t / 0.002)
    return y * 0.5


def add(buf, x, t, g=1.0):
    a = int(round(t * SR))
    if a >= buf.shape[1]:
        return
    if x.ndim == 1:
        x = np.stack([x, x]) / np.sqrt(2)
    m = min(x.shape[1], buf.shape[1] - a)
    buf[:, a:a + m] += x[:, :m] * g


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


FUNC = {"la", "el", "de", "y", "a", "en", "los", "las", "del", "que", "o", "un", "una", "con", "por", "al", "se", "su", "sus", "lo", "e", "tu", "te"}


def wrap2(s, width=46):
    """Parte en dos líneas equilibradas, prefiriendo cortes tras puntuación y evitando dejar colgada una palabra corta."""
    if len(s) <= width:
        return s
    mid = len(s) / 2
    best = None
    for i, c in enumerate(s):
        if c != " ":
            continue
        prev = s[:i].split()[-1].lower().strip(",.;:¿?¡!")
        score = abs(i - mid)
        if s[i - 1] in ",;:":
            score -= 8
        if prev in FUNC:
            score += 12
        if best is None or score < best[0]:
            best = (score, i)
    i = best[1]
    return s[:i] + "\n" + s[i + 1:]


def make_srt(tl, path):
    ev = []
    for ln in tl["lines"]:
        txt, a, b = ln["text"], ln["start"], ln["end"]
        chunks = [txt]
        if len(txt) > 90:
            parts = re.split(r"(?<=[,;:])\s+", txt)
            chunks, cur = [], ""
            for p in parts:
                if cur and len(cur) + 1 + len(p) > 84:
                    chunks.append(cur); cur = p
                else:
                    cur = (cur + " " + p).strip()
            if cur:
                chunks.append(cur)
        tot = sum(len(c) for c in chunks); t = a
        for c in chunks:
            d = (b - a) * len(c) / tot
            ev.append([t, t + d, wrap2(c)])
            t += d
    for i, e in enumerate(ev):   # alarga un poco cada bloque sin solaparlo con el siguiente
        nxt = ev[i + 1][0] if i + 1 < len(ev) else e[1] + 1
        e[1] = min(e[1] + 0.15, nxt - 0.03)
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, c) in enumerate(ev, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n\n")


def mix(vid):
    tl = json.load(open(os.path.join(OUT, vid, "timeline.json"), encoding="utf-8"))
    D = tl["duration"]; n = int(round(D * SR))
    hit = tl["lines"][-1]["end"] + 0.15
    v, _ = sf.read(os.path.join(OUT, vid, "narration.wav"), dtype="float64")
    v = np.pad(v, (0, max(0, n - len(v))))[:n]
    v = voice_chain(v)
    # nivel de voz: RMS de las partes habladas → -19 dBFS
    env = np.sqrt(follower(v * v, 0.01, 0.2) + 1e-12)
    active = env > 10 ** (-45 / 20)
    v *= 10 ** ((-19 - rms_db(v[active])) / 20)
    key, prog, seed = STYLE[vid]
    m, info = compose(D, hit, key=key, prog=prog, seed=seed)
    m = m.astype(np.float64)[:, :n]
    m = np.pad(m, ((0, 0), (0, n - m.shape[1])))
    m *= 10 ** ((-22 - rms_db(m)) / 20)
    # ducking: la música baja 12 dB cuando habla el narrador
    venv = np.sqrt(follower(v * v, 0.03, 0.45) + 1e-12)
    act = np.clip((20 * np.log10(venv + 1e-9) + 44) / 12, 0, 1)
    act = follower(act, 0.06, 0.5)
    m *= 10 ** ((-12 * act) / 20)
    # efectos
    fx = np.zeros((2, n)); R = Rng(99)
    for s in tl["scenes"][1:]:
        add(fx, whoosh(R), s["start"] - 0.4, 1.0)
    for si, cues in tl["cues"].items():
        for k, t in cues.items():
            if re.fullmatch(r"\d+|c\d+|p\d+", k):
                add(fx, pop(R, 1000 + 90 * (int(re.sub(r"\D", "", k)) % 5)), t, 1.0)
    fx *= 10 ** ((-34 - rms_db(fx[fx != 0]) if np.any(fx) else 0) / 20)
    out = m + fx + np.stack([v, v])
    # normalización a -16 LUFS y limitador suave
    meter = pyln.Meter(SR)
    L = meter.integrated_loudness(out.T)
    out *= 10 ** ((-16 - L) / 20)
    pk = np.abs(out).max()
    if pk > 0.89:
        out = np.tanh(out / 0.89) * 0.89
    sf.write(os.path.join(OUT, vid, "mix.wav"), out.T.astype(np.float32), SR, subtype="PCM_24")
    make_srt(tl, os.path.join(OUT, vid, f"{vid}.srt"))
    L2 = meter.integrated_loudness(out.T)
    print(f"{vid}: dur {D:.2f}s  bpm {info['bpm']:.1f}  hit {info['hit']:.2f}  LUFS {L2:.1f}  peak {np.abs(out).max():.2f}", flush=True)


if __name__ == "__main__":
    for vid in (sys.argv[1].split(",") if len(sys.argv) > 1 else list(STYLE)):
        mix(vid)
