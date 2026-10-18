# smart_test.py
import argparse
import json
from typing import List, Dict, Any, Optional
import builtins

from smart_style_engine import plan_smart_overlap, load_cfg
import hud_smart


def _print_preview(current_json: str, next_json: str) -> None:
    with open(current_json, "r", encoding="utf-8") as f:
        cur = json.load(f)
    with open(next_json, "r", encoding="utf-8") as f:
        nxt = json.load(f)

    actions = plan_smart_overlap(cur, nxt, explain=True)

    # Group by timestamp and print only entries with 'why'
    last_ts: Optional[float] = None
    bucket: List[Dict[str, Any]] = []

    def flush_bucket():
        if not bucket:
            return
        ts = bucket[0]["t_sec"]
        reasons = [
            f"{x['deck']}:{x.get('band','xf')} → {x['why']}"
            for x in bucket if "why" in x
        ]
        if reasons:
            print(f"{ts:+6.2f}s | " + "  ||  ".join(reasons))

    for a in actions:
        ts = a["t_sec"]
        if last_ts is None or abs(ts - last_ts) < 1e-6:
            bucket.append(a)
            last_ts = ts
            continue
        flush_bucket()
        bucket = [a]
        last_ts = ts
    flush_bucket()


def _run_hud(current_json: str, next_json: str, explain: bool, no_wait: bool, log_json_override: Optional[bool], midi: bool, midi_port: str) -> None:
    # Optionally override config's explain.log_json without editing files
    cfg = load_cfg()
    if log_json_override is not None:
        cfg.setdefault("explain", {})
        cfg["explain"]["log_json"] = bool(log_json_override)

    # Monkey-patch hud_smart.load_cfg to return the overridden cfg for this run
    orig_load_cfg = hud_smart.load_cfg
    hud_smart.load_cfg = lambda: cfg

    # Optionally auto-press ENTER to start
    orig_input = builtins.input
    if no_wait:
        builtins.input = lambda *args, **kwargs: None

    try:
        hud_smart.run(current_json, next_json, send_midi=midi, midi_port=midi_port, explain=explain)
    finally:
        # restore patches
        hud_smart.load_cfg = orig_load_cfg
        builtins.input = orig_input


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SmartBlend test runner: preview 'why' and optional real-time HUD run")
    ap.add_argument("--current_json", required=True, help="Path to Deck A sidecar JSON")
    ap.add_argument("--next_json", required=True, help="Path to Deck B sidecar JSON")
    ap.add_argument("--preview", action="store_true", help="Run dry-run preview (prints only 'why' notes)")
    ap.add_argument("--hud", action="store_true", help="Run HUD in explain mode (real-time)")
    ap.add_argument("--no_wait", action="store_true", help="Auto-start HUD without waiting for ENTER")
    ap.add_argument("--enable_log_json", action="store_true", help="Force enable JSON timeline logging for this HUD run")
    ap.add_argument("--disable_log_json", action="store_true", help="Force disable JSON timeline logging for this HUD run")
    ap.add_argument("--midi", action="store_true", help="Send timeline over MIDI as well")
    ap.add_argument("--midi_port", default="", help="MIDI port name")
    args = ap.parse_args()

    if not args.preview and not args.hud:
        # default: run both if neither flag provided
        args.preview = True
        args.hud = True

    log_override: Optional[bool] = None
    if args.enable_log_json and args.disable_log_json:
        raise SystemExit("Cannot set both --enable_log_json and --disable_log_json")
    if args.enable_log_json:
        log_override = True
    elif args.disable_log_json:
        log_override = False

    if args.preview:
        print("=== SmartBlend Preview (reasons only) ===")
        _print_preview(args.current_json, args.next_json)

    if args.hud:
        print("=== SmartBlend HUD (real-time) ===")
        if log_override is not None:
            print(f"[config override] explain.log_json = {log_override}")
        _run_hud(
            current_json=args.current_json,
            next_json=args.next_json,
            explain=True,
            no_wait=args.no_wait,
            log_json_override=log_override,
            midi=args.midi,
            midi_port=args.midi_port,
        )
