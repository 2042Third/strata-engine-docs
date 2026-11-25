# Brief: `audio/clips-voices-sources`

| Field | Value |
| --- | --- |
| Title | Clips, voices and sources |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `audio/engine`, `assets/importing`, `assets/loading` |
| From | audio-input ch. 3; 1.2, 1.3 (load modes and safe decoding, the STAU cooked format and the importer, the custom miniaudio data source, destruction order with a real-time reader, lock-free parameters, `AudioSource` and its two races) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/clips-voices-sources` — Clips, voices and sources

**Covers.** The job: a clip (`AudioClip`) is immutable sound data shared by any number of voices; a voice
(`AudioVoice`) is one playing instance in miniaudio's node graph; a source (`AudioSource`) is a voice with remembered
settings that a game controls. The page's example is the Physics Playground's `Wood.ogg` as a Decompressed clip played by
several voices at once, beside a long music file as a Streamed clip. In this order: codecs and the choice per asset
(decode at load or decode while playing; what PCM costs); decoding WAV, FLAC, MP3 and Ogg Vorbis with `ma_decoder` to
float at the file's own rate and channel count, so resampling happens per voice; decoding in chunks of 16,384 frames
instead of trusting a header's length; clips loaded on worker threads and shared freely; memory accounting; the cooked
"STAU" form, the loader and the importer (files over 1 MiB start Streamed; the import settings); the memory layout of the
two load modes.

Then voices: the toy version (a voice as a cursor over shared frames); the custom data source (a C-style table of
functions, the standard-layout asserts, zero-copy reads, the cursor mirrored in an atomic, the end reported with the
last frames so loops wrap within one read, a decode error counted as the end); the voice object and the order in which it
is destroyed while a real-time thread reads it; the source registry, which lets `Shutdown` release every voice before
the engine; volume through the atomic bus volume. Then sources: remembered settings that work before `Init` and after
`Shutdown`; Play, Pause, Stop and Seek; a position that runs ahead of what is heard by up to one period; the state
machine; the two races with the audio thread and their fixes (a finished voice is replaced, never restarted; a voice that
played is replaced on Stop and Seek); input validation. Then what Strata does not do (virtual voices and priorities;
streaming from disk or packs), the alternatives, how it is tested and changing it safely. At the end the reader can
choose a load mode for a sound and defend it, and draw both races as a timeline of the two threads.

**Leaves out.**

- The mixer, the audio thread's rules and the sequence lock → `audio/engine`
- Attenuation models and the listener → `audio/spatial`
- The components and the scene's records of sources → `audio/scene-system`
- Import records, importer versions and background imports in general → `assets/importing`
- Untrusted input and bounded sizes in general → `assets/robustness`
- Residency and when a clip may be evicted → `assets/residency`

**Fit.** `fits`: about 5,850 words against L (5,000). Five excerpts, two of them the races (about 1,250 words), the
two concepts from zero (about 800) and four rules take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:36` | feature | home | The source registry: an intrusive list of plain pointers, so sources with static storage unregister in any order; `Shutdown` releases their voices before the engine (`Strata/src/Strata/Audio/AudioEngine.cpp:56-60, 240-246`) |
| `audio-input:45-52` | feature | home | Decoding, the two load modes, safe decoding, thread safety, memory accounting and `IsDataShared`, the "STAU" form, the clip loader, the importer (`.wav .mp3 .flac .ogg`, `LoadMode`, version 1) |
| `assets:159` | feature | home | The audio importer as the assets inventory lists it, one entry with `audio-input:52`, passed by `assets` (critic-assets-11): `.wav .mp3 .flac .ogg` validated by opening the file as streamed, cooked with the encoded file kept (`AudioClipAsset::Cook`), `LoadMode` Decompressed or Streamed with files over 1 MiB starting Streamed (`Strata/src/Strata/Asset/AssetImporters.cpp:82-137`); `assets/importing` keeps a row of its table of importers |
| `audio-input:58-61` | feature | home | The custom data source, end handling, the voice object and its destruction order, volume through the atomic output bus |
| `audio-input:63-67` | feature | home | `AudioSource` and its settings, Play, Pause, Stop and Seek, finished-voice replacement, a fresh voice after a stop, input validation |
| `audio-input:239` | concept | home | A4: codecs, decoding and streaming from memory; resampling per voice; a header's length is not trusted |
| `audio-input:255` | concept | home | A6: sources and their state machine; the position runs ahead by up to one period |
| `audio-input:392` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:20-77`: the data source over a clip, its asserts, zero-copy reads, the atomic cursor and the end for loops; with its table of functions, `:126-134` |
| `audio-input:393` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:138-164`: the sound is released first, because `ma_sound_uninit` waits for the audio thread, then the decoder and the data source |
| `audio-input:394` | code | home | `Strata/src/Strata/Audio/AudioVoice.cpp:241-260`: why a finished voice is not restarted; with `Strata/src/Strata/Audio/AudioSource.cpp:39-54`, the replacement and the one retry |
| `audio-input:395` | code | home | `Strata/src/Strata/Audio/AudioSource.cpp:269-288`: a voice that played holds a period of old audio, so Stop and Seek replace it |
| `audio-input:399` | code | home | `Strata/src/Strata/Audio/AudioClip.cpp:33-58`: decoding an untrusted file chunk by chunk instead of sizing the buffer from its header |
| `audio-input:424` | figure | home | Diagram: interleaved frames shared by N voices with N cursors (Decompressed) against encoded bytes with one decoder per voice (Streamed); memory and CPU of each |
| `audio-input:428` | figure | home | Diagram: the state machine of a source and its voice (no clip, no voice, stopped, playing, paused, ended and replaced, inert after `Shutdown`) |
| `audio-input:473` | figure | home | Screenshot: the import settings of an audio clip, `LoadMode` with its tooltip |
| `audio-input:497-503` | rule | home | Release the sound before what it reads, and every voice before the engine; replace a finished voice; replace a voice that played; never trust a file's declared length |
| `audio-input:585` | hands-on | home | Exercise: distance culling and virtual voices, after the absence they answer |
| `audio-input:589` | hands-on | home | Exercise ("trace it yourself"): `AudioVoice::Start` and `AudioSource::Play`'s retry on a timeline of both threads |
| `audio-input:612-614` | term | home | Codec or decoder; WAV, FLAC, MP3, Ogg Vorbis; resampling |
| `audio-input:617` | term | home | Source (the class, and the component that describes one) |
| `audio-input:635-637` | term | home | Data source (miniaudio), cursor, load mode |
| `audio-input:647` | term | home | Pitch |
| `audio-input:638` | term | use | Cooked asset (home `assets/what-is-an-asset`) |
| `new:4` | not-done | home | Virtual voices and voice priorities: every playing voice is mixed; how engines virtualize inaudible voices. Evidence: `git grep -niE "virtual\|priorit" 822a7a46 -- Strata/src/Strata/Audio` finds nothing |
| `new:5` | not-done | home | Streaming from disk or packs: a Streamed clip decodes encoded bytes held in memory. Evidence: `Strata/src/Strata/Audio/AudioClip.h:45-52`; `Docs/Roadmap.md:1712` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The `AudioEngine`, its mixer, the node graph and the audio thread | `audio/engine` | must |
| Samples, frames, channels, interleaving and mixing periods | `audio/sound-in-a-computer` | must |
| Import records, importer settings and versions | `assets/importing` | must |
| Asset loaders and loading off the main thread | `assets/loading` | must |
| Atomics and relaxed memory order | `basics/threads` | must |
| Destructors, RAII and unique ownership | `basics/cpp-memory` | must |
| Virtual calls and tables of functions | `basics/cpp-classes` | must |
| Standard-layout types and `offsetof` | `basics/bytes` | helps |
| Untrusted input and bounded sizes | `assets/robustness` | helps |
| Residency: an asset that something still holds | `assets/residency` | helps |
| What a cooked form of an asset is | `assets/what-is-an-asset` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `codec` | Codec | decoder |
| `cursor` | Cursor | - |
| `data-source-miniaudio` | Data source (miniaudio) | - |
| `load-mode` | Load mode | - |
| `pitch` | Pitch | - |
| `resampling` | Resampling | - |
| `source` | Source | - |
