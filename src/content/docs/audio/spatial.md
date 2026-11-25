---
id: audio/spatial
title: "Sound in space"
description: "How a sound gets its direction and its loudness from where its source is, and how its pitch follows motion."
kind: internals
size: M
tracks: [E]
needs: [audio/clips-voices-sources, basics/math-vectors]
time: 50
learn:
  - id: spatial-gain
    text: compute the gain of a source at a distance under each attenuation model
  - id: spatial-pan
    text: predict which ear a source reaches louder from the listener's frame
  - id: spatial-doppler
    text: explain how the Doppler effect shifts pitch and why Strata limits velocities
  - id: spatial-velocity
    text: trace where a source gets its velocity and why a velocity per frame jitters
since: 0.3.0
status: final
---

A game sound in a world has to seem to come from a place. Strata does this in three steps: the loudness falls with the distance to the listener, the two ears hear it unevenly according to its direction, and its pitch moves with the speed of the source. The vendored miniaudio library does the mixing. Strata decides what to give it: the listener's pose, a position and a velocity for each source, and a curve for each voice. This page does not cover the code that visits every source each frame, or the choice of the listener among several: that is the Audio scene system.

## The problem and how engines solve it

Think of two bodies that hit each other in the Physics Playground sample. Its `Impact` script plays a clip with `Audio::PlayOneShotAt` at the contact point. A recording is a list of numbers that says nothing about where the impact happened. Played unchanged, it sounds in the middle of the head, at the same loudness whether the bodies are near or far.

Making a sound seem to come from a place is **spatialization**. Engines split it into parts, and each part copies one cue of real hearing. The first cue is direction.

**Panning** sends more of a sound to the ear on the side of its source, using only the angle between the source and where the listener faces. Two speakers or two ears can do no more than this.

An **HRTF**, a head-related :term[transfer function]{id=transfer-function}, is a filter that changes a sound as the shape of a head and ears would. With it, two channels alone can place a sound in front, behind or above. It needs measured filters and costs more per voice. Strata does not use one: it pans. A surround setup instead gives each speaker a share by its direction.

The second cue is distance. **Attenuation** is the fall of a sound's gain as its source moves away from the listener. Physics says the intensity of a point source drops with the square of the distance, so the pressure, and so the gain, drops as 1/r. Games bend this.

A pure 1/r curve never reaches zero, so a sound far from the listener would still cost mixing time. Near the source it grows without bound. Each engine therefore offers a few curves and two limits.

The third cue is motion: a siren is higher in pitch while it comes toward you and lower after it passes. Engines get this by changing the rate at which each voice plays, from the velocity of the source and of the listener. The velocity has to come from somewhere, and that is the hard part, as the second half of this page shows.

## The map

Everything here runs on the :term[main thread]{id=main-thread}, except the mixing itself. `AudioSystem` reads the entities each frame and gives `AudioSource` objects a position and a velocity. A source forwards them, with its attenuation settings, to its `AudioVoice`, which wraps one miniaudio sound. The mixing thread of miniaudio computes the gains and the pitch from those values.

```mermaid caption="The audio system reads entities on the main thread and gives positions and velocities to sources. Each source passes them to its voice, and the mixing thread turns them into gain, pan and pitch." alt="Boxes joined by arrows. Entities lead to the audio system, which leads to a source, then a voice. The voice and the listener pose both lead to a box named mixing thread, which produces gain, pan and pitch."
flowchart LR
  E[Entity transforms and bodies] --> S[AudioSystem, main thread]
  S -->|position, velocity| A[AudioSource]
  A -->|settings| V[AudioVoice]
  V --> M[miniaudio mixing thread]
  L[Listener pose] --> M
  M --> O[Gain, pan, pitch]
```

The **listener** is the point in the world where the player hears from: it has a position, a forward direction, an up direction and a velocity. The listener's right direction is not stored; it is the :term[cross product]{id=cross-product} of forward and up. Strata uses the engine's frame: :term[right-handed]{id=handedness}, +Y up, and -Z forward, so a listener without rotation looks down -Z and has +X on its right. These are also miniaudio's defaults, and the figure shows the frame from above.

::figure{id=listener-frame}

## The contract

Callers of `AudioEngine::SetListener` may assume the following, each with its reason.

- The listener's four vectors must be finite, and forward and up must not be zero. Strata logs a warning and ignores the whole call otherwise. The reason: miniaudio :term[normalizes]{id=normalization} forward and up, and one zero or :term[NaN]{id=nan} (not a number) vector would turn every sample of the mix into NaNs.
- A source at the same place as the listener gives no pan and no Doppler shift, because there is no direction to use.
- A voice that is not spatial has no position: music and interface sounds play as they are.
- Doppler speeds stay limited, and a jump counts as a teleport (both are explained below). The reason: a single wild velocity would turn the pitch of a voice into noise.

A caller picks an attenuation model and three numbers. An **attenuation model** is the curve that turns a distance into a gain.

The **min distance** is the distance up to which the sound plays at full gain.

The **max distance** is the distance beyond which the sound gets no quieter.

**Rolloff** is the steepness of the curve: how fast the gain falls between the two distances. miniaudio clamps the distance to the range from min to max before it evaluates the curve; these are the "clamped" models of `OpenAL`.

Write $m$ for the min distance, $M$ for the max distance, $r$ for the rolloff and $d$ for the clamped distance, all in world units.

| Model | Gain at distance $d$ |
| --- | --- |
| `NoAttenuation` | 1 |
| `Inverse` | $m / (m + r (d - m))$ |
| `Linear` | $1 - r (d - m) / (M - m)$ |
| `Exponential` | $(d / m)^{-r}$ |

:::example
Take $m = 1$, $M = 50$ and $r = 1$. For `Inverse`, a source at distance 5 has gain 1 / (1 + 4) = 0.2. At 20 the gain is 1 / 20 = 0.05. At 100 the distance is clamped to 50, so the gain is 0.02. Each doubling of the distance halves the gain, which is minus 6 :term[decibels]{id=decibel}.

`Exponential` with $r = 1$ gives the same numbers, as $(5/1)^{-1} = 0.2$. `Linear` gives 1 - 4 / 49 = 0.918 at 5, 1 - 19 / 49 = 0.612 at 20, and 0 at 50. With $r = 2$, `Inverse` at 5 gives 1 / (1 + 8) = 0.111. `Linear` at 30 would reach 1 - 58 / 49 = -0.18, which miniaudio raises to its lowest gain, 0.
:::

::figure{id=gain-curves}

Two settings of a source break the formulas, so Strata guards them. When the max distance is below the min distance, the clamp has no range, and the source behaves as if both were the min distance. A min distance near 0 would break the inverse curve, so Strata keeps it at 0.01 or above. The frame of the listener decides the pan: a listener whose forward is +Z has +X on its left, and an upside-down listener swaps sides as well.

## A toy version

:::question
New to C++ code? Read [functions and structs](../basics/programming-2.md) and [calls and includes](../basics/programming-3.md) first.
:::

The toy below places a listener and computes the distance to a source. It gives each ear a gain: the inverse gain times a pan share from one :term[dot product]{id=dot-product}, that of the direction to the source with the listener's right axis.

```cpp sketch="audio-spatial-toy.cpp"
#include <algorithm>
#include <cstdio>

#include <glm/glm.hpp>

struct Listener
{
	glm::vec3 Position;
	glm::vec3 Forward;
	glm::vec3 Up;
};

// The inverse model: the distance is clamped first, so the gain is 1 inside the minimum distance.
static float InverseGain(float distance, float minDistance, float maxDistance, float rolloff)
{
	const float clamped = std::clamp(distance, minDistance, maxDistance);
	return minDistance / (minDistance + rolloff * (clamped - minDistance));
}

static void Report(const char* name, const Listener& listener, const glm::vec3& source)
{
	const glm::vec3 right = glm::cross(listener.Forward, listener.Up);
	const glm::vec3 toSource = source - listener.Position;
	const float distance = glm::length(toSource);
	// One dot product: +1 when the source is exactly to the right, -1 exactly to the left, 0 ahead or behind.
	const float side = glm::dot(toSource / distance, right);
	const float gain = InverseGain(distance, 1.0f, 50.0f, 1.0f);
	// Each ear gets (1 + side) / 2 of the gain, but never less than 0.2.
	const float leftEar = gain * std::max((1.0f - side) * 0.5f, 0.2f);
	const float rightEar = gain * std::max((1.0f + side) * 0.5f, 0.2f);
	std::printf("%-12s distance %6.2f  gain %.3f  left %.3f  right %.3f\n", name, distance, gain, leftEar, rightEar);
}

int main()
{
	const Listener facingMinusZ = { glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, -1.0f), glm::vec3(0.0f, 1.0f, 0.0f) };
	const Listener facingPlusZ = { glm::vec3(0.0f), glm::vec3(0.0f, 0.0f, 1.0f), glm::vec3(0.0f, 1.0f, 0.0f) };

	Report("right", facingMinusZ, glm::vec3(5.0f, 0.0f, 0.0f));
	Report("ahead", facingMinusZ, glm::vec3(0.0f, 0.0f, -5.0f));
	Report("behind", facingMinusZ, glm::vec3(0.0f, 0.0f, 5.0f));
	Report("front right", facingMinusZ, glm::vec3(3.0f, 0.0f, -4.0f));
	Report("far right", facingMinusZ, glm::vec3(100.0f, 0.0f, 0.0f));
	Report("turned round", facingPlusZ, glm::vec3(5.0f, 0.0f, 0.0f));
	return 0;
}
```

```text output-of="audio-spatial-toy.cpp"
right        distance   5.00  gain 0.200  left 0.040  right 0.200
ahead        distance   5.00  gain 0.200  left 0.100  right 0.100
behind       distance   5.00  gain 0.200  left 0.100  right 0.100
front right  distance   5.00  gain 0.200  left 0.040  right 0.160
far right    distance 100.00  gain 0.020  left 0.004  right 0.020
turned round distance   5.00  gain 0.200  left 0.200  right 0.040
```

1. **Line 16:** the clamp makes the gain 1 inside the min distance and constant beyond the max distance.
2. **Line 26:** one dot product of the unit direction with the right axis gives the side, from -1 to 1.
3. **Lines 29–30:** each ear takes half of one plus or minus the side, and never less than 0.2.
4. **Line 37:** the second listener faces +Z, so its right axis points to -X.

The source straight to the right gets 0.2 in the right ear and the floor 0.04 in the left. A source ahead or behind gets equal gains, so this model cannot tell front from back; a head-related transfer function (HRTF) can. The last line shows the turn: the same source, a listener facing +Z, and the ears swap.

## The real code: attenuation

Strata's `AudioVoice::SetAttenuation` maps its own settings onto miniaudio's. Search for the two places where Strata does not pass a value through.

```cpp src="Strata/src/Strata/Audio/AudioVoice.cpp#L338-L361" symbol="AudioVoice::SetAttenuation"
void AudioVoice::SetAttenuation(AudioAttenuationModel model, float minDistance, float maxDistance, float rolloff)
{
	ma_attenuation_model attenuationModel = ma_attenuation_model_inverse;
	float effectiveRolloff = std::max(rolloff, 0.0f);
	switch (model)
	{
		case AudioAttenuationModel::NoAttenuation:
			// miniaudio's own "none" model also disables panning and the Doppler effect. Inverse attenuation with
			// zero rolloff keeps the gain at 1 at every distance while the voice stays fully spatialized.
			attenuationModel = ma_attenuation_model_inverse;
			effectiveRolloff = 0.0f;
			break;
		case AudioAttenuationModel::Inverse: attenuationModel = ma_attenuation_model_inverse; break;
		case AudioAttenuationModel::Linear: attenuationModel = ma_attenuation_model_linear; break;
		case AudioAttenuationModel::Exponential: attenuationModel = ma_attenuation_model_exponential; break;
	}

	const float effectiveMinDistance = std::max(minDistance, c_MinAttenuationDistance);
	ma_sound& sound = m_Data->Sound;
	ma_sound_set_attenuation_model(&sound, attenuationModel);
	ma_sound_set_min_distance(&sound, effectiveMinDistance);
	ma_sound_set_max_distance(&sound, std::max(maxDistance, effectiveMinDistance));
	ma_sound_set_rolloff(&sound, effectiveRolloff);
}
```

1. **Lines 344–348:** `NoAttenuation` becomes inverse with rolloff 0, so the gain stays 1 and the voice stays spatial.
2. **Line 355:** the min distance never falls below 0.01.
3. **Line 359:** a max distance below the min distance becomes the min distance.

The difference from the toy is that miniaudio, not Strata, evaluates the curves, so the code only chooses and guards the parameters. Strata avoids miniaudio's own "none" model, because that one also disables panning and the Doppler shift. The name is `NoAttenuation` and not `None`, because X11 defines `None` as a :term[macro]{id=macro}.

## The Doppler effect from zero

Sound travels at a fixed speed through the air, about 343 metres per second. When the source moves toward you, each wave crest starts a little closer to you than the last one did, so the crests arrive closer together. A shorter gap between crests is a higher pitch. The **Doppler effect** is this shift of pitch, caused by the speed of the source and the listener along the line between them.

miniaudio uses the `OpenAL` formula, with the default speed of sound 343.3 and a Doppler factor of 1; Strata sets neither. The result is a ratio of the rate at which the voice plays:

$$ \text{ratio} = \frac{c - v_l}{c - v_s} $$

Here $c$ is the speed of sound, $v_s$ is the speed of the source toward the listener and $v_l$ the speed of the listener away from the source, all in units per second. The ratio is the factor that multiplies the pitch of the clip. For a still listener and a source that comes toward you at 20 units per second, the ratio is 343.3 / 323.3 = 1.062, a rise of about 6 %. Leaving at 20 gives 343.3 / 363.3 = 0.945.

Two limits show why Strata caps speeds. At 150 units per second the ratio is 343.3 / 193.3 = 1.78, already close to a doubling of the pitch. As the speed nears 343.3 the bottom of the fraction goes to zero, and the ratio grows without bound. The cap, `AudioSystem::c_MaxDopplerSpeed` of 150, keeps every velocity far below that.

Speeds are per second, never per frame. A source that moves 0.5 units in one frame at 144 :term[frames per second]{id=frame-rate} moves 72 units per second, and a frame in which it did not move has a speed of 0. The same speed measured per frame would flip between 0 and 72, and the pitch would flutter. Where a velocity comes from decides whether that happens.

## The real code: velocities

A velocity has two sources. A physics body knows its own. Strata asks for the velocity of the body that moves the entity, or of its nearest ancestor, at the entity's position (`IBodyMotionQuery::GetPointVelocity`). A point on a spinning body so gets the speed of that point. Strata limits the result to 150.

Every other entity has only its position, and Strata measures the move.

Physics moves bodies in fixed steps of 1/60 second, while the display may run at 144 frames per second, so a transform changes on some frames only. Strata therefore keeps the time since the last move, not since the last frame. Two helpers come first. A speed above the cap, or a move with no time passed, is a **teleport**: a jump that gives no velocity at all, because nothing physical moved at that speed.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L47-L65"
std::optional<glm::vec3> ComputeVelocity(const glm::vec3& previous, const glm::vec3& current, float elapsed)
{
	if (!(elapsed > 0.0f))
		return std::nullopt;
	const glm::vec3 velocity = (current - previous) / elapsed;
	if (!AudioUtils::IsFinite(velocity) || glm::dot(velocity, velocity) > AudioSystem::c_MaxDopplerSpeed * AudioSystem::c_MaxDopplerSpeed)
		return std::nullopt;
	return velocity;
}

// A simulated velocity, limited to AudioSystem::c_MaxDopplerSpeed: near the speed of sound the Doppler pitch shift
// grows without bound.
glm::vec3 LimitSpeed(const glm::vec3& velocity)
{
	if (!AudioUtils::IsFinite(velocity))
		return glm::vec3(0.0f);
	const float speed = glm::length(velocity);
	return speed > AudioSystem::c_MaxDopplerSpeed ? velocity * (AudioSystem::c_MaxDopplerSpeed / speed) : velocity;
}
```

1. **Lines 49–50:** a move without time passed gives no velocity.
2. **Lines 52–53:** a velocity above the cap, or not finite, is a teleport.
3. **Lines 59–64:** a simulated velocity keeps its direction and loses its excess speed.

The next quote is the function that decides which of the two velocities a source gets, and it is the heart of the page. Moves still arrive at uneven gaps of two or three frames, so the measured velocity is blended into the old one. At each move the old value covers $1 - e^{-t/0.1}$ of the way to the new one, with $t$ the time in seconds since the last move. The mathematics of such smoothing is in [Interpolation](../basics/math-interpolation.md).

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L664-L700" symbol="AudioSystem::UpdateMotion"
glm::vec3 AudioSystem::UpdateMotion(MotionTracker& motion, Entity entity, const glm::vec3& position, float timestep)
{
	glm::vec3 bodyVelocity;
	if (GetBodyVelocity(entity, position, bodyVelocity))
	{
		motion = MotionTracker { position, LimitSpeed(bodyVelocity), 0.0f, true };
		return motion.Velocity;
	}

	if (!motion.HasPosition || !(timestep > 0.0f))
	{
		// The first position, or a move while no time passes (e.g. edited while the scene is paused): a teleport.
		if (!motion.HasPosition || position != motion.Position)
			motion = MotionTracker { position, glm::vec3(0.0f), 0.0f, true };
		return motion.Velocity;
	}

	motion.TimeSinceMove += timestep;
	if (position != motion.Position)
	{
		// Over the time since the last move rather than the last frame: a transform that changes only on fixed steps
		// would otherwise alternate between standing still and moving fast. The moves are still seen one or two frames
		// apart, so the velocity is smoothed.
		if (const std::optional<glm::vec3> velocity = ComputeVelocity(motion.Position, position, motion.TimeSinceMove))
			motion.Velocity += (*velocity - motion.Velocity) * (1.0f - std::exp(-motion.TimeSinceMove / c_VelocitySmoothingTime));
		else
			motion.Velocity = glm::vec3(0.0f);
		motion.Position = position;
		motion.TimeSinceMove = 0.0f;
	}
	else
	{
		if (motion.TimeSinceMove > c_StopAfterFixedSteps * m_Scene.GetFixedTimestep())
			motion.Velocity = glm::vec3(0.0f);
	}
	return motion.Velocity;
}
```

1. **Lines 667–671:** a physics body returns at once with its limited velocity.
2. **Lines 673–679:** the first position, or a move with no time passed, is a teleport.
3. **Lines 687–690:** the blend of the new velocity into the old, and zero after a teleport.
4. **Lines 696–697:** two fixed steps without a move mean the entity has stopped.

:::example
A box moves 0.5 units every fixed step, which is 30 units per second, and frames come every 6.94 ms. A step lasts 16.67 ms, so a move appears every 2.4 frames: after 2 frames (13.9 ms) or after 3 (20.8 ms). Measured per frame, the velocity is 72 on a frame with a move and 0 on the others.

Over the time since the last move it is 0.5 / 0.0139 = 36, or 0.5 / 0.0208 = 24. Smoothing, with weights 0.13 and 0.19, pulls the values toward their mean of 30. When no move comes for two fixed steps (33 ms), the velocity is set to 0: the entity has stopped.
:::

The listener gets the same treatment through `UpdateMotion`, so a moving listener shifts pitch as well.

## Alternatives Strata did not choose

Strata has no occlusion, so a wall does not muffle a source, and no zones with an echo of their own, so a room adds no echo. A search of the audio code for either finds nothing. Engines that do this trace rays from the listener to the source and soften the high pitches by what the rays hit, or tag regions of the level with an echo setting. The component has no field for the attenuation model, so every component source uses `Inverse`; the last exercise adds one.

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| HRTF filters | Stereo modes of many engines | Direction in front, behind and above | Measured data, and mixing time per voice |
| Velocity from the last frame | Simple engines | Less code | Jitter when fixed steps and frames differ |
| Occlusion by ray casts | Large game engines | Walls that muffle | A physics query per source each frame |
| Doppler factor per source | `OpenAL` and others | Exaggerated or damped pitch effects | A new field and its tests |

## How it is tested

The `Audio.Spatial` suite measures the root mean square (RMS) level of a looping source on a mixing device that plays to no speaker. `Distance attenuation follows the attenuation model` checks each model against the formulas above. `Panning follows the right-handed listener frame` checks that +X is on the right, then on the left for a listener facing +Z or turned upside down.

In `Audio.System`, `Doppler velocities stay steady when frames and fixed steps differ` runs frames at 144 Hz against fixed steps at 60 Hz. It requires the velocity of a mover to stay within 5 % of its speed after the smoothing has settled. Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=Audio*`.

## Changing it safely

Add a setting by following the voice: a field in the settings, a call in `AudioVoice`, and a test in `Audio.Spatial` with the formula in a comment. Keep every guard: a call that receives NaN or a zero vector logs and returns, and never asserts, because the data comes from game code. Never add a velocity source that bypasses the speed limit. A new component field needs the feature test to exercise it. Run the `Audio*` suites and the feature test before a commit.

## Summary

- Strata computes the gain of a source with one of four attenuation models, clamped between min and max distance.
- The listener's frame, right-handed with +Y up and -Z forward, decides which ear a source is louder in.
- The Doppler ratio depends on velocities along the line between source and listener, and Strata caps them at 150 units per second.
- A velocity comes from the physics body, or from the move over the time since the last move, smoothed; a velocity per frame jitters.

## Check yourself

1. A source has min distance 2, max distance 40 and rolloff 1, with the `Inverse` model. What is its gain at distance 10?

   A) 0.2 B) 0.25 C) 0.79 D) 0.1

   :::answer{tests="spatial-gain"}
   The gain is 2 / (2 + 8) = 0.2, so A is right. B is wrong: 0.25 is the gain at distance 8. C is wrong: 0.79 is the gain of the `Linear` model, 1 - 8 / 38. D is wrong: 0.1 is the pure 1/r value, which ignores the min distance.
   :::

2. A listener faces +Z with +Y up. A source sits at +X. Which ear is louder?

   :::answer{tests="spatial-pan"}
   The right axis is forward times up, which points to -X, so the source at +X is on the left: the left ear is louder.
   :::

3. Why does Strata cap Doppler speeds, and what happens above the cap?

   :::answer{tests="spatial-doppler"}
   The pitch ratio grows without bound as the speed nears the speed of sound. Above 150 units per second a physics velocity is cut to 150, and a measured move counts as a teleport and gives no velocity.
   :::

4. Fixed steps run at 60 Hz and frames at 144 Hz. Why does the velocity of a moving box measured per frame jitter?

   :::answer{tests="spatial-velocity"}
   A new position appears on only two or three frames out of five. On the frames between, the measured speed is 0, and on the others it is 72 instead of the true 30.
   :::

## Exercises

1. **Basic.** A source on a rolling ball passes a still listener at 30 units per second. Compute the pitch ratio right before and right after it passes.

   :::answer[Worked solution]{tests="spatial-doppler"}
   Before, the source comes toward the listener: 343.3 / (343.3 - 30) = 1.096. After, it leaves: 343.3 / 373.3 = 0.920. The pitch falls by about 16 % as the ball passes.
   :::

2. **Medium.** Trace it yourself. Which function gives a source its velocity, and what does it return for a body, for a scripted mover and after a teleport?

   :::answer[Worked solution]{tests="spatial-velocity"}
   Put a breakpoint in `AudioSystem::UpdateMotion` in `Strata/src/Strata/Audio/AudioSystem.cpp`. A body gets `GetBodyVelocity` limited by `LimitSpeed`; a scripted mover gets the smoothed move over the time since the last move; a teleport or two still fixed steps give zero.
   :::

3. **Hard.** Run the simulation of the smoothed velocity and describe the first frames.

   :::answer[Worked solution]{tests="spatial-velocity"}
   The program moves a box 0.5 units on every fixed step and prints the per-frame velocity beside the smoothed one.

   ```cpp sketch="audio-spatial-velocity.cpp"
   #include <cmath>
   #include <cstdio>

   int main()
   {
   	const float stepTime = 1.0f / 60.0f;
   	const float frameTime = 1.0f / 144.0f;
   	const float smoothingTime = 0.1f;

   	float stepClock = 0.0f;
   	float position = 0.0f;      // Moves 0.5 units on every fixed step: 30 units per second.
   	float lastFramePosition = 0.0f;
   	float lastMovePosition = 0.0f;
   	float sinceMove = 0.0f;
   	float smoothed = 0.0f;

   	for (int frame = 1; frame <= 12; frame++)
   	{
   		stepClock += frameTime;
   		while (stepClock >= stepTime)
   		{
   			stepClock -= stepTime;
   			position += 0.5f;
   		}

   		const float naive = (position - lastFramePosition) / frameTime;
   		lastFramePosition = position;

   		sinceMove += frameTime;
   		if (position != lastMovePosition)
   		{
   			const float measured = (position - lastMovePosition) / sinceMove;
   			smoothed += (measured - smoothed) * (1.0f - std::exp(-sinceMove / smoothingTime));
   			lastMovePosition = position;
   			sinceMove = 0.0f;
   		}
   		std::printf("frame %2d  position %.1f  naive %5.1f  smoothed %5.1f\n", frame, position, naive, smoothed);
   	}
   	return 0;
   }
   ```

   ```text output-of="audio-spatial-velocity.cpp"
   frame  1  position 0.0  naive   0.0  smoothed   0.0
   frame  2  position 0.0  naive   0.0  smoothed   0.0
   frame  3  position 0.5  naive  72.0  smoothed   4.5
   frame  4  position 0.5  naive   0.0  smoothed   4.5
   frame  5  position 1.0  naive  72.0  smoothed   8.6
   frame  6  position 1.0  naive   0.0  smoothed   8.6
   frame  7  position 1.0  naive   0.0  smoothed   8.6
   frame  8  position 1.5  naive  72.0  smoothed  11.5
   frame  9  position 1.5  naive   0.0  smoothed  11.5
   frame 10  position 2.0  naive  72.0  smoothed  14.7
   frame 11  position 2.0  naive   0.0  smoothed  14.7
   frame 12  position 2.0  naive   0.0  smoothed  14.7
   ```

   1. **Lines 20–24:** a fixed step moves the box whenever enough :term[frame time]{id=frame-time} has gathered.
   2. **Line 26:** the per-frame velocity is 72 on a frame with a move and 0 on the others.
   3. **Lines 32–33:** the move over the time since the last move, blended into the old value.
   4. **Lines 34–35:** the clock of the last move starts again.

   The per-frame value jumps between 0 and 72 from the first moves on. The smoothed value is steady between moves and reaches 14.7 after 12 frames (83 ms); it needs several tenths of a second to approach 30, which is the price of smoothing.
   :::

4. **Hard.** Add an attenuation model field to `AudioSourceComponent`. Which places change?

   :::answer[Worked solution]{tests="spatial-gain"}
   Add the field with the default `Inverse` to `AudioSourceComponent`. Register it as a property so that the inspector and saved scenes carry it. Copy it in the audio system's apply step to the source with `SetAttenuationModel`. Then add a case to `AudioSystemTests`, and set a non-default value in the feature test so that it is exercised.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Audio/AudioSource.h`: the attenuation enum and the settings.
- `Strata/src/Strata/Audio/AudioVoice.cpp`: `AudioVoice::SetAttenuation`.
- `Strata/src/Strata/Audio/AudioEngine.cpp`: `AudioEngine::SetListener`.
- `Strata/src/Strata/Audio/AudioSystem.cpp`: velocities and the listener.
- `StrataTests/src/Audio/AudioTests.cpp` and `AudioSystemTests.cpp`: the suites above.

## Further reading

- The OpenAL 1.1 specification, chapter on distance models and Doppler (advanced): the formulas behind miniaudio.
- The miniaudio manual, spatialization section (intermediate): what each setting does.
