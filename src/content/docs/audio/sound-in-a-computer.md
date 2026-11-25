---
id: audio/sound-in-a-computer
title: "Sound inside a computer"
description: "How a computer stores sound as numbers, mixes them and feeds them to a speaker on time, and why Strata chose miniaudio."
kind: concept
size: M
tracks: [E]
needs: [basics/numbers, basics/signals]
time: 60
learn:
  - id: pcm-size
    text: compute the bytes of a clip from its sample rate, channels and sample format
  - id: period-length
    text: compute the length of a mixing period in milliseconds from its frames
  - id: gain-clipping
    text: predict whether summed voices clip and how a change in decibels scales them
  - id: pull-mixer
    text: explain what a mixer does in each period and why the audio thread must never wait
since: 0.3.0
status: final
---

A speaker cone moves smoothly. It glides out, glides back and never jumps. A computer cannot store a glide: it stores numbers, one after the other.

This page follows one small sound from a file to the speaker. The sound is `Samples/PhysicsPlayground/Assets/Sounds/Impacts/Wood.ogg`, the knock of a wooden crate in the Physics Playground sample. The file is 6,233 :term[bytes]{id=byte}. Decoded, it holds 13,805 numbers for the left speaker and 13,805 for the right, and it lasts 0.31 seconds. Every later page of this part meets the same clip again.

## One number per instant describes the wave

Imagine reading the cone's position with a ruler many times a second. Each reading is one number. Play the readings back at the same pace, and the cone follows the original path closely enough that the ear hears the same sound.

A **sample** is one such number: the value of the sound wave at one instant for one speaker. The **sample rate** is how many samples the computer takes each second. Music discs use 44,100 per second; Strata mixes at 48,000. The clip above was recorded at 44,100.

The rate decides which pitches survive. A wave that goes up and down more than half the sample rate times a second cannot be told from a slower one, which is the Nyquist limit of [Sampling, aliasing and filtering](../basics/signals.md). At 48,000 samples per second, the highest pitch that survives is 24,000 Hz, above what people hear.

A sample needs a size. A file often stores each sample as a 16-bit integer, a whole number from -32,768 to 32,767 (see [Numbers](../basics/numbers.md)). A mixer prefers a 32-bit :term[floating-point number]{id=floating-point-number}, because it holds fractions and has room to spare. A float sample runs from -1 to 1: 0 is the cone at rest, 1 is fully out, and -1 is fully in. An integer sample converts by dividing by 32,768.

**PCM** is the plain form of sampled sound: samples stored one after another, with no compression. Its full name is pulse-code modulation (PCM). A compressed file such as `Wood.ogg` is decoded to PCM before it plays; [Clips, voices and sources](../audio/clips-voices-sources.md) covers how.

## Channels, frames and interleaved storage describe more than one speaker

Stereo sound has two **channels**, each one independent stream of samples for one speaker. A sound for one speaker has one channel, and surround layouts have more. The clip of the crate has two.

Counting gets confusing here. One instant of stereo sound is two samples, one per channel, and a **frame** of audio is one sample of every channel at one instant. An audio frame has nothing to do with a rendered frame of a game, which is a picture. Whenever this part says "frame" with no other word beside it, it means the audio kind.

The channels of a frame sit next to each other in memory, then the next frame follows. A layout like this is **interleaved**: `L R L R L R`, where each pair is one frame. The other layout stores all of the left channel and then all of the right. Strata's mixer buffers are interleaved.

The number of numbers in a buffer is therefore the number of frames times the number of channels. A buffer of 480 frames of stereo holds 960 floats. Code that confuses the two sizes reads half a buffer or runs off its end.

## The size of PCM follows from four numbers

The bytes of a clip multiply four things: the seconds, the samples per second, the channels and the bytes of one sample. Each factor is a count of something, and the product is the memory.

:::example[How big is the knock of the crate?]
`Wood.ogg` has 13,805 frames at 44,100 per second, in two channels.

- Seconds: $13{,}805 / 44{,}100 \approx 0.313$.
- As float PCM, each frame costs 2 channels times 4 bytes, which is 8 bytes. The total is $13{,}805 \times 8 = 110{,}440$ bytes.
- As 16-bit PCM, each frame costs 2 times 2 bytes, which is 4 bytes. The total is 55,220 bytes.

The file on disk is 6,233 bytes, so the compression saves about a factor of 18 against float PCM. A longer sound shows why the mixer cannot be careless: one minute of stereo float at 48,000 Hz is $60 \times 48{,}000 \times 2 \times 4 = 23{,}040{,}000$ bytes, about 23 MB.
:::

Now the clip plays through the mixer at 48,000 frames per second, and the clip has 44,100. The mixer must convert the rate: the clip becomes $13{,}805 \times 48{,}000 / 44{,}100 \approx 15{,}025$ frames. Strata keeps each clip at its own rate and channel count and converts for each voice. A clip therefore never depends on how the engine is configured.

## Gain multiplies, and decibels count in ratios

Making a sound louder means making each sample larger. The right operation is a multiplication. **Gain** is the number that every sample of a signal is multiplied by. A gain of 2 doubles the swing of the cone, a gain of 0.5 halves it, and a gain of 0 is silence.

Adding a constant is the wrong operation, and the result is a mistake people make. Adding 0.3 to every sample pushes the whole wave away from rest, so the cone sits off centre and the sound gains a rumble rather than a volume.

Ears do not hear in steps of equal size. A change that doubles the amplitude sounds like a similar step each time it repeats, so loudness follows ratios, and ratios are the business of logarithms from [Numbers](../basics/numbers.md). The **decibel** is a unit built on that: a change of $g$ decibels multiplies the amplitude by $10^{g/20}$.

:::example[What does -6 dB do to a sample?]
For $g = -6$, the factor is $10^{-6/20} = 10^{-0.3} \approx 0.501$. Six decibels down is about half the amplitude.

- $g = 0$ gives a factor of 1: nothing changes.
- $g = -20$ gives 0.1, a tenth.
- $g = +6$ gives about 2, double.

Subtracting 6 dB twice multiplies by 0.501 twice, so -12 dB is about a quarter. Decibels add where gains multiply, which is why mixing consoles use them.
:::

A sample at 0.6 and a gain of -6 dB give $0.6 \times 0.501 \approx 0.30$. Zero in, zero out; the gain never changes silence.

## Summing voices can leave the range, and the result is clipping

A game plays many sounds at once. A crate knocks while a character walks and wind blows. Each playing sound is a **voice**: one running instance of a clip, with its own position in the clip and its own gain.

Mixing is addition. At every instant, the output sample is the sum of the samples of all voices. Two voices at 0.6 can sum to 1.2, and the range of a sample is -1 to 1.

A sample outside that range cannot be played. The device or its driver cuts it at the limit, which flattens the top of the wave. This is **clipping**, and it is heard as a harsh crackle. The fix is a lower gain before the sum, a limiter (code that turns down only the peaks), or fewer loud voices at once.

The sketch of the exercises below makes this concrete. It sums two :term[sine]{id=sine} waves of amplitude 0.6, at 440 Hz and 660 Hz, for one second, and counts the samples outside the range. Then it repeats the sum with both gains lowered by 6 dB.

## A mixer sums voices one mixing period at a time

The **mixer** is the code that sums every voice into one stream for the output. It does not make the whole sum in advance, because voices start and stop at any moment.

Instead the mixer works in small blocks. The **mixing period** is the block of frames the mixer produces in one pass.

Take a period of 480 frames at 48,000 per second: it lasts $480 / 48{,}000 = 0.01$ seconds, 10 ms. In each period the mixer takes the next 480 frames of every voice, converts their rate if needed, multiplies each by its gain, adds them and hands the result on. Then the next period starts where the last one ended.

The clip of the crate is 15,025 frames at the mixer's rate, so about 31 periods of 480 carry it. The last period holds only part of the clip, and the rest of its frames come from other voices or from silence.

## The device pulls, and a late period is an underrun

Consider the naive plan: the game computes sound whenever it likes, perhaps once per rendered frame, and pushes the result at the speaker. The speaker does not wait. A device consumes frames at a fixed pace, and it needs the next block on time, every time.

A game's frames are 16.7 ms apart at 60 frames per second, and a mixing period is about 10 ms. Neither is a multiple of the other, so they drift against each other. The main thread also sometimes takes 40 ms for one frame, and a 40 ms gap in sound is a hole.

| Time (ms) | Device needs a period | Game frame ends |
| --- | --- | --- |
| 0 | Period 1 | Frame 1 |
| 10 | Period 2 | - |
| 16.7 | - | Frame 2 |
| 20 | Period 3 | - |
| 30 | Period 4 | - |
| 33.3 | - | Frame 3 |

The table shows the two clocks side by side. Three periods are due while the game finishes two frames. If sound depended on frames, some periods would find nothing ready.

The answer is to turn the question around. The audio device asks the mixer for each period, at its own pace, on its own thread. A **thread** is code that runs at the same time as other code, and the **audio thread** is the real-time thread that the audio library runs the mixer on, called once per period.

Letting the device ask the mixer is the **pull model**: the device pulls frames when it needs them.

```mermaid caption="The device asks for each period and the audio thread runs the mixer, which sums the voices. The main thread only starts, stops and changes voices." alt="A flow chart. The output device asks the audio thread for a period. The audio thread runs the mixer, which sums two voices and returns the period to the device. The main thread changes the voices."
flowchart LR
    D["Output device"] -->|"needs the next period"| T["Audio thread"]
    T --> M["Mixer: sum of voices"]
    V1["Voice 1"] --> M
    V2["Voice 2"] --> M
    M -->|"one period of frames"| D
    G["Main thread: game frames"] -.->|"start, stop, change"| V1
```

The diagram shows two clocks that never wait for each other. The device and audio thread follow the period; the main thread follows the frame.

When the mixer does not finish in time, the device has nothing new to play and outputs silence or stale data. That is an **underrun**, heard as a click or a gap. Work on the audio thread must stay small and predictable: no waiting for a lock the main thread holds, no memory requests, no file reads, and no work that grows with the game.

A margin against underruns has a cost: **latency**, the delay between asking for a sound and hearing it. A larger period gives the mixer more time and fewer underruns, and makes every sound arrive later. A smaller period gives quicker sounds and less margin. A sound requested during a game frame is heard no sooner than the next period, and often later.

The period's real length depends on the :term[operating system]{id=operating-system} and the audio driver. Strata's tests assume about 11 ms at 48,000 Hz, so a period of about 528 frames, and the page gives no other fixed number. A voice's read position runs ahead of the sound you hear by up to one period, which [Clips, voices and sources](../audio/clips-voices-sources.md) uses.

## Engines feed the device in two ways, with six kinds of library

The pull model has a rival: the push model. In it the game fills buffers and queues them, and the library plays them in order. If the game queues too slowly, the queue empties, and the underrun happens the same way.

A middle path exists as well. A library can offer a callback, a function the game hands over so the library can call it later, and use it either way. The table lists the choices a game engine meets.

| Approach | Model | Includes | Used by |
| --- | --- | --- | --- |
| FMOD | Own mixer on a thread, game sends events | Authoring tool, buses, events, effects | Commercial games and engines, by integration |
| Wwise | Own mixer on a thread, game sends events | Authoring tool, buses, events, effects | Commercial games, by integration |
| OpenAL Soft | Source buffers queued by the game | 3D positioning, mixing in software | Games that want a free 3D sound library |
| XAudio2 | Voices fed with queued buffers | Voices, filters, echo effects, Windows and Xbox only | Games on Microsoft platforms |
| System sound interfaces | Callback of the device (pull) or event-driven | Device access only: no mixing, no decoding | Libraries and engines that write the rest |
| miniaudio | Callback of the device (pull) | Decoders, node graph, rate conversion, 3D positioning, one portable C file | Engines and tools that want a small dependency |

System sound interfaces are the layer below all the others: each operating system offers its own. FMOD and Wwise add the most, since their authoring tools let a sound designer work without touching code. They cost a licence and a tool the whole team must learn.

## Strata chose miniaudio, and stays small

Strata uses miniaudio. The choice rests on one fact: the library comes as one portable C source file. It includes a node graph (a network of processing steps the mix flows through), decoders, a rate converter and 3D positioning. It pulls on its own audio thread, so Strata needs no push queue of its own.

Strata mixes float stereo at 48,000 Hz. The settings type `AudioEngineSpecification` in `Strata/src/Strata/Audio/AudioEngine.h` holds those two numbers as defaults, and clips at other rates are converted for each voice.

:::why[Why one library instead of FMOD or Wwise?]
Strata is a code library that games build against, and a full audio package adds a second program with its own project files. A library kept inside the engine's source tree builds on every platform of the engine with one CMake switch (`STRATA_WITH_AUDIO`) and keeps the dependency tree short. The cost is a smaller feature set, listed next.
:::

The engine around the library, its null device for tests and its thread rules are the subject of [The audio engine](../audio/engine.md).

## What the choice cannot do

Strata has no authoring tool for sound and no buses: a bus is a mixing node that several voices feed, with its own volume and effects. A game that wants one "music" volume has no bus to hang its voices on. The list of what Strata omits is in [What Strata does not do](../appendix/not-in-strata.md), and the engine's own limits are on [The audio engine](../audio/engine.md).

The mixer works at one rate and one channel count for a whole run, 48,000 Hz and stereo by default. The conversion for each voice costs processor time for every clip in another rate.

## Common mistakes

- **Frames counted as samples.** A buffer of 480 frames of stereo is 960 floats, not 480. The symptom is a buffer that is half full or a loop that runs past its end. Fix: multiply frames by channels whenever you count floats.
- **Louder by adding.** Adding a constant shifts the wave and does not make it louder; the symptom is a rumble or a click at the start. Fix: multiply by a gain.
- **Slow work on the audio thread.** Reading a file, taking a lock or allocating memory inside the callback makes a period late. The symptom is a click that appears when the game is busy. Fix: prepare data on the main thread and hand it over without waiting.
- **Expecting a period to line up with a game frame.** The two clocks drift, so a sound started in frame 10 may begin in the middle of a period. Fix: treat sound start times as approximate by up to one period.
- **Forgetting the sum.** Ten voices at 0.5 can reach 5. The symptom is crackle in busy scenes. Fix: lower the gains or the number of loud voices before the sum.

## Summary

- A computer stores sound as PCM: samples taken at a fixed rate, one per channel in each frame, whose bytes are seconds times rate times channels times bytes per sample.
- A mixing period of $n$ frames at rate $r$ lasts $n / r$ seconds; 480 frames at 48,000 per second last 10 ms.
- Gain multiplies samples, $g$ decibels multiplies by $10^{g/20}$, and a sum of voices that leaves -1 to 1 clips.
- The audio thread pulls one period at a time from the mixer, which sums every voice, and it must never wait, or the device runs dry and clicks.

## Check yourself

1. A stereo buffer holds 512 frames of 32-bit floats. How many bytes is that? (a) 512 (b) 1,024 (c) 2,048 (d) 4,096.

   :::answer{tests="pcm-size"}
   Choice (d): 512 frames times 2 channels is 1,024 floats, which is 4,096 bytes at 4 bytes each. Choice (a) counts frames, the first common mistake. Choice (b) counts floats and forgets their size. Choice (c) uses 2 bytes for each sample, the size of a 16-bit integer.
   :::

2. How long is a period of 512 frames at 48,000 frames per second?

   :::answer{tests="period-length"}
   $512 / 48{,}000 \approx 0.01067$ seconds, so 10.7 ms. This is close to the 11 ms that Strata's tests assume.
   :::

3. Three voices play at amplitude 0.4 at one instant, all at their peak. Does the sum clip? What gain change in decibels removes the risk?

   :::answer{tests="gain-clipping"}
   The sum is 1.2, outside the range of -1 to 1, so it clips. A factor of $1 / 1.2 \approx 0.83$ or lower is needed. Since -2 dB gives about 0.79, the gain of every voice must drop by at least 2 dB; -6 dB gives 0.6 for margin.
   :::

4. The main thread stalls for 50 ms in one game frame. Which statement is right? (a) The audio thread waits for the game. (b) The audio thread does not wait for the frame, and breaks only if the mixer itself runs late. (c) The mixer sleeps.

   :::answer{tests="pull-mixer"}
   Choice (b). The device pulls on its own thread, so a slow game frame does not delay the mixer unless the two share a lock. Choice (a) describes the push model, and (c) is not how a mixer works.
   :::

## Exercises

1. **Basic.** Compute the bytes of one minute of 16-bit stereo at 44,100 Hz, and compare with one minute of 32-bit float stereo at 48,000 Hz.

   :::answer[Worked solution]{tests="pcm-size"}
   16-bit: $60 \times 44{,}100 = 2{,}646{,}000$ frames, times 2 channels times 2 bytes, which is 10,584,000 bytes. Float: $60 \times 48{,}000 = 2{,}880{,}000$ frames, times 2 times 4 bytes, which is 23,040,000 bytes. The mixer's form is about 2.2 times larger.
   :::

2. **Medium.** Predict then run: the sketch sums two sines of amplitude 0.6 and prints the peak and the count of samples outside -1 to 1, first at full gain and then lowered by 6 dB. Predict both lines, then run it.

   ::::answer[Worked solution]{tests="gain-clipping" solution="sketches/audio-sound-in-a-computer-clipping.cpp"}
   At full gain the sum can reach 1.2, so the peak lies between 1 and 1.2 and many samples lie outside. At -6 dB each voice peaks near 0.3, so the sum stays below 0.6 and the count is 0.

   :::question
   The sketch uses loops, a function and library calls: read [Programming 1](../basics/programming-1.md), [2](../basics/programming-2.md) and [3](../basics/programming-3.md) first.
   :::

   The whole file follows. It runs one pass for each gain and prints a line for each.

   ```cpp sketch="audio-sound-in-a-computer-clipping.cpp"
   #include <cmath>
   #include <cstdio>

   int main()
   {
   	const float sampleRate = 48000.0f;
   	const float twoPi = 6.2831853f;
   	for (int pass = 0; pass < 2; pass++)
   	{
   		const float gain = pass == 0 ? 1.0f : 0.5011872f; // 0 dB, then -6 dB
   		float peak = 0.0f;
   		int outside = 0;
   		for (int i = 0; i < 48000; i++)
   		{
   			const float time = i / sampleRate;
   			const float first = gain * 0.6f * std::sin(twoPi * 440.0f * time);
   			const float second = gain * 0.6f * std::sin(twoPi * 660.0f * time);
   			const float sum = first + second;
   			peak = std::fmax(peak, std::fabs(sum));
   			if (sum > 1.0f || sum < -1.0f)
   				outside++;
   		}
   		std::printf("gain %.4f: peak %.3f, samples outside: %d\n", gain, peak, outside);
   	}
   }
   ```

   ```text output-of="audio-sound-in-a-computer-clipping.cpp"
   gain 1.0000: peak 1.144, samples outside: 6042
   gain 0.5012: peak 0.573, samples outside: 0
   ```

   1. **Line 10:** the factor 0.5011872 is $10^{-6/20}$, so the second pass lowers both gains by 6 dB.
   2. **Lines 13–14:** one pass sums 48,000 samples, one second at 48,000 Hz.
   3. **Lines 16–18:** each voice is a sine of amplitude 0.6, and the sum adds them.
   4. **Lines 19–21:** the peak keeps the largest size, and every sample beyond 1 or -1 is counted.
   ::::

3. **Hard.** Design: explain why a mixer that waits for a lock on the audio thread is heard as a click, and describe what the main thread should do instead to change a voice's gain.

   :::answer[Worked solution]{tests="pull-mixer"}
   The main thread may hold the lock for longer than a period, for example during a slow frame of 40 ms. The mixer then misses its deadline, the device runs out of frames, and the listener hears an underrun. Instead, the main thread writes the new gain into a value the audio thread reads without waiting, such as an atomic number, which one thread can write and another read safely without a lock. The mixer reads it at the start of the next period and never blocks.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Audio/AudioEngine.h` holds `AudioEngineSpecification`, with `SampleRate` 48,000 and `Channels` 2, and `AudioEngine::ReadFrames`, which pulls frames from the mixer for the null device.
- `Strata/src/Strata/Audio/AudioClip.cpp` decodes every clip to 32-bit float at its own rate and channel count.
- `StrataTests/src/Audio/AudioTestUtils.h` holds the test constants for 48,000 Hz and two channels, with a comment about a period of about 11 ms.
- `Strata/vendor/CMakeLists.txt` builds miniaudio when `STRATA_WITH_AUDIO` is on.

## Further reading

- The miniaudio repository on [GitHub](https://github.com/mackron/miniaudio): its documentation describes the device callback and node graph. Intermediate.
- The OpenAL Soft repository on [GitHub](https://github.com/kcat/openal-soft): a free software 3D API with queued buffers. Intermediate.
- The XAudio2 documentation on [Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/xaudio2/xaudio2-introduction): source voices and queued buffers. Intermediate.
- FMOD documentation and Wwise documentation (hosts requested): middleware with authoring tools. Beginner.
