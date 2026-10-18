# midi_out.py
# NOTE: Works with DJ apps that support MIDI mapping (e.g., Traktor, Mixxx, Ableton).
# Rekordbox/Serato EQs generally aren't MIDI-mappable for external control; use as HUD there.
import time
from typing import List, Dict, Any

try:
    import mido
except Exception:
    mido = None  # optional dependency; only needed if sending MIDI

# Example mapping (YOU map these in your app/controller):
MIDI_MAP = {
  # deck A knobs
  ("A","eq_low"):  ("control_change", 10),
  ("A","eq_mid"):  ("control_change", 11),
  ("A","eq_high"): ("control_change", 12),
  ("A","xfader"):  ("control_change", 20),
  # deck B knobs
  ("B","eq_low"):  ("control_change", 30),
  ("B","eq_mid"):  ("control_change", 31),
  ("B","eq_high"): ("control_change", 32),
  ("B","xfader"):  ("control_change", 20),  # same if global
}


def to_cc_val(v: float) -> int:
    return int(max(0, min(127, round(float(v) * 127))))


def send_midi_timeline(actions: List[Dict[str, Any]], port_name: str):
    if mido is None:
        raise RuntimeError("mido is not installed. Run: pip install mido")
    out = mido.open_output(port_name)
    t0 = time.time()
    for a in actions:
        wait = (t0 + a["t_sec"]) - time.time()
        if wait > 0:
            time.sleep(wait)
        if a["action"] == "eq":
            key = (a["deck"], f"eq_{a['band']}")
            kind, cc = MIDI_MAP.get(key, (None, None))
            if kind == "control_change":
                out.send(mido.Message("control_change", control=cc, value=to_cc_val(a["value"])))
        elif a["action"] == "xfader":
            kind, cc = MIDI_MAP.get((a["deck"], "xfader"), (None, None))
            if kind == "control_change":
                out.send(mido.Message("control_change", control=cc, value=to_cc_val(a["value"])))
        # Other actions (filters/FX) can be mapped similarly or just displayed in HUD
