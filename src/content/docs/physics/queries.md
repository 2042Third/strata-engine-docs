---
id: physics/queries
title: "Physics queries"
description: "How Strata answers where a ray hits, who overlaps a shape and what a query sees, and how to add a new query end to end."
kind: internals
size: M
tracks: [E]
needs: [physics/collision-layers]
time: 55
learn:
  - id: choose-query
    text: choose the query that answers a gameplay question and say what it returns
  - id: closest-clip
    text: explain how the ray callback clips the ray so that the closest hit wins
  - id: result-order
    text: name the order in which each query returns its results and why it is fixed
  - id: query-time
    text: explain which state of the world a query sees and which changes it applies first
  - id: add-query
    text: trace the files that a new query touches from the physics world to a script
since: 0.3.0
status: final
---

A game keeps asking questions about space. Can the guard see the player, is anything standing in the blast, and which crate is under the cursor? A physics query answers such a question without moving anything: it reads the bodies of the simulation and returns entities, points and distances. This page explains what Strata offers, the order of the answers, the world a query reads, and the code behind it.

Cameras that make a ray from the cursor, the probes inside the character controller and the editor's own picking have their own pages.

## The problem and how engines solve it

A script that wants to know what lies ahead could loop over every entity and test each shape itself. That works for ten crates and fails for ten thousand. It also repeats work that the physics module already does when it searches for contacts. The module keeps its shapes in trees that skip whole regions of space, and queries borrow those trees (see [Collision detection](collision-detection.md)).

Engines offer the same small family of questions. The first is the **raycast**: a ray has an origin, a direction and a maximum distance, and the question is what it hits first. The second asks which shapes lie inside a region, such as a sphere or a box.

The third is the **shape cast** (also called a sweep): it moves a whole shape along a path and reports where it first touches something. A shape cast tells you how far a crate can slide before it meets a wall, and a thin ray cannot, because a ray slips through a gap that is narrower than the crate.

Every engine settles the same details. Does the caller want the closest hit, or every hit along the ray? Which layers does a query see? Strata answers with the collision layers of [Collision layers](collision-layers.md).

Does a query report triggers, the volumes that detect entry but do not block? Can the caller ignore its own body, so that a ray fired from the player does not hit the player? When the ray starts inside a shape, does it hit the shape at distance zero, or pass out of it?

The last detail is time. A query might read the world as of the last step, or with every change made since, or force the engine to catch up first. Strata reads the world as of the last step, after it applies the pending component changes. A body that a script moved this frame stays where the last step left it, until the next step moves it.

## The map: from a script to box3d

A script calls `Physics::Raycast` of the script software development kit (SDK), header-only C++ that turns the call into plain data. The SDK calls a function of the host table, the set of :term[function pointers]{id=function-pointer} that the engine hands to every script module. The host function `HostRaycast` validates the arguments and asks the scene for its `IPhysicsQueries` service. `PhysicsSystem` implements that service, applies pending changes and passes the call to `PhysicsWorld`. The world asks box3d, the physics library that Strata builds on, to cast the ray or test the overlap.

```mermaid caption="A query travels from the script through the host table and the scene's query service to the physics world, and from there into box3d. Every step runs on the main thread." alt="A chain of seven boxes from a script through the SDK, the host function, the query service, the physics system and the physics world to box3d."
flowchart LR
    A["Script: Physics::Raycast"] --> B["SDK: Physics.h"]
    B --> C["Host function: HostRaycast"]
    C --> D["Service: IPhysicsQueries"]
    D --> E["PhysicsSystem: apply pending changes"]
    E --> F["PhysicsWorld: RayCallback, CollectOverlaps"]
    F --> G["box3d: b3World_CastRay, b3World_OverlapShape"]
```

The SDK lives in `StrataScriptCore/Include/StrataScript/Physics.h` and the host functions in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`. The service is declared in `Strata/src/Strata/Scene/SceneServices.h`. The system and the world are `Strata/src/Strata/Physics/PhysicsSystem.cpp` and `Strata/src/Strata/Physics/PhysicsWorld.cpp`.

## The contract

A caller of a query may rely on these rules, and the engine pays for each of them.

- **The world is the last step's.** A query sees the bodies where the last :term[fixed step]{id=fixed-step} left them. Strata applies component changes (a :term[collider]{id=collider} added, an entity destroyed or disabled) before the query runs. The reason: a query that sees half of a frame's changes is harder to reason about than one that sees none of the motion.
- **Results have a fixed order.** `Raycast` returns one hit. `RaycastAll` returns one hit per entity, nearest first. The overlap queries return entities in the order of their bodies' slots in box3d (creation order, until a freed slot is given again). The reason: a replay of the same inputs must give the same answers, and a tree may visit shapes in any order.
- **Triggers are skipped unless asked.** Every query takes `includeTriggers`, which defaults to false. The reason: most questions ("what is in front of me?") mean solid things.
- **An entity pending destruction never appears.** The reason: a script must not receive an entity that is about to vanish.
- **Distances stop at 100,000 metres.** Strata cuts a larger maximum distance, even infinity, to that length and does not refuse it. The reason: a script may pass infinity to mean "as far as there is world", and the ray still needs a finite length.
- **Bad input returns nothing.** A ray with a non-finite origin or direction, a zero direction, or a maximum distance that is zero, negative or not a number finds nothing, and the script host reports the problem. An overlap with a zero or negative radius or half extent finds nothing. The reason: a recoverable mistake must not crash a game.
- **Without a simulation, queries are empty.** Before Play starts, or in a scene without physics, the answer is no hit or no entity.

:::rule
Background work never touches engine state: jobs return their results through the :term[main thread]{id=main-thread}. A query reads the scene while it runs (`AcceptQueryShape` finds the entity of each shape), so a query from a worker thread would read the scene while the main thread changes it. See [Jobs](../core/jobs.md).
:::

The layer mask works as [Collision layers](collision-layers.md) describes. Bit $L$ of the 32-bit `layerMask` accepts shapes on layer $L$, and the SDK constant `Physics::c_AllLayers` sets all 32 bits. Every shape's mask also holds bit 63, the **query category**: the bit that only queries carry. A query finds a shape whatever that shape collides with, because of it. Without that bit, a layer that collides with nothing would be invisible to every query.

## A toy version

:::question
The sketch uses classes, functions, :term[lambdas]{id=lambda}, `std::vector` and `std::optional`. If these look new, read [Programming 3](../basics/programming-3.md), [Generic C++](../basics/cpp-generic.md) and [Modern C++](../basics/cpp-modern.md) first.
:::

The toy tests rays against balls instead of tree-held shapes, so the logic stays in view. The function `Enter` solves the ray-sphere test of [Geometry](../basics/math-geometry.md): the ray passes closest to the centre at distance `along`, and it enters the ball a half chord earlier. `Raycast` visits the balls in any order and keeps a limit that shrinks to each closer hit. `RaycastAll` collects every entry and sorts them. The balls are three unit balls on the x axis at 3, 6 and 9 metres, listed out of order.

```cpp sketch="physics-queries-toy.cpp"
#include <glm/glm.hpp>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <optional>
#include <vector>

struct Ball
{
	int Id = 0;
	glm::vec3 Center = glm::vec3(0.0f);
	float Radius = 1.0f;
};

struct Hit
{
	int Id = 0;
	float Distance = 0.0f;
};

// Where a ray along a unit direction enters a ball. A ray that starts inside it has no entry and hits nothing.
static std::optional<float> Enter(const glm::vec3& origin, const glm::vec3& direction, const Ball& ball)
{
	const glm::vec3 toCenter = ball.Center - origin;
	const float along = glm::dot(toCenter, direction);
	const float gap = ball.Radius * ball.Radius - (glm::dot(toCenter, toCenter) - along * along);
	if (gap < 0.0f)
		return std::nullopt;
	const float entry = along - std::sqrt(gap);
	if (!(entry > 0.0f))
		return std::nullopt;
	return entry;
}

// The balls come in any order, as a tree would give them. The limit shrinks to each closer hit.
static std::optional<Hit> Raycast(const glm::vec3& origin, const glm::vec3& direction, float maxDistance, const std::vector<Ball>& balls)
{
	std::optional<Hit> closest;
	float limit = maxDistance;
	for (const Ball& ball : balls)
	{
		const std::optional<float> entry = Enter(origin, direction, ball);
		if (!entry || *entry > limit)
			continue;
		closest = Hit { ball.Id, *entry };
		limit = *entry;
	}
	return closest;
}

// Every ball in reach, sorted so that the answer does not depend on the order the balls came in.
static std::vector<Hit> RaycastAll(const glm::vec3& origin, const glm::vec3& direction, float maxDistance, const std::vector<Ball>& balls)
{
	std::vector<Hit> hits;
	for (const Ball& ball : balls)
	{
		const std::optional<float> entry = Enter(origin, direction, ball);
		if (entry && *entry <= maxDistance)
			hits.push_back(Hit { ball.Id, *entry });
	}
	std::sort(hits.begin(), hits.end(), [](const Hit& a, const Hit& b)
	{
		return a.Distance != b.Distance ? a.Distance < b.Distance : a.Id < b.Id;
	});
	return hits;
}

static void Print(const char* label, const std::vector<Hit>& hits)
{
	std::printf("%s:", label);
	for (const Hit& hit : hits)
		std::printf(" ball %d at %.1f", hit.Id, hit.Distance);
	std::printf("\n");
}

int main()
{
	const std::vector<Ball> balls = { { 3, glm::vec3(9.0f, 0.0f, 0.0f), 1.0f }, { 1, glm::vec3(3.0f, 0.0f, 0.0f), 1.0f }, { 2, glm::vec3(6.0f, 0.0f, 0.0f), 1.0f } };
	const glm::vec3 along(1.0f, 0.0f, 0.0f);

	const std::optional<Hit> closest = Raycast(glm::vec3(0.0f), along, 20.0f, balls);
	Print("closest from 0", { *closest });
	Print("all from 0", RaycastAll(glm::vec3(0.0f), along, 20.0f, balls));
	Print("all within 6 m", RaycastAll(glm::vec3(0.0f), along, 6.0f, balls));
	const std::optional<Hit> inside = Raycast(glm::vec3(6.0f, 0.0f, 0.0f), along, 20.0f, balls);
	Print("closest from inside ball 2", { *inside });
	return 0;
}
```

```text output-of="physics-queries-toy.cpp"
closest from 0: ball 1 at 2.0
all from 0: ball 1 at 2.0 ball 2 at 5.0 ball 3 at 8.0
all within 6 m: ball 1 at 2.0 ball 2 at 5.0
closest from inside ball 2: ball 3 at 2.0
```

1. **Lines 26–30:** `along` is the distance to the point nearest the centre, `gap` is the squared half chord, and `entry` is where the ray enters.
2. **Line 31:** an entry at or behind the origin means the ray starts inside the ball, so the ball is not a hit.
3. **Lines 46–47:** each closer hit replaces the best one and lowers the limit, which later balls must stay under.
4. **Lines 62–65:** the sort by distance, then by id, makes the answer independent of the order of the list.

The closest hit from the origin is ball 1 at 2 metres, whatever the order of the list. The all-hits list is sorted by distance, and a shorter maximum distance cuts it: with 6 metres, ball 3 at 8 metres is gone. From inside ball 2, that ball does not hit, ball 1 lies behind the ray, and the closest hit is ball 3, 2 metres ahead. The toy omits layers, triggers, an ignored entity, the grouping per entity and the pending changes of the world.

:::example
Take the Physics Playground of the sample project, a test scene full of crates and balls. A crate stands 3 metres from the player along the x axis, with a half size of 1 metre, and two more stand at 6 and 9 metres. The ray starts at chest height, 1 metre up, and points along the axis with a maximum distance of 20 metres. The faces nearest the player lie at 2, 5 and 8 metres, so their fractions of the ray are 0.10, 0.25 and 0.40. The distance of a hit is its fraction times 20 metres.

For each shape the ray touches, box3d calls a function of Strata's, the :term[callback]{id=callback}, with the hit's fraction. The fraction that the callback returns becomes the ray's new end, as the real code below shows.

Suppose the tree reports the far crate first. The callback stores fraction 0.40 and returns it, so box3d shortens the ray to 8 metres. The tree then reports the near crate at 0.10: the callback stores it and returns 0.10, so the ray is now 2 metres long. The middle crate lies beyond the shortened ray and never reaches the callback. `Raycast` reports the near crate at 2 metres, and no order of the three reports changes that.

Start the ray at the middle crate's centre instead. Its fraction for that crate is 0, so the callback ignores it, and the answer is the far crate at 2 metres. `RaycastAll` from the first position returns all three crates, at 2, 5 and 8 metres.
:::

## The real code

Real queries start at the callback. `PhysicsWorld.cpp` passes `RayCallback` to `b3World_CastRay`, and box3d calls it for each shape the ray touches, with the hit point, the normal and the fraction of the ray's length. The number the callback returns tells box3d what to do next: -1 means ignore this shape, 0 means stop, a fraction means clip the ray to it, and 1 means continue.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4501-L4518" from="RayQuery& query = *static_cast<RayQuery*>(context);" to="return 1.0f;" symbol="RayCallback"
RayQuery& query = *static_cast<RayQuery*>(context);
const ShapeSlot* slot = AcceptQueryShape(*query.Data, shape, query.Ignored, query.IncludeTriggers);
if (!slot)
	return -1.0f;
// A ray starting inside a convex collider passes out of it without a hit.
if (slot->Convex && !(fraction > 0.0f))
	return -1.0f;
RayQuery::Hit hit { slot->Entity, slot->BodyKey, ToGlm(point), ToGlm(normal), fraction };
if (!query.All)
{
	if (fraction < query.Closest.Fraction)
		query.Closest = hit;
	return fraction; // Only closer hits from now on
}
auto [it, inserted] = query.PerEntity.try_emplace(slot->Entity, hit);
if (!inserted && fraction < it->second.Fraction)
	it->second = hit;
return 1.0f;
```

1. **Lines 4502–4504:** `AcceptQueryShape` rejects triggers (unless asked), the ignored entity, and entities that are destroyed or pending destruction.
2. **Lines 4506–4507:** a :term[convex]{id=convex} shape (not a triangle mesh) with a fraction that is not above zero means the ray started inside it, so the ray passes out without a hit.
3. **Lines 4509–4513:** `Raycast` keeps a hit that is closer than the best so far and returns its fraction, which clips the ray.
4. **Lines 4515–4518:** `RaycastAll` keeps the closest hit per entity in a map and returns 1, so the ray stays whole and every entity gets its turn.

The ignored entity needs care. `GetIgnoredEntity` replaces the entity the caller passes with the owner of its body, so ignoring a child that carries a collider ignores the whole body.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L5409-L5416" from="RayQuery query;" to="return MakeRaycastHit(data, query.Closest, length);" symbol="PhysicsWorld::Raycast"
RayQuery query;
query.Data = &data;
query.Ignored = GetIgnoredEntity(data, ignoreEntity);
query.IncludeTriggers = includeTriggers;
b3World_CastRay(data.World, ToB3(origin), ToB3(translation), PhysicsFilters::MakeQueryFilter(layerMask), &RayCallback, &query);
if (query.Closest.Fraction > 1.0f)
	return std::nullopt;
return MakeRaycastHit(data, query.Closest, length);
```

`Raycast` builds the query with `MakeQueryFilter(layerMask)` as the filter and calls box3d. The initial fraction is 2, so a closest fraction above 1 means nothing was hit. `MakeRaycastHit` multiplies the fraction by the clamped length to give the distance, which is why the 100,000 metre limit applies to the ray itself.

`RaycastAll` copies the per-entity map into a vector and sorts it by fraction, then by entity identifier. The map has no defined order, so the sort makes the result :term[deterministic]{id=determinism}. `Raycast` needs no sort, but it has a quiet tie: when two shapes report the same fraction, the test `fraction < query.Closest.Fraction` keeps the one the tree reported first. Two boxes that share a face show such a tie.

An overlap query has no ray to clip. `CollectOverlaps` hands box3d a small convex shape and a centre, and box3d reports every shape that touches it. A sphere is one point with a radius, and a box is its eight corners.

```cpp src="Strata/src/Strata/Physics/PhysicsWorld.cpp#L4551-L4558" from="// The body index (the key's low half)" to="query.Found.erase(std::unique(query.Found.begin(), query.Found.end()), query.Found.end());" symbol="CollectOverlaps"
// The body index (the key's low half) orders them as the bodies were made, whatever order the tree visits them in.
std::sort(query.Found.begin(), query.Found.end(), [](const auto& a, const auto& b)
{
	const uint32_t indexA = static_cast<uint32_t>(a.first);
	const uint32_t indexB = static_cast<uint32_t>(b.first);
	return indexA != indexB ? indexA < indexB : a.first < b.first;
});
query.Found.erase(std::unique(query.Found.begin(), query.Found.end()), query.Found.end());
```

The tree visits shapes in whatever order its structure gives, and that order can change when bodies move. Each shape slot holds a body key whose low half is the body's slot index, given out in creation order and, once freed, to the next new body. Sorting by that index, then by the whole key, gives an order that depends only on the scene's history. Removing repeats drops a body found through two of its shapes. The code after these lines keeps one entry per entity, because a character controller adds a presence body to an entity that may have a body of its own.

The game side shows the queries at work. The Physics Playground builds a ray through the cursor, and its grab tool picks a body with `Physics::Raycast` while you hold **E**. The next quote starts after the pointer ray is built.

```cpp src="Samples/PhysicsPlayground/Scripts/Playground.cpp#L234-L254" from="if (!m_Grabbed.IsValid())" to="body.SetAngularVelocity(body.GetAngularVelocity() * 0.9f);" symbol="Playground::UpdateGrab"
if (!m_Grabbed.IsValid())
{
	// The body under the cursor, if it is one of the playground's.
	const std::optional<RaycastHit> hit = Physics::Raycast(origin, direction, 60.0f);
	if (!hit || !hit->HitEntity.IsValid())
		return;
	const std::string tag = hit->HitEntity.GetTag();
	if (tag != "Crate" && tag != "Domino" && tag != "Ball" && tag != "Ghost" && tag != "Pin")
		return;
	m_Grabbed = hit->HitEntity;
	m_GrabDistance = std::min(hit->Distance, GrabDistance);
}
// Pulled toward a point in front of the camera with a speed that closes the gap within a few steps.
const glm::vec3 target = origin + direction * m_GrabDistance;
RigidBody body = m_Grabbed.GetRigidBody();
glm::vec3 velocity = (target - m_Grabbed.GetTransform().GetWorldPosition()) * 10.0f;
const float speed = glm::length(velocity);
if (speed > 20.0f)
	velocity *= 20.0f / speed;
body.SetLinearVelocity(velocity);
body.SetAngularVelocity(body.GetAngularVelocity() * 0.9f);
```

1. **Line 237:** the pick passes a ray and a 60 metre limit, so the defaults apply: all layers, no ignored entity, no triggers.
2. **Lines 240–242:** the tag check lets only the playground's own bodies be grabbed.
3. **Line 244:** the grab distance is the smaller of the hit distance and the field `GrabDistance`, 12 metres by default.
4. **Lines 249–252:** the velocity is the gap to the target times 10, cut to 20 metres per second: a crate 1.5 metres away gets 15, and one 3 metres away gets 30, cut to 20.
5. **Lines 253–254:** a velocity moves the body through the simulation, so it still collides with the world, unlike a teleport; the :term[angular velocity]{id=angular-velocity} decays by a tenth per fixed step, because `OnFixedUpdate` calls `UpdateGrab`.

The shot of a ball does not query: it spawns a ball and gives it a velocity along the pointer ray.

The public application programming interface (API) has no shape cast. It offers `Raycast`, `RaycastAll`, `OverlapSphere` and `OverlapBox`, and nothing that moves a shape along a path. box3d's mover cast (`b3World_CastMover`) runs only inside the character controller, which has its own page ([Character controllers](character-controllers.md)).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Shape casts (sphere, box, capsule) in the API | Unity, Unreal and Godot offer them | A script could ask how far a body slides, or whether a thick shot fits a gap | One more query per shape through every layer, and tests against meshes |
| A callback that a script supplies for each hit | Native physics libraries, including box3d | Any rule per hit, with no vector of results | A guarded call into module code for each hit |
| Overlap results in the tree's order | Most libraries by default | No sort and no repeat check | Answers that change when bodies move, so replays differ |
| Every hit of a body, not the closest per entity | Libraries that report each shape | A ray through a ramp of colliders lists every one | Several hits for one game object |
| Updating transforms before each query | Unity offers a setting for it | A body moved this frame shows at its new place | A cost on each query, or a hidden step between two script lines |

## How it is tested

The suite `Physics.Queries` in `StrataTests/src/Physics/PhysicsQueryTests.cpp` has seven test cases. `Raycast reports the closest hit` checks the point, the normal and the distance, and that the direction need not have unit length. `Raycast misses and rejects invalid rays` checks the limits, the clamp for infinity and the rejection of :term[NaN]{id=nan}. `Raycasts skip triggers and an ignored entity unless asked` and `RaycastAll returns every entity hit, sorted by distance` check the filters and the order.

`Overlap queries find the entities intersecting a sphere or box` checks both shapes, the same order on a repeated call, and invalid input. `Layer masks filter queries` checks the mask. `Queries see component changes made earlier in the frame` checks that a collider added or removed in the same frame shows at once.

Script modules test the script side: `StrataTests/Scripts/API/PhysicsScripts.cpp` and the feature script `StrataTests/FeatureTest/Scripts/PhysicsApiFeatures.cpp` call `Physics::Raycast` and `Physics::RaycastAll`. Run the suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Physics.Queries`.

## Changing it safely

A new query touches every layer of the map, in this order. First put the shape work in `PhysicsWorld` (`PhysicsWorld.h` and `PhysicsWorld.cpp`), built on `CollectOverlaps` or `RayCallback`. Declare it in `IPhysicsQueries` in `SceneServices.h`, and implement it in `PhysicsSystem` with `ApplyPendingChanges()` first and an empty result when there is no world.

Then append the host function. It goes at the end of the `StrataScriptHostAPI` :term[struct]{id=struct} in `ScriptABI.h` and at the end of `ST_SCRIPT_HOST_FUNCTIONS` in `ScriptHostAPI.cpp`, never in the middle. Wrap its body in `HostCall`, resolve the context first and report misuse with `ReportProblem`. Add the SDK function to `Physics.h` so that a module on an older engine gets an empty answer (`ST_SCRIPT_DETAIL_HOST_WITH`). Finish with a test in `PhysicsQueryTests.cpp`, a call from the API test module and a call from the feature script.

:::rule
Host functions go at the end of the table and never move, because a script module built against an older table reads the functions by position. The application binary interface (ABI) version stays the same when you append. See [Host API](../scripting/host-api.md) and [the host function tutorial](../scripting/tutorial-host-function.md).
:::

Keep two more rules. A new query takes a layer mask and a trigger flag like its relatives. A scene change in a test must be signalled (`MarkModified` or `registry.patch`), or the physics world does not see it.

## Summary

- A query answers a question about space without moving anything. Strata offers a closest raycast, an all-hits raycast and two overlap tests, but no shape cast.
- `RayCallback` returns the fraction of each hit, which clips the ray, so the closest hit wins whatever the order of the shapes.
- `RaycastAll` gives one hit per entity, nearest first. The overlap queries give entities in body slot order.
- A query sees the bodies as of the last fixed step, after pending component changes, and it clamps distances to 100,000 metres.
- A new query touches the physics world, the service, the system, the ABI :term[header]{id=header}, the host function, the SDK, a test and the feature script.

## Check yourself

1. A script must find the nearest wall in front of the player to place a sign. Which query fits?

   - A. `OverlapSphere`, which returns the walls in the sphere.
   - B. `Raycast`, which returns an optional hit with the entity, point, normal and distance.
   - C. `RaycastAll`, which returns a vector of hits that the script must sort.

   :::answer{tests="choose-query"}
   B. A raycast along the player's forward direction returns the closest hit, with the point where the sign goes and the normal that tells it which way to face. A is wrong: an overlap returns entities, not points, and cannot tell which is nearest. C is wrong because the hits already come nearest first and the script needs only the first.
   :::

2. Three boxes stand in a row. `RaycastAll` returns hits at 2, 5 and 8 metres, and `Raycast` returns the 2 metre hit. Why does `RayCallback` return 1 for one and a fraction for the other? What happens if the ray starts inside the middle box?

   :::answer{tests="closest-clip"}
   Returning the fraction clips the ray, so box3d reports only closer shapes afterwards, and the last stored hit is the closest. `RaycastAll` needs every entity, so it returns 1 and the ray stays whole. A ray that starts inside the middle box gets fraction 0 for it on a convex shape. The callback returns -1, so the box is no hit, and the other boxes still count.
   :::

3. The tree visits two shapes in the order east, centre. The centre entity was made first. In which order does `OverlapSphere` return them, and what changes if the tree visits them the other way round?

   :::answer{tests="result-order"}
   Centre comes first: the code sorts by body index, and here the index follows the order in which Strata made the bodies. A different visiting order changes nothing, because the sort removes the dependence on the tree. `RaycastAll` has the same property through its sort by distance.
   :::

4. In one frame, a script sets a crate's transform 5 metres to the left and then calls `Raycast` at the crate's old place. Does the ray hit the crate? What if the script destroys the crate instead?

   :::answer{tests="query-time"}
   The ray still hits the crate: a transform that changes outside physics reaches the body at the next fixed step, and the query reads the bodies as of the last step. `Teleport` would move the body at once. If the script destroys the crate, the ray misses, because Strata applies entity destruction and component changes before every query.
   :::

5. A new host function for your query must go where in `StrataScriptHostAPI` and `ST_SCRIPT_HOST_FUNCTIONS`? A: after the other query functions. B: at the end of both. C: at the start of both.

   :::answer{tests="add-query"}
   B. Modules built against an older table read functions by position, so an inserted function would shift every later one. A is wrong for the same reason, unless the query functions happen to be last. C breaks every module.
   :::

## Exercises

1. **Basic.** A bomb explodes at (0, 0, 0) with a radius of 4 metres. Crates stand at x = 2 and x = 6 (half size 0.5), and a trigger zone stands at x = 1. Which entities does `OverlapSphere(center, 4.0f)` return? Which does it return with `includeTriggers` set?

   :::answer[Worked solution]{tests="choose-query"}
   The crate at x = 2 spans 1.5 to 2.5, which lies inside the sphere, so it is found. The crate at x = 6 spans 5.5 to 6.5, beyond the radius, so it is not. The call skips the trigger by default and finds it when `includeTriggers` is true, so the second call returns the near crate and the trigger, in body slot order.
   :::

2. **Medium.** Write a function that takes the shapes a tree reports (each a body key and an entity) and returns the entities in the engine's order. Predict the output for the keys in the sketch before you run it.

   :::answer[Worked solution]{tests="result-order" solution="sketches/physics-queries-overlap-order.cpp"}
   Sort by the low half of the key (the body index), remove exact repeats, then keep the first entry of each entity. The reported indices are 7, 3, 9, 5 and 7, so the sorted order is 3, 5, 7, 7, 9. The repeat of 7 goes, and entity 50 appears at 5 and 9, so its second entry goes too.

   ```cpp sketch="physics-queries-overlap-order.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <unordered_set>
   #include <utility>
   #include <vector>

   // A body key holds the body's generation in its high half and its index in its low half.
   static uint64_t MakeKey(uint32_t generation, uint32_t index)
   {
   	return (static_cast<uint64_t>(generation) << 32) | index;
   }

   // What the engine does with the shapes a tree reports: order by body index, drop repeats, one entry per entity.
   static std::vector<int> Order(std::vector<std::pair<uint64_t, int>> found)
   {
   	std::sort(found.begin(), found.end(), [](const auto& a, const auto& b)
   	{
   		const uint32_t indexA = static_cast<uint32_t>(a.first);
   		const uint32_t indexB = static_cast<uint32_t>(b.first);
   		return indexA != indexB ? indexA < indexB : a.first < b.first;
   	});
   	found.erase(std::unique(found.begin(), found.end()), found.end());

   	std::vector<int> entities;
   	std::unordered_set<int> seen;
   	for (const auto& [key, entity] : found)
   	{
   		if (seen.insert(entity).second)
   			entities.push_back(entity);
   	}
   	return entities;
   }

   int main()
   {
   	// Bodies 7, 3, 9, 5 and 7 again (a second shape of the same body), in the order a tree might report them.
   	// Body 9 belongs to entity 50 too, as a character's presence body would.
   	const std::vector<std::pair<uint64_t, int>> found = {
   		{ MakeKey(1, 7), 70 }, { MakeKey(2, 3), 30 }, { MakeKey(1, 9), 50 }, { MakeKey(1, 5), 50 }, { MakeKey(1, 7), 70 }
   	};
   	for (int entity : Order(found))
   		std::printf("entity %d\n", entity);
   	return 0;
   }
   ```

   ```text output-of="physics-queries-overlap-order.cpp"
   entity 30
   entity 50
   entity 70
   ```

   1. **Lines 17–22:** the sort by body index, then by the whole key.
   2. **Line 23:** `std::unique` drops the repeat of body 7.
   3. **Lines 27–31:** a set keeps the first entry of each entity.
   :::

3. **Medium.** Trace it yourself. Copy the test `Raycast reports the closest hit`, give it three boxes in a row and put a breakpoint in `RayCallback`. Cast the ray: what does each call return, and when does a call not happen? Repeat with `RaycastAll`, then start the ray inside the middle box.

   :::answer[Worked solution]{tests="closest-clip"}
   The function is `RayCallback` in `Strata/src/Strata/Physics/PhysicsWorld.cpp`, called from `PhysicsWorld::Raycast` and `PhysicsWorld::RaycastAll` through `b3World_CastRay`. With `Raycast`, each call that stores a hit returns its fraction, and later calls come only for closer shapes. The box beyond the clipped ray gets no call. With `RaycastAll`, the callback returns 1 each time, so all three boxes are reported. A ray that starts inside the middle box gets a call for that box with fraction 0, which returns -1 and leaves no hit.
   :::

4. **Hard.** Add `SphereCast`: a sphere of a given radius moves along a ray, and the query returns its hits sorted by distance, with the same mask, ignore and trigger filters. List the files you change, in order, and say what each change holds.

   :::answer[Worked solution]{tests="add-query"}
   Start in `PhysicsWorld.h` and `PhysicsWorld.cpp`: a member that validates its input like `MakeRay`, casts a sphere along the path with a box3d shape cast, filters hits through `AcceptQueryShape` and sorts them like `RaycastAll`. Add a :term[pure virtual function]{id=pure-virtual-function} to `IPhysicsQueries` in `SceneServices.h` and an override in `PhysicsSystem` that starts with `ApplyPendingChanges()`. Append the function to `StrataScriptHostAPI` in `ScriptABI.h` and to `ST_SCRIPT_HOST_FUNCTIONS` in `ScriptHostAPI.cpp`, with a host function that wraps its body in `HostCall`. Add the SDK function to `Physics.h`. Test it in `PhysicsQueryTests.cpp`, call it from `StrataTests/Scripts/API/PhysicsScripts.cpp` and from the feature script.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Physics/PhysicsWorld.cpp`: `RayCallback`, `PhysicsWorld::Raycast`, `PhysicsWorld::RaycastAll`, `CollectOverlaps`, `c_MaxRaycastDistance`.
- `Strata/src/Strata/Physics/PhysicsSystem.cpp`: the query functions that apply pending changes first.
- `Strata/src/Strata/Physics/PhysicsFilters.h`: `MakeQueryFilter` and the :term[query category]{id=query-category} bit.
- `Strata/src/Strata/Scene/SceneServices.h`: `IPhysicsQueries` and `RaycastHit`.
- `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`: `HostRaycast`, `HostRaycastAll`, `HostOverlapSphere`, `HostOverlapBox`.
- `StrataScriptCore/Include/StrataScript/Physics.h`: `Physics::Raycast`, `RaycastAll`, `OverlapSphere`, `OverlapBox`, `c_AllLayers`.
- Tests: the suite `Physics.Queries`; the script modules `StrataTests/Scripts/API/PhysicsScripts.cpp` and `StrataTests/FeatureTest/Scripts/PhysicsApiFeatures.cpp`.
- Sample: `Samples/PhysicsPlayground/Scripts/Playground.cpp`, `Playground::UpdateGrab`.

## Further reading

- The box3d repository, README and the header `types.h`: the ray cast callback and what its return value means (intermediate).
- Unity manual, "Physics.Raycast", "Physics.SphereCast" and "Physics.OverlapSphere": how another engine names the same queries (beginner).
- Christer Ericson, "Real-Time Collision Detection", the chapters on ray and sweep tests: the mathematics behind casts (advanced).
