"""Tiny synth for Greek-flavoured lyre jingles (Karplus-Strong) and paper SFX."""
import numpy as np
from scipy.signal import fftconvolve, lfilter

SR = 48000

# D dorian-ish scale (the ancient "Phrygian" mode) -> sounds Greek, calm
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def freq(name):
    """'A4', 'D5', 'F#4'."""
    n, rest = name[0], name[1:]
    acc = 0
    if rest.startswith("#"):
        acc, rest = 1, rest[1:]
    elif rest.startswith("b"):
        acc, rest = -1, rest[1:]
    octave = int(rest)
    semis = NOTE[n] + acc + (octave - 4) * 12
    return 440.0 * 2 ** (semis / 12)


def pluck(f, dur=2.5, bright=0.6, decay=0.9965, seed=0):
    rng = np.random.default_rng(seed)
    N = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, N)
    # soften the excitation (a finger, not a pick)
    for _ in range(int((1 - bright) * 6) + 1):
        buf = 0.5 * (buf + np.roll(buf, 1))
    buf -= buf.mean()
    n = int(dur * SR)
    out = np.empty(n)
    reps = n // N + 1
    blocks = []
    for _ in range(reps):
        blocks.append(buf.copy())
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    out = np.concatenate(blocks)[:n]
    # body resonance: gentle low-pass + a touch of the octave
    out = lfilter([0.35, 0.35], [1, -0.3], out)
    env = np.minimum(1, np.arange(n) / (0.004 * SR))
    return out * env


def reverb(x, secs=1.6, mix=0.28, seed=3):
    rng = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4.2)
    ir = lfilter([0.2], [1, -0.8], ir)  # darker tail
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return (1 - mix) * dry + mix * wet * 0.9


def sequence(events, length=None):
    """events: list of (time_s, note, dur, vel)."""
    end = max(t + d for t, _, d, _ in events) + 0.2
    length = length or end
    out = np.zeros(int(length * SR) + SR)
    for i, (t, note, d, v) in enumerate(events):
        p = pluck(freq(note), d, seed=i) * v
        s = int(t * SR)
        out[s:s + len(p)] += p[: len(out) - s]
    return out


JINGLES = {
    # opening: rising arpeggio + chord
    "intro": [(0.00, "D4", 2.6, .55), (0.18, "A4", 2.4, .5), (0.36, "D5", 2.2, .5), (0.54, "F5", 2.0, .45),
              (0.72, "E5", 1.8, .45), (0.95, "D5", 2.6, .5), (0.95, "A4", 2.6, .35), (0.95, "D4", 2.6, .35)],
    # section change: short motif
    "section": [(0.00, "A4", 1.8, .5), (0.16, "C5", 1.7, .45), (0.32, "D5", 1.6, .45), (0.52, "E5", 1.4, .45),
                (0.74, "D5", 1.8, .5), (0.74, "A4", 1.8, .3)],
    # key idea sparkle
    "idea": [(0.00, "D5", 1.2, .35), (0.10, "F5", 1.1, .32), (0.20, "A5", 1.2, .32)],
    # ending
    "outro": [(0.00, "A4", 2.0, .5), (0.2, "G4", 2.0, .45), (0.4, "F4", 2.0, .45), (0.6, "E4", 2.0, .45),
              (0.9, "D4", 3.0, .55), (0.9, "A4", 3.0, .35), (0.9, "D5", 3.0, .3)],
    # loop sting for the review video
    "loop": [(0.00, "D5", 1.0, .4), (0.12, "A4", 1.0, .35), (0.24, "D4", 1.4, .4)],
}


def jingle(name, gain=0.5):
    x = reverb(sequence(JINGLES[name]))
    x = x / (np.abs(x).max() + 1e-9) * gain
    # trim silence at the end
    nz = np.nonzero(np.abs(x) > 1e-4)[0]
    return x[: nz[-1] + 1] if len(nz) else x


def swoosh(dur=0.45, gain=0.12, seed=1):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    # sweep a simple one-pole low-pass
    out = np.zeros(n)
    y = 0.0
    for i in range(n):
        a = 0.02 + 0.25 * t[i]
        y += a * (x[i] - y)
        out[i] = y
    out = out * env
    return out / (np.abs(out).max() + 1e-9) * gain


def tap(gain=0.08, seed=2):
    rng = np.random.default_rng(seed)
    n = int(0.06 * SR)
    x = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.008 * SR))
    x = lfilter([0.3], [1, -0.7], x)
    return x / (np.abs(x).max() + 1e-9) * gain
