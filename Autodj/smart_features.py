# smart_features.py
import numpy as np, librosa
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BandTimeline:
    t: np.ndarray               # times (sec)
    energy_low: np.ndarray
    energy_mid: np.ndarray
    energy_high: np.ndarray
    vocal_likelihood: np.ndarray
    high_transients: np.ndarray
    brightness: float           # global spectral centroid (0..1)


def _band_energy(S, freqs, fmin, fmax):
    mask = (freqs >= fmin) & (freqs < fmax)
    if not np.any(mask):
        return np.zeros(S.shape[1])
    return S[mask].mean(axis=0)


def analyze_bands(path: str, sr: int = 22050, hop_length: int = 512) -> BandTimeline:
    y, sr = librosa.load(path, sr=sr, mono=True)
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop_length))**2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop_length)

    # band energies
    e_low  = _band_energy(S, freqs, 20, 150)
    e_mid  = _band_energy(S, freqs, 300, 3400)
    e_high = _band_energy(S, freqs, 6000, 16000)

    # normalize per-track so comparisons are relative inside a track
    def nz(x):
        p95 = np.percentile(x, 95) if x.size else 0.0
        return x / (p95 + 1e-9)
    e_low, e_mid, e_high = nz(e_low), nz(e_mid), nz(e_high)

    # vocal proxy: harmonic energy concentration in 300–3400 Hz
    harm, perc = librosa.effects.hpss(y)
    H_S = np.abs(librosa.stft(harm, n_fft=2048, hop_length=hop_length))**2
    vocal_band = _band_energy(H_S, freqs, 300, 3400)
    vocal_lk = nz(vocal_band)

    # transient proxy for highs: spectral flux focusing on high band
    S_high = S[(freqs >= 6000) & (freqs < 16000)]
    if S_high.size:
        dS = np.diff(S_high, axis=1)
        dS_pos = np.clip(dS, 0, None).mean(axis=0)
        high_trans = np.concatenate([[0.0], dS_pos])
        high_trans = high_trans / (np.percentile(high_trans, 95) + 1e-9)
    else:
        high_trans = np.zeros(S.shape[1])

    # brightness (global)
    sc = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    brightness = float(np.median(np.clip(sc / (sr/2), 0, 1))) if sc.size else 0.0

    return BandTimeline(times, e_low, e_mid, e_high, vocal_lk, high_trans, brightness)
