import sys, numpy as np, soundfile as sf, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
x, sr = sf.read(sys.argv[1]); out = sys.argv[2]
m = x.mean(1) if x.ndim > 1 else x
fig, ax = plt.subplots(3, 1, figsize=(16, 10), gridspec_kw={"height_ratios": [1, 2, 1]})
t = np.arange(len(m)) / sr
ax[0].plot(t[::20], m[::20], lw=0.3); ax[0].set_xlim(0, t[-1]); ax[0].set_title("waveform")
ax[1].specgram(m, NFFT=4096, Fs=sr, noverlap=2048, cmap="magma", vmin=-120); ax[1].set_ylim(0, 12000); ax[1].set_title("spectrogram")
w = int(0.5 * sr); rms = [20*np.log10(np.sqrt(np.mean(m[i:i+w]**2))+1e-9) for i in range(0, len(m)-w, w)]
ax[2].plot(np.arange(len(rms))*0.5, rms); ax[2].set_ylim(-60, 0); ax[2].grid(); ax[2].set_title("RMS dBFS (0.5 s)")
plt.tight_layout(); plt.savefig(out, dpi=60)
if x.ndim > 1:
    c = np.corrcoef(x[:,0], x[:,1])[0,1]; print("stereo corr", round(c,3))
print("peak", np.abs(x).max().round(3), "rms dB", round(20*np.log10(np.sqrt(np.mean(m**2))),1), "dc", m.mean().round(5))
