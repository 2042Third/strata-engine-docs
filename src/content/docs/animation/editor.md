---
id: animation/editor
title: "Edit-mode poses and previews"
description: "How the editor draws animated characters before Play, with poses that never write the scene."
kind: internals
size: M
tracks: [E]
needs: [animation/system, animation/skinning]
time: 55
learn:
  - id: edit-mode-poses
    text: explain what draws a skinned character in the editor before Play and why editing it writes nothing to the scene
  - id: shared-poses
    text: compute how many poses the preview makes for a set of animators, and when it makes them again
  - id: provider-versions
    text: explain why the render scene computes every palette again when the poses provider changes
  - id: render-transforms
    text: trace how an attachment reaches its joint in the edited scene without a change to the scene
since: 0.3.0
status: final
---

You open a scene with a character in the editor and the character stands up, arms at its sides, as it will when the game starts. Nothing plays, yet a pose appears.

The :term[renderer]{id=renderer} asks one object, the poses provider, for the joint poses of each skinned mesh. `AnimationPreview` is that provider in scenes that do not play: the edited scene, and the scenes that thumbnails render. It shows each animator's :term[rest pose]{id=rest-pose}, or the first frame of what the animator plays on start, and it answers requests to show a given state, clip and time. It never writes the scene, and it does not run the game's animation rules: no events, no :term[root motion]{id=root-motion}, no transitions.

## The problem and how engines solve it

A skinned mesh is stored in its own space, the space it was modeled in. Its vertices follow joints, and the :term[renderer]{id=renderer} turns joint poses into a palette of matrices, as the [skinning page](../animation/skinning.md) explains. With no poses at all, the renderer draws the mesh as stored: the :term[bind pose]{id=bind-pose}.

Many files store a character lying down. An artist's tool that works with Z up exports a standing character whose head sits on the Z axis. Engines that work with Y up fix this with a joint above the skin, often named `Armature`, which turns the character a quarter turn.

Take a head at (0, 0, 1.8) in mesh space. The `Armature` turns Z into Y, so the head belongs at (0, 1.8, 0). Without a provider, the renderer never applies that turn, and the character lies on the floor with its head at 1.8 metres along Z.

```mermaid caption="A character exported with Z up, drawn without and with the joints above its skin." alt="Two outcomes. Without a provider the head stays at 0, 0, 1.8 and the character lies on the floor. With a provider the top joint turns Z into Y and the head stands at 0, 1.8, 0."
flowchart LR
	A["Mesh space: head at 0, 0, 1.8"] --> B{"Poses provider?"}
	B -- no --> C["Bind pose: the character lies down"]
	B -- yes --> D["Armature turns Z into Y: head at 0, 1.8, 0"]
```

A game in Play mode has no such problem: its Animation system, taught on the [system page](../animation/system.md), poses every animator each frame. The editor draws a scene that does not play, so no such system runs there. Engines meet this in three ways.

- Run the whole animation system in the editor. Characters then move while you edit. The system writes transforms and fires events, so the saved scene could change, and every edit would compete with moving data.
- Leave the bind pose. This costs nothing, but the character you edit differs from the character you play, and you place a lying character on the floor.
- Use a separate provider with a narrow job. It shows a still pose, and it keeps its results beside the scene, never in it. This is Strata's choice.

The third way costs a second implementation of "which pose does this animator show". Strata keeps that cost small: the preview calls the same code that play mode uses, as the sections below show.

## The map

The renderer reads poses through one :term[scene service]{id=scene-service}, `ISkinningPoses`. A scene has exactly one provider, and which one depends on whether the scene plays.

```mermaid caption="Which provider answers for which scene, and what the render scene does when the provider changes." alt="The edited scene and the thumbnail scenes use the preview provider. The play copy uses the animation system provider. Both answer the render scene, which computes every palette again when its provider changes."
flowchart TD
	E["Edited scene"] --> P["AnimationPreview"]
	T["Thumbnail scenes"] --> P
	C["Play copy"] --> S["AnimationSystem"]
	P --> I(["ISkinningPoses"])
	S --> I
	I --> R["RenderScene: palettes"]
```

The files are small in number. `Strata/src/Strata/Animation/AnimationPreview.h` and `AnimationPreview.cpp` hold the provider. `Strata/src/Strata/Animation/RestPose.cpp` holds `ComputeRestPose`, shared with play mode. `Strata/src/Strata/Animation/AnimationEditPose.h` names the two edit poses.

In the editor, `EditorContext` creates the preview for each edited scene, and `ThumbnailCache` creates one for each scene it renders. Only the :term[main thread]{id=main-thread} touches the preview.

A **pose preview** is a request, made through the `animation.preview` command, to show one animator at a state, a clip and a time without playing the scene.

An **edit pose** is what an animator shows in a scene that does not play when no request poses it: its skeleton's rest pose, or the first frame of what it plays on start. The viewport setting `editPose` chooses between them. The value `"rest"` gives the rest pose and `"clipStart"` gives the first frame. The Scene view's camera chip offers both in a menu under "Characters while editing", labeled **Rest pose** and **First frame of their animation**.

::figure{id=edit-poses}

The picture shows two copies of the robot. The left copy is at rest: its arms hang as the skeleton holds them. The right copy plays a clip that begins crouched, and a pose preview at time 0 shows that clip's first frame. That frame is what `clipStart` would show: the pose the game shows before its first update. The sample's own default state, `Idle`, begins close to the rest pose, so the two settings differ little for the sample's robot and much for a clip that begins in another pose.

### Simulate has no provider

The preview serves only the edited scene. Play mode copies that scene and runs the copy. In Play mode the copy runs the Animation system, which offers its own provider. Simulate mode is different: the Animation system is registered with `RunsInSimulateMode` set to false, so the Simulate copy has no provider at all.

Its viewport draws the copy, which has no preview, so its skinned meshes show the bind pose. This follows from reading the code; the [play mode page](../editor/play-mode.md) explains the two modes.

### Versions belong to their provider

Each provider counts its pose changes in a version, and the :term[render scene]{id=render-scene} compares versions to skip work. Two providers count on their own, so the edit preview and a play copy's system can both say "version 12" about different poses. The render scene therefore remembers which provider it last read. When the provider differs, it ignores the version comparison and computes every palette again. That happens when you press Play, and again when you stop.

## The contract

Callers of the preview, and the code around it, follow these rules.

1. The preview changes no scene data. Poses, bounds and attachment placements all live in the preview's own memory. Reason: the edited scene is the document you save, and a pose that leaked into it would be saved by accident.
2. A request always wins over the edit pose. When you clear it, the edit pose shows again.
3. A pose version belongs to its provider. Reason: the section above.
4. The preview runs on the main thread, once per frame before rendering: `AnimationPreview::Update`. Reason: the scene and its signals belong to that thread. With no request open, an update that changes nothing adds nothing to the preview's counters.
5. A scene gets the preview only when it has no other provider. The :term[constructor]{id=constructor} offers the service, and `IsRegistered` says whether the scene accepted.

:::rule
Other :term[engine modules]{id=engine-module} reach animation only through scene services such as `ISkinningPoses`. The renderer never includes the Animation module, so it cannot ask `AnimationPreview` anything directly. See the layering rules in the [Core layers page](../core/layers-registries.md).
:::

:::why
The preview calls the play-mode evaluation instead of a copy of it. Two evaluations would drift: a fix to one would leave the other wrong, and the character in the editor would differ from the character in the game. The cost is that the preview depends on the animator's types, which is acceptable inside one module.
:::

## A toy version

The toy models a skeleton as a chain: each joint sits on its parent at a rest height. The provider keeps one pose for each skeleton and makes it again only when the skeleton's revision grows, as it does after an import. The program asks for the same pose 500 times, then changes the skeleton.

```cpp sketch="animation-editor-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <unordered_map>
#include <vector>

// A skeleton is a chain: each joint sits on its parent, offset by its rest height.
struct Skeleton
{
	std::vector<int> Parents;
	std::vector<float> RestHeights;
	uint64_t Revision = 1; // Grows when the file is imported again
};

struct CachedPose
{
	std::vector<float> Heights; // Height of every joint in the animator's space
	uint64_t Revision = 0;      // The skeleton's revision it was computed from
};

class RestPoseProvider
{
public:
	// Every animator on the same skeleton gets the same pose: computed once, again only after an import.
	const std::vector<float>& GetPose(int skeletonId, const Skeleton& skeleton)
	{
		CachedPose& cached = m_Cache[skeletonId];
		if (cached.Revision != skeleton.Revision)
		{
			cached.Heights.assign(skeleton.Parents.size(), 0.0f);
			for (size_t joint = 0; joint < skeleton.Parents.size(); joint++)
			{
				const int parent = skeleton.Parents[joint];
				const float base = parent < 0 ? 0.0f : cached.Heights[static_cast<size_t>(parent)];
				cached.Heights[joint] = base + skeleton.RestHeights[joint];
			}
			cached.Revision = skeleton.Revision;
			m_Computed++;
		}
		return cached.Heights;
	}

	int GetComputed() const { return m_Computed; }

private:
	std::unordered_map<int, CachedPose> m_Cache;
	int m_Computed = 0;
};

int main()
{
	Skeleton robot;
	robot.Parents = { -1, 0, 1 };
	robot.RestHeights = { 0.5f, 0.5f, 0.75f };

	RestPoseProvider provider;
	for (int animator = 0; animator < 500; animator++)
		provider.GetPose(7, robot);
	std::printf("500 animators, %d pose computed, head at %.2f\n", provider.GetComputed(), provider.GetPose(7, robot)[2]);

	robot.RestHeights[2] = 1.0f;
	robot.Revision++;
	provider.GetPose(7, robot);
	provider.GetPose(7, robot);
	std::printf("after an import, %d poses computed, head at %.2f\n", provider.GetComputed(), provider.GetPose(7, robot)[2]);
	return 0;
}
```

```text output-of="animation-editor-toy.cpp"
500 animators, 1 pose computed, head at 1.75
after an import, 2 poses computed, head at 2.00
```

1. **Line 27:** the cache holds the skeleton's revision, so a stale pose is found by one comparison.
2. **Lines 30–36:** a joint's height is its parent's height plus its own rest height, which works because parents come first.
3. **Line 37:** the counter grows only when a pose is built, the number the program prints.
4. **Line 56:** 500 animators ask, and only the first builds anything.
5. **Line 61:** an import raises the revision, so the next question builds again.

The 500 animators share one pose, so the toy computes one. After the import the revision differs, and the next question computes a second pose; later questions use it again. The real provider adds three things the toy omits: it waits for assets that load in the background, it finds changed animators through signals, and it keeps requests.

## The real code

Data flows in four steps: an animator is noticed, its key is made, the pose is computed, and the palettes follow.

### The same evaluation as play

`EvaluateAnimator` builds an `AnimatorInstance` from the same assets that play mode uses and advances it by the requested time. One setting differs from play: transitions are off, so the preview holds the pose it shows.

```cpp src="Strata/src/Strata/Animation/AnimationPreview.cpp#L55-L79" from="AnimatorInstance instance;" to="return instance.Advance(time, assets, settings, events) && instance.Evaluate(assets, settings, scratch, outPose);" symbol="EvaluateAnimator"
AnimatorInstance instance;
if (state != AnimatorInstance::c_ClipState)
{
	stateClips[state] = bound;
	assets.StateClips = stateClips;
	instance.Play(assets, controller->GetStates()[state].Name);
}
else if (playedClip.IsValid())
{
	assets.StateClips = stateClips;
	assets.PlayedClip = bound;
	instance.PlayClip(playedClip);
}
else
{
	stateClips[0] = bound;
	assets.StateClips = stateClips;
	instance.Start();
}
AnimatorSettings settings;
settings.Loop = loop;
settings.ApplyRootMotion = rootMotion;
settings.Transitions = false; // The preview holds what it shows
std::vector<AnimatorFiredEvent> events;
return instance.Advance(time, assets, settings, events) && instance.Evaluate(assets, settings, scratch, outPose);
```

1. **Line 60:** a named state plays by its name, as the controller starts it.
2. **Line 66:** a clip asked for by handle plays outside any controller.
3. **Line 72:** with neither, `Start` begins what the animator plays on start.
4. **Line 77:** transitions are off, so no fade changes the pose.
5. **Line 79:** the pose is the matrices at the asked time.

Look at the three branches. A named state plays through `Play`, a clip by handle through `PlayClip`, and neither through `Start`, which is how play mode begins. After that, one `Advance` and one `Evaluate` produce the joint matrices.

### One pose for many animators

The shared pose has a key. Two animators with the same key show the same pose, so the preview computes it once.

```cpp src="Strata/src/Strata/Animation/AnimationPreview.cpp#L266-L304"
AnimationPreview::EditPoseKey AnimationPreview::MakeEditPoseKey(const AnimatorComponent& component) const
{
	EditPoseKey key;
	key.Skeleton = component.Skeleton;
	if (m_Specification.EditPose == AnimationEditPose::ClipStart && (component.Controller.IsValid() || component.Clip.IsValid()))
	{
		// What it plays on start: its controller's default state, or (no controller, or one that does not load) its clip.
		key.Controller = component.Controller;
		key.Clip = component.Clip;
		key.RootMotion = component.ApplyRootMotion;
	}
	return key;
}

void AnimationPreview::ExamineAnimator(entt::entity handle)
{
	m_Stats.AnimatorsExamined++;
	const entt::registry& registry = m_Scene.GetRegistry();
	const AnimatorComponent* component = registry.valid(handle) ? registry.try_get<AnimatorComponent>(handle) : nullptr;
	const EditPoseKey key = component ? MakeEditPoseKey(*component) : EditPoseKey();
	auto it = m_RestAnimators.find(handle);
	const EditPoseKey previous = it != m_RestAnimators.end() ? it->second : EditPoseKey();
	if (previous == key)
		return;
	// What the animator shows changes (a request still wins over it).
	m_PosesVersion++;
	if (previous.Skeleton.IsValid())
	{
		m_RestAnimators.erase(it);
		ReleaseRestPose(previous);
	}
	if (!key.Skeleton.IsValid())
		return;
	m_RestAnimators.emplace(handle, key);
	auto [pose, added] = m_RestPoses.try_emplace(key);
	pose->second.Animators++;
	if (added)
		m_WaitingRestPoses++; // A new entry starts out waiting for its skeleton
}
```

1. **Line 270:** only the clip-start mode adds the controller, the clip and root motion to the key.
2. **Line 288:** an animator whose key did not change costs one comparison.
3. **Line 291:** a change of key grows the version, so palettes follow.
4. **Line 303:** a new key starts out waiting for its skeleton.

The key holds the skeleton and, only in the clip-start mode, the controller, the clip and the root motion flag. In rest mode the other three stay empty, so every animator on a skeleton shares one key. `ExamineAnimator` compares the new key to the animator's previous key and does nothing when they match. The preview calls it only for animators whose component signalled a change: added, changed or about to be destroyed. A scene of 1,000 animators that nobody touches costs nothing per frame.

The preview computes a pose when the key's assets have arrived. A new import changes an asset's :term[source revision]{id=source-revision}, and only that sets the pose to wait again. A pose records the revision of every asset it used: the skeleton, the controller and the clip. A new import of the skeleton alone also sets a pose with a clip to wait. In contrast, an :term[eviction]{id=eviction} from memory keeps the matrices.

`AnimationPreviewStats` counts the poses computed, the asset requests and the animators examined, so a test can show that idle updates add nothing.

At the first run a skeleton has no pose yet. The animator draws the bind pose until the skeleton loads, then the pose appears and the version grows. A pose computed from a clip also keeps the joint names, because attachments need them.

### Posing with no request

When no clip takes part, the pose comes from `ComputeRestPose`. With a clip or controller, it comes from `EvaluateAnimator` at time 0. Play mode computes the rest pose with the same function, so edit mode and play mode cannot drift apart.

### Render transforms

A **render transform** is a :term[world transform]{id=world-transform} that a poses provider asks the renderer to draw an entity at, without changing the scene. Attachments need it. A sword attached to a hand joint moves with the hand in play, because the Animation system writes its transform. The preview may not write, so it hands the renderer a list instead.

```cpp src="Strata/src/Strata/Animation/AnimationPreview.cpp#L444-L472" from="const RenderInputs inputs" to="const glm::mat4 change = *world * glm::inverse(sceneWorld);" symbol="AnimationPreview::UpdateRenderTransforms"
const RenderInputs inputs { m_PosesVersion, m_Scene.GetTransformsVersion(), m_Scene.GetHierarchyVersion(), m_RequestsRevision,
	m_AttachmentsRevision };
if (inputs == m_RenderInputs)
	return;
m_RenderInputs = inputs;
std::vector<RenderTransform> transforms;
bool posed = false;
for (const auto& [handle, entry] : m_Entries)
	posed = posed || entry.Version != 0;
for (const auto& [key, pose] : m_RestPoses)
	posed = posed || (pose.Version != 0 && !pose.ClipJoints.empty());
if (posed)
{
	const entt::registry& registry = m_Scene.GetRegistry();
	std::vector<Entity> stack;
	for (const auto [handle, attachment] : registry.view<AttachToJointComponent>().each())
	{
		const Entity entity(handle, &m_Scene);
		if (!m_Scene.IsActiveInHierarchy(entity))
			continue;
		const std::optional<glm::mat4> world = GetAttachmentWorld(entity, attachment);
		if (!world)
			continue;
		const glm::mat4 sceneWorld = m_Scene.GetWorldTransform(entity);
		if (!(std::abs(glm::determinant(glm::mat3(sceneWorld))) > Scene::c_MinInvertibleDeterminant))
			continue;
		// The attachment and what is under it move together: by the change from where the scene has the attachment to
		// its joint. An attachment below it that is placed itself starts its own subtree.
		const glm::mat4 change = *world * glm::inverse(sceneWorld);
```

1. **Line 446:** unchanged inputs end the function at once.
2. **Lines 453–454:** nothing is placed until some pose exists.
3. **Line 468:** a transform that cannot be inverted is skipped.
4. **Line 472:** `change` carries the attachment from the scene's place to its joint.

The function first checks five version numbers and returns when none changed. Then, for each active attachment whose animator has a pose, it computes where the joint puts it, `world`, and the matrix that moves the attachment from where the scene has it to there, `change`. An attachment whose transform cannot be inverted is skipped.

```cpp src="Strata/src/Strata/Animation/AnimationPreview.cpp#L473-L487" from="stack.assign(1, entity);" to="stack.push_back(child);" symbol="AnimationPreview::UpdateRenderTransforms"
stack.assign(1, entity);
while (!stack.empty())
{
	const Entity current = stack.back();
	stack.pop_back();
	if (current != entity)
	{
		const AttachToJointComponent* inner = current.TryGetComponent<AttachToJointComponent>();
		if (inner && m_Scene.IsActiveInHierarchy(current) && GetAttachmentWorld(current, *inner))
			continue;
	}
	if (current.HasComponent<MeshRendererComponent>())
		transforms.push_back(RenderTransform { current.GetHandle(), current == entity ? *world : change * m_Scene.GetWorldTransform(current) });
	for (const Entity child : current.GetChildren())
		stack.push_back(child);
```

1. **Line 481:** an inner attachment that has its own pose starts its own :term[subtree]{id=subtree}.
2. **Line 485:** each mesh renderer gets its new world matrix, and the attachment itself the joint's.
3. **Line 487:** the walk continues down the children.

The loop walks the :term[subtree]{id=subtree} below the attachment. Each mesh renderer there moves by the same `change`, so a sword's blade follows the hand. An inner attachment that has its own pose starts a separate subtree. The result becomes `GetRenderTransforms`, with a version that changes only when the list differs :term[byte]{id=byte} for byte.

### Palettes after a change of provider

In the render scene, the check that handles a changed provider is short.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1378-L1383"
const bool providerChanged = poses != m_PosesProvider;
m_PosesProvider = poses;
m_PosesVersion = posesVersion;
m_SkinTransformsVersion = transformsVersion;
m_SkinHierarchyVersion = hierarchyVersion;
m_SkinDrawnVersion = drawnVersion;
```

The first line sets a flag when the provider is not the one read last. Later in the same function, a skin whose version matches skips its work only when `providerChanged` is false.

### Tools see the pose too

The editor's tools need the size a character has in its pose, not in its bind pose. `SceneBounds::GetPosedMeshBounds` measures a skinned mesh through the provider's pose. Framing, focus, drop to ground and placement all call it, so a character that stands on its feet is framed as standing. While the skeleton still loads, the function asks for it and reports which skeleton it waits for, so the caller measures again later. The [placement page](../editor/placement.md) uses this for its ghost.

Thumbnails create a preview of the same kind for each scene they render, with rest poses on, and wait for it like they wait for meshes. The [thumbnails page](../editor/thumbnails.md) explains the rest.

## The editor's commands for animation

Four commands form the editor's application programming interface (API) for this part. Each runs as one line with `StrataCLI`; the [commands page](../make/commands.md) explains the line, and [Commands in the editor](../editor/commands.md) explains kinds and schemas.

`animation.createController` writes a `.stanimator` from :term[JSON]{id=json} sections: parameters, states, a default state and transitions. The path is relative to the asset folder.

```sh
./StrataCLI call animation.createController '{ "path": "Animations/Hero.stanimator", "states": [ { "Name": "Idle", "Clip": null } ] }'
```

`animation.setController` replaces the sections you give and keeps the others, as one undo step through `AssetEdit::SetControllerData`. Animators and previews use the new controller at once.

```sh
./StrataCLI call animation.setController '{ "controller": "Animations/Hero.stanimator", "defaultState": "Idle" }'
```

`animation.info` is a Query: it describes a model, a skeleton, a clip or a controller, or the state and parameters of a live animator. `animation.preview` has kind Session and may defer. It poses an animator of the edited scene and answers once that pose shows. It refuses while the game plays, with the message that `play.stop` comes first. The [deferred commands page](../editor/deferred-commands.md) explains why the answer waits.

```sh
./StrataCLI call animation.preview '{ "entity": "<robot id>", "state": "Run", "time": 0.3 }'
```

While a preview shows, the viewport names it in a chip, so nobody mistakes the pose for scene data. A click on the chip stops the preview. The [animation how-to](../make/animation.md) shows the Asset tab's views and the Inspector's live state.

::figure{id=preview-chip}

::figure{id=preview-chip crop=chip}

:::example
A scene holds 500 robots, each with an Animator on the same skeleton and the same clip, and the editor shows the rest pose. Opening the scene marks all 500 animators dirty. The first update examines 500 animators and makes one key. The key waits for the skeleton, then the preview computes one pose: the count of poses computed is 1.

Switching the camera chip to **First frame of their animation** examines the 500 once more. Each gets the key with its controller or clip. If all share one clip, the count rises to 2. Importing the skeleton again makes it 3. Frames in between add nothing to any of the three counters.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Run the animation system in the editor | Engines with an always-live viewport | One code path for edit and play | Moving data while editing, scene writes to undo, constant cost |
| Draw the bind pose | Simple viewers | No provider code | Lying characters, wrong bounds, wrong placement |
| Bake the pose into the scene | Tools that apply the rest pose once | No provider at all at draw time | A scene edit that you did not make, and a file that differs from the source |

The sources for these appear in the further reading.

## How it is tested

The suite `Animation.Preview` in `StrataTests/src/Animation/AnimationSystemTests.cpp` holds five cases. They check that a request is posed once its own pose is computed, while the earlier pose shows meanwhile. They check that rest poses are what animators evaluate with nothing playing, and that they come once per skeleton and again only after a new import. A request beats the rest pose, and the clip-start edit pose shows the first frame of what animators play on start. One case builds 500 animators on one skeleton and one clip and checks the count of poses computed.

The :term[graphics processing unit]{id=gpu} (GPU) case "Skinned models stand in their rest pose in edited scenes as they do in play before their first animation, on both paths" lives in `StrataTests/src/Renderer/GPUAnimationTests.cpp`. It renders two arm models, one with Z up, on the :term[central processing unit]{id=processor} (CPU) path and the GPU-driven path.

`StrataTests/src/Editor/EditorAnimationTests.cpp` runs the four commands, including a preview that leaves the scene unchanged. Run one suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Animation.Preview`. The GPU case needs a graphics device.

## Changing it safely

- Add a new input to a pose, such as a setting that changes what an animator shows, to `EditPoseKey`. A missing field makes two different poses share one cache entry.
- A new thing the preview computes needs a version, and the render scene needs to read it. Changing a pose without growing `m_PosesVersion` leaves stale palettes.
- Never write a scene component from the preview. Where the renderer needs another transform, use a render transform.
- Keep the idle cost at zero: no walk over all animators per frame. Extend the `AnimationPreviewStats` test when you add a loop.
- Run `Animation.Preview`, the editor animation tests and the GPU case above before you commit.

## Summary

- A scene that does not play has no Animation system, and `AnimationPreview` supplies poses, never writing the scene.
- Animators that share a skeleton (and, in clip-start mode, a controller and clip) share one computed pose, made again only after a new import.
- Each provider counts its own versions, so the render scene computes all palettes again when the provider changes.
- Attachments are drawn through render transforms that the preview owns, so the scene stays unchanged.

## Check yourself

1. A character exported with Z up shows lying in a scene that has no provider. What fixes it in the edited scene?

   - A. The preview moves the `Armature` node in the scene.
   - B. The preview supplies the rest pose, which includes the `Armature` joint's turn.
   - C. The editor changes the mesh in the file.

   :::answer{tests="edit-mode-poses"}
   B. The `Armature` is a joint of the skeleton, so the rest pose contains its turn. A is wrong because the preview never writes the scene. C is wrong because no file or mesh changes.
   :::

2. A scene has 300 animators: 200 share skeleton 1 with no clip, 100 share skeleton 2 with no clip. The edit pose is rest. How many poses does the preview compute, and how many after you import skeleton 2 again?

   :::answer{tests="shared-poses"}
   Two poses at first, one per skeleton. The new import changes skeleton 2's source revision, so only its pose is computed again: three in total.
   :::

3. Why does the render scene compute palettes again when you press Play, even when the pose version numbers happen to match?

   :::answer{tests="provider-versions"}
   The numbers belong to different providers. The preview and the play copy's system count on their own, so "version 12" can mean two poses. The render scene remembers the provider and treats any change as new data.
   :::

4. A sword is attached to a hand joint in the edited scene. Where is its transform stored while you preview a pose?

   :::answer{tests="render-transforms"}
   The scene keeps the sword where it was. The preview keeps a render transform, a world matrix it computed from the hand's pose, and the renderer draws the sword there.
   :::

## Exercises

1. **Basic.** Run the sketch below. It counts the poses for six animators in rest mode and in clip-start mode. Say why the numbers differ.

   :::answer[Worked solution]{tests="shared-poses" solution="sketches/animation-editor-keys.cpp"}
   The rest key holds the skeleton only, so the six animators make two keys. The clip-start key adds the clip, so they make three.

   ```cpp sketch="animation-editor-keys.cpp"
   #include <cstdio>
   #include <map>
   #include <utility>
   #include <vector>

   // An animator names its skeleton and the clip it plays on start (0: none).
   struct Animator
   {
   	int Skeleton = 0;
   	int Clip = 0;
   };

   int main()
   {
   	const std::vector<Animator> animators = { { 1, 0 }, { 1, 0 }, { 1, 5 }, { 1, 5 }, { 1, 5 }, { 2, 5 } };

   	// The rest pose depends on the skeleton alone.
   	std::map<int, int> restPoses;
   	for (const Animator& animator : animators)
   		restPoses[animator.Skeleton]++;

   	// The clip-start pose depends on the skeleton and the clip.
   	std::map<std::pair<int, int>, int> clipStartPoses;
   	for (const Animator& animator : animators)
   		clipStartPoses[{ animator.Skeleton, animator.Clip }]++;

   	std::printf("rest: %zu poses for %zu animators\n", restPoses.size(), animators.size());
   	std::printf("clip start: %zu poses for %zu animators\n", clipStartPoses.size(), animators.size());
   	return 0;
   }
   ```

   ```text output-of="animation-editor-keys.cpp"
   rest: 2 poses for 6 animators
   clip start: 3 poses for 6 animators
   ```

   1. **Line 20:** the rest key is the skeleton alone.
   2. **Line 25:** the clip-start key is the pair of skeleton and clip.
   3. **Line 28:** three keys, because pairs (1, 0), (1, 5) and (2, 5) occur.
   :::

2. **Medium.** You add a field `StartTime` to `AnimatorComponent`: the clip starts that many seconds in, so the first frame differs. What must you change in the preview, and what breaks if you forget?

   :::answer[Worked solution]{tests="edit-mode-poses"}
   Add the field to `EditPoseKey` and to `MakeEditPoseKey`, and pass it to `EvaluateAnimator` in place of time 0. If you forget the key, two animators that differ only in this field share a key and both show the first one's pose. The error appears only when both exist in one scene.
   :::

3. **Hard.** Trace it yourself. Run the test case "The clip-start edit pose shows the first frame of what animators play on start, once per skeleton and clip" in a source build. Put a breakpoint on the call of `EvaluateAnimator` in `UpdateRestPoses`, and count the hits for the 500 animators that share a skeleton and a clip.

   :::answer[Worked solution]{tests="shared-poses"}
   The call stands in `AnimationPreview::UpdateRestPoses` in `Strata/src/Strata/Animation/AnimationPreview.cpp`. The 500 animators share one key, so they cause one hit. The controlled animator causes a second hit. The animator with no clip uses `ComputeRestPose`, so the test sees three poses in all.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Animation/AnimationPreview.h` and `AnimationPreview.cpp`: the provider, its requests, edit poses and render transforms.
- `Strata/src/Strata/Animation/AnimationEditPose.h` and `RestPose.cpp`: the two edit poses and `ComputeRestPose`.
- `Strata/src/Strata/Renderer/RenderScene.cpp`: palettes and provider changes.
- `StrataEditor/src/Editor/EditorContext.cpp`: `CreateAnimationPreview` and the per-frame update.
- `StrataEditor/src/Editor/SceneBounds.cpp` and `EditorPlacement.cpp`: :term[posed bounds]{id=posed-bounds}.
- `StrataEditor/src/Editor/EditorAnimationCommands.cpp`: the four commands. `viewport.setSettings` takes `editPose`.
- Tests: `Animation.Preview`, `StrataTests/src/Editor/EditorAnimationTests.cpp`, the GPU case in `GPUAnimationTests.cpp`.

## Further reading

- "Skeletal animation" chapters of game engine textbooks: how bind poses and rest poses relate (intermediate).
- The glTF 2.0 specification, skins: how files store joints and inverse bind matrices (advanced).
