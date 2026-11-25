# Notes: audio/engine

## New terms

None proposed. The six terms the brief homes here (bus, node graph, null device, one-shot, output device, voice
stealing) are defined in bold on the page. "Real-time code" is explained in plain words, not bold.

## Requests

- Names for `tools/data/names.txt`: Wwise (a commercial sound system, named as an example of buses) and OpenAL (buffer
  queues, in the alternatives table). `pagecheck` reports both as `word-list`.
- Host: `miniaud.io` (the miniaudio documentation) and `www.rossbencina.com` (Ross Bencina's real-time audio article)
  are cited in Further reading without a link; the miniaudio repository is linked on `github.com`.
- Page links to pages of the outline that may not be written yet: `../audio/sound-in-a-computer.md` is only a needs entry;
  the page links `../editor/play-mode.md`, `../appendix/not-in-strata.md`, `../core/jobs.md`,
  `../core/engine-modules.md`, `../core/layers-registries.md` and `../basics/threads.md`.
- Figures: both pictures are Mermaid diagrams; no figures file.

## Since

`since: 0.3.0`: `Strata/src/Strata/Audio/AudioEngine.cpp` was added in commit `f43be3a2`, which release `v0.3.0` contains
(`git tag --contains f43be3a2`). `AudioModule.cpp` came later (`7d66c367`).

## Not verified

- Other products: that Wwise has buses and that Godot has audio buses, and that OpenAL queues buffers (alternatives
  table); the book "Game Engine Architecture", Ross Bencina's article and Hans Boehm's paper in Further reading are cited
  from general knowledge.
- What a device does with a mixed value above 1: the engine's mix is not clipped (the device is created with `noClip` and
  the engine's read path has no clipping at the pin), but what each backend does with a float above 1 was not read.
- miniaudio's behavior when a device goes away on backends other than WASAPI (the page says only that it differs).
- The length of a mixing period: Strata leaves it to miniaudio's default; the page uses 480 frames as an example.
- The claim that formatting a log message allocates and that writing may wait: stated as a general real-time rule, not
  checked in `Log`.
- The sketches' behavior is real (compiled and run by `pagecheck`); the toy's peak of 1.144 is that output.

## Findings not applied

- `audio-input:492-494` (rule: "never write a value the audio thread reads without atomics"): at the pin `AGENTS.md` has
  no such sentence under "Audio" and `Docs/DeveloperGuide.md` has none either, so the page states it as the engine's own
  discipline (a bullet of the contract and a `:::why`), not as a `:::rule`.
- "Sums above 1 clip" (`audio-input:247`): the engine does not clip at the pin (see Not verified); the page says the sum
  is not limited.
- `audio-input:97` is one sentence with a link to `editor/play-mode`.
- `new:2`, `new:16`, `new:17`, `new:23` are applied (SetPaused is called only by tests; `AudioModule::OnUpdate` is the
  caller of `AdvanceNullDevice`; device loss is miniaudio's, checked in the WASAPI backend; the trace exercise).
- `audio-input:753` (minimized window): the page states what the code does (frames skipped, no module hook, the device
  thread keeps mixing, the null device stands still) without a claim about what a player hears beyond that.
- The example of the brief says the Playground's impact sound goes through the engine's one-shots; at the pin it goes
  through the scene's one-shots (`AudioSystem`, an `AudioSource`), so the page says so and keeps the engine's one-shots
  as the same idea without a scene.

## Clerk

- Admitted to names.txt: Wwise, OpenAL.
- Admitted to external-hosts.txt: miniaud.io (its front page is miniaudio's). Not admitted: www.rossbencina.com, whose front page gave no title to one fetch; left for the planner.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
