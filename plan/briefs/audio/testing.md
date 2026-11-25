# Brief: `audio/testing`

| Field | Value |
| --- | --- |
| Title | Testing sound without speakers |
| Kind | I |
| Size | S |
| Tracks | E |
| Needs | `audio/scene-system`, `core/first-change` |
| From | audio-input ch. 7 (the null device, RMS tests, settle frames, `audio.state` for agents) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/testing` — Testing sound without speakers

**Covers.** The job: how Strata proves its sound right on machines without a sound card and without anyone listening.
The page's example is the test "Panning follows the right-handed listener frame": a looping 440 Hz sine placed at +X,
measured channel by channel. In this order: the problem (CI has no sound card, and "it sounds right" is no test); the
idea, taught from zero: a null device pulled by the test, synthetic signals of known RMS (a sine of amplitude 0.5 has RMS
0.3536), measuring only after the spatializer's gain smoothing has settled (2,400 frames), and ratios rather than
absolute levels; the helpers `ScopedAudioEngine`, `Render`, `ComputeRms` and `MeasureRms`; the panning test, walked
through; what the suites cover (`AudioTests`, `AudioSystemTests`, `AudioClipAssetTests`) and the feature test's
`AudioFeatures` script, which calls every function of the SDK's audio; `audio.state`, the query a tool or an agent uses to
hear a game without a sound card (voices, one-shot counts, the listener, master volume; Play mode only), with its JSON
answer; and what the tests cannot prove: nobody judged panning or the Doppler effect by ear, and the release notes say
the Asset tab's preview was checked only on the null device. At the end the reader can write an RMS test for a new
audio feature that does not flake.

**Leaves out.**

- The null device's code → `audio/engine`
- Test kinds, determinism and flaky tests in general → `engineering/testing`
- The feature test's coverage checks and runners → `engineering/feature-test`
- Running a command from a terminal → `editor/commands`

**Fit.** `over`: about 3,100 words against S (1,500). One concept, one excerpt, the suites, `audio.state` with its
answer, the internals sections and two exercises go past S's top. Proposed: M (3,000) by S2, whose range holds the
estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:98` | feature | home | `audio.state`: voices, one-shot counts, the listener and master volume, Play mode only (`StrataEditor/src/Editor/Commands/AudioCommands.cpp:34-79`) |
| `audio-input:101` | feature | home | `AudioFeatures`, which exercises every SDK audio call and requests its clip in `OnCreate` |
| `audio-input:290` | concept | home | A11: testing sound without ears; why measuring before the smoothing settles flakes |
| `audio-input:406` | code | home | `StrataTests/src/Audio/AudioTests.cpp:1095-1129`: panning measured by RMS per channel; with the helpers, `StrataTests/src/Audio/AudioTestUtils.h:54-82` |
| `audio-input:483` | figure | home | Text capture of an `audio.state` answer from StrataCLI; a plot of the left and right RMS as a listener turns; the `input.state` answer is used by `input/simulated` |
| `audio-input:581` | hands-on | home | Exercise: the missing test, a Linear source exactly at MaxDistance with Rolloff 0.5 |
| `audio-input:624` | term | home | RMS |
| `audio-input:759` | open | home | Nothing at the pin shows that panning or Doppler were judged by listening; the preview was "only checked on the null audio device, not by ear" (`Docs/Releases/0.3.0.md:177`) |
| `audio-input:29` | feature | use | The null device that the tests pull with `ReadFrames` |
| `new:26` | hands-on | home | Trace it yourself (D27): a breakpoint in `MeasureRms` during the panning test shows the 2,400 frames pulled so that the gain smoothing settles before the 4,800 frames measured; the same test with the settle step removed shows the level it would measure too early. Evidence: `StrataTests/src/Audio/AudioTestUtils.h:28`, `:77-82`; `StrataTests/src/Audio/AudioTests.cpp:1095-1129` |
| `audio-input:85` | feature | use | `GetVoices` and `GetStats`, which `audio.state` reports |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The null device, `ReadFrames` and `AdvanceNullDevice` | `audio/engine` | must |
| doctest test cases and running one suite | `core/first-change` | must |
| Panning and attenuation | `audio/spatial` | must |
| The scene system's voices and statistics | `audio/scene-system` | must |
| Sine waves and amplitude | `basics/math-vectors` | helps |
| Test kinds, determinism and flaky tests | `engineering/testing` | helps |
| Running an editor command from a terminal (`StrataCLI call`) | `editor/commands` | helps |
| Play mode | `editor/play-mode` | helps |
| The feature test and its coverage checks | `engineering/feature-test` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `rms` | RMS | - |
