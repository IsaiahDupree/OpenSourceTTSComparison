import argparse, json, glob, os
from typing import Dict, Any, List, Tuple


def load_library(index_path_or_glob: str) -> List[Dict[str, Any]]:
    paths = []
    if os.path.exists(index_path_or_glob):
        paths = [index_path_or_glob]
    else:
        paths = glob.glob(index_path_or_glob, recursive=True)
    entries = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    entries.append(data)
        except Exception:
            pass
    return entries


def key_match_score(cur: str, nxt: str) -> float:
    try:
        cnum, clet = int(cur[:-1]), cur[-1]
        nnum, nlet = int(nxt[:-1]), nxt[-1]
    except Exception:
        return 0.2
    if cur == nxt:
        return 1.0
    if cnum == nnum and clet != nlet:
        return 0.9  # relative major/minor
    if clet == nlet and ((nnum - cnum) % 12 in (1, 11)):
        return 0.8  # ±1
    if clet == nlet and ((nnum - cnum) % 12 in (2, 10)):
        return 0.7  # +2
    return 0.2


def bpm_fit_score(cbpm: float, nbpm: float) -> float:
    diff = abs(nbpm - cbpm) / max(cbpm, 1.0)
    if diff <= 0.02:
        return 1.0
    if diff <= 0.04:
        return 0.8
    if diff <= 0.06:
        return 0.5
    return 0.2


def energy_follow_score(cur: int, nxt: int, goal: str) -> float:
    if goal == "lift":
        return 1.0 if nxt >= cur else 0.5
    if goal == "hold":
        return 1.0 if abs(nxt - cur) <= 1 else 0.6
    if goal == "breathe":
        return 1.0 if nxt <= cur - 1 else 0.5
    return 0.8


def timbre_match_score(ct: str, nt: str) -> float:
    return 1.0 if ct == nt else (0.7 if (ct == "neutral" or nt == "neutral") else 0.5)


def score_track(current: Dict[str, Any], candidate: Dict[str, Any], goal: str) -> Tuple[float, Dict[str, float]]:
    key_s = key_match_score(current["harmony"]["key_open"], candidate["harmony"]["key_open"])
    bpm_s = bpm_fit_score(float(current["rhythm"]["bpm"]), float(candidate["rhythm"]["bpm"]))
    phr_ready = 1.0  # TODO: infer from structure if available
    energy_s = energy_follow_score(int(current["energy"].get("percussiveness_1_10", 5)), int(candidate["energy"].get("percussiveness_1_10", 5)), goal)
    timbre_s = timbre_match_score(current["feel"].get("timbre_brightness", "neutral"), candidate["feel"].get("timbre_brightness", "neutral"))
    components = {"key_match": key_s, "bpm_fit": bpm_s, "phrase_ready": phr_ready, "energy_fit": energy_s, "timbre_match": timbre_s}
    total = 3.0 * key_s + 2.0 * bpm_s + 1.5 * phr_ready + 1.0 * energy_s + 0.5 * timbre_s
    return float(total), components


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--current_json", required=True, help="Path to current track sidecar .mixmeta.json")
    ap.add_argument("--library_glob", required=True, help="Glob for library sidecars e.g. 'D:/Music/**/*.mixmeta.json'")
    ap.add_argument("--goal", default="lift", choices=["lift", "hold", "breathe"])
    ap.add_argument("--topk", type=int, default=5)
    args = ap.parse_args()

    with open(args.current_json, "r", encoding="utf-8") as f:
        current = json.load(f)
    library = load_library(args.library_glob)
    scored = []
    for cand in library:
        if cand.get("file", {}).get("path") == current.get("file", {}).get("path"):
            continue
        s, comps = score_track(current, cand, args.goal)
        scored.append((s, comps, cand))
    scored.sort(key=lambda x: x[0], reverse=True)
    for s, comps, c in scored[: args.topk]:
        print(
            f"{s:0.2f}  | {c['file']['path']}  | {c['harmony'].get('key_open','?')} | "
            f"{float(c['rhythm'].get('bpm',0.0)):.1f} BPM | E{int(c['energy'].get('percussiveness_1_10',5))} | "
            f"{c['feel'].get('timbre_brightness','?')} | {c['feel'].get('vocal_presence','?')}"
        )


if __name__ == "__main__":
    main()
