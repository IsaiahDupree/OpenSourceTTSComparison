# smart_blend.py
import numpy as np
from typing import Dict, Any, List
from smart_features import analyze_bands


def smooth_ma(x, k=4):
    if k <= 1:
        return x
    c = np.convolve(x, np.ones(k) / k, mode="same")
    return np.clip(c, 0.0, 1.0)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _reason_band(band: str, ts: float, prev: float, cur: float,
                 extras: dict, cfg: dict, deck: str):
    """Return a compact human explanation or None."""
    dmin = float(cfg.get("explain", {}).get("delta_min", 0.08))
    if abs(cur - prev) < dmin:
        return None
    arrow = "↑" if cur > prev else "↓"
    why_bits = []
    if band == "mid":
        vd = float(extras.get("vocal_delta", 0.0))
        if abs(vd) >= float(cfg.get("explain", {}).get("vocal_delta_min", 0.15)):
            why_bits.append(f"vocals {'B' if vd > 0 else 'A'} +{abs(vd):.2f}")
        md = float(extras.get("mid_ratio_log", 0.0))
        if abs(md) >= 0.10:
            why_bits.append(f"mid energy {'B' if md > 0 else 'A'} {np.exp(abs(md)):.2f}×")
    elif band == "high":
        td = float(extras.get("transient_delta", 0.0))
        if abs(td) >= float(cfg.get("explain", {}).get("transient_delta_min", 0.10)):
            why_bits.append(f"transients {'B' if td > 0 else 'A'} +{abs(td):.2f}")
        bb = float(extras.get("bright_bias", 0.0))
        if abs(bb) >= float(cfg.get("explain", {}).get("brightness_delta_min", 0.10)):
            why_bits.append(f"brightness {'B' if bb > 0 else 'A'} +{abs(bb):.2f}")
    elif band == "low":
        if bool(extras.get("is_swap", False)):
            return "one-bass swap on the 1"
        if bool(extras.get("is_preduck", False)) and deck == "B":
            return "pre-duck lows ready for swap"
    if not why_bits:
        return f"balance {arrow}"
    return f"{' | '.join(why_bits)} → {('open' if deck == 'B' else 'duck')} {band} {arrow}"


def compute_smart_blend(
    outgoing_audio: str,
    incoming_audio: str,
    cfg: Dict[str, Any],
    swap_at_sec: float,
    bpm: float,
    explain: bool = False,
) -> List[Dict[str, Any]]:
    # analyze both tracks
    A = analyze_bands(outgoing_audio)  # Deck A (outgoing)
    B = analyze_bands(incoming_audio)  # Deck B (incoming)

    # align timelines (min length)
    L = min(len(A.t), len(B.t))
    ta, tb = A.t[:L], B.t[:L]
    t = np.minimum(ta, tb)

    # Build dominance signals (incoming vs outgoing) per band
    eps = 1e-6
    ratio_low = (B.energy_low[:L] + eps) / (A.energy_low[:L] + eps)
    ratio_mid = (B.energy_mid[:L] + eps) / (A.energy_mid[:L] + eps)
    ratio_high = (B.energy_high[:L] + eps) / (A.energy_high[:L] + eps)

    # weights
    w_voc = float(cfg["weights"]["vocal_priority"])  # protect incoming vocals
    w_tr = float(cfg["weights"]["transient_priority"])  # protect crisp highs
    w_timb = float(cfg["weights"]["timbre_balance"])  # prefer brighter incoming
    base_th = float(cfg["weights"]["base_mask_thresh"])

    # enhance MID dominance if incoming vocals are present
    mid_bonus = 1.0 + w_voc * (B.vocal_likelihood[:L] - A.vocal_likelihood[:L])
    mid_dom = ratio_mid * mid_bonus

    # enhance HIGH dominance if incoming has more transients OR is brighter
    trans_delta = (B.high_transients[:L] - A.high_transients[:L])
    bright_bias = np.clip((B.brightness - A.brightness), -1.0, 1.0) * w_timb
    high_dom = ratio_high * (1.0 + w_tr * trans_delta + bright_bias)

    # LOW is special (one-bass rule), we pre-duck and then swap hard at bar 0
    low_dom = ratio_low  # used only for pre-duck shaping

    # convert dominance to target gains (0..1) per band per deck
    def dom_to_gain(dom):
        # map > base_th to favor incoming; symmetric around 1
        x = np.log(dom + eps)
        gB = sigmoid(2.2 * x - base_th)  # incoming gain
        gA = 1.0 - gB  # outgoing gain
        return np.clip(gA, 0, 1), np.clip(gB, 0, 1)

    gA_mid, gB_mid = dom_to_gain(mid_dom)
    gA_high, gB_high = dom_to_gain(high_dom)

    # LOW handling: pre-duck then swap
    sec_per_bar = 60.0 / max(bpm, 1e-6) * 4.0
    pre_bars = int(cfg["bass_swap"]["pre_fade_bars"]) or 0
    swap_at = float(swap_at_sec)
    pre_start = swap_at - pre_bars * sec_per_bar
    # simple shapes; you can refine to use low_dom if desired
    pre_mask = (t >= pre_start) & (t < swap_at)
    pre_len = max(swap_at - pre_start, 1e-6)
    pre_ratio = np.clip((t - pre_start) / pre_len, 0.0, 1.0)
    gA_low = np.where(
        pre_mask,
        1.0,  # keep A lows steady pre-swap
        np.where(t >= swap_at, 0.0, 1.0),
    )
    gB_low = np.where(
        pre_mask,
        0.2 + 0.2 * pre_ratio,  # slight presence incoming lows pre-swap
        np.where(t >= swap_at, 1.0, 0.0),
    )

    # smoothing (convert smoothing_bars → windows)
    hop_sec = float(cfg.get("time", {}).get("hop_sec", 0.125))
    k = max(1, int((float(cfg["gains"]["smoothing_bars"]) * sec_per_bar) / max(hop_sec, 1e-3)))
    gA_low, gB_low = smooth_ma(gA_low, k), smooth_ma(gB_low, k)
    gA_mid, gB_mid = smooth_ma(gA_mid, k), smooth_ma(gB_mid, k)
    gA_high, gB_high = smooth_ma(gA_high, k), smooth_ma(gB_high, k)

    # clamp to min/max per band
    def clamp(g, band):
        mn = float(cfg["gains"]["min"][band])
        mx = float(cfg["gains"]["max"][band])
        return np.clip(g, mn, mx)

    gA_low = clamp(gA_low, "low"); gB_low = clamp(gB_low, "low")
    gA_mid = clamp(gA_mid, "mid"); gB_mid = clamp(gB_mid, "mid")
    gA_high = clamp(gA_high, "high"); gB_high = clamp(gB_high, "high")

    # quantize to bar grid (reduce MIDI spam)
    bar = sec_per_bar
    q = int(cfg["time"]["bar_quantize"]) or 1
    grid = np.arange(t[0], t[-1] + 1e-6, q * bar)

    def sample_on_grid(tt, arr):
        idx = np.searchsorted(tt, grid, side="left")
        idx = np.clip(idx, 0, len(arr) - 1)
        return grid, arr[idx]

    # sample gains on grid
    _, A_low = sample_on_grid(t, gA_low);  _, B_low = sample_on_grid(t, gB_low)
    _, A_mid = sample_on_grid(t, gA_mid);  _, B_mid = sample_on_grid(t, gB_mid)
    _, A_high = sample_on_grid(t, gA_high); _, B_high = sample_on_grid(t, gB_high)

    # extras on grid for explanations
    _, mid_ratio_log = sample_on_grid(t, np.log(mid_dom + eps))
    _, transient_delta = sample_on_grid(t, trans_delta)
    bright_bias_arr = np.full_like(transient_delta, float(bright_bias))
    _, vocal_delta = sample_on_grid(t, (B.vocal_likelihood[:L] - A.vocal_likelihood[:L]))

    actions: List[Dict[str, Any]] = []
    prev_vals = {
        ("A", "low"): None, ("A", "mid"): None, ("A", "high"): None,
        ("B", "low"): None, ("B", "mid"): None, ("B", "high"): None,
        ("B", "xfader"): None,
    }

    xf_open = int(cfg["style_defaults"]["crossfader_after_swap_bars"]) or 4
    for i, ts in enumerate(grid):
        extras = {
            "vocal_delta": float(vocal_delta[i]),
            "mid_ratio_log": float(mid_ratio_log[i]),
            "transient_delta": float(transient_delta[i]),
            "bright_bias": float(bright_bias_arr[i]),
            "is_preduck": bool((ts >= pre_start) and (ts < swap_at)),
            "is_swap": bool(abs(ts - swap_at) < 1e-6),
        }
        # per-band EQ
        for band, a_val, b_val in (("low", A_low[i], B_low[i]),
                                   ("mid", A_mid[i], B_mid[i]),
                                   ("high", A_high[i], B_high[i])):
            for deck, val in (("A", float(a_val)), ("B", float(b_val))):
                act = {"t_sec": float(ts), "deck": deck, "action": "eq", "band": band, "value": float(val)}
                prev = prev_vals[(deck, band)]
                if explain and (prev is not None):
                    reason = _reason_band(band, float(ts), float(prev), float(val), extras, cfg, deck)
                    if reason:
                        act["why"] = reason
                prev_vals[(deck, band)] = val
                actions.append(act)

        # crossfader plan: keep centered pre-swap; open to B post-swap
        if ts < swap_at:
            xf_val = 0.5
        else:
            prog = min(1.0, (ts - swap_at) / (xf_open * bar))
            xf_val = 0.5 + 0.5 * prog
        xf_act = {"t_sec": float(ts), "deck": "B", "action": "xfader", "value": float(xf_val)}
        xf_prev = prev_vals[("B", "xfader")]
        if explain and (xf_prev is not None):
            dmin = float(cfg.get("explain", {}).get("delta_min", 0.08))
            if abs(xf_val - xf_prev) >= dmin:
                xf_act["why"] = "post-swap open to Deck B" if ts >= swap_at else "center before swap"
        prev_vals[("B", "xfader")] = xf_val
        actions.append(xf_act)

    actions.sort(key=lambda x: x["t_sec"])
    return actions
