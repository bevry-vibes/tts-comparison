# TTS showdown — full findings (2026-09-06)

Target: replace Sumba Bisa's machine-sounding 16 kHz Piper `en_GB-alan-low` word audio. Constraints: Apple-Silicon MacBook (CPU, no CUDA), free/key-less, offline, ≥22 kHz, British English preferred. Sample set: `bird stop vision about the kite` + "The best sand in the land!" + "Sumba bisa!" — chosen to expose rhotics, clusters, /ʒ/, schwa, weak forms and connected speech.

Sources: [Artificial Analysis open-weights leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice/open-weights), [awesome-ai-voice](https://github.com/wildminder/awesome-ai-voice), and per-model Hugging Face cards (read 2026-09-06).

## Auditioned

| Engine | Elo (AA) | License | Size | Runtime used here | Output | Voices | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Kokoro 82M v1.0](https://huggingface.co/hexgrad/Kokoro-82M) | 1060 | Apache-2.0 | 82M | official pypi `kokoro` on CPU (py3.12 venv) | 24 kHz | 8 British (4 F / 4 M) | 1-line pipeline; needs `en_core_web_sm` + a venv ≤ py3.13 (spaCy wheels); fastest generation of all tried |
| [Piper en_GB-alan-medium](https://huggingface.co/rhasspy/piper-voices) | n/a | MIT | 63 MB | piper1-gpl on CPU | 22.05 kHz | the incumbent | Same voice as the app's current audio, one quality tier up — isolates the "16 kHz low" variable |
| [Breeze TTS 2 Q8_0](https://huggingface.co/BreezeBlue/Breeze-TTS-2) | 1215 (#1) | BreezeBlue Research & Non-Commercial (code Apache-2.0) | 3.47B / 3.3 GB Q8 | [Breeze-TTS-2.cpp](https://github.com/HoppouAI/Breeze-TTS-2.cpp) ggml on macOS (Metal/CPU) — official runtime is CUDA-only | 24 kHz | voice design/clone (EN+ZH) | Leaderboard #1; community runtime builds cleanly with `-DBREEZE_VULKAN=OFF`; slower generation, voice-designable accent |
| [Higgs Audio v3 TTS 4B](https://huggingface.co/bosonai/higgs-tts-3-4b) | 1038 | Boson research & non-commercial (creator attribution grant) | 4.65B / ~4.7 GB bf16 | [mlx-audio](https://github.com/Blaizzy/mlx-audio) on Apple Silicon Metal — the card's documented Mac path (the raw transformers path is CUDA-only) | 24 kHz | cloning + zero-shot default; GB English in the polished tier | MLX converts/downloads its own weights on first run; generation comfortably faster than real time on Metal |
| [Chatterbox](https://huggingface.co/ResembleAI/chatterbox) | 1021 | MIT | 0.5B | official pypi `chatterbox-tts`, `device='cpu'` (MPS crashes) | ~24 kHz | cloning + built-in default | Needs `setuptools<81` in uv venvs (perth uses `pkg_resources`); no preset British voice; PerTh watermark embedded |
| [Magpie-Multilingual 357M](https://huggingface.co/nvidia/magpie_tts_multilingual_357m) | 1065 | NVIDIA Open Model License (commercial-ready) | 364M / 449 MB GGUF | [NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) `cpu-tts` preset | 22.05 kHz | 5 US voices (Aria/Jason/Leo/Sofia/John) | Great CLI (`nemo-speech pull magpie`); **no British voice** — accent conflict with the app's AU-leaning teaching |

## Eliminated (with evidence)

| Engine | Elo | Why eliminated |
| --- | --- | --- |
| [VibeVoice 1.5B](https://huggingface.co/microsoft/VibeVoice-1.5B) | 969 | Embeds an **audible AI disclaimer** in every generation — disqualifying; also 3B BF16 + research-only advisory |
| [Voxtral 4B TTS](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603) | 1078 | vLLM/GPU-only (≥16 GB VRAM per card) + CC BY-NC 4.0 weights |
| Fish Audio S2 Pro | 1128 | No usable open CPU runtime; Fish's open stack is multi-billion GPU-class |
| Step Audio EditX | 1104 | StepFun Step-Audio family, 13B-class GPU |

## Skipped (Apache-2.0 but wrong fit)

- **Qwen3-TTS 12Hz 1.7B CustomVoice** — CUDA-documented; 9 preset speakers but the English voices (Ryan, Aiden) are US-accent; no British timbre. Revisit with a GPU.
- **VoxCPM2** — CUDA ≥ 12 + ~8 GB VRAM documented; no British voice list. Revisit with a GPU.
- **Maya1, Zonos, OpenVoice v2, XTTS v2, StyleTTS 2, MetaVoice** — not requested; older or GPU-oriented; XTTS/Coqui is effectively abandoned.

## Toolchain locations (outside the repo, by design)

`~/.cache/sumba-tts/` — python venvs (`kokoro-venv`, `piper-venv`, `chatterbox-venv`), Breeze runtime + Q8 weights. `~/.cache/nemo-build/src/` — NeMo-Speech.cpp + its model cache in `~/Library/Caches/NeMoSpeech/`. `data/higgs/` (in the sumba-bisa repo, gitignored) — Higgs weights.

> Caution learned the hard way: never host model weights or run third-party CMake builds inside the repo's `data/` directory — a NeMo build wiped the directory once. Venvs need `pip` + `en_core_web_sm` installed explicitly when created with `uv venv`.

## Setup quick reference

```bash
# kokoro (py3.12 venv; model cached at ~/.cache/huggingface)
uv venv ~/.cache/sumba-tts/kokoro-venv --python ~/.local/bin/python3.12
uv pip install --python ~/.cache/sumba-tts/kokoro-venv/bin/python kokoro soundfile pip \
  https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# breeze (community ggml runtime, Metal/CPU)
git clone https://github.com/HoppouAI/Breeze-TTS-2.cpp ~/.cache/sumba-tts/breeze-cpp
cd ~/.cache/sumba-tts/breeze-cpp && git submodule update --init --recursive
cmake -S . -B build -DBREEZE_VULKAN=OFF && cmake --build build -j 8

# magpie (NVIDIA official C++ runtime)
git clone https://github.com/NVIDIA/NeMo-Speech.cpp ~/.cache/nemo-build/src
cd ~/.cache/nemo-build/src && git submodule update --init ggml
cmake -S . -B build --preset cpu-tts -DCMAKE_MAKE_PROGRAM=<ninja path> \
  -DCMAKE_C_COMPILER=$(xcrun -f clang) -DCMAKE_CXX_COMPILER=$(xcrun -f clang++)
build/bin/nemo-speech pull magpie
```