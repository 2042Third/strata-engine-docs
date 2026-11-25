---
id: animation/clips
title: "Clips: sampling motion"
description: "How a clip stores the keys of a motion, shares and reduces them, loads safely, binds to a skeleton by name and answers a joint's pose at any time."
kind: internals
size: L
tracks: [E]
needs: [animation/skeletons, assets/loading, basics/math-interpolation]
time: 90
learn:
  - id: sample-channel
    text: compute the value of a step, linear or cubic spline channel at a given time
  - id: bind-by-name
    text: explain why a clip binds to a skeleton by name once and what that cannot retarget
  - id: reduction-sharing
    text: explain what keyframe reduction and shared key times save and what they cost
  - id: safe-loading
    text: write a loader check that bounds every count before it allocates
since: 0.3.0
status: final
---

A walk cycle lasts a second or two, and the game needs the pose of every joint at any instant of it. A clip stores that motion as a few keys for each joint it moves, and it answers one question: what is this joint's local pose at time t? The clip knows its joints by name only, as text, until it is bound to a skeleton. It does not blend poses, decide which clip plays, advance time or move the mesh; other pages teach those. This page follows one clip from the arrays that store it to the pose it gives.

## The problem and how engines solve it

Take a character with 50 joints that walks in a loop of 2 seconds. Each joint has up to three animated parts: a translation of 3 numbers, a rotation of 4 and a scale of 3, so 10 numbers. An artist who poses every joint at every frame of a 30 :term[frames per second]{id=frame-rate} animation makes 60 poses of 500 numbers each. That is 30,000 numbers of 4 :term[bytes]{id=byte} each, or 120,000 bytes, for one walk.

Two costs follow. The first is storage: a game has hundreds of clips, and it reads the numbers of every playing clip each frame. The second is search. The game asks for the pose at 0.4137 seconds, not at frame 12, because the game draws 60 frames per second and the clip has 30 keys per second. The two do not line up, so something must find the keys on each side of that time.

Engines answer in five ways:

- **Uniform keys.** One key every 1/30 second for every channel. The key's index is the time times 30, so nothing is searched, but a joint that never moves still stores 60 keys.
- **Irregular keys.** Each channel stores the time of each key, and only the keys that matter. Finding the pair around a time is a search; a :term[binary search]{id=binary-search} needs about 6 steps for 60 keys, a scan from the start 30 on average.
- **Keyframe reduction.** Remove keys that the line between their neighbours reproduces.
- **Quantization and curve fitting.** Round each value to fewer bits, or replace many keys by a few fitted curve pieces. The result is much smaller and no longer exact.
- **Uniform sampling with compression.** Sample at a fixed rate, then compress the stream with the methods above.

**Keyframe reduction** removes the keys that interpolation of their neighbours reproduces, so the motion stays the same within a tolerance.

**Clip compression** is the name for the methods that store each value in fewer bits or replace keys by fitted curves, and so lose a little precision; Strata has none.

Strata keeps irregular keys with exact 32-bit values, reduces keys when it imports a clip, and shares identical key times between channels. Sampling finds a key with a binary search. The choice costs memory: a clip of a compressing engine can be several times smaller. It wins simplicity: the sampling code is short enough to read in one sitting, the stored numbers are the artist's numbers, and the only loss is a tolerance far below what the eye sees.

:::why[Reduction now, compression when measured]
Compression adds a decoder to every sample, tuning of error bounds per joint, and a second format to test. The project's plan for later work lists compressed clips for the day a measurement shows that clip memory or bandwidth is a real cost. Until then Strata keeps the code that can be wrong small. The page [Limits of the animation system](limits.md) states this absence together with the others.
:::

## The map

A clip travels through several stages and threads before a joint moves. The :term[importer]{id=importer}, on a worker, reduces the keys of each channel and makes the clip. The clip is saved in its cooked form. A loading worker reads that form back into a clip. The animation system binds the clip to a skeleton, and sampling runs while animators are evaluated.

```mermaid caption="The life of a clip. Keys are reduced and shared when the clip is made, the cooked bytes are checked when it is loaded, a binding is made once for each skeleton, and sampling then gives a pose." alt="A flow diagram from a glTF file to an importer, then to a reduction of keys, then to the creation of a clip, then to cooked bytes. The bytes are decoded and checked into a loaded clip. The loaded clip is bound to a skeleton once. The clip and its binding are sampled to give a pose per joint, and rotation sampling calls the slerp function."
flowchart TB
  G["glTF file"] --> I["Importer (worker)"]
  I -->|"ReduceKeys per channel"| D["AnimationChannelData"]
  D -->|"AnimationClip Create"| C["AnimationClip"]
  C -->|"Serialize (cooked form)"| S["STAC bytes"]
  S -->|"Deserialize (loading worker)"| L["AnimationClip, loaded"]
  L -->|"Bind skeleton, once"| B["AnimationClipBinding"]
  L --> P["Sample"]
  B --> P
  P --> J["JointPose per joint"]
  P -.-> M["AnimationMath Slerp"]
```

A **clip** is a named set of channels together with the arrays that the channels read.

A **channel** holds the keys of one path of one joint, where a path is the translation, the rotation or the scale. A key is a time and the value at that time. A clip cannot hold two channels for the same path of the same joint, and it names the joint with text, never with a number.

Each channel is one small record: the joint's name (an index into the clip's list of names), the path, the interpolation, the number of keys, and two offsets. The first offset says where its times start in one shared array of times. The second says where its values start in one shared array of values. Channels that have the same times point at the same run of the time array.

```mermaid caption="The storage of a clip. Every channel record points into one array of times, which channels with equal times share. Each record also points into one array of values, where a cubic key holds an in-tangent, a value and an out-tangent." alt="A diagram of three channel records that point into two arrays. All three records point at one run of three times. The first two records point at runs of nine values each. The third points at a run of twenty-seven values: for each key, three numbers of in-tangent, three of value and three of out-tangent."
flowchart LR
  subgraph Channels["Channel records"]
    C0["Shoulder, Translation, Linear, 3 keys, FirstTime 0, FirstValue 0"]
    C1["Shoulder, Scale, Linear, 3 keys, FirstTime 0, FirstValue 9"]
    C2["Elbow, Translation, CubicSpline, 3 keys, FirstTime 0, FirstValue 18"]
  end
  subgraph Times["Times array"]
    T["0.0, 1.0, 3.0"]
  end
  subgraph Values["Values array"]
    V0["9 floats: x, y, z for each key"]
    V1["9 floats: x, y, z for each key"]
    V2["27 floats: in-tangent, value, out-tangent, each x, y, z, for each key"]
  end
  C0 --> T
  C1 --> T
  C2 --> T
  C0 --> V0
  C1 --> V1
  C2 --> V2
```

The interpolation says how the value runs between two keys, and it is one of the three samplers of glTF. `Step` holds the earlier key's value until the next key. `Linear` moves in a straight line between the keys, and for rotations along the shorter arc of a sphere. `CubicSpline` follows a smooth curve that leaves each key along a slope that the file gives.

A **tangent** is the slope that a cubic key stores for the curve to follow as it arrives at the key (the in-tangent) and leaves it (the out-tangent). A cubic key therefore holds three groups of numbers, in this order: in-tangent, value, out-tangent. The first key's in-tangent and the last key's out-tangent exist but no sample reads them.

The clip lasts until the last key of any of its channels. Before a channel's first key the channel holds the first value, and after its last key it holds the last value. A clip does not loop: the caller picks the time, and a looping animation wraps the time before it asks.

## The contract

These rules say what a caller may assume and what it must do. Each has its reason.

1. **A clip never changes after it is made.** `Sample` promises not to change the clip and writes only into the pose it receives, so several animators can sample one clip in the same frame. The reason is memory: one clip serves every character that plays it.
2. **Every channel has at least one key, strictly increasing finite times that are not negative, and finite values.** `Create` and `Deserialize` reject anything else with a reason. The reason is that sampling can then search and divide by a key span without a check for zero.
3. **Rotations are unit quaternions.** `Create` and `Deserialize` :term[normalize]{id=normalization} the rotation values, and `SampleChannel` normalizes its result, also for cubic channels, whose tangents would otherwise stretch it.
4. **Time may be any number.** A time before the first key gives the first value, and a time after the last key gives the last. The reason is that callers then need no special case at the ends of a motion.
5. **A joint without a channel keeps what the caller's pose holds.** The caller starts from the skeleton's :term[rest pose]{id=rest-pose}. A clip that animates only the arm leaves the legs where the rest pose puts them.
6. **A clip is bound once for each skeleton.** `Sample` takes the binding, and the system keeps it next to the clip. The reason is the cost of a name lookup, which the paragraphs after the two asides below show.
7. **A cooked clip is untrusted input.** `Deserialize` must reject truncated and garbage bytes without crashing, and without sampling outside the clip's arrays later.

:::note[Joint names are unique]
A skeleton must not hold two joints of one name, because a clip finds its joint by that name and a duplicate would make the choice ambiguous. The skeleton :term[loader]{id=loader} rejects duplicates, and the glTF importer renames a node whose name is taken. The rule is the reason a clip needs no joint indices at all.
:::

:::rule[Loaders cope with bad bytes]
A loader may meet a file that is cut short or full of garbage, and the engine must not crash on it. Every size a file claims is checked against a limit and against the bytes that remain, before the loader allocates anything. The reason is the same as for the skeleton: a file is input from outside, and the editor opens files that an agent or a download made. [Robustness of loaders](../assets/robustness.md) shows the whole pipeline.
:::

**Binding** is making the map from a clip's channels to the joints of one skeleton: for each target name, the joint index in that skeleton, or no joint. Engines bind a clip in three ways:

- **By index.** The clip stores joint numbers. Playing is fast, but the clip works only on the skeleton it was made for, and a change of the joint order silently breaks it.
- **By name.** The clip stores names, and a lookup makes the map once. Any skeleton that has joints of those names can play the clip; Strata does this.
- **Through a retargeting table.** A table maps one rig's joints to another's and corrects for proportions. Unreal and Unity's rigs for human characters work this way.

**Retargeting** is playing a clip on a skeleton with other proportions or other joint names. Strata matches names and nothing else. A joint that has no channel stays at its rest pose. A skeleton with other proportions gets the same local rotations on its own bones, which can make feet slide or float. A clip for a rig with other names needs its channels renamed before import.

The common mistake is a name lookup in every frame. Finding a joint by name costs a :term[hash]{id=hash} and a compare. With 50 joints, 100 characters and 60 frames per second that is 300,000 lookups every second, all with the same answers. Strata finds each name once and keeps an array of joint indices, so sampling only follows numbers.

:::elsewhere
Unreal Engine's retargeting and Unity's rigs for human characters solve the case that name matching cannot: rigs of different proportions. They cost a setup step for each rig and a mapping to maintain. See the entries in Further reading.
:::

## A toy version

The toy samples one channel of single floats with :term[linear interpolation]{id=linear-interpolation}. It does what every sampler must do: find the key, hold the ends, and turn the time into a weight between two keys. It has no names, no rotations and no checks; the real code adds them.

:::question
The toy uses a function that takes a reference and a vector of floats. If those are new, read [functions and vectors](../basics/programming-2.md) and [classes and references](../basics/programming-3.md) first.
:::

The channel has keys at 0, 1 and 3 seconds with the values 0, 2 and 1. The program asks for seven times, from before the first key to after the last, and prints the key it used and the value.

```cpp sketch="animation-clips-toy.cpp"
// A linear-only clip sampler for one channel of single floats: binary search for the key, hold outside the keys.
#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <vector>

namespace
{

	struct Channel
	{
		std::vector<float> Times;
		std::vector<float> Values;
	};

	// The last key whose time is not after `time`.
	size_t FindKey(const Channel& channel, float time)
	{
		auto next = std::upper_bound(channel.Times.begin(), channel.Times.end(), time);
		size_t index = static_cast<size_t>(next - channel.Times.begin());
		return index == 0 ? 0 : index - 1;
	}

	float Sample(const Channel& channel, float time, size_t& outKey)
	{
		const size_t last = channel.Times.size() - 1;
		if (!(time > channel.Times[0]) || last == 0)
		{
			outKey = 0;
			return channel.Values[0];
		}
		if (time >= channel.Times[last])
		{
			outKey = last;
			return channel.Values[last];
		}
		const size_t key = std::min(FindKey(channel, time), last - 1);
		const float span = channel.Times[key + 1] - channel.Times[key];
		const float s = (time - channel.Times[key]) / span;
		outKey = key;
		return channel.Values[key] + (channel.Values[key + 1] - channel.Values[key]) * s;
	}

}

int main()
{
	const Channel channel { { 0.0f, 1.0f, 3.0f }, { 0.0f, 2.0f, 1.0f } };
	for (float time : { -1.0f, 0.0f, 0.5f, 1.0f, 2.0f, 3.0f, 5.0f })
	{
		size_t key = 0;
		const float value = Sample(channel, time, key);
		std::printf("t = %4.1f  key %zu  value %.2f\n", static_cast<double>(time), key, static_cast<double>(value));
	}
	return 0;
}
```

```text output-of="animation-clips-toy.cpp"
t = -1.0  key 0  value 0.00
t =  0.0  key 0  value 0.00
t =  0.5  key 0  value 1.00
t =  1.0  key 1  value 2.00
t =  2.0  key 1  value 1.50
t =  3.0  key 2  value 1.00
t =  5.0  key 2  value 1.00
```

1. **Lines 19-21:** `upper_bound` gives the first key after the time, so one less is the key at or before it, and 0 guards a time before the first key.
2. **Lines 27-36:** a single key, a time at or before the first key, or a time at or after the last key returns one key's value, so the search never meets the ends.
3. **Lines 37-39:** the pair of keys is `key` and `key + 1`, and the weight is the distance from the key over the span.
4. **Line 41:** the linear mix of the two values.

At 0.5 seconds the value is 1: halfway between 0 and 2. At 2 seconds the toy uses key 1 (time 1) with a span of 2, so the weight is 0.5 and the value is 2 plus (1 minus 2) times 0.5, which is 1.5. At 3 seconds the time equals the last key, so the toy holds the last value without a search. The two ends are cases of their own, and that is what makes the search safe: it only runs when the time lies strictly inside the keys.

## The real code, in the order data flows

Strata differs from the toy in four ways. It has three interpolations and three paths, and rotations need care. It stores many channels in shared arrays and reduces keys before the clip is made. It checks everything it reads. The sections follow a clip from the importer to a pose.

### Reduction at import

The importer calls `ReduceKeys` on each channel before it makes the clip. A baked animation often has a key at every frame of a motion that is a straight line for half a second. The function keeps the keys that the interpolation between their kept neighbours does not reproduce.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L256-L301"
std::vector<uint8_t> keep(keys, 0);
keep.front() = 1;
keep.back() = 1;
size_t lastKept = 0;
for (size_t key = 1; key + 1 < keys; key++)
{
	// Each key tests up to c_ReductionWindow earlier ones: a stretch of keys is milliseconds of work.
	if (isCancelled && key % c_ReductionCancelInterval == 0 && isCancelled())
		return false;
	bool removable = key - lastKept <= c_ReductionWindow;
	if (removable && channel.Interpolation == AnimationInterpolation::Step)
	{
		// A step holds the previous kept value: a key repeating it changes nothing.
		removable = std::equal(value(key), value(key) + components, value(lastKept));
	}
	else if (removable)
	{
		// Every key since the last kept one must lie on the interpolation from it to the next key.
		const float startTime = channel.Times[lastKept];
		const float span = channel.Times[key + 1] - startTime;
		for (size_t tested = lastKept + 1; removable && tested <= key; tested++)
		{
			const float s = (channel.Times[tested] - startTime) / span;
			float interpolated[4];
			if (rotation)
			{
				const glm::quat result = AnimationMath::Slerp(AnimationMath::Normalize(ReadRotation(value(lastKept))), AnimationMath::Normalize(ReadRotation(value(key + 1))), s);
				interpolated[0] = result.x;
				interpolated[1] = result.y;
				interpolated[2] = result.z;
				interpolated[3] = result.w;
			}
			else
			{
				for (uint32_t component = 0; component < components; component++)
					interpolated[component] = value(lastKept)[component] + (value(key + 1)[component] - value(lastKept)[component]) * s;
			}
			removable = matches(interpolated, value(tested));
		}
	}
	if (!removable)
	{
		keep[key] = 1;
		lastKept = key;
	}
}
```

1. **Lines 256-259:** the first and last key always stay, and `lastKept` starts at the first.
2. **Lines 263-264:** every 256th key asks the cancel function, and a yes returns false. Nothing has been written back yet, so the channel is exactly as it came.
3. **Lines 265-270:** a key more than 256 keys after the last kept one is kept at once, which bounds the work. For Step, a key that repeats the last kept value is dropped.
4. **Lines 273-295:** for the other paths, every key since the last kept one must lie on the interpolation from the last kept key to the next key. Rotations use `Slerp`, so a reduction judges rotations the way sampling will.
5. **Lines 296-300:** one failing test keeps the key and starts a new run from it.

A key is judged against the next key, not against the key before it. The tolerance is `1e-5` of the value (or of 1, if the value is smaller) for translations and scales. For rotations it is `1e-4` as the distance between the two unit :term[quaternions]{id=quaternion}, about 0.01 degrees. Cubic channels are never reduced, because dropping a key would change the slopes around it.

:::example[Reducing five keys]
A linear channel has keys at the times 0, 1, 2, 3 and 4 with the values 0, 1, 2, 3 and 5. The first and last keys stay. Key 1 lies on the line from key 0 to key 2, which gives 1 at time 1, so it goes. Key 2 lies on the line from key 0 to key 3, where the value equals the time, so it goes too.

Key 3 is tested against the line from key 0 to key 4, which gives 1.25 at time 1 while key 1 holds 1, so the test fails and key 3 stays. The result is three keys: times 0, 3 and 4, values 0, 3 and 5. Sampling at time 2 gives 2 before the reduction and 2 after.
:::

The price of reduction is paid once, at import, and it is bounded: a window of 256 keys and a cancel check make a long channel cheap to refuse. Its other price is that channels no longer have the same times, so fewer channels can share their time arrays, as the next section shows.

### Sharing key times

`Create` validates the channels and then stores them in the clip's arrays. Channels that come from one glTF input, or that were baked at one rate, have identical times. Instead of copying the times again, the clip points the new channel at the run it already holds.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L206-L222"
// Channels of one glTF sampler input (or baked at one rate) share their times.
const TimesKey timesKey { Hash::FNV1a(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(data.Times.data()), data.Times.size() * sizeof(float))), keys };
std::vector<uint32_t>& candidates = sharedTimes[timesKey];
auto shared = std::find_if(candidates.begin(), candidates.end(), [&](uint32_t offset)
{
	return std::equal(data.Times.begin(), data.Times.end(), clip->m_Times.begin() + offset);
});
if (shared != candidates.end())
{
	channel.FirstTime = *shared;
}
else
{
	channel.FirstTime = static_cast<uint32_t>(clip->m_Times.size());
	clip->m_Times.insert(clip->m_Times.end(), data.Times.begin(), data.Times.end());
	candidates.push_back(channel.FirstTime);
}
```

1. **Line 207:** the lookup key is the :term[FNV-1a]{id=fnv-1a} hash of the time bytes and the number of keys.
2. **Lines 208-212:** the candidates with that key are compared exactly, number for number. A hash collision therefore cannot make two different time arrays one.
3. **Lines 213-216:** a match uses the earlier offset again, and the times are not stored again.
4. **Lines 217-222:** no match appends the times and remembers the offset for later channels.

:::example[What sharing saves]
Take the 50 joint walk again with translation and rotation animated only: 100 channels of 60 keys. One time array has 240 bytes. Without sharing, the times take 24,000 bytes; with sharing they take 240. The values take 84,000 bytes either way, so the clip shrinks from 108,000 to 84,240 bytes. The saving is 23,760 bytes, or 22 %, and it costs one hash of 240 bytes for each channel when the clip is made.
:::

### Loading the cooked form

A clip is saved in the cooked format of the Strata animation clip (:term[STAC]{id=stsk}), version 1. The file holds a :term[header]{id=header} with the counts, the clip's name, the target names, one 20-byte record for each channel, the times and then the values. `Deserialize` must never trust the counts in the header, because anyone can change a byte of a file. It checks them against the limits and against the bytes that remain before it allocates.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L351-L361"
BinaryReader reader(data);
const CookedClipHeader header = reader.Read<CookedClipHeader>();
if (!reader.IsValid() || header.Magic != c_ClipMagic)
	return fail("Not a cooked Strata animation clip");
if (header.Version != c_CookedVersion)
	return fail(fmt::format("Unsupported cooked animation clip version {}", header.Version));
// Every count is bounded by the format's limits and by the bytes that are left, before anything is allocated.
if (header.ChannelCount == 0 || header.ChannelCount > c_MaxChannels || header.TargetCount == 0 || header.TargetCount > header.ChannelCount
	|| header.TimeCount == 0 || header.TimeCount > c_MaxKeys || header.ValueCount == 0 || header.ValueCount > c_MaxValues
	|| (static_cast<uint64_t>(header.ChannelCount) * sizeof(CookedChannel) + (header.TimeCount + header.ValueCount) * sizeof(float)) > reader.GetRemaining())
	return fail("Cooked animation clip header is corrupt");
```

1. **Lines 351-354:** a header that cannot be read, or that has the wrong :term[magic number]{id=magic-number}, is not a clip.
2. **Lines 355-356:** a version the code does not know is refused, because the layout could differ.
3. **Lines 358-360:** the counts must not be zero and must stay below the limits (at most 196,605 channels, 2^24 keys, 2^26 values), and the records, times and values together must fit in the remaining bytes.
4. **Line 361:** one message for every failure of these, and nothing has been allocated yet.

After the header the function reads the names (each non-empty and unique), then the channel records (valid path, valid interpolation, a target inside the list), then the arrays. It rejects a cut file and a file with bytes left over. It then checks that every channel lies inside the arrays, that its times increase, that no joint part has two channels, and that the duration in the header equals the largest last key. A failing check returns null with a reason, and the asset system reports a failed load.

### Binding

The animation system binds a clip when it has both the clip and the skeleton, and it keeps the binding next to the clip. `Bind` walks the clip's names, not its channels, so a joint is found once even if three channels name it.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L438-L457"
AnimationClipBinding AnimationClip::Bind(const Skeleton& skeleton) const
{
	AnimationClipBinding binding;
	std::vector<JointIndex> targetJoints(m_TargetNames.size());
	for (size_t target = 0; target < m_TargetNames.size(); target++)
		targetJoints[target] = skeleton.FindJoint(m_TargetNames[target]);
	binding.ChannelJoints.resize(m_Channels.size());
	for (size_t index = 0; index < m_Channels.size(); index++)
	{
		const AnimationChannel& channel = m_Channels[index];
		const JointIndex joint = targetJoints[channel.Target];
		binding.ChannelJoints[index] = joint;
		if (joint == c_NoJoint)
			continue;
		binding.BoundChannels++;
		if (joint == skeleton.GetRootMotionJoint())
			binding.RootMotionChannels[static_cast<size_t>(channel.Path)] = static_cast<int32_t>(index);
	}
	return binding;
}
```

1. **Lines 441-443:** one lookup for each name of the clip, through the skeleton's table of names.
2. **Lines 445-449:** each channel copies the answer for its target, so a channel's joint is a plain index.
3. **Lines 450-452:** a name the skeleton lacks gives `c_NoJoint`, and the channel is skipped; the others are counted in `BoundChannels`.
4. **Lines 453-454:** a channel of the skeleton's root motion joint is also recorded by path, so root motion can be sampled alone.

`Sample` then loops over the channels and writes each into `pose[joint]`. A joint index outside the pose is skipped, so a binding of the wrong skeleton cannot write outside the pose. It writes the wrong joints, though, which is why the system keeps the binding with its skeleton, and binds again when the skeleton asset changes. `SampleRootMotionJoint` starts from the rest pose of the root motion joint and samples only the three channels that `Bind` recorded; [Root motion](root-motion.md) uses it.

### Sampling: find the key and hold the ends

`SampleChannel` turns a time into one value. It first reads the layout: how many numbers a key has (3, or 4 for rotations), and the stride (three times as many for a cubic channel). It then decides whether the time is inside the keys.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L470-L491"
const uint32_t components = GetComponentCount(channel.Path);
const uint32_t stride = GetKeyStride(channel.Path, channel.Interpolation);
const bool cubic = channel.Interpolation == AnimationInterpolation::CubicSpline;
const float* values = m_Values.data() + channel.FirstValue;
const float* times = m_Times.data() + channel.FirstTime;
auto valueOf = [&](uint32_t key) { return values + static_cast<size_t>(key) * stride + (cubic ? components : 0u); };

float result[4];
const uint32_t last = channel.KeyCount - 1;
if (channel.KeyCount == 1 || !(time > times[0]) || time >= times[last])
{
	const float* value = valueOf(channel.KeyCount == 1 || !(time > times[0]) ? 0u : last);
	std::copy(value, value + components, result);
}
else
{
	const uint32_t key = std::min(FindKey(channel, time), last - 1);
	const float keyTime = times[key];
	const float span = times[key + 1] - keyTime;
	const float s = std::clamp((time - keyTime) / span, 0.0f, 1.0f);
	const float* from = valueOf(key);
	const float* to = valueOf(key + 1);
```

1. **Lines 470-475:** the stride and `valueOf` hide the cubic layout: a cubic key's value sits after its in-tangent.
2. **Lines 479-483:** a single key, a time at or before the first key, or a time at or after the last key copies one key's value without a search. The test is written so that a :term[NaN]{id=nan} time also lands here.
3. **Line 486:** `FindKey` returns the last key whose time is not after the given time, found with `std::upper_bound` on the channel's run of times, which is a binary search. The `std::min` keeps the pair inside the channel.
4. **Lines 487-489:** the weight is the distance from the key divided by the span, clamped to the range 0 to 1.

### The three interpolations

With the pair of keys and the weight $s$ the rest is arithmetic. Step copies the earlier value. Linear mixes the two values, and for rotations it calls `Slerp`. The cubic curve evaluates glTF's :term[Hermite curve]{id=cubic-hermite-curve}.

```cpp src="Strata/src/Strata/Animation/AnimationClip.cpp#L492-L524"
switch (channel.Interpolation)
{
	case AnimationInterpolation::Step:
		std::copy(from, from + components, result);
		break;
	case AnimationInterpolation::Linear:
		if (channel.Path == AnimationPath::Rotation)
		{
			const glm::quat rotation = AnimationMath::Slerp(ReadRotation(from), ReadRotation(to), s);
			result[0] = rotation.x;
			result[1] = rotation.y;
			result[2] = rotation.z;
			result[3] = rotation.w;
		}
		else
		{
			for (uint32_t component = 0; component < components; component++)
				result[component] = from[component] + (to[component] - from[component]) * s;
		}
		break;
	case AnimationInterpolation::CubicSpline:
	{
		// glTF's cubic Hermite spline: the key's out-tangent and the next key's in-tangent, scaled by the span.
		const float* outTangent = values + static_cast<size_t>(key) * stride + 2u * components;
		const float* inTangent = values + static_cast<size_t>(key + 1) * stride;
		const float s2 = s * s;
		const float s3 = s2 * s;
		const float h00 = 2.0f * s3 - 3.0f * s2 + 1.0f;
		const float h10 = (s3 - 2.0f * s2 + s) * span;
		const float h01 = -2.0f * s3 + 3.0f * s2;
		const float h11 = (s3 - s2) * span;
		for (uint32_t component = 0; component < components; component++)
			result[component] = h00 * from[component] + h10 * outTangent[component] + h01 * to[component] + h11 * inTangent[component];
```

1. **Lines 494-496:** Step copies the earlier key's value.
2. **Lines 497-511:** Linear is `from + (to - from) * s` for translations and scales, and `Slerp` for rotations, never a plain mix of four numbers.
3. **Lines 515-516:** the tangents come from the right keys: the earlier key's out-tangent and the later key's in-tangent.
4. **Lines 519-522:** the four Hermite weights, where the two tangent weights `h10` and `h11` carry a factor `span`.
5. **Line 524:** the value is the weighted sum of two values and two tangents.

$$h_{00}=2s^3-3s^2+1,\quad h_{10}=(s^3-2s^2+s)\,d,\quad h_{01}=-2s^3+3s^2,\quad h_{11}=(s^3-s^2)\,d$$

$s$ is the weight, from 0 to 1, and $d$ is the span between the two keys in seconds. The value is $h_{00}v_0+h_{10}m_0+h_{01}v_1+h_{11}m_1$, where $v_0$ and $v_1$ are the two key values, $m_0$ is the earlier key's out-tangent and $m_1$ the later key's in-tangent. Each tangent is a slope in value per second, but $s$ runs from 0 to 1, so the factor $d$ turns the slope into the change over the whole span. The classic mistake is to omit that factor; the curve then looks right for a span of one second and wrong for every other.

:::example[One sample by hand, three ways]
Take the channel of the toy with keys at 0, 1 and 3 seconds and values 0, 2 and 1. Sample it at 2 seconds. The search gives key 1 (time 1), the span is 2 and the weight is $(2-1)/2=0.5$. Step gives 2. Linear gives $2+(1-2)\times0.5=1.5$.

For the cubic version give key 1 an out-tangent of 1 and key 2 an in-tangent of -2. With $s=0.5$ the weights are $h_{00}=0.5$, $h_{10}=0.125\times2=0.25$, $h_{01}=0.5$ and $h_{11}=-0.125\times2=-0.25$. The value is $0.5\times2+0.25\times1+0.5\times1+(-0.25)\times(-2)=2.25$. Without the factor $d$ the same sum gives 1.875, a wrong answer that looks plausible.
:::

The figure draws the three curves through the same keys. The cubic curve passes above 2 between the second and third key, because the out-tangent leaves key 1 rising.

::figure{id=interpolation-curves}

### Slerp

A rotation is a quaternion, and a straight mix of two quaternions does not turn at a steady speed. The middle is fast, the ends are slow, and the length of the result is not 1. `Slerp` fixes both, and it handles the :term[double cover]{id=double-cover}: $q$ and $-q$ are the same rotation, and the mix must not go the long way round.

```cpp src="Strata/src/Strata/Animation/AnimationTypes.h#L43-L58"
inline glm::quat Slerp(const glm::quat& a, glm::quat b, float t)
{
	float cosine = a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
	if (cosine < 0.0f)
	{
		b = -b;
		cosine = -cosine;
	}
	if (cosine > 0.9995f)
		return Normalize(glm::quat(a.w + (b.w - a.w) * t, a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t));
	const float angle = std::acos(cosine);
	const float sine = std::sin(angle);
	const float weightA = std::sin((1.0f - t) * angle) / sine;
	const float weightB = std::sin(t * angle) / sine;
	return Normalize(glm::quat(a.w * weightA + b.w * weightB, a.x * weightA + b.x * weightB, a.y * weightA + b.y * weightB, a.z * weightA + b.z * weightB));
}
```

1. **Lines 45-50:** the :term[dot product]{id=dot-product} is negative when the two quaternions are in opposite halves of the sphere. Flipping the sign of one makes the arc the shorter one.
2. **Lines 51-52:** when the quaternions are closer than about 1.8 degrees as vectors of four numbers, the :term[cosine]{id=cosine} is above 0.9995 and the :term[sine]{id=sine} in the :term[slerp]{id=slerp} formula is almost zero. Dividing by it loses precision, so the function mixes in a straight line and normalizes instead.
3. **Lines 53-57:** the slerp weights $\sin((1-t)\theta)/\sin\theta$ and $\sin(t\theta)/\sin\theta$ for the angle $\theta$ between the two, then a normalization against rounding.

:::example[Slerp against the straight mix]
Take the identity rotation and a quarter turn about Z: $(0,0,0,1)$ and $(0,0,0.7071,0.7071)$. Their dot product is 0.7071, so $\theta$ is 45 degrees in four dimensions. At $t=0.25$ slerp gives $z=0.1951$, which is exactly 22.5 degrees of rotation. The straight mix gives $(0, 0, 0.1768, 0.9268)$, which normalizes to $z=0.1874$, a rotation of 21.6 degrees. The error vanishes at the ends and the middle and peaks between them, and it is the reason that Strata uses the straight mix only for tiny arcs.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Binding by index | Engines that bake a clip to one rig | No name lookup at all, smaller clips | Clips that work on any skeleton of the same names; the safety of a name that does not move |
| Retargeting tables | Unreal, Unity's human rigs | One clip for rigs of different proportions | A setup step for each rig and a table to keep correct |
| Quantization and curve fitting | The Animation Compression Library | Clips several times smaller | Exact stored values; a decoder in every sample; error bounds to tune |
| Uniform sampling with compression | Engines built on a fixed sample rate | No key search; steady memory access | Small clips for slow motions, because every channel stores every sample |
| Keys of 16 bits or less in the file | Engines tuned for memory | Half the bytes of values | Exact keys; simpler sampling |

## How it is tested

The suite `Animation.Sampling` tests the sampling and the reduction:

- `Step, linear and cubic spline channels interpolate as glTF defines` samples three channels at chosen times, including times before the first key and after the last. It checks the cubic curve against $3s^2-2s^3$ for flat tangents and against the line for tangents that match the chord.
- `Rotations interpolate along the shorter arc and stay normalized` uses keys of opposite sign and a cubic channel with long tangents, and checks that the angle grows steadily from 0 to 170 degrees and that every result has length 1.
- `Keyframe reduction drops only keys the interpolation reproduces` checks three cases. 31 keys on a line with one key off it keep five keys. A run of rotations on one arc reduces to its ends. Repeated step values reduce to their changes.
- `Keyframe reduction of a long channel stops when it is cancelled, leaving the channel as it was` checks the cancel path and the number of times the function asks.

The clip cases of `Animation.Assets` test `Create` and the cooked form: `Clips validate, share key times and round trip` and `Clip loading rejects truncated and garbage bytes`. The second one damages the cooked bytes in many ways, and every clip that still loads must sample at five times without reading outside its data. Run the suites with `StrataTests --test-suite=Animation*` from the build folder.

## Changing it safely

The extension points are few. A new interpolation is a new value of `AnimationInterpolation` with its own key stride. It needs a branch in `SampleChannel`, a rule in `ReduceKeys` (reduce it, or leave it as the cubic channels are left) and a place in the loader's validity checks.

- A change to the stored layout bumps `c_CookedVersion`, and the loader keeps rejecting versions it does not know. The reason is the old files that exist.
- A change to what the importer produces, such as a new tolerance, bumps the importer's version, so that cached clips are made again.
- A new count in the file gets a limit and a check against the remaining bytes before an allocation. The reason is rule 7 above.
- Sampling keeps its promise not to change the clip and allocates nothing, because it runs for every animator in every frame.

Pass `Animation.Sampling` and `Animation.Assets` and the feature test before a change lands, and extend the byte-damage test whenever the format changes.

## Summary

- A channel stores the keys of one path of one joint, in arrays that the clip's channels share. Sampling finds the key with a binary search, holds the end values outside the keys, and applies step, linear (slerp for rotations) or cubic Hermite with tangents scaled by the span.
- A clip binds to a skeleton by name once, skipping missing joints, so it plays on any skeleton with the same names and does not adapt to other proportions.
- Keyframe reduction and shared key times shrink a clip and cost a tolerance at import; Strata has no compression.
- The loader bounds every count by its limit and by the remaining bytes before it allocates.

## Check yourself

1. A linear channel has keys at 0, 2 and 4 seconds with the values 10, 20 and 0. What does it give at 3 seconds, at 7 and at -1? (a) 10, 0 and 10 (b) 10, 0 and 0 (c) 15, 0 and 10

   :::answer{tests="sample-channel"}
   Option (a) is right. At 3 seconds the pair is keys 1 and 2, the span is 2 and the weight is 0.5, so the value is $20+(0-20)\times0.5=10$. At 7 the time is after the last key, so the channel holds 0, and at -1 it holds the first value, 10. Option (b) holds the wrong end for -1. Option (c) mixes the first and second keys for 3 seconds, a mistake in the search.
   :::

2. A cubic segment runs from 1 to 3 seconds. The earlier key has value 2 and out-tangent 1, and the later one has value 1 and in-tangent -2. What is the value at 2 seconds, and what would it be if the tangents were not multiplied by the span?

   :::answer{tests="sample-channel"}
   The weight is 0.5 and the span is 2. The weights are $h_{00}=h_{01}=0.5$, $h_{10}=0.125\times2=0.25$ and $h_{11}=-0.125\times2=-0.25$. The value is $0.5\times2+0.25\times1+0.5\times1+(-0.25)\times(-2)=2.25$. Without the span the two tangent weights are 0.125 and -0.125, and the sum is $1+0.125+0.5+0.25=1.875$.
   :::

3. A clip has channels for the targets `Hips`, `Spine` and `Tail`. Skeleton A has the joints `Hips` and `Spine`; skeleton B has `Hips`, `Spine2` and `Tail`. How many channels does the binding count as bound for each, and what happens to `Spine` on B?

   :::answer{tests="bind-by-name"}
   A has 2 bound channels, `Hips` and `Spine`, and the `Tail` channel is skipped. B has 2 bound channels, `Hips` and `Tail`, and the `Spine` channel is skipped. On B the joint `Spine2` has no channel, so it keeps whatever pose the caller started from, normally its rest pose. Nothing maps `Spine` to `Spine2`: that is retargeting, which Strata does not do.
   :::

4. A clip of 20 joints animates translation and rotation, 40 channels, baked at 30 keys. How many bytes of key times does it store with shared times and without? What happens to the saving if reduction first removes different keys from each channel?

   :::answer{tests="reduction-sharing"}
   One time array has 30 floats, or 120 bytes. Without sharing the clip stores 40 times 120, which is 4,800 bytes. With sharing it stores 120. Reduction that keeps different keys in each channel gives each channel its own times, so the arrays no longer match and the saving shrinks, while the removed keys save their values as well.
   :::

5. A damaged file claims 4 billion channels in its header. What does `Deserialize` do, and why does it matter that it does it before any allocation? (a) it allocates and then fails on the first channel (b) it rejects the header because the count is above the limit (c) it clamps the count to the limit

   :::answer{tests="safe-loading"}
   Option (b) is right. The count is above 196,605, and the records alone could not fit in the remaining bytes. The function fails with the message that the header is corrupt. Option (a) would ask the system for billions of bytes on the word of a damaged file. Option (c) would silently load a clip that is not the clip in the file.
   :::

## Exercises

1. **Basic.** Take the channel with keys at 0, 1 and 3 seconds and values 0, 2 and 1. Its cubic keys hold in-tangent, value and out-tangent: 0, 0, 2 for key 0; 2, 2, 1 for key 1; and -2, 1, 0 for key 2. Sample the step, linear and cubic versions at 0.5 and 2.5 seconds.

   :::answer[Worked solution]{tests="sample-channel"}
   At 0.5 seconds the pair is keys 0 and 1, the span is 1 and the weight is 0.5. Step gives 0 and linear gives 1. Cubic: $h_{00}=0.5$, $h_{10}=0.125$, $h_{01}=0.5$, $h_{11}=-0.125$, and the tangents are the out-tangent 2 of key 0 and the in-tangent 2 of key 1, so the value is $0+0.25+1-0.25=1$.

   At 2.5 seconds the pair is keys 1 and 2, the span is 2 and the weight is 0.75. Step gives 2 and linear gives $2-0.75=1.25$. Cubic: $h_{00}=0.15625$, $h_{10}=0.046875\times2=0.09375$, $h_{01}=0.84375$, $h_{11}=-0.140625\times2=-0.28125$. With the out-tangent 1 and the in-tangent -2 the value is $0.3125+0.09375+0.84375+0.5625=1.8125$.
   :::

2. **Medium.** A Step channel has keys at 0, 1, 2, 3, 4 and 5 seconds with the values 1, 1, 2, 2, 2 and 3. Which keys does `ReduceKeys` keep, and does sampling at 1.5 and 4 seconds change?

   :::answer[Worked solution]{tests="reduction-sharing"}
   The first and last key stay. Key 1 repeats the value of the last kept key (1), so it goes. Key 2 holds 2, a change, so it stays and becomes the last kept key. Keys 3 and 4 repeat 2, so they go.

   The result is keys at 0, 2 and 5 with the values 1, 2 and 3. At 1.5 seconds the channel gave 1 and still gives 1; at 4 seconds it gave 2 and still gives 2. Six keys became three, and the motion is the same.
   :::

3. **Medium.** Trace it yourself. Start from `AnimationClip::Bind` and search the engine for every call that binds a clip to a skeleton. Say how often each runs, and why no joint is found by name while the clip plays.

   :::answer[Worked solution]{tests="bind-by-name"}
   A search for `Bind(` in the animation code finds two calls in `Strata/src/Strata/Animation/AnimationSystem.cpp`. `ResolveSet` binds each clip of an animator's asset set when the clip arrives or the skeleton changes, and stores the binding in the set. `ResolvePlayedClip` binds a clip that is played directly, and binds again when the clip or the skeleton's identity changes. Neither binds in every sample.

   `AnimationClip::Sample` only reads `binding.ChannelJoints`, an array of joint numbers made by `Bind`, so no lookup by name remains in the frame.
   :::

4. **Hard.** Write a program with a cooked clip of three keys: a header with a magic number and a key count, then the times, then the values. Write a loader that checks the count against a limit and the remaining bytes before it allocates, and that rejects times that are not finite, negative or not increasing. Flip each byte of the file in turn and count how many damaged files load.

   :::answer[Worked solution]{tests="safe-loading" solution="sketches/animation-clips-sweep.cpp"}
   The header gives two fields. The loader checks the magic and the count first, then the exact byte size, and only then sets the size of its vectors. The times are checked one by one. The sweep flips every byte with 0xFF and loads the result.

   ```cpp sketch="animation-clips-sweep.cpp"
   // A tiny cooked clip and a loader that bounds every count before it allocates, then a sweep that flips each byte.
   #include <cmath>
   #include <cstdint>
   #include <cstdio>
   #include <cstring>
   #include <vector>

   namespace
   {

   	constexpr uint32_t c_Magic = 0x43544E59;
   	constexpr uint32_t c_MaxKeys = 1024;

   	struct Header
   	{
   		uint32_t Magic;
   		uint32_t KeyCount;
   	};

   	// The bytes: a header, then the key times, then one value per key.
   	std::vector<uint8_t> Cook(const std::vector<float>& times, const std::vector<float>& values)
   	{
   		const Header header { c_Magic, static_cast<uint32_t>(times.size()) };
   		std::vector<uint8_t> bytes(sizeof(Header) + (times.size() + values.size()) * sizeof(float));
   		std::memcpy(bytes.data(), &header, sizeof(Header));
   		std::memcpy(bytes.data() + sizeof(Header), times.data(), times.size() * sizeof(float));
   		std::memcpy(bytes.data() + sizeof(Header) + times.size() * sizeof(float), values.data(), values.size() * sizeof(float));
   		return bytes;
   	}

   	bool Load(const std::vector<uint8_t>& bytes, std::vector<float>& outTimes, std::vector<float>& outValues)
   	{
   		Header header;
   		if (bytes.size() < sizeof(Header))
   			return false;
   		std::memcpy(&header, bytes.data(), sizeof(Header));
   		// Both bounds come before any allocation: the format's limit and the bytes that are left.
   		if (header.Magic != c_Magic || header.KeyCount == 0 || header.KeyCount > c_MaxKeys)
   			return false;
   		if (bytes.size() != sizeof(Header) + 2 * static_cast<size_t>(header.KeyCount) * sizeof(float))
   			return false;
   		outTimes.resize(header.KeyCount);
   		outValues.resize(header.KeyCount);
   		std::memcpy(outTimes.data(), bytes.data() + sizeof(Header), header.KeyCount * sizeof(float));
   		std::memcpy(outValues.data(), bytes.data() + sizeof(Header) + header.KeyCount * sizeof(float), header.KeyCount * sizeof(float));
   		for (uint32_t key = 0; key < header.KeyCount; key++)
   		{
   			const bool increasing = key == 0 || outTimes[key] > outTimes[key - 1];
   			if (!std::isfinite(outTimes[key]) || outTimes[key] < 0.0f || !increasing || !std::isfinite(outValues[key]))
   				return false;
   		}
   		return true;
   	}

   }

   int main()
   {
   	const std::vector<uint8_t> cooked = Cook({ 0.0f, 1.0f, 3.0f }, { 0.0f, 2.0f, 1.0f });
   	int accepted = 0;
   	int rejected = 0;
   	for (size_t position = 0; position < cooked.size(); position++)
   	{
   		std::vector<uint8_t> damaged = cooked;
   		damaged[position] ^= 0xFF;
   		std::vector<float> times;
   		std::vector<float> values;
   		(Load(damaged, times, values) ? accepted : rejected)++;
   	}
   	std::printf("%zu bytes flipped one at a time: %d rejected, %d loaded\n", cooked.size(), rejected, accepted);
   	return 0;
   }
   ```

   ```text output-of="animation-clips-sweep.cpp"
   32 bytes flipped one at a time: 11 rejected, 21 loaded
   ```

   1. **Lines 38-41:** the magic number, the count limit and the exact byte size are checked before anything is allocated.
   2. **Lines 42-45:** only now are the vectors sized and the bytes copied.
   3. **Lines 46-51:** each time must be finite, not negative and larger than the one before it, and each value must be finite.
   4. **Lines 62-69:** the sweep flips every byte in turn and counts the files that load.

   Of the 32 flips, 11 are rejected: the 4 bytes of the magic number, the 4 of the count, and the 3 that make a time negative. The other 21 load, because a flipped value, or a small change to a time, is still a valid number. The format has no :term[checksum]{id=checksum}, and a loader promises safety, not honesty. Whatever the byte, the program never reads outside the bytes or allocates more than its limit.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationClip.h` and `AnimationClip.cpp`: `AnimationClip`, `AnimationChannel`, `AnimationChannelData`, `AnimationClipBinding`, `Create`, `ReduceKeys`, `Serialize`, `Deserialize`, `Bind`, `Sample`, `SampleChannel`, `SampleRootMotionJoint`.
- `Strata/src/Strata/Animation/AnimationTypes.h`: `JointPose`, `JointIndex`, `c_NoJoint`, `AnimationMath::Slerp`.
- `Strata/src/Strata/Animation/AnimationSystem.cpp`: `ResolveSet` and `ResolvePlayedClip`, the two places that bind.
- `Strata/src/Strata/Asset/GltfImporter.cpp`: the importer's calls to `ReduceKeys` and `Create`.
- `StrataTests/src/Animation/AnimationAssetTests.cpp`: the suites `Animation.Assets` and `Animation.Sampling`.

## Further reading

- The Khronos glTF 2.0 specification, the animation section: the three samplers and the scaling of tangents by the key span; intermediate.
- Jason Gregory, "Game Engine Architecture", the chapter on animation: clips, sampling and compression in a production engine; intermediate.
- The documentation and blog of the Animation Compression Library by Nicholas Frechette: quantization and curve fitting in depth, with measurements; advanced.
- Ken Shoemake, "Animating rotation with quaternion curves" (1985): where slerp comes from; advanced.
- The Unreal Engine documentation on animation retargeting and the Unity manual on humanoid avatars: the table-based way to bind clips across rigs; beginner.
