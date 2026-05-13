import subprocess, json, shutil, pathlib, time
import numpy as np
import librosa


def run_keyfinder(path: str) -> str | None:
    exe = shutil.which("keyfinder-cli")
    if not exe:
        return None
    try:
        out = subprocess.check_output([exe, path], text=True).strip()
        return out or None  # e.g., "A", "C#m", "Eb"
    except Exception:
        return None


# basic Krumhansl-style fallback using chroma (coarse but works)
# major/minor profiles (Krumhansl-Kessler normalized)
_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

_PITCHES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def estimate_key_fallback(y, sr):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, norm=None)
    chroma = chroma.mean(axis=1)
    chroma = chroma / (np.linalg.norm(chroma) + 1e-9)
    scores = {}
    for i, p in enumerate(_PITCHES):
        scores[f"{p}"] = np.dot(np.roll(_MAJ, i), chroma)
        scores[f"{p}m"] = np.dot(np.roll(_MIN, i), chroma)
    return max(scores, key=scores.get)  # e.g., "Am"


def analyze_file(path: str):
    y, sr = librosa.load(path, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")  # DP beat tracker :contentReference[oaicite:5]{index=5}
    key = run_keyfinder(path)
    if not key:
        key = estimate_key_fallback(y, sr)
    return {
        "path": str(path),
        "tempo": float(tempo),
        "beats": [float(b) for b in beats],
        "key": key,
    }


def analyze_folder(folder: str, out_json: str):
    folder = pathlib.Path(folder)
    tracks = []
    candidates = [
        p for p in sorted(folder.glob("*"))
        if p.suffix.lower() in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No audio files found in folder '{folder}'. Supported: .mp3 .wav .flac .m4a .ogg"
        )
    print(f"[analyze] Found {len(candidates)} audio files in {folder}")
    t_total = time.perf_counter()
    for i, p in enumerate(candidates, start=1):
        t0 = time.perf_counter()
        print(f"[analyze] {i}/{len(candidates)}: {p.name} ...", flush=True)
        tracks.append(analyze_file(str(p)))
        dt = time.perf_counter() - t0
        print(f"[analyze] done {p.name} in {dt:.2f}s", flush=True)
    print(f"[analyze] Completed {len(tracks)} files in {time.perf_counter() - t_total:.2f}s")
    with open(out_json, "w") as f:
        json.dump({"tracks": tracks}, f, indent=2)
