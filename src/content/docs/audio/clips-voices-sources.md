---
id: audio/clips-voices-sources
title: "Clips, voices and sources"
description: "How Strata turns an audio file into shared sound data, plays it through voices, and lets a game control it through sources."
kind: internals
size: L
tracks: [E]
needs: [audio/engine, assets/importing, assets/loading]
time: 65
learn:
  - id: choose-load-mode
    text: choose a load mode for a sound and defend the choice with its memory and decoding costs
  - id: safe-decoding
    text: explain why a clip is decoded in chunks and why a failed decode counts as the end
  - id: voice-lifetime
    text: explain in which order a voice is destroyed while the audio thread reads it, and why
  - id: source-races
    text: draw both races between the main thread and the audio thread as a sequence of steps for each thread
since: 0.3.0
status: final
---

A game plays a sound in three steps, and Strata gives each step its own object.

A clip (`AudioClip`) is the sound's data: never changed after loading, so any number of players can share it. A voice (`AudioVoice`) is one playing instance of a clip inside the mixer. A source (`AudioSource`) is a voice with remembered settings, which is the object a game controls.

This page covers how a file becomes a clip, how a voice reads it, and how a source hides the voice's dangers. It does not cover the mixer ([audio engine](../audio/engine.md)), distance and panning ([spatial audio](../audio/spatial.md)), or the scene components that own sources ([audio scene system](../audio/scene-system.md)).

## The problem and how engines solve it

An audio file is small because it is compressed. A **codec** (also called a decoder) is code that turns a compressed format such as MP3 or `.ogg` back into samples. Strata reads files that end in `.wav`, `.flac`, `.mp3` and `.ogg`. The mixer wants raw samples, as [sound in a computer](../audio/sound-in-a-computer.md) explains. Someone must pay the cost of decoding, and the open question is when.

Raw samples are large. One minute of stereo sound at 48,000 Hz holds 48,000 × 60 = 2,880,000 frames. Each frame has two samples of 4 :term[bytes]{id=byte} each, so the minute needs 2,880,000 × 2 × 4 = 23,040,000 bytes, about 23 MB. A music track of three minutes at 44,100 Hz needs 63,504,000 bytes. The same track as an `.ogg` file is often a few MiB.

A **load mode** is the choice of when a clip is decoded: once at load, or again by each voice during play. Strata has two. `Decompressed` decodes the whole file once into shared samples. `Streamed` keeps only the encoded bytes, and every voice owns a decoder that works while it plays.

| | `Decompressed` | `Streamed` |
| --- | --- | --- |
| Memory of the clip | all decoded samples | the encoded file |
| Work at load | decode everything | read the :term[header]{id=header} |
| Work per playing voice | copy frames | decode frames |
| Start of a voice | cheap | creates a decoder |
| Fits | short effects, many at once | music and background sound |

Think of a footstep that plays eight times in a second. If it is `Streamed`, eight decoders run, and each starts by parsing the file's header. If it is `Decompressed`, eight voices copy from one buffer.

A footstep of 0.4 s with one channel at 44,100 Hz needs 17,640 frames × 4 bytes = 70,560 bytes decoded. That is a small price for cheap starts.

Strata's Physics Playground keeps its impact sounds, such as `Wood.ogg` (a file of 6,233 bytes), as `Decompressed` clips. Several voices can hit the wood at once and read the same frames.

A music file of 63,504,000 decoded bytes is another matter, and one `Decompressed` music track would cost more memory than a hundred effects. Streaming it keeps 4 MiB or so in memory and decodes 44,100 frames each second for each voice playing it. Music has one voice, so the decoding work is small and constant.

Two details of a clip's format matter to the choice. The file has its own :term[sample rate]{id=sample-rate} and channel count, and **resampling** is the conversion from one sample rate to another.

Strata decodes a clip to 32-bit floats at the file's own rate and channels and converts the rate inside each voice, so a clip never depends on how the engine is configured. That costs a little work per voice and buys clips that load before the engine starts. A voice's **pitch** scales how fast it consumes frames. At pitch 2 the sound runs twice as fast and sounds twice as high, so a clip of 44,100 Hz at pitch 2 consumes 88,200 frames each second.

Other engines draw the same line. The table in [Alternatives Strata did not choose](#alternatives-strata-did-not-choose) lists what Strata omits.

## The map

Three things own memory, and they live on different threads. Clips are made on any thread, voices are made and changed on the :term[main thread]{id=main-thread}, and the :term[audio thread]{id=audio-thread} reads voices while it mixes. The diagram shows who holds whom.

```mermaid caption="A source holds a clip and a voice. The voice holds the same clip and a data source. The audio thread reads the data source, and the engine keeps a list of every live source." alt="A box for the source points to a clip and to a voice. The voice points to the same clip and to its data source. The audio thread reads the data source. The engine's source list points back to every source."
flowchart LR
    Reg["AudioEngine: list of sources"] --> Src["AudioSource (main thread)"]
    Src --> Clip["AudioClip (shared, read only)"]
    Src --> Voice["AudioVoice (main thread)"]
    Voice --> Clip
    Voice --> DS["ClipDataSource"]
    Audio["Audio thread"] -- "reads" --> DS
```

A clip holds one of two things, and the picture below shows what each voice adds. In a `Decompressed` clip the frames are shared and each voice adds only a cursor. In a `Streamed` clip the encoded bytes are shared and each voice adds a decoder.

```mermaid caption="Voices of a clip decoded at load share one array of frames and own a cursor each. Streamed voices share the encoded bytes and own a decoder each." alt="Two groups. In the first, three voices with a cursor each point at one array of frames. In the second, three voices with a decoder each point at one block of encoded bytes."
flowchart LR
    subgraph D["Decompressed"]
        V1["voice 1: cursor"] --> F["shared frames"]
        V2["voice 2: cursor"] --> F
        V3["voice 3: cursor"] --> F
    end
    subgraph S["Streamed"]
        W1["voice 1: decoder"] --> E["shared encoded bytes"]
        W2["voice 2: decoder"] --> E
        W3["voice 3: decoder"] --> E
    end
```

## The contract

These rules hold for every caller. Each has a reason, and the later sections show the code behind it.

- A loaded clip is never modified, so any thread may read it and any number of voices may share it. Loading is thread-safe, so [loaders](../assets/loading.md) run it on worker threads.
- A file's declared length is never trusted. A corrupt header could ask for any amount of memory, so the decoder grows its buffer in steps.
- A voice releases its sound before the data it reads, because the audio thread may still be inside that data.
- Every voice is released before the engine, because each voice belongs to the engine's :term[node graph]{id=node-graph}.
- A voice that reached its end is never restarted: the source builds a new one. A voice that has played is also replaced on Stop, and on a Seek while it is not playing.
- A source works before the engine starts and after it stops. It keeps its clip and settings and does nothing audible.

:::rule
Release the sound before what it reads, and release every voice before the engine. The audio thread reads a voice's data without a lock, so freeing the data first lets it read freed memory. The [audio engine](../audio/engine.md) page explains the audio thread.
:::

## A toy voice

A clip's frames never change, so a voice needs only a position in them. That position is the **cursor**: the voice's current frame in its clip.

:::question
Which C++ is new here? A :term[struct]{id=struct} holding a `std::shared_ptr` is explained in [C++ memory](../basics/cpp-memory.md), calls such as `std::copy_n(...)` in [programming 3](../basics/programming-3.md).
:::

The toy below has one clip of ten frames, in one channel, and three voices over it.

Voice `a` starts at frame 0. Voice `b` starts at frame 4. Voice `c` starts at frame 7 and loops. Each period, a voice copies four frames out and moves its cursor. Look at how `c` wraps inside one read, and at how `b` reports its end only when a read comes up short.

```cpp sketch="audio-clips-voices-sources-toy.cpp"
// A toy voice: a cursor over frames that many voices share. The end is reported with the last frames, so a looping
// voice wraps inside one read.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <vector>

namespace
{

	struct Clip
	{
		std::vector<float> Frames; // One channel, to keep the numbers small
	};

	struct Voice
	{
		std::shared_ptr<const Clip> Shared;
		uint64_t Cursor = 0;
		bool Looping = false;
		bool Ended = false;

		// Copies up to frameCount frames into out and returns how many it wrote.
		uint64_t Read(float* out, uint64_t frameCount)
		{
			uint64_t written = 0;
			while (written < frameCount && !Ended)
			{
				const uint64_t available = Shared->Frames.size() - Cursor;
				if (available == 0)
				{
					if (Looping)
						Cursor = 0;
					else
						Ended = true;
					continue;
				}
				const uint64_t count = std::min(frameCount - written, available);
				std::copy_n(Shared->Frames.data() + Cursor, count, out + written);
				Cursor += count;
				written += count;
			}
			return written;
		}
	};

	void Print(const char* name, Voice& voice)
	{
		float period[4] = {};
		const uint64_t written = voice.Read(period, 4);
		std::printf("%s:", name);
		for (uint64_t i = 0; i < written; i++)
			std::printf(" %.0f", period[i]);
		std::printf(" | cursor %llu, ended %s\n", static_cast<unsigned long long>(voice.Cursor), voice.Ended ? "yes" : "no");
	}

}

int main()
{
	auto clip = std::make_shared<Clip>();
	for (int i = 0; i < 10; i++)
		clip->Frames.push_back(static_cast<float>(i));

	Voice a { clip, 0, false, false };
	Voice b { clip, 4, false, false };
	Voice c { clip, 7, true, false };
	std::printf("owners of the clip: %ld\n", clip.use_count());

	for (int period = 1; period <= 2; period++)
	{
		std::printf("period %d\n", period);
		Print("a", a);
		Print("b", b);
		Print("c", c);
	}
	return 0;
}
```

```text output-of="audio-clips-voices-sources-toy.cpp"
owners of the clip: 4
period 1
a: 0 1 2 3 | cursor 4, ended no
b: 4 5 6 7 | cursor 8, ended no
c: 7 8 9 0 | cursor 1, ended no
period 2
a: 4 5 6 7 | cursor 8, ended no
b: 8 9 | cursor 10, ended yes
c: 1 2 3 4 | cursor 5, ended no
```

1. **Line 19:** every voice holds a :term[shared pointer]{id=shared-pointer} to the same clip, and none of them copies a frame in advance.
2. **Line 20:** the cursor is the only position the voice owns.
3. **Lines 28–29:** the loop stops when the request is full or the voice has ended.
4. **Lines 31–38:** at the last frame a looping voice returns to frame 0, and any other voice ends.
5. **Lines 39–42:** the copy takes what the request needs or what is left, whichever is less.

The three voices share one clip, so the program reports four owners of it. Voice `c` read the frames 7, 8 and 9, found nothing left, returned to frame 0 and read one more frame, all in one call. Voice `b` of the second period received only two frames, and the short read marked it ended. Real voices work the same way, with a mixer asking for the frames.

## Decoding a clip

A clip is made by `AudioClip::LoadFromMemory` or `LoadFromFile`. Both return null and log when the data is empty, corrupt or in a format Strata does not read. The loader opens a miniaudio decoder (`ma_decoder`) on the bytes and asks for 32-bit floats at the file's own channel count and rate, with no conversion.

The loader then checks the format the decoder found: at least one channel, no more than miniaudio's maximum, and a rate above zero. A `Decompressed` clip then decodes every frame. The loop below is the page's first real code.

```cpp src="Strata/src/Strata/Audio/AudioClip.cpp#L35-L58"
bool DecodeAllFrames(ma_decoder& decoder, uint32_t channels, std::vector<float>& outSamples, const std::string& debugName)
{
	outSamples.clear();
	while (true)
	{
		const size_t offset = outSamples.size();
		outSamples.resize(offset + static_cast<size_t>(c_DecodeChunkFrames) * channels);

		ma_uint64 framesRead = 0;
		const ma_result result = ma_decoder_read_pcm_frames(&decoder, outSamples.data() + offset, c_DecodeChunkFrames, &framesRead);
		outSamples.resize(offset + static_cast<size_t>(framesRead) * channels);

		if (result == MA_AT_END || (result == MA_SUCCESS && framesRead == 0))
			break;
		if (result != MA_SUCCESS)
		{
			ST_CORE_ERROR("AudioClip: failed to decode '{}' ({})", debugName, ma_result_description(result));
			return false;
		}
	}

	outSamples.shrink_to_fit();
	return true;
}
```

1. **Line 41:** the buffer grows by one chunk of 16,384 frames per pass, never to a size read from the file.
2. **Line 45:** the buffer shrinks to what the decoder really produced, which may be less than a chunk.
3. **Lines 47–48:** the stream ends either with the decoder's end signal or with a read of zero frames.
4. **Lines 49–52:** any other result is a failed decode, which is logged and refused.
5. **Line 56:** the unused room at the end of the buffer is given back.

A chunk of stereo frames is 16,384 × 2 × 4 = 131,072 bytes, 128 KiB. Suppose a hostile file claims 4,294,967,296 frames of stereo. Trusting that would ask for 34,359,738,368 bytes, about 34 GB, before decoding a single frame. Chunking means such a file costs only the bytes it really holds, and its decoding ends, or fails, where its data runs out. [Robustness](../assets/robustness.md) explains the general rule.

A `Streamed` clip needs its length for seeks and for position queries. The loader asks the decoder first, and every decoder Strata vendors answers when it reads from memory. If one does not answer, the loader counts frames by decoding through the stream with a null output. A streamed clip keeps the encoded bytes by moving the vector, so the decoder's pointer stays valid until the loader frees the decoder.

A memory count is part of the contract too. `GetMemoryUsage` adds the object, its name, the samples (four bytes each) and the encoded bytes. The asset layer reports it to the residency system, and `AudioClipAsset::IsDataShared` returns true while a voice holds the clip, so [residency](../assets/residency.md) does not unload a clip that is playing.

## The cooked form and the importer

The asset layer stores a clip in a **cooked** form (see [what an asset is](../assets/what-is-an-asset.md)): three 32-bit numbers, then the original file. The first is the :term[magic number]{id=magic-number} whose four letters are `STAU`. The second is the version, 1. The third is the load mode, 0 for `Decompressed` and 1 for `Streamed`.

```cpp src="Strata/src/Strata/Audio/AudioClipAsset.cpp#L14-L22"
std::vector<uint8_t> AudioClipAsset::Cook(std::span<const uint8_t> encodedData, AudioClipLoadMode mode)
{
	BinaryWriter writer;
	writer.Write(c_AudioMagic);
	writer.Write(c_CookedVersion);
	writer.Write(static_cast<uint32_t>(mode));
	writer.WriteBytes(encodedData.data(), encodedData.size());
	return writer.TakeData();
}
```

The cooked data always holds the encoded file, whatever the mode. The mode only says what happens on load. `AudioClipAsset::Deserialize` rejects a wrong magic number, a wrong version or a mode above 1 with the message "Not a cooked Strata audio clip". It then calls `AudioClip::LoadFromMemory`, so one decode path serves tests, tools and the game. `RegisterAudioModule` registers this function as the loader of the `AudioClip` :term[asset type]{id=asset-type}.

The :term[importer]{id=importer} ([importing](../assets/importing.md) explains the interface) handles `.wav`, `.mp3`, `.flac` and `.ogg`. It has one setting, `LoadMode`, with the values `Decompressed` and `Streamed`. A new file larger than 1 MiB (1,048,576 bytes) starts as `Streamed`, and a smaller one starts as `Decompressed`. The threshold only picks a default: you can change it for any file.

An unknown mode name in the settings makes the importer add a warning to the import result and use `Decompressed`. The import also validates the file by opening it as a `Streamed` clip. That reads the header and, for most formats, no sample, so a bad file fails the import fast and a `Decompressed` file never decodes twice for a check. The importer's version is 1, so a change to its output must raise it.

::figure{id=import-settings}

## The custom data source

A **data source** (miniaudio's term) is an object that a sound plays from: a table of five functions that read frames, seek, report the format, report the cursor and report the length. Strata's is `ClipDataSource`, and every voice owns one. The struct and its two compile-time checks come first.

```cpp src="Strata/src/Strata/Audio/AudioVoice.cpp#L25-L37"
struct ClipDataSource
{
	ma_data_source_base Base; // Must be first: miniaudio accesses every data source as an ma_data_source_base
	const float* Samples = nullptr; // Decompressed clips: the clip's interleaved frames
	ma_decoder* Decoder = nullptr;  // Streamed clips: the voice's decoder
	uint64_t FrameCount = 0;
	uint32_t Channels = 0;
	uint32_t SampleRate = 0;
	std::atomic<uint64_t> Cursor = 0;
};

static_assert(std::is_standard_layout_v<ClipDataSource> && offsetof(ClipDataSource, Base) == 0, "miniaudio requires the data source base at offset 0");
static_assert(std::atomic<uint64_t>::is_always_lock_free, "The audio thread must never block on the playback cursor");
```

1. **Line 27:** miniaudio treats every data source as a base struct, so the base must be the first member.
2. **Line 33:** the cursor is an atomic number, because the audio thread moves it while the main thread asks where the sound is.
3. **Line 36:** the standard-layout check and the offset check make the cast from base to derived legal.
4. **Line 37:** the check that the atomic is lock free guarantees that the audio thread never waits for a lock on the cursor.

The read function is the voice's inner loop. A `Decompressed` voice copies from the clip's shared frames, and a `Streamed` voice asks its private decoder. Both finish by moving the cursor.

```cpp src="Strata/src/Strata/Audio/AudioVoice.cpp#L45-L77"
ma_result ReadClipDataSource(ma_data_source* dataSource, void* framesOut, ma_uint64 frameCount, ma_uint64* framesRead)
{
	ClipDataSource& source = GetClipDataSource(dataSource);
	const uint64_t cursor = source.Cursor.load(std::memory_order_relaxed);

	ma_result result = MA_SUCCESS;
	ma_uint64 framesAdvanced = 0;
	if (source.Decoder)
	{
		// Decoding from memory cannot fail transiently, so treat a decoding error (corrupt data past the
		// header) as the end of the clip: the voice then finishes instead of playing silence forever.
		result = ma_decoder_read_pcm_frames(source.Decoder, framesOut, frameCount, &framesAdvanced);
		if (result != MA_SUCCESS)
			result = MA_AT_END;
	}
	else
	{
		const uint64_t framesAvailable = cursor < source.FrameCount ? source.FrameCount - cursor : 0;
		framesAdvanced = std::min<uint64_t>(frameCount, framesAvailable);
		// A null output buffer asks for a forward seek.
		if (framesOut && framesAdvanced > 0)
			std::memcpy(framesOut, source.Samples + cursor * source.Channels, static_cast<size_t>(framesAdvanced * source.Channels * sizeof(float)));
	}

	// Reporting the end together with the final frames lets a looping voice wrap around within the same read.
	if (result == MA_SUCCESS && framesAdvanced < frameCount)
		result = MA_AT_END;

	source.Cursor.store(cursor + framesAdvanced, std::memory_order_relaxed);
	if (framesRead)
		*framesRead = framesAdvanced;
	return result;
}
```

1. **Line 48:** the cursor is read with relaxed order, because only the audio thread writes it and nothing else is ordered by it.
2. **Lines 56–58:** a failed decode after the header ends the clip, so the voice finishes instead of playing silence forever.
3. **Lines 62–66:** a `Decompressed` read copies straight from the shared frames, with no decoding and no allocation. A null output asks for a forward seek.
4. **Lines 70–71:** a short read reports the end together with its last frames, so a looping voice wraps within the same read.
5. **Line 73:** the new cursor is stored for the main thread to read.

The toy did the same with one difference. The real function never loops by itself: it reports the end with the frames, and miniaudio's looping seeks back to the start, which is why the table of functions leaves the looping :term[callback]{id=callback} empty. [Basics: threads](../basics/threads.md) covers relaxed atomics, and [classes](../basics/cpp-classes.md) covers tables of functions.

## The voice and its destruction order

`AudioVoice::Create` builds the data source, then the decoder when the clip is `Streamed`, then the `ma_sound`, and applies every setting. The sound starts stopped, so the audio thread does not mix it before its settings are in place. The miniaudio objects live in a heap-allocated `Data` struct, because the node graph keeps pointers into them and the voice object itself may move. Volume goes through the output bus volume of the node, which is atomic, and not through `ma_sound_set_volume`, a plain float the audio thread would read while the main thread writes it.

The :term[destructor]{id=destructor} of `Data` is where the order matters.

```cpp src="Strata/src/Strata/Audio/AudioVoice.cpp#L153-L163"
~Data()
{
	// Uninitializing the sound detaches it from the node graph and waits for the audio thread to finish
	// with it; only then may the data source and decoder it reads from be released.
	if (SoundInitialized)
		ma_sound_uninit(&Sound);
	if (DecoderInitialized)
		ma_decoder_uninit(&Decoder);
	if (SourceInitialized)
		ma_data_source_uninit(&Source);
}
```

1. **Lines 157–158:** the sound goes first. Releasing it detaches it from the graph and waits until the audio thread is done with it.
2. **Lines 159–162:** only then are the decoder and the data source released, because the sound read from both.

Reverse the order and the main thread frees a decoder while the audio thread is decoding with it. The failure is a crash that appears one run in a thousand. Destroying the sound first makes the wait part of the destructor, so no caller can forget it.

The source registry protects the same boundary one level up. `AudioEngine` keeps every live `AudioSource` in a doubly :term[linked list]{id=linked-list} of plain pointers. A plain pointer has no destructor, so a source with static storage can leave the list whatever the order of static destruction at exit. `AudioEngine::Shutdown` walks the list and calls `ReleaseVoice` on each source before `ma_engine_uninit`, so no voice lives longer than the node graph it joined.

## Sources and their state machine

A **source** is a voice with remembered settings: volume, pitch, looping, spatial mode, position, velocity, distances, rolloff and attenuation model. It exists even when no voice does. Before `AudioEngine::Init`, or after `Shutdown`, it stores its clip and settings, and `Play` does nothing audible. When a voice is made, it receives all settings.

The functions that set a value check it. A value that is not finite is ignored with a warning. A negative volume or distance is clamped to zero, and a pitch must be above zero. A bad value from a script can therefore never reach miniaudio.

```mermaid caption="States of a source. Stop and Seek on a voice that played replace the voice. A finished voice is replaced on the next Play. A source stays idle while the engine is stopped." alt="Six states: no clip, clip without voice, stopped, playing, paused and ended. Arrows show Play, Pause, Stop and Seek between them, and an arrow from every state with a voice to the clip-without-voice state, for the stop of the engine."
stateDiagram-v2
    [*] --> NoClip
    NoClip --> ClipOnly: SetClip, engine not running
    NoClip --> Stopped: SetClip, engine running
    ClipOnly --> Playing: Play, voice created
    Stopped --> Playing: Play
    Playing --> Paused: Pause
    Paused --> Playing: Play
    Playing --> Ended: clip ends
    Ended --> Playing: Play, voice replaced
    Playing --> Stopped: Stop, voice replaced
    Paused --> Stopped: Stop, voice replaced
    Stopped --> ClipOnly: Shutdown
    Playing --> ClipOnly: Shutdown
```

`Play` resumes a paused source, starts a stopped one, or restarts a finished one. `Pause` keeps the position. `Stop` moves to the start. `Seek` clamps to the clip's length and takes effect at once for a playing voice, or on the next `Play`.

The position a source reports is the mixer's cursor. The mixer reads ahead of what you hear, by up to one :term[mixing period]{id=mixing-period}. If a period is 480 frames at 48,000 Hz, it is 10 ms, and `GetPlaybackPosition` may be 10 ms ahead of the speaker. That is fine for a progress bar and wrong for lip sync to the millisecond.

## Two races between the threads

Both races follow from one fact: the audio thread changes a voice at any moment, between two instructions of the main thread.

### A finished voice is replaced

When a voice reads its last frames, the audio thread marks it ended. The voice stays started until the audio thread processes it once more, and that pass stops it. Now look at the voice's start function.

```cpp src="Strata/src/Strata/Audio/AudioVoice.cpp#L241-L260"
bool AudioVoice::Start()
{
	ma_sound& sound = m_Data->Sound;

	// A voice that played to its end stays started until the audio thread processes it once more, and that pass stops
	// it. A restart from here (ma_sound_start rewinds it and marks it started) can be undone by that deferred stop, and
	// would be lost silently, so finished voices are replaced instead (see AudioSource::Play). The audio thread may
	// mark the voice finished at any moment, including right after a caller checked HasEnded: then this returns false.
	if (ma_sound_at_end(&sound))
		return false;

	const ma_result result = ma_sound_start(&sound);
	if (result != MA_SUCCESS)
	{
		ST_CORE_ERROR("AudioVoice: failed to start '{}' ({})", m_Data->Clip->GetDebugName(), ma_result_description(result));
		return false;
	}
	m_Data->Started = true;
	return true;
}
```

1. **Lines 245–249:** a restart of a finished voice would move it to the start and mark it started, and the deferred stop could then undo that without any sign. So the function refuses.
2. **Line 252:** only a voice that has not ended is started.
3. **Line 258:** the voice remembers that it started, which a later seek uses.

The refusal can come at any time, even right after a caller checked `HasEnded` and saw false. So the source tries again once.

```cpp src="Strata/src/Strata/Audio/AudioSource.cpp#L39-L54"
void AudioSource::Play()
{
	if (!EnsureVoice())
		return;

	// A finished voice is replaced rather than restarted (see AudioVoice::Start); the new one starts at the beginning.
	// That creates a voice on this thread for every replay, for a streamed clip including a decoder over its data.
	if (m_Voice->HasEnded() && !ReplaceFinishedVoice())
		return;
	bool started = m_Voice->Start();
	// The audio thread may have finished the voice since HasEnded: replace it and try once more.
	if (!started && m_Voice->HasEnded() && ReplaceFinishedVoice())
		started = m_Voice->Start();
	if (started)
		m_Paused = false;
}
```

1. **Lines 46–47:** a voice that ended is replaced with a new one at the start of the clip. For a streamed clip, this builds a decoder on the main thread for every replay.
2. **Lines 50–51:** if the start still returns false because the audio thread finished the voice in between, the source replaces the voice and tries again once.
3. **Lines 52–53:** only a started voice clears the paused flag.

```mermaid caption="The first race. The audio thread ends the voice after the main thread checked it, so the first start is refused and the source replaces the voice." alt="A diagram with two lanes, the main thread and the audio thread. The main thread checks that the voice has not ended, the audio thread then marks it ended, the first start is refused, and the main thread replaces the voice and starts the new one."
sequenceDiagram
    participant M as Main thread
    participant A as Audio thread
    M->>M: Play: HasEnded is false
    A->>A: reads the last frames, marks the voice ended
    M->>M: Start: the voice is at its end, returns false
    M->>M: HasEnded is true now: replace the voice
    M->>M: Start on the new voice succeeds
    A->>A: deferred stop reaches only the old voice
```

### A voice that played is replaced

`Stop` and a `Seek` on a voice that is not playing both move to a new position through `ResetVoice`.

```cpp src="Strata/src/Strata/Audio/AudioSource.cpp#L269-L288"
void AudioSource::ResetVoice()
{
	// Without a voice, m_StartPosition applies when one is created.
	m_PlayingSeekFrame.reset();
	if (!m_Voice)
		return;

	// A voice that has played holds up to one mixing period of audio it already read from its old position,
	// which it would play first when started again, so it is replaced by a fresh voice. A voice that never
	// played holds no audio yet and can simply be moved.
	if (m_Voice->HasStarted())
	{
		m_Voice.reset();
		EnsureVoice();
		return;
	}

	m_Voice->SeekToFrame(SecondsToFrames(m_StartPosition));
	m_StartPosition = 0.0f;
}
```

1. **Lines 276–279:** a voice that has started holds up to one period of audio it already read from the old position.
2. **Lines 281–283:** the voice is dropped and a fresh one made at the start position, so no old frame plays first.
3. **Lines 286–287:** a voice that never played holds no audio and is moved at once.

A seek on a playing voice does not replace it: the audio thread takes the seek before its next read. If the voice ends first, the source remembers the seek target, so the voice that replaces it starts there.

```mermaid caption="The second race. A stopped voice still holds audio from the old position, so Stop discards the voice instead of moving it." alt="A diagram with two lanes. The audio thread reads one period ahead of the playing voice. The main thread stops the voice and seeks it to the start. A new play would start with the old period of audio, so the source replaces the voice."
sequenceDiagram
    participant M as Main thread
    participant A as Audio thread
    A->>A: reads one period ahead from frame 4,800
    M->>M: Stop, then Seek to frame 0 on the same voice
    Note over M,A: the voice still holds the period read from 4,800
    M->>M: Play on that voice would play 10 ms of old audio first
    M->>M: so Stop replaces the voice and the new one starts clean
```

:::example
A rolling ball plays an impact clip of 0.4 s on one source. At 0.4 s the voice ends.

The ball touches again at 0.401 s. Now `Play` sees `HasEnded` true, replaces the voice and starts at frame 0. If it touches at 0.399 s, `HasEnded` is false and the audio thread ends the voice a moment later. Then `Start` returns false, `HasEnded` is true, and the second try replaces the voice. Either way the player hears the sound from its start, once.
:::

## What Strata does not do

Strata has no virtual voices. Every playing voice is mixed, even one a kilometre away at zero volume. Engines with virtual voices keep a voice's position and clock but skip its mixing until it is audible again, and they rank voices by priority so the quietest ones are dropped first. The Audio folder has no such code.

Strata does not stream from disk or from packs either. A `Streamed` clip decodes encoded bytes that are already in memory, so it saves the samples' memory but not the file's. A music file of 4 MiB stays resident for as long as its clip does.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Stream from disk through a :term[ring buffer]{id=ring-buffer} | Unity's Streaming load type; some audio libraries stream | no encoded file in memory | a read thread, :term[underrun]{id=underrun} handling, a path to the file |
| Convert the rate at load to the engine's rate | Audio libraries that store clips at their output rate | cheaper voices | clips that depend on the engine's rate |
| Virtual voices with priorities | Audio libraries | bounded mixing cost with hundreds of sounds | an inaudible voice must keep time |
| Compressed in memory, decoded per play for every clip | Unity's Compressed In Memory | one code path | decode work for every effect start |

## How it is tested

Two suites in `StrataTests/src/Audio/AudioTests.cpp` cover this page. `Audio.Clip` loads and decodes clips without the engine. `Audio.Source` plays them on the :term[null device]{id=null-device}, so no sound card is needed, and checks the frames that come out. Run every audio suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Audio*`.

Some tests map to rules on this page.

`Clips load concurrently on worker threads` checks sharing. `Empty, truncated and unsupported data is rejected` checks safe decoding. `Playing a source again the moment it finishes restarts it` and `A seek made as a source finishes applies to its next Play` check the first race.

`Restarting after Stop or a Seek plays nothing from the old position` checks the second. `Streamed and decompressed clips play identically` checks that the modes agree, and `Invalid parameters are ignored or clamped` checks validation.

## Changing it safely

Add a new codec by teaching the decoder, never the voice: the voice sees only 32-bit floats. Keep the clip unchanged after loading, and keep every new member of `AudioVoice::Data` after the sound in destruction order. A change to the cooked layout needs a new `c_CookedVersion` and a change to the importer's output needs a new :term[importer version]{id=importer-version}.

Run the `Audio.Clip` and `Audio.Source` suites, and for a change to either race write a test that fails without it. The engine's rules say that tests never wait by frames but by the clock or a condition.

## Summary

- A `Decompressed` clip costs memory and starts cheaply, a `Streamed` clip costs decoding for each voice, and the importer picks `Streamed` for new files over 1 MiB.
- A clip decodes in chunks of 16,384 frames, and a failed decode after the header ends the clip.
- A voice releases its sound, then its decoder, then its data source, and every voice goes before the engine.
- A finished voice is replaced and a voice that played is replaced on Stop and Seek, because the audio thread can change a voice between two main-thread steps.

## Check yourself

1. A footstep of 0.4 s plays about eight times a second. Which load mode fits, and why?

   :::answer{tests="choose-load-mode"}
   `Decompressed`. The decoded clip is about 70 KB (for one channel at 44,100 Hz) and all eight voices read it with a copy. `Streamed` would create and run eight decoders every second to save a small amount of memory.
   :::

2. A header says a stereo file holds 4,294,967,296 frames. What does the loader allocate before decoding?

   :::answer{tests="safe-decoding"}
   One chunk: 16,384 × 2 × 4 = 131,072 bytes. The buffer grows only as frames arrive, so the claim costs nothing and decoding stops where the data ends.
   :::

3. Which is right? (a) A voice frees its decoder first, since it is the larger object. (b) A voice releases its sound first, because releasing it waits for the audio thread. (c) The order does not matter, because the audio thread holds a lock.

   :::answer{tests="voice-lifetime"}
   (b). The sound waits for the audio thread, so afterwards nothing reads the decoder. (a) frees data that the audio thread may be reading. (c) is wrong because the data source's cursor is lock free on purpose.
   :::

4. Why does `Stop` replace a voice that played, when it could move the cursor back to 0?

   :::answer{tests="source-races"}
   The voice holds up to one period of audio read from the old position, so a moved voice would play that audio before the new position. A fresh voice holds nothing.
   :::

## Exercises

1. **Basic.** Write a program that prints, for one and for eight voices, the shared memory and the frames decoded per second of a three-minute stereo track at 44,100 Hz, in both load modes. Use an encoded size of 4 MiB.

   :::answer[Worked solution]{tests="choose-load-mode" solution="sketches/audio-clips-voices-sources-memory.cpp"}
   Decoded size is 180 × 44,100 × 2 × 4 bytes. Streaming costs one decoder's work per voice, so its decoding rate is the voice count times 44,100.

   ```cpp sketch="audio-clips-voices-sources-memory.cpp"
   // What one three-minute stereo music file costs at 44,100 Hz in each load mode, for one and for eight voices.
   #include <cstdint>
   #include <cstdio>
   #include <initializer_list>

   namespace
   {

   	constexpr uint64_t c_Seconds = 180;
   	constexpr uint64_t c_SampleRate = 44100;
   	constexpr uint64_t c_Channels = 2;
   	constexpr uint64_t c_EncodedBytes = 4 * 1024 * 1024; // The size of the encoded file in this exercise

   	uint64_t DecodedBytes()
   	{
   		return c_Seconds * c_SampleRate * c_Channels * sizeof(float);
   	}

   }

   int main()
   {
   	for (uint64_t voices : { 1, 8 })
   	{
   		std::printf("%llu voice(s)\n", static_cast<unsigned long long>(voices));
   		std::printf("  Decompressed: %llu bytes shared, 0 frames decoded per second\n", static_cast<unsigned long long>(DecodedBytes()));
   		std::printf("  Streamed: %llu bytes shared, %llu frames decoded per second\n", static_cast<unsigned long long>(c_EncodedBytes), static_cast<unsigned long long>(voices * c_SampleRate));
   	}
   	return 0;
   }
   ```

   ```text output-of="audio-clips-voices-sources-memory.cpp"
   1 voice(s)
     Decompressed: 63504000 bytes shared, 0 frames decoded per second
     Streamed: 4194304 bytes shared, 44100 frames decoded per second
   8 voice(s)
     Decompressed: 63504000 bytes shared, 0 frames decoded per second
     Streamed: 4194304 bytes shared, 352800 frames decoded per second
   ```

   1. **Line 16:** the decoded size is seconds, times rate, times channels, times 4 bytes per float sample.
   2. **Line 26:** a decoded clip is shared by all voices and decodes nothing while they play.
   3. **Line 27:** a streamed clip shares only the encoded file, and every voice decodes its own frames.

   Memory does not change with the voice count, and decoding work grows with it.
   :::

2. **Medium.** Trace it yourself: find where a source replays a clip that finished, and list the calls on a sequence of steps for each thread.

   :::answer[Worked solution]{tests="source-races"}
   Search for `ReplaceFinishedVoice`. It is called twice in `AudioSource::Play` in `Strata/src/Strata/Audio/AudioSource.cpp`, and the refusing function is `AudioVoice::Start` in `Strata/src/Strata/Audio/AudioVoice.cpp`. The sequence is the one drawn in the first race.
   :::

3. **Hard.** Strata mixes every voice. Sketch how you would skip the mixing of voices that are too far away to hear, and say what must still be kept.

   :::answer[Worked solution]{tests="voice-lifetime"}
   Compute each voice's gain from its distance and model. Below a small threshold, stop reading its data but keep advancing its cursor by the frames that pass, so it resumes in time. Keep the voice object alive: dropping it would lose the position and the settings. Destruction order stays the same.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Audio/AudioClip.cpp`: decoding, load modes and memory use.
- `Strata/src/Strata/Audio/AudioClipAsset.cpp`: the cooked form.
- `Strata/src/Strata/Audio/AudioVoice.cpp`: the data source and the voice.
- `Strata/src/Strata/Audio/AudioSource.cpp`: sources and both races.
- `Strata/src/Strata/Audio/AudioEngine.cpp`: the source list and `Shutdown`.
- `Strata/src/Strata/Asset/AssetImporters.cpp`: the audio importer.
- `StrataTests/src/Audio/AudioTests.cpp`: the `Audio.Clip` and `Audio.Source` suites.

## Further reading

- Unity manual, "Audio Clip" (the load types): intermediate.
- FMOD documentation, "Sound creation modes": intermediate.
- Game Audio Programming, by Guy Somberg (CRC Press): advanced, on voice management.
