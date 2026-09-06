#!/usr/bin/env python3
"""Trim leading/trailing breath artifacts — two methods.

energy  hand-tuned gate: scan from the edges for the first SUSTAINED region
        above (peak - 18 dB); word-internal soft consonants are protected
        because they sit between louder vowels. Fast, no model.
vad     silero-vad gating: a 2 MB trained model classifies speech vs
        breaths/noise; everything outside the first..last speech segment
        is cut. More robust to soft onsets and odd breath levels.

Usage:
  trim_breaths.py [--method energy|vad] [--out DIR] file.mp3 [...]

In place by default; with --out, writes <name>.mp3 into DIR (originals kept).
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np

SR = 24000
WIN = int(SR * 0.01)
THRESHOLD_REL_DB = -18.0
SUSTAIN_FRAMES = 3
MAX_TRIM = int(SR * 0.4)
FADE = int(SR * 0.04)


def load(path: str, sr: int = SR) -> np.ndarray:
    raw = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def save(path: str, audio: np.ndarray) -> None:
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', tmp_path],
                   input=audio.astype(np.float32).tobytes(), check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp_path, '-codec:a', 'libmp3lame',
                    '-qscale:a', '4', path], check=True)
    os.remove(tmp_path)


def db_frames(audio: np.ndarray) -> np.ndarray:
    frames = [np.sqrt(np.mean(audio[i:i + WIN] ** 2)) for i in range(0, max(1, len(audio) - WIN), WIN)]
    return 20 * np.log10(np.maximum(np.array(frames), 1e-9))


def first_sustained(db: np.ndarray, threshold: float, from_end: bool = False) -> int:
    order = range(len(db) - 1, -1, -1) if from_end else range(len(db))
    for i in order:
        if from_end:
            window = [db[j] for j in range(max(0, i - SUSTAIN_FRAMES + 1), i + 1)]
        else:
            window = [db[j] for j in range(i, min(i + SUSTAIN_FRAMES, len(db)))]
        if len(window) == SUSTAIN_FRAMES and all(v >= threshold - 3 for v in window):
            return i
    return 0 if not from_end else len(db) - 1


def fade_edges(audio: np.ndarray) -> np.ndarray:
    fade = min(FADE, len(audio) // 4)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    return audio


def trim_energy(audio: np.ndarray) -> tuple[np.ndarray, int, int]:
    db = db_frames(audio)
    if len(db) == 0 or db.max() < -60:
        return audio, 0, 0
    threshold = db.max() + THRESHOLD_REL_DB
    start_frame = first_sustained(db, threshold)
    end_frame = first_sustained(db, threshold, from_end=True)
    start = min(start_frame * WIN, MAX_TRIM)
    end = min((len(db) - 1 - end_frame) * WIN, MAX_TRIM)
    if end > 0:
        audio = audio[:-end]
    if start > 0:
        audio = audio[start:]
    return fade_edges(audio), start, end


def trim_vad(path: str) -> tuple[np.ndarray, int, int]:
    from silero_vad import load_silero_vad, get_speech_timestamps
    model = load_silero_vad()
    vad_sr = 16000
    audio = load(path)
    speech = get_speech_timestamps(load(path, vad_sr), model, sampling_rate=vad_sr)
    if not speech:
        return audio, 0, 0
    scale = SR / vad_sr
    start = int(max(0, speech[0]['start'] * scale - SR * 0.02))
    end = int(max(0, len(audio) - speech[-1]['end'] * scale - SR * 0.02))
    trimmed = audio[start:len(audio) - end if end else len(audio)]
    return fade_edges(trimmed), start, end


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', choices=['energy', 'vad'], default='energy')
    parser.add_argument('--out', help='write result to DIR instead of in place')
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    for path in args.files:
        if args.method == 'vad':
            trimmed, cut_start, cut_end = trim_vad(path)
        else:
            audio = load(path)
            trimmed, cut_start, cut_end = trim_energy(audio)
        target = os.path.join(args.out, os.path.basename(path)) if args.out else path
        if args.out:
            os.makedirs(args.out, exist_ok=True)
        save(target, trimmed)
        print(f"{os.path.basename(path)}: -{cut_start / SR * 1000:.0f}ms head, -{cut_end / SR * 1000:.0f}ms tail")


if __name__ == '__main__':
    main()