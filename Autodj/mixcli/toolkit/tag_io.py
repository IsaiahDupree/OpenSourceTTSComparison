import json, pathlib
from typing import Dict, Any

from mutagen.id3 import ID3, TKEY, TBPM, TXXX, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4FreeForm


def write_sidecar(audio_path: str, tags: Dict[str, Any]) -> str:
    sidecar = audio_path + ".mixmeta.json"
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=2)
    return sidecar


def write_id3_mp3(path: str, key_open: str, bpm: float, tags_json: str):
    try:
        id3 = ID3(path)
    except ID3NoHeaderError:
        id3 = ID3()
    # Overwrite or add frames
    id3.setall("TKEY", [TKEY(encoding=3, text=[key_open])])
    id3.setall("TBPM", [TBPM(encoding=3, text=[str(round(bpm, 2))])])
    id3.setall("TXXX", [TXXX(encoding=3, desc="MIXMETA", text=[tags_json])])
    id3.save(path)


def write_mp4_m4a(path: str, key_open: str, bpm: float, tags_json: str):
    mp4 = MP4(path)
    mp4["----:com.apple.iTunes:MIXMETA"] = [MP4FreeForm(tags_json.encode("utf-8"))]
    mp4["\xa9key"] = key_open
    mp4["tmpo"] = int(round(bpm))
    mp4.save()


def embed_tags(audio_path: str, tags: Dict[str, Any]) -> None:
    ext = pathlib.Path(audio_path).suffix.lower()
    tags_json = json.dumps(tags, separators=(",", ":"))
    key_open = tags.get("harmony", {}).get("key_open", "")
    bpm = float(tags.get("rhythm", {}).get("bpm", 0.0))
    if ext == ".mp3":
        write_id3_mp3(audio_path, key_open, bpm, tags_json)
    elif ext in (".m4a", ".mp4", ".alac"):
        write_mp4_m4a(audio_path, key_open, bpm, tags_json)
    # sidecar for all formats
    write_sidecar(audio_path, tags)
