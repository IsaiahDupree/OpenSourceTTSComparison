# smart_preview.py
import json, argparse
from typing import List, Dict, Any
from smart_style_engine import plan_smart_overlap


def _print_bucket(bucket: List[Dict[str, Any]]):
    if not bucket:
        return
    ts = bucket[0]["t_sec"]
    reasons = [
        f"{x['deck']}:{x.get('band','xf')} → {x['why']}"
        for x in bucket if "why" in x
    ]
    if reasons:
        print(f"{ts:+6.2f}s | " + "  ||  ".join(reasons))


def main():
    ap = argparse.ArgumentParser(description="SmartBlend dry-run explainer (no timing)")
    ap.add_argument("--current_json", required=True)
    ap.add_argument("--next_json", required=True)
    args = ap.parse_args()

    with open(args.current_json, "r", encoding="utf-8") as f:
        cur = json.load(f)
    with open(args.next_json, "r", encoding="utf-8") as f:
        nxt = json.load(f)

    actions = plan_smart_overlap(cur, nxt, explain=True)

    # collapse to unique timestamps and print reasons
    last_ts = None
    bucket: List[Dict[str, Any]] = []
    for a in actions:
        ts = a["t_sec"]
        if last_ts is None or abs(ts - last_ts) < 1e-6:
            bucket.append(a)
            last_ts = ts
            continue
        _print_bucket(bucket)
        bucket = [a]
        last_ts = ts
    if bucket:
        _print_bucket(bucket)


if __name__ == "__main__":
    main()
