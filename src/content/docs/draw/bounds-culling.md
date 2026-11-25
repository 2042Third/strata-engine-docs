---
id: draw/bounds-culling
title: "Bounding volumes, frustums and the spatial index"
description: "How Strata finds the proxies a camera can see, exactly and in time that follows what is visible, and how big each looks on screen."
kind: internals
size: L
tracks: [E]
needs: [draw/render-scene, basics/math-geometry, core/math]
time: 95
learn:
  - id: transform-bounds
    text: compute the box that bounds a rotated box with Arvo's method and explain the corner mistake
  - id: frustum-test
    text: explain how six planes come from a view-projection matrix and why the positive vertex test is conservative
  - id: grid-exact
    text: explain why the loose grid answers exactly like a scan of every box
  - id: screen-fraction
    text: compute a screen fraction for a perspective and an orthographic camera
  - id: trace-query
    text: trace a box through the frustum query, taken with its cell or tested alone
since: 0.3.0
status: final
---

A camera sees a small part of a scene, and drawing the rest wastes the frame. This page covers the part of Strata that decides, every frame, which proxies the camera can see. The answer must be exact: it equals what a test of every proxy would give. The time it takes follows the number of visible proxies, not the number in the scene, and the same code says how large each visible proxy looks on screen. It does not decide what hides behind other objects, which level of detail to draw, or which casters the sun's shadow needs.

## The problem and how engines solve it

Suppose a scene holds 100,000 proxies and the camera sees 3,000 of them. The plain way to find those is to test the :term[bounding box]{id=bounding-box} of each proxy against the camera. A box test costs a few dozen operations, so 100,000 tests cost a few million. The cost grows in step with the scene, which the page on [data structures](../basics/data-structures.md) calls linear growth. A game that doubles its scene doubles the cost, although the camera still sees the same 3,000 proxies.

Engines answer by sorting objects into a structure that lets a query skip whole groups at once. Five families are common.

- A :term[bounding volume]{id=bounding-volume} hierarchy wraps objects in boxes, and those boxes in larger boxes, up to one root. A query walks down from the root and skips every branch whose box is outside.
- An octree cuts space into eight equal cubes, then each cube again, as deep as needed. An object lives in the smallest cube that holds it.
- A loose octree gives each cube a margin, so an object that crosses a cube edge still lives in one cube.
- A uniform grid cuts space into equal cells and lists the objects of each cell.
- Hashing stores the cells of a grid in a :term[hash table]{id=hash-map} keyed by cell coordinates, so empty space costs nothing.

The families trade query speed against the cost of change. A hierarchy built for still objects queries fast, but moving objects stretch the boxes above them, so the boxes need repair. Octrees move objects between cubes, which can mean walking many levels. A grid moves an object with one calculation, but one cell size suits only one size of object.

Strata's proxies move every frame: animated characters, physics bodies, a person's edits. So Strata chooses the structure whose edit is cheapest, a grid, and repairs its weakness with two ideas that later sections show. A **spatial index** is a structure that finds the objects of a region of space without testing all of them; Strata's is the class `SpatialIndex`.

| Technique | Query | Moving an object | Weak point |
| --- | --- | --- | --- |
| Test every box | Linear in the scene | Nothing to update | Slow in large scenes |
| Hierarchy of boxes | Fast, follows the visible part | Fit the boxes above again | Repair after every frame of motion |
| Octree | Fast | Walk between cubes | Objects on cube edges |
| Uniform grid | Fast for one object size | One calculation | Huge and tiny objects together |
| :term[Hash]{id=hash} of cells | As the grid | One calculation plus a lookup | The same single cell size |

A **loose grid** is a grid whose objects live in the cell of their centre and whose cells keep the box that covers their objects, so an object may reach beyond its cell. The rest of the page builds up to it.

## Bounding volumes and their transforms

A mesh can hold a million triangles, and no culling test can afford to look at each. So every proxy carries a **bounding volume**, a simple shape that holds the whole mesh. If the shape is outside the view, the mesh is too, and one test replaces a million.

Three shapes are common. A sphere is one centre and one radius, and it stays the same when the object turns. An axis-aligned box (:term[AABB]{id=axis-aligned-bounding-box}) has faces parallel to the world's axes and stores a minimum and a maximum corner. An oriented box turns with the object, fits it tightly and costs more to test. Strata keeps [the `AABB` type](../core/math.md) for the index and derives a sphere from it when it needs one.

Strata stores the box in the mesh's own space, but the index needs it in :term[world space]{id=world-space}. When the entity moves, the box must follow. For a move that only translates, add the offset. For a rotation, a tempting shortcut transforms the two stored corners and takes their box. The shortcut is wrong, as a small case shows.

Take a box 4 wide and 2 tall, centred on the origin: its corners run from (-2, -1) to (2, 1). Turn it by 45 degrees. Turning the two stored corners gives (-0.71, -2.12) and (0.71, 2.12), whose box reaches only 0.71 from the centre along x. But the corner (2, -1) turns to x = 2.12, outside that box. The sketch computes both answers.

```cpp sketch="draw-bounds-culling-corners.cpp"
#include <cmath>
#include <cstdio>

int main()
{
	const float c = std::cos(0.785398f);
	const float s = std::sin(0.785398f);
	const float halfX = 2.0f;
	const float halfY = 1.0f;
	// Wrong: turn only the corners (-2, -1) and (2, 1) and keep the box of those two.
	const float wrongX = std::abs(halfX * c - halfY * s);
	const float wrongY = std::abs(halfX * s + halfY * c);
	// Right (Arvo): add up how far each half size reaches along each axis.
	const float rightX = std::abs(c) * halfX + std::abs(s) * halfY;
	const float rightY = std::abs(s) * halfX + std::abs(c) * halfY;
	// The corner (2, -1) turns to x = 2c + s.
	const float probe = halfX * c + halfY * s;
	std::printf("wrong half sizes: %.3f %.3f\n", wrongX, wrongY);
	std::printf("right half sizes: %.3f %.3f\n", rightX, rightY);
	std::printf("corner (2, -1) turns to x = %.3f\n", probe);
}
```

```text output-of="draw-bounds-culling-corners.cpp"
wrong half sizes: 0.707 2.121
right half sizes: 2.121 2.121
corner (2, -1) turns to x = 2.121
```

1. **Lines 10–12:** the shortcut turns two corners and keeps their box, so x reaches only 0.707.
2. **Lines 13–15:** Arvo's method adds how far each half size reaches along each axis, and gives 2.121 both ways.
3. **Line 17:** the corner the shortcut never saw turns to x = 2.121, outside the wrong box.

The wrong box is too small, so an object would vanish at the edge of the screen while a part of it is still in view. The right half sizes come from a method by Arvo. Each half size of the new box is a sum over the three old half sizes: the absolute value of a matrix entry times the half size. The mathematics of rotation matrices is on the [geometry](../basics/math-geometry.md) page. The result is the smallest axis-aligned box that holds the turned one.

```cpp src="Strata/src/Strata/Math/AABB.cpp#L7-L25"
AABB AABB::Transformed(const glm::mat4& transform) const
{
	if (!IsValid())
		return AABB();

	// Arvo's method: transform the center, then accumulate the absolute basis contributions of the extents.
	const glm::vec3 center = GetCenter();
	const glm::vec3 extents = GetExtents();
	const glm::vec3 newCenter = glm::vec3(transform * glm::vec4(center, 1.0f));

	glm::vec3 newExtents(0.0f);
	for (int axis = 0; axis < 3; axis++)
	{
		newExtents[axis] = glm::abs(transform[0][axis]) * extents.x
			+ glm::abs(transform[1][axis]) * extents.y
			+ glm::abs(transform[2][axis]) * extents.z;
	}
	return AABB(newCenter - newExtents, newCenter + newExtents);
}
```

1. **Lines 9–10:** an empty box stays empty.
2. **Lines 13–15:** the centre moves like a point, with the full matrix.
3. **Lines 18–23:** each new half size sums the absolute matrix entries times the old half sizes, so no sign can cancel.
4. **Line 24:** the new box is the new centre plus and minus the new half sizes.

The new box can be larger than needed: it holds the turned box, not the object, so a turning object grows its box by a bounded amount. That slack is the price of cheap tests, and it never makes a visible object disappear.

## Frustum culling

The camera's visible region is a **frustum**, a pyramid with its tip cut off, whose six sides are two depth limits and four edges of the screen. Each side is a plane, and a plane splits space into an inner side and an outer side. A point is inside the frustum when it is on the inner side of all six planes. Strata stores a plane as four numbers: a unit normal that points inward, and a distance. The number $n \cdot p + d$ is then the :term[signed distance]{id=signed-distance} of point $p$ from the plane: positive inside, zero on the plane and negative outside.

**Frustum culling** is skipping every object whose bounding volume lies wholly outside the camera's frustum. It needs the six planes, and the camera already holds a matrix that describes them.

### Planes from the matrix

The view-projection matrix turns a world point into :term[clip space]{id=clip-space}, four numbers $(x, y, z, w)$. A point is on screen when $-w \le x \le w$, $-w \le y \le w$ and $0 \le z \le w$. The depth range from 0 to 1 is the rule of Strata's [clip space](../gpu/coordinates.md). Each limit is a row of the matrix: the clip $x$ of a point is the :term[dot product]{id=dot-product} of the matrix's first row with the point, extended by a 1. The clip $w$ is the dot product of the fourth row with it.

So the left limit, $x + w \ge 0$, is the dot product of the sum of the first and fourth rows with the point. The right limit subtracts the first row from the fourth. The bottom and top use the second row, and depth uses the third. Further reading names the paper that published this method.

Strata divides each plane by the length of its normal, which makes the distance real units. Strata uses reversed depth, where the :term[near plane]{id=near-plane} has depth 1 and the :term[far plane]{id=far-plane} depth 0. So the third row alone is the far plane, and the fourth row minus the third is the near plane. A projection with an infinite far plane has a third row without any direction, only a number. Dividing that plane would divide by zero, so Strata replaces it with the plane (0, 0, 0, 1), which every point passes, and the far plane never rejects anything.

```cpp src="Strata/src/Strata/Math/Frustum.cpp#L12-L35"
void Frustum::Update(const glm::mat4& viewProjection)
{
	// Gribb/Hartmann plane extraction. glm is column-major: row i is (m[0][i], m[1][i], m[2][i], m[3][i]).
	const glm::vec4 row0(viewProjection[0][0], viewProjection[1][0], viewProjection[2][0], viewProjection[3][0]);
	const glm::vec4 row1(viewProjection[0][1], viewProjection[1][1], viewProjection[2][1], viewProjection[3][1]);
	const glm::vec4 row2(viewProjection[0][2], viewProjection[1][2], viewProjection[2][2], viewProjection[3][2]);
	const glm::vec4 row3(viewProjection[0][3], viewProjection[1][3], viewProjection[2][3], viewProjection[3][3]);

	m_Planes[0] = row3 + row0; // Left   (x >= -w)
	m_Planes[1] = row3 - row0; // Right  (x <= w)
	m_Planes[2] = row3 + row1; // Bottom (y >= -w)
	m_Planes[3] = row3 - row1; // Top    (y <= w)
	m_Planes[4] = row2;        // Depth 0 (z >= 0): far plane with reversed Z
	m_Planes[5] = row3 - row2; // Depth 1 (z <= w): near plane with reversed Z

	for (glm::vec4& plane : m_Planes)
	{
		const float length = glm::length(glm::vec3(plane));
		if (length > 0.0f)
			plane /= length;
		else
			plane = glm::vec4(0.0f, 0.0f, 0.0f, 1.0f); // Degenerate plane (infinite far): never culls
	}
}
```

1. **Lines 15–18:** glm stores matrices by column, so each row is gathered from four columns.
2. **Lines 20–23:** left, right, bottom and top add or subtract the first or second row from the fourth.
3. **Lines 24–25:** the two depth planes, the far one first because of reversed depth.
4. **Lines 29–33:** each plane is scaled to unit length; a plane without a direction becomes the always-passing plane.

### Testing a box against a plane

A point test is one dot product per plane. A box has eight corners, but only two matter for one plane. The **positive vertex test** asks whether the corner furthest along the plane's normal is behind the plane: if even that corner is behind, the whole box is behind. Finding the corner needs no search: for each axis, take the maximum when the normal's component is zero or positive and the minimum when it is negative.

A worked case uses a 2D camera at the origin looking along $y$, with a 90 degree view, near distance 1 and far distance 10. Its planes are $x + y \ge 0$, $-x + y \ge 0$, $y \ge 1$ and $y \le 10$, the first two divided by 1.41 to give unit normals. The sketch tests four boxes. For each plane it also takes the opposite corner, the nearest to the plane's back side, which tells whether the box is wholly inside.

```cpp sketch="draw-bounds-culling-planes.cpp"
#include <cmath>
#include <cstdio>

struct Plane { float X, Y, D; }; // Inward normal and distance: inside when X*x + Y*y + D >= 0

int main()
{
	const float k = std::sqrt(0.5f);
	// Left, right, near (y >= 1) and far (y <= 10) of a camera at the origin looking along +y.
	const Plane planes[] = { { k, k, 0.0f }, { -k, k, 0.0f }, { 0.0f, 1.0f, -1.0f }, { 0.0f, -1.0f, 10.0f } };
	const float boxes[][4] = { { -1.0f, 3.0f, 1.0f, 5.0f }, { -2.0f, 0.0f, 2.0f, 2.0f }, { 8.0f, 1.5f, 9.0f, 2.0f }, { -12.0f, 9.5f, -10.5f, 11.0f } };
	for (const float* b : boxes) // Each box: minimum x, minimum y, maximum x, maximum y
	{
		bool inside = true;
		bool outside = false;
		for (const Plane& p : planes)
		{
			const float positive = p.X * (p.X >= 0.0f ? b[2] : b[0]) + p.Y * (p.Y >= 0.0f ? b[3] : b[1]) + p.D;
			const float negative = p.X * (p.X >= 0.0f ? b[0] : b[2]) + p.Y * (p.Y >= 0.0f ? b[1] : b[3]) + p.D;
			if (positive < 0.0f)
				outside = true;
			if (negative < 0.0f)
				inside = false;
		}
		std::printf("box at (%.1f, %.1f): %s\n", b[0], b[1], outside ? "outside" : (inside ? "inside" : "intersecting"));
	}
}
```

```text output-of="draw-bounds-culling-planes.cpp"
box at (-1.0, 3.0): inside
box at (-2.0, 0.0): intersecting
box at (8.0, 1.5): outside
box at (-12.0, 9.5): intersecting
```

1. **Line 10:** the four planes of the view, each with a unit normal pointing inward.
2. **Lines 18–19:** the positive and the negative corner, chosen by the sign of each normal component.
3. **Lines 20–23:** a positive corner behind any plane rejects the box; a negative corner behind any plane means it is not wholly inside.

The first box lies in the middle of the view and passes every plane with both corners. The second crosses the near plane, so one corner is in front and the other behind. The third lies beyond the right edge, where the positive corner of one plane is already behind it. The fourth box shows the weakness: it sits past the corner where the left plane meets the far plane, and no point of it is in the frustum. But the positive corner of each plane taken alone is in front, so no single plane rejects it, and the test answers that it crosses.

A test that sometimes keeps what it should reject, and never rejects what it should keep, is a **conservative test**. This one is wrong only in the safe direction: a few extra objects go to the next stage, and nothing visible is lost. The cost is a little extra work for boxes near the frustum's corners. An exact test would need more calculation than it saves.

```cpp src="Strata/src/Strata/Math/Frustum.cpp#L57-L73"
bool Frustum::IsAABBVisible(const AABB& box) const
{
	if (!box.IsValid())
		return false;

	for (const glm::vec4& plane : m_Planes)
	{
		// Test the box corner furthest along the plane normal (the "positive vertex").
		const glm::vec3 positive(
			plane.x >= 0.0f ? box.Max.x : box.Min.x,
			plane.y >= 0.0f ? box.Max.y : box.Min.y,
			plane.z >= 0.0f ? box.Max.z : box.Min.z);
		if (glm::dot(glm::vec3(plane), positive) + plane.w < 0.0f)
			return false;
	}
	return true;
}
```

1. **Lines 59–60:** an empty box is never visible.
2. **Lines 65–68:** the positive corner, picked per axis by the sign of the normal.
3. **Lines 69–70:** one plane that has the positive corner behind it rejects the box.
4. **Line 72:** a box that no plane rejects passes.

## The map

Three groups of code meet here. The :term[render scene]{id=render-scene} owns the proxies and their world bounds, and it feeds the index. The index answers the queries. The :term[renderer's]{id=renderer} extraction and the editor's raycast ask them.

```mermaid caption="The render scene feeds boxes into the spatial index on the main thread. The renderer asks it for the visible proxies and then measures them in parallel chunks, and the editor asks it for the boxes along a ray." alt="A flow chart. The render scene sends proxy boxes to the spatial index. The camera culling and the editor raycast each send a query to the index and receive proxy ids. The camera culling then passes the visible proxies to chunks that run in parallel and merge in order."
flowchart LR
  RS["RenderScene: proxies, world bounds, Sync"] -->|"Insert, Update, Remove, Refresh"| SI["SpatialIndex: cells, blocks, large list"]
  CV["SceneRenderer::CullView"] -->|"QueryFrustum, QuerySphere"| SI
  RC["SceneRaycast"] -->|"QueryPlanes"| SI
  SI -->|"proxy ids"| CV
  CV --> MV["MarkVisibleProxies: chunks of 2048, run by JobSystem"]
  MV --> ORD["merge in chunk order, main thread"]
```

The :term[main thread]{id=main-thread} owns the edits: `RenderScene::Sync` inserts, updates and removes boxes, then calls `Refresh`. Queries are `const` and may run at the same time on several threads. The index stores no proxies, only their ids and boxes.

## The contract

Callers of the index can count on these rules, each with its reason.

- **A query returns exactly the objects whose own box passes the volume's test.** The index is a speed-up, never an approximation. Whatever the camera sees by a test of every box, the index returns, so culling never changes a picture.
- **The result order depends only on the sequence of edits.** Thread timing never changes it, so two runs with the same edits draw the same frame.
- **Edits cost a constant amount, and bounds grow at once but shrink later.** Between an edit and the next `Refresh`, cells may be larger than needed. That costs time and never changes a result.
- **An id must not be in the index when inserted, and a box must be valid and finite.** A box with `NaN` in it would break every comparison, so the index asserts instead of guessing.
- **Edits and `Refresh` need exclusive access.** Queries need none, so they must not overlap an edit.

:::rule[Signal changes to the scene]
A script or system that writes a transform must signal the change, for example with `MarkModified<TransformComponent>`. The render scene learns of a moved entity from that signal and works out its world box again. A write without a signal leaves a stale box in the index, and the object is skipped at the wrong place. The [render scene](../draw/render-scene.md) page shows the whole path.
:::

## A toy version

Start with the plain method. The toy works in 2D, so the numbers stay small: 1,000 boxes, each 1 unit wide, in a world 100 units across, and a view that is a rectangle. The first program tests every box.

```cpp sketch="draw-bounds-culling-brute.cpp"
#include <cstdio>
#include <vector>

struct Box { float X0, Y0, X1, Y1; };

bool Overlaps(const Box& a, const Box& b)
{
	return a.X0 <= b.X1 && a.X1 >= b.X0 && a.Y0 <= b.Y1 && a.Y1 >= b.Y0;
}

int main()
{
	std::vector<Box> boxes;
	for (int i = 0; i < 1000; i++)
	{
		const float x = static_cast<float>(i * 37 % 1000) * 0.1f;
		const float y = static_cast<float>(i * 91 % 1000) * 0.1f;
		boxes.push_back({ x, y, x + 1.0f, y + 1.0f });
	}
	const Box view = { 20.0f, 20.0f, 45.0f, 35.0f };
	int found = 0;
	for (const Box& box : boxes)
		found += Overlaps(box, view) ? 1 : 0;
	std::printf("tested %zu boxes, %d overlap the view\n", boxes.size(), found);
}
```

```text output-of="draw-bounds-culling-brute.cpp"
tested 1000 boxes, 44 overlap the view
```

1. **Lines 6–9:** two boxes overlap when their ranges overlap on both axes.
2. **Lines 22–23:** the scan tests every box, so its cost grows with the scene.

The second program cuts the world into cells 10 units wide and files each box under its corner. The query tests each cell's area first, grown by the box size because a box may reach over a cell edge. Only the boxes of cells that touch the view get a test.

```cpp sketch="draw-bounds-culling-grid.cpp"
#include <cstdio>
#include <map>
#include <utility>
#include <vector>

struct Box { float X0, Y0, X1, Y1; };

bool Overlaps(const Box& a, const Box& b)
{
	return a.X0 <= b.X1 && a.X1 >= b.X0 && a.Y0 <= b.Y1 && a.Y1 >= b.Y0;
}

int main()
{
	std::map<std::pair<int, int>, std::vector<Box>> cells; // Cells of 10 by 10 units, keyed by the box's corner
	for (int i = 0; i < 1000; i++)
	{
		const float x = static_cast<float>(i * 37 % 1000) * 0.1f;
		const float y = static_cast<float>(i * 91 % 1000) * 0.1f;
		cells[{ static_cast<int>(x / 10.0f), static_cast<int>(y / 10.0f) }].push_back({ x, y, x + 1.0f, y + 1.0f });
	}
	const Box view = { 20.0f, 20.0f, 45.0f, 35.0f };
	int found = 0;
	int tested = 0;
	for (const auto& [cell, boxes] : cells)
	{
		const float x = static_cast<float>(cell.first) * 10.0f;
		const float y = static_cast<float>(cell.second) * 10.0f;
		if (!Overlaps({ x, y, x + 11.0f, y + 11.0f }, view)) // The cell's area, grown by a box's size
			continue;
		for (const Box& box : boxes)
		{
			tested++;
			found += Overlaps(box, view) ? 1 : 0;
		}
	}
	std::printf("tested %d boxes, %d overlap the view\n", tested, found);
}
```

```text output-of="draw-bounds-culling-grid.cpp"
tested 120 boxes, 44 overlap the view
```

1. **Lines 15–20:** a map from cell coordinates to the boxes filed under them.
2. **Lines 27–30:** one test decides about a whole cell, and a cell that misses the view is skipped.
3. **Lines 31–35:** the boxes of the cells that touch the view get their own test.

The same 44 boxes overlap the view, but the grid tested 120 boxes, not 1,000. Two things are missing from the toy. A cell wholly inside the view could be taken without testing its boxes. And a box much larger than a cell breaks the guess that a cell's area plus one box size covers its boxes. Strata's grid handles both.

## The real code

The real index keeps every difference from the toy for a reason. It works in three dimensions, takes any :term[convex]{id=convex} volume, keeps cells in hash tables, and groups cells into blocks.

### The grid and its edits

`SpatialIndexSpecification` holds two numbers: a cell edge of 32 world units, and a limit of four cells for the length of an object. An object lives in the cell that contains the centre of its box. A cell keeps the union of its objects' boxes, so cell bounds follow the objects, not the grid lines. Eight by eight by eight cells form a block, which keeps the union of its cells' boxes.

An object longer than four cells along any axis, such as a terrain, goes to a separate list. Without that list, one terrain would stretch its cell's bounds over the world, and every query would test the objects of that cell. Strata packs cell coordinates into 21 bits per axis, so a key is one 64-bit number. A cell exists only while it holds an object, so empty space costs nothing.

An edit must not cost more than the move itself. `Update` handles the common case, an object that stays in its cell, by replacing its box and growing the cell's bounds to cover it.

```cpp src="Strata/src/Strata/Renderer/SpatialIndex.cpp#L303-L345"
void SpatialIndex::Update(uint32_t id, const AABB& bounds)
{
	ST_CORE_ASSERT(Contains(id), "SpatialIndex: object {} is not in the index", id);
	ST_CORE_ASSERT(bounds.IsValid() && std::isfinite(bounds.Min.x + bounds.Min.y + bounds.Min.z + bounds.Max.x + bounds.Max.y + bounds.Max.z),
		"SpatialIndex: object {} has an invalid box", id);
	Object& object = m_Objects[id];
	const bool large = IsLarge(bounds);
	if (object.Cell == c_LargeCell && large)
	{
		object.Bounds = bounds;
		return;
	}
	if (object.Cell != c_LargeCell && !large)
	{
		Cell& cell = m_Cells[object.Cell];
		if (cell.Coordinates == GetCellCoordinates(bounds))
		{
			// Stays in its cell: the cell's bounds grow at once and are tightened by Refresh if the object shrank or
			// moved away from part of them.
			if (!ContainsBox(bounds, object.Bounds) && !cell.BoundsStale)
			{
				cell.BoundsStale = true;
				m_StaleCells.push_back(object.Cell);
			}
			object.Bounds = bounds;
			GrowCell(object.Cell, bounds);
			return;
		}
	}

	RemoveFromCell(id);
	object.Bounds = bounds;
	if (large)
	{
		object.Cell = c_LargeCell;
		object.Position = static_cast<uint32_t>(m_LargeObjects.size());
		m_LargeObjects.push_back(id);
	}
	else
	{
		AddToCell(id, AcquireCell(GetCellCoordinates(bounds)));
	}
}
```

1. **Lines 310–314:** a large object that stays large only gets a new box.
2. **Lines 318–330:** an object that stays in its cell grows the cell's bounds at once.
3. **Lines 322–326:** a box that no longer covers the old one flags the cell stale, once.
4. **Lines 333–344:** an object that changes cell is removed and added again, one hash lookup each.

Growth is immediate, so a query between two `Refresh` calls never misses an object. Shrinking is lazy: a cell whose object moved or shrank is only flagged stale. `Refresh`, which the render scene calls at the end of its `Sync`, works out the stale cells again and then their blocks. A moving crowd therefore pays at most one flag per cell per frame, and one new union per flagged cell. A hierarchy would instead fit every box above each moved object again.

:::why[A grid, not a hierarchy]
A hierarchy of boxes queries in time that follows the visible part, but it repairs itself after each move. Strata's proxies move every frame, and a cell move costs one hash lookup, which is less than a repair. The two-level layout gives the grid a hierarchy's skipping: one test rejects a block of 512 cells. The price is one cell size and the list of large objects. A scene full of objects far bigger than four cells would fall back to a test of each, which is why a terrain goes to its own list and not into the grid.
:::

### Classifying a box

The query needs a three-way answer for blocks and cells. So the index pairs the positive corner with its mirror, the negative corner: the one furthest against the normal. If the positive corner is behind any plane, the box is outside; if the negative corner is in front of every plane, the box is inside. Otherwise the box crosses the volume's edge. `ClassifyPlanes` does both in one pass over the planes.

```cpp src="Strata/src/Strata/Renderer/SpatialIndex.cpp#L73-L93"
VolumeOverlap SpatialIndex::ClassifyPlanes(const AABB& bounds, std::span<const glm::vec4> planes)
{
	if (!bounds.IsValid())
		return VolumeOverlap::Outside;
	// Inside when the corner nearest to each plane's back side is in front of it. A box inside the volume holds only
	// boxes that pass IntersectsPlanes: their furthest corners lie at least as far along every normal.
	bool inside = true;
	for (const glm::vec4& plane : planes)
	{
		const glm::vec3 normal(plane);
		const glm::vec3 positive(normal.x >= 0.0f ? bounds.Max.x : bounds.Min.x, normal.y >= 0.0f ? bounds.Max.y : bounds.Min.y,
			normal.z >= 0.0f ? bounds.Max.z : bounds.Min.z);
		if (glm::dot(normal, positive) + plane.w < 0.0f)
			return VolumeOverlap::Outside;
		const glm::vec3 negative(normal.x >= 0.0f ? bounds.Min.x : bounds.Max.x, normal.y >= 0.0f ? bounds.Min.y : bounds.Max.y,
			normal.z >= 0.0f ? bounds.Min.z : bounds.Max.z);
		if (glm::dot(normal, negative) + plane.w < 0.0f)
			inside = false;
	}
	return inside ? VolumeOverlap::Inside : VolumeOverlap::Intersecting;
}
```

1. **Lines 75–76:** an empty box is outside.
2. **Lines 83–86:** the positive corner behind a plane ends the pass with outside.
3. **Lines 87–90:** a negative corner behind a plane takes away the right to say inside.
4. **Line 92:** a box no plane rejects is inside or `Intersecting`.

`IntersectsPlanes`, a few lines above, is the same pass without the second corner, and `Frustum::IsAABBVisible` runs the same arithmetic. A sphere has its own pair: the nearest point of the box decides outside, and its furthest corner decides inside.

### The query

The query works from the top down, and the answer for a group of objects decides how much more work the group needs.

```cpp src="Strata/src/Strata/Renderer/SpatialIndex.cpp#L406-L438"
template<typename Classify, typename Test>
void SpatialIndex::Query(const Classify& classify, const Test& test, std::vector<uint32_t>& outIds) const
{
	for (const uint32_t blockIndex : m_ActiveBlocks)
	{
		const Block& block = m_Blocks[blockIndex];
		const VolumeOverlap blockOverlap = classify(block.Bounds);
		if (blockOverlap == VolumeOverlap::Outside)
			continue;
		for (const uint32_t cellIndex : block.Cells)
		{
			const Cell& cell = m_Cells[cellIndex];
			const VolumeOverlap cellOverlap = blockOverlap == VolumeOverlap::Inside ? VolumeOverlap::Inside : classify(cell.Bounds);
			if (cellOverlap == VolumeOverlap::Outside)
				continue;
			if (cellOverlap == VolumeOverlap::Inside)
			{
				outIds.insert(outIds.end(), cell.Ids.begin(), cell.Ids.end());
				continue;
			}
			for (const uint32_t id : cell.Ids)
			{
				if (test(m_Objects[id].Bounds))
					outIds.push_back(id);
			}
		}
	}
	for (const uint32_t id : m_LargeObjects)
	{
		if (test(m_Objects[id].Bounds))
			outIds.push_back(id);
	}
}
```

1. **Lines 409–414:** each block is classified, and an outside block costs one test.
2. **Lines 418–420:** the cells of an inside block are inside without a test of their own.
3. **Lines 421–425:** an inside cell appends all its ids at once, with no box test.
4. **Lines 426–430:** a crossing cell tests each of its boxes with the volume's own test.
5. **Lines 433–437:** the large objects are always tested one by one.

A worked case shows the outcomes. A block outside the frustum rejects up to 512 cells with one test. A cell wholly inside, with 40 boxes, appends its 40 ids with no box test. A crossing cell with 40 boxes costs 40 calls of `IsAABBVisible`.

Why is the answer exact? A union box that is outside has some plane with the whole union behind it, so every box inside the union is behind that plane too. A union box that is inside has its negative corner in front of every plane, so any box inside it has its positive corner in front of every plane too and passes. A crossing group falls back to the test of each object. So every decision a group makes agrees with what each object's own test would say, and the result equals the result of a scan of every box.

The index offers three queries over this one routine: `QueryFrustum` for a camera, `QueryPlanes` for any convex volume and `QuerySphere` for the objects within a radius. They differ only in the two functions they pass: one classifies a group, and one tests a single box.

### From the query to the draw list

`SceneRenderer::CullView` calls `QueryFrustum`, marks what the camera needs, and then queries a sphere around the camera for the prefetch. The sphere's radius is `PrefetchDistance` in the renderer's specification, 100 world units by default. Meshes outside the view but near the camera get a low-priority mark, so turning the camera finds them loaded. A mesh with unknown bounds cannot be rejected, so the renderer requests it as if it were in view until its bounds arrive.

`MarkVisibleProxies` is the part that scales with the visible count. It computes each proxy's screen fraction and records which meshes and materials the frame uses. It runs in chunks of 2,048 proxies on the job system, and each chunk writes only its own record.

```cpp src="Strata/src/Strata/Renderer/SceneRendererExtraction.cpp#L289-L327"
ForEachChunk(chunks, [&](uint32_t chunk)
{
	ExtractionChunk& output = m_Chunks[chunk];
	output.MeshMarks.clear();
	output.MaterialMarks.clear();
	output.Animators.clear();
	output.Receivers = AABB();
	const uint32_t end = std::min(visible, (chunk + 1) * c_ExtractionChunkSize);
	for (uint32_t item = chunk * c_ExtractionChunkSize; item < end; item++)
	{
		const uint32_t proxy = m_VisibleProxies[item];
		m_ProxyStamps[proxy] = m_FrameStamp;
		const AABB& bounds = renderScene.GetWorldBounds(proxy);
		// Animators that only animate while seen learn that their meshes are (ReportVisibleAnimators), and that their
		// shadows fall on what is seen (FindShadowCasters).
		if (skins)
		{
			if (renderScene.GetSkinAnimator(proxy) != entt::null)
				output.Animators.push_back(renderScene.GetSkinAnimator(proxy));
			output.Receivers.Expand(bounds);
		}
		const float fraction = GetScreenFraction(camera, bounds.GetCenter(), glm::length(bounds.GetExtents()));
		m_VisibleFractions[item] = fraction;
		const uint32_t usage = fraction > highFraction ? (c_UseView | c_UseHigh) : c_UseView;
		const uint32_t overrideSlot = renderScene.GetOverrideMaterialSlot(proxy);
		AppendMark(output.MeshMarks, renderScene.GetMeshSlot(proxy), usage | (overrideSlot == RenderScene::c_InvalidIndex ? usage << c_SubmeshMaterialsShift : 0u));
		if (overrideSlot != RenderScene::c_InvalidIndex)
			AppendMark(output.MaterialMarks, overrideSlot, usage);
	}
});
for (uint32_t chunk = 0; chunk < chunks; chunk++)
{
	for (const auto& [slot, usage] : m_Chunks[chunk].MeshMarks)
		MarkMesh(slot, usage);
	for (const auto& [slot, usage] : m_Chunks[chunk].MaterialMarks)
		MarkMaterial(slot, usage);
	m_VisibleAnimators.insert(m_VisibleAnimators.end(), m_Chunks[chunk].Animators.begin(), m_Chunks[chunk].Animators.end());
	m_VisibleReceivers.Expand(m_Chunks[chunk].Receivers);
}
```

1. **Lines 289–296:** each chunk clears its own record and covers up to 2,048 visible proxies.
2. **Line 310:** the screen fraction of the proxy's :term[bounding sphere]{id=bounding-sphere}, from its world box.
3. **Line 312:** a fraction above the high-priority limit adds the high-priority bit to the mark.
4. **Lines 319–327:** the main thread merges the records chunk by chunk, in order.

The merge runs in chunk order, so the marks land in the same order whatever the number of threads. The draw gathering that follows uses the same pattern, which is why the frame does not depend on the machine. The [jobs](../core/jobs.md) page explains it.

The editor's raycast is the index's second reader. `SceneRaycast` builds a long thin volume of six planes around the ray: four sides 0.001 units away, a start plane at the origin and an end plane at the ray's length. `QueryPlanes` returns the boxes that touch it, and the exact tests against triangles run on those candidates, nearest first. This is a broad phase, as the [collision detection](../physics/collision-detection.md) page names it: a cheap filter before the exact test. The rest of the raycast belongs to the [placement](../editor/placement.md) page.

## How big does it look?

Culling asks whether an object is in view. Many stages also ask how large it looks, because a mesh a few pixels across needs neither its finest triangles nor its sharpest textures, and may not need drawing. The measure must be cheap, steady as the object turns and the same on the :term[central processing unit]{id=processor} (CPU) and the :term[graphics processing unit]{id=gpu} (GPU).

Think of a camera 50 units from an object. At that distance the view is as tall as $2 \times 50 \times \tan(30°)$ for a 60 degree :term[field of view]{id=field-of-view}, about 57.7 units. An object 6 units across fills a tenth of that height. The measure is that ratio: the object's size over the height of the view at its distance.

The **screen fraction** is the projected diameter of an object's :term[bounding sphere]{id=bounding-sphere} divided by the height of the viewport, so 1 means the object fills the height. Strata takes the sphere that holds the object's box, with the box's half diagonal as radius. A sphere looks the same from every angle, so the number does not flicker as the object turns, and the half diagonal costs one length.

For a perspective camera at distance $d$ with vertical field of view $f$, the view at that distance is $2 d \tan(f/2)$ tall, so:

$$\text{fraction} = \frac{2r}{2 d \tan(f/2)} = \frac{r}{d \tan(f/2)}$$

Here $r$ is the sphere's radius in world units, $d$ is the distance from the camera to the sphere's centre in world units and $f$ is the field of view in :term[radians]{id=radian}. Strata never lets $d$ fall below the near distance, so an object at the camera does not give an infinite answer. For an orthographic camera, the height of the view does not depend on distance, so the fraction is $2r$ over that height. Strata's camera stores that height in the field that holds the field of view, so one function serves both.

```cpp src="Strata/src/Strata/Renderer/LODSelection.cpp#L10-L17"
float GetScreenFraction(const SceneCamera& camera, const glm::vec3& center, float radius)
{
	if (camera.Orthographic)
		return (2.0f * radius) / std::max(camera.VerticalFOV, 1e-4f);
	const float halfFOVTangent = std::tan(std::max(camera.VerticalFOV, 1e-3f) * 0.5f);
	const float distance = glm::length(center - camera.Position);
	return radius / (std::max(distance, camera.Near) * halfFOVTangent);
}
```

Check the limits. An object of zero radius gives 0, and an object at the near distance with a radius equal to the half height gives 1. A perspective object twice as far away gives half the fraction. With the box above (half sizes 2, 1 and 2, radius 3) at 50 units, $\tan 30° = 0.577$ gives $3 / (50 \times 0.577) = 0.104$. An orthographic camera that shows 20 units of height gives $6 / 20 = 0.3$ at any distance.

Several stages read the number. Level of detail takes it as its input, and the [level of detail](../draw/lod.md) page shows how. A proxy above `HighPriorityScreenFraction`, 0.05 by default, requests its assets at a higher priority. The texture streamer works out the same measure to choose how sharp a texture must be.

**Size culling** is not drawing an object whose size on screen is below a limit in pixels. The renderer multiplies the fraction by the viewport height: for a 1,080 pixel viewport, 0.104 is a diameter of 112 pixels. An object below the quality row **Smallest drawn size (pixels)** is skipped, a value of 0 draws everything, and a higher value draws fewer objects. The GPU path applies the same rule, as the [GPU-driven](../draw/gpu-driven.md) page shows.

:::example[A camera over a field of boxes]
A camera looks over 1-unit boxes in cells of 32 units, so box P at (40, 0, 70) falls in the cell (1, 0, 2), where 40 and 70 over 32 round down. The frustum holds that whole cell, so `Query` appends its ids and runs no box test. Box Q at (100, 0, 130) lies in a cell that the frustum's side plane crosses, so `Query` calls `IsAABBVisible` for each box of that cell, and Q passes or fails on its own box. Now take a box 8,000 units from the camera under a 60 degree view: its radius of 0.87 gives a fraction of 0.0002, which is 0.2 pixels at 1,080 pixels high. With the smallest drawn size set to 0.5, size culling skips it although the frustum holds it.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Hierarchy of boxes | Physics engines, ray tracing, many renderers of still scenes | Tighter skipping for uneven scenes | A repair or rebuild after every moving object |
| Octree | Scene managers of several engines | A cell size that adapts to dense and sparse regions | Moves walk the tree, and objects on cube edges sit in large cubes |
| Loose octree | Engines with many moving objects | Constant-time moves with adaptive depth | A margin that makes every query test more cubes |
| Uniform grid with hashing | Particle systems, broad phases of physics | The simplest code | One cell size for every object, and no skip for far blocks |
| Testing every box | Small scenes and tools | No structure to keep in step | Cost that grows with the scene |

The loose grid wins because edits are the common operation. The sources for these structures are in Further reading.

## How it is tested

The suite `Renderer.SpatialIndex` in `StrataTests/src/Renderer/SpatialIndexTests.cpp` has three test cases. One inserts 100,000 random boxes of mixed sizes and compares frustum, plane and sphere queries with a scan of every box, then repeats it after random moves, removals and inserts. One checks that results follow the order of edits and that empty cells and blocks are released. The third checks that cells inside the volume are taken whole, that large objects are tested one by one, and that boxes classify as inside, crossing and outside. The test case `Frustum culling with reversed-Z projections` in `StrataTests/src/Math/MathTests.cpp` covers the frustum itself.

Run the suite from the build folder of your platform:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.SpatialIndex
```

The exercises below write the same kind of comparison yourself.

## Changing it safely

- **Add a query shape** by passing a classify function and a test function to `Query`. They must agree: a box that `classify` calls inside must pass `test`, which is the reason the answer stays exact.
- **Change the cell size or the large-object limit** only with a timing run. Both are fields of the specification, and neither changes a result.
- **Keep every edit constant-time.** A loop over a cell's objects in `Update` would turn a moving crowd into a slow scene.
- **Keep queries `const`.** The extraction reads the index from worker threads.
- **Compare with a scan of every box** in a test for every change to a test or a classification. The 100,000-box case is the safety net.

## Summary

- A box's world bounds under a rotation come from Arvo's method: add up the absolute reach of each half size along each axis. Turning only the two stored corners gives a box that is too small.
- Six planes come from the rows of the view-projection matrix; the positive vertex test rejects a box whose furthest corner is behind a plane, and the test is conservative at the frustum's corners.
- Strata's loose grid takes whole blocks and cells that lie inside the volume, tests the boxes of crossing cells one by one, and so answers exactly like a scan of every box.
- The screen fraction is the bounding sphere's diameter over the viewport height: $r / (d \tan(f/2))$ for perspective and $2r$ over the view height for orthographic.
- A query takes a box with its cell when the cell lies inside the frustum, and tests the box alone when its cell crosses the frustum's edge.

## Check yourself

1. A box of half sizes 3 and 1, centred at the origin, turns by 45 degrees. What are its half sizes with Arvo's method, and what does the corner shortcut give?

   :::answer{tests="transform-bounds"}
   Arvo's method gives $0.707 \times 3 + 0.707 \times 1 = 2.83$ along each axis. The shortcut turns the corners (-3, -1) and (3, 1) to (-1.41, -2.83) and (1.41, 2.83), so it gives 1.41 along x. That is too small by half, because the other two corners reach x = 2.83.
   :::

2. Which statement about the positive vertex test is correct? (a) It returns inside when the positive vertex is in front of every plane. (b) It rejects a box when the furthest corner along a plane's normal is behind that plane. (c) It never keeps an object that lies outside.

   :::answer{tests="frustum-test"}
   Only (b) is correct. Option (a) is wrong: the furthest corner in front of every plane shows only that the box is not rejected, since the nearest corner may still be behind a plane. Option (c) is wrong: near a frustum corner the test keeps an object that lies outside, and that is why it is called conservative.
   :::

3. A cell of 40 boxes is classified inside. How many box tests does `Query` run for it, and why is the answer still correct?

   :::answer{tests="grid-exact"}
   Zero. The cell's bounds hold all 40 boxes, and the cell's negative corner is in front of every plane. So each box's own positive corner is in front too, and each box would pass the test. A crossing cell would run 40 tests.
   :::

4. A camera with a 90 degree vertical field of view sees an object of radius 2 at distance 10. What is its screen fraction, and how many pixels tall is it on a 1,000 pixel viewport?

   :::answer{tests="screen-fraction"}
   The tangent of 45 degrees is 1, so the fraction is $2 / (10 \times 1) = 0.2$. On 1,000 pixels that is 200 pixels. An orthographic camera that shows 20 units gives $4 / 20 = 0.2$ for the same object at any distance.
   :::

5. A large object is longer than four cells. Where does the index keep it, and how does a query test it?

   :::answer{tests="grid-exact"}
   In a list of its own, apart from the cells. Every query tests it alone with the same box test, so it never makes a cell's bounds large, and the result stays exact.
   :::

6. A box lies in a cell that the frustum's side plane crosses. Which function decides whether the query returns the box, and does a box in an inside cell call it?

:::answer{tests="trace-query"}
`Frustum::IsAABBVisible` decides, once for each box of the crossing cell. A box in an inside cell never calls it: `Query` appends the cell's ids whole.
:::

## Exercises

1. **Basic.** A box has centre (0, 0, 0) and half sizes (3, 2, 1). A 90 degree turn about the vertical axis maps $x$ to $z$ and $z$ to $-x$. What are the new half sizes by Arvo's method?

   :::answer[Worked solution]{tests="transform-bounds"}
   The turn leaves $y$ alone, so the new $y$ half size is 2. The new $x$ axis comes from the old $z$ axis, so the new $x$ half size is the old $z$ half size, 1. The new $z$ half size is the old $x$ half size, 3. The new half sizes are (1, 2, 3).
   :::

2. **Medium.** Extend the grid toy to 100,000 boxes, collect the ids that overlap the view both ways, and compare them. Print how many boxes the grid tested.

   :::answer[Worked solution]{tests="grid-exact"}
   The sketch files each box by its corner, collects the ids that a scan of every box finds, and collects the ids the grid finds after the cell test. It sorts the grid's ids, because cells come in another order than boxes, and compares the two lists.

   ```cpp sketch="draw-bounds-culling-compare.cpp"
   #include <algorithm>
   #include <cstdio>
   #include <map>
   #include <utility>
   #include <vector>

   struct Box { float X0, Y0, X1, Y1; };

   bool Overlaps(const Box& a, const Box& b)
   {
   	return a.X0 <= b.X1 && a.X1 >= b.X0 && a.Y0 <= b.Y1 && a.Y1 >= b.Y0;
   }

   int main()
   {
   	std::vector<Box> boxes;
   	std::map<std::pair<int, int>, std::vector<int>> cells; // Ids of the boxes in each 10 by 10 cell
   	for (int i = 0; i < 100000; i++)
   	{
   		const float x = static_cast<float>(i * 7919 % 100000) * 0.01f;
   		const float y = static_cast<float>(i * 6007 % 100000) * 0.01f;
   		boxes.push_back({ x, y, x + 1.0f, y + 1.0f });
   		cells[{ static_cast<int>(x / 10.0f), static_cast<int>(y / 10.0f) }].push_back(i);
   	}
   	const Box view = { 200.0f, 200.0f, 450.0f, 350.0f };
   	std::vector<int> brute;
   	std::vector<int> grid;
   	int tested = 0;
   	for (int i = 0; i < 100000; i++)
   	{
   		if (Overlaps(boxes[i], view))
   			brute.push_back(i);
   	}
   	for (const auto& [cell, ids] : cells)
   	{
   		const float x = static_cast<float>(cell.first) * 10.0f;
   		const float y = static_cast<float>(cell.second) * 10.0f;
   		if (!Overlaps({ x, y, x + 11.0f, y + 11.0f }, view))
   			continue;
   		for (const int id : ids)
   		{
   			tested++;
   			if (Overlaps(boxes[id], view))
   				grid.push_back(id);
   		}
   	}
   	std::sort(grid.begin(), grid.end());
   	std::printf("same ids: %s, brute tested 100000, grid tested %d\n", grid == brute ? "yes" : "no", tested);
   }
   ```

   ```text output-of="draw-bounds-culling-compare.cpp"
   same ids: yes, brute tested 100000, grid tested 4580
   ```

   1. **Lines 29–33:** the scan tests all 100,000 boxes.
   2. **Lines 38–44:** the grid tests only the boxes of cells that touch the view.
   3. **Line 47:** sorting makes the two lists comparable.

   The grid tests a small share of the boxes. On your own machine, time both loops: the scan grows with the scene, and the grid grows with the size of the view. Strata's test makes the same comparison on its own index.
   :::

3. **Hard.** Write the shape of a Strata test that compares `QuerySphere` with a scan of every box after a box moves from one cell to another.

   :::answer[Worked solution]{tests="grid-exact,trace-query"}
   Insert a set of boxes, call `Update` on one so that its centre crosses a cell edge, call `Refresh`, then query the sphere and compare the sorted ids with the scan. The steps in :term[pseudocode]{id=pseudocode}:

   ```pseudocode
   index = SpatialIndex()
   for id, box in boxes: index.Insert(id, box)
   boxes[7] = moved(boxes[7], by one cell)
   index.Update(7, boxes[7])
   index.Refresh()
   found = index.QuerySphere(center, radius), sorted
   expected = ids whose box passes IntersectsSphere, sorted
   check found equals expected
   ```

   Moving between cells exercises the remove and add path, and the sort removes the difference in order.
   :::

4. **Hard.** Trace it yourself: with a breakpoint in `SpatialIndex::Query`, follow two boxes of the page's field from `CullView` through `QueryFrustum` to the visible list. One lies in a cell wholly inside the frustum, and one in a crossing cell.

:::answer[Worked solution]{tests="trace-query"}
`SceneRenderer::CullView` in `SceneRendererExtraction.cpp` calls `SpatialIndex::QueryFrustum`, which calls the `Query` template with `ClassifyPlanes` and `Frustum::IsAABBVisible`. The box in the inside cell is appended by the `outIds.insert` line when the cell classifies as Inside, and no box test runs. The box in the crossing cell reaches the loop over `cell.Ids`, where `Frustum::IsAABBVisible` returns true and `push_back` adds it. Both end in `m_VisibleProxies`.
:::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SpatialIndex.h` and `SpatialIndex.cpp`: the grid, its edits, `Refresh` and the queries.
- `Strata/src/Strata/Math/Frustum.cpp` and `AABB.cpp`: the planes, the box test and `AABB::Transformed`.
- `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`: `CullView` and `MarkVisibleProxies`.
- `Strata/src/Strata/Renderer/LODSelection.cpp`: `GetScreenFraction`.
- `StrataEditor/src/Editor/SceneRaycast.cpp`: the thin volume of six planes.
- `StrataTests/src/Renderer/SpatialIndexTests.cpp`: the suite `Renderer.SpatialIndex`.
- The quality row **Smallest drawn size (pixels)** of the renderer's quality section.

## Further reading

- Christer Ericson, "Real-Time Collision Detection": grids, hierarchies and box tests (advanced).
- Thatcher Ulrich, "Loose Octrees" in Game Programming Gems: the loose structure (intermediate).
- Gil Gribb and Klaus Hartmann, "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix": the plane method (intermediate).
- James Arvo, "Transforming Axis-Aligned Bounding Boxes" in Graphics Gems: the transformed box (intermediate).
