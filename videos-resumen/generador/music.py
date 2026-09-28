# -*- coding: utf-8 -*-
"""Música motivadora original, sintetizada desde cero (sin samples ni derechos).

Estilo "uplifting corporate": pads supersaw, arpegio pluck con delay,
bajo pulsante con sidechain, batería electrónica suave, risers y golpe final.
La estructura se adapta a la duración de cada vídeo y el acorde final cae
exactamente en el instante indicado (hit_time).
"""
import numpy as np
import numba
import soundfile as sf
from scipy import signal as sg

SR = 44100
DEBUG = False


def m2f(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


# ───────────────────────────── DSP básico
@numba.njit(cache=True)
def svf(x, fc, q, mode):
    """Filtro de estado variable (Simper). mode 0=LP, 1=BP, 2=HP. fc por muestra."""
    y = np.empty_like(x)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(x.shape[0]):
        f = fc[i]
        if f > 0.45 * SR:
            f = 0.45 * SR
        if f < 10.0:
            f = 10.0
        g = np.tan(np.pi * f / SR)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = v1
        else:
            y[i] = x[i] - k * v1 - v2
    return y


def peq(x, f0, gain_db, q):
    """Ecualizador paramétrico (biquad RBJ)."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return sg.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def lp(x, fc, q=0.707):
    return svf(np.ascontiguousarray(x, dtype=np.float64), np.full(len(x), float(fc)), q, 0)


def hp(x, fc, q=0.707):
    return svf(np.ascontiguousarray(x, dtype=np.float64), np.full(len(x), float(fc)), q, 2)


def bp(x, fc, q=1.0):
    return svf(np.ascontiguousarray(x, dtype=np.float64), np.full(len(x), float(fc)), q, 1)


@numba.njit(cache=True)
def pingpong(xl, xr, d, fb, mix_out):
    n = xl.shape[0]
    bl = np.zeros(n)
    br = np.zeros(n)
    for i in range(n):
        dl = bl[i - d] if i >= d else 0.0
        dr = br[i - d] if i >= d else 0.0
        bl[i] = 0.5 * (xl[i] + xr[i]) + fb * dr
        br[i] = fb * dl
    return bl * mix_out, br * mix_out


_TBL = {}


def _saw_table(nh, N=2048):
    if nh not in _TBL:
        ph = np.arange(N) / N
        t = np.zeros(N)
        for k in range(1, nh + 1):
            t += np.sin(2 * np.pi * k * ph) / k
        _TBL[nh] = t * (2 / np.pi)
    return _TBL[nh]


def saw(f, n, phase0=0.0):
    """Diente de sierra de banda limitada (tabla aditiva, sin aliasing)."""
    nh = int(min(120, max(1, (SR * 0.45) // f)))
    tbl = _saw_table(nh)
    N = len(tbl)
    idx = ((phase0 + f * np.arange(n) / SR) % 1.0) * N
    i0 = idx.astype(np.int64)
    fr = idx - i0
    return tbl[i0 % N] * (1 - fr) + tbl[(i0 + 1) % N] * fr


def env_adsr(n_on, a, d, s, r):
    n = n_on + int(r * SR)
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    if n_on < n:
        level = e[min(n_on, n - 1)]
        tr = (np.arange(n - n_on)) / SR
        e[n_on:] = level * np.exp(-tr / max(r / 4.0, 1e-4))
    return e


class Rng:
    def __init__(self, seed):
        self.g = np.random.default_rng(seed)


# ───────────────────────────── instrumentos
def pad_note(R, midi, dur, cutoff, rel=1.4):
    f0 = m2f(midi)
    n_on = int(dur * SR)
    e = env_adsr(n_on, 0.35, 0.8, 0.85, rel)
    n = len(e)
    L = np.zeros(n)
    Rr = np.zeros(n)
    det = (-0.13, -0.06, 0.0, 0.06, 0.13)
    for i, dt in enumerate(det):
        v = saw(f0 * 2 ** (dt / 12), n, R.g.random())
        pan = (i / (len(det) - 1)) * 2 - 1
        L += v * np.sqrt(0.5 * (1 - 0.85 * pan))
        Rr += v * np.sqrt(0.5 * (1 + 0.85 * pan))
    fc = cutoff * (0.55 + 0.45 * e)
    return svf(L * e, fc, 0.8, 0) * 0.2, svf(Rr * e, fc, 0.8, 0) * 0.2


def pluck_note(R, midi, bright=1.0, length=0.9):
    f = m2f(midi)
    n = int(length * SR)
    t = np.arange(n) / SR
    v = 0.5 * saw(f * 2 ** (0.08 / 12), n, R.g.random()) + 0.5 * saw(f * 2 ** (-0.08 / 12), n, R.g.random())
    v += 0.25 * np.sin(2 * np.pi * f * t)
    fc = 350 + 5200 * bright * np.exp(-t / 0.085)
    amp = (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.26)
    return svf(v * amp, fc, 1.1, 0) * 0.55


def bass_note(R, midi, dur):
    f = m2f(midi)
    n = int((dur + 0.05) * SR)
    t = np.arange(n) / SR
    v = 0.75 * np.sin(2 * np.pi * f * t) + 0.4 * saw(f, n, R.g.random())
    fc = 220 + 1100 * np.exp(-t / 0.05)
    amp = np.minimum(1, t / 0.004) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.015))
    y = svf(v * amp, fc, 0.9, 0)
    return np.tanh(1.6 * y) / np.tanh(1.6) * 0.55


def bell_note(R, midi, length=2.2):
    f = m2f(midi)
    n = int(length * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ratio, a, d in ((1.0, 1.0, 1.1), (2.0, 0.42, 0.7), (3.01, 0.2, 0.45), (4.18, 0.12, 0.3), (5.43, 0.07, 0.2)):
        y += a * np.sin(2 * np.pi * f * ratio * t + R.g.random() * 6.28) * np.exp(-t / d)
    return y * np.minimum(1, t / 0.0015) * 0.28


def kick(R):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 46 + 115 * np.exp(-t / 0.032)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    click = hp(R.g.standard_normal(n) * np.exp(-t / 0.0025), 1800) * 0.25
    return np.tanh(1.7 * (y + click)) * 0.8


def clap(R):
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    e = np.zeros(n)
    for d in (0.0, 0.010, 0.021):
        e += (t >= d) * np.exp(-np.maximum(t - d, 0) / 0.007)
    e += (t >= 0.03) * np.exp(-np.maximum(t - 0.03, 0) / 0.12) * 0.7
    return bp(R.g.standard_normal(n), 1300, 0.9) * e * 0.55


def snare(R, vel=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.5
    nz = bp(R.g.standard_normal(n), 3000, 0.7) * np.exp(-t / 0.09)
    return (tone + nz) * 0.45 * vel


def hat(R, open_=False):
    n = int((0.4 if open_ else 0.09) * SR)
    t = np.arange(n) / SR
    y = hp(R.g.standard_normal(n), 7800) * np.exp(-t / (0.13 if open_ else 0.022))
    return y * (0.2 if open_ else 0.24)


def shaker(R):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return bp(R.g.standard_normal(n), 7000, 1.2) * np.sin(np.pi * np.minimum(t / 0.06, 1)) * 0.12


def crash(R, length=3.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    y = hp(R.g.standard_normal(n), 4500) * np.exp(-t / 0.95)
    y += hp(R.g.standard_normal(n), 9000) * np.exp(-t / 0.35) * 0.6
    return y * 0.16


def riser(R, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = t / length
    fc = 300 * (9000 / 300) ** x
    y = svf(R.g.standard_normal(n), fc, 2.0, 1) * (x ** 2.2) * 0.35
    return y


def boom(R, length=2.8):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 34 + 40 * np.exp(-t / 0.12)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    y += lp(R.g.standard_normal(n), 900) * np.exp(-t / 0.25) * 0.5
    return np.tanh(1.5 * y) * 0.7


def reverb_ir(R, rt60=2.2, length=3.0, pre=0.02):
    n = int(length * SR)
    t = np.arange(n) / SR
    out = []
    for ch in range(2):
        nz = R.g.standard_normal(n)
        # amortiguación de agudos progresiva: mezcla de ruido filtrado
        bright = lp(nz, 7000)
        dark = lp(nz, 1800)
        w = np.exp(-t / 0.5)
        ir = (bright * w + dark * (1 - w)) * np.exp(-6.9 * t / rt60)
        ir[: int(pre * SR)] = 0
        out.append(ir / np.sqrt(np.sum(ir ** 2)))
    return out


# ───────────────────────────── composición
KEYS = {"C": 36, "D": 38, "Eb": 39, "E": 40, "F": 41, "G": 43, "A": 45}
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def chord_tones(key_root, degree):
    """degree 1..7 → (raíz, tercera, quinta) en semitonos relativos a key_root."""
    i = degree - 1
    r = MAJOR[i]
    third = MAJOR[(i + 2) % 7] + (12 if i + 2 >= 7 else 0)
    fifth = MAJOR[(i + 4) % 7] + (12 if i + 4 >= 7 else 0)
    return key_root + r, key_root + third, key_root + fifth


class Mix:
    def __init__(self, n):
        self.buses = {}
        self.n = n

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((2, self.n))
        return self.buses[name]

    def add(self, name, x, t, gain=1.0, pan=0.0):
        b = self.bus(name)
        a = int(round(t * SR))
        if a >= self.n:
            return
        if x.ndim == 1:
            l = x * np.sqrt(0.5 * (1 - pan)) * np.sqrt(2)
            r = x * np.sqrt(0.5 * (1 + pan)) * np.sqrt(2)
        else:
            l, r = x
        m = min(len(l), self.n - a)
        b[0, a:a + m] += l[:m] * gain
        b[1, a:a + m] += r[:m] * gain


ARP = [0, 2, 3, 4, 3, 2, 1, 2, 0, 2, 3, 5, 4, 3, 2, 1]


def compose(duration, hit_time, key="D", prog=(1, 5, 6, 4), seed=1):
    R = Rng(seed)
    # tempo ajustado para que el golpe final caiga al inicio de un compás
    best = None
    for bars in range(20, 90):
        bpm = 240.0 * bars / hit_time
        if 112 <= bpm <= 126:
            cand = (abs(bpm - 120), bars, bpm)
            best = cand if best is None or cand < best else best
    _, NB, bpm = best
    bar = 240.0 / bpm
    beat = bar / 4
    s16 = beat / 4
    n = int((duration + 0.5) * SR)
    M = Mix(n)
    kr = KEYS[key]

    a_end = max(6, int(round(NB * 0.30)))
    c_end = max(a_end + 6, int(round(NB * 0.62)))

    def section(b):
        if b < 2:
            return "intro"
        if b < a_end:
            return "A"
        if b < a_end + 2:
            return "B"
        if b < c_end:
            return "C"
        if b < c_end + 4:
            return "D"
        if b < NB - 2:
            return "E"
        return "F"

    kicks = []
    for b in range(NB):
        sec = section(b)
        t0 = b * bar
        deg = prog[b % len(prog)]
        r, th, fi = chord_tones(kr, deg)
        # ── pad
        cutoff = {"intro": 900, "A": 1700, "B": 2400, "C": 2600, "D": 1500, "E": 2900, "F": 3200}[sec]
        voicing = [r + 12, fi + 12, th + 24, r + 24]
        for m in voicing:
            L, Rr = pad_note(R, m, bar * 1.02, cutoff)
            M.add("pad", np.stack([L, Rr]), t0, 1.0)
        # ── arpegio pluck
        if not (sec == "intro" and b == 0):
            tones = [r + 24, th + 24, fi + 24, r + 36, th + 36, fi + 36]
            bright = {"intro": 0.35, "A": 0.6, "B": 0.75, "C": 0.95, "D": 0.5, "E": 1.0, "F": 1.0}[sec]
            g = {"intro": 0.55, "A": 0.8, "B": 0.85, "C": 1.0, "D": 0.8, "E": 1.0, "F": 1.0}[sec]
            for k in range(16):
                vel = 1.0 if k % 4 == 0 else (0.78 if k % 2 == 0 else 0.62)
                M.add("pluck", pluck_note(R, tones[ARP[k] % len(tones)], bright), t0 + k * s16, g * vel,
                      pan=0.25 * np.sin(k * 0.7))
        # ── bajo
        if sec in ("A", "C", "E", "F"):
            pat = [0, 0, 12, 0, 0, 0, 12, 0] if sec in ("C", "E", "F") else [0, 0, 0, 0, 0, 0, 0, 0]
            root_b = r if r - kr < 7 else r - 12
            for k in range(8):
                M.add("bass", bass_note(R, root_b + pat[k], s16 * 1.7), t0 + k * 2 * s16, 1.0)
        # ── batería
        if sec in ("A", "C", "E") or (sec == "F" and b == NB - 2):
            for k in range(4):
                M.add("drums", kick(R), t0 + k * beat, 1.0)
                kicks.append(t0 + k * beat)
            for k in range(4):
                M.add("drums", hat(R, open_=sec in ("C", "E")), t0 + k * beat + beat / 2, 0.9, pan=0.2)
            if sec in ("C", "E") or (sec == "A" and b >= 6):
                for k in (1, 3):
                    M.add("drums", clap(R), t0 + k * beat, 0.9)
            if sec in ("C", "E"):
                for k in range(16):
                    M.add("drums", shaker(R), t0 + k * s16 + (0.012 if k % 2 else 0), 0.9 if k % 4 == 2 else 0.6, pan=-0.3)
        if sec == "B" or (sec == "F"):
            # redoble de caja creciente
            steps = 8 if (b % 2 == 0) else 16
            for k in range(steps):
                tt = t0 + k * bar / steps
                prog_in = (tt - (t0 - (bar if b % 2 else 0))) / (2 * bar)
                M.add("drums", snare(R, 0.3 + 0.7 * min(1, max(0, prog_in))), tt, 0.8)
        # ── campanas en estribillos
        if sec in ("C", "E") and b % 2 == 0:
            for j, m in enumerate([fi + 36, th + 36, r + 36]):
                M.add("bell", bell_note(R, m), t0 + j * beat * 0.5 + beat * 2, 0.55 - 0.1 * j, pan=0.3 - 0.3 * j)
        # ── transiciones
        if b in (a_end, c_end + 4) or b == 2:
            M.add("drums", crash(R), t0, 0.9)
        if b == a_end + 1 or b == c_end + 3 or b == NB - 1:
            L = riser(R, bar)
            M.add("fx", L, t0, 0.7)

    # ── inicio: golpe grave + brillo
    M.add("fx", boom(R), 0.05, 0.8)
    M.add("drums", crash(R, 3.0), 0.05, 0.6)
    # ── final: acorde de tónica largo, golpe, platillo y arpegio de campanas
    th_t = NB * bar
    r, th, fi = chord_tones(kr, 1)
    for m in [r + 12, fi + 12, th + 24, r + 24, fi + 24]:
        L, Rr = pad_note(R, m, 1.2, 3000, rel=3.0)
        M.add("pad", np.stack([L, Rr]), th_t, 1.15)
    M.add("drums", kick(R), th_t, 1.1)
    M.add("drums", crash(R, 4.0), th_t, 1.0)
    M.add("fx", boom(R, 3.5), th_t, 0.9)
    M.add("bass", bass_note(R, r if r - kr < 7 else r - 12, 1.6), th_t, 1.0)
    for j, m in enumerate([r + 36, th + 36, fi + 36, r + 48, th + 48]):
        M.add("bell", bell_note(R, m, 3.0), th_t + j * s16, 0.55, pan=-0.4 + 0.2 * j)

    # ── sidechain (bombeo) a partir de los bombos
    pump = np.ones(n)
    tt = np.arange(n) / SR
    for kt in kicks:
        a = int(kt * SR)
        m = min(n - a, int(beat * SR))
        seg = tt[a:a + m] - kt
        pump[a:a + m] = np.minimum(pump[a:a + m], 1 - 0.55 * np.exp(-seg / 0.11))
    for name, depth in (("pad", 1.0), ("bass", 1.0), ("pluck", 0.5)):
        b = M.bus(name)
        b *= 1 - depth * (1 - pump)

    # ── efectos: delay ping-pong y reverb
    d = int(beat * 0.75 * SR)
    pl = M.bus("pluck")
    dl, dr = pingpong(pl[0].copy(), pl[1].copy(), d, 0.38, 0.5)
    pl[0] += lp(dl, 4000)
    pl[1] += lp(dr, 4000)
    be = M.bus("bell")
    dl, dr = pingpong(be[0].copy(), be[1].copy(), d, 0.35, 0.45)
    be[0] += dl
    be[1] += dr

    irL, irR = reverb_ir(R, rt60=2.4)
    send = (M.bus("pad") * 0.35 + M.bus("pluck") * 0.3 + M.bus("bell") * 0.5 + M.bus("drums") * 0.08 + M.bus("fx") * 0.4)
    rv = np.stack([sg.fftconvolve(send[0], irL)[:n], sg.fftconvolve(send[1], irR)[:n]])

    gains = {"pad": 0.5, "pluck": 0.74, "bass": 0.6, "drums": 0.65, "bell": 0.95, "fx": 0.6}
    stems = {name: M.bus(name) * g for name, g in gains.items()}
    stems["reverb"] = rv * 0.36
    if DEBUG:
        for k, v in stems.items():
            print(f"   stem {k:7s} rms {20*np.log10(np.sqrt(np.mean(v**2))+1e-12):6.1f} dB  peak {np.abs(v).max():.2f}")
    out = sum(stems.values())
    out[0] = hp(out[0], 28)
    out[1] = hp(out[1], 28)
    # EQ de "hueco para la voz": -3 dB en 2,5 kHz y suavizado de agudos
    out = np.stack([peq(out[0], 2500, -3.0, 0.9), peq(out[1], 2500, -3.0, 0.9)])
    out = np.stack([lp(out[0], 13000), lp(out[1], 13000)])
    # nivel previo a la saturación suave (percentil 99.9 → 0.75)
    ref = np.percentile(np.abs(out), 99.9)
    out *= 0.75 / max(ref, 1e-9)
    out = np.tanh(out)
    fade = np.clip((duration - tt) / 0.8, 0, 1)
    out *= fade
    out = out[:, : int(duration * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.89
    info = {"bpm": bpm, "bars": NB, "bar": bar, "hit": th_t}
    return out.astype(np.float32), info


if __name__ == "__main__":
    import sys, time
    DEBUG = True
    t = time.time()
    y, info = compose(122.0, 117.0, key="D", prog=(1, 5, 6, 4), seed=3)
    sf.write(sys.argv[1] if len(sys.argv) > 1 else "music_test.wav", y.T, SR)
    print(info, f"{time.time()-t:.1f}s")
