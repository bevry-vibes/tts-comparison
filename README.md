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
| ✅ auditioned (runner-up) | Piper `en_GB-alan-medium` | The incumbent, upgraded from 16 kHz `low` to 22.05 kHz `medium` — isolates "how much of the problem is just the low tier?" |
| ✅ auditioned | Breeze TTS 2 (Q8_0) | Leaderboard #1 (Elo 1215); official runtime is CUDA-only, but the community [Breeze-TTS-2.cpp](https://github.com/HoppouAI/Breeze-TTS-2.cpp) ggml runtime runs on macOS via Metal/CPU — EN+ZH, voice design/clone |
| ✅ auditioned | Chatterbox (0.5B) | MIT, runs on CPU/MPS, cloning-based |
| ✅ auditioned | Magpie-Multilingual 357M | Elo 1065, NVIDIA Open Model License, CPU-viable via [NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) — 5 US voices only |
| 🏆 **winner** | Higgs Audio v3 4B | Her favourite by ear; runs great on Apple Silicon via **mlx-audio** (Metal) — the CUDA-only verdict was wrong for this Mac. Now the app's word audio. Non-commercial license (fine for this private app). Needs capitalize+period for single words; ref-audio cloning for accents |
| ❌ eliminated | VibeVoice 1.5B | Embeds an **audible AI disclaimer** in every clip — disqualifying for word audio |
| ❌ eliminated | Voxtral 4B | GPU-only (16 GB+) and CC BY-NC weights |
| ❌ eliminated | Fish S2 Pro, Step Audio EditX | No usable open CPU runtime / 13B-class GPU models |
| ❌ skipped | Qwen3-TTS 1.7B, VoxCPM2 | Apache-2.0 but CUDA-documented and no British voice — revisit if a GPU enters the household |

## Where this stands (2026-09-08) & what's next

**The decision landed:** Higgs v3 default voice renders all 194 app words (shipped to sumba-bisa @ d814129, untrimmed, one model load, spectral-QA'd). The audition player ([`auditions/index.html`](./auditions/index.html)) is organised A–E: **A** English voices matrix · **B** word render A/B (Higgs vs Piper, all 194) · **C** Indonesian (one table) · **D** phoneme library (240 clips — current + extracted sandwich cut + vetted Commons alternates per phoneme) · **E** historical 78rpm records (Lloyd James 1930, Daniel Jones). Settled one-time A/Bs live in [`auditions/diagnostics.html`](./auditions/diagnostics.html).

**Follow-ups needed (in order):**
1. Her per-phoneme ear picks from section D → wire winners into the app with attribution.
2. If Commons material still disappoints (p/s/w/z/ʒ have no other clean isolated takes — real gap), propose fine-tuning a small phoneme-conditioned TTS on our extracted takes.
3. Higgs US/GB accent clones (Samantha/Daniel refs): 2/6 rendered; rerun `~/.cache/sumba-tts/render_higgs_clones.py` alone behind `mem_wait 70` (16GB machine: one model job, nothing beside it).
4. Sumbanese MMS-tts-kdb — needs her Hugging Face token (gated), then it can prototype L1 reference audio.
5. Machine health: the 460GB disk hit 99% full on 2026-09-08 — real cleanup needed before more model/download work.

Full quirks log (Higgs single-word fix, Kokoro tail artifact, venv pitfalls, Wikimedia rate limits, the disk/memory incidents) in [FINDINGS.md](./FINDINGS.md).

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