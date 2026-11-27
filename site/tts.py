#!/usr/bin/env -S uv run --python 3.12
# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#   "kokoro-onnx>=0.4",
#   "lameenc>=1.7",
#   "numpy>=1.26",
# ]
# ///
"""Generate MP3 narration for each essay using Kokoro-82M (kokoro-onnx)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

import lameenc
import numpy as np
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = ROOT / "essays"
AUDIO_DIR = Path(__file__).resolve().parent / "audio"
HASHES_PATH = AUDIO_DIR / ".hashes.json"
CACHE_DIR = Path.home() / ".cache" / "kokoro-onnx"

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

SAMPLE_RATE = 24000
MAX_CHUNK_CHARS = 420


def ensure_models() -> tuple[Path, Path]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    model_path = CACHE_DIR / "kokoro-v1.0.onnx"
    voices_path = CACHE_DIR / "voices-v1.0.bin"
    for url, dest in ((MODEL_URL, model_path), (VOICES_URL, voices_path)):
        if not dest.exists():
            print(f"Downloading {dest.name} to {CACHE_DIR}...", flush=True)
            urllib.request.urlretrieve(url, dest)
    return model_path, voices_path


def clean_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    cur = ""
    for s in sentences:
        if not s:
            continue
        if len(s) > max_chars:
            for part in re.split(r"(?<=[,;:])\s+", s):
                if len(cur) + len(part) + 1 <= max_chars:
                    cur = f"{cur} {part}".strip()
                else:
                    if cur:
                        chunks.append(cur)
                    cur = part
            continue
        if len(cur) + len(s) + 1 <= max_chars:
            cur = f"{cur} {s}".strip()
        else:
            if cur:
                chunks.append(cur)
            cur = s
    if cur:
        chunks.append(cur)
    return chunks


def essay_to_segments(md: str) -> list[tuple[str, float, float]]:
    """Return list of (spoken_text, pause_before_sec, pause_after_sec)."""
    lines = md.replace("\r\n", "\n").split("\n")
    segments: list[tuple[str, float, float]] = []
    para: list[str] = []
    in_code = False

    def flush_para() -> None:
        if not para:
            return
        text = clean_inline(" ".join(para))
        para.clear()
        if not text:
            return
        chunks = split_sentences(text)
        for idx, chunk in enumerate(chunks):
            after = 0.7 if idx == len(chunks) - 1 else 0.14
            segments.append((chunk, 0.0, after))

    for raw in lines:
        s = raw.strip()
        if s.startswith("```"):
            flush_para()
            in_code = not in_code
            continue
        if in_code:
            continue
        if not s:
            flush_para()
            continue
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
            flush_para()
            segments.append(("", 0.5, 0.0))
            continue
        if s.startswith("# "):
            flush_para()
            segments.append((clean_inline(s[2:]), 0.0, 1.0))
            continue
        if re.match(r"^#{2,6}\s+", s):
            flush_para()
            heading = re.sub(r"^#{2,6}\s+", "", s)
            segments.append((clean_inline(heading), 1.35, 0.7))
            continue
        if s.startswith(">"):
            s = s.lstrip("> ").strip()
            if not s:
                flush_para()
                continue
        s = re.sub(r"^([-*]|\d+\.)\s+", "", s)
        para.append(s)

    flush_para()
    return segments


def encode_mp3(pcm_float: np.ndarray, out_path: Path, bitrate: int = 64) -> None:
    clipped = np.clip(pcm_float, -1.0, 1.0)
    pcm_i16 = (clipped * 32767.0).astype(np.int16)

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(SAMPLE_RATE)
    encoder.set_channels(1)
    encoder.set_quality(2)

    mp3_bytes = encoder.encode(pcm_i16.tobytes()) + encoder.flush()
    out_path.write_bytes(mp3_bytes)


def synthesize_essay(kokoro: Kokoro, md_path: Path, out_path: Path, voice: str, speed: float) -> float:
    md = md_path.read_text(encoding="utf-8")
    segments = essay_to_segments(md)
    parts: list[np.ndarray] = []
    lang = "en-gb" if voice.startswith(("bf_", "bm_")) else "en-us"

    for text, before_s, after_s in segments:
        if before_s > 0:
            parts.append(np.zeros(int(before_s * SAMPLE_RATE), dtype=np.float32))
        if text:
            samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
            if sr != SAMPLE_RATE:
                raise RuntimeError(f"Unexpected sample rate {sr}")
            parts.append(samples.astype(np.float32, copy=False))
        if after_s > 0:
            parts.append(np.zeros(int(after_s * SAMPLE_RATE), dtype=np.float32))

    audio = np.concatenate(parts) if parts else np.zeros(SAMPLE_RATE, dtype=np.float32)
    encode_mp3(audio, out_path)
    return len(audio) / SAMPLE_RATE


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Kokoro-82M MP3 audio for essays.")
    parser.add_argument("slugs", nargs="*", help="Optional essay slugs to generate (default: all).")
    parser.add_argument("--voice", default="bf_emma", help="Kokoro voice name (default: bf_emma).")
    parser.add_argument("--speed", type=float, default=0.95, help="Speech speed (default: 0.95).")
    parser.add_argument("--force", action="store_true", help="Regenerate even if essay hash is unchanged.")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    if HASHES_PATH.exists():
        hashes = json.loads(HASHES_PATH.read_text(encoding="utf-8"))

    targets = sorted(ESSAYS_DIR.glob("*.md"))
    if args.slugs:
        wanted = set(args.slugs)
        targets = [p for p in targets if p.stem in wanted]
        if not targets:
            sys.exit(f"No matching essays for: {', '.join(args.slugs)}")

    model_path, voices_path = ensure_models()
    kokoro = Kokoro(str(model_path), str(voices_path))

    for md_path in targets:
        slug = md_path.stem
        out_path = AUDIO_DIR / f"{slug}.mp3"
        digest = hashlib.sha256(
            f"{args.voice}:{args.speed}:".encode() + md_path.read_bytes()
        ).hexdigest()[:16]
        if not args.force and out_path.exists() and hashes.get(slug) == digest:
            print(f"Skipping {slug} (up to date)", flush=True)
            continue

        print(f"Generating {slug}.mp3 ({args.voice})...", flush=True)
        duration_s = synthesize_essay(kokoro, md_path, out_path, args.voice, args.speed)
        hashes[slug] = digest
        HASHES_PATH.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"  -> {out_path.name}: {duration_s / 60:.1f} min, {size_mb:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
