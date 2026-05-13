# smart_style_engine.py
import yaml
from typing import Dict, Any, List
from smart_blend import compute_smart_blend


def load_cfg(path: str = "smart_config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def plan_smart_overlap(
    current_meta: Dict[str, Any],
    next_meta: Dict[str, Any],
    cfg_path: str = "smart_config.yaml",
    explain: bool = False,
) -> List[Dict[str, Any]]:
    cfg = load_cfg(cfg_path)
    cbpm = float(current_meta.get("rhythm", {}).get("bpm", 120.0))
    nbpm = float(next_meta.get("rhythm", {}).get("bpm", cbpm))
    bpm = (cbpm + nbpm) / 2.0
    # put the swap exactly at bar 0 relative to HUD start
    swap_at_sec = 0.0
    return compute_smart_blend(
        outgoing_audio=current_meta["file"]["path"],
        incoming_audio=next_meta["file"]["path"],
        cfg=cfg,
        swap_at_sec=swap_at_sec,
        bpm=bpm,
        explain=explain,
    )
