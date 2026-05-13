import json, os
from typing import List, Dict, Any, Optional

from .plan import key_to_camelot


def _to_camelot(key_or_code: Optional[str]) -> Optional[str]:
    if not key_or_code:
        return None
    s = key_or_code.strip().upper()
    # Accept direct Camelot like '8A'/'10B'
    if len(s) in (2, 3) and s[-1] in {"A", "B"} and s[:-1].isdigit():
        n = int(s[:-1])
        if 1 <= n <= 12:
            return f"{n}{s[-1]}"
    # Else map musical key (e.g., 'C#m') via normalize->camelot
    cam = key_to_camelot(key_or_code)
    return cam


def _camelot_num_ring(code: str) -> Optional[tuple[int, str]]:
    try:
        return (int(code[:-1]), code[-1])
    except Exception:
        return None


def key_match_score(cur_key: Optional[str], cand_key: Optional[str]) -> float:
    """Return key compatibility score per playbook:
    1.0 same key; 0.8 relative; 0.7 ±1; 0.6 +2; else 0.2
    Accepts musical keys (e.g., 'Am') or Camelot codes ('8A').
    """
    a = _to_camelot(cur_key)
    b = _to_camelot(cand_key)
    if not a or not b:
        return 0.2
    if a == b:
        return 1.0
    na = _camelot_num_ring(a)
    nb = _camelot_num_ring(b)
    if not na or not nb:
        return 0.2
    (an, ar), (bn, br) = na, nb
    # Relative (same number, other letter)
    if an == bn and ar != br:
        return 0.8
    # Same ring +/-1
    if ar == br and ((bn - an) % 12 in (1, 11)):
        return 0.7
    # Same ring +2
    if ar == br and ((bn - an) % 12 == 2):
        return 0.6
    return 0.2


def bpm_fit_score(cur_bpm: float, cand_bpm: float) -> float:
    """Map BPM proximity to score per playbook thresholds.
    Uses percentage difference relative to current BPM.
    """
    cur = max(1e-6, float(cur_bpm))
    diff = abs(cand_bpm - cur) / cur
    if diff <= 0.02:
        return 1.0
    if diff <= 0.04:
        return 0.8
    if diff <= 0.06:
        return 0.5
    return 0.2


def phrase_ready_score(beats: List[float]) -> float:
    """Heuristic: treat tracks with at least a clean 16-beat intro as phrase-ready.
    - First beat near 0 (<= 0.15s)
    - At least 16 beats detected
    """
    if not beats:
        return 0.5
    if beats[0] > 0.15:
        return 0.5
    return 1.0 if len(beats) >= 16 else 0.5


def recommend_next(
    analysis_json: str,
    current_key: Optional[str] = None,
    current_bpm: Optional[float] = None,
    from_path: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    data = json.load(open(analysis_json))
    tracks = data.get("tracks", [])
    if not tracks:
        return []

    # Optionally derive current state from a known track path
    if from_path:
        # Try exact match then basename match
        match = next((t for t in tracks if t.get("path") == from_path), None)
        if not match:
            base = os.path.basename(from_path)
            match = next((t for t in tracks if os.path.basename(t.get("path", "")) == base), None)
        if match:
            current_key = current_key or match.get("key")
            current_bpm = current_bpm or match.get("tempo")

    if current_key is None or current_bpm is None:
        raise ValueError("current_key and current_bpm are required (or provide --from-path)")

    cur_key = current_key
    cur_bpm = float(current_bpm)

    scored: List[Dict[str, Any]] = []
    for t in tracks:
        # Skip self if from_path is provided
        if from_path and t.get("path") == from_path:
            continue
        k = key_match_score(cur_key, t.get("key"))
        b = bpm_fit_score(cur_bpm, float(t.get("tempo") or 0.0))
        p = phrase_ready_score([float(x) for x in t.get("beats", [])])
        total = 3.0 * k + 2.0 * b + 1.5 * p
        scored.append({
            "path": t.get("path"),
            "key": t.get("key"),
            "tempo": float(t.get("tempo") or 0.0),
            "score": float(total),
            "components": {"key_match": k, "bpm_fit": b, "phrase_ready": p},
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[: max(1, int(top_k))]
