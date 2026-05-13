# style_engine.py
import yaml, json, math
from typing import Dict, Any, List


def load_styles(path: str = "mixing_styles.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("styles", {})


def bars_to_seconds(bars: float, bpm: float, beats_per_bar: int = 4) -> float:
    sec_per_beat = 60.0 / max(float(bpm), 1e-6)
    return float(bars) * beats_per_bar * sec_per_beat


def phrase_guess(meta: Dict[str, Any], default_bars: int) -> int:
    pb = (meta.get("rhythm", {}) or {}).get("phrase_bars", {}) or {}
    intro = pb.get("intro") or default_bars
    outro = pb.get("outro") or default_bars
    # choose a stable window around the swap → use min(intro,outro,default)
    return int(max(4, min(intro, outro, default_bars)))


def plan_transition(current_meta: Dict[str, Any], next_meta: Dict[str, Any],
                    style: Dict[str, Any], start_at_bar_zero: bool = True) -> List[Dict[str, Any]]:
    cbpm = float((current_meta.get("rhythm", {}) or {}).get("bpm", 0.0))
    nbpm = float((next_meta.get("rhythm", {}) or {}).get("bpm", cbpm))
    bpm = (cbpm + nbpm) / 2.0 if (cbpm and nbpm) else (cbpm or nbpm or 120.0)
    phrase_bars = phrase_guess(current_meta, style.get("default_bars", 16))
    actions: List[Dict[str, Any]] = []
    for step in style.get("steps", []):
        t_bar = step["t_bar"]
        # scale relative window to our phrase length if style default != phrase
        scale = phrase_bars / float(style.get("default_bars", phrase_bars))
        t_sec = bars_to_seconds(t_bar * scale, bpm)
        actions.append({
            "t_sec": t_sec,
            "deck": step["deck"],
            "action": step["action"],
            **{k: v for k, v in step.items() if k not in ("t_bar", "deck", "action")}
        })
    # sort by time
    actions.sort(key=lambda a: a["t_sec"])
    return actions


def pretty_print(actions: List[Dict[str, Any]]):
    for a in actions:
        t = a["t_sec"]
        deck = a["deck"]
        act = a["action"]
        rest = {k: v for k, v in a.items() if k not in ("t_sec", "deck", "action")}
        print(f"{t:+6.2f}s | Deck {deck} | {act} | {json.dumps(rest)}")
