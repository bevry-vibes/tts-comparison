# tts-comparison

An open-weights text-to-speech showdown, run on an Apple-Silicon MacBook (CPU, no CUDA) to pick the voice for [Sumba Bisa](https://github.com/bevry-vibes/sumba-bisa) — a local-first English-learning app for Indonesian/Sumba speakers whose 194-word dictionary needed natural, consistent, offline word audio.

**Trigger:** the original Piper (`en_GB-alan-low`, 16 kHz) voice sounded machine-like with a metallic resonance. This repo benchmarks every credible open-weights replacement from the [Artificial Analysis open-weights TTS leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice/open-weights) and community lists, on identical sample text, auditioned by human ear.

## Constraints (the rules every engine must obey)

- Free, **no API keys**, offline after download
- Runs on a MacBook — Apple Silicon, **no CUDA GPU**
- Produces one-word clips (plus one sentence) at ≥ 22 kHz, mp3-friendly
- Prefer a **British English** voice (the app teaches International/AU-leaning English)
- Clean licensing strongly preferred; non-commercial weight licenses acceptable for this private personal app

## Findings

Full evidence table in [FINDINGS.md](./FINDINGS.md). Audition clips in [`auditions/`](./auditions/) — open `auditions/index.html` to play them side by side.

| Verdict | Engine | Why |
| --- | --- | --- |
| ✅ auditioned | Kokoro 82M v1.0 | Best CPU-feasible quality on the leaderboard (Elo 1060), 8 British voices, Apache-2.0, 24 kHz |
| ✅ auditioned | Piper `en_GB-alan-medium` | The incumbent, upgraded from 16 kHz `low` to 22.05 kHz `medium` — isolates "how much of the problem is just the low tier?" |
| ✅ auditioned | Breeze TTS 2 (Q8_0) | Leaderboard #1 (Elo 1215); official runtime is CUDA-only, but the community [Breeze-TTS-2.cpp](https://github.com/HoppouAI/Breeze-TTS-2.cpp) ggml runtime runs on macOS via Metal/CPU — EN+ZH, voice design/clone |
| ✅ auditioned | Chatterbox (0.5B) | MIT, runs on CPU/MPS, cloning-based |
| ✅ auditioned | Magpie-Multilingual 357M | Elo 1065, NVIDIA Open Model License, CPU-viable via [NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) — 5 US voices only |
| ❌ eliminated | Higgs TTS 3 4B | ~9.3 GB, documented paths are CUDA/H100-class; MPS/CPU attempt too slow to be practical for re-rendering — weights kept for reference |
| ❌ eliminated | VibeVoice 1.5B | Embeds an **audible AI disclaimer** in every clip — disqualifying for word audio |
| ❌ eliminated | Voxtral 4B | GPU-only (16 GB+) and CC BY-NC weights |
| ❌ eliminated | Fish S2 Pro, Step Audio EditX | No usable open CPU runtime / 13B-class GPU models |
| ❌ skipped | Qwen3-TTS 1.7B, VoxCPM2 | Apache-2.0 but CUDA-documented and no British voice — revisit if a GPU enters the household |

## Repository layout

```
auditions/        committed mp3 samples + index.html player (the evidence)
engines/          per-engine adapters + setup notes (venv paths, model downloads)
FINDINGS.md       the full evidence table with citations
```

Engine toolchains (venvs, model weights) live outside this repo in `~/.cache/sumba-tts/` — see `engines/*/setup.md`. Nothing here phones home at runtime; every engine runs fully locally.

<!-- LICENSE/ -->

## License

Unless stated otherwise all works are:

- Copyright &copy; [Benjamin Lupton](https://balupton.com)

and licensed under:

- [Reciprocal Public License 1.5](http://spdx.org/licenses/RPL-1.5.html)

<!-- /LICENSE -->