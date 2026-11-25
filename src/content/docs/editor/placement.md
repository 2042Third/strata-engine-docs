---
id: editor/placement
title: "Placing content"
description: "How the editor finds the surface under a point of the Scene view, rests an asset on it, and makes the drop, its ghost and asset.place agree."
kind: internals
size: M
tracks: [E]
needs: [editor/undo, basics/math-geometry, draw/bounds-culling, editor/deferred-commands]
time: 60
learn:
  - id: ray-from-pixel
    text: explain how a point of the Scene view becomes a ray and why the camera position is added last
  - id: place-decision
    text: trace the order in which Place looks for a surface, the grid plane and a point in front, and what snapping changes
  - id: rest-box
    text: compute where the origin of a box lands when its bottom side rests on a tilted surface
  - id: one-request
    text: explain why the drop, its ghost and asset.place build one request and what the ghost writes
since: 0.3.0
status: final
---

A person drags a crate :term[prefab]{id=prefab-world} from the Content Browser into the Scene view. An agent sends `asset.place` with a point of
the same view. Both expect the crate to stand on whatever lies under that point, and both must get exactly the same
place. This page explains the code that decides where such content lands: it finds the surface under a ray, rests the
asset's box on it, and falls back to a guess when nothing is there. It does not draw the Scene view, and it does not
query the physics colliders of a running game.

## The problem and how engines solve it

Three naive answers fail. The first puts every new asset at the origin: the person must then drag it across the world,
and in a large scene the origin may be far away. The second puts the asset's origin on the point under the pointer. A
crate model whose origin is its center then sinks half into the ground.

The third computes the place twice, once for the
preview while dragging and once for the drop. The two results read the camera at different moments, so the crate
lands where the preview was not.

Take a crate that is a cube of 1 m, with its origin in the middle. The ground is the plane $y = 0$ and the pointer is over
it. Placing the origin on the ground point gives a height of 0, and half the crate is below ground. Placing the crate
on the ground needs a height of 0.5 m, half its height. On a tilted surface the lift is no longer straight up, and the
rest of this page works out by how much.

Engines find the point under the pointer in three ways. They can read the depth of the pixel under the pointer from a
picture the graphics hardware drew. That is exact for what shows on screen, but it arrives a frame late and does not
exist for a script with no window. They can cast a ray against physics colliders, which only finds things that have a collider.

Strata's editor takes a third way: it casts its own ray against what the scene draws, in plain code, in the frame that
asks. The table at the end of the page lists the costs.

## The map

All of this runs on the :term[main thread]{id=main-thread}. The Scene view's drag and the `asset.place` command meet at one function,
`EditorPlacement::Place`, and everything below it is shared.

```mermaid caption="Two callers build one kind of request. Place casts the ray through the render scene's index, rests the asset's box on the hit and returns the translation." alt="A diagram in which the Scene view drag and the asset.place command both feed a request builder, which feeds Place; Place calls the ray cast and the box rest and takes the asset's bounds."
flowchart TD
    Drag["Scene view drag: PlacementPreview"] --> Ray["MakeViewRay"]
    Cmd["asset.place command"] --> Req["MakeRayRequest"]
    Ray --> Req
    Req --> Place["EditorPlacement::Place"]
    Bounds["AssetBounds: what the asset draws"] --> Place
    Place --> Cast["SceneRaycast::Cast"]
    Cast --> Index["render scene spatial index"]
    Cast --> Tri["loaded triangles, or bounds"]
    Place --> Rest["RestOn"]
```

The files sit in `StrataEditor/src/Editor/`. `SceneRaycast` casts, `EditorPlacement` decides, `PlacementPreview`
holds the state of the ghost, `AssetBounds` measures assets, and `Commands/PlacementCommands.cpp` registers
`scene.raycast` and `asset.place`. The Scene view's panel draws the ghost and feeds the pointer; its drawing is another
page's subject.

## The contract

What the code promises and what callers must do:

- A ray comes from `MakeViewRay`, which adds the camera's position after the rotation, so it stays exact far from the
  origin.
- A request comes from `MakeRayRequest`. The drag and the command call it with the same floats, so the two requests are
  equal to the last bit.
- `Place` returns a translation for the asset's root. Rotation and scale of the request apply over the asset's own.
- The entities being placed are never hit: a cast takes an ignore list, and its descendants are skipped too.
- A hover creates no entity and no :term[undo step]{id=undo-step}, and it changes no selection and no version.
- `asset.place` is an Edit command that waits, by the clock and never by frames, until the asset it places has loaded.

:::rule
Place content through `EditorPlacement::Place`, and let the drop and its ghost use one request. The drop runs the same
command an agent runs, so no second code path can disagree about where a crate lands. A command that must wait
returns a poll function, as [Commands that take frames](deferred-commands.md) explains.
:::

## Resting a box: the geometry

Where a ray hits a surface, the surface has a point $P$ and a unit normal $n$ (a normal is a direction that points
away from the surface and has length 1). The asset is a box around its origin, and the box must touch the surface
without sinking. The lowest part of the box is its farthest point against the normal. That point lies some distance
behind the origin, and the asset must move out along the normal by that distance.

Small numbers first. The crate has half-size $e = (0.5, 0.5, 0.5)$ and its center $c$ is the origin. On flat ground
the normal is $(0, 1, 0)$ and the lift is 0.5, as before. On a ramp that rises 30 degrees the normal is
$(-0.5, 0.866, 0)$.

The crate keeps its upright pose, so its lowest edge touches the ramp. The distance behind the
origin is $0.5 \cdot 0.5 + 0.866 \cdot 0.5 = 0.683$, more than 0.5 because the box reaches diagonally toward the ramp.

The general rule is called the **support function** of the box: the distance from the box's origin to its farthest point against a direction.

$$h = |n| \cdot e - n \cdot c$$

Read it as: the :term[dot product]{id=dot-product} of $|n|$ and $e$, minus the dot product of $n$ and $c$. Here $h$ is the lift in meters and $n$ is the unit normal.
$|n|$ is $n$ with every component made positive. $e$ is the half-size of the box along each axis. $c$ is the box's
center relative to its origin.

The first term is how far the box reaches against the normal from
its center; the second moves that reach from the center to the origin. The asset's translation is $P + h\,n$.

Check the limits. A box with its origin at the bottom center has $c = (0, 0.5, 0)$ and $e = (0.5, 0.5, 0.5)$. On flat
ground $h = 0.5 - 0.5 = 0$, so it stays on the point. A normal along $x$ gives $h$ equal to the extent along $x$ minus
the center along $x$, the right lift for a wall. All of this holds for a box aligned with the axes; Strata keeps
the placed bounds axis-aligned, so a rotated asset may float by the slack between its true shape and its box.

## A toy version

The toy has one endless ramp instead of a scene, and no grid and no snapping. A ray either hits the ramp or does
not. On a hit it rests the box with the formula above; on a miss it puts the box's center on the ray at a fixed
distance. Find the two paths in `Place`, and note how little `RestOn` needs.

```cpp sketch="editor-placement-toy.cpp"
// A toy of placement: one ramp, one ray, and a box that rests on what the ray hits.
#include <glm/glm.hpp>

#include <cstdio>
#include <optional>

struct Ray
{
	glm::vec3 Origin;
	glm::vec3 Direction;
};

struct Box
{
	glm::vec3 Min;
	glm::vec3 Max;
};

// The ramp is an endless plane through the origin that rises 30 degrees along +X.
constexpr glm::vec3 c_RampNormal(-0.5f, 0.8660254f, 0.0f);
constexpr float c_FallbackDistance = 10.0f;

// The distance along the ray to the ramp, or nothing when the ray looks away from its face.
std::optional<float> HitRamp(const Ray& ray)
{
	const float facing = glm::dot(c_RampNormal, ray.Direction);
	if (facing >= 0.0f)
		return std::nullopt;
	return -glm::dot(c_RampNormal, ray.Origin) / facing;
}

// The translation that puts the box's side facing the surface on the point.
glm::vec3 RestOn(const glm::vec3& point, const glm::vec3& normal, const Box& box)
{
	const glm::vec3 center = (box.Min + box.Max) * 0.5f;
	const glm::vec3 extents = (box.Max - box.Min) * 0.5f;
	const float behind = glm::dot(glm::abs(normal), extents) - glm::dot(normal, center);
	return point + normal * behind;
}

void Place(const char* label, const Ray& ray, const Box& box)
{
	glm::vec3 translation;
	const char* source;
	if (const std::optional<float> distance = HitRamp(ray))
	{
		source = "surface";
		translation = RestOn(ray.Origin + ray.Direction * *distance, c_RampNormal, box);
	}
	else
	{
		source = "inFront";
		translation = ray.Origin + ray.Direction * c_FallbackDistance - (box.Min + box.Max) * 0.5f;
	}
	std::printf("%s: %s, translation (%.3f, %.3f, %.3f)\n", label, source, translation.x, translation.y, translation.z);
}

int main()
{
	const Box crate { glm::vec3(-0.5f), glm::vec3(0.5f) };
	Place("ray down at x = 2", Ray { glm::vec3(2.0f, 5.0f, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f) }, crate);
	Place("ray into the sky", Ray { glm::vec3(0.0f, 5.0f, 10.0f), glm::vec3(0.0f, 0.6f, -0.8f) }, crate);
	return 0;
}
```

```text output-of="editor-placement-toy.cpp"
ray down at x = 2: surface, translation (1.658, 1.746, 0.000)
ray into the sky: inFront, translation (0.000, 11.000, 2.000)
```

1. **Lines 26–28:** a ray whose direction points along the normal looks away from the face, so it misses. A hit needs
   the ray to go against the normal.
2. **Line 37:** the support function: the box's reach against the normal minus the normal's share of its center.
3. **Lines 45–48:** on a hit the box rests on the point where the ray meets the surface.
4. **Lines 52–53:** on a miss nothing is below, so the box's center sits on the ray.

The first ray lands on the ramp at height 1.155 and the translation is about 0.34 left and 0.59 above the hit
point, the 0.683 along the normal. The second ray climbs and meets nothing, so the box is centered 10 m along it. The
real code differs in what it hits and in what it does between a hit and a miss.

## The real code

### From a pixel to a ray

:since[0.8.0] The panel first turns a point of the image into :term[normalized device coordinates]{id=normalized-device-coordinates} (NDC). Here $x$ runs from $-1$ at the left
edge to $1$ at the right, and $y$ runs from $-1$ at the bottom to $1$ at the top. For a pixel $(p_x, p_y)$ of an image of
size $(w, h)$ the panel computes $(2p_x / w - 1,\ 1 - 2p_y / h)$. In a 1280 by 720 image the pixel (640, 360) maps to
$(0, 0)$ and the pixel (0, 0) to $(-1, 1)$, the top-left corner.

```cpp src="StrataEditor/src/Editor/EditorPlacement.cpp#L97-L103"
Ray MakeViewRay(const SceneCamera& camera, const glm::vec2& ndc)
{
	// Through the rotation-only view: the ray's origin stays near zero, so the camera's position is added exactly once
	// instead of being lost in the inverse of a matrix that holds it.
	const glm::mat4 rotation(glm::mat3(camera.View));
	const Ray relative = Ray::FromNDC(ndc, glm::inverse(camera.Projection * rotation));
	return Ray(camera.Position + relative.Origin, relative.Direction);
```

The ray comes from the inverse of the projection times the view. If the :term[view matrix]{id=view-matrix} held the camera's position, the
inverse would carry large numbers, and a 32-bit float near 100,000 m can only tell positions 0.0078 m apart. So the
code keeps only the view's rotation, builds the ray near the origin, and adds the camera's position once at the end.
`MakeRayRequest` then builds the request: it :term[normalizes]{id=normalization} the direction through `Ray`, clamps the fallback distance
to the range 0.5 m to 500 m, and stores the snapping step. The command reads the floats back from its :term[JSON]{id=json} parameters;
a float widens to a double and narrows back without change, so both callers build equal requests.

### Casting against the scene

`SceneRaycast::Cast` answers a question the physics world cannot: what does the scene draw under this ray? It asks the
:term[render scene's]{id=render-scene} :term[spatial index]{id=spatial-index} for the boxes near the ray, tests those boxes in order of entry, and tests exact triangles
only in the boxes that can still hold a nearer hit.

```cpp src="StrataEditor/src/Editor/SceneRaycast.cpp#L134-L169"
// The candidates the ray enters, nearest first: a box nearer than the best hit so far may hold a nearer surface.
std::vector<std::pair<float, uint32_t>> candidates;
for (const uint32_t proxy : proxies)
{
	const entt::entity handle = renderScene.GetEntity(proxy);
	if (handle == entt::null || (renderScene.GetProxyFlags(proxy) & RenderProxyFlags::Active) == 0 || ignored.contains(handle))
		continue;
	if (const std::optional<float> entry = IntersectRayAABB(ray, renderScene.GetWorldBounds(proxy)); entry && *entry <= length)
		candidates.emplace_back(*entry, proxy);
}
std::sort(candidates.begin(), candidates.end());

std::optional<SceneRayHit> best;
for (const auto& [entry, proxy] : candidates)
{
	if (best && entry >= best->Distance)
		break;
	const Entity entity(renderScene.GetEntity(proxy), &scene);
	const uint32_t slot = renderScene.GetMeshSlot(proxy);
	if (slot == RenderScene::c_InvalidIndex)
		continue;
	const AssetHandle meshHandle = renderScene.GetMeshHandle(slot);
	const Ref<Mesh> mesh = assets ? assets->GetAsset<Mesh>(meshHandle) : nullptr;
	if (mesh && !mesh->GetPositions().empty() && !mesh->GetIndices().empty())
	{
		if (std::optional<SceneRayHit> hit = CastMesh(*mesh, renderScene.GetWorldTransform(proxy), ray, best ? best->Distance : length))
		{
			hit->HitEntity = entity;
			best = hit;
		}
		continue;
	}
	// Not loaded: its bounds stand in.
	const AABB& bounds = renderScene.GetWorldBounds(proxy);
	const glm::vec3 point = ray.GetPoint(entry);
	best = SceneRayHit { entity, point, GetBoxNormal(bounds, point), entry, false };
```

1. **Lines 139–142:** a box near the ray is skipped when it is inactive or ignored, and kept when the ray enters its world box within the length.
2. **Line 144:** candidates are sorted by the distance at which the ray enters them.
3. **Line 149:** the search stops at the first box that starts beyond the best hit.
4. **Line 159:** a loaded mesh gets the exact triangle test, limited to the best distance so far.
5. **Lines 166–169:** a mesh that is not loaded stands in with its box: the entry point and the face it lies on.

The toy's single plane becomes a search with a stopping rule, and a fallback when a mesh is not loaded.

### Deciding where

`Place` chooses a source for the resting point, in this order: the point given by the request, the first surface the
ray hits, the grid plane, a point in front. The returned `Placement` records the source as `surface`, `grid`,
`inFront` or `point`.

```cpp src="StrataEditor/src/Editor/EditorPlacement.cpp#L131-L162"
// Where: the given point, else what the ray hits, else the grid plane, else in front of the camera.
const Ray& ray = request.CastRay;
if (request.At)
{
	placement.Source = PlacementSource::Point;
	placement.RestingOn = *request.At;
	const float length = glm::length(placement.RestingOn.Normal);
	placement.RestingOn.Normal = length > 0.0f && std::isfinite(length) ? placement.RestingOn.Normal / length : glm::vec3(0.0f, 1.0f, 0.0f);
}
else if (const std::optional<SceneRayHit> hit = SceneRaycast::Cast(scene, ray, request.MaxDistance))
{
	placement.Source = PlacementSource::Surface;
	placement.RestingOn = ToSurface(*hit);
	placement.HitEntity = hit->HitEntity;
}
else
{
	if (request.RequireSurface)
		return std::nullopt;
	const float reach = std::min(request.MaxDistance, c_GridFallbackDistance);
	const float gridDistance = std::abs(ray.Direction.y) > 1.0e-6f ? -ray.Origin.y / ray.Direction.y : -1.0f;
	if (gridDistance > 0.0f && gridDistance <= reach)
	{
		placement.Source = PlacementSource::Grid;
		placement.RestingOn = Surface { ray.GetPoint(gridDistance), glm::vec3(0.0f, ray.Direction.y < 0.0f ? 1.0f : -1.0f, 0.0f), false };
	}
	else
	{
		// Never std::clamp with bounds that may cross: a reach under the minimum distance wins.
		const float distance = std::min(std::max(request.FallbackDistance, c_MinFallbackDistance), reach);
		placement.Source = PlacementSource::InFront;
		placement.RestingOn = Surface { ray.GetPoint(distance), glm::vec3(0.0f, 1.0f, 0.0f), false };
```

1. **Lines 133–138:** a request that gives a point skips the ray, and its normal is made unit length.
2. **Line 140:** the first surface the ray hits wins, and its entity is recorded.
3. **Lines 148–149:** with `RequireSurface` a miss returns nothing.
4. **Lines 151–155:** the ray meets the plane $y = 0$ only when it is not parallel to it, ahead of the origin and within the reach.
5. **Line 160:** otherwise the point is in front, never nearer than 0.5 m and never beyond the reach.

The grid fallback exists because an empty scene still has a visible ground: a ray that meets the plane $y = 0$ within
500 m rests there. Beyond that, or for a ray that climbs, the box is centered on the ray at the fallback distance. With
`RequireSurface` a miss places nothing.

### Snapping

**Snapping** puts the placement point on a grid of a given step in meters, as the :term[gizmo]{id=gizmo-start} does when it moves things. The
step comes from the Scene view's snap setting, and holding **Ctrl** inverts it. Snapping rounds only the axes across the
surface: on a floor, $x$ and $z$ snap and the height stays.

```cpp src="StrataEditor/src/Editor/EditorPlacement.cpp#L166-L192"
// Snapping: along the surface (the normal's dominant axis keeps its value), as the gizmo snaps translations.
if (request.Snap && *request.Snap > 0.0f)
{
	const float step = *request.Snap;
	const glm::vec3 normal = placement.RestingOn.Normal;
	const glm::vec3 magnitude = glm::abs(normal);
	int axis = 1;
	if (placement.Source == PlacementSource::Surface || placement.Source == PlacementSource::Point)
		axis = magnitude.x > magnitude.y && magnitude.x > magnitude.z ? 0 : (magnitude.y >= magnitude.z ? 1 : 2);
	glm::vec3 snapped = placement.RestingOn.Point;
	for (int i = 0; i < 3; i++)
	{
		if (i != axis)
			snapped[i] = std::round(snapped[i] / step) * step;
	}
	placement.RestingOn.Point = snapped;
	// On ground facing up, the height under the snapped point (still at the hit's height when nothing is there).
	if (placement.Source == PlacementSource::Surface && axis == 1 && normal.y > 0.0f)
	{
		const Ray down(snapped + glm::vec3(0.0f, c_SnapLift, 0.0f), glm::vec3(0.0f, -1.0f, 0.0f));
		if (const std::optional<SceneRayHit> under = SceneRaycast::Cast(scene, down, c_SnapLift + c_SnapDepth))
		{
			placement.RestingOn = ToSurface(*under);
			placement.HitEntity = under->HitEntity;
		}
	}
	placement.Snapped = true;
```

1. **Lines 172–174:** a guess always snaps across the height; a surface or point picks the normal's largest component.
2. **Lines 176–180:** the two other axes round to a multiple of the step.
3. **Lines 183–190:** on ground facing up, a ray down at the snapped point finds the new height.
4. **Line 192:** the result reports that it was snapped.

The height of the surface can change under the snapped point. So on ground facing up, the code casts one ray straight
down from 1 m above that point, reaching 1,000 m below it. The placement then rests on whatever the ray hits.

### Resting and measuring

`RestOn` is the formula above in a few lines. It makes the normal unit length, reads the box's center and half-size,
and moves the point along the normal by the support distance. Look at the line that computes `behind`.

```cpp src="StrataEditor/src/Editor/EditorPlacement.cpp#L208-L212"
const glm::vec3 normal = glm::length(surface.Normal) > 0.0f ? glm::normalize(surface.Normal) : glm::vec3(0.0f, 1.0f, 0.0f);
const glm::vec3 center = bounds.GetCenter();
const glm::vec3 extents = bounds.GetExtents();
const float behind = glm::dot(glm::abs(normal), extents) - glm::dot(normal, center);
return surface.Point + normal * behind;
```

The bounds this function gets come from `AssetBounds`: the box of what the asset
draws, around the origin of its first root, with children and skinned meshes in their rest pose. A result is cached by
the asset's :term[content stamp]{id=content-stamp}, so it is worked out again only when the asset or something it uses changed. While a mesh is
still loading, the result is marked pending and holds placeholder boxes.

### The ghost

The **placement ghost** is the preview of where a dragged asset will land: a box drawn over the finished Scene view
image, with a label at the pointer. On a surface the box is drawn tested against depth, its hidden edges at 30 % of
the color's strength, and a ring marks the touching point. For a guess (`grid` or `inFront`) only a quieter box is
drawn on top, and while the size loads, a marker.

`PlacementPreview` writes nothing, and it casts again only when its key changes. The key holds the asset, the ray's
origin and direction, the distances, the snapping step, the render scene and its update count, the :term[asset manager's]{id=asset-manager} content
version and three flags. A still pointer over a still scene therefore casts once. On release, the panel runs
`asset.place` with `MakeDropParameters`: the same ray floats, so the drop is the ghost's request.

### The command, and the other users

`asset.place` takes exactly one of a ray, a Scene view pixel (`viewport`) or a point with a normal. It returns the
root's id, `placedOn`, the point, the normal, the translation and the bounds. While a prefab or model loads it waits
for up to 30 s and fails when the asset has not loaded by then. Once it has, the command waits up to 5 s more for its
size, then places by the size known so far and reports `bounds.pending`.

The command fixes its request when it starts, so a camera that moves while it waits changes nothing.
The `scene.raycast` command casts without placing and answers `hit`, `entity`, `point`, `normal`, `distance` and
`onTriangle`.

Two more users of the same cast exist. `FindPivotSurface` finds what lies under the point the view orbits: a ray
straight down from 0.01 m above the target, else the ray through the view's center, else the target itself. The create
menus put new entities there. `entity.dropToGround` casts five rays down from the bottom of an entity's bounds, the
center and four corners pulled 10 % inward, and moves the entity down by the shortest distance.

## A worked example

:::example
A project holds `Prefabs/Crate.stprefab`, a crate of 1 m with its origin at its center, and a ramp that rises 30
degrees along $x$ from the origin. The first call rays straight down at $x = 2$:

```json
{ "asset": "Prefabs/Crate.stprefab", "ray": { "origin": [2, 5, 0], "direction": [0, -1, 0] } }
```

The ray meets the ramp at $(2, 1.155, 0)$ with the normal $(-0.5, 0.866, 0)$, so `placedOn` is `surface`. The lift is
0.683 along the normal, and the translation is $(2 - 0.342, 1.155 + 0.591, 0) = (1.658, 1.746, 0)$. The crate keeps its
upright pose and touches the ramp along its lowest edge. A drag whose pointer ray is the same floats gives the same
translation, and its ghost shows that box with the ring at $(2, 1.155, 0)$.

The second call points into the sky:

```json
{ "asset": "Prefabs/Crate.stprefab", "ray": { "origin": [0, 5, 10], "direction": [0, 0.6, -0.8] } }
```

The ray climbs, so it never meets the grid plane, and nothing is hit. With no `fallbackDistance`, the default is 10 m.
`placedOn` is `inFront`, the point is $(0, 11, 2)$ and the crate's center goes there. The ghost is the quieter box at
the same place. With `requireSurface` set to true the call would fail and place nothing.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Read the depth under the pointer from a picture | Selection by picking in many editors | Exact for what is on screen, skinned meshes included | A frame of delay, and nothing for a script with no window |
| Cast against physics colliders | Gameplay queries, see the physics pages | One answer for the editor and the game | Assets without colliders cannot be hit |
| Place by bounds only | Simple tools | No waiting for meshes | A crate on a ramp hovers above the real surface |
| Drop with a physics simulation | Some games' own tools | A resting pose that follows the shape | Many frames, no fixed answer, colliders required |
| Test every triangle of the scene | Small tools | No index to keep in step | Cost grows with the whole scene per cast |

## How it is tested

The suite `Editor.Placement` in `StrataTests/src/Editor/PlacementTests.cpp` holds the checks of the logic:

- Rays hit triangles nearest first and skip what is being placed.
- A placement rests on a surface, else on the grid within 500 m, else in front of the camera.
- Snapping puts the point on the step and finds the height there.
- The view's ray goes through the pointer, also far from the origin.
- `AssetBounds` measures a pending template again only when something it waits for was published.
- `scene.raycast`, `asset.place` (one undo step, its refusals and its wait) and `entity.dropToGround` do what their
  descriptions say, and new content rests under the view's pivot.

The suite `Editor.UI.Placement` drives drags: a hover changes nothing until the drop, a still pointer casts nothing,
and **Escape** cancels the drag. Run one suite with `StrataTests.exe --test-suite=Editor.Placement` from the build's
`bin` folder.

## Changing it safely

Extension points are few. A new kind of resting place is a new `PlacementSource` value, with its string, its ghost
drawing and its entry in the command's description. A new request option goes into `PlacementRequest`,
`MakeRayRequest`, `MakeDropParameters` and the command's schema together, or the drop and the command stop agreeing.

- Find what is under a point with `SceneRaycast::Cast`, never with a loop over the scene's entities: the render scene's
  index makes it cheap, and the loop is paid on every call.
- Never block a frame on an asset: `asset.place` returns a poll function and is registered as one that may defer.
- Never let the ghost write: a hover that creates an entity would leave undo steps behind the person's back.
- Reach assets through the scene's asset manager, so a scene opened for another project sees its own meshes.

Before a commit, run both suites, and run the commands of the editor's feature test.

## Summary

- A point of the image becomes a ray through normalized device coordinates, with the camera position added after the rotation so far-away scenes stay exact.
- `Place` tries a given point, the first surface, the grid plane within 500 m, then a point in front; snapping rounds the axes across the normal.
- A box rests on a surface at the point plus the normal times $|n| \cdot e - n \cdot c$.
- The drop, its ghost and `asset.place` build one request from the same floats, and the ghost writes nothing.

## Check yourself

1. A prefab's origin is the center of a 2 m cube. It is placed on flat ground facing up. How far above the hit point is
   its origin?

   - A. 0 m, on the point.
   - B. 1 m.
   - C. 2 m.
   - D. 0.5 m.

   :::answer{tests="rest-box"}
   B. The half-size is 1 m and the center is the origin, so $h = 1$. A is the buried answer. C uses the full height. D
   belongs to the 1 m crate of the text.
   :::

2. The ray has origin $(0, 2, 0)$ and direction $(0, 1, 0)$ in an empty scene, with a fallback distance of 10 m. Where
   does the box's center land, and what is `placedOn`?

   :::answer{tests="place-decision"}
   The ray climbs, so it never meets the plane $y = 0$ in front of it. Nothing is hit, so `placedOn` is `inFront`, and the
   center goes 10 m along the ray, to $(0, 12, 0)$.
   :::

3. Why is a pixel's ray built from a rotation-only view matrix with the camera's position added afterwards?

   :::answer{tests="ray-from-pixel"}
   The inverse of a matrix that holds a large position loses digits, and a float near 100,000 m has gaps of 0.0078 m.
   With only the rotation, the origin stays near zero, and adding the position once loses almost nothing.
   :::

4. A person hovers over a still scene. An import then finishes. Does the ghost cast again? And what changes in the scene
   while the pointer moves?

   :::answer{tests="one-request"}
   The ghost casts again, because the asset manager's content version is in the key. Nothing changes in the scene: the ghost
   writes no entity, undo step, selection or version.
   :::

## Exercises

1. **Basic.** A box has its origin at the bottom center: $e = (0.5, 0.5, 0.5)$, $c = (0, 0.5, 0)$. It rests on the ramp
   with normal $(-0.5, 0.866, 0)$. How far along the normal does it move?

   :::answer[Worked solution]{tests="rest-box"}
   First term: $0.5 \cdot 0.5 + 0.866 \cdot 0.5 = 0.683$. Second term: $n \cdot c = 0.866 \cdot 0.5 = 0.433$. So $h = 0.683 - 0.433 = 0.25$. The
   translation is the hit point plus $(-0.125, 0.217, 0)$.
   :::

2. **Medium.** Snap the point $(3.27, 1.89, -0.81)$ to a step of 0.5, on a floor and on a wall that faces $+x$. Write a
   program that prints both.

   :::answer[Worked solution]{tests="place-decision" solution="sketches/editor-placement-snap.cpp"}
   The axis the normal points along keeps its value; the other two round to the step.

   ```cpp sketch="editor-placement-snap.cpp"
   // Snapping a placement point along a surface: the axis of the normal keeps its value.
   #include <glm/glm.hpp>

   #include <cmath>
   #include <cstdio>

   glm::vec3 Snap(const glm::vec3& point, const glm::vec3& normal, float step)
   {
   	const glm::vec3 magnitude = glm::abs(normal);
   	const int axis = magnitude.x > magnitude.y && magnitude.x > magnitude.z ? 0 : (magnitude.y >= magnitude.z ? 1 : 2);
   	glm::vec3 snapped = point;
   	for (int i = 0; i < 3; i++)
   	{
   		if (i != axis)
   			snapped[i] = std::round(snapped[i] / step) * step;
   	}
   	return snapped;
   }

   int main()
   {
   	const glm::vec3 point(3.27f, 1.89f, -0.81f);
   	const glm::vec3 floor = Snap(point, glm::vec3(0.0f, 1.0f, 0.0f), 0.5f);
   	const glm::vec3 wall = Snap(point, glm::vec3(1.0f, 0.0f, 0.0f), 0.5f);
   	std::printf("floor: (%.2f, %.2f, %.2f)\n", floor.x, floor.y, floor.z);
   	std::printf("wall: (%.2f, %.2f, %.2f)\n", wall.x, wall.y, wall.z);
   	return 0;
   }
   ```

   ```text output-of="editor-placement-snap.cpp"
   floor: (3.50, 1.89, -1.00)
   wall: (3.27, 2.00, -1.00)
   ```

   1. **Line 10:** the dominant axis of the normal.
   2. **Lines 12–15:** the other axes round to a multiple of the step.
   :::

3. **Hard.** Add a `stackOn` option to `asset.place` that rests the asset on top of a given entity's bounds. Say what
   the handler does.

   :::answer[Worked solution]{tests="one-request"}
   Read the entity like `parent`, and keep its :term[universally unique identifier]{id=uuid} (UUID) in the job, since the entity may vanish while the command waits.
   In the poll, measure `SceneBounds::GetEntityBounds` and build the point form of the request: the point is the top
   center of that box and the normal is up. `Place` then rests the asset by its own bounds. Refuse `stackOn` together
   with `ray`, `viewport` or `point`, and fail with a reason when the entity is gone.
   :::

4. **Hard.** Trace it yourself: drop a prefab on the Scene view, then call `asset.place` at the same pixel. Put a
   breakpoint in `MakeRayRequest` each time. How do the two requests compare?

   :::answer[Worked solution]{tests="one-request"}
   The drop calls `MakeRayRequest` in `StrataEditor/src/Editor/Commands/PlacementCommands.cpp`, inside the handler of
   `asset.place`, because the release runs that command with `MakeDropParameters`. The command call reaches the same
   function through its `viewport` branch, with `MakeViewRay`'s origin and direction. At the same pixel, both show the
   same origin, direction, maximum distance and fallback distance to the last digit. The breakpoint also stops while
   you drag, because `PlacementPreview::Update` calls the function for the ghost each time its key changes.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/SceneRaycast.cpp`: `SceneRaycast::Cast`.
- `StrataEditor/src/Editor/EditorPlacement.cpp`: `Place`, `RestOn`, `MakeViewRay`, `MakeRayRequest`, `FindPivotSurface`.
- `StrataEditor/src/Editor/PlacementPreview.cpp`: the ghost's key and `MakeDropParameters`.
- `StrataEditor/src/Editor/AssetBounds.cpp`: `AssetBounds::Measure`.
- `StrataEditor/src/Editor/Commands/PlacementCommands.cpp`: `scene.raycast` and `asset.place`.
- `StrataTests/src/Editor/PlacementTests.cpp`: the suites `Editor.Placement` and `Editor.UI.Placement`.

## Further reading

- Real-Time Collision Detection, Christer Ericson: rays against boxes and triangles, and support functions (advanced).
- Real-Time Rendering, Akenine-Moller, Haines and Hoffman: picking and bounding volumes (intermediate).
