---
id: audio/scene-system
title: "The Audio scene system"
description: "How the Audio scene system turns audio components into sources, follows them each frame, picks the listener, pauses with the scene and plays one-shots."
kind: internals
size: L
tracks: [E]
needs: [audio/spatial, world/systems, physics/bodies-colliders]
time: 90
learn:
  - id: edit-heard
    text: explain when an edit to an Audio Source is heard, and why plain writes need no change signal
  - id: clip-states
    text: trace a source's clip through its four states, including a reload and a new clip
  - id: listener-choice
    text: find which listener a scene uses and what happens with several scenes
  - id: one-shot-limits
    text: explain why a one-shot waits, plays or is dropped
  - id: pause-rules
    text: predict what a paused scene does with edits and with sounds asked for meanwhile
since: 0.3.0
status: final
---

A running game must turn the audio components in its scene into sound that follows the scene. The "Audio" :term[scene system]{id=scene-system} does this work. It makes one voice for each entity with an Audio Source, keeps the voice in step with the component every frame, chooses the listener, pauses with the scene and plays the scene's :term[one-shot]{id=one-shot} sounds. It runs in Play mode only, never in Simulate mode. It does not mix samples, place sounds in space or decode files: the mixer, the spatial rules and the clip assets live in other pages.

## The problem and how engines solve it

Picture a scene with a radio on a table, a door that creaks and a coin that the player collects. The scene knows three entities. The mixer, the part of the engine that adds sounds into the stream sent to the speakers, knows nothing about entities. It knows voices: a clip, a volume, a pitch and a position.

Someone must connect the two worlds, every frame, for as long as the game plays. That connection is the job of this page.

The first problem is memory. When the radio entity appears, the system must create its voice. When the entity changes, the system must change the same voice and not create a second one. So the system keeps one **source record** for each entity: the voice, the component values that the voice last received, and a few flags about what the game asked for. A map from entity to record is all the structure this needs.

The second problem is how the record learns about changes. A person drags the Volume slider in the Inspector, or a script writes `Volume = 0.5`. Engines solve this in two ways. In the event-driven way, each writer announces its change, and the system reacts to the announcement. The cost is trust: one writer that forgets to announce leaves the sound unchanged, and nothing reports the mistake.

In the comparing way, the system reads every component each frame and compares it with the values it applied last. Take 500 sources with 9 fields each: that is 4,500 comparisons per frame, a few microseconds. In return, every write is heard, whoever made it. Strata chooses the comparing way for audio.

The third problem is time. A clip is an asset, and an asset may still be loading when the entity wakes up. A frame cannot wait for a file: at 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, and a large sound file takes longer to read. So the record must hold a state for "the clip is not here yet", remember what the game asked for in the meantime, and act when the clip arrives. The page [Loading assets](../assets/loading.md) teaches the asset side of this.

The fourth problem is the pause. A game that pauses must silence its sounds and resume them where they stopped, and it must handle the sounds that the game asks for while it is paused. A last kind of sound has no entity at all: a coin pickup, a footstep, a gunshot. The scene needs fire-and-forget sounds that it owns, with a limit on how many play at once and a limit on how long they wait for a slow clip.

## The map

The system is one class, `AudioSystem` in `Strata/src/Strata/Audio/AudioSystem.cpp`, and a thin module around the mixer. To see who runs when, follow one frame of a running game.

```mermaid caption="One frame of a running game." alt="A top to bottom flow. The input stage reads the window and the input actions. The scene's systems run next: scripts, animation and physics, then the Audio system in the late update. The Audio module's update comes after the scene and advances the mixer."
flowchart TD
	A[Input stage] --> B[Scene systems: Scripting, Animation, Physics]
	B --> C[Audio system in OnLateUpdate]
	C --> D[Audio module update: AudioEngine::Update]
```

The Audio system declares that it runs after "Scripting", "Animation" and "Physics", but only when those systems exist: a game without physics still has sound. The declaration is a soft order. When all four exist, the audio code sees the transforms that scripts, animation and physics produced in the same frame, so a sound never lags a frame behind its entity. The scene's own update (`Scene::OnUpdateRuntime`) calls the late update of every system after the :term[fixed steps]{id=fixed-step}.

The module's update comes afterwards and belongs to the program, not to the scene. It keeps the mixer itself running: when the mixer runs on its silent :term[null device]{id=null-device}, the update advances it by the :term[frame time]{id=frame-time}, so that sounds still end.

Inside the Audio system, each update does four jobs in a fixed order, and the record's life follows from them.

| Order | Job | What it reads |
| --- | --- | --- |
| 1 | Update the sources | Each active Audio Source component |
| 2 | Process asset changes | The :term[asset manager's]{id=asset-manager} :term[content version]{id=content-version} |
| 3 | Update the listener | Listener components, else the primary camera |
| 4 | Update the one-shots | The scene's own list of sounds |

The sources go first on purpose. Records of removed components and of destroyed or inactive entities leave before anything else looks at them.

A record also has a state machine for its clip, with four states. A record with no clip handle is in `NoClip`. A record whose clip is loading is Waiting. Once the source holds the clip, the record is Ready. A clip that cannot play (unknown handle, failed load, not an audio clip) puts the record in Unavailable, with one warning.

```mermaid caption="The four clip states of a source record, and the edges between them." alt="A state diagram. No clip leads to waiting when a clip handle is set. Waiting leads to ready when the clip loads, or to unavailable when it cannot play. Unavailable and ready return to waiting when the asset or the handle changes."
flowchart LR
	N[NoClip] -->|handle set| W[Waiting]
	W -->|clip loaded| R[Ready]
	W -->|cannot play, warn once| U[Unavailable]
	U -->|asset changed| W
	R -->|handle changed| W
	R -->|reload replaces clip| R
	R -->|handle cleared| N
	W -->|handle cleared| N
```

Next to the state, the record keeps three more facts. `PlayRequested` says that a start waits for the clip or for the end of a pause. `PausedByScene` says that the scene halted a source that was playing. `PendingSeek` holds a position asked for before the clip arrived. The comparison with the last applied values lives in the field `Applied`, and `SeenUpdate` marks the last update that found the component.

## The contract

What may a caller assume, and what must a caller do? Five rules hold, each with its reason.

First, the system runs in Play mode only. Like scripts, it does not exist in Simulate mode. The editor's Play and Simulate modes are explained in [Play mode](../editor/play-mode.md).

Second, game code plays sound through `AudioSystem`, never through `AudioEngine` directly. A script uses the software development kit (SDK) classes `AudioSource` and `Audio`. The reason: only the system knows the pause, the record and the listener, and a voice made behind its back would not pause, stop or follow anything.

:::rule
The engine's guide sends all game sound through the scene's audio system, and scripts through the SDK. Nothing starts a voice on the mixer itself. A voice made that way escapes the scene's pause and its stop, so it keeps sounding after the game ends. See [Scene systems](../world/systems.md).
:::

Third, assets go by handle and never block. The system stores `AssetHandle` values and asks the asset manager for the clip each time it needs it, treating "not loaded yet" as a normal answer. A clip that is loading is not an error. Fourth, everything runs on the :term[main thread]{id=main-thread}, like the scene it serves.

Fifth comes a rule with an exception. The guide says that code which works for a scene reaches assets through `Scene::GetAssetManager()`, never through the static functions of `AssetManager`. `AudioSystem` is older than that rule.

At the pin it still reads `AssetManager::GetActive()` in five places: the :term[constructor]{id=constructor}, `ResolveClip`, `RefreshClip`, `ProcessAssetChanges` and `TryStartOneShot`. Only `DropOneShot`, which prints a clip's path in a warning, goes through the scene. The excerpts below are therefore no model for that line. New code takes the scene's manager.

Two guarantees complete the contract. The system works whether or not the mixer started: without output, sources are silent and never playing, and the gameplay calls return false. And the system registers the :term[scene service]{id=scene-service} `IAudioPlayback` while it exists, so that other modules, scripts above all, reach the gameplay calls without including the Audio module. [Scene systems](../world/systems.md) teaches scene services in general.

### The components as the Inspector shows them

Two components feed the system. They are registered with ranges, which the Inspector turns into slider controls and limits.

| Property | Default | Range in the Inspector | Meaning |
| --- | --- | --- | --- |
| `Clip` | none | an audio clip asset | The sound to play |
| `Volume` | 1 | slider, 0 to 4 | Gain: 1 keeps the clip's level |
| `Pitch` | 1 | 0.01 to 8, step 0.01 | Speed and tone |
| `Loop` | off | switch | Start again at the end |
| `PlayOnStart` | on | switch | Start when the source is created |
| `Spatial` | on | switch | Place the sound at the entity |
| `MinDistance` | 1 | 0 and up | Distance up to which the sound is at full level |
| `MaxDistance` | 50 | 0 and up | Distance beyond which it stops falling |
| `Rolloff` | 1 | 0 to 100, step 0.01 | How fast the level falls between the two |

The Audio Listener has one property, `Active`, on by default. The editor shows the components under the category "Audio". The page [Spatial audio](../audio/spatial.md) teaches how the last three source properties and the listener shape what you hear.

::figure{id=inspector-audio}

The system itself is registered once, by `RegisterAudioModule`, with a name, a flag that says it does not run in Simulate mode and the soft order. Find the three lines that build and order the descriptor.

```cpp src="Strata/src/Strata/Audio/AudioRegistration.cpp#L44-L48" from="SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<AudioSystem>" to="ST_CORE_VERIFY" symbol="RegisterAudioModule"
SceneSystemDescriptor descriptor = MakeSceneSystemDescriptor<AudioSystem>("Audio", false, [](Scene& scene) { return CreateScope<AudioSystem>(scene); });
descriptor.AfterIfPresent = { "Scripting", "Animation", "Physics" };
descriptor.ProfileStage = "Scene.Audio";
const bool registered = SceneSystemRegistry::Register(std::move(descriptor));
ST_CORE_VERIFY(registered, "The audio module could not register its scene system");
```

The registration also names a profiler stage called Scene.Audio, so the system's cost appears in the frame's timings.

## A toy version

Before the real code, a toy keeps only the idea: one record per entity, a comparison with the values applied last, and pruning of records whose entity vanished. The toy has two settings, volume and loop. It prints what a real system would tell a voice.

The first update creates sources 1 and 2. The second changes source 1. The third removes source 2, adds source 3 and writes a :term[NaN]{id=nan} (not a number, a value no mixer can use) as the volume of source 1. The fourth repeats the third.

```cpp sketch="audio-scene-system-toy.cpp"
// A toy audio system: one record per entity, a comparison with the values applied last, pruning by the update
// that last saw the entity. No sound is made; the "source" only prints what the system tells it.
#include <bit>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <map>
#include <vector>

namespace
{

	struct Component
	{
		int Id = 0;
		float Volume = 1.0f;
		bool Loop = false;
	};

	struct Record
	{
		Component Applied;
		uint64_t SeenUpdate = 0;
	};

	bool IsSameFloat(float a, float b)
	{
		return std::bit_cast<uint32_t>(a) == std::bit_cast<uint32_t>(b);
	}

	class ToyAudioSystem
	{
	public:
		void Update(const std::vector<Component>& components)
		{
			m_UpdateIndex++;
			for (const Component& component : components)
			{
				auto it = m_Records.find(component.Id);
				if (it == m_Records.end())
				{
					std::printf("update %llu: create source %d (volume %.2f)\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Volume);
					it = m_Records.emplace(component.Id, Record { component, m_UpdateIndex }).first;
					continue;
				}
				Record& record = it->second;
				record.SeenUpdate = m_UpdateIndex;
				if (!IsSameFloat(component.Volume, record.Applied.Volume))
					std::printf("update %llu: source %d volume %.2f\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Volume);
				if (component.Loop != record.Applied.Loop)
					std::printf("update %llu: source %d loop %d\n", static_cast<unsigned long long>(m_UpdateIndex), component.Id, component.Loop ? 1 : 0);
				record.Applied = component;
			}
			std::erase_if(m_Records, [this](const auto& entry)
			{
				const bool gone = entry.second.SeenUpdate != m_UpdateIndex;
				if (gone)
					std::printf("update %llu: release source %d\n", static_cast<unsigned long long>(m_UpdateIndex), entry.first);
				return gone;
			});
		}
	private:
		std::map<int, Record> m_Records;
		uint64_t m_UpdateIndex = 0;
	};

}

int main()
{
	ToyAudioSystem system;
	const float notANumber = std::numeric_limits<float>::quiet_NaN();
	system.Update({ { 1, 1.0f, false }, { 2, 0.5f, false } });
	system.Update({ { 1, 0.4f, true }, { 2, 0.5f, false } });
	system.Update({ { 1, notANumber, true }, { 3, 1.0f, false } });
	system.Update({ { 1, notANumber, true }, { 3, 1.0f, false } });
	return 0;
}
```

```text output-of="audio-scene-system-toy.cpp"
update 1: create source 1 (volume 1.00)
update 1: create source 2 (volume 0.50)
update 2: source 1 volume 0.40
update 2: source 1 loop 1
update 3: source 1 volume nan
update 3: create source 3 (volume 1.00)
update 3: release source 2
```

1. **Line 28:** Floats compare by their bits, so a NaN equals itself and is applied only once.
2. **Line 43:** The first sight of an entity creates its record and stores the component as applied.
3. **Line 47:** Each update marks the records it saw with its own number.
4. **Line 48:** A field is told to the source only when it differs from the applied value.
5. **Line 54:** A record with an old number belongs to a vanished entity and is released.

The toy shows four behaviors that the real system shares. A write is heard by the next update, with no signal. A record the update did not see is released: `SeenUpdate` carries the count of the update that last found the component. The NaN is applied once, in update 3, and is silent in update 4, because the toy compares the bits of the two floats. An ordinary `==` would call a NaN different from itself and apply it every frame, flooding the log.

What the toy lacks is the half of the job where time passes: clips that load late, pauses and moving sources.

## The real code, in the order of one update

### The records and the comparison

An update starts with `UpdateSources`. It counts the update, visits every Audio Source component with an EnTT view (a loop over all entities that have the component), creates missing records and refreshes known ones.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L717-L746" symbol="AudioSystem::UpdateSources"
void AudioSystem::UpdateSources(float timestep)
{
	ST_PROFILE_FUNCTION();

	m_UpdateIndex++;
	entt::registry& registry = m_Scene.GetRegistry();
	for (const auto [handle, component] : registry.view<AudioSourceComponent>().each())
	{
		const Entity entity(handle, &m_Scene);
		if (!IsAudible(entity))
			continue;

		auto it = m_Sources.find(handle);
		if (it == m_Sources.end())
		{
			CreateSource(entity, component);
			continue;
		}

		SourceRecord& record = it->second;
		record.SeenUpdate = m_UpdateIndex;
		ApplyComponent(record, component);
		if (record.Applied.Clip != component.Clip || record.State == ClipState::Waiting)
			ResolveClip(record, entity, component);
		UpdateSourcePosition(record, entity, timestep);
	}

	// Components removed, entities deactivated or destroyed: their sources stop and are released.
	std::erase_if(m_Sources, [this](const auto& entry) { return entry.second.SeenUpdate != m_UpdateIndex; });
}
```

1. **Line 721:** The counter grows once per update, and records store it when seen.
2. **Line 726:** Inactive entities and those about to be destroyed are skipped, so their records go unseen.
3. **Lines 737–738:** A known record is marked as seen, then compared with the component.
4. **Lines 739–740:** The clip is resolved only when the handle changed or the record waits.
5. **Line 745:** Records not seen in this update are erased, which stops and releases their sources.

The function differs from the toy in three ways. It skips entities that are not audible: `IsAudible` walks from the entity to its root and fails when an ancestor is inactive or about to be destroyed, so an inactive parent silences its children. It resolves the clip only when the handle changed or the record waits. And it places the source: a spatial source takes its position from the entity's :term[world transform]{id=world-transform} at every update.

The comparison itself is in `ApplyComponent`. For each field, the code compares the component with `Applied` and calls the source's function for that field only when it changed.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L510-L536" symbol="AudioSystem::ApplyComponent"
void AudioSystem::ApplyComponent(SourceRecord& record, const AudioSourceComponent& component)
{
	AudioSource& source = *record.Source;
	AudioSourceComponent& applied = record.Applied;
	if (!IsSameFloat(component.Volume, applied.Volume))
		source.SetVolume(component.Volume);
	if (!IsSameFloat(component.Pitch, applied.Pitch))
		source.SetPitch(component.Pitch);
	if (component.Loop != applied.Loop)
		source.SetLooping(component.Loop);
	if (component.Spatial != applied.Spatial)
	{
		source.SetSpatial(component.Spatial);
		record.Motion = MotionTracker(); // No velocity from a position that was not followed
	}
	if (!IsSameFloat(component.MinDistance, applied.MinDistance))
		source.SetMinDistance(component.MinDistance);
	if (!IsSameFloat(component.MaxDistance, applied.MaxDistance))
		source.SetMaxDistance(component.MaxDistance);
	if (!IsSameFloat(component.Rolloff, applied.Rolloff))
		source.SetRolloff(component.Rolloff);

	// The clip is left to ResolveClip, which notices a new handle, stops the source and loads the new clip.
	const AssetHandle previousClip = applied.Clip;
	applied = component;
	applied.Clip = previousClip;
}
```

1. **Line 514:** Each field compares by bits with the applied value, and only a change reaches the source.
2. **Lines 520–524:** A source made spatial forgets its motion, so no velocity comes from a position nobody followed.
3. **Lines 532–535:** The whole component is stored except the clip, which `ResolveClip` handles.

Floats compare through `IsSameFloat`, which compares the bits with `std::bit_cast`. A value the source rejects, a NaN pitch for instance, is thus applied and reported once, and the source keeps its old value. The test "Component changes apply while playing, with or without a signal" writes a NaN pitch, steps five updates and expects one log line. Note the end of the function: it copies the whole component into `Applied` but keeps the previous clip, because the clip is the job of `ResolveClip`.

The same comparison also runs before every gameplay call. `PrepareSource` applies pending changes first, then calls `PlaceSource`, which moves a spatial source to where its entity is now. So a script that sets a new Clip and calls Play in the same frame starts the new clip. A sound source that a script has moved starts its sound at the new place.

### The life of a source

A record is born when the scene starts, when the component is added or when the entity becomes active. `CreateSource` copies the component's settings into the new `AudioSource`, stores them as `Applied` and places the source before it can start, so that its first samples come from the right position. If the component has a clip and `PlayOnStart` is on, the record is marked `PlayRequested`.

A record dies at once in three cases: its component is removed, its entity becomes inactive, or its entity is destroyed. The first two are found by pruning, because the update does not see the component. Destruction is faster. `OnEntityDestroying` erases the record immediately, so a destroyed entity is silent even when the entity dies between two updates.

The first update happens at a particular moment. `OnRuntimeStart` only reads the pause flag and finds the physics service. `OnRuntimeStarted` runs the first update, with a :term[time step]{id=time-step} of zero, after the scripts' `OnCreate`. The order lets a script configure a source in `OnCreate`, for instance setting a clip or disabling `PlayOnStart`, before the system starts the source.

### Clips that load late

`ResolveClip` moves a record through its clip states. Its first half handles a new handle.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L540-L548" from="if (record.Applied.Clip != component.Clip)" to="record.State = component.Clip.IsValid() ? ClipState::Waiting : ClipState::NoClip;" symbol="AudioSystem::ResolveClip"
if (record.Applied.Clip != component.Clip)
{
	// A new clip stops the source; Play starts the new one.
	record.Applied.Clip = component.Clip;
	record.Source->SetClip(nullptr);
	record.PlayRequested = false;
	record.PausedByScene = false;
	record.PendingSeek.reset();
	record.State = component.Clip.IsValid() ? ClipState::Waiting : ClipState::NoClip;
```

A new clip stops the source and drops everything pending: the play request, the seek and the scene pause. The reason is meaning: the old requests were about the old sound. After the change, a call to Play starts the new clip.

The second half asks the asset manager and branches on the answer.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L559-L591" from="if (Ref<Asset> asset = manager->GetAsset(handle))" to="record.State = ClipState::Unavailable;" symbol="AudioSystem::ResolveClip"
	if (Ref<Asset> asset = manager->GetAsset(handle))
	{
		if (Ref<AudioClip> clip = GetClip(asset, reason))
		{
			if (record.Source->SetClip(clip))
			{
				record.State = ClipState::Ready;
				if (record.PendingSeek)
					record.Source->Seek(*record.PendingSeek);
				record.PendingSeek.reset();
				StartIfRequested(record);
				return;
			}
			reason = "the mixer cannot play it";
		}
	}
	else if (manager->GetAssetState(handle) == AssetState::Loading)
	{
		return;
	}
	else if (reason.empty())
	{
		reason = manager->IsHandleValid(handle) ? manager->GetAssetError(handle) : std::string("it is not a known asset");
	}
}
else
{
	reason = "no asset manager is active";
}
if (reason.empty())
	reason = "it did not load";

record.State = ClipState::Unavailable;
```

1. **Line 559:** The manager returns the asset if it is loaded and otherwise starts the load without waiting.
2. **Lines 563–570:** The source takes the clip; the record becomes Ready, applies a stored seek and starts if asked.
3. **Lines 575–577:** A clip still loading ends the call, and the record stays Waiting.
4. **Lines 579–582:** Any other answer sets a reason for the warning.
5. **Line 591:** The record becomes Unavailable until its asset changes.

`GetAsset` requests the load when needed and never blocks. A loaded audio clip goes into the source: the record becomes Ready, a pending seek applies and a pending play starts. A clip that is still loading leaves the record Waiting, and the next update asks again. Anything else is a failure with a reason (unknown handle, load error, not an audio clip), and the record becomes Unavailable after one warning that names the entity.

Unavailable is not final. When an asset changes, for instance after an import runs again, `ProcessAssetChanges` notices that the manager's content version moved and asks which assets changed. For each record whose clip is among them, `RefreshClip` tries an Unavailable clip again and replaces a Ready clip that was reloaded. A playing source continues with the new clip. A clip unloaded on purpose is kept, not loaded again.

:::example
A scene starts with a radio entity whose clip is still loading, with `PlayOnStart` on. In update 0 the record is created in Waiting with `PlayRequested` set. In updates 1 to 4 the asset manager answers "loading", and the radio is silent. In update 5 the clip is ready, so the record becomes Ready and the radio plays. A Seek to 2 seconds in update 2 would start it 2 seconds in; a new clip in update 3 would drop the play and the seek.
:::

### The listener

`UpdateListener` collects the candidates: every Audio Listener with `Active` set on an audible entity. With none, it collects the primary cameras. If several candidates remain, `SelectListener` picks the first one in hierarchy order.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L834-L864" symbol="AudioSystem::SelectListener"
Entity AudioSystem::SelectListener()
{
	if (m_ListenerCandidates.size() <= 1)
		return m_ListenerCandidates.empty() ? Entity() : m_ListenerCandidates.front();

	// Ordering by hierarchy looks up every candidate's place among its siblings (all root entities for roots), so it is
	// redone only when the candidates or the hierarchy change.
	m_CandidateHandles.clear();
	for (const Entity candidate : m_ListenerCandidates)
		m_CandidateHandles.push_back(candidate.GetHandle());
	std::sort(m_CandidateHandles.begin(), m_CandidateHandles.end());
	if (m_CandidateHandles == m_SelectedAmong && m_Scene.GetHierarchyVersion() == m_SelectedAtVersion)
		return m_SelectedListener;

	m_ListenerSearchCount++;
	Entity first = m_ListenerCandidates.front();
	GetHierarchyPath(m_Scene, first, m_FirstPath);
	for (size_t index = 1; index < m_ListenerCandidates.size(); index++)
	{
		GetHierarchyPath(m_Scene, m_ListenerCandidates[index], m_CandidatePath);
		if (m_CandidatePath < m_FirstPath)
		{
			first = m_ListenerCandidates[index];
			std::swap(m_FirstPath, m_CandidatePath);
		}
	}
	m_SelectedAmong = m_CandidateHandles;
	m_SelectedAtVersion = m_Scene.GetHierarchyVersion();
	m_SelectedListener = first;
	return first;
}
```

1. **Lines 836–837:** With at most one candidate there is nothing to order.
2. **Lines 845–846:** The same candidates and the same :term[hierarchy version]{id=hierarchy-version} return the earlier choice.
3. **Line 848:** Only a real search is counted.
4. **Lines 854–858:** The smaller path wins, so the earlier entity in hierarchy order is kept.
5. **Lines 860–863:** The choice and its inputs are stored for the next update.

Ordering by hierarchy would normally visit the whole scene. The code instead gives each candidate a path: the sibling indices from its root down to it, made by `GetHierarchyPath`. Comparing two paths like words in a dictionary (the first index that differs decides) gives the order of a depth-first walk: a parent, then the whole branch of its first child, then the next child.

A cache avoids even that. The choice is kept while the candidates and the scene's :term[hierarchy version]{id=hierarchy-version} stay the same, and the counter `ListenerSearchCount` shows how often a real search ran. Two listeners at paths `[0, 2]` and `[1]` choose `[0, 2]`, because 0 is smaller than 1; the depth does not matter.

Without a candidate, the system puts the listener back at the origin, facing -Z. With one, the system reads the entity's world transform. Position is the fourth column, forward is minus the third column and up is the second column. A transform with no orientation, such as zero scale, leaves the listener where it was. The velocity for the Doppler effect comes from the same motion tracker that sources use, so [Spatial audio](../audio/spatial.md) holds the physics of that effect.

One policy concerns the up vector. The mixer derives the listener's right axis from forward and up. For an upright listener that does not roll, passing +Y as up gives the same orientation whatever its pitch and :term[yaw]{id=yaw-angle}. The up vector then never changes, and it does not have to travel to the mixing thread every frame.

A listener that rolls, looks nearly straight up or down, or is upside down passes its own up vector instead. At those poses, forward crossed with +Y either degenerates or points to the listener's left.

The engine has one listener. With several running scenes, the scene updated last places it. When a scene stops, `OnRuntimeStop` resets the listener to the origin facing -Z, so the next scene starts from the default.

### The pause

When the scene pauses, `OnPausedChanged` halts the playing sources and one-shots and marks them `PausedByScene`. Resuming plays exactly those. The method has a detail worth reading in full.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L203-L247" symbol="AudioSystem::OnPausedChanged"
void AudioSystem::OnPausedChanged(bool paused)
{
	if (m_Stopped || paused == m_Paused)
		return;

	if (!paused)
	{
		// Edits made while paused (sources removed, deactivated, muted or given another clip, a moved listener) apply before
		// anything resumes; still paused, nothing starts meanwhile. No time passed, so moves made meanwhile are teleports.
		UpdateSources(0.0f);
		ProcessAssetChanges();
		UpdateListener(0.0f);
	}
	m_Paused = paused;

	for (auto& [handle, record] : m_Sources)
	{
		if (paused && record.Source->IsPlaying())
		{
			record.Source->Pause();
			record.PausedByScene = true;
		}
		else if (!paused)
		{
			if (record.PausedByScene)
				record.Source->Play();
			record.PausedByScene = false;
			StartIfRequested(record);
		}
	}

	for (OneShot& oneShot : m_OneShots)
	{
		if (paused && oneShot.Source->IsPlaying())
		{
			oneShot.Source->Pause();
			oneShot.PausedByScene = true;
		}
		else if (!paused && oneShot.PausedByScene)
		{
			oneShot.Source->Play();
			oneShot.PausedByScene = false;
		}
	}
}
```

1. **Lines 208–215:** On resume, edits made during the pause apply first, with a time step of zero.
2. **Lines 218–231:** A pause halts the playing sources and marks them; a resume plays the marked ones and starts requested ones.
3. **Lines 234–246:** One-shots follow the same pattern.

Edits made while the scene was paused (sources removed, made inactive, muted or given another clip, a moved listener) apply before anything resumes. No time passed, so a move made meanwhile counts as a :term[teleport]{id=teleport-audio} and gives no Doppler velocity. While the scene is still paused, nothing starts. `Play` follows the same rule: asked during a pause, a source starts on resume. A step of a paused scene (the editor's single step) stays silent, since the system's pause flag does not change.

### The gameplay API and the one-shots

Entity sounds have six calls: `Play`, `Pause`, `Stop`, `IsPlaying`, `Seek` and `GetPlaybackPosition`. `IsPlaying` is true for a sound that will play: one waiting for its clip or held by the scene's pause. Each call first prepares the source as described above. `Seek` before the clip is ready stores the position, and `GetPlaybackPosition` reports the stored position until then. Sounds without an entity use `PlayOneShot` (not spatial, for interface sounds) and `PlayOneShotAt` (at a world position).

A one-shot belongs to the scene. It pauses with it and stops when it stops. It has three limits.

The scene plays at most 64 one-shots at once (`c_MaxOneShots`); when a 65th arrives, the oldest is cut off, so the newest sound always plays. A one-shot waits for its clip at most 0.25 s of scene time (`c_MaxOneShotClipWait`), because a footstep that comes half a second late is worse than none. And a clip that cannot play at all, because its handle is unknown or it is not an audio clip, drops at once.

```mermaid caption="A one-shot's life: it waits at most a quarter of a second for its clip, plays, and is reclaimed when it ends." alt="A flow. A request enters a waiting step. If the clip is ready, the sound plays, and the system reclaims it when it ends. If the clip is not ready within a quarter second, or cannot play, the sound is dropped and a warning is logged. When more than sixty-four sounds play, the oldest is dropped."
flowchart LR
	Q[Request] --> W[Waiting for clip]
	W -->|clip ready| P[Playing]
	P -->|ended| X[Reclaimed]
	W -->|over 0.25 s or unusable| D[Dropped, counted, warned]
	P -->|65th sound arrives| D
```

`StartOneShot` creates the sound. After a successful start it applies the cut-off.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L896-L902" from="if (m_OneShots.size() >= c_MaxOneShots)" to="m_OneShotsPlayed++;" symbol="AudioSystem::StartOneShot"
if (m_OneShots.size() >= c_MaxOneShots)
{
	DropOneShot(m_OneShots.front().Clip, fmt::format("more than {} one-shots played at once, so the oldest was cut off", c_MaxOneShots));
	m_OneShots.erase(m_OneShots.begin());
}
m_OneShots.push_back(std::move(oneShot));
m_OneShotsPlayed++;
```

The order matters. The new sound is tried first. Only a sound that succeeded, or waits, causes a cut-off, and the list is oldest first, so `front()` is the oldest. Then `UpdateOneShots` runs every update for the waiting sounds.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L942-L966" symbol="AudioSystem::UpdateOneShots"
void AudioSystem::UpdateOneShots(float timestep)
{
	std::erase_if(m_OneShots, [&](OneShot& oneShot)
	{
		if (!oneShot.Started)
		{
			oneShot.WaitedTime += timestep;
			std::string reason;
			if (!TryStartOneShot(oneShot, reason))
			{
				DropOneShot(oneShot.Clip, reason);
				return true;
			}
			// Too late: a sound effect that comes long after its cause is worse than none.
			if (!oneShot.Started && oneShot.WaitedTime > c_MaxOneShotClipWait)
			{
				DropOneShot(oneShot.Clip, fmt::format("its clip took longer than {} s to load", c_MaxOneShotClipWait));
				return true;
			}
			return false;
		}
		// Finished (or never got a voice) one-shots are reclaimed.
		return !oneShot.PausedByScene && !oneShot.Source->IsPlaying();
	});
}
```

1. **Line 948:** A waiting sound adds this update's scene time to its wait.
2. **Lines 950–954:** The start is tried first, and a sound that can never play drops at once.
3. **Lines 956–960:** Only a sound still not started after more than 0.25 s drops for being late.
4. **Line 964:** A started sound leaves the list when it stops playing, unless the pause holds it.

For a waiting sound, the update adds the frame time to `WaitedTime` and tries to start it again. Only when the start still fails, and the total wait is above the limit, does the sound drop. So a clip that becomes ready at 0.26 s is not dropped if it is ready when checked, but a clip that is not ready then is. Sounds that were started leave the list when they are no longer playing, unless the scene's pause holds them.

Every drop goes through one function.

```cpp src="Strata/src/Strata/Audio/AudioSystem.cpp#L435-L446" symbol="AudioSystem::DropOneShot"
void AudioSystem::DropOneShot(AssetHandle clip, std::string_view reason)
{
	m_OneShotsDropped++;
	const auto now = std::chrono::steady_clock::now();
	auto [it, added] = m_DropWarnings.try_emplace(clip, now);
	if (!added && now - it->second < std::chrono::seconds(1))
		return;
	it->second = now;
	const AssetManagerBase* manager = m_Scene.GetAssetManager();
	const std::optional<AssetMetadata> metadata = manager ? manager->GetMetadata(clip) : std::nullopt;
	ST_CORE_WARN("Audio: dropped a one-shot of '{}': {}", metadata && !metadata->Path.empty() ? metadata->Path : clip.ToString(), reason);
}
```

1. **Line 437:** Every drop counts.
2. **Lines 439–441:** A clip warned about less than a second ago gets no new warning.
3. **Lines 443–445:** The warning names the clip by path when the scene's manager knows it.

The counter `OneShotsDropped` rises for every drop, but the warning is rate limited: one per clip per second, with a map from clip handle to the time of its last warning. A game that asks for 200 footsteps of a clip that never loads gets 200 counted drops and about one warning per second, and the Console stays clear. The warning names the clip by path when the scene's manager knows one. The wait is measured in scene time, but the warning rate in real time (`steady_clock`).

The picture below shows the other reason for a drop. In the Physics Playground, impacts start more than 64 one-shots at once, so the oldest are cut off, and each warning names the clip and that reason.

::figure{id=console-dropped-warning crop=log}

The Physics Playground plays a one-shot when two bodies collide. The collision :term[callback]{id=callback} of its script `Impact.cpp` turns the hit into a volume and a pitch. Find the speed formula and the clamp.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L54-L61"
	const glm::vec3 other = collision.Other.IsValid() ? collision.Other.GetRigidBody().GetLinearVelocity() : glm::vec3(0.0f);
	const float separating = std::abs(glm::dot(own - other, collision.Normal));
	const float speed = separating + 0.5f * std::max(glm::length(own), glm::length(other));
	if (speed < MinSpeed || !m_Sound.IsValid() || !TakeSoundBudget())
		return;
	const float volume = std::clamp(speed / FullVolumeSpeed, 0.1f, 1.0f);
	Audio::PlayOneShotAt(m_Sound, collision.Point, volume, 0.9f + 0.2f * std::min(1.0f, speed / FullVolumeSpeed));
}
```

The collision :term[callback]{id=callback} computes the speed from both bodies' linear velocity, filters, then calls the SDK. It never touches the mixer. The call lands in the host function and ends in `AudioSystem::PlayOneShotAt`, with the hit's contact point as the position. The page [Rigid bodies and colliders](../physics/bodies-colliders.md) teaches the velocities the script reads.

:::example
The script takes how fast the bodies separate along the contact normal and adds half of the faster body's speed. It ignores hits below `MinSpeed`, 1.5 here. Volume is the speed over `FullVolumeSpeed` (10), clamped to 0.1 to 1, and pitch is 0.9 plus 0.2 times the same ratio, capped at 1.1. A hit at speed 4 gives volume 0.4 and pitch 0.98. A hit at 12 gives volume 1 and pitch 1.1, and a hit at 1 makes no sound.
:::

The second sample is the Third-Person's robot. Its animation controller raises a "Footstep" event in the walk and run states, and the script `Footsteps.cpp` answers in `OnAnimationEvent`. It picks one of four clips at random and plays it at the robot's world position with a random pitch between 0.9 and 1.1, so that no two steps sound alike.

In `OnCreate` the script calls `Assets::RequestLoad` for all four clips. This is the advice of the page in one habit: request clips before you need them. A footstep whose clip was never requested starts its load at the first step, and the 0.25 s limit would drop the first steps. What a game maker does with sounds is the subject of [Sound in a game](../make/sound.md).

### Inspection

Tools can hear a game without a sound card. `GetStats` counts sources, playing and waiting sources, one-shots, one-shots played and dropped, and listener searches. `GetVoices` lists every source and one-shot with its clip, volume, pitch, flags and position, and the editor command `audio.state` reports that list. `GetListenerEntity` names the entity the listener follows.

### The script side

Scripts never include the Audio module. A script calls the SDK: `AudioSource`, which wraps one entity's source (`Play`, `Pause`, `Stop`, `IsPlaying`, `Seek`, `GetPlaybackPosition`), and `Audio`, with `PlayOneShot`, `PlayOneShotAt`, `SetMasterVolume` and `GetMasterVolume`. Each SDK function first checks, through `ST_SCRIPT_DETAIL_HOST_WITH`, that the engine's table of host functions holds that entry and fills it, and returns false or a neutral value when it does not.

Ten host functions carry the calls: `AudioPlay`, `AudioPause`, `AudioStop`, `AudioIsPlaying`, `AudioSeek`, `AudioGetPlaybackPosition`, `AudioPlayOneShot`, `AudioPlayOneShotAt`, `AudioSetMasterVolume` and `AudioGetMasterVolume`. The first six and the one-shots reach the scene service `IAudioPlayback`; the master volume goes through the engine service `IAudioOutput`, which the Audio module registers. A scene service lives and dies with a scene that plays, while the master volume, like a game's sound option, lasts longer than any scene.

Misuse is reported and the call returns a failure value. A source call on an entity without an Audio Source says so, and an inactive entity reports that its source is silent. A non-finite seek position, a negative volume and a pitch of 0 or less each get their own message. A scene without the Audio module reports that it plays without audio. The pattern of these functions, `HostCall`, `ResolveContext` and `ReportProblem`, is taught in [host functions](../scripting/host-api.md).

## Not done: listeners per world

The engine has one listener: the mixer is configured with `listenerCount = 1`, and the plan for the engine lists per-world listeners as future work. A split-screen game would need one listener for each player's view, with a mix for each, or each source choosing its nearest listener. Neither exists at the pin.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Change events (`MarkModified`) for each audio field | Systems that react to signals | No per-frame comparison of idle sources | Every writer must signal; a forgotten signal gives silence without a message |
| Blocking until the clip loads | Simple engines and prototypes | One-shots never miss their start | A frame that stalls for a file, at 60 frames per second a stall above 16.7 ms |
| Unlimited one-shots | Engines with a large voice budget | No cut-off sounds | A count of voices with no limit, and its mixing cost |
| Queue a late one-shot until ready, however long | Many audio tools | No dropped sounds | A sound far from its cause: a footstep heard after the player stopped |
| One listener per world or per camera | Split-screen games | Each player hears their own view | A mix per listener and a larger mixer |
| Audio in the entity's own component code | Small engines | No separate system | Scattered code; no common pause, no listener choice |

The comparing way costs a few microseconds per frame for hundreds of sources, as computed above. The 0.25 s limit costs a missed sound when a game forgets to request its clips. Strata accepts that because a late sound is worse than a missing one, and a missing one leaves a warning.

## How it is tested

The suite `Audio.System` in `StrataTests/src/Audio/AudioSystemTests.cpp` holds the cases. They run on the :term[null device]{id=null-device}, so they need no sound card and no graphics hardware. A few cases and what each checks:

- "Audio plays in Play mode only, after scripts and physics" checks the mode and the order.
- "Component changes apply while playing, with or without a signal" writes fields directly and through `ComponentAccess`, then checks a NaN pitch logged once, and a new clip with Play.
- "Clips that are still loading play once they are ready", "Reloaded clips replace the playing ones; unloaded clips keep playing" and "Clips that cannot be played are reported once" cover the four clip states.
- "The listener is the first active listener in hierarchy order, then the primary camera" covers the choice.
- "The listener is chosen by hierarchy order only when the candidates or the hierarchy change" covers its cache.
- "Pausing the scene pauses its audio" and "Changes made while the scene is paused apply before it resumes" cover the pause.
- "One-shots belong to the scene" checks the cap of 64, the 0.25 s wait and invalid parameters, and "Scenes run without audio output" checks the silent mode.

Run the suite directly with `build/windows/bin/Debug/StrataTests.exe --test-suite=Audio.System`, or all tests with `ctest --preset windows-debug`.

## Changing it safely

Extension points are few. A new source property is a new field of `AudioSourceComponent`, a registration line with its range in `AudioComponents.cpp`, a comparison in `ApplyComponent` and a call that sets it on the source. A new gameplay call goes into the `IAudioPlayback` interface, `AudioSystem` and the host function list, at the end of the list.

Several rules of the engine's guide apply, each with its reason. Keep the Audio system out of Simulate mode. Keep every script-facing call behind `HostCall`, and append host functions at the end of the host table, so that old modules keep working. Keep work on the main thread.

Do not add a new `AssetManager::GetActive()` call: use `Scene::GetAssetManager()`. Keep the bitwise comparison, or a NaN floods the log. Before you commit, run the whole `Audio.System` suite and the scripting tests, and extend the feature test project when you add a script function.

## Summary

- An edit to an Audio Source is heard at the next update, because the system compares each component with the values last applied; no change signal is needed, and a NaN applies only once.
- A record's clip moves through `NoClip`, Waiting, Ready and Unavailable; a new clip stops the source and drops the pending play, seek and scene pause. A changed asset makes a new try or replaces the clip.
- The scene uses the first active listener in hierarchy order, else the primary camera, else the origin; the engine has one listener, so the last scene updated places it.
- A one-shot waits at most 0.25 s of scene time for its clip, the oldest is cut off beyond 64, and every drop is counted and warned about once per clip per second.
- A paused scene applies edits before it resumes, starts sounds asked for meanwhile on resume and keeps steps silent.

## Check yourself

1. A script writes `Volume = 0.2` on an Audio Source with plain field access and never signals a change. When is it heard? (a) Never, without `MarkModified`; (b) at the next update of the Audio system, in the late update; (c) at the next fixed step of physics.

   :::answer{tests="edit-heard"}
   (b). The system compares every component with `Applied` at each update. (a) is wrong: that is the event-driven way, which Strata did not choose for audio. (c) is wrong: the audio update runs in the late update, not in fixed steps.
   :::

2. A source plays clip A. A script sets Clip to clip B and does nothing else. What happens? (a) The source plays B from the start; (b) the source stops, and Play starts B; (c) the source keeps playing A.

   :::answer{tests="clip-states"}
   (b). `ResolveClip` stops the source and drops the pending play, seek and pause. (a) would hold if `PlayRequested` survived. (c) is wrong: the handle differs from the applied one.
   :::

3. Two active listeners stand at hierarchy paths `[2]` and `[0, 5]`. Which one does the scene use, and why?

   :::answer{tests="listener-choice"}
   The one at `[0, 5]`. Paths compare like words in a dictionary, and 0 is less than 2, whatever the depth. The result equals the order of a depth-first walk.
   :::

4. A one-shot's clip loads in 0.30 s. The game runs at 25 frames per second (0.04 s per frame). What happens, and when is the drop known?

   :::answer{tests="one-shot-limits"}
   The sound drops. Each update adds 0.04 s. After 6 updates the wait is 0.24 s, which is not above 0.25 s, so the sound still waits. After 7 it is 0.28 s, and the sound is dropped, counted and warned about.
   :::

5. The scene is paused. A script calls Play on a source with a ready clip, then you resume. What do you hear? Do edits made during the pause apply before or after the source starts?

   :::answer{tests="pause-rules"}
   The source starts on resume: `Play` during a pause only sets `PlayRequested`. The edits apply first, because `OnPausedChanged` runs `UpdateSources` before it resumes anything, so a changed volume is heard from the first sample.
   :::

## Exercises

1. **Basic.** Predict, then check: in the test "Component changes apply while playing, with or without a signal", a Play, a new clip and a second Play happen in one frame, and the test then checks `GetLength()`. Which length does the source's clip report, and does `IsPlaying` hold?

   :::answer[Worked solution]{tests="clip-states"}
   The first `Play` starts the old clip. Assigning the new clip does nothing yet. The second `Play` calls `PrepareSource`, which compares the handle, so `ResolveClip` stops the source, drops the old requests and loads the new clip, and `Play` starts it. The clip reports 1.0 s, the length of the long clip, and `IsPlaying` holds. To check, run the suite and put a break point in `ResolveClip`.
   :::

2. **Medium.** Run the wait sketch of one-shots for three clips and read the result. Then change the frame time to 0.1 s and predict the three results before you run.

   :::answer[Worked solution]{tests="one-shot-limits" solution="sketches/audio-scene-system-wait.cpp"}
   The sketch adds the frame time and tests the start before the deadline, as `UpdateOneShots` does through `TryStartOneShot`.

   ```cpp sketch="audio-scene-system-wait.cpp"
   // How long a one-shot waits for its clip: each update adds the frame time, and a clip not ready after the limit is dropped.
   #include <cstdio>

   namespace
   {

   	constexpr float c_MaxClipWait = 0.25f;

   }

   int main()
   {
   	const float frameTime = 0.04f;
   	const int loadFrames[3] = { 3, 6, 9 };
   	for (const int load : loadFrames)
   	{
   		float waited = 0.0f;
   		int frame = 0;
   		bool started = false;
   		while (!started && waited <= c_MaxClipWait)
   		{
   			frame++;
   			waited += frameTime;
   			started = frame >= load;
   		}
   		std::printf("clip ready after %d frames: %s at frame %d, waited %.2f s\n", load, started ? "plays" : "dropped", frame, waited);
   	}
   	return 0;
   }
   ```

   ```text output-of="audio-scene-system-wait.cpp"
   clip ready after 3 frames: plays at frame 3, waited 0.12 s
   clip ready after 6 frames: plays at frame 6, waited 0.24 s
   clip ready after 9 frames: dropped at frame 7, waited 0.28 s
   ```

   1. **Line 7:** The limit is the engine's 0.25 s.
   2. **Lines 20–25:** Each pass adds a frame, and the start is tested before the deadline.
   3. **Line 26:** One line reports the outcome.

   With 0.1 s frames, a clip ready after 3 frames plays at frame 3 (0.3 s waited, but the start succeeded first). Clips ready after 6 and 9 frames drop at frame 3 too, since 0.3 s is above 0.25 s.
   :::

3. **Medium.** Trace it yourself: many one-shots of a clip that is not loaded are asked for. Find where the drops are counted and where the warning is limited.

   :::answer[Worked solution]{tests="one-shot-limits"}
   Search for `DropOneShot` in `Strata/src/Strata/Audio/AudioSystem.cpp`. The function `AudioSystem::DropOneShot` raises `m_OneShotsDropped` first and then checks `m_DropWarnings` for the clip, returning without a warning when the last one is under one second old. A break point there shows the count rising on every call and the warning only about once per second.
   :::

4. **Hard.** Design: a split-screen game with two players needs one listener for each. Which parts of this page would change, and which would not?

   :::answer[Worked solution]{tests="listener-choice"}
   The choice (`SelectListener`) would return one listener for each view, and the engine (`AudioEngine`, with `listenerCount = 1`) would need to mix each source once for each listener or pick one per source. The records, the clip states, the pause and the one-shots keep their shape, though the position of a one-shot would need a rule for which listener hears it. The source records stay per entity, not per listener.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Audio/AudioSystem.h` and `AudioSystem.cpp`: the system, the records, the listener and the one-shots.
- `Strata/src/Strata/Audio/AudioComponents.cpp` and `AudioRegistration.cpp`: the components with their ranges, the system's registration and the service `IAudioOutput`.
- `Strata/src/Strata/Audio/AudioModule.cpp`: the module's update of the mixer.
- `Strata/src/Strata/Scene/SceneServices.h`: `IAudioPlayback` and `IAudioOutput`.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` and `StrataScriptCore/Include/StrataScript/Audio.h`: the host functions and the SDK.
- `StrataTests/src/Audio/AudioSystemTests.cpp`: the suite `Audio.System`.
- The command `audio.state`: the voices of a running game.

## Further reading

- Game Audio Programming, edited by Guy Somberg: chapters on voice management and sound engines (intermediate).
- The miniaudio documentation: the engine and its listener model (intermediate).
