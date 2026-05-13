from typing import Tuple, Dict

import numpy as np
import librosa

from ..plan import key_to_camelot, normalize_key

# Krumhansl-Kessler profiles
_KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

_PITCHES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def _chroma_profile(y, sr):
    C = librosa.feature.chroma_cqt(y=y, sr=sr, norm=None)
    v = C.mean(axis=1)
    v = v / (np.linalg.norm(v) + 1e-9)
    return v


def detect_key(y, sr) -> Tuple[str, str, float]:
    """Return (key_name, camelot_code, confidence 0..1).
    key_name like "A minor" or "E major". Camelot via mixcli.plan mapping.
    """
    chroma = _chroma_profile(y, sr)
    best_pitch = None
    best_mode = "major"
    best_score = -1.0
    for mode, tpl in (("major", _KK_MAJOR), ("minor", _KK_MINOR)):
        for i, pitch in enumerate(_PITCHES):
            prof = np.roll(tpl, i)
            # cosine similarity
            score = float(np.dot(chroma, prof) / (np.linalg.norm(prof) + 1e-9))
            if score > best_score:
                best_score = score
                best_pitch = pitch
                best_mode = mode
    # Build key strings
    key_symbol = best_pitch + ("m" if best_mode == "minor" else "")
    camelot = key_to_camelot(normalize_key(key_symbol))
    key_name = f"{best_pitch} {'minor' if best_mode=='minor' else 'major'}"
    conf = float((best_score + 1.0) / 2.0)
    return key_name, (camelot or ""), conf


def camelot_neighbors(camelot: str) -> Dict[str, list]:
    """Return neighbor sets as dict: same, safe (±1 same letter), energy_boost (+2), relative.
    Example: for 8A →
      same: ["8A"], safe: ["7A","9A"], energy_boost: ["10A"], relative: ["8B"]
    """
    if not camelot or not isinstance(camelot, str):
        return {"same": [], "safe": [], "energy_boost": [], "relative": []}
    try:
        num = int(''.join([c for c in camelot if c.isdigit()]))
        letter = 'A' if 'A' in camelot.upper() else 'B'
    except Exception:
        return {"same": [], "safe": [], "energy_boost": [], "relative": []}

    def wrap(n: int) -> int:
        return ((n - 1) % 12) + 1

    same = [f"{num}{letter}"]
    safe = [f"{wrap(num-1)}{letter}", f"{wrap(num+1)}{letter}"]
    energy_boost = [f"{wrap(num+2)}{letter}"]
    relative = [f"{num}{'B' if letter=='A' else 'A'}"]
    return {"same": same, "safe": safe, "energy_boost": energy_boost, "relative": relative}
