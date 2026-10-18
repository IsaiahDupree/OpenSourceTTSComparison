import json, math

# Simple Camelot map (major=outer ring "B", minor=inner ring "A")
CAMELOT = {
    "C": "8B",
    "G": "9B",
    "D": "10B",
    "A": "11B",
    "E": "12B",
    "B": "1B",
    "F#": "2B",
    "Db": "3B",
    "Ab": "4B",
    "Eb": "5B",
    "Bb": "6B",
    "F": "7B",
    "Am": "8A",
    "Em": "9A",
    "Bm": "10A",
    "F#m": "11A",
    "C#m": "12A",
    "G#m": "1A",
    "Ebm": "2A",
    "Bbm": "3A",
    "Fm": "4A",
    "Cm": "5A",
    "Gm": "6A",
    "Dm": "7A",
}

# Enharmonic normalization to our canonical names above
NORMALIZE = {
    # majors
    "C#": "Db",
    "D#": "Eb",
    "Gb": "F#",
    "G#": "Ab",
    "A#": "Bb",
    "Cb": "B",
    "E#": "F",
    "B#": "C",
    # minors
    "C#m": "C#m",  # canonical
    "D#m": "Ebm",
    "G#m": "G#m",  # canonical
    "A#m": "Bbm",
    "Dbm": "C#m",
    "Fbm": "Em",
    "E#m": "Fm",
    "B#m": "Cm",
}


def camelot_neighbors(code: str):
    # same, +/-1 hour, relative (A<->B same number)
    n = int(code[:-1])
    ring = code[-1]
    same = {f"{n}{ring}"}
    up = {f"{(n % 12) + 1}{ring}"}
    down = {f"{(n - 2) % 12 + 1}{ring}"}
    relative = {f"{n}{'A' if ring == 'B' else 'B'}"}
    return same | up | down | relative  # basic rules :contentReference[oaicite:6]{index=6}


def normalize_key(k: str | None) -> str | None:
    if not k:
        return None
    k = k.strip()
    # Ensure the 'm' suffix (minor) remains lowercase
    if k.endswith("m"):
        root = k[:-1]
        minor = True
    else:
        root = k
        minor = False
    root = root.replace("♯", "#").replace("♭", "b")
    norm = NORMALIZE.get(root + ("m" if minor else ""), root + ("m" if minor else ""))
    return norm


def key_to_camelot(k: str):
    nk = normalize_key(k)
    return CAMELOT.get(nk)


PC_MAP = {
    "C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11,
}


def key_to_pc(k: str | None) -> int | None:
    """Return pitch class (0-11) for the given key, ignoring mode. None if unknown."""
    nk = normalize_key(k) if k else None
    if not nk:
        return None
    root = nk[:-1] if nk.endswith("m") else nk
    return PC_MAP.get(root)


def semitone_diff(a_pc: int, b_pc: int) -> int:
    """Signed minimal semitone difference b-a in range [-6, +6]."""
    d = (b_pc - a_pc) % 12
    if d > 6:
        d -= 12
    return d


def compat_score(a, b):
    # 1.0 for perfect/same-key; 0.7 for neighbor/relative; else 0.3 baseline
    if a == b:
        return 1.0
    neigh = camelot_neighbors(a) if a else set()
    return 0.7 if b in neigh else 0.3


def tempo_score(a_bpm, b_bpm):
    # prefer small stretch; Gaussian around 0 delta
    delta = abs(a_bpm - b_bpm)
    return math.exp(-((delta ** 2) / (2 * 3.0 ** 2)))  # 3 BPM std dev


def plan_order(tracks, max_key_shift: int = 2):
    # greedy start: pick lowest key-hour then chain best next by combined score
    if not tracks:
        return []
    items = []
    for t in tracks:
        cam = key_to_camelot(t["key"])
        items.append({**t, "camelot": cam})
    remaining = items[:]
    remaining.sort(key=lambda x: (x["camelot"] or "99Z"))
    order = [remaining.pop(0)]
    while remaining:
        last = order[-1]
        best_i, best_s = None, -1.0
        last_pc = key_to_pc(last.get("key"))
        # First pass: enforce key semitone limit where both keys are known
        for i, cand in enumerate(remaining):
            cand_pc = key_to_pc(cand.get("key"))
            within_limit = True
            if last_pc is not None and cand_pc is not None:
                dist = abs(semitone_diff(last_pc, cand_pc))
                within_limit = dist <= max(0, int(max_key_shift))
            if not within_limit:
                continue
            ks = compat_score(last.get("camelot"), cand.get("camelot")) if last.get("camelot") and cand.get("camelot") else 0.5
            ts = tempo_score(last["tempo"], cand["tempo"])
            s = 0.65 * ks + 0.35 * ts
            if s > best_s:
                best_s, best_i = s, i
        # Fallback: if none met the limit (e.g., unknown keys), pick best by score without the gate
        if best_i is None:
            for i, cand in enumerate(remaining):
                ks = compat_score(last.get("camelot"), cand.get("camelot")) if last.get("camelot") and cand.get("camelot") else 0.5
                ts = tempo_score(last["tempo"], cand["tempo"])
                s = 0.65 * ks + 0.35 * ts
                if s > best_s:
                    best_s, best_i = s, i
        order.append(remaining.pop(best_i))
    return order


def write_plan(analysis_json: str, out_json: str, max_key_shift: int = 2):
    data = json.load(open(analysis_json))
    tracks = data.get("tracks", [])
    if not tracks:
        raise ValueError(
            f"No tracks in analysis file '{analysis_json}'. Ensure the analyze step found audio files."
        )
    order = plan_order(tracks, max_key_shift=max_key_shift)
    json.dump({"order": order}, open(out_json, "w"), indent=2)
