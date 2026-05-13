import json
import time
import pickle
from pathlib import Path
from typing import Iterable, Iterator, List

import faiss  # type: ignore
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

from RealtimeSTT import AudioToTextRecorder  # VAD + faster-whisper
from RealtimeTTS import TextToAudioStream, SystemEngine

# Optional Piper TTS (fully offline). If missing or misconfigured, we fallback to SystemEngine.
try:
    from RealtimeTTS import PiperEngine, PiperVoice  # type: ignore
    PIPER_AVAILABLE = True
except Exception:
    PiperEngine = None  # type: ignore
    PiperVoice = None  # type: ignore
    PIPER_AVAILABLE = False

# -------------------- RAG: load index --------------------
IDX_DIR = Path("index")
FAISS_PATH = IDX_DIR / "faiss.index"
META_PATH = IDX_DIR / "meta.pkl"

if not FAISS_PATH.exists() or not META_PATH.exists():
    raise SystemExit("RAG index not found. Run: python index_repo.py --src . --out index")

INDEX = faiss.read_index(str(FAISS_PATH))
with open(META_PATH, "rb") as f:
    METAS: List[dict] = pickle.load(f)

EMB = SentenceTransformer("BAAI/bge-small-en-v1.5")


def retrieve(query: str, k: int = 8) -> List[dict]:
    q = EMB.encode(query, normalize_embeddings=True).astype("float32")
    D, I = INDEX.search(np.array([q]), k)
    return [METAS[i] for i in I[0] if 0 <= i < len(METAS)]


def build_prompt(user_q: str, contexts: List[dict]) -> str:
    ctx = "\n\n".join(
        f"[{i+1}] {c['path']}#chunk{c['chunk_id']}\n{c['text']}"
        for i, c in enumerate(contexts)
    )
    return (
        "You are a senior code assistant. Use only the CONTEXT when possible.\n"
        "If unsure, say so. Reference helpful file paths and chunk ids.\n\n"
        f"QUESTION:\n{user_q}\n\nCONTEXT:\n{ctx}\n"
    )


# -------------------- LLM: stream from Ollama --------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # e.g., "qwen2.5-coder:7b"
GEN_OPTS = {"temperature": 0.2}


def stream_ollama(prompt: str) -> Iterator[str]:
    payload = {"model": MODEL, "prompt": prompt, "stream": True, "options": GEN_OPTS}
    with requests.post(OLLAMA_URL, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            data = json.loads(line)
            if "response" in data:
                yield data["response"]
            if data.get("done"):
                break


# -------------------- TTS --------------------
PIPER_EXE = r""  # e.g., r"C:\\path\\to\\piper.exe" or just "piper" if on PATH
VOICE_ONNX = r""  # e.g., r"C:\\path\\to\\voices\\en_US-amy-medium.onnx"
VOICE_CFG = r""   # e.g., r"C:\\path\\to\\voices\\en_US-amy-medium.onnx.json"


def make_tts() -> TextToAudioStream:
    if PIPER_AVAILABLE and PIPER_EXE and VOICE_ONNX and VOICE_CFG:
        try:
            voice = PiperVoice(VOICE_ONNX, VOICE_CFG, piper_path=PIPER_EXE)  # type: ignore
            return TextToAudioStream(PiperEngine(voice))  # type: ignore
        except Exception as e:
            print(f"[TTS] Piper not ready ({e}). Falling back to SystemEngine.")
    return TextToAudioStream(SystemEngine())  # local OS voices


TTS = make_tts()


# -------------------- STT loop --------------------

def handle_query(text: str) -> None:
    if not text:
        return
    print(f"\n> You: {text}")
    ctx = retrieve(text, k=8)
    prompt = build_prompt(text, ctx)
    # Stream tokens to TTS for immediate speech
    TTS.feed(stream_ollama(prompt))
    TTS.play()  # blocking; use play_async() if you prefer


if __name__ == "__main__":
    print("Say something (VAD auto-starts). Ctrl+C to quit.")
    # You can pass params like model='base.en', language='en', wake_words='jarvis'
    rec = AudioToTextRecorder()
    try:
        while True:
            rec.text(handle_query)  # callback receives partial/final text
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
