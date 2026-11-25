---
id: animation/blending
title: "Blending and cross-fades"
description: "How an animator mixes up to four clips into one pose while a cross-fade runs, and why walking into running still slides the feet."
kind: internals
size: M
tracks: [E]
needs: [animation/state-machines]
time: 65
learn:
  - id: compute-weights
    text: compute every entry's weight while cross-fades interrupt each other
  - id: pose-blend
    text: explain how Evaluate mixes several entries into one pose
  - id: hemisphere
    text: explain why rotations are summed on one hemisphere
  - id: phase-mismatch
    text: explain why a walk to run cross-fade slides the feet
since: 0.3.0
status: final
---

When a state machine moves a character from one state to the next, the character must not jump. While the change runs, `AnimatorInstance` plays up to four entries at once, each with a share of the result, and mixes their poses into one. An entry is one state that plays: which state, how far into its clip, and its share.

When the change ends, only the target is left. This page covers that mixing: how the shares start, grow and shrink, and how the poses are combined. It does not cover how a state machine decides to change, which the previous page teaches, nor how the character's travel is weighted, which the page on root motion teaches.

## The problem and how engines solve it

Take a character that idles and then starts to walk. If the engine stops the idle clip and starts the walk clip in the same frame, every joint jumps from one angle to another in 16.7 ms (one frame at 60 :term[frames per second]{id=frame-rate}). The player sees a pop. A game needs a way to move from the old pose to the new one over time.

The common answer is the **cross-fade**: for a chosen duration the engine plays the old and the new clip together and mixes their poses, moving the share from the old to the new. Strata does this.

The share of each clip is its **blend weight**: a number from 0 to 1, where all weights together are 1.

Other engines add more tools. A blend tree mixes several clips by a parameter, such as speed, so that a walk and a run give every speed between them. A blend space does the same with two parameters, such as speed and direction. Strata has neither. Its controllers have states and transitions only, and the page on the [limits](limits.md) of the animation module lists what is missing.

A third answer is **inertialization**: the engine plays only the new clip and adds a correction. The correction is the difference between the old pose and the new one at the moment of the change, and it decays to zero over the duration. Playing one clip costs less, but the method needs the velocities of the old pose and cannot show the old motion continuing. Strata does not use it.

All of these meet one more problem. Two cycles, such as a walk and a run, have their foot contacts at different points of their loops. A fade that ignores this mixes a foot that is down with a foot that is up. A fix is **sync markers**, labels in the clips that say where each foot lands (also called phase matching). With them, the engine starts the target at the matching point of its cycle, but Strata has none.

The rest of this page is about the first answer, the one Strata chose.

## The map

The job is split between three places. `AnimationSystem` receives commands and owns one `AnimatorInstance` per animator. The instance holds the entries, the fade's clock and the weights. `Evaluate` reads them and fills a pose.

```mermaid caption="A command or a transition starts a fade. Each update advances the clock and computes the weights again. Evaluation reads the entries and the weights and returns the pose." alt="Boxes for the command, the start of a state, the update of the weights, the evaluation and the skeleton, joined by arrows in the order the data flows."
flowchart LR
	C["AnimationSystem::CrossFade or a transition"] --> S["AnimatorInstance::StartState"]
	S --> E["entries: state, time, StartWeight, Weight"]
	A["Advance: fade clock"] --> U["UpdateWeights"]
	U --> E
	E --> V["Evaluate: blend poses"]
	V --> K["Skeleton::ComputeModelTransforms"]
```

An instance knows nothing about scenes: it takes the clips and the skeleton it needs from its caller.

## The contract

A caller of an animator may rely on these rules, and the code keeps them.

- **At most four entries.** The limit `c_MaxPlaying` is 4. A fifth fade drops the faintest entry, so the cost of a pose never grows with the number of interruptions.
- **The weights sum to 1.** After every update the weights of the entries add up to 1, so a blend never makes the character larger or smaller. The test checks this with a tolerance of 1e-6.
- **The target is last.** The newest entry is the target of the running fade. When the fade ends, it is the only entry, and its weight is exactly 1.
- **A duration of zero is a cut.** `StartState` with a duration of 0, or with nothing playing yet, replaces the entries by one.
- **Bad durations are refused.** `AnimatorInstance::CrossFade` returns `false` for a negative or non-finite duration and caps a longer one at `AnimationController::c_MaxDuration`, 60 seconds.
- **Events follow the state, not the fade.** Events fire from the state the animator is in, not from the states that fade out.

:::why[Weights that always add up to 1]
A blend with weights that sum to 0.9 shrinks every translation by a tenth, and one that sums to 1.2 stretches it. If the weights are always a partition of 1, the blend needs no rescaling and a fade can be interrupted at any moment without a visible jump. The price is that the weights of the entries that fade out depend on each other: when one is dropped, the others must absorb its share.
:::

## A toy version

Before the real code, here is a toy that does only the weights. It holds up to four entries, starts fades, updates the weights from a progress value between 0 and 1, and drops the faintest entry when a fifth fade starts.

:::question
Never wrote a class or called a function? Read [classes and calls](../basics/programming-3.md), [loops and functions](../basics/programming-2.md) and [variables and conditions](../basics/programming-1.md) first.
:::

The main function starts four fades, each before the last one ends, and prints the weights after each update. The class `Fader` below has one function to start a fade and one to update the weights. Look at how `Start` copies each weight into `StartWeight` before it adds the target, and how `DropFaintest` divides what remains.

```cpp sketch="animation-blending-toy.cpp"
// A toy cross-fader: up to four entries, kept shares, the faintest dropped, weights that sum to 1.
#include <cstdio>

struct Entry
{
	int State = 0;
	float StartWeight = 1.0f;
	float Weight = 1.0f;
};

class Fader
{
public:
	static constexpr int c_MaxPlaying = 4;

	void Start(int state)
	{
		if (m_Count == 0)
		{
			m_Entries[0] = Entry{ state, 1.0f, 1.0f };
			m_Count = 1;
			return;
		}
		// Every entry keeps the share it has now as the share it fades out from.
		for (int index = 0; index < m_Count; index++)
			m_Entries[index].StartWeight = m_Entries[index].Weight;
		if (m_Count == c_MaxPlaying)
			DropFaintest();
		m_Entries[m_Count] = Entry{ state, 0.0f, 0.0f };
		m_Count++;
	}

	void Update(float progress)
	{
		if (progress >= 1.0f)
		{
			// The fade is over: only the target (the last entry) is left.
			m_Entries[0] = m_Entries[m_Count - 1];
			m_Entries[0].StartWeight = 1.0f;
			m_Entries[0].Weight = 1.0f;
			m_Count = 1;
			return;
		}
		for (int index = 0; index + 1 < m_Count; index++)
			m_Entries[index].Weight = (1.0f - progress) * m_Entries[index].StartWeight;
		m_Entries[m_Count - 1].Weight = progress;
	}

	void Print(const char* label) const
	{
		float sum = 0.0f;
		std::printf("%-14s", label);
		for (int index = 0; index < m_Count; index++)
		{
			std::printf(" S%d=%.4f", m_Entries[index].State, m_Entries[index].Weight);
			sum += m_Entries[index].Weight;
		}
		std::printf("  sum=%.4f\n", sum);
	}

private:
	void DropFaintest()
	{
		int faintest = 0;
		for (int index = 1; index < m_Count; index++)
		{
			if (m_Entries[index].StartWeight < m_Entries[faintest].StartWeight)
				faintest = index;
		}
		const float dropped = m_Entries[faintest].StartWeight;
		for (int index = faintest; index + 1 < m_Count; index++)
			m_Entries[index] = m_Entries[index + 1];
		m_Count--;
		// The others share the dropped weight in the proportions they had.
		for (int index = 0; index < m_Count; index++)
			m_Entries[index].StartWeight /= 1.0f - dropped;
	}

	Entry m_Entries[c_MaxPlaying + 1] = {};
	int m_Count = 0;
};

int main()
{
	Fader fader;
	fader.Start(0);
	fader.Start(1);
	fader.Update(0.4f);
	fader.Print("fade 1 at 0.4");
	fader.Start(2);
	fader.Update(0.5f);
	fader.Print("fade 2 at 0.5");
	fader.Start(3);
	fader.Update(0.5f);
	fader.Print("fade 3 at 0.5");
	fader.Start(4);
	fader.Update(0.25f);
	fader.Print("fade 4 at 0.25");
	fader.Update(1.0f);
	fader.Print("fade 4 done");
	return 0;
}
```

```text output-of="animation-blending-toy.cpp"
fade 1 at 0.4  S0=0.6000 S1=0.4000  sum=1.0000
fade 2 at 0.5  S0=0.3000 S1=0.2000 S2=0.5000  sum=1.0000
fade 3 at 0.5  S0=0.1500 S1=0.1000 S2=0.2500 S3=0.5000  sum=1.0000
fade 4 at 0.25 S0=0.1250 S2=0.2083 S3=0.4167 S4=0.2500  sum=1.0000
fade 4 done    S4=1.0000  sum=1.0000
```

1. **Lines 16–31:** `Start` saves each share, makes room when four entries play, and appends the target with weight 0.
2. **Lines 33–47:** `Update` turns a progress into weights, or leaves only the target at 1.
3. **Lines 62–77:** `DropFaintest` finds the smallest start weight and shares it over the others.
4. **Lines 83–101:** the main function starts four fades, each before the last ends.

Each line sums to 1. The third line shows four entries; the fourth shows that the fifth fade removed `S1`, the faintest, and shared its 0.1 over the others. The end of the last fade leaves `S4` alone.

:::example[Three fades that interrupt each other]
Take a controller with five states and a character that plays `S0`. At time zero a fade to `S1` starts with a duration of 1 second. At 0.4 seconds the fade is 40 % done, so `S0` has weight 0.6 and `S1` has 0.4.

Now a fade to `S2` starts. The two entries keep their shares as start weights: 0.6 and 0.4. Halfway through the new fade, the progress is 0.5. The old entries get their start weight times 0.5, which is 0.3 and 0.2, and the target `S2` gets 0.5. The sum is 1.

A third fade to `S3` starts at that moment, and the start weights are 0.3, 0.2 and 0.5. Halfway through it, the weights are 0.15, 0.1, 0.25 and 0.5. Four entries play, and the sum is 1.

A fourth fade to `S4` starts. The faintest start weight is 0.1, the weight of `S1`, so `S1` goes. The others divide by 1 minus 0.1, which is 0.9: they become 0.1667, 0.2778 and 0.5556. At progress 0.25, each gets 0.75 times its start weight, and `S4` gets 0.25: the weights are 0.125, 0.2083, 0.4167 and 0.25, and they sum to 1. The toy printed the same numbers.
:::

The table lists the same sequence, one row for each moment.

| Moment | S0 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- |
| Fade 1 at 0.4 | 0.6 | 0.4 | | | |
| Fade 2 at 0.5 | 0.3 | 0.2 | 0.5 | | |
| Fade 3 at 0.5 | 0.15 | 0.1 | 0.25 | 0.5 | |
| Fade 4 at 0.25 | 0.125 | dropped | 0.2083 | 0.4167 | 0.25 |

The toy differs from the engine in three ways. It takes the progress from the caller, while the engine computes it from a clock. It has no poses, so it cannot show what the weights are for. It omits the cases of a fade of zero seconds and a refused duration.

## The real code, in the order data flows

### Starting a fade

Every change of what plays goes through `StartState`: a command, a transition, a reset or the end of a fade. A state machine's transition calls it with the transition's duration. Search it for three jobs: saving the shares, making room, and adding the target.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L247-L288" symbol="AnimatorInstance::StartState"
void AnimatorInstance::StartState(uint32_t state, float fadeSeconds)
{
	// Every change of what plays (and of the clip played directly, which callers set before starting it) comes through
	// here, Reset or the end of a cross-fade.
	m_PlayRevision++;
	Playing entry;
	entry.State = state;
	if (fadeSeconds <= 0.0f || m_Count == 0)
	{
		m_Entries[0] = entry;
		m_Count = 1;
		m_FadeElapsed = 0.0f;
		m_FadeDuration = 0.0f;
		return;
	}
	// The entries playing now keep their current shares of what fades out.
	for (uint32_t index = 0; index < m_Count; index++)
		m_Entries[index].StartWeight = m_Entries[index].Weight;
	if (m_Count == c_MaxPlaying)
	{
		// The faintest entry makes room; the others share its weight.
		uint32_t faintest = 0;
		for (uint32_t index = 1; index < m_Count; index++)
		{
			if (m_Entries[index].StartWeight < m_Entries[faintest].StartWeight)
				faintest = index;
		}
		const float dropped = m_Entries[faintest].StartWeight;
		std::move(m_Entries.begin() + faintest + 1, m_Entries.begin() + m_Count, m_Entries.begin() + faintest);
		m_Count--;
		if (dropped < 1.0f)
		{
			for (uint32_t index = 0; index < m_Count; index++)
				m_Entries[index].StartWeight /= 1.0f - dropped;
		}
	}
	entry.StartWeight = 0.0f;
	entry.Weight = 0.0f;
	m_Entries[m_Count++] = entry;
	m_FadeElapsed = 0.0f;
	m_FadeDuration = fadeSeconds;
}
```

1. **Line 254:** a duration of zero, or nothing playing yet, makes a cut: one entry, no fade.
2. **Lines 263–264:** every entry keeps its present weight as the share it fades out from.
3. **Lines 265–281:** with four entries, the faintest goes and the others divide by 1 minus its weight.
4. **Lines 283–285:** the target joins at the end with weight 0.

### The weights while a fade runs

`Advance` adds the time of each update, times the animator's speed without its sign, to the fade's clock and then calls `UpdateWeights`. The function turns the clock into a progress between 0 and 1 and writes the weights.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L587-L609" symbol="AnimatorInstance::UpdateWeights"
void AnimatorInstance::UpdateWeights()
{
	if (m_Count == 0)
		return;
	const float progress = m_FadeDuration > 0.0f ? std::clamp(m_FadeElapsed / m_FadeDuration, 0.0f, 1.0f) : 1.0f;
	if (progress >= 1.0f)
	{
		// The fade is over: only the target plays. (Without a fade this runs every update: what plays changes only when
		// entries go.)
		if (m_Count != 1)
			m_PlayRevision++;
		m_Entries[0] = m_Entries[m_Count - 1];
		m_Entries[0].Weight = 1.0f;
		m_Entries[0].StartWeight = 1.0f;
		m_Count = 1;
		m_FadeDuration = 0.0f;
		m_FadeElapsed = 0.0f;
		return;
	}
	for (uint32_t index = 0; index + 1 < m_Count; index++)
		m_Entries[index].Weight = (1.0f - progress) * m_Entries[index].StartWeight;
	m_Entries[m_Count - 1].Weight = progress;
}
```

1. **Line 591:** the clock over the duration, clamped to the range 0 to 1, is the progress.
2. **Lines 592–604:** at progress 1 the last entry, the target, becomes the only one, with weight 1.
3. **Lines 606–608:** the others get their start weight times the share that is left, and the target gets the progress.

The growth is linear in time. A fade of 0.5 seconds has its target at weight 0.2 after 0.1 seconds, and at 0.8 after 0.4 seconds. The weights always sum to 1. The entries that fade out start from weights that sum to 1 and lose a fraction $p$ of them, while the target gains exactly $p$.

$$\sum_{i<n-1} (1-p)\,s_i + p = (1-p) + p = 1$$

Here $s_i$ is the saved start weight of entry $i$, $p$ is the progress of the fade between 0 and 1, and $n$ is the number of entries. At $p=0$ the old entries keep their shares. At $p=1$ only the target is left, and the code handles that case first.

### Blending poses

`Evaluate` turns the entries into a pose. With one entry, it copies the skeleton's :term[rest pose]{id=rest-pose} and samples the clip over it, so joints the clip does not animate keep their rest values. With several entries, it sums the samples of every entry, each weighted.

The sum works on three parts of a joint. Translations and scales are added linearly: with weights that sum to 1, the result is an average. Rotations are :term[quaternions]{id=quaternion}, and these need care.

A rotation can be written as a quaternion $q$, and $q$ and $-q$ are the same rotation. A weighted sum of quaternions is only meaningful when all of them lie in the same **hemisphere**: the half of the set of unit quaternions on one side of a chosen one.

Strata chooses the first entry's side. For each further entry it takes the :term[dot product]{id=dot-product} of the running sum and the new rotation; when that is negative, the entry is added with its sign flipped. The sum has no unit length, so the code :term[normalizes]{id=normalization} it at the end. The full mathematics of quaternions is in [rotations](../basics/math-rotations.md).

A worked example shows why the test matters. Take a rotation of 0 degrees about the vertical axis and one of 90 degrees, with weights 0.5 and 0.5. Write each quaternion as the pair (w, z): they are (1, 0) and (0.7071, 0.7071). The sum is (0.8536, 0.3536), whose length is 0.9239. After normalizing, it is (0.9239, 0.3827), which is 45 degrees, halfway.

Now suppose the clip stores the same 90 degrees as $-q$, which is (-0.7071, -0.7071). Without the test, the sum is (0.1464, -0.3536), which normalizes to (0.3827, -0.9239). The joint then turns -135 degrees, the long way round. The sketch repeats this arithmetic and prints the angle of the blend for three cases.

```cpp sketch="animation-blending-hemisphere.cpp"
// Blends two rotations with weights 0.5 and 0.5, with and without the hemisphere test.
#include <cmath>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/quaternion.hpp>

float BlendAngle(const glm::quat& a, const glm::quat& b, bool useHemisphere)
{
	const float weight = 0.5f;
	// b and -b are one rotation: flip b when it points away from a.
	const float sign = (useHemisphere && glm::dot(a, b) < 0.0f) ? -1.0f : 1.0f;
	glm::quat sum(a.w * weight + b.w * weight * sign, a.x * weight + b.x * weight * sign,
		a.y * weight + b.y * weight * sign, a.z * weight + b.z * weight * sign);
	sum = glm::normalize(sum);
	return glm::degrees(2.0f * std::atan2(sum.z, sum.w));
}

int main()
{
	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
	const glm::quat a = glm::angleAxis(glm::radians(0.0f), axis);
	const glm::quat b = glm::angleAxis(glm::radians(90.0f), axis);
	const glm::quat minusB(-b.w, -b.x, -b.y, -b.z);
	std::printf("b,  with the test:    %.1f degrees\n", BlendAngle(a, b, true));
	std::printf("-b, with the test:    %.1f degrees\n", BlendAngle(a, minusB, true));
	std::printf("-b, without the test: %.1f degrees\n", BlendAngle(a, minusB, false));
	return 0;
}
```

```text output-of="animation-blending-hemisphere.cpp"
b,  with the test:    45.0 degrees
-b, with the test:    45.0 degrees
-b, without the test: -135.0 degrees
```

1. **Line 11:** the sign is -1 when the entry points away from the first one, unless the test is off.
2. **Lines 12–15:** the weighted sum, normalized, and read back as an angle.
3. **Line 23:** `minusB` is the same rotation as `b`, stored with the other sign.

The test costs one dot product and a sign for each joint and entry. The engine gives each sample the rest pose first, so a joint that a clip does not animate adds the rest rotation, the same for every clip, and never disagrees.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L784-L824" from="if (m_Count == 1)" to="skeleton.ComputeModelTransforms(blended, outModel);" symbol="AnimatorInstance::Evaluate"
if (m_Count == 1)
{
	std::copy(rest.begin(), rest.end(), blended.begin());
	const AnimatorClip clip = GetClip(assets, m_Entries[0].State);
	if (clip.Clip && clip.Binding)
		clip.Clip->Sample(*clip.Binding, m_Entries[0].Time, blended);
}
else
{
	// Weighted sums: translations and scales linearly, rotations by normalized weighted sum on the first entry's
	// hemisphere (each sample's rest pose fills the joints its clip does not animate).
	for (uint32_t joint = 0; joint < joints; joint++)
	{
		blended[joint].Translation = glm::vec3(0.0f);
		blended[joint].Scale = glm::vec3(0.0f);
		blended[joint].Rotation = glm::quat(0.0f, 0.0f, 0.0f, 0.0f);
	}
	for (uint32_t index = 0; index < m_Count; index++)
	{
		const Playing& entry = m_Entries[index];
		std::copy(rest.begin(), rest.end(), sample.begin());
		const AnimatorClip clip = GetClip(assets, entry.State);
		if (clip.Clip && clip.Binding)
			clip.Clip->Sample(*clip.Binding, entry.Time, sample);
		const float weight = entry.Weight;
		for (uint32_t joint = 0; joint < joints; joint++)
		{
			JointPose& target = blended[joint];
			const JointPose& source = sample[joint];
			target.Translation += source.Translation * weight;
			target.Scale += source.Scale * weight;
			const glm::quat& reference = index == 0 ? source.Rotation : target.Rotation;
			const float sign = glm::dot(reference, source.Rotation) < 0.0f ? -1.0f : 1.0f;
			target.Rotation = glm::quat(target.Rotation.w + source.Rotation.w * weight * sign, target.Rotation.x + source.Rotation.x * weight * sign,
				target.Rotation.y + source.Rotation.y * weight * sign, target.Rotation.z + source.Rotation.z * weight * sign);
		}
	}
	for (uint32_t joint = 0; joint < joints; joint++)
		blended[joint].Rotation = AnimationMath::Normalize(blended[joint].Rotation);
}
skeleton.ComputeModelTransforms(blended, outModel);
```

1. **Lines 784–790:** one entry: the rest pose, with the clip's sample written over it.
2. **Lines 795–800:** several entries: the sums start at zero.
3. **Lines 801–820:** each entry is sampled over the rest pose and added joint by joint, with its weight.
4. **Lines 815–816:** the sign test of the hemisphere, against the running sum.
5. **Line 824:** :term[forward kinematics]{id=forward-kinematics} turns the blended local pose into model transforms.

After the sum, `ComputeModelTransforms` runs :term[forward kinematics]{id=forward-kinematics} once on the blended pose: each joint's model transform is its parent's times its own. The engine blends the local pose of each joint and only then places the joints in the model, which keeps every bone at its length. A blend of finished model matrices would average matrices that are not rotations. The average of the identity and a 90 degree turn has columns of length 0.71, so a bone would shrink to 71 % at the halfway point, and in general would shear. The rest of `Evaluate`, the root hold, belongs to the [root motion](root-motion.md) page.

The toy has no poses, so these loops have no counterpart there. With one entry, the pose costs one sample and no sum, which is the case whenever no fade runs.

### Phases that do not match

A fade mixes poses at the same moment in time, and the target always starts at its first frame. The source is wherever its loop happens to be. Suppose a walk cycle puts the left foot down at the start and a run cycle puts it down later. The mixed pose then has a foot between the two, and it moves across the ground instead of staying planted. The plan in `Docs/Roadmap.md` says that the walk and the run of the robot differ by 27 % of a cycle when they cross-fade.

To feel the size of it, assume a cycle of 1 second. The foot contacts then lie 0.27 seconds apart, which is 16 frames at 60 frames per second. A fade of 0.25 seconds lasts 15 frames, so the feet cannot agree during it.

Strata has no sync markers and no phase matching, so the feet slide during such a fade. A fix is to start the target at the normalized time of the source, which is an exercise below. The page on [time and events](time-events.md) explains normalized time.

::compare{id=halfway before=walk after=halfway}

:::note[Capture a fade at fixed steps]
A fade is hard to inspect in a running game, because it lasts a fraction of a second. Pause the game and step it with `play.step`, one fixed step at a time, as the [stepping](../editor/stepping.md) page describes. Each step moves the fade by the same amount, so a capture at a given step always shows the same weights.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| :term[Slerp]{id=slerp} pair by pair | Blenders that mix two clips at a time | Even angular speed in a blend | An order that matters with three entries or more, and one slerp for each entry beyond the first |
| Inertialization | Engines that follow the Gears of War talk in the further reading | One clip sampled during a change, no limit of four | A need for velocities, and a pose that cannot show two motions at once |
| Sync markers | Engines whose walk and run clips carry matching marks | Feet that stay planted when a walk becomes a run | Marked clips and a node that matches the phases |
| Blend spaces | Engines that drive movement by speed and direction | Every speed and direction from a few clips | A new kind of asset, an editor for it and a place in the controller |

## How it is tested

The suite `Animation.StateMachine` holds both tests of this page, in `StrataTests/src/Animation/AnimatorTests.cpp`. The first, "Cross-fade weights add up to 1, also when fades interrupt each other", plays seven fades in a row, each started before the last one ends. After each update it checks that no more than four entries play, that the weights sum to 1 within 1e-6, and that each weight lies between 0 and 1. At the end it checks that only the target plays with weight 1, and that the three bad commands are refused.

The second, "A cross-fade blends the poses by the weights", fades an arm from 0 to 90 degrees. After half of the fade the target has weight 0.5, and the elbow turns 45 degrees. The test also checks the position of the wrist, which rides on the elbow, to prove that the blend happens on local poses before forward kinematics.

Run them with the test program's filter for the suite, for example `StrataTests.exe --test-suite=Animation.StateMachine`.

## Changing it safely

- **Keep the sum at 1.** Any change that adds a way to remove or add an entry must keep the weights a partition of 1. The first test covers it.
- **Keep the target last.** `UpdateWeights` gives the weight of progress to the last entry and the end of a fade keeps it. A change of the order breaks both.
- **Blend before forward kinematics.** A new blend feature works on the local pose of each joint, never on model matrices.
- **Keep the sign test.** Any new way to sum rotations must handle `q` and `-q`.
- **Count entries in one place.** `c_MaxPlaying` also sizes the root travel array in `Advance`; raising it means checking both.

## Summary

- The weights of a fade follow a linear schedule for the target and a proportional share for the others, and they always sum to 1.
- `Evaluate` mixes entries joint by joint and then runs forward kinematics once.
- Rotations are summed on one hemisphere, because $q$ and $-q$ are the same rotation, and then normalized.
- A cross-fade starts the target at its first frame, so a walk and a run 27 % of a cycle apart slide the feet.

## Check yourself

1. A fade to `S1` of 2 seconds has run 0.5 seconds. `S0` played alone before it. A fade to `S2` starts now, and 0.5 seconds later (the new fade lasts 1 second) the animator updates. What are the weights of `S0`, `S1` and `S2`?

   :::answer{tests="compute-weights"}
   When the second fade starts, the first has run 0.5 of 2 seconds, so its progress is 0.25: `S0` has 0.75 and `S1` has 0.25. Those are the start weights. After 0.5 of 1 second, the progress is 0.5, so `S0` has 0.375, `S1` has 0.125 and `S2` has 0.5. The sum is 1.
   :::

2. Four entries play, with start weights 0.4, 0.3, 0.2 and 0.1, and a new fade starts. Which entry goes, and what are the new start weights of the others?

   :::answer{tests="compute-weights"}
   The entry with 0.1 goes. The others divide by 0.9: 0.4444, 0.3333 and 0.2222. They sum to 1, and the target joins with weight 0.
   :::

3. Why does `Evaluate` add the rotation of an entry with its sign flipped when the dot product with the running sum is negative? (a) To make the sum shorter. (b) Because $q$ and $-q$ are one rotation, and a sum of opposite signs cancels. (c) Because the engine needs positive weights.

   :::answer{tests="hemisphere"}
   Option (b). Option (a) is wrong: the code normalizes afterwards, so the length does not matter. Option (c) is wrong: the weights are never negative. The sign choice keeps both entries on one side, so the sum lies between them and not around the other way.
   :::

4. A programmer blends the final model matrices of the entries with the same weights, to save the work of the sum on rotations. What goes wrong at a weight of 0.5 between the identity and a 90 degree turn?

   :::answer{tests="pose-blend"}
   The mixed matrix is not a rotation. Its columns have length 0.71, so bones shrink to 71 %; with other angles or scales it also shears. Blending local rotations, normalizing, and only then running forward kinematics keeps each bone at its length.
   :::

5. A character fades from a walk to a run over 0.25 seconds, and the feet slide. Name the cause and one fix Strata lacks.

   :::answer{tests="phase-mismatch"}
   The target starts at its first frame while the source is at another point of its cycle, so the foot contacts are out of phase (27 % for the robot). Sync markers, or starting the target at the source's normalized time, would line them up.
   :::

## Exercises

1. **Basic.** Trace it yourself. Starting from the command `AnimationSystem::CrossFade`, find which line of `StartState` drops the faintest entry and which line of `UpdateWeights` keeps the sum at 1.

   :::answer[Worked solution]{tests="compute-weights,pose-blend"}
   Search for `CrossFade` in `Strata/src/Strata/Animation/`. `AnimationSystem::CrossFade` in `AnimationSystem.cpp` finds the animator's record and calls `AnimatorInstance::CrossFade`, which checks the duration, finds the state and calls `StartState` with the duration capped at 60 seconds. In `StartState`, the line `std::move(m_Entries.begin() + faintest + 1, m_Entries.begin() + m_Count, m_Entries.begin() + faintest);` removes the faintest entry. In `UpdateWeights`, the line that gives the target `progress` and the lines that scale the others by `1.0f - progress` keep the sum at 1.
   :::

2. **Medium.** For rotations about one axis at 0, 60 and 120 degrees with weights 0.5, 0.25 and 0.25, compute the angle of the weighted sum by hand, then compare it with slerp pair by pair. Which is right?

   :::answer[Worked solution]{tests="pose-blend,hemisphere" solution="sketches/animation-blending-slerp.cpp"}
   The sum is (0.5 + 0.2165 + 0.125, 0 + 0.125 + 0.2165) = (0.8415, 0.3415) as (w, z), which is 44.18 degrees. Slerp pair by pair gives 20 degrees after the first pair and 45 after the second. The program below does both.

   ```cpp sketch="animation-blending-slerp.cpp"
   // Three rotations about one axis, blended by a weighted sum and by slerp pair by pair.
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/quaternion.hpp>

   float AngleOf(const glm::quat& q)
   {
   	return glm::degrees(2.0f * std::atan2(q.z, q.w));
   }

   int main()
   {
   	const glm::vec3 axis(0.0f, 0.0f, 1.0f);
   	const glm::quat rotations[3] = { glm::angleAxis(glm::radians(0.0f), axis), glm::angleAxis(glm::radians(60.0f), axis),
   		glm::angleAxis(glm::radians(120.0f), axis) };
   	const float weights[3] = { 0.5f, 0.25f, 0.25f };

   	// The engine's way: sum the weighted quaternions, then normalize.
   	glm::quat sum(0.0f, 0.0f, 0.0f, 0.0f);
   	for (int index = 0; index < 3; index++)
   	{
   		sum.w += rotations[index].w * weights[index];
   		sum.x += rotations[index].x * weights[index];
   		sum.y += rotations[index].y * weights[index];
   		sum.z += rotations[index].z * weights[index];
   	}
   	sum = glm::normalize(sum);

   	// Pair by pair: fold in each rotation with the share it adds to the weight so far.
   	glm::quat folded = rotations[0];
   	float total = weights[0];
   	for (int index = 1; index < 3; index++)
   	{
   		total += weights[index];
   		folded = glm::slerp(folded, rotations[index], weights[index] / total);
   	}

   	std::printf("weighted sum:  %.2f degrees\n", AngleOf(sum));
   	std::printf("slerp by pair: %.2f degrees\n", AngleOf(folded));
   	return 0;
   }
   ```

   ```text output-of="animation-blending-slerp.cpp"
   weighted sum:  44.18 degrees
   slerp by pair: 45.00 degrees
   ```

   1. **Lines 20–28:** the engine's way: sum the weighted quaternions, then normalize.
   2. **Lines 31–37:** slerp pair by pair, each rotation folded in with its share of the weight so far.

   Neither is wrong, and the gap is small. The weighted sum does not depend on the order of the entries. Slerp pair by pair gives the weighted mean of the angles, 45 degrees, for rotations about one axis. With several axes, the order of the pairs changes the answer.
   :::

3. **Hard.** Start the target of a fade at the normalized time of the source inside `StartState`, and measure the sliding of the robot's feet for the walk to run fade, before and after.

   :::answer[Worked solution]{tests="phase-mismatch"}
   `StartState` has no clips, so pass the phase in from `Advance` or `CrossFade`, which know the assets. Set the target's `Time` to the phase times the target's duration, and its `Loops` and `Normalized` to match. To measure, run the game paused, step with `play.step`, and record the world position of a foot joint at each fixed step of the fade. The sliding is the distance the foot joint moves in the world while the foot should stand still. Expect it to fall, but not to vanish: the two clips also differ in stride length, and this change aligns the cycles only.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: `StartState`, `UpdateWeights`, `Evaluate` and `CrossFade`.
- `Strata/src/Strata/Animation/AnimatorInstance.h`: `c_MaxPlaying` and the `Playing` entry.
- `Strata/src/Strata/Animation/AnimationSystem.cpp`: `AnimationSystem::CrossFade`.
- `Strata/src/Strata/Animation/AnimationTypes.h`: `AnimationMath::Normalize`.
- `StrataTests/src/Animation/AnimatorTests.cpp`: the two cross-fade tests.

## Further reading

- David Bollo, "Inertialization: High Performance Animation Transitions in Gears of War" (conference talk, 2018; advanced): the source of inertialization.
- Jason Gregory, "Game Engine Architecture", the chapter on animation (book; intermediate): blend trees, cross-fades and sync.
- Ken Shoemake, "Animating rotation with quaternion curves" (paper; advanced): slerp and the two-to-one cover of rotations.
