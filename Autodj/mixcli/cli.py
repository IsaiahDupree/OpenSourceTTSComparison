import click
import pathlib
import json
from rich import print
from .analyze import analyze_folder
from .plan import write_plan
from .render import render_mix, render_video
from .recommend import recommend_next


@click.group()
def cli():
    ...


@cli.command()
@click.argument("music_folder")
@click.argument("analysis_json")
def analyze(music_folder, analysis_json):
    """Scan folder → BPM/beatgrid/key JSON."""
    analyze_folder(music_folder, analysis_json)
    print(f"[green]wrote[/green] {analysis_json}")


@cli.command()
@click.argument("analysis_json")
@click.argument("plan_json")
@click.option("--max-key-shift", default=2, type=int, help="Max semitone difference between adjacent track keys")
def plan(analysis_json, plan_json, max_key_shift):
    """Build Camelot/tempo-friendly order."""
    write_plan(analysis_json, plan_json, max_key_shift=max_key_shift)
    print(f"[green]wrote[/green] {plan_json}")


@cli.command()
@click.argument("plan_json")
@click.argument("out_audio")
@click.option("--fade", default=8.0, help="Crossfade seconds")
@click.option("--video/--no-video", default=False, help="Also render MP4 video overlay")
@click.option("--video-out", default=None, help="Video output path (defaults to out_audio with .mp4)")
@click.option("--size", default="1280x720", help="Video size WxH")
@click.option("--fps", default=30, type=int, help="Video frames per second")
@click.option("--font", default=None, help="FFmpeg drawtext font name")
@click.option("--fontfile", default=None, help="FFmpeg drawtext font file (Windows friendly)")
@click.option("--pulses/--no-pulses", default=True, help="Show beat pulse overlays in video")
@click.option("--pitch-match/--no-pitch-match", default=False, help="Pitch-shift each next track toward previous key (requires ffmpeg rubberband)")
@click.option("--max-pitch-shift", default=2, type=int, help="Max semitone shift applied when --pitch-match is on")
def render(plan_json, out_audio, fade, video, video_out, size, fps, font, fontfile, pulses, pitch_match, max_pitch_shift):
    """Render continuous mix with tempo-align + crossfades. Optionally make a video."""
    render_mix(plan_json, out_audio, fade_seconds=fade, pitch_match=pitch_match, max_pitch_shift=max_pitch_shift)
    print(f"[green]mix ready[/green] → {out_audio}")
    if video:
        out_video = video_out or str(pathlib.Path(out_audio).with_suffix(".mp4"))
        render_video(plan_json, out_audio, out_video, fade_seconds=fade, size=size, fps=fps, font=font, fontfile=fontfile, show_pulses=pulses, pitch_match=pitch_match, max_pitch_shift=max_pitch_shift)
        print(f"[green]video ready[/green] → {out_video}")


@cli.command()
@click.argument("analysis_json")
@click.option("--from-path", default=None, help="Path or basename of current track to derive key/BPM")
@click.option("--current-key", default=None, help="Current track key (e.g., 8A or Am)")
@click.option("--current-bpm", default=None, type=float, help="Current track BPM")
@click.option("--top-k", default=3, type=int, help="How many suggestions to show")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output JSON instead of pretty text")
def recommend(analysis_json, from_path, current_key, current_bpm, top_k, as_json):
    """Suggest the next tracks using key/BPM/phrase heuristics.

    Provide either --from-path to infer current key/BPM from the analysis JSON,
    or pass --current-key and --current-bpm explicitly.
    """
    try:
        results = recommend_next(
            analysis_json,
            current_key=current_key,
            current_bpm=current_bpm,
            from_path=from_path,
            top_k=top_k,
        )
    except Exception as e:
        print(f"[red]recommend error:[/red] {e}")
        return
    if as_json:
        print(json.dumps(results, indent=2))
        return
    if not results:
        print("No recommendations.")
        return
    print("[green]Top suggestions:[/green]")
    for i, r in enumerate(results, start=1):
        name = pathlib.Path(r["path"]).name if r.get("path") else "?"
        comps = r.get("components", {})
        print(f"{i:>2}. {name}  |  Key {r.get('key') or '?'}  |  {r.get('tempo', 0):.1f} BPM  |  score {r.get('score', 0):.2f}  (key={comps.get('key_match',0):.2f}, bpm={comps.get('bpm_fit',0):.2f}, phrase={comps.get('phrase_ready',0):.2f})")

@cli.command()
@click.argument("music_folder")
@click.argument("out_audio")
@click.option("--workdir", default=".mixcache.json")
@click.option("--fade", default=8.0, help="Crossfade seconds")
@click.option("--video/--no-video", default=False, help="Also render MP4 video overlay")
@click.option("--video-out", default=None, help="Video output path (defaults to out_audio with .mp4)")
@click.option("--size", default="1280x720", help="Video size WxH")
@click.option("--fps", default=30, type=int, help="Video frames per second")
@click.option("--font", default=None, help="FFmpeg drawtext font name")
@click.option("--fontfile", default=None, help="FFmpeg drawtext font file (Windows friendly)")
@click.option("--pulses/--no-pulses", default=True, help="Show beat pulse overlays in video")
@click.option("--max-key-shift", default=2, type=int, help="Max semitone difference between adjacent track keys")
@click.option("--pitch-match/--no-pitch-match", default=False, help="Pitch-shift each next track toward previous key (requires ffmpeg rubberband)")
@click.option("--max-pitch-shift", default=2, type=int, help="Max semitone shift applied when --pitch-match is on")
def auto(music_folder, out_audio, workdir, fade, video, video_out, size, fps, font, fontfile, pulses, max_key_shift, pitch_match, max_pitch_shift):
    """One-shot: analyze → plan → render (and video if requested)."""
    analysis_json = workdir + ".analysis.json"
    plan_json = workdir + ".plan.json"
    analyze_folder(music_folder, analysis_json)
    print(f"[green]wrote[/green] {analysis_json}")
    write_plan(analysis_json, plan_json, max_key_shift=max_key_shift)
    print(f"[green]wrote[/green] {plan_json}")
    render_mix(plan_json, out_audio, fade_seconds=fade, pitch_match=pitch_match, max_pitch_shift=max_pitch_shift)
    print(f"[green]mix ready[/green] → {out_audio}")
    if video:
        out_video = video_out or str(pathlib.Path(out_audio).with_suffix(".mp4"))
        render_video(plan_json, out_audio, out_video, fade_seconds=fade, size=size, fps=fps, font=font, fontfile=fontfile, show_pulses=pulses, pitch_match=pitch_match, max_pitch_shift=max_pitch_shift)
        print(f"[green]video ready[/green] → {out_video}")


if __name__ == "__main__":
    cli()

