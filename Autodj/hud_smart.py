# hud_smart.py
import time, json, argparse
from rich.console import Console
from smart_style_engine import plan_smart_overlap, load_cfg

# optional MIDI
try:
    from midi_out import send_midi_timeline
    HAVE_MIDI = True
except Exception:
    HAVE_MIDI = False

console = Console()


def run(current_json: str, next_json: str, send_midi: bool = False, midi_port: str = "", explain: bool = False):
    with open(current_json, "r", encoding="utf-8") as f:
        cur = json.load(f)
    with open(next_json, "r", encoding="utf-8") as f:
        nxt = json.load(f)

    cfg = load_cfg()
    actions = plan_smart_overlap(cur, nxt, explain=explain)

    console.rule("[bold]SmartBlend (why mode enabled)" if explain else "[bold]SmartBlend: adaptive band overlap (mid fade-in, high fade-out)")
    console.print("[green]Tap ENTER on the downbeat ('1') to start[/]")
    input()
    t0 = time.time()
    idx = 0
    timeline_log = []
    while idx < len(actions):
        now = time.time() - t0
        a = actions[idx]
        if now >= a["t_sec"]:
            payload = {k: v for k, v in a.items() if k not in ("t_sec", "deck", "action", "why")}
            msg = f"[cyan]{now:6.2f}s[/]  Deck {a['deck']}  {a['action']}  {payload}"
            if explain and ("why" in a):
                msg += f"  [magenta]why:[/] {a['why']}"
            console.print(msg)
            timeline_log.append(a)
            idx += 1
        else:
            time.sleep(0.02)

    # Optional JSON log
    if (cfg.get("explain", {}) or {}).get("log_json", False):
        out = {"current": cur.get("file", {}).get("path", ""),
               "next": nxt.get("file", {}).get("path", ""),
               "actions": timeline_log}
        with open("smartblend_log.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        console.print("[yellow]Saved smartblend_log.json[/]")

    if send_midi and HAVE_MIDI:
        console.print("[yellow]Sending timeline over MIDI…[/]")
        send_midi_timeline(actions, midi_port)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--current_json", required=True)
    ap.add_argument("--next_json", required=True)
    ap.add_argument("--midi", action="store_true")
    ap.add_argument("--midi_port", default="")
    ap.add_argument("--explain", action="store_true")
    args = ap.parse_args()
    run(args.current_json, args.next_json, args.midi, args.midi_port, args.explain)
