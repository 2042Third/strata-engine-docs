---
id: animation/culling
title: "Animating only what is seen"
description: "How an animator skips its pose while no renderer sees it, keeps its time and events, and reappears posed where its clip took it."
kind: internals
size: M
tracks: [E]
needs: [animation/system, animation/skinning, draw/bounds-culling, draw/gpu-driven]
time: 55
learn:
  - id: skip-keep
    text: explain what an unseen WhenVisible animator skips, what it keeps, and why gameplay must not depend on the camera
  - id: reach-compute
    text: compute the number of samples and the boxes of a clip's reach
  - id: decision-trace
    text: trace a visibility report from the renderer to the next update's decision to pose
  - id: stale-pause
    text: explain how a stale pose is detected and posed while the game is paused
since: 0.3.0
status: final
---

A level can hold a thousand characters while the player sees forty. Posing the other nine hundred and sixty costs time and shows nothing. An animator whose **culling mode** is `WhenVisible` (a **WhenVisible animator**) skips its pose while no :term[renderer]{id=renderer} reports it seen. It still advances its time, fires its events, takes its transitions and applies its :term[root motion]{id=root-motion}, so the game plays the same whatever the camera does. This page teaches the animation half of that loop and links the pages on the renderer's half.

## The problem and how engines solve it

Posing an animator means sampling clips, blending and multiplying matrices down the joint tree. For one character that is cheap. For a crowd it adds up, and most of the crowd stands behind the camera, behind a wall or a kilometre away. Engines meet this in three ways.

The first is to pose less often. An engine lowers the update rate of an animator by its distance or by the share of the screen it covers, so a far character gets ten poses a second instead of sixty. Unreal Engine calls this its update rate :term[optimization]{id=optimization}. Every character still pays something, and a far character may move in visible jumps.

The second is to stop posing what nobody sees. Unity's animator has a culling mode with the choices `Always Animate`, `Cull Update Transforms` and `Cull Completely`. The last one freezes the animation while no renderer is visible, so the character's time stops too, and gameplay that watches the clip breaks. The middle one keeps the state machine running and skips the rest.

The third is Strata's: two modes, `AlwaysAnimate` and `WhenVisible`. The second resembles Unity's middle choice. Time, events, transitions and root motion always run, and only the pose is skipped. The choice rests on a report from the renderer about what it drew, not on a distance rule.

The report has a trap. A skipped animator holds a frozen pose. Suppose a walk clip carries the character ten units to the right. A renderer that tested the frozen pose would test the place where the walk starts, find it outside the view and report nothing. The animator would never be posed again, and the character would stay frozen for good.

Strata avoids this with the **reach**: the box of every place a clip can take the joints. The renderer tests the box as well as the pose.

## The map

The loop has two halves. The animation system runs in the update and decides which animators to pose. The renderer runs after it, draws, and tells the system what it drew. The next update reads that report.

```mermaid caption="The WhenVisible loop: each update poses the animators reported after the update before, and the renderer reports the animators of what it draws." alt="A cycle of five boxes. The update poses reported animators and publishes poses and reaches. The renderer tests meshes with bounds grown by the reach. Extraction collects the animators of visible meshes and shadows. A report returns to the next update."
flowchart LR
	U["Update N: pose the animators reported after update N-1"] --> P["Publish poses and reaches"]
	P --> R["Renderer tests skinned proxies with posed bounds plus the reach"]
	R --> E["Extraction collects animators of visible meshes and of shadows that can fall into the view"]
	E --> V["ReportVisible, once per animator"]
	V --> U
```

The pieces live in these files:

| Part | File | Owns |
| --- | --- | --- |
| The mode | `Strata/src/Strata/Animation/AnimationComponents.h` | `AnimatorCullingMode`: `AlwaysAnimate` or `WhenVisible` |
| The decision | `Strata/src/Strata/Animation/AnimationSystem.cpp` | `PrepareStep`, `ReportVisible`, `OnPausedUpdate` |
| The reach | `Strata/src/Strata/Animation/AnimatorInstance.cpp` | `AnimationReach::Compute`, `GetReach` |
| The service | `Strata/src/Strata/Scene/SceneServices.h` | `ISkinningPoses`, the interface the renderer calls |
| The report | `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp` | collecting animators, `ReportVisibleAnimators` |

The animation system and the renderer never include each other. The renderer reaches the system only through `ISkinningPoses`, a service of the scene.

## The contract

Six rules hold for `WhenVisible`, each with its reason.

1. **A WhenVisible animator keeps time, events, transitions and root motion.** A script that waits for an :term[animation event]{id=animation-event-notify}, or a door that opens when a clip ends, must work the same whether anyone looks. An unseen robot keeps its footsteps because its footstep events keep firing.
2. **A reach is published with every pose that may be skipped.** Without it the renderer could not find the animator again once its clip had carried it elsewhere.
3. **An animator that only moves rigid parts poses every update.** A model made of rigid parts, such as a chest, has attachments but no skinned mesh. Reports come from skinned meshes, so no renderer could report it, and its parts would stand still.
4. **The first pose is always computed.** The renderer needs something to draw before it can report anything.
5. **A joint that gameplay reads may depend on the camera.** While a `WhenVisible` animator is unseen, `GetJointTransform` returns its stale pose, placed at the entity's current transform. A **stale pose** is a pose older than its animator's time.
6. **Scripts read the previous update's pose.** The Animation system runs after Scripting, so a script that reads a joint sees the pose of the update before.

:::why
Rule 1 is the reason the mode exists. If time stopped while unseen, a guard could stand in a frozen attack clip and its hit event would never fire. Strata keeps every result that gameplay can read and drops only the picture of the pose.
:::

Rule 5 is the one exception to the camera-free game. A script that asks for a joint's transform asks for a pose, and an unseen animator has an old one. Use `AlwaysAnimate` for a character whose joints gameplay reads.

## Posing by report: the decision

The part of the update that decides is `PrepareStep`. The system counts updates in `m_UpdateIndex`, and `ReportVisible` writes that count into the animator's record as `SeenUpdate`. The decision compares the two.

The next fence is the whole decision. The first line is the setting root motion reads; watch for the four reasons to pose in the last: a mode other than `WhenVisible`, a report, rigid parts and a missing first pose.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L743-L750" from="record.Settings.ApplyRootMotion = component.ApplyRootMotion;" to="record.Evaluate = !record.MayCull || seen || rigidParts || record.PoseVersion == 0;" symbol="AnimationSystem::PrepareStep"
record.Settings.ApplyRootMotion = component.ApplyRootMotion;
// Unseen WhenVisible animators skip their poses, except for a first one (renderers then have something to draw until
// they report it). One that skins no mesh but places attachments (a model of rigid parts) has no mesh a renderer could
// see it by: it poses every update, or its parts would stand still.
record.MayCull = component.CullingMode == AnimatorCullingMode::WhenVisible;
const bool seen = record.SeenUpdate != 0 && record.SeenUpdate + 1 >= m_UpdateIndex;
const bool rigidParts = record.AttachedUpdate != 0 && record.AttachedUpdate + 1 >= m_UpdateIndex && !HasSkinUsers(record.ID);
record.Evaluate = !record.MayCull || seen || rigidParts || record.PoseVersion == 0;
```

An animator counts as seen when a renderer reported it after the previous update. The report stores the index of the latest update; the next update adds one to it and poses the animator when the sum is at least its own index. A pose version of 0 means the animator has no pose yet.

:::example
A thousand robots stand in a street. After update 7 the renderer finds 40 of them in view and reports them, so their `SeenUpdate` is 7.

In update 8 each of the 40 passes the test 7 + 1 >= 8 and poses. The other 960 skip, and the system's statistics count 40 in `Evaluated` and 960 in `Culled`. After update 8 the camera turns, and the renderer reports only 25 of the 40.

Update 9 poses those 25, because 8 + 1 >= 9. The other 15 still carry 7, and 7 + 1 >= 9 is false, so they skip. A robot that leaves the view poses for one more update, and a robot that enters it is drawn at most one update old.
:::

The decision has no clock and no distance. It reads one :term[integer]{id=integer} per animator, so an unseen animator costs one comparison.

## The reach

A pose says where the joints are now. The reach says where they can be while the clip plays. The system computes it for each clip with `AnimationReach::Compute`.

The function samples the clip at regular times. For each sample it builds the model-space matrices, widens a box to hold every joint's origin and keeps the largest scale. It does this twice: once with the pose as it is, and once as the pose would be with root motion held, as `Evaluate` does. Watch for the sample count and the two boxes.

```cpp src="Strata/src/Strata/Animation/AnimatorInstance.cpp#L132-L155" from="const uint32_t samples" to="reach.RootMotionBounds.Expand(glm::vec3(transform[3]));" symbol="AnimationReach::Compute"
const uint32_t samples = duration > 0.0f ? std::clamp(static_cast<uint32_t>(std::ceil(duration * c_SamplesPerSecond)) + 1u, 2u, c_MaxSamples) : 1u;
const AnimatorClip bound { &clip, &binding };
const RootSample start = SampleRoot(bound, skeleton, setup, 0.0f);
const JointIndex root = skeleton.GetRootMotionJoint();
std::vector<JointPose> local;
std::vector<glm::mat4> model(joints);
for (uint32_t sample = 0; sample < samples; sample++)
{
	const float time = samples > 1 ? duration * static_cast<float>(sample) / static_cast<float>(samples - 1) : 0.0f;
	local = skeleton.GetRestPose();
	clip.Sample(binding, time, local);
	skeleton.ComputeModelTransforms(local, model);
	for (const glm::mat4& transform : model)
	{
		reach.Bounds.Expand(glm::vec3(transform[3]));
		reach.MaxScale = std::max(reach.MaxScale, GetMaxScale(transform));
	}
	// As the pose holds the root with root motion (Evaluate).
	const RootSample now = SampleRoot(bound, skeleton, setup, time);
	glm::vec3 offset = now.Position - start.Position;
	offset.y = 0.0f;
	HoldRoot(model, setup, root, offset, GetYaw(now.Rotation * glm::inverse(start.Rotation)));
	for (const glm::mat4& transform : model)
		reach.RootMotionBounds.Expand(glm::vec3(transform[3]));
```

1. **Line 132:** the sample count, 15 for each second, with both ends included and a cap of 48.
2. **Lines 141–143:** the clip is sampled at the sample's time and turned into model-space matrices.
3. **Lines 146–147:** the first box takes each joint's origin, and the largest scale is kept.
4. **Lines 150–153:** the root's travel since the start is held, as the pose does with root motion.
5. **Lines 154–155:** the second box takes the joints of that held pose.

The count is 15 for each second of the clip, rounded up, plus one so that both ends are samples, and kept between 2 and 48. A clip of no length takes one sample.

:::example
A clip of 2 seconds gets $\lceil 2 \times 15 \rceil + 1 = 31$ samples, one every $2 / 30$ of a second. A 10-second clip would get 151, so the cap of 48 applies and a sample falls every 0.21 seconds. A 0.05-second clip gets $\lceil 0.75 \rceil + 1 = 2$, its start and its end. The symbol $\lceil x \rceil$ is read "round $x$ up to a whole number".

For the walk of the toy below, which carries a joint from $z = 0$ to $z = 10$ in one second, 16 samples touch $z = 0, 0.67, 1.33$ and on to 10, so the box is $[0, 10]$.
:::

A controller can play several clips at once. `GetReach` therefore unites the reaches of every clip that plays, with or without root motion as the animator's setting says, and takes the largest scale. If one clip has no valid reach, the animator publishes none. The reach travels with the pose in `SkeletonPose::Reach` and `ReachScale`, and the renderer adds it to the :term[posed bounds]{id=posed-bounds} with a margin of the largest joint extent times the scale.

The reach is not worked out again every update. Watch for the four values the next fence compares; the work repeats only when one differs from last time.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L768-L773" from="const uint32_t playRevision" to="record.ReachKnown = true;" symbol="AnimationSystem::StepRecord"
const uint32_t playRevision = record.Instance.GetPlayRevision();
const uint32_t setVersion = record.Set != c_NoSet ? m_Sets[record.Set].ReachVersion : 0;
if (record.ReachKnown && record.ReachPlayRevision == playRevision && record.ReachSetVersion == setVersion && record.ReachMayCull == record.MayCull
	&& record.ReachRootMotion == record.Settings.ApplyRootMotion)
	return;
record.ReachKnown = true;
```

The **play revision** is a counter in the animator instance that changes whenever what plays changes: a state, a transition or a clip. The set's reach version covers the clip assets that many animators share. The culling mode and the root motion setting are plain flags. An unseen animator pays a few comparisons per update, and the count `ReachUpdates` in the system's statistics shows how many did the real work.

## A toy version

The toy models the loop in one dimension. A clip carries a joint 10 units along $z$ each second, and the camera sees $z$ from 5.5 to 7.5. Each update adds time, then poses the animator if it was seen. Afterwards the renderer reports it when its bounds overlap the view. Two animators run side by side: one reports with the reach $[0, 10]$, and one with its pose alone.

```cpp sketch="animation-culling-toy.cpp"
// A toy WhenVisible animator: time always advances, the pose is computed only for an animator reported seen.
#include <cstdio>

struct Range
{
	float Min;
	float Max;
};

bool Overlaps(const Range& a, const Range& b)
{
	return a.Min <= b.Max && b.Min <= a.Max;
}

constexpr float c_Speed = 10.0f;           // The clip carries the joint 10 units along z each second.
constexpr Range c_Reach { 0.0f, 10.0f };   // Where the clip takes the joint over its whole loop.
constexpr Range c_View { 5.5f, 7.5f };     // The part of z the camera sees.

struct Animator
{
	float Time = 0.0f;
	float PoseZ = 0.0f;
	bool HasPose = false;
	int SeenUpdate = 0;
	bool UseReach = true;
};

void Update(Animator& animator, int updateIndex, float deltaTime)
{
	animator.Time += deltaTime; // Gameplay always sees the time go on.
	const bool seen = animator.SeenUpdate != 0 && animator.SeenUpdate + 1 >= updateIndex;
	if (seen || !animator.HasPose) // The first pose is always computed.
	{
		animator.PoseZ = animator.Time * c_Speed;
		animator.HasPose = true;
	}
}

void Report(Animator& animator, int updateIndex)
{
	Range bounds { animator.PoseZ, animator.PoseZ };
	if (animator.UseReach)
	{
		bounds.Min = c_Reach.Min;
		bounds.Max = c_Reach.Max;
	}
	if (Overlaps(bounds, c_View))
		animator.SeenUpdate = updateIndex;
}

int main()
{
	Animator withReach;
	Animator withoutReach;
	withoutReach.UseReach = false;
	for (int update = 1; update <= 10; update++)
	{
		Update(withReach, update, 0.1f);
		Update(withoutReach, update, 0.1f);
		Report(withReach, update);
		Report(withoutReach, update);
		std::printf("update %2d time %.1f | with reach: pose z %4.1f | own bounds only: pose z %4.1f\n", update, withReach.Time, withReach.PoseZ, withoutReach.PoseZ);
	}
}
```

```text output-of="animation-culling-toy.cpp"
update  1 time 0.1 | with reach: pose z  1.0 | own bounds only: pose z  1.0
update  2 time 0.2 | with reach: pose z  2.0 | own bounds only: pose z  1.0
update  3 time 0.3 | with reach: pose z  3.0 | own bounds only: pose z  1.0
update  4 time 0.4 | with reach: pose z  4.0 | own bounds only: pose z  1.0
update  5 time 0.5 | with reach: pose z  5.0 | own bounds only: pose z  1.0
update  6 time 0.6 | with reach: pose z  6.0 | own bounds only: pose z  1.0
update  7 time 0.7 | with reach: pose z  7.0 | own bounds only: pose z  1.0
update  8 time 0.8 | with reach: pose z  8.0 | own bounds only: pose z  1.0
update  9 time 0.9 | with reach: pose z  9.0 | own bounds only: pose z  1.0
update 10 time 1.0 | with reach: pose z 10.0 | own bounds only: pose z  1.0
```

1. **Line 16:** the reach of the whole walk, one box.
2. **Line 30:** time advances whether or not anyone sees the animator.
3. **Lines 31–32:** the decision of `PrepareStep` in one line: seen in the update before, or no pose yet.
4. **Lines 41–48:** the report uses the reach or the pose, and stores the update's index when the box meets the view.
5. **Line 55:** the second animator reports with its pose alone.

The animator that tests its pose alone is posed once, at time 0.1 and $z = 1$. That lies outside the view, so no report comes, and the pose stays at 1.0 while its time reaches 1.0. The animator with the reach is reported every update, and its pose follows the clip through $z = 6$ and 7, where the camera sees it.

The toy also hides a cost. Its reach covers the whole walk, so the animator is always reported and always posed while the camera looks anywhere near the walk. Strata has the same trade: a reach saves nothing for a character whose clip passes through the view, and it saves everything for one that never comes near. The toy has one dimension, no entity and no shadows.

## The real code, in the order data flows

The data flows from the renderer to the system and back. The first stop is the renderer's report.

### From the renderer

Extraction runs while the renderer prepares a frame. For each visible proxy with a skin it records the animator. For a shadow caster out of view it records the animator only when the caster's shadow can fall into the view; that test is `CanShadowView`, and [Sun shadows](../light/sun-shadows-1.md) teaches which casters count. When the :term[graphics processing unit]{id=gpu} (GPU) finds the casters, the renderer still tests the skinned proxies out of view on the :term[central processing unit]{id=processor} (CPU) for their animators. [The GPU-driven path](../draw/gpu-driven.md) explains the feedback.

At the end of extraction one function sends the list. Watch for the sort that keeps each animator once, and for the counter.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L1321-L1326" from="std::sort(m_VisibleAnimators.begin(), m_VisibleAnimators.end());" to="m_Stats.StalePoses++;" symbol="SceneRenderer::ReportVisibleAnimators"
std::sort(m_VisibleAnimators.begin(), m_VisibleAnimators.end());
m_VisibleAnimators.erase(std::unique(m_VisibleAnimators.begin(), m_VisibleAnimators.end()), m_VisibleAnimators.end());
for (const entt::entity animator : m_VisibleAnimators)
{
	if (poses->ReportVisible(animator))
		m_Stats.StalePoses++;
```

A character's meshes and shadows each name the animator, so the list holds duplicates. The sort puts them side by side, `std::unique` removes them, and the order is the same in every run. `ReportVisible` returns a flag, and the renderer adds one to its `StalePoses` count for each animator that answers yes.

### In the system

The report arrives in `AnimationSystem::ReportVisible`. Read what it writes and what it returns.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L935-L942" symbol="AnimationSystem::ReportVisible"
bool AnimationSystem::ReportVisible(entt::entity animator)
{
	AnimatorRecord* record = FindRecord(animator);
	if (!record)
		return false;
	record->SeenUpdate = m_UpdateIndex;
	return record->PoseStale && record->Active && record->PoseVersion != 0;
}
```

The function writes `SeenUpdate`, which `PrepareStep` reads in the next update. It also answers one question: is the pose the renderer drew older than the animator's time? The update sets the `PoseStale` flag when it skips an animator and clears it when it poses one. The answer is true only for an active animator that already has a pose. A report about an entity without an animator returns false and changes nothing.

### While paused

A paused game runs no update, so no animator is posed. A capture would then draw the pose of the last update that posed the animator, which can be old. `OnPausedUpdate` fixes that. Watch for the filter in the `if` and for what the body omits.

```cpp src="Strata/src/Strata/Animation/AnimationSystem.cpp#L950-L960" from="for (AnimatorRecord& record : m_Records)" to="m_Stats.PausedEvaluations++;" symbol="AnimationSystem::OnPausedUpdate"
for (AnimatorRecord& record : m_Records)
{
	if (record.Removed || !record.Active || !record.PoseStale || record.PoseVersion == 0 || record.SeenUpdate != m_UpdateIndex || !IsReady(record))
		continue;
	// At its time, with the settings of its latest update: nothing advances, so no events, transitions or root motion.
	if (!record.Instance.Evaluate(MakeAssets(record), record.Settings, scratch, record.Pose))
		continue;
	record.PoseVersion = m_NextPoseVersion++;
	record.PoseStale = false;
	posesChanged = true;
	m_Stats.PausedEvaluations++;
```

1. **Line 952:** the filter: an animator is posed only when it is active, stale, has a pose and was reported since the latest update.
2. **Lines 954–955:** the pose is computed at the animator's time with the settings of its latest update.
3. **Lines 957–958:** a new pose version replaces the stale pose, and the flag is cleared.
4. **Line 960:** the paused evaluations are counted.

Only an animator with a stale pose that a renderer reported since the latest update is posed. The pose is computed at the animator's time with the settings of its latest update, and nothing advances: no event, no transition, no root motion. A renderer that must show the pose of the moment, such as the one behind the command `viewport.capture`, sees a yes from `ReportVisible`, counts a stale pose and renders again. The second frame draws the fresh pose. [Stepping a paused game](../editor/stepping.md) describes pausing from the editor's side.

### Many animators

The Open World sample places thirty foxes in ten cells and sets `AlwaysAnimate` on every one. The figure's recipe loads one cell of the wildlife layer, sets `WhenVisible` on the six foxes it holds and looks from high above. Two of the six are in view, small: one on the grass and one on top of a tree, where the sample placed it.

::figure{id=foxes-afar}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Lower update rate by distance or screen size | Unreal Engine's update rate optimization | Far characters keep moving and never show a stale pose | Every animator still pays; hidden ones save nothing |
| Freeze everything while unseen | Unity's `Cull Completely` | The largest saving | Time, events and root motion stop, so gameplay depends on the camera |
| Test the frozen pose's own bounds | Simple implementations | No reach to compute | A character whose clip carries it elsewhere is never seen again |

The rows for other engines come from their manuals and cover only the modes named.

## How it is tested

Two suites carry the cases. `Animation.System` needs no GPU: it runs the animation system in a scene and reads the counts of evaluated and skipped animators. `GPU.Animation` renders and carries the label `gpu`.

- `WhenVisible animators compute their pose only while a renderer saw them` checks that an unseen animator keeps its time and its pose version, and that a report makes the next update pose it.
- `A renderer learns when it drew an older pose than its animator's time, and a paused scene poses such animators` checks that `ReportVisible` answers yes for a stale pose, and that a paused frame poses it once without advancing it.
- `WhenVisible animators that skin no mesh but place attachments animate every update` covers rigid parts.
- `An unseen WhenVisible animator's skinned meshes are bounded by where its clips take them` and `WhenVisible animators work out their reach again only when what it follows changes` cover the reach and its cache.
- `Shadow casters out of view report their animators only when their shadows can fall into the view` uses a low sun and three characters. Only the one whose shadow falls on the floor in front of the camera is reported.
- `A WhenVisible animator whose clip carries its mesh into a view that its first pose is not in is posed there` renders a walk whose arm starts out of view and reaches it.

Run the first suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Animation.System` and the second with `--test-suite=GPU.Animation`, or skip it with `ctest --preset linux-debug -LE gpu`. The other cases of `GPU.Animation` belong to [Skinned meshes in the renderer](../draw/skinned.md).

## Changing it safely

An input that changes where joints go, such as a new setting, joins the values that `StepRecord` compares. A missing one leaves a stale reach. A new source of reports calls `ReportVisible` once per animator per frame.

- Never let the decision show gameplay the camera. Time, events, transitions and root motion keep running, and the `Animation.System` tests check it.
- Publish a reach whenever a pose can be skipped, so a renderer finds the animator wherever its clip takes it.
- Pose in `OnPausedUpdate` only what a renderer reported, or a paused game pays for the whole crowd.

:::rule
Other :term[engine modules]{id=engine-module} reach animation only through :term[scene services]{id=scene-service} such as `ISkinningPoses`, and only the Engine layer and the asset pipeline include Animation. The reason is the layering of the engine, in which a lower module never includes a higher one.
:::

## What went wrong before

In the 0.4.0 round, a `WhenVisible` animator showed in a capture the pose of the capture before, also while the game was paused. The renderer drew the stale pose and could not tell. The answer of `ReportVisible` and `OnPausedUpdate` fixed it, and the second test above is its regression test.

## Summary

- An unseen `WhenVisible` animator skips its pose and keeps its time, events, transitions and root motion, because gameplay must not depend on the camera; its first pose is always computed, and rigid-part animators always pose.
- A reach samples each clip 15 times a second (2 to 48 samples) and keeps the joints' origins in two boxes, with and without root motion. The system works it out again only when the play revision, the set's reach version, the mode or the root motion setting changes.
- The renderer reports each animator once after extraction, and the next update's `PrepareStep` poses an animator whose `SeenUpdate` plus one reaches the update's index.
- `ReportVisible` returns whether the drawn pose is stale, and `OnPausedUpdate` poses those animators at their time without advancing them, so a capture renders again until it shows the pose of its moment.

## Check yourself

1. A walk clip carries a character 10 units to the right, and the camera sees only the far end. Why does Strata publish a reach instead of testing the frozen pose?

   - A. The frozen pose is too large to test.
   - B. The frozen pose stays at the start, never overlaps the view, so no report arrives and it stays frozen.
   - C. The reach is cheaper to compute than a pose.

   :::answer{tests="skip-keep"}
   B. A is wrong: a pose is a few matrices. C is wrong: the reach costs more than one pose, which is why Strata caches it. Only the reach lets the renderer find the animator where the clip will take it.
   :::

2. A robot stays out of view for ten seconds, and its clip fires footstep events. What happens to the footsteps, and why?

   :::answer{tests="skip-keep"}
   The footsteps keep firing. The update still advances time and collects events, and only the pose is skipped. Gameplay, such as a sound at each footstep, must not depend on the camera.
   :::

3. A clip lasts 1.2 seconds. How many samples does its reach take?

   :::answer{tests="reach-compute"}
   $\lceil 1.2 \times 15 \rceil + 1 = 18 + 1 = 19$, inside the range 2 to 48.
   :::

4. The renderer reports an animator after update 7 and not after update 8. Which update is the first to skip it?

   :::answer{tests="decision-trace"}
   Update 9. Update 8 poses it because 7 + 1 >= 8. In update 9 its `SeenUpdate` is still 7, and 7 + 1 >= 9 is false. This assumes it has a pose already and no rigid parts.
   :::

5. The game is paused and a capture draws an unseen animator. What does the renderer learn, and what does the system do?

   :::answer{tests="stale-pause"}
   `ReportVisible` returns yes, because the animator's pose is stale, and the renderer counts it in `StalePoses`. The next paused frame calls `OnPausedUpdate`, which poses the animator at its time without advancing it. The renderer renders again and draws the fresh pose.
   :::

## Exercises

1. **Basic.** Write the sample count of `AnimationReach::Compute` as a function and print it for clips of 0, 0.05, 0.5, 1, 2, 3.1 and 4 seconds.

   :::answer[Worked solution]{tests="reach-compute" solution="sketches/animation-culling-samples.cpp"}
   The count is 15 for each second of the clip, rounded up, plus one, kept between 2 and 48. A clip of no length takes one sample.

   ```cpp sketch="animation-culling-samples.cpp"
   // How many times AnimationReach::Compute samples a clip: 15 a second, the start and end included, 2 to 48.
   #include <algorithm>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>
   #include <initializer_list>

   constexpr float c_SamplesPerSecond = 15.0f;
   constexpr uint32_t c_MaxSamples = 48;

   uint32_t SampleCount(float duration)
   {
   	if (duration <= 0.0f)
   		return 1;
   	return std::clamp(static_cast<uint32_t>(std::ceil(duration * c_SamplesPerSecond)) + 1u, 2u, c_MaxSamples);
   }

   int main()
   {
   	for (const float duration : { 0.0f, 0.05f, 0.5f, 1.0f, 2.0f, 3.1f, 4.0f })
   		std::printf("clip of %.2f s: %2u samples\n", duration, SampleCount(duration));
   }
   ```

   ```text output-of="animation-culling-samples.cpp"
   clip of 0.00 s:  1 samples
   clip of 0.05 s:  2 samples
   clip of 0.50 s:  9 samples
   clip of 1.00 s: 16 samples
   clip of 2.00 s: 31 samples
   clip of 3.10 s: 48 samples
   clip of 4.00 s: 48 samples
   ```

   1. **Line 13:** a clip of no length takes one sample.
   2. **Line 15:** the count is rounded up, gets one more and is kept between 2 and 48.
   3. **Lines 20–21:** each duration is printed with its count.

   The 4-second clip would need 61 samples without the cap, and the 3.1-second clip 48 exactly.
   :::

2. **Medium.** Add a `SampleCount` statistic to `AnimationSystemStats` that counts the joints posed in an update. Read it with `WhenVisible` on and off for 1,000 animators of 30 joints, 50 of them in view.

   :::answer[Worked solution]{tests="skip-keep"}
   Add `uint32_t SampleCount = 0;` to the :term[struct]{id=struct} in `Strata/src/Strata/Animation/AnimationSystem.h`. In the loop of results in `AnimationSystem.cpp`, where `stats.Evaluated++` runs, add `stats.SampleCount += static_cast<uint32_t>(record.Pose.size());`. With `AlwaysAnimate` the count is $1000 \times 30 = 30000$. With `WhenVisible` only the 50 seen animators pose, so it is $50 \times 30 = 1500$, one twentieth. The statistic is defined here by the exercise; the engine has no such counter.
   :::

3. **Hard.** Trace it yourself. Follow one visibility report with a search, from the renderer's extraction to the next update's decision.

   :::answer[Worked solution]{tests="decision-trace"}
   Search for `ReportVisibleAnimators`. Its definition is in `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`; it sorts the list and calls `ISkinningPoses::ReportVisible`. The service's implementation is `AnimationSystem::ReportVisible` in `Strata/src/Strata/Animation/AnimationSystem.cpp`, which writes `SeenUpdate`. Search for `SeenUpdate`: `AnimationSystem::PrepareStep` reads it in the next update and sets `record.Evaluate`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationComponents.h`: `AnimatorCullingMode`.
- `Strata/src/Strata/Animation/AnimationSystem.cpp`: `PrepareStep`, `StepRecord`, `ReportVisible`, `OnPausedUpdate`, `GetJointTransform`.
- `Strata/src/Strata/Animation/AnimatorInstance.cpp`: `AnimationReach::Compute`, `AnimatorInstance::GetReach`.
- `Strata/src/Strata/Scene/SceneServices.h`: `ISkinningPoses`, `SkeletonPose`.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `ReportVisibleAnimators`; the count `StalePoses`.
- `StrataTests/src/Animation/AnimationSystemTests.cpp` and `StrataTests/src/Renderer/GPUAnimationTests.cpp`.

## Further reading

- Unity manual, Animator component, the Culling Mode property. Beginner.
- Unreal Engine documentation, Animation Optimization, the update rate optimization. Intermediate.
