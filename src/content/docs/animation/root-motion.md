---
id: animation/root-motion
title: "Root motion"
description: "How an animator takes the root joint's travel and turn out of the pose and moves its entity with them, through a character controller when there is one."
kind: internals
size: M
tracks: [E]
needs: [animation/time-events, physics/character-controllers, animation/blending]
time: 65
learn:
  - id: travel-split
    text: compute the root travel of an update that crosses a loop boundary
  - id: blend-travel
    text: compute the move of a blend from each entry's travel and weight
  - id: hold-root
    text: explain why the pose holds the root's subtree back when root motion applies
  - id: where-travel-goes
    text: explain where the travel of a looping walk goes in one update
  - id: controller-branch
    text: trace which branch of the apply step runs for an entity with a character controller
since: 0.3.0
status: final
---

When an animator applies **root motion**, the clip decides how far and in which direction the character travels, and the entity follows. The animator takes the root joint's horizontal travel and its turn about the +Y axis out of the pose and hands them to the entity. A plain entity moves by that amount; an entity with a :term[character controller]{id=character-controller} asks the controller to walk it. This page follows one update of that move from the clip to the entity. It does not teach how the controller walks a move, how to switch root motion on in the editor, or when in the frame the system applies it.

## The problem and how engines solve it

Imagine a walk clip where the character's feet land two metres further along each second. You want the character in the game to cover the ground at the same pace. There are two classic ways to get there.

The first is **in-place animation**: the clip is authored with the character walking on the spot, and game code moves the entity at a speed you choose. This is simple, and the speed is yours to tune. The cost is sliding. When the code moves the entity at 3 m/s and the clip's feet step at 2 m/s, the feet skate over the ground. Blends make it worse, because a walk clip and a run clip each have their own pace, and the code must guess the pace in between.

The second way is root motion. The clip keeps its travel, and the engine reads it from the **root motion joint**, the joint of the skeleton whose movement stands for the movement of the whole body. Feet and ground then agree by construction, because the same data drives both. The cost is that the animation now controls gameplay: a change to a clip changes how far the character walks, and a mistake in the setup moves the character twice, or wrongly. Four mistakes are worth knowing before you read the code.

- **Double motion.** If the root moves in the pose and the entity moves by the same amount, the mesh runs ahead of its entity at twice the speed. The engine removes the travel from the pose, so the move happens once.
- **Drift at loop boundaries.** A walk loops every second or so. An update that ends soon after the loop restarts has two parts: the end of one pass and the start of the next. Measure the root only by where it is now, and the jump back to the start of the clip appears as a big step backwards, or the travel of the boundary is lost.
- **Vertical motion.** The root rises and falls a little with each step. If the entity followed that, it would fight gravity and the ground contact. Strata moves the entity in the ground plane only; the vertical part stays in the pose.
- **Scale.** A clip travels two metres for a character of normal size. A character that is scaled to twice the size has feet that travel four metres, so the move must be scaled with the entity, or the feet slide again.

Strata extracts the horizontal move and the :term[yaw]{id=yaw-angle}, and applies them in one function.

## The map

The animator instance does the measuring and the animation system does the moving. The pose evaluation holds the root back so that the two do not add up.

```mermaid caption="One update of an animator with root motion: the playhead moves, the travel is measured and weighted, the pose holds the root back, and one function moves the entity." alt="A diagram of boxes and arrows. Advance reads the root at the start and end of each playing clip and adds the travel. The weighted result is stored as a delta. Evaluate holds the root and its subtree where the clips started. The apply step turns the delta into a controller motion or a change of the transform."
flowchart LR
  A["AnimatorInstance::Advance: travel per entry"] --> B["Weighted RootMotionDelta"]
  B --> D["AnimationSystem::ApplyRootMotion"]
  A -.-> C["AnimatorInstance::Evaluate: HoldRoot"]
  D --> E["Entity transform"]
  D --> F["ICharacterControl::AddCharacterMotion"]
```

Everything on the left runs inside the animator, which knows nothing about scenes. Only the function on the right touches an entity.

## The contract

Callers can rely on these rules, and the code relies on callers to keep them.

- **The delta is in the animator's space.** `RootMotionDelta` holds a move in X and Z and a yaw in :term[radians]{id=radian}, measured in the frame the entity had when the update began. Y is always 0.
- **Root motion moves entities in one place.** Only `AnimationSystem::ApplyRootMotion` changes an entity because of root motion, and it signals the change.
- **The pose holds the root back.** While root motion applies, the root joint's :term[subtree]{id=subtree} stays where the clips started, so the mesh stays with its entity.
- **The move reaches a controller only on the animator's own entity.** A model under the entity that carries the controller walks away from its capsule.

:::rule[Root motion moves entities in one function]
The engine's guide says root motion moves entities only in `AnimationSystem::ApplyRootMotion`. The reason is the :term[transform contract]{id=transform-contract}: a second place that wrote the transform could forget to signal it, and the scene's cached :term[world transforms]{id=world-transform} would go stale. The system's frame is taught in [The animation system](../animation/system.md).
:::

## A toy version

:::question
The toy uses functions, :term[structs]{id=struct} and `std::printf`. If those are new, read [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) first.
:::

The toy has a clip whose root walks a circle of radius 2 m in a period of 2 s. An entity starts at x = 10 facing +X and follows that travel in steps of 0.7 s, so some steps cross the loop boundary. It uses the engine's three ideas: travel measured in the frame the root faced at the start of a stretch, a stretch split at the loop boundary, and the turn added after the move. If it is right, the entity stays 2 m from the centre of its own circle, whatever the step.

```cpp sketch="animation-root-motion-toy.cpp"
// A toy root motion: a clip's root walks a circle; the entity follows the root's travel, not its place.
#include <cmath>
#include <cstdio>
#include <numbers>

struct Vec
{
	float X = 0.0f;
	float Z = 0.0f;
};

struct RootSample
{
	Vec Position;
	float Yaw = 0.0f;
};

struct Entity
{
	Vec Position;
	float Yaw = 0.0f;
};

constexpr float c_Pi = std::numbers::pi_v<float>;
constexpr float c_Radius = 2.0f;
constexpr float c_Period = 2.0f; // Seconds for one lap: one loop of the clip

// The clip: where the root is, and which way it faces, at a time inside one loop.
RootSample SampleClip(float time)
{
	const float angle = 2.0f * c_Pi * time / c_Period;
	return { { c_Radius * (1.0f - std::cos(angle)), c_Radius * std::sin(angle) }, angle };
}

// The shortest signed angle from a to b.
float AngleDifference(float a, float b)
{
	float difference = std::fmod(b - a, 2.0f * c_Pi);
	if (difference > c_Pi)
		difference -= 2.0f * c_Pi;
	else if (difference < -c_Pi)
		difference += 2.0f * c_Pi;
	return difference;
}

Vec RotateY(const Vec& vector, float angle)
{
	return { std::cos(angle) * vector.X + std::sin(angle) * vector.Z, -std::sin(angle) * vector.X + std::cos(angle) * vector.Z };
}

// The travel of one update, in the frame the root faced when the update began.
struct Travel
{
	Vec Translation;
	float Yaw = 0.0f;

	void Append(const RootSample& from, const RootSample& to)
	{
		const Vec local = RotateY({ to.Position.X - from.Position.X, to.Position.Z - from.Position.Z }, -from.Yaw);
		const Vec turned = RotateY(local, Yaw);
		Translation.X += turned.X;
		Translation.Z += turned.Z;
		Yaw += AngleDifference(from.Yaw, to.Yaw);
	}
};

// The playhead goes from before to after (times since the start); a loop boundary splits the stretch in two.
Travel Advance(float before, float after)
{
	const float loopBefore = std::floor(before / c_Period);
	const float loopAfter = std::floor(after / c_Period);
	const float from = before - loopBefore * c_Period;
	const float to = after - loopAfter * c_Period;
	Travel travel;
	if (loopBefore == loopAfter)
	{
		travel.Append(SampleClip(from), SampleClip(to));
		return travel;
	}
	travel.Append(SampleClip(from), SampleClip(c_Period));
	travel.Append(SampleClip(0.0f), SampleClip(to));
	return travel;
}

int main()
{
	Entity entity;
	entity.Position = { 10.0f, 0.0f };
	entity.Yaw = c_Pi * 0.5f; // Facing +X
	const Vec center = { entity.Position.X + c_Radius * std::cos(entity.Yaw), entity.Position.Z - c_Radius * std::sin(entity.Yaw) };
	const float step = 0.7f;
	for (int update = 1; update <= 6; update++)
	{
		const float before = static_cast<float>(update - 1) * step;
		const Travel travel = Advance(before, before + step);
		const Vec move = RotateY(travel.Translation, entity.Yaw);
		entity.Position = { entity.Position.X + move.X, entity.Position.Z + move.Z };
		entity.Yaw += travel.Yaw;
		const float away = std::hypot(entity.Position.X - center.X, entity.Position.Z - center.Z);
		std::printf("t=%.1f  x=%6.3f  z=%6.3f  yaw=%6.1f  from centre=%.3f\n", before + step, entity.Position.X, entity.Position.Z,
			entity.Yaw * 180.0f / c_Pi, away);
	}
	return 0;
}
```

```text output-of="animation-root-motion-toy.cpp"
t=0.7  x=11.618  z=-3.176  yaw= 216.0  from centre=2.000
t=1.4  x= 8.098  z=-2.618  yaw= 342.0  from centre=2.000
t=2.1  x=10.618  z=-0.098  yaw= 468.0  from centre=2.000
t=2.8  x=11.176  z=-3.618  yaw= 594.0  from centre=2.000
t=3.5  x= 8.000  z=-2.000  yaw= 720.0  from centre=2.000
t=4.2  x=11.176  z=-0.382  yaw= 846.0  from centre=2.000
```

1. **Lines 29–33:** The clip is a circle: the root's place and heading at a time inside one loop.
2. **Line 36:** The turn between two headings takes the shortest way round, as in the engine.
3. **Lines 57–64:** `Append` measures a stretch in the frame the root faced at its start, then turns it by the yaw so far.
4. **Lines 67–83:** A stretch that crosses the loop boundary is split in two, as in the engine.
5. **Lines 96–98:** The entity moves by the travel turned by its own yaw, and the yaw is added after.

The distance from the centre stays at 2.000 in every row, also in the rows that cross a loop boundary (t = 2.1 and 4.2). The toy omits blending, the hold on the pose, vertical motion, scale, parents and controllers; the real code has each of them.

## The real code

### What the setup knows

`RootMotionSetup` is made for a skeleton each time the skeleton loads, and holds two things.

The first is the **ancestors' rest transform**: one model-space matrix and one rotation that all the joints above the root motion joint form together, taken from the :term[rest pose]{id=rest-pose}. These joints usually only orient the skeleton, and the root's motion must be measured through them. The second is a mask, one :term[byte]{id=byte} per joint, that marks the root motion joint and everything below it. Root motion moves exactly that subtree.

The :term[importer]{id=importer} picks the root motion joint: the lowest-numbered joint over all of the file's skins, which is the topmost one, such as a character's hips. `RootMotionSetup::Create` walks up from it to collect the ancestors and then walks down the joint list once to fill the mask. It marks a joint when its parent is marked, so one pass over the joints after the root is enough.

### Reading the root's heading

To say how far the root has turned, the engine needs one angle from a rotation. `GetYaw` finds where the rotation sends the +Z direction and reads the angle of that direction in the ground plane with `atan2`. Recall that `atan2(x, z)` gives the angle of the point (x, z) from the +Z axis, in radians, between minus pi and pi.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L17-L24"
// The heading of a rotation: the angle about +Y of where it turns +Z (0 for rotations that keep +Z pointing up or down).
float GetYaw(const glm::quat& rotation)
{
	const glm::vec3 forward = rotation * glm::vec3(0.0f, 0.0f, 1.0f);
	if (std::abs(forward.x) < 1.0e-6f && std::abs(forward.z) < 1.0e-6f)
		return 0.0f;
	return std::atan2(forward.x, forward.z);
}
```

The guard handles a rotation that points +Z straight up or down: then there is no heading, and the answer is 0.

### Adding up the travel

A stretch of the clip is a pair of root samples, one at the start and one at the end. `RootTravel::Append` adds one stretch to the travel so far. It measures the stretch in the frame the root faced at the start of the stretch, and then turns that move by the yaw gathered so far, so that stretches join up as a path.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L88-L96" symbol="RootTravel::Append"
// Appends a stretch that starts where this one ends.
void Append(const RootSample& from, const RootSample& to, const glm::quat& clipStart)
{
	const float fromYaw = GetYaw(from.Rotation * glm::inverse(clipStart));
	const float toYaw = GetYaw(to.Rotation * glm::inverse(clipStart));
	const glm::vec3 local = RotateY(to.Position - from.Position, -fromYaw);
	Translation += RotateY(local, Yaw);
	Yaw += AngleDifference(fromYaw, toYaw);
}
```

All headings are relative to the clip's start: each sample's rotation is multiplied by the inverse of the rotation at time 0. The result is a travel in "clip-start frame": zero yaw means the clip's first heading, whatever the model's own orientation.

::figure{id=extraction}

### A worked update across a loop boundary

:::example[A 0.4 s update that crosses the loop]
A walk clip lasts 1 s, loops, and its root travels 2 m along +Z in each pass without turning. The :term[playhead]{id=playhead} is at 0.8 s and the update is 0.4 s. The playhead ends at 1.2 s, which is 0.2 s into the next pass, so one loop boundary is crossed.

The stretch from 0.8 s to the end of the clip is 0.2 s of travel: 0.4 m. The stretch from the start to 0.2 s is another 0.4 m. No whole loop lies between. The sum is 0.8 m, which is 2 m/s times 0.4 s, as it should be. The yaw is 0, so the move stays +Z in the clip-start frame.

Now the entity: it is turned 90 degrees about +Y, so its +Z points along world +X, and its scale is 2. The move (0, 0, 0.8) is carried by the entity's world transform, which turns it to +X and doubles it: 1.6 m along world +X. The feet travel 0.8 m in the animator's space and 1.6 m in the world, and the entity matches them.
:::

### Loop crossings and the blend

`Advance` moves every playing entry's playhead and measures the root's travel for each one. A **crossing** is one pass over the loop boundary; the helper that moves the playhead says how many happened, and a negative count means the clip played backwards.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L652-L698" from="const float scaled = deltaTime * settings.Speed;" to="travel[index].Append(last, to, clipStart);" symbol="AnimatorInstance::Advance"
const float scaled = deltaTime * settings.Speed;
const bool rootMotion = settings.ApplyRootMotion && assets.RootMotion && assets.SkeletonAsset->GetJointCount() == assets.RootMotion->InSubtree.size();
std::array<RootTravel, c_MaxPlaying> travel = {};
const uint32_t current = m_Count - 1;
const double previousNormalized = m_Entries[current].Normalized;
for (uint32_t index = 0; index < m_Count; index++)
{
	Playing& entry = m_Entries[index];
	const float seconds = scaled * GetStateSpeed(assets, entry.State);
	const float before = entry.Time;
	const int64_t crossings = AdvanceEntry(entry, seconds, assets, settings, index == current, outEvents);
	if (!rootMotion)
		continue;
	const AnimatorClip clip = GetClip(assets, entry.State);
	if (!clip.Clip || !clip.Binding || !(clip.Clip->GetDuration() > 0.0f))
		continue;
	// The root's travel through each pass of the clip this update made, split where the playhead crossed the loop
	// boundary (whole loops included).
	const Skeleton& skeleton = *assets.SkeletonAsset;
	const RootMotionSetup& setup = *assets.RootMotion;
	const float duration = clip.Clip->GetDuration();
	const glm::quat clipStart = SampleRoot(clip, skeleton, setup, 0.0f).Rotation;
	const RootSample from = SampleRoot(clip, skeleton, setup, before);
	const RootSample to = SampleRoot(clip, skeleton, setup, entry.Time);
	if (crossings == 0)
	{
		travel[index].Append(from, to, clipStart);
		continue;
	}
	const RootSample first = SampleRoot(clip, skeleton, setup, 0.0f);
	const RootSample last = SampleRoot(clip, skeleton, setup, duration);
	const uint32_t whole = static_cast<uint32_t>(std::min<int64_t>((crossings > 0 ? crossings : -crossings) - 1, c_MaxRootMotionLoops));
	if (crossings > 0)
	{
		// On to the end, whole loops, then from the start.
		travel[index].Append(from, last, clipStart);
		for (uint32_t loopIndex = 0; loopIndex < whole; loopIndex++)
			travel[index].Append(first, last, clipStart);
		travel[index].Append(first, to, clipStart);
	}
	else
	{
		// Backwards: down to the start, whole loops back, then on from the end.
		travel[index].Append(from, first, clipStart);
		for (uint32_t loopIndex = 0; loopIndex < whole; loopIndex++)
			travel[index].Append(last, first, clipStart);
		travel[index].Append(last, to, clipStart);
```

1. **Line 662:** `AdvanceEntry` moves the playhead and returns how many loop boundaries it crossed, negative when the clip plays backwards.
2. **Lines 673–675:** The root at the clip's start, where this update began and where it ends: all three are samples of the same clip.
3. **Line 683:** The whole loops between the two partial stretches, one fewer than the crossings, and never more than 64.
4. **Lines 686–690:** Forwards: from the playhead to the end, each whole loop, then from the start to the playhead.

Forwards, the travel goes to the clip's end, then through the whole loops, then from the start. Backwards it is the mirror: down to the start, whole loops back, and on from the end. The number of whole loops is capped at 64 (`c_MaxRootMotionLoops`), so a huge update, such as a long stall, cannot make the engine add up millions of stretches. The cost is that an update that crosses more than 65 boundaries moves the entity less than the clip's travel.

The next part combines the entries. A :term[cross-fade]{id=cross-fade} has several entries playing, and each has a travel and a weight. The weights are those after the update, because the update may have dropped entries whose fade finished.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L702-L722" from="m_FadeElapsed += std::abs(scaled);" to="m_RootMotion.Translation.y = 0.0f;" symbol="AnimatorInstance::Advance"
m_FadeElapsed += std::abs(scaled);
UpdateWeights();
if (rootMotion)
{
	// Weighted by the shares after the update; the move stays in the plane (vertical motion stays in the pose).
	// The entries before UpdateWeights may have been dropped: travel was recorded by the old indices, and a finished
	// fade keeps only the last entry, so its travel weighs 1.
	if (m_Count == 1)
	{
		m_RootMotion.Translation = travel[current].Translation;
		m_RootMotion.Yaw = travel[current].Yaw;
	}
	else
	{
		for (uint32_t index = 0; index < m_Count; index++)
		{
			m_RootMotion.Translation += travel[index].Translation * m_Entries[index].Weight;
			m_RootMotion.Yaw += travel[index].Yaw * m_Entries[index].Weight;
		}
	}
	m_RootMotion.Translation.y = 0.0f;
```

1. **Lines 709–713:** With one entry left the travel counts in full, whatever the weight says.
2. **Lines 716–720:** With a blend each entry's move and yaw are multiplied by its weight and added.
3. **Line 722:** The vertical part is dropped, and stays in the pose.

If one entry is left, its travel counts in full. The y component is set to 0 last: vertical motion stays in the pose.

:::example[A cross-fade from walk to run]
The walk clip's root travels 2 m/s and the run clip's 4 m/s. Halfway through a fade the shares are 0.5 and 0.5, and the update is 0.5 s. Walk contributes 1 m times 0.5, run contributes 2 m times 0.5, and the entity moves 1.5 m. At a share of 0.25 for run, the move is 0.75 times 1 m plus 0.25 times 2 m: 1.25 m. A blend between the two paces gives a move between the two paces, so there is no sliding on either end, and none in between.
:::

### Holding the root in the pose

The pose must not move by the amount that the entity moves. At the end of `Evaluate`, the animator computes each entry's offset from where its clip started and weights it the same way. It then calls `HoldRoot`, which moves the whole subtree of the root motion joint back by that offset and turns it back by the yaw, about the root's own position.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L829-L846" from="// Root motion moves the entity; the pose keeps" to="HoldRoot(outModel, *assets.RootMotion, skeleton.GetRootMotionJoint(), offset, yaw);" symbol="AnimatorInstance::Evaluate"
// Root motion moves the entity; the pose keeps the root where (and facing how) each clip started: the root's subtree
// is moved back by its weighted offset from the clips' starts.
glm::vec3 offset(0.0f);
float yaw = 0.0f;
for (uint32_t index = 0; index < m_Count; index++)
{
	const Playing& entry = m_Entries[index];
	const AnimatorClip clip = GetClip(assets, entry.State);
	if (!clip.Clip || !clip.Binding)
		continue;
	const RootSample start = SampleRoot(clip, skeleton, *assets.RootMotion, 0.0f);
	const RootSample now = SampleRoot(clip, skeleton, *assets.RootMotion, entry.Time);
	const float weight = m_Count == 1 ? 1.0f : entry.Weight;
	offset += (now.Position - start.Position) * weight;
	yaw += GetYaw(now.Rotation * glm::inverse(start.Rotation)) * weight;
}
offset.y = 0.0f;
HoldRoot(outModel, *assets.RootMotion, skeleton.GetRootMotionJoint(), offset, yaw);
```

1. **Lines 833–844:** For each entry, the root's offset and turn since the clip's start, weighted as the travel was.
2. **Line 845:** The offset is flat, like the travel.
3. **Line 846:** The subtree is moved back by that offset and turned back by that yaw.

The correction is a translation, a rotation and a translation back, built once and multiplied into every joint of the subtree.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L62-L74" symbol="HoldRoot"
// Root motion moves the entity, so the pose holds the root's subtree back: moved by -offset in the plane and turned by
// -yaw about the root's position.
void HoldRoot(std::vector<glm::mat4>& model, const RootMotionSetup& setup, JointIndex root, const glm::vec3& offset, float yaw)
{
	const glm::vec3 pivot(model[root][3].x, 0.0f, model[root][3].z);
	const glm::mat4 correction = glm::translate(glm::mat4(1.0f), pivot - offset) * glm::rotate(glm::mat4(1.0f), -yaw, glm::vec3(0.0f, 1.0f, 0.0f))
		* glm::translate(glm::mat4(1.0f), -pivot);
	for (size_t joint = 0; joint < model.size(); joint++)
	{
		if (setup.InSubtree[joint])
			model[joint] = AnimationMath::MultiplyAffine(correction, model[joint]);
	}
}
```

1. **Line 66:** The turn happens about the root's own place on the ground.
2. **Lines 67–68:** Move to the pivot less the offset, turn by minus the yaw, move the pivot to the origin: one matrix for the whole subtree.
3. **Lines 69–73:** Only joints marked in the mask are corrected.

The pivot's Y is 0 and the offset's Y is 0, so the hold never lifts the pose: the vertical part of the clip's root motion is left alone, as the delta leaves it alone.

### Moving the entity

`AnimationSystem::ApplyRootMotion` is the one place that moves the entity. It carries the move into the world with the entity's world transform, scale included, and multiplies the yaw into the rotation. Then it chooses between two branches.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L788-L827" symbol="AnimationSystem::ApplyRootMotion"
void AnimationSystem::ApplyRootMotion(Entity animator, const RootMotionDelta& delta)
{
	if (!animator.IsValid() || animator.GetScene() != &m_Scene || delta.IsZero())
		return;
	// The move is in the entity's space: its world transform takes it to the world (scale included, so a model scaled up
	// travels as far as its feet do), the parent's inverse into the space of the local translation.
	const glm::mat4 world = m_Scene.GetWorldTransform(animator);
	glm::vec3 move = glm::vec3(world * glm::vec4(delta.Translation, 0.0f));
	TransformComponent& transform = animator.GetTransform();
	const glm::quat rotation = glm::normalize(transform.Rotation * glm::angleAxis(delta.Yaw, glm::vec3(0.0f, 1.0f, 0.0f)));
	if (!std::isfinite(rotation.x) || !std::isfinite(rotation.y) || !std::isfinite(rotation.z) || !std::isfinite(rotation.w))
		return;

	// A character controller walks the move at its next fixed step, colliding as it walks (it stops at walls, climbs steps,
	// keeps to the ground), instead of being placed there: only the turn is written to the entity. The controller writes
	// its position back and keeps the entity's rotation.
	if (ICharacterControl* characters = m_Scene.GetService<ICharacterControl>(); characters && characters->AddCharacterMotion(animator, move))
	{
		if (delta.Yaw != 0.0f)
		{
			transform.Rotation = rotation;
			animator.MarkModified<TransformComponent>();
		}
		return;
	}

	if (const Entity parent = animator.GetParent())
	{
		const glm::mat4 parentWorld = m_Scene.GetWorldTransform(parent);
		if (!(std::abs(glm::determinant(glm::mat3(parentWorld))) > Scene::c_MinInvertibleDeterminant))
			return;
		move = glm::vec3(glm::inverse(parentWorld) * glm::vec4(move, 0.0f));
	}
	const glm::vec3 translation = transform.Translation + move;
	if (!std::isfinite(translation.x) || !std::isfinite(translation.y) || !std::isfinite(translation.z))
		return;
	transform.Translation = translation;
	transform.Rotation = rotation;
	animator.MarkModified<TransformComponent>();
}
```

1. **Lines 794–795:** The world transform carries the move into the world, scale included.
2. **Lines 797–799:** The new rotation is checked before anything is written.
3. **Lines 804–811:** A controller takes the move, and only the turn is written.
4. **Lines 814–820:** Without a controller, the move goes through the inverse of the parent's world transform, unless it cannot be inverted.
5. **Lines 821–826:** The new translation and rotation are written and the change is signalled.

With a controller, only the turn is written and the move is handed to the controller, which walks it at its next :term[fixed step]{id=fixed-step}, colliding as it goes. The walk is [taught with the controller](../physics/character-controllers.md). Without one, the world move goes through the inverse of the parent's world transform into the space of the local translation, and the transform is changed and signalled.

Note the hand-off: `AddCharacterMotion` finds the controller by the animator's own entity. If the controller sits on a parent and the animator on a model below it, the lookup fails, the code falls through to the second branch, and the model walks away from its capsule. Put the animator and the controller on the same entity.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| In-place clips moved by code | Simple prototypes | A speed tuned in code, no clip-specific setup | Feet that slide whenever speed and clip differ |
| Full three-axis root motion | Games that author climbs in clips | Climbs and jumps authored in the clip | A clip that fights gravity and the controller's ground contact |
| Motion matching | Games with large clip libraries | Choosing clips by the speed the player wants | A large clip library and a search step each frame |
| Writing the root's place, not its delta | Simple preview tools | No loop-boundary arithmetic | A jump back at each loop, and no hand-off to collision |

Further reading names sources for these.

## How it is tested

The suite `Animation.RootMotion` in `StrataTests/src/Animation/AnimationSystemTests.cpp` has four cases. The first moves an entity by the clip's travel, and checks that the root stays in place in the pose of the entity that moves and travels in the pose of one that does not. It uses a turned entity, an entity under a parent scaled by 2, and an entity with root motion off, with steps of 0.07 s that do not divide the loop.

The second case checks the turn about +Y. The third checks that an entity moves and turns by the same amount in every update, also across loop boundaries. The fourth puts a controller on the walker: a wall stops it, a disabled controller lets the entity go through the wall, and the turn still applies.

Run one suite directly with the test :term[executable]{id=executable}:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Animation.RootMotion
```

A passing run reports its test cases and assertions as passed.

## Changing it safely

- **Keep the delta in the plane.** Anything that adds a Y component also has to change `HoldRoot`, or the pose and the entity disagree.
- **Keep one place that moves.** Add new effects of root motion inside `ApplyRootMotion`, so the signal and the checks for finite values stay in one function.
- **Signal what you write.** The transform contract applies: write, then `MarkModified<TransformComponent>`.
- **Extend the cases of `Animation.RootMotion`.** A change that alters the travel needs a case with a loop boundary, as the third test has.

## Summary

- You can compute the root travel of an update that crosses a loop boundary: the end of one pass plus the start of the next, plus the whole loops between.
- You can compute the move of a blend: each entry's travel times its weight after the update, with Y set to 0.
- The pose holds the root's subtree back so that the mesh does not run ahead of the entity by the same amount twice.
- The travel of a looping walk goes into the entity, scaled and turned by its world transform, and not into the pose.
- On an entity with a character controller, the move goes to the controller and only the turn is written.

## Check yourself

1. A walk clip lasts 1 s and its root travels 2 m per pass. An update starts at 0.9 s and lasts 0.25 s. How far does the root travel in the update? (a) 0.5 m (b) 0.5 m plus a jump of 1.5 m back (c) 0.3 m

   :::answer{tests="travel-split"}
   (a). The playhead ends at 1.15 s: 0.1 s to the end of the pass gives 0.2 m, and 0.15 s into the next pass gives 0.3 m, in all 0.5 m. Option (b) is the mistake of measuring only where the root is now. Option (c) is only the second part: it forgets the 0.2 m to the end of the first pass.
   :::

2. Two entries play with weights 0.6 for walk (2 m/s) and 0.4 for run (4 m/s). The update lasts 0.5 s. What move does the entity get?

   :::answer{tests="blend-travel"}
   The walk travel is 1 m and the run travel is 2 m. The weighted sum is 0.6 times 1 plus 0.4 times 2, which is 1.4 m.
   :::

3. If the pose did not hold the root back, what would you see?

   :::answer{tests="hold-root"}
   The root would travel in the pose and the entity would move too, so the mesh would run ahead of its entity at twice the speed: the double-motion mistake.
   :::

4. A model with an animator sits below an entity that carries the character controller, and root motion is on. What happens?

   :::answer{tests="where-travel-goes,controller-branch"}
   The controller lookup is by the animator's own entity, so it fails. The model's transform changes instead, and it walks away from the capsule. The travel of the clip still goes into the entity, but not through the controller.
   :::

## Exercises

1. **Basic.** The entity is scaled by 3 and faces +X. The clip's root travels 2 m along +Z in 1 s. What move, in the world, does an update of 0.5 s make?

   :::answer[Worked solution]{tests="travel-split,where-travel-goes"}
   The clip's travel is 1 m along +Z in the animator's space. The world transform turns +Z to +X and scales by 3, so the entity moves 3 m along +X.
   :::

2. **Medium.** Change the toy so that the clip's radius is 4 m and keep the step. Predict the distance from the centre in each row, then run it.

   :::answer[Worked solution]{tests="travel-split"}
   Each stretch is a chord of the same circle, carried over exactly, so the distance from the centre stays equal to the new radius, 4.000, in every row.
   :::

3. **Medium.** The next sketch cross-fades from walk to run and prints the move of one update for five shares. Predict the five numbers, then compare.

   :::answer[Worked solution]{tests="blend-travel" solution="sketches/animation-root-motion-blend.cpp"}
   Each pass of the loop sets the share of the run clip and adds each entry's travel times its weight.

   ```cpp sketch="animation-root-motion-blend.cpp"
   // Root motion of a cross-fade: each playing entry's travel, weighted by its share of the blend.
   #include <cstdio>

   struct Entry
   {
   	float Speed = 0.0f;  // Metres per second the clip's root travels
   	float Weight = 0.0f; // Share of the blend after the update
   };

   int main()
   {
   	const float deltaTime = 0.5f;
   	for (int fade = 0; fade <= 4; fade++)
   	{
   		const float share = static_cast<float>(fade) / 4.0f;
   		const Entry entries[2] = { { 2.0f, 1.0f - share }, { 4.0f, share } };
   		float travel = 0.0f;
   		for (const Entry& entry : entries)
   			travel += entry.Speed * deltaTime * entry.Weight;
   		std::printf("run share %.2f: the entity moves %.2f m\n", share, travel);
   	}
   	return 0;
   }
   ```

   ```text output-of="animation-root-motion-blend.cpp"
   run share 0.00: the entity moves 1.00 m
   run share 0.25: the entity moves 1.25 m
   run share 0.50: the entity moves 1.50 m
   run share 0.75: the entity moves 1.75 m
   run share 1.00: the entity moves 2.00 m
   ```

   1. **Lines 4–8:** An entry is a clip's pace and its weight after the update.
   2. **Line 16:** The two entries share the blend: the walk takes what the run does not.
   3. **Lines 18–19:** Each entry's travel, its pace times the update, is multiplied by its weight.

   The move rises in equal steps of 0.25 m from 1 m to 2 m, because each share moves 0.25 of the way from the walk's 1 m to the run's 2 m.
   :::

4. **Hard.** Trace it yourself: find where an entity with a character controller gets its move from the clip.

   :::answer[Worked solution]{tests="controller-branch"}
   Set a breakpoint in `AnimationSystem::ApplyRootMotion` in `Strata/src/Strata/Animation/AnimationSystem.cpp` and run the test case "Root motion walks a character controller, which collides, and turns its entity". The branch with the controller runs: `AddCharacterMotion` receives the world move. Step into it, through `PhysicsSystem::AddCharacterMotion` and `PhysicsWorld::AddCharacterMotion`, to `CharacterControllerSet::AddMotion` in `Strata/src/Strata/Physics/CharacterControllers.cpp`, which calls `FindController` with the animator's own entity and adds the move to the record's pending motion.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: `GetYaw`, `RootTravel`, `SampleRoot`, `HoldRoot`, `RootMotionSetup::Create`, `AnimatorInstance::Advance` and `Evaluate`.
- `Strata/src/Strata/Animation/AnimationSystem.cpp`: `AnimationSystem::ApplyRootMotion`.
- `Strata/src/Strata/Physics/CharacterControllers.cpp`: `CharacterControllerSet::AddMotion`.
- `StrataTests/src/Animation/AnimationSystemTests.cpp`: the suite `Animation.RootMotion`.

## Further reading

- "Animation Programming" chapters on root motion in game engine texts: root motion extraction against in-place movement, intermediate.
- Documentation of other engines' root motion features: how a delta is extracted and applied, beginner.
- Texts on motion matching: how clips are chosen by desired movement, advanced.
