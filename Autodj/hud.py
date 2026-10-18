# hud.py
import time, argparse, json
from rich.console import Console
from style_engine import load_styles, plan_transition, pretty_print
from style_selector import select_style, select_style_with_why

console = Console()


def run_hud(current_json: str, next_json: str, style_name: str | None = None):
    with open(current_json, "r", encoding="utf-8") as f:
        cur = json.load(f)
    with open(next_json, "r", encoding="utf-8") as f:
        nxt = json.load(f)

    styles = load_styles()
    if style_name:
        chosen = style_name
        reason_style, reason = select_style_with_why(cur, nxt)
        reason_note = f"(auto would pick: {reason_style} — {reason})"
    else:
        chosen, reason = select_style_with_why(cur, nxt)
        reason_note = ""

    if chosen not in styles:
        raise SystemExit(f"Style '{chosen}' not found in mixing_styles.yaml. Available: {', '.join(styles.keys())}")

    actions = plan_transition(cur, nxt, styles[chosen])

    target_bpm = (float(cur.get('rhythm',{}).get('bpm',0.0)) + float(nxt.get('rhythm',{}).get('bpm',0.0))) / 2 or 120.0
    console.rule(f"[bold]Style: {chosen}[/]  |  Target BPM ~ {target_bpm:.1f}")
    if reason:
        console.print(f"[dim]Why: {reason} {reason_note}[/]")
    pretty_print(actions)

    console.print("\n[bold green]Tap ENTER on the downbeat (the '1') to start timeline...[/]")
    input()
    t0 = time.time()
    idx = 0
    while idx < len(actions):
        now = time.time() - t0
        tgt = actions[idx]["t_sec"]
        if now >= tgt:
            a = actions[idx]
            console.print(
                f"[cyan]{now:6.2f}s[/]  Deck [bold]{a['deck']}[/]  {a['action']}  "
                f"{ {k:v for k,v in a.items() if k not in ('t_sec','deck','action')} }"
            )
            idx += 1
        else:
            time.sleep(0.05)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--current_json", required=True)
    ap.add_argument("--next_json", required=True)
    ap.add_argument("--style", default=None)
    args = ap.parse_args()
    run_hud(args.current_json, args.next_json, args.style)
