import subprocess, tempfile, pathlib, json, shutil, os
import librosa
from .plan import key_to_pc, semitone_diff


def has_rubberband():
    # detect ffmpeg rubberband filter (higher quality) :contentReference[oaicite:7]{index=7}
    try:
        out = subprocess.check_output(["ffmpeg", "-hide_banner", "-filters"], text=True)
        return "rubberband" in out
    except Exception:
        return False


def atempo_chain(ratio: float):
    # ffmpeg atempo only supports ~0.5–2.0 per stage; chain if needed :contentReference[oaicite:8]{index=8}
    chain = []
    r = ratio
    while r < 0.5 or r > 2.0:
        step = 2.0 if r > 2 else 0.5
        chain.append(f"atempo={step}")
        r /= step
    chain.append(f"atempo={r:.6f}")
    return ",".join(chain)


def stretch_cmd(inp, outp, tempo_ratio: float, pitch_ratio: float | None = None):
    if has_rubberband():
        filt = f"rubberband=tempo={tempo_ratio:.6f}"
        if pitch_ratio is not None and abs(pitch_ratio - 1.0) > 1e-6:
            filt += f":pitch={pitch_ratio:.6f}"
        return [
            "ffmpeg",
            "-y",
            "-i",
            inp,
            "-filter:a",
            filt,
            "-vn",
            outp,
        ]
    else:
        # Fallback: high-quality tempo change only; pitch not applied without rubberband
        return [
            "ffmpeg",
            "-y",
            "-i",
            inp,
            "-filter:a",
            atempo_chain(tempo_ratio),
            "-vn",
            outp,
        ]


def crossfade_cmd(a, b, outp, fade_s=8.0):
    # acrossfade does equal-power curves and handles overlap. :contentReference[oaicite:9]{index=9}
    return [
        "ffmpeg",
        "-y",
        "-i",
        a,
        "-i",
        b,
        "-filter_complex",
        f"[0:a][1:a]acrossfade=d={fade_s}:c1=exp:c2=exp[a]",
        "-map",
        "[a]",
        "-vn",
        outp,
    ]


def render_mix(plan_json: str, out_path: str, fade_seconds=8.0, pitch_match: bool = False, max_pitch_shift: int = 2):
    if not os.path.exists(plan_json):
        raise FileNotFoundError(f"Plan file '{plan_json}' not found. Run the plan step first.")
    order = json.load(open(plan_json))["order"]
    if not order:
        raise ValueError(f"Plan '{plan_json}' contains no tracks. Ensure analyze/plan found audio files.")
    print(f"[render] Mixing {len(order)} tracks with crossfade={fade_seconds:.1f}s")
    enable_pitch = bool(pitch_match and has_rubberband())
    if pitch_match and not enable_pitch:
        print("[render] pitch-match requested but ffmpeg rubberband filter not found; skipping pitch shift")
    tmp = tempfile.mkdtemp(prefix="mixcli_")
    try:
        # 1) BPM-align each next track to previous
        prepped = []
        prev_bpm = None
        prev_key = None
        for i, tr in enumerate(order):
            src = tr["path"]
            bpm = tr["tempo"]
            key = tr.get("key")
            if i == 0:
                prepped.append(src)
                prev_bpm = bpm
                prev_key = key
                continue
            ratio = max(0.25, min(4.0, prev_bpm / max(bpm, 1e-6)))
            # Optional pitch shift toward previous key within limit
            pitch_semitones = 0
            pitch_ratio = None
            if enable_pitch:
                a = key_to_pc(key)
                b = key_to_pc(prev_key)
                if a is not None and b is not None:
                    d = semitone_diff(a, b)  # shift needed to move current to previous
                    limit = max(0, int(max_pitch_shift))
                    if abs(d) > limit:
                        d = limit if d > 0 else -limit
                    pitch_semitones = d
                    if d != 0:
                        pitch_ratio = 2.0 ** (d / 12.0)
            outp = str(pathlib.Path(tmp) / f"t{i:03d}.wav")
            if pitch_ratio is not None:
                print(f"[render] stretch {i}: {os.path.basename(src)} tempo={ratio:.3f}  pitch={pitch_semitones:+d} st")
            else:
                print(f"[render] stretch {i}: {os.path.basename(src)} tempo={ratio:.3f}")
            subprocess.check_call(stretch_cmd(src, outp, ratio, pitch_ratio))
            print(f"[render] stretch {i} done")
            prepped.append(outp)
            # keep previous BPM as the reference; do not advance it
            prev_key = key
        # 2) Chain crossfades pairwise
        cur = prepped[0]
        for i, nxt in enumerate(prepped[1:], start=1):
            outp = str(pathlib.Path(tmp) / f"x{i:03d}.wav")
            print(f"[render] crossfade {i}: {os.path.basename(cur)} + {os.path.basename(nxt)} d={fade_seconds:.1f}s")
            subprocess.check_call(crossfade_cmd(cur, nxt, outp, fade_seconds))
            print(f"[render] crossfade {i} done")
            cur = outp
        # Write final output
        ext = pathlib.Path(out_path).suffix.lower()
        if ext == ".wav":
            print(f"[render] copy WAV → {out_path}")
            shutil.copyfile(cur, out_path)
        else:
            # Let ffmpeg pick sensible defaults based on container
            print(f"[render] encode → {out_path}")
            subprocess.check_call(["ffmpeg", "-y", "-i", cur, out_path])
    finally:
        # keep temp if you want to debug; otherwise cleanup
        for root, dirs, files in os.walk(tmp, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(tmp)


# -------------------- Video rendering helpers --------------------

def _escape_drawtext_text(s: str) -> str:
    # Basic escaping for drawtext (ASCII-only for Windows codepages)
    s = s.replace("\\", "\\\\")
    s = s.replace(":", "\\:")
    s = s.replace(",", "\\,")
    s = s.replace("'", "\\'")
    return s


def _escape_filter_value(s: str) -> str:
    # Escape value used in drawtext options like fontfile or font
    s = s.replace("\\", "\\\\")
    s = s.replace(":", "\\:")
    s = s.replace(",", "\\,")
    return s


def _build_timeline(order, fade_seconds: float, pitch_match: bool = False, max_pitch_shift: int = 2):
    """Compute start/end times and stretch ratios for each track in the final mix.
    Returns list of entries with keys: index, path, title, key, camelot, tempo,
    target_bpm, ratio, start, end, beats_scaled
    """
    if not order:
        return []
    prev_bpm = float(order[0].get("tempo") or 120.0)
    prev_key = order[0].get("key")
    timeline = []
    t_cursor = 0.0
    for i, tr in enumerate(order):
        bpm = float(tr.get("tempo") or prev_bpm)
        ratio = 1.0 if i == 0 else max(0.25, min(4.0, prev_bpm / max(bpm, 1e-6)))
        # Optional pitch shift toward previous key within limit
        pitch_semitones = 0
        pitch_ratio = 1.0
        if i > 0 and pitch_match:
            a = key_to_pc(tr.get("key"))
            b = key_to_pc(prev_key)
            if a is not None and b is not None:
                d = semitone_diff(a, b)
                limit = max(0, int(max_pitch_shift))
                if abs(d) > limit:
                    d = limit if d > 0 else -limit
                pitch_semitones = d
                pitch_ratio = 2.0 ** (d / 12.0)
        # duration from source file; apply stretch for i>0
        try:
            dur_orig = float(librosa.get_duration(filename=tr["path"]))
        except Exception:
            dur_orig = 0.0
        dur = dur_orig if i == 0 else (dur_orig / ratio)
        start = t_cursor
        end = start + dur
        beats = [float(b) for b in tr.get("beats", [])]
        beats_scaled = beats if i == 0 else [b / ratio for b in beats]
        timeline.append({
            "index": i,
            "path": tr["path"],
            "title": os.path.basename(tr["path"]),
            "key": tr.get("key"),
            "camelot": tr.get("camelot"),
            "tempo": bpm,
            "target_bpm": prev_bpm if i > 0 else bpm,
            "ratio": ratio,
            "pitch_semitones": pitch_semitones,
            "pitch_ratio": pitch_ratio,
            "start": start,
            "end": end,
            "beats_scaled": beats_scaled,
        })
        # overlap next by fade
        t_cursor = end - fade_seconds
        prev_key = tr.get("key")
    return timeline


def _format_hms(t: float) -> str:
    t = max(0.0, float(t))
    m, s = divmod(int(round(t)), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def _make_filter_script(timeline, fade_seconds: float, size: str, fps: int, font: str | None, fontfile: str | None, show_pulses: bool = True) -> str:
    W, H = (int(size.split("x")[0]), int(size.split("x")[1]))
    cur_label = "[0:v]"
    lines = []
    if fontfile:
        font_arg = f":fontfile={_escape_filter_value(fontfile)}"
    elif font:
        font_arg = f":font={_escape_filter_value(font)}"
    else:
        font_arg = ""

    # Title (ASCII hyphen to avoid Unicode)
    title = _escape_drawtext_text("mixcli - Auto-Mix")
    lines.append(f"{cur_label} drawtext=text='{title}'{font_arg}:fontsize=36:fontcolor=white:x=40:y=30:box=1:boxcolor=black@0.4 [v0]")
    cur_label = "[v0]"

    # For each track: Now/Next info
    beat_cap = 300 if len(timeline) > 30 else 1000
    # Cap total pulse drawops across the whole graph to avoid Windows cmd length issues
    tracks_count = len(timeline) if timeline else 1
    pulses_budget_total = 500
    per_track_budget = max(60, pulses_budget_total // max(1, tracks_count))
    for i, tr in enumerate(timeline):
        s = tr["start"]; e = tr["end"]
        next_start = timeline[i+1]["start"] if i + 1 < len(timeline) else None
        # Now: title
        now_text = _escape_drawtext_text(f"Now: {tr['title']}")
        lines.append(f"{cur_label} drawtext=text='{now_text}'{font_arg}:fontsize=32:fontcolor=white:x=40:y=90:box=1:boxcolor=black@0.4:enable='between(t,{s:.3f},{e:.3f})' [v{i}a]")
        cur_label = f"[v{i}a]"
        # Now: details
        pitch_txt = ""
        if int(tr.get("pitch_semitones", 0)) != 0:
            ps = int(tr.get("pitch_semitones", 0))
            pitch_txt = f"    Pitch: {ps:+d} st"
        det = _escape_drawtext_text(f"Key: {tr.get('key') or '?'} ({tr.get('camelot') or '?'})    BPM: {tr.get('target_bpm'):.1f}    Stretch: {tr['ratio']:.3f}x{pitch_txt}")
        lines.append(f"{cur_label} drawtext=text='{det}'{font_arg}:fontsize=26:fontcolor=white:x=40:y=130:box=1:boxcolor=black@0.4:enable='between(t,{s:.3f},{e:.3f})' [v{i}b]")
        cur_label = f"[v{i}b]"
        # Times
        tline = _escape_drawtext_text(f"{_format_hms(s)} → {_format_hms(e)}  (Δ {_format_hms(e - s)})")
        lines.append(f"{cur_label} drawtext=text='{tline}'{font_arg}:fontsize=24:fontcolor=white:x=40:y=165:box=1:boxcolor=black@0.4:enable='between(t,{s:.3f},{e:.3f})' [v{i}c]")
        cur_label = f"[v{i}c]"
        # Next info only during crossfade window
        if next_start is not None:
            ne = timeline[i+1]
            xs = max(s, e - fade_seconds)
            xe = e
            next_text = _escape_drawtext_text(f"Next: {ne['title']}  Key {ne.get('key') or '?'} ({ne.get('camelot') or '?'})  BPM {ne.get('tempo'):.1f} → {ne.get('target_bpm'):.1f}")
            lines.append(f"{cur_label} drawtext=text='{next_text}'{font_arg}:fontsize=26:fontcolor=yellow:x=40:y=205:box=1:boxcolor=black@0.4:enable='between(t,{xs:.3f},{xe:.3f})' [v{i}d]")
            cur_label = f"[v{i}d]"
        # Beat pulses: small box that flashes at each beat of this track (sampled)
        if show_pulses:
            beats_seq = tr.get("beats_scaled", [])[:beat_cap]
            # Sample pulses to stay within per-track budget
            allowed = per_track_budget
            if len(beats_seq) > allowed:
                step = (len(beats_seq) + allowed - 1) // allowed  # ceiling division
            else:
                step = 1
            for b in beats_seq[::step]:
                bs = tr["start"] + b
                be = bs + 0.08
                lines.append(f"{cur_label} drawbox=x=w-100:y=40:w=24:h=24:color=deepskyblue@0.9:t=fill:enable='between(t,{bs:.3f},{be:.3f})' [v{i}p]")
                cur_label = f"[v{i}p]"

        # Crossfade progress bar (during last fade of this segment)
        if next_start is not None:
            s0 = e - fade_seconds
            # background bar
            lines.append(f"{cur_label} drawbox=x=40:y=h-60:w=w-80:h=14:color=white@0.15:t=fill:enable='between(t,{s0:.3f},{e:.3f})' [v{i}q]")
            cur_label = f"[v{i}q]"
            # foreground bar with animated width
            prog = f"(w-80)*( (t-{s0:.3f})/{fade_seconds:.3f} )"
            lines.append(f"{cur_label} drawbox=x=40:y=h-60:w={prog}:h=14:color=lime@0.8:t=fill:enable='between(t,{s0:.3f},{e:.3f})' [v{i}r]")
            cur_label = f"[v{i}r]"

    # Final label
    lines[-1] = lines[-1].replace(cur_label, "[vout]") if lines else "[0:v] null [vout]"
    # But the above replacement targets the last appended line; ensure last output is [vout]
    if lines and not lines[-1].endswith("[vout]"):
        # force last to map to vout
        last = lines[-1]
        last = last[: last.rfind("[")] + "[vout]"
        lines[-1] = last

    return "\n".join(lines)


def render_video(plan_json: str, audio_path: str, out_video: str, fade_seconds=8.0, size: str = "1280x720", fps: int = 30, font: str | None = None, fontfile: str | None = None, show_pulses: bool = True, pitch_match: bool = False, max_pitch_shift: int = 2):
    order = json.load(open(plan_json))["order"]
    pm = bool(pitch_match and has_rubberband())
    if pitch_match and not pm:
        print("[video] pitch-match requested but ffmpeg rubberband filter not found; disabling pitch overlay info")
    timeline = _build_timeline(order, fade_seconds, pitch_match=pm, max_pitch_shift=max_pitch_shift)
    # Approx audio duration for color source; we also use -shortest
    try:
        total_dur = float(librosa.get_duration(filename=audio_path))
    except Exception:
        total_dur = timeline[-1]["end"] if timeline else 0.0
    pulses = sum(len(tr.get("beats_scaled", [])) for tr in timeline)
    print(f"[video] Tracks: {len(timeline)}  duration≈{total_dur:.1f}s ({total_dur/60:.1f} min)  size={size}  fps={fps}")
    if show_pulses:
        print(f"[video] Beat pulses (capped per track): ~{pulses}")
    else:
        print(f"[video] Beat pulses disabled")
    script = _make_filter_script(timeline, fade_seconds, size, fps, font, fontfile, show_pulses=show_pulses)
    with tempfile.TemporaryDirectory(prefix="mixcli_vid_") as td:
        script_path = str(pathlib.Path(td) / "filters.txt")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        cmd = [
            "ffmpeg","-y",
            "-f","lavfi","-i", f"color=c=black:s={size}:r={fps}:d={max(total_dur,0.1):.3f}",
            "-i", audio_path,
            "-filter_complex_script", script_path,
            "-map", "[vout]",
            "-map", "1:a",
            "-c:v","libx264","-pix_fmt","yuv420p","-shortest","-c:a","aac","-b:a","192k",
            out_video,
        ]
        print(f"[video] ffmpeg starting → {out_video}")
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print(f"[video] filter_complex_script failed (rc={e.returncode}); retrying with inline -filter_complex")
            inline_graph = script.replace("\n", ";")
            cmd2 = [
                "ffmpeg","-y",
                "-f","lavfi","-i", f"color=c=black:s={size}:r={fps}:d={max(total_dur,0.1):.3f}",
                "-i", audio_path,
                "-filter_complex", inline_graph,
                "-map", "[vout]",
                "-map", "1:a",
                "-c:v","libx264","-pix_fmt","yuv420p","-shortest","-c:a","aac","-b:a","192k",
                out_video,
            ]
            try:
                subprocess.check_call(cmd2)
            except OSError as oe:
                # Windows: command line too long when many pulses are present
                if getattr(oe, "winerror", None) == 206:
                    print("[video] inline filter graph too long on Windows; retrying without beat pulses")
                    script_np = _make_filter_script(timeline, fade_seconds, size, fps, font, fontfile, show_pulses=False)
                    inline_graph_np = script_np.replace("\n", ";")
                    cmd3 = [
                        "ffmpeg","-y",
                        "-f","lavfi","-i", f"color=c=black:s={size}:r={fps}:d={max(total_dur,0.1):.3f}",
                        "-i", audio_path,
                        "-filter_complex", inline_graph_np,
                        "-map", "[vout]",
                        "-map", "1:a",
                        "-c:v","libx264","-pix_fmt","yuv420p","-shortest","-c:a","aac","-b:a","192k",
                        out_video,
                    ]
                    subprocess.check_call(cmd3)
                else:
                    raise
