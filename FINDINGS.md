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

## Accent × gender coverage (the honest matrix)

| Engine | UK | US | AU | International/neutral | Bahasa Indonesia | Genders |
| --- | --- | --- | --- | --- | --- | --- |
| Breeze TTS 2 | ✅ (designed) | ✅ (designed) | ✅ (designed) | ✅ (designed) | ❌ (EN+ZH only) | any, via design text |
| Kokoro | ✅ bf/bm ×4+ | ✅ af/am ×9+ | ❌ none in v1.0 | ❌ | ❌ | F+M per accent |
| Piper | ✅ alan/alba(+jenny/amy) | ✅ lessac/ryan(+more) | ❌ none in rhasspy voices | ❌ | ❌ | F+M per accent |
| macOS system voices | ✅ Daniel | ✅ Samantha | ✅ Karen | ❌ | ✅ Damayanti (id-ID) | per installed voice |
| Magpie 357M | ❌ | ✅ Sofia/Leo/Jason/John(+Aria) | ❌ | ❌ | ❌ (12 languages, no ID) | F+M |
| Higgs v3 (mlx) | ⚠️ cloning only | ⚠️ cloning only | ⚠️ cloning only | ⚠️ cloning only | ✅ 100+ languages | default voice; more via reference clips |
| Chatterbox | ⚠️ cloning only | ⚠️ cloning only | ❌ | ❌ | ⚠️ Malay (closest relative) | default/cloned |

Key finding for Sumba Bisa: **no open engine ships an Australian English voice** — AU comes only from Breeze's voice design or the OS's Karen. Indonesian is served by Higgs (excellent) and macOS Damayanti; Magpie/Kokoro/Breeze/Chatterbox have none.

## Engine quirks discovered (cost someone hours — read before running)

- **Higgs single words**: the mlx runtime emits silence/noise for short lowercase text. Fix: **capitalize + trailing period** (`"Bird."` → clean speech; `"bird"` → garbage). Multi-word sentences are fine as-is.
- **Kokoro trailing artifact**: short clips get a trailing breath/burst (measured: energy re-rises to −24 dBFS after the word decays). Two fixes auditioned in `auditions/kokoro-fix-ab/`: trailing period (clean, prosody changes) or energy-trim at the silence dip. Pick one before word rendering.
- **uv venvs** ship without pip/setuptools: chatterbox's `perth` watermarker needs `setuptools<81` (84+ removed `pkg_resources`) and kokoro's G2P needs `pip` + the `en_core_web_sm` wheel installed explicitly, else it shells out to `uv` mid-run and dies.
- **curl downloads from HF** intermittently fail with exit 56 on this network — `huggingface_hub.hf_hub_download` retries and resumes reliably.
- **Never host weights or build third-party CMake inside the repo** — a NeMo build wiped `data/` once. Everything lives in `~/.cache/` now.

## Phoneme input (the breakthrough)

The app needs 41 isolated phoneme clips. The first phoneme test fed ASCII spellings ("shhh") — every engine pronounced the letters. Harness research (reading the installed sources, not guessing) found proper phoneme input:

| Engine | Phoneme input | Evidence |
| --- | --- | --- |
| **Kokoro** | ✅ `KPipeline.generate_from_tokens('<IPA>')` — raw UTF-8 IPA direct to the vocoder, ≤510 chars (`kokoro/pipeline.py` in the pypi package) | All 13 test phonemes (ʃ θ s f m ɑː iː eɪ aɪ ɔɪ aʊ əʊ ɜː) generated and verified as structured speech — **including the five diphthongs that had been TTS-only fallbacks and the AU ɜː** |
| **Piper** | ✅ `[[…]]` blocks in text → raw phonemes against the model's id map (piper1-gpl `voice.py`, `_PHONEME_BLOCK_PATTERN`) — this voice's map is IPA-flavoured (espeak-style `T` warns "missing from id map", IPA `ɑː` passes) | ʃ/S/θ/T/ɑː clips generated |
| **Higgs v3** | ❌ no phoneme path — LLM tokenizer sees IPA as plain text and improvises | "ʃ" produced loud structured audio (improvised), rest n/a |
| Breeze / Chatterbox / macOS | ❌ text only | — |

Implication for Sumba Bisa: a **single Apache-2.0 Kokoro voice can render all 41 phonemes from IPA** consistently (with the same breath-trim post-processing), replacing the "real recordings + TTS fallback" split — pending the ear verdict on quality vs the Commons recordings.

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