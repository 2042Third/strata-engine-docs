# Brief: `audio/sound-in-a-computer`

| Field | Value |
| --- | --- |
| Title | Sound inside a computer |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `basics/numbers`, `basics/signals` |
| From | audio-input ch. 1; concepts A1-A2, A12 (samples, frames, channels, formats, gain and decibels, the pull model) |
| Unit | `plan/allocation/audio-input.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `audio/sound-in-a-computer` — Sound inside a computer

**Covers.** The page starts with the problem as a reader meets it: a speaker cone moves smoothly, but a computer stores
numbers. Its example is one clip of the Physics Playground, `Samples/PhysicsPlayground/Assets/Sounds/Impacts/Wood.ogg`,
followed from the file to the speaker; the same clip comes back on the later pages of the part. In this order the page
teaches: sampling and the sample rate (Nyquist's limit in one sentence, with a link to `basics/signals`); sample values
from -1 to 1 (16-bit integers in files, 32-bit floats in a mixer); channels, the audio frame (one sample of every channel,
not a rendered frame) and interleaving (`L R L R`); the size of PCM (one minute of stereo float at 48 kHz is about
23 MB); gain as a multiplier, decibels (-6 dB is about half the amplitude) and clipping when a sum leaves [-1, 1]; a
mixer that sums voices into one stream, one mixing period at a time; the pull model, in which the device's audio thread
asks for the next period, against the push model of queued buffers; buffer size against latency, and an underrun heard
as a click.

Then the approaches: a table of FMOD, Wwise, OpenAL Soft, XAudio2, the platform APIs and miniaudio, with their model
(pull or push), what they include and who uses them. Strata's choice and its reason: miniaudio, one portable C file with
a node graph, decoders and a spatializer, which pulls on its own thread; Strata mixes float stereo at 48 kHz and lets
every clip keep its own rate and channel count. What the choice does not give: no authoring tool and no buses (one
sentence, linking `audio/engine` and `appendix/not-in-strata`). Common mistakes: frames counted as samples, "louder" made
by adding instead of multiplying, slow work on the audio thread, and a period expected to line up with a game frame. At
the end the reader can compute the size of a clip and the length of a period, and say what a mixer does in each period.

**Leaves out.**

- Strata's `AudioEngine`, the null device and the rules of the audio thread → `audio/engine`
- Codecs, decoding and load modes → `audio/clips-voices-sources`
- Panning, attenuation and the Doppler effect → `audio/spatial`
- Logarithms and decibels as mathematics → `basics/numbers`
- Sampling theory and aliasing → `basics/signals`

**Fit.** `fits`: about 3,500 words against M (3,000). The concepts from zero, with the mixer and the pull model (about
1,250 words), take the most, then the exercises of `new:22` (about 550) and the table of approaches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:215` | concept | home | A1: sampling, sample values, channels, frames and interleaving; gain multiplies and loudness is logarithmic; Strata mixes float stereo at 48 kHz (`Strata/src/Strata/Audio/AudioEngine.h:22-23`) and clips keep their own rate (`AudioClip.cpp:92-94`) |
| `audio-input:222` | concept | home | A2: the pull model and its thread, buffer size against latency, underruns; push queues (XAudio2, OpenAL) as the other approach |
| `audio-input:296` | concept | home | A12: the landscape table and why Strata took miniaudio (`Strata/vendor/CMakeLists.txt:133`) |
| `audio-input:426` | figure | home | Diagram: the device pulling periods of about 10 ms against game frames of 16.7 ms, and an underrun; the cursor's lead over the audible sample is named here and taught in `audio/clips-voices-sources` |
| `audio-input:748` | open | home | The period's length depends on the backend: the page gives no fixed number, only that the tests assume about 11 ms at 48 kHz (`StrataTests/src/Audio/AudioTestUtils.h:25-26`) |
| `audio-input:606-611` | term | home | Sample, sample rate, channel, frame (audio), interleaved, PCM |
| `audio-input:615-616` | term | home | Mixer and voice in general; Strata's `AudioVoice` is `audio/clips-voices-sources`' |
| `audio-input:622-623` | term | home | Gain; decibel |
| `audio-input:625` | term | home | Clipping |
| `audio-input:628-631` | term | home | Mixing period, underrun, latency, audio thread |
| `audio-input:247` | concept | link | The node graph and voice limits, named with a link to `audio/engine` |
| `new:22` | hands-on | home | Exercises (D27): the bytes of one minute of 16-bit stereo at 44.1 kHz against 32-bit float stereo at 48 kHz, and the milliseconds of a period of 480 and of 512 frames at 48 kHz (computation); a sketch that sums two sine voices of amplitude 0.6 at 48 kHz, prints the peak and counts the samples outside [-1, 1], then lowers both gains by 6 dB and counts again, each result predicted first (predict, then run; a sketch with its output: done); why a mixer that waits for a lock on the audio thread is heard as a click (design). Evidence: `Strata/src/Strata/Audio/AudioEngine.h:22-23` (48 kHz, 2 channels); `StrataTests/src/Audio/AudioTestUtils.h:25` (a mixing period of about 11 ms at 48 kHz) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Powers, logarithms and decibels | `basics/numbers` | must |
| Floating-point numbers, integers of 16 bits and their ranges | `basics/numbers` | must |
| Sampling, the Nyquist limit and aliasing | `basics/signals` | must |
| A thread: code that runs at the same time as other code | `basics/threads` | helps |
| A function handed to a library to be called later (a callback) | `basics/cpp-generic` | helps |
| A queue | `basics/data-structures` | helps |
| One frame of a game, in milliseconds | `start/what-an-engine-is` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `audio-thread` | Audio thread | - |
| `channel-audio` | Channel (audio) | - |
| `clipping` | Clipping | - |
| `frame-audio` | Frame (audio) | - |
| `gain` | Gain | - |
| `interleaved` | Interleaved | - |
| `latency` | Latency | - |
| `mixer` | Mixer | - |
| `mixing-period` | Mixing period | - |
| `pcm` | PCM | - |
| `sample-audio` | Sample (audio) | - |
| `underrun` | Underrun | - |
| `voice` | Voice | - |
