---
id: audio/engine
title: "The audio engine"
description: "How Strata mixes sound: the audio engine, its output device and null device, the two threads, the real-time rules and the sequence-locked up vector."
kind: internals
size: L
tracks: [E]
needs: [basics/threads, core/frame-loop, core/engine-modules, audio/sound-in-a-computer]
time: 75
learn:
  - id: trace-sound
    text: trace a sound from a script call through the scene and the engine to the output device
  - id: real-time-rules
    text: explain why the audio thread never blocks, allocates or logs, and name the tools that replace a lock
  - id: up-vector
    text: explain why the listener's up vector crosses to the mixing thread through a sequence lock while the master volume does not
  - id: null-device
    text: compute how many frames the null device mixes for each frame of a game, with the remainder carried over
  - id: one-shot-cap
    text: predict which one-shots survive a flood beyond the cap
since: 0.3.0
status: final
---

The audio engine, `AudioEngine`, owns four things: the mixer that sums every playing sound into one stream, the output device that plays the stream, the one listener and the master volume. It also owns the sounds that need no owner, the engine's own fire-and-forget voices. It knows nothing of scenes, entities or components: the audio system of a scene sits above it and calls it. This page follows one sound from a script's call to the speaker, then follows the program's life, from the module that starts the engine to the one that stops it. It does not teach clips, voices or sources, the listener's frame or the scene's sounds: later pages of this part do.

## The problem and how engines solve it

A speaker needs a new number 48,000 times a second. If the program delivers one number late, the listener hears a click. A game also plays many sounds at once, and the set changes every frame: a crate lands, a footstep starts, a song ends. The sounds must become one stream of numbers, on time, whatever the game does.

Three answers are common.

- Write the mixer and the device code yourself. You control every detail, but you write a driver for each :term[operating system]{id=operating-system}, and a mistake shows only as an occasional click.
- Buy a commercial sound system such as Wwise. It adds tools for sound designers and **buses**: groups of sounds that share one volume and effects, so a game lowers all music with one setting. The cost is a license, a second set of concepts and a build step.
- Use a small library that opens the **output device** (the hardware or system service that turns the stream into sound, as the operating system offers it) and mixes with a graph of nodes. Strata chose this: miniaudio, one C library in a vendored :term[source file]{id=source-file}.

The third answer leaves Strata only a thin layer of work. It decides what the engine must guarantee to its callers, how it behaves when no device exists, and how the :term[main thread]{id=main-thread} talks to a thread it does not own.

## The map: files, owners and two threads

A game never touches the audio engine directly. Take the Physics Playground, where a crate hits the floor. Its `Impact` script computes a loudness from the contact speed and calls `Audio::PlayOneShotAt`. The call crosses the script boundary into the scene's `IAudioPlayback` service, which `AudioSystem` implements.

The system makes an `AudioSource`, which asks `AudioEngine` for an `AudioVoice`. The voice is a node in miniaudio's graph, and the graph's last node sends the sum to the device.

```mermaid caption="The audio stack from a script's call to the device, with the clip beside it and the two services: one of the scene and one of the engine." alt="A flow diagram. A script call goes to the scene's sound service, then to the scene's audio system, a source, a voice, the audio engine and the output device. A clip feeds the voice. A script's master volume goes through the engine's output service to the audio engine. The audio module starts, updates and stops the audio engine."
flowchart TD
	script["Script: Audio::PlayOneShotAt"] --> playback["IAudioPlayback (scene service)"]
	playback --> system["AudioSystem (scene system)"]
	system --> source["AudioSource"]
	source --> voice["AudioVoice"]
	clip["AudioClip"] --> voice
	voice --> engine["AudioEngine: miniaudio node graph"]
	volume["Script: master volume"] --> output["IAudioOutput (engine service)"]
	output --> engine
	module["AudioModule"] -.->|"Init, Update, Shutdown"| engine
	engine --> device["Output device or null device"]
```

Two services exist because the two lifetimes differ. A scene may come and go; the engine's volume lasts longer than every scene. `IAudioPlayback` is registered with the scene by `AudioSystem` while that system exists. `IAudioOutput` is an engine service that `RegisterAudioModule` registers once, for code that may not include the audio module, such as scripts.

:::example[A crate hits the floor]
The crate bounces off the floor and still moves up at 3 m/s; the floor stands still. The script adds the speed along the contact (3 m/s) to half the larger body speed (1.5 m/s), so the impact speed is 4.5 m/s. That is above the script's `MinSpeed` of 1.5 m/s, so a sound plays. The volume is the speed divided by the `FullVolumeSpeed` of 10 m/s, 0.45, and the pitch is 0.9 + 0.2 × 0.45 = 0.99.

The call reaches `AudioSystem::PlayOneShotAt` with a clip handle, the position, 0.45 and 0.99. When the clip has loaded, the system plays it through a source, and the voice joins the graph. Within a few :term[mixing periods]{id=mixing-period} the stream carries its first samples to the device.
:::

The registration function shows what the module adds to the engine. It installs the components, the engine service and, after them, the clip loader and the scene system.

```cpp src="Strata/src/Strata/Audio/AudioRegistration.cpp#L28-L33"
void RegisterAudioModule()
{
	RegisterAudioComponents();

	static AudioOutputService s_AudioOutput;
	EngineServices::Register<IAudioOutput>(s_AudioOutput);
```

The scene system, named "Audio", declares that it runs after "Scripting", "Animation" and "Physics" when those exist, so sources follow the transforms those modules produced. The composition root calls `RegisterAudioModule` only when the build option `STRATA_WITH_AUDIO` is on ([optional modules](../core/layers-registries.md)).

The second picture shows who runs what. The program's main thread runs the :term[frame loop]{id=game-loop} and every call of the engine. miniaudio's thread, which the device starts, runs the mixing. Only a few values cross between them, and each crosses in a way that never makes the mixing thread wait.

```mermaid caption="The two threads and what crosses between them: three values that the mixing thread reads, and one wait that the main thread makes." alt="A flow diagram with two groups. The main thread group holds the listener call, the volume call, the position query and the destruction of a voice. The mixing thread group holds the callback and the graph. The up vector crosses by a sequence lock, the volume and the cursor as atomic values, and a destroyed voice waits for the mixing thread."
flowchart LR
	subgraph mainthread["Main thread"]
		setlistener["SetListener"]
		setvolume["SetMasterVolume"]
		query["Playback position query"]
		destroy["Voice destroyed"]
	end
	subgraph mixingthread["Mixing thread"]
		apply["onProcess: ApplyPendingWorldUp"]
		mixing["Node graph mixing"]
	end
	setlistener -->|"up vector: sequence lock"| apply
	setvolume -->|"master volume: atomic"| mixing
	mixing -->|"cursor: atomic"| query
	destroy -->|"ma_sound_uninit waits"| mixing
```

The wait in the last arrow is the one place where the main thread waits for the mixing thread. The main thread may do that; the mixing thread may not.

## The contract

Callers of `AudioEngine` may assume the rules below and must keep the others. Each has a reason.

- **Call it from the main thread only.** The engine's state is plain data, with no lock, and the mixing thread is miniaudio's. Two main-thread callers never race, because there is one main thread.
- **Settings may come before `Init`.** Master volume, pause and listener are kept in a settings object; `Init` applies them and `Shutdown` resets them. A game that restores a saved volume at startup need not know when the engine starts.
- **`Init` returns false only when the engine cannot exist.** A bad specification or a mixer that cannot be made fails it. A missing device does not: the engine falls back to the null device and logs a warning, because a game without sound is better than no game.
- **Every call before `Init` or after `Shutdown` fails soft.** A one-shot returns false; a read of the :term[sample rate]{id=sample-rate} returns 0. Nothing asserts, because the editor starts and stops the engine while the user watches.
- **Release every voice before the engine.** A voice is a node in the engine's graph. `Shutdown` releases the sources' voices and the one-shots, then the engine.
- **Never write a value the mixing thread reads without an atomic operation or a sequence lock.** Otherwise the two threads race, and the bug shows once a day on one machine.

:::rule[Game code plays sound through the audio system]
The engine's `AGENTS.md`, under "Audio", sends game code to `AudioSystem` (scripts use the SDK's `AudioSource` and `Audio`) and keeps `AudioEngine` for the engine's own code; tests mix on the null device. `AudioSystem` ties sources to entities and to the scene's pause, and it releases them with the scene. Code that plays on the engine directly gets none of that.
:::

## The real-time rules

The mixing thread has a deadline. Suppose a period holds 480 frames and the sample rate is 48,000 Hz: the period lasts 10 ms. In those 10 ms the thread must produce all 480 frames, and the device then asks for the next period. A thread that is 1 ms late may still be on time, because the device keeps a small buffer. A thread that is 10 ms late leaves the buffer empty, and the listener hears an :term[underrun]{id=underrun} as a click or a gap.

Code with such a deadline is real-time code: its worst case matters, not its average. A function that takes 20 microseconds on average and 30 ms once a minute fails. Three rules follow, and they hold for every line the mixing thread runs.

- Never block. A :term[mutex]{id=mutex} that the main thread holds makes the mixing thread wait for the main thread, and the main thread may be busy for a whole frame. A wait with no upper bound has no place before a deadline.
- Never allocate memory. The :term[allocator]{id=allocator} may take a lock inside, or ask the operating system for a page, and neither has a known limit.
- Never log. Formatting a message allocates, and writing it may wait for a file or a queue.

The main thread must still hand values to the mixing thread. Strata uses three tools.

An atomic value (see [threads](../basics/threads.md)) is one word that no thread ever sees half written. The cursor of a voice, which marks how far it has played, and the volume of a node are atomic. A word has no lock, so the mixing thread never waits for it.

A value of several words is the problem. The listener's up vector has three floats, 12 :term[bytes]{id=byte}. Suppose the main thread changes it from (0, 1, 0) to (1, 0, 0) while the mixing thread reads it. The reader may see the new first float and the old second one: (1, 1, 0).

The library :term[normalizes]{id=normalization} that vector to (0.71, 0.71, 0), a listener rolled by 45 degrees for one period. A plain write of three floats is also a :term[data race]{id=data-race}, which the language leaves undefined.

A sequence lock (see [the job system](../core/jobs.md)) solves this without a wait. The writer makes a counter odd, writes the words and makes the counter even. The reader takes a value only when the counter is even and unchanged after the copy. Otherwise it takes nothing and tries again after the next period.

The third tool is order: destroy what the reader uses only after the reader has let go. A voice is read by the mixing thread until its node leaves the graph. Strata destroys it through `ma_sound_uninit`, which detaches the node and waits until the :term[audio thread]{id=audio-thread} has finished with it; only then are the data source and the decoder it read from released.

## Mixing

The engine mixes with a **node graph**: miniaudio's structure of nodes joined by arrows, where each node reads the streams of its inputs, changes them and offers one stream. A sound is a node. The engine has one last node, the endpoint, which every voice feeds and which feeds the device. The endpoint adds up its inputs, then multiplies the sum by its own volume. That volume is the master volume, set by `ma_engine_set_volume`.

The toy below sums two voices the same way. Two sines of amplitude 0.6 may add up to 1.2: their sum is a sample above 1, and a sample above 1 is a distortion when it reaches the speaker. Halving the master volume halves the sum, so the peak of 1.144 becomes 0.572. Strata adds no limiter: the engine's own mix is not clipped, and a loud sum leaves the mixer unchanged. What the backend of the device does with a value above 1 differs by operating system, and a game keeps its voices quiet enough to avoid it.

A graph has more than the sum. A node may hold a volume of its own, and a node may be a group that many voices feed, which is how a sound system builds buses.

Strata uses only the voices' own volumes and the endpoint's. A search of the audio folder for `ma_sound_group`, for echo effects, for head-related spatial sound or for a filter node finds none at the pin. A game that needs buses, echo or head-related spatial sound must add them. See [what Strata does not do](../appendix/not-in-strata.md).

## A toy version

The toy has the core of any mixer: voices, a master volume and a function that the device would call. Each voice is a sine wave with a phase from 0 to 1. `Pull` fills a period: for every frame it adds one sample of each voice, moves each phase on, and multiplies the sum by the master volume. The master volume is an atomic float, as in the real engine, so another thread may change it while `Pull` runs. The `main` function plays the part of the device and pulls 480 frames twice.

```cpp sketch="audio-engine-toy.cpp"
// A toy mixer: voices summed into one stream that a callback pulls, one period at a time.
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <numbers>
#include <vector>

struct ToyVoice
{
	float Frequency = 440.0f; // Hz
	float Volume = 0.5f;
	double Phase = 0.0; // 0 to 1 around one cycle
};

class ToyMixer
{
public:
	explicit ToyMixer(uint32_t sampleRate)
		: m_SampleRate(sampleRate)
	{
	}

	void AddVoice(float frequency, float volume) { m_Voices.push_back({ frequency, volume, 0.0 }); }
	// Another thread may call this while the callback runs: the callback reads the value with one atomic load.
	void SetMasterVolume(float volume) { m_MasterVolume.store(std::max(volume, 0.0f), std::memory_order_relaxed); }

	// What the device calls when it needs the next period: the sum of every voice, times the master volume.
	void Pull(float* output, uint32_t frameCount)
	{
		const float master = m_MasterVolume.load(std::memory_order_relaxed);
		for (uint32_t frame = 0; frame < frameCount; frame++)
		{
			float sum = 0.0f;
			for (ToyVoice& voice : m_Voices)
			{
				sum += voice.Volume * static_cast<float>(std::sin(2.0 * std::numbers::pi * voice.Phase));
				voice.Phase += voice.Frequency / static_cast<double>(m_SampleRate);
				if (voice.Phase >= 1.0)
					voice.Phase -= 1.0;
			}
			output[frame] = sum * master;
		}
	}
private:
	uint32_t m_SampleRate;
	std::atomic<float> m_MasterVolume = 1.0f;
	std::vector<ToyVoice> m_Voices;
};

int main()
{
	ToyMixer mixer(48000);
	mixer.AddVoice(440.0f, 0.6f);
	mixer.AddVoice(660.0f, 0.6f);

	std::vector<float> period(480);
	for (float master : { 1.0f, 0.5f })
	{
		mixer.SetMasterVolume(master);
		mixer.Pull(period.data(), 480);
		float peak = 0.0f;
		for (float sample : period)
			peak = std::max(peak, std::abs(sample));
		std::printf("master %.1f: peak %.3f of a possible 1.000\n", master, peak);
	}
	return 0;
}
```

```text output-of="audio-engine-toy.cpp"
master 1.0: peak 1.144 of a possible 1.000
master 0.5: peak 0.572 of a possible 1.000
```

1. **Line 27:** the master volume is an atomic float, so another thread may set it while `Pull` runs.
2. **Lines 32–44:** `Pull` reads the volume once and then adds one sample of every voice for each frame.
3. **Line 43:** the sum is multiplied by the master volume and not limited, so it may leave the range from -1 to 1.
4. **Lines 55–56:** two voices of volume 0.6, at 440 Hz and 660 Hz.

The first line shows the problem of the last section. Two voices of 0.6 reach a peak of 1.144, above the possible 1.000. The second line shows the master volume at work: 0.572 is exactly half of 1.144. The real engine differs in four ways.

The device's thread runs `Pull`, a voice may start and end at any time, the listener moves, and no sound may start while the device is absent. The next sections show how each difference is handled.

## The real code, in the order of a program's life

### The module

`AudioModule` is an engine module ([engine modules](../core/engine-modules.md)): the program lists it, and the application calls its hooks. It starts the engine, advances the null device by the frame's step, reclaims finished one-shots, and shuts the engine down.

```cpp src="Strata/src/Strata/Audio/AudioModule.cpp#L19-L40"
bool AudioModule::OnInit(EngineContext&)
{
	AudioEngineSpecification audioSpecification;
	audioSpecification.NullDevice = m_Specification.NullDevice;
	// A program without sound still runs.
	if (!AudioEngine::Init(audioSpecification))
		ST_CORE_ERROR("Audio is unavailable; continuing without sound");
	return true;
}

void AudioModule::OnUpdate(EngineFrame& frame)
{
	// Without an output device nothing pulls the mix: advance it by the frame time, so that sounds still progress and end.
	if (AudioEngine::IsNullDevice())
		AudioEngine::AdvanceNullDevice(frame.Step);
	AudioEngine::Update();
}

void AudioModule::OnShutdown()
{
	AudioEngine::Shutdown();
}
```

1. **Lines 24–26:** a failed `Init` logs an error and the module still returns true. A program whose machine cannot mix sound runs without it.
2. **Lines 32–33:** with no device, nothing pulls the mix, so the module advances it by `frame.Step`, the time of the frame.
3. **Line 34:** every frame, the module calls `Update`, which reclaims one-shots that have finished.
4. **Line 39:** `OnShutdown` runs after the job system stopped, so no job touches the engine while it goes.

The editor and the :term[runtime]{id=runtime} list the module with `AudioModule::Factory({ .NullDevice = specification.Headless })`. A program started with `--headless` has no window; the editor's `--no-gpu` implies it. So both choose the null device, and the runtime's line stands inside `#if ST_WITH_AUDIO`.

The build option `STRATA_WITH_AUDIO` is on by default. With it, the build compiles miniaudio, version 0.11.25 in the pinned source, with its Ogg Vorbis decoder in one implementation file.

### Starting the engine: the device and the fallback

`Init` checks its arguments before it makes anything. The sample rate must lie between 8,000 and 384,000 Hz and the channel count between 1 and miniaudio's limit; otherwise `Init` logs an error and returns false.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L172-L176"
if (specification.SampleRate < c_MinSampleRate || specification.SampleRate > c_MaxSampleRate)
{
	ST_CORE_ERROR("AudioEngine: unsupported sample rate {} Hz (supported: {}-{} Hz)", specification.SampleRate, c_MinSampleRate, c_MaxSampleRate);
	return false;
}
```

Next comes the device. The code builds a configuration, tries the device and, on any failure, tries again without one.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L186-L210"
ma_engine_config config = ma_engine_config_init();
config.listenerCount = 1;
config.channels = specification.Channels;
config.sampleRate = specification.SampleRate;

bool nullDevice = specification.NullDevice;
if (!nullDevice)
{
	const ma_result result = InitializeEngine(*data, config, true);
	if (result != MA_SUCCESS)
	{
		ST_CORE_WARN("AudioEngine: no usable audio output device ({}); continuing without audio output", ma_result_description(result));
		nullDevice = true;
	}
}
if (nullDevice)
{
	const ma_result result = InitializeEngine(*data, config, false);
	if (result != MA_SUCCESS)
	{
		ST_CORE_ERROR("AudioEngine: failed to create the mixer ({})", ma_result_description(result));
		return false;
	}
}
data->NullDevice = nullDevice;
```

1. **Lines 192–200:** the first attempt uses the default output device. A failure logs a warning and switches to the null device instead of failing.
2. **Lines 201–209:** the second attempt has no device. Only when it fails does `Init` return false, with the error text of miniaudio.
3. **Line 210:** the engine records which of the two it got. It is a **null device**: a mixer with no output device, which mixes only when the program pulls it, for tests, servers and headless runs.

Both attempts go through one function. It sets the configuration, creates the engine and applies the settings that were kept before `Init`.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L85-L117"
ma_result InitializeEngine(AudioEngineData& data, ma_engine_config config, bool useDevice)
{
	ma_engine& engine = data.Engine;
	config.noDevice = useDevice ? MA_FALSE : MA_TRUE;
	config.onProcess = ApplyPendingWorldUp;
	config.pProcessUserData = &data;
	// Start the device only once the listener and volume are set. This also avoids ma_engine_init's
	// auto-start failure path, which does not uninitialize its internal resource manager.
	config.noAutoStart = MA_TRUE;

	ma_result result = ma_engine_init(&config, &engine);
	if (result != MA_SUCCESS)
		return result;

	result = ma_engine_set_volume(&engine, s_Settings.MasterVolume);
	if (result != MA_SUCCESS)
	{
		ma_engine_uninit(&engine);
		return result;
	}
	ApplyListener(engine);

	if (useDevice && !s_Settings.Paused)
	{
		result = ma_engine_start(&engine);
		if (result != MA_SUCCESS)
		{
			ma_engine_uninit(&engine);
			return result;
		}
	}
	return MA_SUCCESS;
}
```

1. **Lines 88–90:** `noDevice` selects the null device, and `onProcess` registers the function that miniaudio calls after each mixing period. The up vector section uses it.
2. **Lines 91–93:** the device does not start by itself. Strata sets the volume and the listener first, so that the first period already sounds right.
3. **Lines 105–115:** the listener is applied, and a device starts only if the engine is not paused. Every failure after `ma_engine_init` calls `ma_engine_uninit`, so nothing leaks.

What happens when the device goes away during play, for example when the user disconnects a speaker? Strata registers no notification :term[callback]{id=callback} with miniaudio, so the answer is miniaudio's. Its source states the rule for the Windows backend. When the program uses the default device, miniaudio re-routes the stream to the new default device. Otherwise it stops the device and leaves the rest to the application.

Strata opens the default device, so on Windows sound moves to the new default. On other systems the behavior is miniaudio's and may differ.

### Master volume, pause and the settings kept before the engine starts

`SetMasterVolume` ignores a value that is not finite, clamps a negative one to 0 and stores the result in the settings object. If the engine exists, it also calls `ma_engine_set_volume`, which sets the endpoint's volume with one atomic store. That is why the volume needs no sequence lock: it is one float.

`SetPaused` stops a real device outright, so a paused engine costs nothing, and restarts it. The null device has no thread to stop, so while paused `ReadFrames` writes silence and `AdvanceNullDevice` does nothing. At the pin, only tests call `SetPaused`. The comment in the header says the editor pauses audio this way; it does not. The editor pauses audio through the scene's `AudioSystem`, and the editor restores the master volume when Play stops ([play mode](../editor/play-mode.md)).

### The null device

A mixer on the null device mixes only when something pulls it. `ReadFrames` pulls a given number of frames and returns them, for tests that look at the output. The header's comment says that the Application calls `AdvanceNullDevice` every frame. That is wrong: the Application calls no module code, and `AudioModule::OnUpdate` is the caller. The function mixes the time that the game's frame took, so a sound that lasts 0.5 s also ends after 0.5 s in a headless run.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L429-L448"
void AudioEngine::AdvanceNullDevice(float seconds)
{
	ST_PROFILE_FUNCTION();

	if (!s_Data || !s_Data->NullDevice || s_Settings.Paused || !std::isfinite(seconds) || seconds <= 0.0f)
		return;

	s_Data->PendingNullDeviceFrames += std::min(static_cast<double>(seconds), c_MaxNullDeviceAdvance) * static_cast<double>(GetSampleRate());
	uint64_t frames = static_cast<uint64_t>(s_Data->PendingNullDeviceFrames);
	s_Data->PendingNullDeviceFrames -= static_cast<double>(frames);

	s_Data->DiscardedFrames.resize(static_cast<size_t>(c_NullDeviceChunkFrames * GetChannelCount()));
	while (frames > 0)
	{
		const uint64_t chunk = std::min(frames, c_NullDeviceChunkFrames);
		if (ReadFrames(s_Data->DiscardedFrames.data(), chunk) != chunk)
			return; // Mixing failed (logged)
		frames -= chunk;
	}
}
```

1. **Line 433:** nothing happens with a real device, while paused, or for a time that is zero, negative or not finite.
2. **Lines 436–438:** the time becomes a number of frames. The fraction that cannot be mixed yet stays in `PendingNullDeviceFrames` for the next call, and one call advances at most one second.
3. **Lines 441–447:** the frames are mixed in chunks of 1,024 and thrown away. A failed chunk ends the call.

:::example[A headless Physics Playground]
Start the runtime with `--headless`. The module picks the null device, and `MaxFrameRate` is 60. Suppose a frame takes 16.7 ms. The frame brings 0.0167 × 48,000 = 801.6 frames: the call mixes 801 in one chunk and keeps 0.6. The next frame brings 801.6 + 0.6 = 802.2: it mixes 802 and keeps 0.2.

A frame of 30 ms brings 1,440 frames, which the loop cuts into chunks of 1,024 and 416. A hitch of 5 s mixes only one second, 48,000 frames in 47 chunks, and drops the rest of the backlog, as a device that underruns would.

The crate's sound therefore starts, advances and ends as in a game with speakers. Nothing is heard, and `AudioEngine::Update` still reclaims the finished voice.
:::

The minimized window is a related case. Application skips whole frames while the window is minimized, so no module hook runs. With a device, the device's thread keeps mixing the sounds that already play, and they run to their end. Nothing starts a new sound, and nothing reclaims a finished one-shot until the window returns. A null device is advanced only by `OnUpdate`, so it stands still.

### Engine one-shots

A **one-shot** is a sound that plays once and needs no owner: the caller starts it and forgets it. The engine owns the voice and releases it after the sound ends. `PlayOneShot` plays without a position, for interface sounds and short music cues. `PlayOneShotAt` places it in the world. Game code uses the scene's one-shots instead, which `AudioSystem` keeps; the engine's are for code that has no scene.

An engine keeps its one-shots in a list ordered oldest first. A flood of them must not use all the memory, and a new sound must always play, so the list has a cap, `MaxOneShots`, 128 by default and never below 1.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L143-L157"
std::vector<Scope<AudioVoice>>& oneShots = s_Data->OneShots;
if (oneShots.size() >= s_Data->MaxOneShots)
{
	ReclaimFinishedOneShots();
	// Voice stealing: cut off the oldest one-shot so the newest sound always plays.
	if (oneShots.size() >= s_Data->MaxOneShots)
		oneShots.erase(oneShots.begin());
}

Scope<AudioVoice> voice = AudioVoice::Create(&s_Data->Engine, clip, settings);
if (!voice || !voice->Start())
	return false;

oneShots.push_back(std::move(voice));
return true;
```

1. **Lines 144–150:** at the cap, the list first drops the voices that have finished. If it is still full, `erase(begin())` cuts off the oldest.
2. **Lines 152–153:** the new voice is created and started; a failure returns false before the list changes.
3. **Line 156:** the new voice goes to the back, so the list stays ordered oldest first.

The cut is **voice stealing**: taking the voice of a playing sound for a new one, and choosing the oldest. Its cost is audible when a long sound is the oldest, because it stops in the middle. Its gain is that the newest sound, which the player caused a moment ago, always plays. With a cap of 4 and 10 one-shots started at once, the list holds the last four.

### The up vector and the hand-off

`SetListener` rejects non-finite values and zero vectors for forward and up, because miniaudio normalizes them and a zero vector would turn the mix into :term[NaN]{id=nan} values. Then it stores the state and passes it on.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L334-L348"
const bool upChanged = up != s_Settings.ListenerUp;
s_Settings.ListenerPosition = position;
s_Settings.ListenerForward = forward;
s_Settings.ListenerUp = up;
s_Settings.ListenerVelocity = velocity;
if (!s_Data)
	return;

// Position, direction and velocity are atomics in miniaudio; the up vector is not, so the mixing thread applies it.
ma_engine& engine = s_Data->Engine;
ma_engine_listener_set_position(&engine, c_ListenerIndex, position.x, position.y, position.z);
ma_engine_listener_set_direction(&engine, c_ListenerIndex, forward.x, forward.y, forward.z);
ma_engine_listener_set_velocity(&engine, c_ListenerIndex, velocity.x, velocity.y, velocity.z);
if (upChanged)
	s_Data->WorldUp.Publish(up);
```

1. **Line 334:** the code compares the new up vector with the old one, because most listeners never roll and the vector then never has to travel.
2. **Lines 344–348:** position, direction and velocity are atomic inside miniaudio, so the main thread writes them directly. The up vector is not, so it goes through `Publish` of a `SequenceLockedValue`.

The reader is the callback that miniaudio runs on the mixing thread after each period. Once the engine mixes, it is the only place that writes the up vector into the mixer, so the mixer's plain float is never written from two threads.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L64-L71"
void ApplyPendingWorldUp(void* userData, float*, ma_uint64)
{
	AudioEngineData& data = *static_cast<AudioEngineData*>(userData);
	// A vector being written right now is taken after the next period.
	glm::vec3 up;
	if (data.WorldUp.TakeNew(up))
		ma_engine_listener_set_world_up(&data.Engine, c_ListenerIndex, up.x, up.y, up.z);
}
```

`TakeNew` returns false when nothing new was published or when the writer is in the middle of a write. The new vector then waits for the next period, 10 ms later. The mix may therefore use the old up vector for one more period, which no listener can hear. The lock's own code is on [the job system's page](../core/jobs.md). With the null device, the test calls `GetMixedListenerUp` to read what the mixer uses; with a real device the audio thread owns the value, and the function returns nothing.

### Statistics and the stop

`GetStats` counts the active voices, the one-shots held, the voices that hold mixer resources and the live sources. It walks the one-shot list and the list of live sources, which is linked through the sources themselves so that a source with static storage can still remove itself while the program exits. `Shutdown` stops a real device first unless it is paused, so the audio thread is idle, releases every source's voice and every one-shot, and only then releases the engine's own resources.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Push queue: the game fills buffers and queues them | OpenAL's buffer queues | A model that fits streaming a long file | Mixing of many voices; the game must stay ahead of the device |
| A mutex for the hand-off of the up vector | Teaching mixers and simple engines | Shorter code, no sequence lock | A mixing thread that can wait on the main thread, and so an audible click |
| Buses, effects and a mixer with groups | Wwise and Godot's audio buses | Separate volumes for music and effects, echo effects | More code and concepts, and a larger script interface |
| Own mixer and device code | Engines with their own audio team | Full control and no vendored library | Code for each operating system, and its bugs |

## How it is tested

The suites `Audio.Engine`, `Audio.Spatial` and `Audio.OneShot`, in `StrataTests/src/Audio/AudioTests.cpp`, run on the null device with no sound hardware. A test pulls frames with `ReadFrames` and measures the root mean square of the samples, so it checks what the mixer produces.

- `The listener's up vector reaches the mix through the mixing thread`, in `Audio.Spatial`, places a source 5 units to the right and checks that the right channel is louder. It then rolls the listener upside down and checks that `GetMixedListenerUp` still shows the old vector until `Render(64)` has run. After that it shows the new vector and the left channel wins. Last, 101 changes between periods must leave the latest vector, so a hand-off that drops updates fails.
- `The null device advances playback by the time it is given` calls `AdvanceNullDevice(0.00002f)` 5,000 times. Each call brings 0.96 frames, so only the carried fraction explains that the source moves 0.1 s. A call with 5 s moves a source by 1 s, and `NaN`, infinity and negative times move nothing.
- `One-shots beyond the limit replace the oldest`, in `Audio.OneShot`, uses `MaxOneShots` 4, starts 10 and expects 4 active.
- The test of `Master volume scales the mix` checks volumes 0.25 and 0, that a negative volume gives 0, and that a `NaN` volume is ignored, so the volume stays 0.
- The suite `Core.Application` holds a test that the Audio module advances the null device with the :term[frame time]{id=frame-time}.

Run the audio suites alone with `build/windows/bin/Debug/StrataTests.exe --test-suite=Audio.*`. The device test (`The default output device is used when available, the null device otherwise`) adapts to the machine: it checks the device paths only when a device opened.

## Changing it safely

An extension that adds engine-wide state follows the pattern of the master volume: a field in the settings object, applied in `Init`, reset in `Shutdown`, set from the main thread. If the mixing thread reads the value, choose the tool by size: one word is an atomic, a few words are a `SequenceLockedValue`, and a structure is a question to ask before the code.

- Keep every call on the main thread. Do not add a call that miniaudio's callbacks make into `AudioEngine`.
- Never write in the mixing thread what the main thread reads, or the other way around, without an atomic or a sequence lock.
- Keep release order: voices first, the engine last.
- Run `Audio.*` and `Core.Application` suites with the null device, and rely on no sound hardware.

:::why[An atomic or a sequence lock for what the mixing thread reads]
The mixing thread may not wait, so a lock is out. A plain write that the mixer reads at the same moment is a data race, and a torn value such as the rolled listener above plays for a period before anyone can notice. No test finds that twice in a row. The cost is the extra code: the sequence lock, and the rule that one thread writes and one thread reads.
:::

## Summary

- A sound travels from a script call to `IAudioPlayback`, `AudioSystem`, an `AudioSource`, an `AudioVoice`, `AudioEngine` and the output device; `AudioModule` starts, updates and stops the engine.
- The mixing thread has a deadline of one period, so it never blocks, allocates or logs; atomics, sequence locks and the order of destruction replace locks.
- The up vector has three floats, so it crosses through a sequence lock, while the master volume is one atomic float.
- On the null device, `AudioModule::OnUpdate` mixes the frame's time in chunks of 1,024 frames and carries the fraction over.
- Engine one-shots are capped at `MaxOneShots`, and the oldest is cut off when a new one needs room.

## Check yourself

1. A game runs headless with a step of 1/60 s, 0.016667 s, at 48,000 Hz. How many frames does `AdvanceNullDevice` mix for that step, and in how many chunks?

   :::answer{tests="null-device"}
   The step brings 0.016667 × 48,000 = 800.0 frames, so it mixes 800 frames in one chunk, because 800 is below 1,024. No fraction of note carries over.
   :::

2. Why does `SetListener` publish the up vector through a `SequenceLockedValue`, while `SetMasterVolume` calls `ma_engine_set_volume` directly? (a) Volume is not read by the mixing thread. (b) Volume is one float that miniaudio stores atomically; the up vector is three floats stored without atomics. (c) The up vector changes more often.

   :::answer{tests="up-vector"}
   Option (b) is right. One atomic word cannot be seen half written, and three plain words can. Option (a) is wrong: the endpoint's volume is read on every period. Option (c) is wrong too, because `SetListener` publishes only when the up vector changed.
   :::

3. `MaxOneShots` is 3. You start the one-shots A, B and C, then D and E while all of them still play. Which are playing, and which was cut off first?

   :::answer{tests="one-shot-cap"}
   D cuts off A, the oldest, and E cuts off B. C, D and E play. Neither start fails: both return true.
   :::

4. Which of these may the audio thread do? (a) Log a warning. (b) Load an atomic float. (c) Take a mutex that the main thread holds for under 1 ms. (d) Allocate a small vector.

   :::answer{tests="real-time-rules"}
   Only (b). A log call formats, which allocates, and may wait; the mutex can make the thread wait for a busy main thread; an allocation has no bounded time. A deadline of 10 ms leaves no room for such waits.
   :::

5. Name the objects between `Audio::PlayOneShotAt` in a script and the output device, in order.

   :::answer{tests="trace-sound"}
   The script's call reaches `IAudioPlayback`, which `AudioSystem` implements. The system plays the clip through an `AudioSource`, which holds an `AudioVoice`. The voice is a node of miniaudio's graph in `AudioEngine`, and the graph's endpoint feeds the output device, or the null device.
   :::

## Exercises

1. **Basic.** Design music and effects buses for Strata. Say where the groups live, how a voice joins one, and how a script sets a bus volume without breaking old scripts.

   :::answer[Worked solution]{tests="up-vector"}
   The groups are miniaudio group nodes inside `AudioEngine`, which owns the node graph; a voice would connect to its group instead of the endpoint. A bus volume is one float, so an atomic suffices. Scripts cannot include the audio module, so the volume would be an engine service next to `IAudioOutput`. The script interface only grows at the end: new host functions go last in `StrataScriptHostAPI`, and the version of the application binary interface (ABI) stays.
   :::

2. **Medium.** Write a complete program that computes, for each frame time of 0.0167 s, 0.0167 s, 0.030 s and 5 s, the chunks that the null device mixes. Carry the fraction over, cap one call at 1 s and use chunks of 1,024 frames.

   :::answer[Worked solution]{tests="null-device" solution="sketches/audio-engine-advance.cpp"}
   The function adds the capped time in frames to the pending fraction, takes the whole part as frames to mix and keeps the rest. The loop then cuts the frames into chunks.

   ```cpp sketch="audio-engine-advance.cpp"
   // The null device's clock: how many frames to mix for each frame of the game, with the remainder carried over.
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <vector>

   constexpr uint64_t c_ChunkFrames = 1024;
   constexpr double c_MaxAdvance = 1.0;
   constexpr double c_SampleRate = 48000.0;

   // Returns the sizes of the chunks to mix for this call.
   std::vector<uint64_t> Advance(double seconds, double& pending)
   {
   	std::vector<uint64_t> chunks;
   	pending += std::min(seconds, c_MaxAdvance) * c_SampleRate;
   	uint64_t frames = static_cast<uint64_t>(pending);
   	pending -= static_cast<double>(frames);
   	while (frames > 0)
   	{
   		const uint64_t chunk = std::min(frames, c_ChunkFrames);
   		chunks.push_back(chunk);
   		frames -= chunk;
   	}
   	return chunks;
   }

   int main()
   {
   	double pending = 0.0;
   	for (double seconds : { 0.0167, 0.0167, 0.030, 5.0 })
   	{
   		const std::vector<uint64_t> chunks = Advance(seconds, pending);
   		uint64_t total = 0;
   		for (uint64_t chunk : chunks)
   			total += chunk;
   		std::printf("%.4f s: %zu chunks, %llu frames, carry %.2f\n", seconds, chunks.size(), static_cast<unsigned long long>(total), pending);
   	}
   	return 0;
   }
   ```

   ```text output-of="audio-engine-advance.cpp"
   0.0167 s: 1 chunks, 801 frames, carry 0.60
   0.0167 s: 1 chunks, 802 frames, carry 0.20
   0.0300 s: 2 chunks, 1440 frames, carry 0.20
   5.0000 s: 47 chunks, 48000 frames, carry 0.20
   ```

   1. **Line 15:** the capped time becomes frames and joins the carried fraction.
   2. **Lines 16–17:** the whole part is mixed now and the rest stays in `pending`.
   3. **Lines 18–23:** the loop cuts the frames into chunks of at most 1,024.

   The two first frames mix 801 and 802 frames, and the carry returns to 0.20. The 30 ms frame needs two chunks, and 5 s mixes only one second: 47 chunks.
   :::

3. **Medium.** In a scratch branch, replace the sequence lock in `SetListener` with a `std::mutex` that both `SetListener` and `ApplyPendingWorldUp` lock. Run `Audio.Engine`. Say what you expect, and why the code is still wrong.

   :::answer[Worked solution]{tests="real-time-rules"}
   The tests pass: the null device has no deadline, and the thread that mixes is the thread that calls `ReadFrames`. With a real device the callback would lock a mutex that the main thread may hold during a long step. If the main thread is paused there for 10 ms, the period is late and the listener hears a click. The bug sits where no test looks, which is why the code uses a sequence lock.
   :::

4. **Hard.** Trace it yourself: set a breakpoint in `AudioEngine::AdvanceNullDevice` in a run of the runtime with `--headless`. Find its caller and what it mixes.

   :::answer[Worked solution]{tests="trace-sound"}
   The caller is `AudioModule::OnUpdate` in `Strata/src/Strata/Audio/AudioModule.cpp`, with `frame.Step` as the argument. It is not the Application, as the header's comment says. The function mixes chunks of at most 1,024 frames through `ReadFrames` into a scratch buffer and discards them. The program lists the module in `StrataRuntime/src/RuntimeApplication.cpp`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Audio/AudioEngine.h` and `AudioEngine.cpp`: `AudioEngine`, `AudioEngineSpecification`, `AudioListenerState`, `AudioStats`; in the source file `InitializeEngine`, `StartOneShot` and `ApplyPendingWorldUp`.
- `Strata/src/Strata/Audio/AudioModule.h` and `AudioModule.cpp`: `AudioModule`, `AudioModuleSpecification`.
- `Strata/src/Strata/Audio/AudioRegistration.cpp`: `RegisterAudioModule` and the engine service `IAudioOutput`.
- `Strata/src/Strata/Core/SequenceLock.h`: `SequenceLockedValue`.
- `StrataTests/src/Audio/AudioTests.cpp` and `StrataTests/src/Core/ApplicationAudioTests.cpp`: the suites `Audio.Engine`, `Audio.Spatial`, `Audio.OneShot` and `Core.Application`.
- Settings: the :term[CMake]{id=cmake} option `STRATA_WITH_AUDIO`; the program option `--headless` of the runtime and editor.

## Further reading

- Ross Bencina, "Real-time audio programming 101: time waits for nothing": why the audio thread may not lock, allocate or wait; intermediate.
- The miniaudio documentation and its source on GitHub (<https://github.com/mackron/miniaudio>): the engine, node graph and device APIs that Strata calls; intermediate.
- Jason Gregory, "Game Engine Architecture", the chapter on audio: buses, voices and engine layers; intermediate.
- Hans Boehm, "Can seqlocks get along with programming language memory models?": why a sequence lock needs care with atomics; advanced.
