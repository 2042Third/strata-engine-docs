---
id: audio/testing
title: "Testing sound without speakers"
description: "How Strata proves its sound right on machines with no sound card: a pulled null device, signals of known RMS, settled gains and ratios."
kind: internals
size: S
tracks: [E]
needs: [audio/scene-system, core/first-change]
time: 50
learn:
  - id: explain-pull
    text: explain why a Strata sound test pulls the null device and measures levels instead of listening
  - id: compute-rms
    text: compute the RMS of a sine and the channel ratio a panning test expects
  - id: write-settled-test
    text: write an RMS test for an audio feature that settles before it measures
  - id: run-audio-state
    text: run audio.state during Play mode and read its answer
  - id: name-limits
    text: name what the sound tests cannot prove
since: 0.3.0
status: final
---

A sound test must decide whether a game sounds right without a person, a speaker or a sound card. Strata does it by mixing on a device that plays nothing, pulling the mix into memory and measuring how loud each channel is.

## The problem and how engines solve it

A build machine that runs the tests in the cloud has no sound card, and "it sounds right" is not a test anyone can run. An engine can record the output of a real device, compare it with a stored file, or measure the mix itself. Strata measures the mix, because the mix is plain numbers that need no hardware. The device that makes this possible, the null device, is taught in [the audio engine page](../audio/engine.md).

## What RMS is, with numbers

A sound is a list of numbers, one per frame, that swing above and below zero. Their plain average is zero for a :term[sine]{id=sine}, so it tells nothing. The **RMS** (root mean square) of a list squares every number, averages the squares and takes the square root, which gives one positive number for how strong the signal is.

:::example
A sine of amplitude 0.5 swings between -0.5 and 0.5. Its root mean square (RMS) is the amplitude divided by the square root of 2, so $0.5 / 1.4142 = 0.3536$. A copy played at 0.2 of the gain has RMS $0.2 \times 0.3536 = 0.0707$, and one at 0.8 has $0.2828$. The ratio of the loud copy to the quiet one is $0.2828 / 0.0707 = 4$, whatever the amplitude was.
:::

Because the ratio does not change with the clip, a test can change the clip and keep its checks.

## The map

The test owns the clock. It starts the engine without an :term[output device]{id=output-device}, creates a source, asks for frames and measures them. Nothing else pulls the mix, so the result depends only on the code under test. The editor's `audio.state` command is the second way in, and it asks a running game what it plays.

```mermaid caption="A test starts the engine, plays a source, pulls frames and measures them. A tool asks the running game for its voices through a command." alt="Two paths. In the first, a test starts the audio engine on the null device, plays a source, pulls frames and computes the loudness of each channel. In the second, a tool calls a command of the editor, which reads the voices and the listener."
flowchart LR
    T[Test case] --> E[ScopedAudioEngine]
    E --> S[AudioSource Play]
    S --> R[Render: ReadFrames]
    R --> M[ComputeRms per channel]
    A[StrataCLI] --> C[audio.state]
    C --> V[AudioSystem GetVoices and GetStats]
```

## The contract

Four rules make a sound test reliable, and each has a reason.

- **Pull only on the null device.** `ReadFrames` returns 0 and logs an error when a real device is open, because a real device pulls the mix itself.
- **Measure whole periods.** A sine measured over a whole number of periods has an exact RMS; the tests measure 4,800 frames, which is 44 periods of 440 Hz.
- **Settle after every move.** Moving a source or the listener changes the target gains, and the mix follows them smoothly, because a sudden jump of gain would be heard as a click. The helper mixes 2,400 frames (50 ms at 48,000 frames each second) first.
- **Compare ratios.** A ratio of two measured levels hides the clip's loudness, the distance and the master volume.

:::rule
Tests mix on the null device and game code plays sound through `AudioSystem`; both rules of `AGENTS.md` keep tests independent of hardware. See [the audio engine page](../audio/engine.md).
:::

## A toy version

:::question
The toy uses classes, `std::vector` and :term[function calls]{id=function-call}; if they are new, read [programming 3](../basics/programming-3.md) first.
:::

The toy below is a mixer with the same two traits as Strata's: the caller pulls frames, and the gains move toward their targets a little each frame. It plays a 440 Hz sine of amplitude 0.5 whose target gains are 0.2 on the left and 0.8 on the right, as a source on the right would have. The program measures twice: at once, and after 2,400 frames of settling.

```cpp sketch="audio-testing-toy.cpp"
// A toy mixer pulled by the caller, with gain smoothing, and the RMS measurement of a test.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr float c_SampleRate = 48000.0f;
constexpr float c_Pi = 3.14159265f;
constexpr float c_Amplitude = 0.5f;
constexpr uint64_t c_SettleFrames = 2400;

class ToyMixer
{
public:
	// The source's wanted gains; the mix moves toward them a little every frame.
	void SetTarget(float left, float right)
	{
		m_TargetLeft = left;
		m_TargetRight = right;
	}

	// Pulls frameCount stereo frames, interleaved, like AudioEngine::ReadFrames.
	std::vector<float> Render(uint64_t frameCount)
	{
		std::vector<float> output;
		for (uint64_t frame = 0; frame < frameCount; frame++)
		{
			const float sample = c_Amplitude * std::sin(2.0f * c_Pi * 440.0f * static_cast<float>(m_Frame++) / c_SampleRate);
			m_GainLeft += (m_TargetLeft - m_GainLeft) * 0.002f;
			m_GainRight += (m_TargetRight - m_GainRight) * 0.002f;
			output.push_back(sample * m_GainLeft);
			output.push_back(sample * m_GainRight);
		}
		return output;
	}

private:
	uint64_t m_Frame = 0;
	float m_GainLeft = 0.5f;
	float m_GainRight = 0.5f;
	float m_TargetLeft = 0.5f;
	float m_TargetRight = 0.5f;
};

float ComputeRms(const std::vector<float>& samples, size_t channel)
{
	double sum = 0.0;
	size_t count = 0;
	for (size_t index = channel; index < samples.size(); index += 2)
	{
		sum += static_cast<double>(samples[index]) * samples[index];
		count++;
	}
	return count > 0 ? static_cast<float>(std::sqrt(sum / static_cast<double>(count))) : 0.0f;
}

int main()
{
	ToyMixer early;
	early.SetTarget(0.2f, 0.8f);
	const std::vector<float> tooSoon = early.Render(4800);
	std::printf("too soon: left %.4f right %.4f ratio %.3f\n", ComputeRms(tooSoon, 0), ComputeRms(tooSoon, 1), ComputeRms(tooSoon, 1) / ComputeRms(tooSoon, 0));

	ToyMixer settled;
	settled.SetTarget(0.2f, 0.8f);
	settled.Render(c_SettleFrames);
	const std::vector<float> steady = settled.Render(4800);
	std::printf("settled:  left %.4f right %.4f ratio %.3f\n", ComputeRms(steady, 0), ComputeRms(steady, 1), ComputeRms(steady, 1) / ComputeRms(steady, 0));
	std::printf("sine RMS: %.4f\n", c_Amplitude / std::sqrt(2.0f));
	return 0;
}
```

```text output-of="audio-testing-toy.cpp"
too soon: left 0.0845 right 0.2727 ratio 3.227
settled:  left 0.0708 right 0.2828 ratio 3.994
sine RMS: 0.3536
```

1. **Line 28:** a sine of amplitude 0.5.
2. **Lines 29-30:** the gains move a fraction of the way to their targets with every frame.
3. **Lines 61-67:** the first mixer is pulled for 4,800 frames at once; the second mixes 2,400 settling frames first.

Measured at once, the loud channel is only 3.2 times the quiet one and both levels are off, because the gains were still travelling. After settling, the ratio is 3.99 and the levels match the hand calculation.

## The real code

Three helpers carry every sound test. The first starts the engine on the null device for the length of one test case.

```cpp src="StrataTests/src/Audio/AudioTestUtils.h#L31-L52"
struct ScopedAudioEngine
{
	explicit ScopedAudioEngine(uint32_t maxOneShots = 128)
	{
		AudioEngineSpecification specification;
		specification.NullDevice = true;
		specification.SampleRate = c_SampleRate;
		specification.Channels = c_Channels;
		specification.MaxOneShots = maxOneShots;
		Initialized = AudioEngine::Init(specification);
	}

	~ScopedAudioEngine()
	{
		AudioEngine::Shutdown();
	}

	ScopedAudioEngine(const ScopedAudioEngine&) = delete;
	ScopedAudioEngine& operator=(const ScopedAudioEngine&) = delete;

	bool Initialized = false;
};
```

1. **Line 36:** `NullDevice` makes the engine mix without an output device.
2. **Lines 43-46:** the :term[destructor]{id=destructor} shuts the engine down, so the next test case starts clean.

The second group pulls and measures. Read how `MeasureRms` settles first, and how `ComputeRms` skips the other channel.

```cpp src="StrataTests/src/Audio/AudioTestUtils.h#L54-L82"
// Pulls the next frames of the mix. The buffer is pre-filled with a non-zero value so tests notice unwritten frames.
inline std::vector<float> Render(uint64_t frameCount)
{
	std::vector<float> output(static_cast<size_t>(frameCount) * c_Channels, -1.0f);
	CHECK(AudioEngine::ReadFrames(output.data(), frameCount) == frameCount);
	return output;
}

// Root mean square of every sample, or of one channel of the interleaved stereo mix.
inline float ComputeRms(const std::vector<float>& samples, int channel = -1)
{
	double sum = 0.0;
	size_t count = 0;
	for (size_t index = 0; index < samples.size(); index++)
	{
		if (channel >= 0 && index % c_Channels != static_cast<size_t>(channel))
			continue;
		sum += static_cast<double>(samples[index]) * static_cast<double>(samples[index]);
		count++;
	}
	return count > 0 ? static_cast<float>(std::sqrt(sum / static_cast<double>(count))) : 0.0f;
}

// Steady-state level of the mix: lets gain smoothing settle, then measures.
inline float MeasureRms(int channel = -1)
{
	Render(c_SettleFrames);
	return ComputeRms(Render(4800), channel);
}
```

1. **Line 57:** the buffer starts at -1 so a frame the mix never wrote shows.
2. **Lines 69-70:** one channel of the :term[interleaved]{id=interleaved} mix is skipped.
3. **Lines 80-81:** settle first, then measure 4,800 frames.

The test that uses them is "Panning follows the :term[right-handed]{id=handedness} listener frame". A looping sine sits at +X, five units from a listener at the origin. Moving the listener's direction decides which ear is nearer.

```cpp src="StrataTests/src/Audio/AudioTests.cpp#L1095-L1129"
TEST_CASE("Panning follows the right-handed listener frame")
{
	ScopedAudioEngine engine;
	REQUIRE(engine.Initialized);
	AudioSource source;
	REQUIRE(source.SetClip(CreateSineClip(1.0f)));
	source.SetLooping(true);
	source.SetSpatial(true);
	source.SetPosition(glm::vec3(5.0f, 0.0f, 0.0f));
	source.Play();

	// Default listener: at the origin facing -Z with +Y up, so +X is to the right.
	float left = MeasureRms(0);
	float right = MeasureRms(1);
	CHECK(right > left * 1.5f);

	// Facing +Z, +X is to the left.
	AudioEngine::SetListener(glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, 1.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	left = MeasureRms(0);
	right = MeasureRms(1);
	CHECK(left > right * 1.5f);

	// Facing -Z but upside down (rolled 180 degrees), +X is to the left as well.
	AudioEngine::SetListener(glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, -1.0f), glm::vec3(0.0f, -1.0f, 0.0f));
	left = MeasureRms(0);
	right = MeasureRms(1);
	CHECK(left > right * 1.5f);

	// Straight ahead is centered.
	AudioEngine::SetListener(glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, -1.0f), glm::vec3(0.0f, 1.0f, 0.0f));
	source.SetPosition(glm::vec3(0.0f, 0.0f, -5.0f));
	left = MeasureRms(0);
	right = MeasureRms(1);
	CHECK(left == doctest::Approx(right).epsilon(0.01));
}
```

1. **Line 1103:** the source sits at +X.
2. **Line 1112:** the listener turns to face +Z, and the louder channel flips.

The real gains come from the spatial mixer, so the test checks "more than 1.5 times", not an exact ratio, and a source straight ahead must agree within 1 %.

## Asking a running game: audio.state

A test pulls frames; a tool that watches a running game has no frames, so it asks for the facts. `audio.state` is a query command, and it works only in Play mode, because only then does the scene own an audio system. It fails with a message if the game is not running, or if the scene was started with `play.simulate`, which runs physics only.

```cpp src="StrataEditor/src/Editor/Commands/AudioCommands.cpp#L43-L78"
{
	if (!context.IsPlaying())
		return EditorCommandResult::Fail("audio.state reports a running game: start play mode first (play.start)");
	Scene& scene = *context.GetActiveScene();
	const AudioSystem* audio = scene.GetSystem<AudioSystem>();
	if (!audio)
		return EditorCommandResult::Fail("The running scene has no audio (play.simulate runs physics only)");
	nlohmann::json voices = nlohmann::json::array();
	for (const AudioVoiceInfo& voice : audio->GetVoices())
	{
		voices.push_back({
			{ "entity", voice.Entity.IsValid() ? UUIDToJson(voice.Entity) : nlohmann::json(nullptr) },
			{ "clip", DescribeClip(context, voice.Clip) },
			{ "volume", voice.Volume },
			{ "pitch", voice.Pitch },
			{ "playing", voice.Playing },
			{ "paused", voice.Paused },
			{ "waiting", voice.Waiting },
			{ "looping", voice.Looping },
			{ "spatial", voice.Spatial },
			{ "position", { voice.Position.x, voice.Position.y, voice.Position.z } },
			{ "seconds", voice.Seconds } });
	}
	const AudioSystemStats stats = audio->GetStats();
	nlohmann::json listener = nullptr;
	if (const Entity entity = audio->GetListenerEntity())
	{
		const glm::vec3 position(scene.GetWorldTransform(entity)[3]);
		listener = { { "entity", UUIDToJson(entity.GetUUID()) }, { "position", { position.x, position.y, position.z } } };
	}
	return EditorCommandResult::Ok({
		{ "voices", std::move(voices) },
		{ "oneShots", { { "playing", stats.OneShotCount }, { "played", stats.OneShotsPlayed }, { "dropped", stats.OneShotsDropped } } },
		{ "listener", std::move(listener) },
		{ "masterVolume", AudioSystem::GetMasterVolume() } });
}, EditorCommandKind::Query, EditorCommandResults::Session });
```

1. **Lines 44-49:** the command refuses outside Play mode and in a scene without audio.
2. **Lines 66-77:** the counts, the listener and the master volume join the voices.

The handler reads `GetVoices`, `GetStats` and the listener's world position. The answer below comes from the Tetris sample: start the game, press **Space** so a piece drops and plays its lock sound, pause the game so the short sound stays, and ask:

```sh
StrataCLI call play.start
StrataCLI call input.key '{"key": "Space"}'
StrataCLI call play.pause '{"paused": true}'
StrataCLI call audio.state
```

The answer is one :term[JSON object]{id=json-object}.

```text capture="audio-state-answer"
{
  "voices": [
    {
      "clip": {
        "handle": "E77575181E2BE37E",
        "path": "Sounds/Lock.wav"
      },
      "entity": null,
      "looping": false,
      "paused": true,
      "pitch": 1.0,
      "playing": true,
      "position": [
        0.0,
        0.0,
        0.0
      ],
      "seconds": 0.06965986639261246,
      "spatial": false,
      "volume": 1.0,
      "waiting": false
    }
  ],
  "oneShots": {
    "dropped": 0,
    "played": 1,
    "playing": 1
  },
  "listener": {
    "entity": "528432BE84E14409",
    "position": [
      5.5,
      9.5,
      30.0
    ]
  },
  "masterVolume": 1.0
}
```

1. **Lines 2-23:** the `voices` list holds one entry per source or :term[one-shot]{id=one-shot}: its clip, state and place.
2. **Lines 10-12:** the lock sound reads `paused` and `playing` at once: a one-shot counts as playing until the system takes it back, and the paused game holds it.
3. **Line 18:** `seconds` says how far into the clip the voice is.
4. **Lines 24-27:** the `oneShots` counts: how many play now, how many played since Play began and how many were dropped.
5. **Lines 29-37:** the listener and the master volume.

An agent that fires a sound and finds `played` one higher has heard it.

## What the tests cannot prove

The tests prove levels, ratios and counts. They do not prove that a sound is pleasant. Nothing at the pin shows that anyone judged panning or the :term[Doppler effect]{id=doppler-effect} by ear. The release notes of 0.3.0 add that the Asset tab's audio preview got its checks on the null device alone.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Record the real device and compare with a stored file | Some audio tool makers | Tests the whole path to the device | Needs a sound card on every build machine |
| Compare the mix with a stored reference, sample by sample | :term[Codec]{id=codec} and effect libraries | Catches any change | Breaks on every harmless change of the mixer |
| Measure the gains the mixer computes | Unit tests of mixers | Exact numbers, no settling | Skips the real mix and the mixing thread |

## How it is tested

The tests live in `StrataTests/src/Audio/`. `AudioTests.cpp` holds the suites `Audio.Engine`, `Audio.Clip`, `Audio.Source`, `Audio.Spatial` and `Audio.OneShot`. `AudioSystemTests.cpp` holds `Audio.System`, which runs the :term[scene system]{id=scene-system} with entities and a project. `AudioClipAssetTests.cpp` adds to `Audio.Clip`. Run one suite with `StrataTests.exe --test-suite=Audio.Spatial`.

The feature test adds a second kind of proof. Its script `AudioFeatures` runs in a real scene on an entity called Speaker and calls every function of the audio of the software development kit (SDK): play, seek, pause, stop, :term[one-shots]{id=one-shot}, and the master volume. It requests its clip in `OnCreate`, because a one-shot of a clip that is not yet loaded is dropped.

## Changing it safely

When you add an audio feature, add an RMS test next to the others: start `ScopedAudioEngine`, build a looping sine source, change the one thing, call `MeasureRms` for each case and compare ratios. Never read a level before the settle step has run; never compare an absolute level; never wait by frames, because the test controls the clock by pulling. Extend `AudioFeatures` when the SDK gains a call, and add a field to `audio.state` when a tool needs to see new state. Run `StrataTests.exe --test-suite=Audio*` before you commit.

## Summary

- A sound test starts the engine on the null device, pulls frames with `ReadFrames` and measures them, so it needs no sound card.
- The RMS of a sine is its amplitude divided by the square root of 2, 0.3536 for amplitude 0.5, and the tests compare ratios of RMS.
- A test mixes 2,400 frames after any move and then measures 4,800, so the smoothing has settled.
- `audio.state` answers in Play mode with voices, one-shot counts, the listener and the master volume.
- No test proves that panning or Doppler sound right to a person.

## Check yourself

1. Why does `ReadFrames` return 0 when the engine runs on a real output device?

   - A) The mix is empty.
   - B) A real device pulls the mix itself, so the call is refused and logs an error.
   - C) The sound card is too slow.

   :::answer{tests="explain-pull"}
   B. The real device pulls the mix itself, so `ReadFrames` refuses and logs an error; only the null device waits for a caller. A is wrong because the mix is not empty, and C names a cause the code does not use.
   :::

2. A sine of amplitude 0.5 plays on the left at gain 1 and on the right at gain 0.25. What RMS do the channels show, and what is the ratio?

   :::answer{tests="compute-rms"}
   Left 0.3536, right $0.25 \times 0.3536 = 0.0884$, and the ratio left to right is 4.
   :::

3. A test moves the listener and measures 100 frames at once. What goes wrong?

   :::answer{tests="write-settled-test"}
   The gains are still moving toward their targets, so the level is between the old and the new one. The test passes or fails by accident, so it is unreliable. The fix is the settle step.
   :::

4. A tool calls `audio.state` after `play.simulate`. What answer comes back, and why?

   :::answer{tests="run-audio-state"}
   A failure that says the running scene has no audio, because `play.simulate` runs physics only. Use `play.start` instead.
   :::

5. Name one thing the audio tests do not prove.

   :::answer{tests="name-limits"}
   That panning or the Doppler effect sound right to a person; the preview of the Asset tab was also checked only on the null device.
   :::

## Exercises

1. **Basic.** Compute the RMS of a sine of amplitude 0.8 over 4,800 frames by a program, and compare it with the formula.

   :::answer[Worked solution]{tests="compute-rms" solution="sketches/audio-testing-ex1.cpp"}
   The program squares each sample, averages the squares over the frames and takes the root. The result agrees with the amplitude divided by the square root of 2.

   ```cpp sketch="audio-testing-ex1.cpp"
   // RMS of a sine of amplitude 0.8 over a whole number of periods, against amplitude / sqrt(2).
   #include <cmath>
   #include <cstdio>

   int main()
   {
   	constexpr double c_Pi = 3.14159265358979;
   	constexpr double c_SampleRate = 48000.0;
   	constexpr double c_Amplitude = 0.8;
   	constexpr int c_Frames = 4800;

   	double sum = 0.0;
   	for (int frame = 0; frame < c_Frames; frame++)
   	{
   		const double sample = c_Amplitude * std::sin(2.0 * c_Pi * 440.0 * frame / c_SampleRate);
   		sum += sample * sample;
   	}
   	std::printf("measured %.4f, expected %.4f\n", std::sqrt(sum / c_Frames), c_Amplitude / std::sqrt(2.0));
   	return 0;
   }
   ```

   ```text output-of="audio-testing-ex1.cpp"
   measured 0.5657, expected 0.5657
   ```

   1. **Lines 13-17:** the loop squares every sample and sums the squares.
   2. **Line 18:** the root of the mean is compared with the amplitude over the square root of 2.
   :::

2. **Medium.** Trace it yourself: find where the 2,400 settle frames are pulled during the panning test, and what happens if you remove that step.

   :::answer[Worked solution]{tests="write-settled-test,explain-pull"}
   `MeasureRms` in `StrataTests/src/Audio/AudioTestUtils.h` calls `Render(c_SettleFrames)` and then measures `Render(4800)`. Put a breakpoint there during the panning test, and step over the first `Render`. Remove that line and run `Audio.Spatial`: the levels are measured while the gains still move, so the checks that compare close ratios become unreliable.
   :::

3. **Hard.** Write the missing test: a source with the Linear model exactly at its maximum distance, with :term[rolloff]{id=rolloff} 0.5. Say what ratio to its level at the minimum distance the test expects.

   :::answer[Worked solution]{tests="write-settled-test,compute-rms"}
   The Linear gain is $1 - \text{Rolloff} \times (d - \text{Min}) / (\text{Max} - \text{Min})$. At the minimum distance it is 1. At the maximum distance with rolloff 0.5 it is $1 - 0.5 = 0.5$, so the source is not silent; only rolloff 1 gives silence. Copy `measureAtDistance` from the :term[attenuation]{id=attenuation} test, which already sets the minimum distance to 1 and the maximum to 50, and compare `measureAtDistance(AudioAttenuationModel::Linear, 50.0f, 0.5f)` with the same call at distance 1.0f. Expect the ratio 0.5 with the tolerance of `doctest::Approx(0.5f).epsilon(0.05)`.
   :::

## Where it lives in Strata

- `StrataTests/src/Audio/AudioTestUtils.h`: `ScopedAudioEngine`, `Render`, `ComputeRms`, `MeasureRms`, `c_SettleFrames`.
- `StrataTests/src/Audio/AudioTests.cpp`, `AudioSystemTests.cpp`, `AudioClipAssetTests.cpp`: the suites `Audio.*`.
- `StrataTests/FeatureTest/Scripts/AudioFeatures.cpp`: the feature script.
- `StrataEditor/src/Editor/Commands/AudioCommands.cpp`: the command `audio.state`.
- `Strata/src/Strata/Audio/AudioEngine.h`: `ReadFrames` and `AdvanceNullDevice`.

## Further reading

- Engine documentation of the miniaudio library: how a null backend and a pulled device work (intermediate).
- A signal processing textbook chapter on root mean square and decibels (beginner to intermediate).
