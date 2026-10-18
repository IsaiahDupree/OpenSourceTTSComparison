# style_selector.py
from typing import Dict, Tuple


def key_ok(cur: str, nxt: str) -> bool:
    if not cur or not nxt:
        return False
    if cur == nxt:
        return True
    try:
        cnum, clet = int(cur[:-1]), cur[-1].upper()
        nnum, nlet = int(nxt[:-1]), nxt[-1].upper()
    except Exception:
        return False
    # relative major/minor (same number, different letter)
    if cnum == nnum and nlet != clet:
        return True
    # +/-1 around the circle within same mode/letter
    if clet == nlet and ((nnum - cnum) % 12 in (1, 11)):
        return True
    return False


def select_style(current: Dict, next_: Dict) -> str:
    cbpm = float(current.get("rhythm", {}).get("bpm", 0.0))
    nbpm = float(next_.get("rhythm", {}).get("bpm", cbpm))
    bpm_diff = abs(nbpm - cbpm) / max(cbpm or 1.0, 1.0)

    cur_voc = (current.get("feel", {}) or {}).get("vocal_presence", "none")
    nxt_voc = (next_.get("feel", {}) or {}).get("vocal_presence", "none")

    cur_key = (current.get("harmony", {}) or {}).get("key_open", "")
    nxt_key = (next_.get("harmony", {}) or {}).get("key_open", "")

    cur_gen = (current.get("classify", {}) or {}).get("genre_top", "unknown")
    nxt_gen = (next_.get("classify", {}) or {}).get("genre_top", "unknown")

    # 1) safe long blend if keys compatible + small BPM diff
    if key_ok(cur_key, nxt_key) and bpm_diff <= 0.04:
        return "three_band_eq_blend"

    # 2) vocal over drums bridge if next has lead vocal & BPM close
    if nxt_voc == "lead" and bpm_diff <= 0.04:
        return "acapella_bridge"

    # 3) filter-in for medium BPM/key differences
    if bpm_diff <= 0.06:
        return "filter_in_bass_swap"

    # 4) genre pivot or large BPM jump → impact cut
    if cur_gen != nxt_gen or bpm_diff > 0.06:
        return "impact_cut_echo"

    # fallback
    return "filter_in_bass_swap"


def select_style_with_why(current: Dict, next_: Dict) -> Tuple[str, str]:
    cbpm = float(current.get("rhythm", {}).get("bpm", 0.0))
    nbpm = float(next_.get("rhythm", {}).get("bpm", cbpm))
    bpm_diff = abs(nbpm - cbpm) / max(cbpm or 1.0, 1.0)

    cur_voc = (current.get("feel", {}) or {}).get("vocal_presence", "none")
    nxt_voc = (next_.get("feel", {}) or {}).get("vocal_presence", "none")

    cur_key = (current.get("harmony", {}) or {}).get("key_open", "")
    nxt_key = (next_.get("harmony", {}) or {}).get("key_open", "")

    cur_gen = (current.get("classify", {}) or {}).get("genre_top", "unknown")
    nxt_gen = (next_.get("classify", {}) or {}).get("genre_top", "unknown")

    if key_ok(cur_key, nxt_key) and bpm_diff <= 0.04:
        return (
            "three_band_eq_blend",
            f"keys compatible ({cur_key}→{nxt_key}); BPM diff {bpm_diff*100:.1f}% → long blend safe",
        )
    if nxt_voc == "lead" and bpm_diff <= 0.04:
        return (
            "acapella_bridge",
            f"next has lead vocal; BPM diff {bpm_diff*100:.1f}% → vocal bridge fits",
        )
    if bpm_diff <= 0.06:
        return (
            "filter_in_bass_swap",
            f"moderate BPM diff {bpm_diff*100:.1f}% → short filter-in then bass swap",
        )
    if cur_gen != nxt_gen or bpm_diff > 0.06:
        return (
            "impact_cut_echo",
            f"genre pivot ({cur_gen}→{nxt_gen}) or large BPM diff {bpm_diff*100:.1f}% → impact cut",
        )
    return ("filter_in_bass_swap", "fallback choice")
