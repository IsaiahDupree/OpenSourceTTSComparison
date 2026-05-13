import argparse
import os
import pickle
from pathlib import Path
from typing import Iterable, Iterator, List

import faiss  # type: ignore
import numpy as np
from sentence_transformers import SentenceTransformer

# File types to index
ALLOWED_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".md", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".cs",
    ".rb", ".php", ".kt", ".swift", ".sql", ".yml", ".yaml",
    ".toml", ".ini", ".json", ".txt"
}

# Excluded directories (relative or nested)
EXCLUDED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "envs",
    "venv_chatterbox", "venv_chatterbox311", "index", "__pycache__",
    "dist", "build", "downloads", "temp_downloads"
}

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_BYTES = 2_000_000  # 2 MB


def iter_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in ALLOWED_EXTS:
            continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield p


def chunk(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterator[str]:
    i, n = 0, len(text)
    step = max(1, size - overlap)
    while i < n:
        yield text[i : i + size]
        i += step


def build_index(src_dir: str, out_dir: str = "index") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"[index] Loading embedding model 'BAAI/bge-small-en-v1.5' (384-d)...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    embeds: List[np.ndarray] = []
    metadatas: List[dict] = []

    root = Path(src_dir).resolve()
    print(f"[index] Scanning files under: {root}")

    for file in iter_files(root):
        try:
            txt = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for j, ch in enumerate(chunk(txt)):
            metadatas.append({
                "path": str(file),
                "chunk_id": j,
                "text": ch,
            })
            vec = model.encode(ch, normalize_embeddings=True)
            embeds.append(np.asarray(vec, dtype="float32"))

    if not embeds:
        raise SystemExit("[index] No files found to index.")

    mat = np.vstack(embeds).astype("float32")
    dim = mat.shape[1]
    print(f"[index] Building FAISS IndexFlatIP with dim={dim} and {mat.shape[0]} chunks...")
    index = faiss.IndexFlatIP(dim)
    index.add(mat)

    faiss_path = out / "faiss.index"
    meta_path = out / "meta.pkl"
    faiss.write_index(index, str(faiss_path))
    with open(meta_path, "wb") as f:
        pickle.dump(metadatas, f)

    print(f"[index] Wrote index to {faiss_path.resolve()}")
    print(f"[index] Wrote metadata to {meta_path.resolve()}")
    print(f"[index] Done. Total chunks: {len(metadatas)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a FAISS index over the repo")
    parser.add_argument("--src", dest="src", default=".", help="Source directory to index (default: .)")
    parser.add_argument("--out", dest="out", default="index", help="Output directory for index files (default: index)")
    args = parser.parse_args()

    build_index(src_dir=args.src, out_dir=args.out)
