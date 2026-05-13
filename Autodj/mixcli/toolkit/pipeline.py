import argparse, glob, json
from typing import Dict, Any, List

import numpy as np
import librosa

from .features import analyze_core
from .key_bpm import detect_key, camelot_neighbors
from .tag_io import embed_tags, write_sidecar


def analyze_one(path: str) -> Dict[str, Any]:
    core = analyze_core(path)
    y, sr = librosa.load(path, sr=22050, mono=True)
    key_name, camelot, key_conf = detect_key(y, sr)
    core["harmony"] = {
        **core.get("harmony", {}),
        "key_open": camelot,
        "key_name": key_name,
        "key_confidence": key_conf,
        "camelot_neighbors": camelot_neighbors(camelot) if camelot else {"same": [], "safe": [], "energy_boost": [], "relative": []},
    }
    # placeholder cue points
    core.setdefault("mix", {}).setdefault("cue_points", []).append({"label": "mix_in", "time": 0.0})
    return core


def calibrate_energy(library_jsons: List[Dict[str, Any]]):
    # set energy_1_10 using library loudness & percussiveness
    if not library_jsons:
        return []
    lufs = np.array([float(m.get("energy", {}).get("lufs_integrated", -14.0)) for m in library_jsons])
    perc = np.array([int(m.get("energy", {}).get("percussiveness_1_10", 5)) for m in library_jsons])
    # invert LUFS (louder → higher energy)
    lufs_z = (np.median(lufs) - lufs) / (np.std(lufs) + 1e-9)
    energy = np.clip(np.round(3 + 2 * lufs_z + 0.5 * perc / 1.0), 1, 10).astype(int)
    return energy.tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music_glob", required=True, help="e.g., 'D:/Music/**/*.[Mm][Pp]3'")
    ap.add_argument("--write_tags", action="store_true")
    ap.add_argument("--recalibrate", action="store_true")
    args = ap.parse_args()

    audio_paths = glob.glob(args.music_glob, recursive=True)
    sidecars = []
    library = []
    for p in audio_paths:
        meta = analyze_one(p)
        sidecar = write_sidecar(p, meta)
        sidecars.append(sidecar)
        library.append(meta)
        if args.write_tags:
            embed_tags(p, meta)

    # Calibration pass (optional, improves energy_1_10 to library context)
    if args.recalibrate and library:
        mapping = calibrate_energy(library)
        for i, sc in enumerate(sidecars):
            with open(sc, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta.setdefault("energy", {})["energy_1_10"] = int(mapping[i]) if i < len(mapping) else int(np.clip(np.round(5), 1, 10))
            with open(sc, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)


if __name__ == "__main__":
    main()
