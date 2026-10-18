import json
from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
import librosa
import pyloudnorm as pyln


@dataclass
class AudioData:
    y: np.ndarray
    sr: int
    duration: float


def load_audio(path: str, sr: int = 22050) -> AudioData:
    y, sr = librosa.load(path, sr=sr, mono=True)
    return AudioData(y=y, sr=sr, duration=y.shape[0] / sr)


def loudness_metrics(y: np.ndarray, sr: int) -> Dict[str, float]:
    meter = pyln.Meter(sr)  # BS.1770
    lufs = float(meter.integrated_loudness(y))
    peak = float(np.max(np.abs(y)))
    peak_dbfs = float(20 * np.log10(max(peak, 1e-9)))
    # crude DR: 95th - 5th percentile in dB
    p95 = float(20 * np.log10(np.percentile(np.abs(y), 95) + 1e-9))
    p05 = float(20 * np.log10(np.percentile(np.abs(y), 5) + 1e-9))
    dr = float(p95 - p05)
    return {"lufs_integrated": lufs, "peak_dbfs": peak_dbfs, "dynamic_range_db": dr}


def beat_tempo(y: np.ndarray, sr: int) -> Dict[str, Any]:
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, units="time")
    # beat regularity → danceability component
    if len(beats) > 2:
        ibi = np.diff(beats)
        reg = 1.0 / (np.std(ibi) + 1e-3)  # higher is steadier
        reg_norm = float(np.tanh(reg))
    else:
        reg_norm = 0.0
    # downbeat proxy (approx): first beat & every 4th beat
    downbeats = beats[::4].tolist() if len(beats) else []
    # confidence proxy: mean onset strength at beats
    beat_frames = librosa.time_to_frames(beats, sr=sr)
    os = onset_env
    os_at_beats = os[beat_frames[beat_frames < len(os)]] if len(beat_frames) else np.array([0.0])
    conf = float(np.tanh(np.mean(os_at_beats) / (np.std(os_at_beats) + 1e-6)))
    return {"bpm": float(tempo), "bpm_confidence": conf, "downbeats": downbeats, "danceability_component": reg_norm}


def hpss_features(y: np.ndarray, sr: int) -> Dict[str, Any]:
    harm, perc = librosa.effects.hpss(y)
    # spectral centroid → brightness
    sc = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    sc_nyq = np.clip(sc / (sr / 2), 0, 1)
    brightness = float(np.median(sc_nyq))
    # percussiveness & sub intensity
    rms_all = float(np.sqrt(np.mean(y ** 2)) + 1e-9)
    perc_ratio = float(np.sqrt(np.mean(perc ** 2)) / rms_all)
    # sub band (20–80 Hz) energy ratio
    S = np.abs(librosa.stft(y, n_fft=2048)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    sub_mask = (freqs >= 20) & (freqs <= 80)
    sub_energy = float(np.mean(S[sub_mask])) if sub_mask.any() else 0.0
    all_energy = float(np.mean(S))
    sub_ratio = float(sub_energy / (all_energy + 1e-9))
    # crude vocal presence: harmonic energy in 300–3400 Hz
    band_mask = (freqs >= 300) & (freqs <= 3400)
    H = np.abs(librosa.stft(harm, n_fft=2048)) ** 2
    vocal_band = float(np.mean(H[band_mask])) if band_mask.any() else 0.0
    vocal_ratio = float(vocal_band / (np.mean(H) + 1e-9))
    return {
        "brightness_med": brightness,
        "percussive_ratio": perc_ratio,
        "sub_ratio": sub_ratio,
        "vocal_band_energy_ratio": vocal_ratio,
    }


def heuristics_to_tags(duration, bpm, dance_comp, brightness, perc_ratio, sub_ratio, vocal_ratio) -> Dict[str, Any]:
    # brightness → timbre
    timbre = "dark" if brightness < 0.35 else ("neutral" if brightness < 0.6 else "bright")
    # vocal presence
    if vocal_ratio < 0.12:
        vp = "none"
    elif vocal_ratio < 0.22:
        vp = "sparse"
    else:
        vp = "lead"
    instrumental = vp == "none"
    # percussiveness & sub intensity → 1..10
    percussiveness = int(np.clip(np.round(3 + 7 * min(1.0, perc_ratio)), 1, 10))
    sub_intensity = int(np.clip(np.round(2 + 12 * min(1.0, sub_ratio)), 1, 10))
    # danceability rough: combine beat regularity + tempo in dance ranges
    tempo_fit = float(np.exp(-(((bpm - 126.0) ** 2) / (2 * 12.0 ** 2))))  # peak ~126 BPM
    danceability = int(np.clip(np.round(2 + 8 * (0.6 * float(dance_comp) + 0.4 * tempo_fit)), 1, 10))
    # intro/outro bars guess
    intro_bars = 8 if percussiveness >= 6 else 16
    outro_bars = 8 if sub_intensity >= 6 else 16
    return dict(
        timbre_brightness=timbre,
        vocal_presence=vp,
        instrumental=instrumental,
        percussiveness_1_10=percussiveness,
        sub_intensity_1_10=sub_intensity,
        danceability_1_10=danceability,
        phrase_bars={"intro": intro_bars, "outro": outro_bars},
    )


def analyze_core(path: str) -> Dict[str, Any]:
    ad = load_audio(path)
    lm = loudness_metrics(ad.y, ad.sr)
    bt = beat_tempo(ad.y, ad.sr)
    hs = hpss_features(ad.y, ad.sr)
    tags = heuristics_to_tags(
        ad.duration,
        bt["bpm"],
        bt["danceability_component"],
        hs["brightness_med"],
        hs["percussive_ratio"],
        hs["sub_ratio"],
        hs["vocal_band_energy_ratio"],
    )
    return {
        "file": {
            "path": path,
            "duration_sec": ad.duration,
            "samplerate_hz": ad.sr,
            "bitrate_kbps": None,
            "format": path.split(".")[-1].lower(),
        },
        "rhythm": {
            "bpm": bt["bpm"],
            "bpm_confidence": bt["bpm_confidence"],
            "downbeat_times": bt["downbeats"],
            "phrase_bars": tags["phrase_bars"],
        },
        "energy": {
            "lufs_integrated": lm["lufs_integrated"],
            "peak_dbfs": lm["peak_dbfs"],
            "dynamic_range_db": lm["dynamic_range_db"],
            "percussiveness_1_10": tags["percussiveness_1_10"],
            "sub_intensity_1_10": tags["sub_intensity_1_10"],
        },
        "feel": {
            "danceability_1_10": tags["danceability_1_10"],
            "timbre_brightness": tags["timbre_brightness"],
            "vocal_presence": tags["vocal_presence"],
            "instrumental": tags["instrumental"],
        },
        "mix": {
            "vocal_band_energy_ratio": hs["vocal_band_energy_ratio"],
            "cue_points": [],
            "structure": [],
        },
        "classify": {"genre_top": "unknown", "genre_alt": []},
    }
