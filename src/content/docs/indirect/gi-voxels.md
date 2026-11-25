---
id: indirect/gi-voxels
title: "Global illumination I: a voxel copy of the world"
description: "How Strata turns the static triangles around the camera into a clipmap of voxels: the triangle-box test, solid fill, two-sided voxels, scrolling and anchors."
kind: internals
size: L
tracks: [E]
needs: [indirect/seam, gpu/compute, gpu/geometry-pool, draw/render-scene, indirect/problem]
time: 95
learn:
  - id: explain-voxelize
    text: explain how a triangle becomes voxels with the triangle-box test and buffer atomics
  - id: explain-fill
    text: explain how winding steps fill a closed mesh and when a voxel becomes two-sided
  - id: compute-window
    text: compute a level's window, a voxel's texel and the slabs of a scroll
  - id: compute-memory
    text: compute the memory of a global illumination layout
  - id: trace-batch
    text: trace a batch of regions from the frame the processor builds to the finished voxels
since: 0.8.0
status: final
---

Strata's :term[global illumination]{id=global-illumination} (GI) lights a surface with the bounce light that probes collect by tracing rays through the world around the camera. A ray needs something cheap to hit, and the triangles of a scene are not that. This page covers the first half of the system: a copy of the static world made of **voxels**, the small cubes of a grid around the camera. The grid records where surfaces are, what color they have, which way they face and what they emit. Two later pages cover the rest: [Radiance cascades and the irradiance field](../indirect/gi-cascades.md) for the light and the probes, and [Moving objects, limits and what comes next](../indirect/gi-limits.md) for movers, local lights and limits.

::compare{id=cornell-gi-off-on}

## The problem and how engines solve it

The page [The indirect-light problem](../indirect/problem.md) explains why indirect light is hard and which families of answers exist. Strata chose world-space radiance cascades, which trace the world and never the screen. A ray in the world must learn what it hits and how bright that is.

A scene holds millions of triangles, and a ray cannot test them all. A regular grid answers differently: the cell of a point has an address, and one read returns what lies there. A march costs a few reads per step, whatever the triangle count. The price is detail, because a cell holds one answer for everything inside it. The rest of this page builds that grid and says what it costs.

## The map: what asks, what runs

GI is experimental and costs nothing until a scene asks for it. Three settings and one stage decide what runs.

| Where | Name | Value |
| --- | --- | --- |
| Post Process | `GlobalIllumination` | Off by default |
| Post Process | `GlobalIlluminationIntensity` | 1 by default, from 0 to 4; inactive with the reason "Global Illumination is off" |
| Graphics Quality | row `GlobalIllumination` | Off for the two lower presets, High for the two upper ones; the layouts are Low and High |
| Stage of the :term[graphics processing unit]{id=gpu} (GPU) | `GPU.RadianceCascades` | After `GPU.AO`, before `GPU.Reflections` |

GI runs when the scene asks and the row is not Off. A frame that does not run it makes no memory and no stage, and the forward :term[shaders]{id=shader} hold nothing of the field, so the image is what it was before GI existed, bit for bit. The page [Where indirect light meets the surface](../indirect/seam.md) shows how the forward pass joins the field.

```mermaid caption="The whole global illumination frame. This page covers the first three boxes. The field of the frame before feeds the injection, which is how light bounces on between frames." alt="A chain of boxes runs from the geometry pool to the forward gather. They are the clipmap, voxelization, light injection, a merge into coarser levels, probe validity and weights, the cascade marches, the field reduce and the forward gather. A dashed arrow leads from the field reduce back to the injection."
flowchart LR
    Pool["Geometry pool: static submeshes"] --> Clip["CPU clipmap: regions and work items"]
    Clip --> Vox["GPU voxelization: Triangles, Tiles, Fill, Finalize"]
    Vox --> Inj["Light injection"]
    Inj --> Down["Level downsample"]
    Down --> Val["Probe validity and weights"]
    Val --> Cas["Cascade marches, top cascade first"]
    Cas --> Red["Field reduce"]
    Red --> Gather["Forward gather"]
    Red -.->|"previous field"| Inj
```

Two threads of control meet here. On the :term[main thread]{id=main-thread}, the :term[central processing unit]{id=processor} (CPU) runs `VoxelClipmap::BuildFrame`, which reads the :term[render scene's]{id=render-scene} :term[change log]{id=change-log} and decides which boxes of voxels to rebuild. Inside `GPU.RadianceCascades`, four compute passes turn the triangles of those boxes into voxels. The CPU decides only a list of boxes and work items, and the GPU never walks the scene.

The `voxels` debug view shows what this page builds: the surfaces of the finest level's voxels, smoothed between voxels and shaded by the light they store. The grid shows only where the light changes.

::figure{id=voxels-view}

## The contract

The voxel copy follows rules that later pages rely on. Each has a reason.

- **The voxels hold world data only.** Nothing in them comes from the screen or from an earlier frame, so the light at a point depends on the world and on where the camera stands, and never smears behind a turning camera.
- **Voxel coordinates are relative to an anchor.** A scene gives the same voxel bits wherever the camera stands. Worlds stay within 20 km of the origin, where a float still resolves 2 mm ([Why levels must stream](../worlds/why-streaming.md)).
- **Walls are thicker than two voxels of the finest level:** 20 cm at High and 40 cm at Low. A thinner wall puts both faces into one coarser voxel, which turns two-sided and dark.
- **Only static, opaque or cut-out triangles enter.** Skinned meshes never enter, and an object that moves leaves while it moves ([Moving objects, limits and what comes next](../indirect/gi-limits.md)).
- **The clipmap runs on the main thread and works on changes.** It never walks every proxy in a frame; it reads the change log and the regions it takes.

:::rule[Global illumination traces world data, never the screen]
`AGENTS.md` bars screen-space input to GI. Screen-space light needs frames blended over time and misses what is off screen. Strata pays for a voxel copy so that the light stays the same whatever the earlier frames showed ([The indirect-light problem](../indirect/problem.md)).
:::

## Voxelization: which cells a triangle touches

**Voxelization** turns triangles into voxels: for each triangle, find the cells it touches and write what the surface there looks like. Each voxel of a level takes 20 :term[bytes]{id=byte}: the material (an 8-bit color and an occupancy), the emission, the normal and the stored light.

Finding the cells starts with the triangle's :term[bounding box]{id=bounding-box}, but the box lies. The test that settles a cell is the **triangle-box overlap** test of Akenine-Moller. It asks whether a triangle and an axis-aligned box share a point. The example shows a cell whose bounds overlap the triangle's bounds while the triangle still misses the cell.

:::example[One axis decides]
Put the cell's center at the origin and give it half sizes of 0.5. A triangle has the corners (1.1, 0, 0), (0, 1.1, 0) and (1.1, 1.1, 0), relative to that center. Its bounds, 0 to 1.1 on x and y, overlap the cell's bounds of −0.5 to 0.5, so no axis of the box separates the shapes.

Take the edge from the first corner to the second: it runs along (−1.1, 1.1, 0). Its :term[cross product]{id=cross-product} with the z axis is (−1.1, −1.1, 0). Project the corners on that axis with the :term[dot product]{id=dot-product}: −1.21, −1.21 and −2.42.

The box projects to a radius of 0.5 × 1.1 + 0.5 × 1.1 = 1.1. All three corners lie below −1.1, so that axis puts the shadows apart, and the triangle misses the cell. In space, the edge's plane x + y = 1.1 passes 0.1 beyond the cell's far corner, where x + y = 1.
:::

The test generalizes: two convex shapes are apart when one axis separates their shadows ([Geometry for engines](../basics/math-geometry.md)). For a triangle and a box, 13 axes suffice: the three face axes of the box, the normal of the triangle, and the nine cross products of a box axis with a triangle edge. A cell overlaps when none of the 13 separates. Touching counts as overlap: a face on a cell boundary marks the cells on both sides, so the face has a lit layer in front of it.

The GPU runs one thread per triangle, and many triangles reach the same voxel at the same moment. The passes write into a scratch buffer, a temporary grid of words that holds a batch of voxels until the last pass turns them into textures. The two triangle passes write there with buffer atomics only ([Compute shaders](../gpu/compute.md)):

- **The key** is the voxel's class and color. The class sits in the top two bits: opaque is 3, interior 2, alpha-masked 1. `InterlockedMax` keeps the largest key, so an opaque surface hides a cut-out one in the same voxel.
- **The normal** is the triangle's unit normal times 256, added as an :term[integer]{id=integer} with `InterlockedAdd`, but only to a voxel that does not lie wholly behind the triangle. Three upward triangles in a floor voxel sum to (0, 768, 0).
- **The emission** takes `InterlockedMax`, and its coverage takes `InterlockedAdd`.

:::why
Maximum and integer addition give the same result in any order, but float addition does not. With integers, two runs of one scene give the same voxels, however the GPU schedules its threads. The cost is a fixed point: normals have a resolution of 1/256.
:::

The emission is stored as **RGB9E5**: a 32-bit color of three 9-bit :term[mantissas]{id=significand} that share one 5-bit :term[exponent]{id=exponent}, so that 4 bytes hold light in :term[nits]{id=lux} up to 65,408.

## Solid fill: counting windings

A box that is only a shell of voxels has an empty inside, and a ray that starts inside would see nothing. Strata marks the inside of some meshes solid. The meshes must be closed, because a fill on a mesh with a hole would flood the whole column above it.

A **closed mesh** has no holes: every edge belongs to exactly two faces, which run in opposite directions along it. `MeshUtils::IsClosed` welds positions that are equal bit for bit, lists each triangle's three directed edges, sorts them and checks that each appears once and that its opposite appears too. A cube has 12 triangles and 36 directed edges. Remove one face, two triangles, and the four edges around the hole lose their opposites, so the test fails.

**Solid fill** marks every voxel inside a closed mesh as solid, not only those the surface touches. It counts winding steps along vertical columns. A line going up through a closed mesh enters it at a triangle that faces down and leaves it at one that faces up. Each entry adds +1 and each exit −1, at the first voxel whose center lies above the crossing, and a voxel is inside where the running sum upward is not 0.

:::example[One column through a box]
The toy box below spans 2.4 to 6.6 on every axis, in voxel units. A column at x = 4.5, z = 4.5 meets the box's bottom face at y = 2.4. That face points down, so the step is +1, at layer 2, the first whose center (2.5) lies above 2.4. The top face at y = 6.6 points up, so its step is −1, at layer 7, whose center is 7.5.

The running sum over layers 0 to 8 reads 0, 0, 1, 1, 1, 1, 1, 0, 0. The box's inside is layers 2 to 6, five voxels, as its extent says. A second box around the first would raise the sum to 2 inside the inner box, still not 0.
:::

A voxel found inside that no triangle marked is the **interior** class: occupancy 1, no color and no normal. Its color never shows, because it has no empty neighbor. Rays stop there, and probes that start in it die. A closed mesh that has a glass or cut-out part counts as open, since its missing faces would leave holes in the sums.

## Thin walls and two-sided voxels

A surface voxel keeps one normal: the sum of its triangles' unit normals. A wall thinner than a voxel puts both of its faces in one voxel, and the normals cancel. A voxel that cannot say which side it faces is a **two-sided voxel**. Strata flags it and gives it no light, rather than let the light of one side into the other.

The :term[finalize]{id=finalize} pass decides with two rules. The first compares the length of the summed normal, in unit normals, with the triangles that added: the voxel is two-sided below 0.5 times the count. The second counts, per axis, the triangles that face within about 41 degrees of it, each way. The voxel is two-sided when the fewer side has at least a quarter as many as the other.

Four triangles, two facing +x and two facing −x, sum to zero, below 0.5 × 4 = 2, so their voxel is two-sided. A floor voxel with two upward triangles sums to 2, above 0.5 × 2 = 1, so it keeps its normal.

The finest level is not the only one that matters. The far cascades read level 1 and coarser, whose voxels are twice as large, so a wall must stay thicker than two voxels of the finest level. Below that, a coarser voxel holds both faces, and the wall turns dark from both sides.

```mermaid caption="The four classes of voxel in cross section. A surface voxel is lit on its front. An interior voxel only blocks. A thin wall in one voxel is two-sided and gets no light. A cut-out surface fills only part of its voxel." alt="Four boxes in a row: surface, interior, two-sided and alpha-masked. The surface box has one normal and occupancy 1. The interior box has occupancy 1 and no color. The two-sided box has two opposite normals and no light. The alpha-masked box has occupancy 0.15."
flowchart LR
    S["Surface voxel: occupancy 1, one normal, lit on its front"]
    I["Interior voxel: occupancy 1, no color, no normal"]
    T["Two-sided voxel: both faces of a wall, normal flag -1, no light"]
    M["Alpha-masked voxel: occupancy 0.15, a partial cell"]
    S --- I --- T --- M
```

## A clipmap: nested windows around the camera

A uniform grid fails by size. The space around a player may be 100 m by 50 m by 100 m. At 10 cm that is 1,000 × 500 × 1,000 = 500 million voxels, and at 20 bytes each, 10 GB. Most of those cells lie far from the camera, where a coarse cell serves as well as a fine one.

A **clipmap** keeps several grids of the same size around the camera, each with cells twice the size of the one before. The part of the world a level holds is its window. At High, Strata has four levels of 128 × 64 × 128 voxels, with cells of 10, 20, 40 and 80 cm. The windows measure 12.8 × 6.4 × 12.8 m up to 102.4 × 51.2 × 102.4 m. Each level holds 1,048,576 voxels, 20 MiB, and the four hold 80 MiB, less than 1 % of the uniform grid.

```mermaid caption="The four levels at High, nested around the camera. Every level holds the same number of voxels, so each covers twice the width of the one inside it." alt="Four boxes inside one another. The outer box, level 3, has 80 cm voxels and a window 102.4 m wide. Inside it lie level 2 and level 1. The innermost box, level 0, has 10 cm voxels and a window 12.8 m wide, with the camera at its center."
flowchart TB
    subgraph L3["Level 3: 80 cm voxels, window 102.4 m wide"]
        subgraph L2["Level 2: 40 cm voxels, 51.2 m"]
            subgraph L1["Level 1: 20 cm voxels, 25.6 m"]
                L0["Level 0: 10 cm voxels, 12.8 m, camera at the center"]
            end
        end
    end
```

A window follows the camera in steps of four voxels, so that most frames move nothing and a move brings in few, large slabs. The camera is the window's center, with one exception: at High the finest level is centered 0.8 m below the camera, because floors lie below the eye.

:::example[A window by hand]
The camera stands at (3.25, 1.75, −2.0) m. At High, level 0 has 0.1 m voxels and centers 0.8 m below the camera, at y = 0.95 m. The center voxel is floor(3.25 / 0.1) = 32 on x, floor(0.95 / 0.1) = 9 on y and floor(−2.0 / 0.1) = −20 on z. Half the dimensions are (64, 32, 64), so the window starts at (−32, −23, −84), rounded down to a multiple of 4: (−32, −24, −84). It covers x from −32 to 95, y from −24 to 39 and z from −84 to 43 voxels.

The camera's voxel lies 64 voxels from the window's minimum on x. The rounding keeps it between 64 and 67, so a camera move of one voxel usually moves nothing.
:::

## Scrolling without moving data

When the window moves, most voxels stay where they are in the world. Copying them to new addresses would cost memory traffic at every step. **Toroidal addressing** avoids the copy: a world voxel lives at the texel found by dividing its index by the dimension and keeping the remainder, so the texture wraps around at its edges. A scroll then replaces only the voxels that left, at the addresses of the voxels that enter. The remainder is never negative: voxel −3 of 128 lives at texel 125.

The voxels a scroll brings in form **slabs**: boxes of the new window that the old window did not hold. The clipmap queues each slab as **regions**, boxes of at most 64 voxels on a side, cut where their texels wrap, that the GPU builds together.

:::example[Scrolling by one step]
The camera moves 0.5 m along x, from 3.25 to 3.75 m. Its center voxel moves from 32 to 37, and the window starts at floor((37 − 64) / 4) × 4 = −28: one step of four voxels. The old window ended at x = 95, so the slab covers x from 96 to 99, y from −24 to 39 and z from −84 to 43. That is 4 × 64 × 128 = 32,768 voxels, 3.1 % of the window's 1,048,576.

Where do they live? The remainder of 96 divided by 128 is 96, so texels 96 to 99. The voxels that left, at x = −32 to −29, lived at exactly those texels, because the remainder of −32 divided by 128 is 96. Nothing else moves.

The slab is cut into regions. Along x it is one piece. Along y it wraps at 0, so it splits into −24 to −1 and 0 to 39. Along z it wraps at 0, and the part from −84 to −1 is longer than 64, so it splits into −84 to −21, −20 to −1 and 0 to 43. That makes 1 × 2 × 3 = 6 regions.
:::

A move of a whole window or more has nothing to keep, so the clipmap queues the window whole. The first frame of a :term[renderer]{id=renderer} does the same.

## Anchors: the same bits wherever the camera is

A float has 24 bits of precision. Near 1 km it resolves 0.06 mm; near 20 km, 2 mm. If the voxelization subtracted the camera first, the same vertex would round differently each time the window moved, and a wall's voxel edge would flicker.

An **anchor** is a voxel index that is a multiple of 1,024 voxels, so 102.4 m at the finest level of High. The voxelization subtracts the anchor from the instance's translation before anything else, in `precise` arithmetic, so every coordinate depends on the anchor alone. `precise` forbids the :term[compiler]{id=compiler} to change the order of those operations or merge them.

The window of the example above starts at x = −32 voxels, and its anchor is floor(−32 / 1,024) × 1,024 = −1,024. Two cameras 37.3 m apart have different windows but the same anchor, so the same vertex gives the same bits. The test `Voxels are independent of the camera` checks it.

The anchor moves only when the camera goes more than 1,000 m beyond its cell on an axis. The clipmap then rebuilds the window's voxels relative to the new anchor and keeps the old voxels valid meanwhile.

:::why
A camera-relative origin would be simpler, but it would change every voxel with every step. Anchors cost a rebuild once in a kilometer. One limit remains: an instance 20 km from the origin has its own translation rounded to 2 mm. The test `20 km out` therefore allows at most 1 % of the voxels to differ from the origin's, each next to an occupied one.
:::

## Budgets and what enters

Voxelization costs time in proportion to triangles, not voxels. Each frame the clipmap takes regions in order: changes first, so a moved object never waits behind a slab, then slabs, then whole windows, level 0 first. It stops when the next region would take the frame past 500,000 triangles, but it always takes one. A frame that rebuilds or jumps a window may spend 4,000,000. The rest waits, and while level 0, 1 or 2 misses more of its window than two scroll steps bring, the frame is pending and the forward pass reads no field.

The clipmap takes active proxies of the static arena whose meshes have indices. Meshes of the skinned arena do not enter: characters receive bounce light, but they neither block it nor bounce it. A material enters as means, because the compute passes read no texture. The :term[albedo]{id=albedo} is the base color times one minus the metallic value, times the mean of the base color map. The emission is the emissive color times its map's mean, so streaming never changes a voxel.

An open mesh takes the coarsest level of detail (LOD) whose error stays within half a voxel, because finer triangles cannot change a voxel. A closed mesh keeps full detail, since a simplified level might open it. Transparent and glass :term[submeshes]{id=submesh} are omitted, and so are submeshes past the 256th, which the clipmap counts; a closed mesh that loses them takes no solid fill.

## The layout from first principles

`ComputeLayout` makes the numbers from a few choices. Every level has the same dimensions, so each costs the same memory. The finest cell must be smaller than a thin wall. The coarsest window decides how far a ray can march before it leaves the copy.

| | High | Low |
| --- | --- | --- |
| Voxel levels | 4, from 10 cm | 3, from 20 cm |
| Level dimensions | 128 × 64 × 128 | 64 × 32 × 64 |
| Coarsest window | 102.4 × 51.2 × 102.4 m | 51.2 × 25.6 × 51.2 m |
| Cascades, from spacing | 4, from 0.5 m | 3, from 1 m |
| Directions per probe | 64, 64, 256, 1,024 | 64, 64, 256 |
| Bounces | Every bounce | One |
| Memory per view | 155.7 MiB | 24.9 MiB |

The memory counts everything the frame makes, at any resolution, for each view that runs GI: two views hold it twice. At High, the voxel levels take 83,886,080 bytes of 163,305,072. The test `Memory adds up` checks every term. The guide's layout line says the cascades hold 16 to 1,024 directions, but cascade 0 marches cascade 1's 64, as the table says.

The sweep shows one room at both layouts. The room's own scene does not ask for GI, so the shot enables it in the Post Process.

::compare{id=low-high}

## A toy version

The toy turns a box of twelve triangles into voxels of a unit grid, with the same 13-axis test as the shader. Look at how `AxisSeparates` projects the triangle on an axis and compares it with the box's radius. The box spans 2.4 to 6.6 on each axis, off the grid, so each face lies inside one layer of voxels.

```cpp sketch="indirect-gi-voxels-toy.cpp"
// Voxelizes a box's twelve triangles on a grid of unit voxels with Akenine-Moller's triangle-box test.
#include <glm/glm.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <set>
#include <vector>

struct Triangle
{
	glm::vec3 A;
	glm::vec3 B;
	glm::vec3 C;
};

// True when the axis puts the triangle's shadow and the box's shadow apart. The box is centered on the origin.
static bool AxisSeparates(const glm::vec3& axis, const Triangle& triangle, const glm::vec3& halfSize)
{
	const float p0 = glm::dot(triangle.A, axis);
	const float p1 = glm::dot(triangle.B, axis);
	const float p2 = glm::dot(triangle.C, axis);
	const float radius = halfSize.x * std::abs(axis.x) + halfSize.y * std::abs(axis.y) + halfSize.z * std::abs(axis.z);
	return std::max({ p0, p1, p2 }) < -radius || std::min({ p0, p1, p2 }) > radius;
}

// Touching counts as overlap. Thirteen axes decide: nine edge crossings, three box faces and the triangle's plane.
static bool TriangleBoxOverlap(const glm::vec3& center, const glm::vec3& halfSize, Triangle triangle)
{
	triangle.A -= center;
	triangle.B -= center;
	triangle.C -= center;
	const std::array<glm::vec3, 3> edges = { triangle.B - triangle.A, triangle.C - triangle.B, triangle.A - triangle.C };
	const std::array<glm::vec3, 3> axes = { glm::vec3(1, 0, 0), glm::vec3(0, 1, 0), glm::vec3(0, 0, 1) };
	for (const glm::vec3& axis : axes)
	{
		for (const glm::vec3& edge : edges)
		{
			if (AxisSeparates(glm::cross(axis, edge), triangle, halfSize))
				return false;
		}
		if (AxisSeparates(axis, triangle, halfSize))
			return false;
	}
	return !AxisSeparates(glm::cross(edges[0], edges[1]), triangle, halfSize);
}

// A face with its normal along cross(u, v) is two triangles.
static void AddFace(std::vector<Triangle>& triangles, const glm::vec3& origin, const glm::vec3& u, const glm::vec3& v)
{
	triangles.push_back({ origin, origin + u, origin + u + v });
	triangles.push_back({ origin, origin + u + v, origin + v });
}

static std::vector<Triangle> MakeBox(float low, float high)
{
	const float s = high - low;
	const glm::vec3 o(low);
	std::vector<Triangle> triangles;
	AddFace(triangles, o, glm::vec3(0, 0, s), glm::vec3(0, s, 0));
	AddFace(triangles, { high, low, low }, glm::vec3(0, s, 0), glm::vec3(0, 0, s));
	AddFace(triangles, o, glm::vec3(s, 0, 0), glm::vec3(0, 0, s));
	AddFace(triangles, { low, high, low }, glm::vec3(0, 0, s), glm::vec3(s, 0, 0));
	AddFace(triangles, o, glm::vec3(0, s, 0), glm::vec3(s, 0, 0));
	AddFace(triangles, { low, low, high }, glm::vec3(s, 0, 0), glm::vec3(0, s, 0));
	return triangles;
}

int main()
{
	std::set<std::array<int, 3>> voxels;
	for (const Triangle& triangle : MakeBox(2.4f, 6.6f))
	{
		const glm::vec3 low = glm::min(glm::min(triangle.A, triangle.B), triangle.C);
		const glm::vec3 high = glm::max(glm::max(triangle.A, triangle.B), triangle.C);
		for (int z = int(std::floor(low.z)); z <= int(std::floor(high.z)); z++)
		{
			for (int y = int(std::floor(low.y)); y <= int(std::floor(high.y)); y++)
			{
				for (int x = int(std::floor(low.x)); x <= int(std::floor(high.x)); x++)
				{
					if (TriangleBoxOverlap(glm::vec3(x, y, z) + 0.5f, glm::vec3(0.5f), triangle))
						voxels.insert({ x, y, z });
				}
			}
		}
	}
	std::printf("voxels touched by the box's surface: %zu\n", voxels.size());
	for (int z = 0; z < 9; z++)
	{
		for (int x = 0; x < 9; x++)
			std::printf("%c ", voxels.count({ x, 4, z }) ? '#' : '.');
		std::printf("\n");
	}
}
```

```text output-of="indirect-gi-voxels-toy.cpp"
voxels touched by the box's surface: 98
. . . . . . . . . 
. . . . . . . . . 
. . # # # # # . . 
. . # . . . # . . 
. . # . . . # . . 
. . # . . . # . . 
. . # # # # # . . 
. . . . . . . . . 
. . . . . . . . . 
```

1. **Lines 19–26:** an axis separates when the triangle's range of dot products lies wholly outside the box's range.
2. **Lines 29–47:** the thirteen axes: nine edge crossings, three box faces and, in the last line, the triangle's plane.
3. **Line 84:** a voxel enters the set once, however many triangles touch it; the GPU gets this from the key's maximum.

The box covers 5 voxels on each axis, 125 in all, and its inside holds 3 × 3 × 3 = 27. Only the 98 voxels of the shell are touched, and the output shows them as a ring in the middle slice. Voxelization alone finds the shell; the fill finds the other 27.

## The real code, in the order data flows

The frame starts with the layout. This excerpt of `ComputeLayout` makes the levels and the cascades from a few numbers; compare each line with the table above.

```cpp src="Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp#L167-L184" from="for (uint32_t index = 0; index < levelCount; index++)" to="layout.Cascades.push_back(cascade);" symbol="GlobalIllumination::ComputeLayout"
for (uint32_t index = 0; index < levelCount; index++)
	layout.Levels.push_back(VoxelLevelLayout { firstVoxelSize * static_cast<float>(1u << index), dimensions, index == 0 && high ? RenderData::c_GIFinestLevelDrop : 0.0f });
for (uint32_t k = 0; k < cascadeCount; k++)
{
	ProbeCascadeLayout cascade;
	cascade.Spacing = firstSpacing * static_cast<float>(1u << k);
	cascade.Grid = firstGrid / (1u << k);
	// Directions four times as many per cascade from cascade 1's 64; cascade 0 marches cascade 1's directions (its rays go
	// straight into the field, each continued by cascade 1's merged ray of the same direction: FieldReduce.comp).
	cascade.DirectionsPerAxis = 4u << std::max(k, 1u);
	// Intervals four times as long per cascade: [0, s0], [s0, 4 s0], [4 s0, 16 s0]..., the top one without an end.
	cascade.IntervalStart = k == 0 ? 0.0f : firstSpacing * static_cast<float>(1u << (2 * (k - 1)));
	cascade.IntervalEnd = k + 1 == cascadeCount ? std::numeric_limits<float>::infinity() : firstSpacing * static_cast<float>(1u << (2 * k));
	cascade.LeadIn = cascade.IntervalStart;
	cascade.Overlap = k + 1 == cascadeCount ? 0.0f : cascade.Spacing;
	cascade.MinimumLevel = k == 0 ? 0 : std::min(k - 1, 1u);
	cascade.SubRays = k > 0 && k + 1 < cascadeCount ? 2u : 1u;
	layout.Cascades.push_back(cascade);
```

1. **Line 168:** `1u << index` doubles the voxel size at each level.
2. **Line 173:** the grid of probes halves on every axis from one cascade to the next.
3. **Line 176:** cascades 0 and 1 both get 8 × 8 = 64 directions, and each later cascade gets four times as many.
4. **Line 182:** cascades 0 and 1 read voxel level 0, and the later ones start at level 1.

The toy fixes one grid, and the clipmap moves it. When the window moves, `GetScrollSlabs` returns the boxes that entered, as the scrolling example computed by hand. Look at how each axis takes the part beyond the old window, inside the overlap on earlier axes, so that the pieces never overlap.

```cpp src="Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp#L302-L332" symbol="GlobalIllumination::GetScrollSlabs"
bool GetScrollSlabs(const glm::i64vec3& oldMinimum, const glm::i64vec3& newMinimum, const glm::uvec3& dimensions, std::vector<VoxelBox>& outSlabs)
{
	const glm::i64vec3 size(dimensions);
	for (int axis = 0; axis < 3; axis++)
	{
		const int64_t move = newMinimum[axis] - oldMinimum[axis];
		if (move >= size[axis] || -move >= size[axis])
			return false;
	}
	const VoxelBox before { oldMinimum, oldMinimum + size };
	const VoxelBox after { newMinimum, newMinimum + size };
	// Axis by axis: the new window's part beyond the old one on this axis, within the overlap on the axes before it and
	// the new window's whole range on the axes after it. The three are disjoint and make up the new window minus the old.
	for (int axis = 0; axis < 3; axis++)
	{
		if (newMinimum[axis] == oldMinimum[axis])
			continue;
		VoxelBox slab = after;
		for (int earlier = 0; earlier < axis; earlier++)
		{
			slab.Minimum[earlier] = std::max(before.Minimum[earlier], after.Minimum[earlier]);
			slab.Maximum[earlier] = std::min(before.Maximum[earlier], after.Maximum[earlier]);
		}
		if (newMinimum[axis] > oldMinimum[axis])
			slab.Minimum[axis] = before.Maximum[axis];
		else
			slab.Maximum[axis] = before.Minimum[axis];
		SplitRegion(slab, dimensions, outSlabs);
	}
	return true;
}
```

1. **Lines 308–309:** a move of a whole window on any axis leaves nothing to keep, so the function fails and the window is rebuilt whole.
2. **Lines 322–323:** on the axes before the moving one, the slab shrinks to the overlap of both windows, so slabs never share a voxel.
3. **Lines 325–328:** on the moving axis the slab is the new window's part beyond the old window.
4. **Line 329:** `SplitRegion` cuts the slab into the regions of the example.

The GPU's side begins with the shader version of the toy's test, which `VoxelTriangles` calls for every cell in a small triangle's bounds.

```slang src="Strata/shaders/Include/Voxelize.slang#L171-L196" symbol="TriangleBoxOverlap"
// Whether a triangle overlaps a box (center, half size); touching counts.
bool TriangleBoxOverlap(float3 center, float3 halfSize, float3 a, float3 b, float3 c)
{
	float3 v0 = a - center;
	float3 v1 = b - center;
	float3 v2 = c - center;
	float3 e0 = v1 - v0;
	float3 e1 = v2 - v1;
	float3 e2 = v0 - v2;
	float3 axes[3] = { float3(1.0, 0.0, 0.0), float3(0.0, 1.0, 0.0), float3(0.0, 0.0, 1.0) };
	[unroll]
	for (int axis = 0; axis < 3; axis++)
	{
		if (AxisSeparates(cross(axes[axis], e0), v0, v1, v2, halfSize) || AxisSeparates(cross(axes[axis], e1), v0, v1, v2, halfSize)
			|| AxisSeparates(cross(axes[axis], e2), v0, v1, v2, halfSize))
			return false;
	}
	if (max(max(v0.x, v1.x), v2.x) < -halfSize.x || min(min(v0.x, v1.x), v2.x) > halfSize.x)
		return false;
	if (max(max(v0.y, v1.y), v2.y) < -halfSize.y || min(min(v0.y, v1.y), v2.y) > halfSize.y)
		return false;
	if (max(max(v0.z, v1.z), v2.z) < -halfSize.z || min(min(v0.z, v1.z), v2.z) > halfSize.z)
		return false;
	float3 normal = cross(e0, e1);
	return abs(dot(normal, v0)) <= halfSize.x * abs(normal.x) + halfSize.y * abs(normal.y) + halfSize.z * abs(normal.z);
}
```

1. **Lines 174–176:** the box's center moves to the origin, as in the example by hand.
2. **Lines 182–187:** nine axes, each a box axis crossed with a triangle edge; one :term[separating axis]{id=separating-axis} ends the test.
3. **Lines 188–193:** the three face axes of the box, as range tests of the triangle's bounds.
4. **Lines 194–195:** the triangle's plane separates when its distance from the center exceeds the box's reach along its normal.

The toy lacks three things the real passes add. A triangle whose bounds hold more than 64 voxels goes to tiles of 8 × 8 × 8 voxels. A group of threads handles each tile in `VoxelTiles`, so that one road triangle of 220 m does not keep a single thread busy for milliseconds. `VoxelTriangles` counts the tiles into an argument buffer, and the dispatch of `VoxelTiles` reads its group count from it, so the CPU never learns the count. Then `VoxelFill` runs one thread per column and sums the winding steps upward.

```slang src="Strata/shaders/GI/VoxelFill.comp.slang#L37-L50" from="int sum = 0;" to="u_Scratch.Store(GetScratchAddress(ST_SCRATCH_KEYS, voxel), key | ST_VOXEL_KEY_SOLID);" symbol="main"
int sum = 0;
for (int y = 0; y < size.y; y++)
{
	uint voxel = GetScratchVoxel(region, int3(x, y, z));
	sum += int(u_Scratch.Load(GetScratchAddress(ST_SCRATCH_WINDING, voxel)));
	if (sum == 0)
		continue;
	// Inside a closed mesh: interior where nothing marked it, and solid where a face only touched it from the front (a box's
	// bottom layer on a floor's top).
	uint key = u_Scratch.Load(GetScratchAddress(ST_SCRATCH_KEYS, voxel));
	if ((key >> 30) == 0u)
		u_Scratch.Store(GetScratchAddress(ST_SCRATCH_KEYS, voxel), ST_VOXEL_CLASS_INTERIOR << 30);
	else if ((key & ST_VOXEL_KEY_SOLID) == 0u)
		u_Scratch.Store(GetScratchAddress(ST_SCRATCH_KEYS, voxel), key | ST_VOXEL_KEY_SOLID);
```

1. **Line 41:** the running sum adds each layer's winding steps, from the bottom of the region up.
2. **Lines 42–43:** a sum of 0 means outside, so the voxel keeps what the surface pass wrote.
3. **Lines 47–48:** nothing marked this inside voxel, so it becomes the interior class.
4. **Lines 49–50:** a face touched this voxel only from the front, so it gets the solid bit.

`VoxelFinalize` turns the scratch into the three textures of each level. The excerpt is the two-sided decision: the `opposing` flag from the facing counts, then the choice among a double-sided material, a voxel behind every face, a normal that holds and a two-sided voxel.

```slang src="Strata/shaders/GI/VoxelFinalize.comp.slang#L64-L80" from="bool opposing = false;" to="normal = float4(0.0, 0.0, 0.0, -1.0);" symbol="main"
bool opposing = false;
[unroll]
for (uint axis = 0u; axis < 3u; axis++)
{
	uint positive = u_Scratch.Load(GetScratchAddress(ST_SCRATCH_FACING_POSITIVE + axis, voxel));
	uint negative = u_Scratch.Load(GetScratchAddress(ST_SCRATCH_FACING_NEGATIVE + axis, voxel));
	uint fewer = min(positive, negative);
	opposing = opposing || (fewer > 0u && float(fewer) >= ST_GI_OPPOSED_SHARE * float(max(positive, negative)));
}
if ((key & ST_VOXEL_KEY_DOUBLE_SIDED) != 0u)
	normal = float4(summedLength > 0.0 ? summed / summedLength : float3(0.0, 0.0, 0.0), 0.5);
else if (added == 0u)
	normal = float4(0.0, 0.0, 0.0, 0.0); // Behind every face that touched it: no surface of its own
else if (!opposing && summedLength >= ST_GI_TWO_SIDED_SUM * float(added))
	normal = float4(summed / summedLength, 1.0);
else
	normal = float4(0.0, 0.0, 0.0, -1.0);
```

1. **Lines 64–71:** per axis, count the triangles that face each way; the voxel opposes itself when the fewer side has a quarter as many.
2. **Lines 73–74:** a double-sided material keeps the summed normal with the flag 0.5, lit from both sides.
3. **Lines 75–76:** no triangle added a normal, so the voxel lies behind every face and has no surface of its own.
4. **Lines 77–78:** a normal that holds, with the flag 1, needs no opposing faces and a long enough sum.
5. **Lines 79–80:** otherwise the flag −1 marks the voxel two-sided.

The renderer records one batch at a time, and a batch holds the regions of one level whose voxels fit the scratch. The loop clears the scratch and runs the four passes with a barrier after each, because consecutive passes through one :term[binding set]{id=binding-set} read each other's writes.

```cpp src="Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp#L912-L950" from="commandList->clearBufferUInt(gi.Scratch, 0);" to="commandList->dispatch(DivideUp(batch.Voxels, c_GroupSize));" symbol="SceneRenderer::RecordGlobalIllumination"
commandList->clearBufferUInt(gi.Scratch, 0);
const uint32_t arguments[4] = { 0, 1, 1, 0 };
commandList->writeBuffer(gi.TileArguments, arguments, sizeof(arguments));

nvrhi::ComputeState state;
state.bindings = { voxelSet };
// The triangles, in dispatches of at most c_MaxDispatchGroups groups.
state.pipeline = gi.TrianglesPipeline;
commandList->setComputeState(state);
for (uint32_t first = 0; first < batch.GroupCount; first += c_MaxDispatchGroups)
{
	RenderData::VoxelPassParameters part = parameters;
	part.FirstGroup = batch.FirstGroup + first;
	part.GroupCount = std::min(c_MaxDispatchGroups, batch.GroupCount - first);
	commandList->setPushConstants(&part, sizeof(part));
	commandList->dispatch(part.GroupCount);
}
scratchBarrier();

// The large triangles' tiles, as many groups as VoxelTriangles listed.
nvrhi::ComputeState tilesState;
tilesState.pipeline = gi.TilesPipeline;
tilesState.bindings = { gi.TilesSets[batch.Level] };
tilesState.indirectParams = gi.TileArguments;
commandList->setComputeState(tilesState);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatchIndirect(0);
scratchBarrier();

state.pipeline = gi.FillPipeline;
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch(DivideUp(batch.Columns, c_GroupSize));
scratchBarrier();

state.pipeline = gi.FinalizePipeline;
commandList->setComputeState(state);
commandList->setPushConstants(&parameters, sizeof(parameters));
commandList->dispatch(DivideUp(batch.Voxels, c_GroupSize));
```

1. **Line 912:** every batch starts with a cleared scratch, so no voxel keeps the work of an earlier batch.
2. **Lines 921–928:** `VoxelTriangles` runs in parts of at most `c_MaxDispatchGroups` groups, the limit of one dispatch.
3. **Lines 935–938:** `VoxelTiles` reads its group count from the buffer that `VoxelTriangles` filled.
4. **Lines 944–950:** `VoxelFill` runs per column and `VoxelFinalize` per voxel, each after a barrier.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Sparse voxel octree | Research on voxel cone tracing | Memory in proportion to surface, and fine detail where surfaces are | Direct addressing of a cell: a tree needs pointer chasing, and a changing scene rebuilds branches |
| Voxel cone tracing on clipmaps | NVIDIA's voxel global illumination | One cone per pixel for diffuse and specular light | Cones blur and leak through thin walls, and they need a filtered, lit copy of the voxels |
| Signed distance fields | Unreal Engine's software tracing | Long steps through empty space; smooth thin shapes | A field per mesh at import time; open meshes give poor fields |
| Ray-traced probes | NVIDIA's probe-based global illumination | Exact hits on the real triangles, no voxel copy and no thin-wall rule | A hardware or driver feature, and light blended over frames, which Strata forbids |

## How it is tested

The CPU arithmetic needs no GPU. The suite `Renderer.GlobalIlluminationLayout` holds `The High and Low layouts`, `Memory adds up`, `Windows snap and follow`, `Scrolling queues exactly what entered` and `Voxels are independent of the camera`. The suite `Renderer.VoxelClipmap` checks the queue, for example `A jump queues every window within the cut's budget, level 0 first`, and `Renderer.Mesh` holds `Closed meshes are found`.

The suite `GPU.SceneRenderer.GlobalIllumination` runs the passes on a device. `A box voxelizes to its cells` compares a box with `ReferenceVoxels` in `StrataTests/src/Renderer/GIScenes.h`, and `A plane is open and faces up, and thin walls are two-sided` checks the classes. Run one suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.VoxelClipmap`.

## Changing it safely

- **Change the CPU and GPU versions of a coordinate together.** `GlobalIllumination::GetVoxelCoordinate` repeats the shader's operations in its order, and a test compares them to the bit.
- **Use integer atomics and maxima only.** A float add would make the scratch depend on thread order.
- **Give a new pass a GPU stage and a barrier.** `AGENTS.md` asks for the stage, and consecutive passes through one binding set need explicit barriers.
- **Never address the camera.** Anything that depends on the camera, other than the window, breaks the anchors' promise.
- **Read geometry through the pool, every frame.** Mesh data moves when the pool compacts ([the geometry pool](../gpu/geometry-pool.md)).
- **Keep the memory test and the guide in step.** A new buffer changes `Memory adds up`.

## What went wrong before

The first rule for two-sided voxels summed the normals' components. The pole of a sphere built from small triangles has 48 of them leaning 3.75 degrees around it. Their normals cancel a little on each axis, so the pole's voxel looked two-sided and went dark at every level. Rough ground did the same. The commit `30b52fb0` changed the rule to count the triangles that face each way along an axis, and the test `Curved and rough surfaces stay one-sided, a thin wall on the ground two-sided` guards it.

## Summary

- A triangle becomes voxels through the 13-axis triangle-box test, run by one GPU thread per triangle, and integer atomics make the result independent of thread order.
- A closed mesh turns solid by winding steps along vertical columns, and a voxel that holds both faces of a thin wall becomes two-sided and gets no light.
- A level's window follows the camera in steps of four voxels, and toroidal addressing writes only the slabs that entered.
- A layout's memory is the sum of its buffers: High takes 155.7 MiB and Low 24.9 MiB per view that runs GI.
- A batch of regions goes through `VoxelTriangles`, the indirect `VoxelTiles`, `VoxelFill` and `VoxelFinalize`, with a barrier after each.

## Check yourself

1. In the example of one axis, the corners project to −1.21, −1.21 and −2.42, and the box's radius is 1.1. How wide must the voxel be before that axis stops separating?

   :::answer{tests="explain-voxelize"}
   The radius must reach 1.21. With half sizes h on x and y, the radius is 1.1h + 1.1h = 2.2h, so h = 0.55 and the voxel is 1.1 wide. Touching counts as overlap, so at that width the test reports an overlap.
   :::

2. A column through two nested closed boxes meets four surfaces, going up: +1 at layer 3, +1 at layer 5, −1 at layer 8 and −1 at layer 10. Which layers are inside?

   :::answer{tests="explain-fill"}
   The running sum over layers 0 to 11 is 0, 0, 0, 1, 1, 2, 2, 2, 1, 1, 0, 0, so layers 3 to 9 are inside. A parity test would call layers 5 to 7 outside, because the count there is 2; a test for a count that is not 0 does not.
   :::

3. At High, a 6 cm wall has both faces in one 10 cm voxel of level 0. Is that voxel one-sided, two-sided or interior?

   :::answer{tests="explain-fill"}
   The voxel is two-sided. The faces add +256 and −256 on one axis, so the sum is zero, below 0.5 times the count, and the opposing counts are equal. The voxel is not interior, because triangles marked it.
   :::

4. A world voxel has the index −130 on an axis of 128 voxels. At which texel does it live, and where does voxel 130 live?

   :::answer{tests="compute-window"}
   The remainder is never negative: −130 + 2 × 128 = 126. Voxel 130 lives at 130 − 128 = 2. The two voxels share no texel, because indices share one only when they differ by a multiple of 128, and these differ by 260.
   :::

5. A game shows two cameras at once, each with its own renderer that runs GI at High. How much GPU memory does GI take?

   :::answer{tests="compute-memory"}
   Each view holds its own layout's memory, 155.7 MiB, so the two hold 311.4 MiB. The size of the image does not change it.
   :::

6. Why does the renderer dispatch `VoxelTiles` indirectly?

   :::answer{tests="trace-batch"}
   The number of tiles is known only after `VoxelTriangles` has run, because each large triangle adds its tiles with an atomic. The pass writes the count into an argument buffer on the GPU, and the dispatch reads its group count from there. Reading the count on the CPU would stall the frame.
   :::

## Exercises

1. **Basic.** Trace it yourself. Follow one batch of voxel work from the frame the CPU builds to the finished voxels, and name the function and the lines where each step happens.

   :::answer[Worked solution]{tests="trace-batch"}
   `SceneRenderer::PrepareGlobalIllumination` in `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp` calls `VoxelClipmap::BuildFrame` at line 586, which lists the regions, work items and batches. `SceneRenderer::RecordGlobalIllumination` loops over the batches from line 900, clears the scratch at line 912 and resets the tile counter at lines 913 and 914. Line 927 dispatches `VoxelTriangles` in parts of at most `c_MaxDispatchGroups` groups. Line 938 dispatches `VoxelTiles` indirectly, line 944 `VoxelFill` per column and line 950 `VoxelFinalize` per voxel, each followed by `scratchBarrier()`. The tiles' dispatch is indirect because line 163 of `Strata/shaders/GI/VoxelTriangles.comp.slang` counts them on the GPU.
   :::

2. **Medium.** Compute the memory of the Low layout's voxel levels, its scratch and its cascade atlases by hand, and compare with `Memory adds up`.

   :::answer[Worked solution]{tests="compute-memory"}
   A voxel takes 4 + 4 + 4 + 8 = 20 bytes. Low has 3 levels of 64 × 32 × 64 = 131,072 voxels, so the levels take 3 × 131,072 × 20 = 7,864,320 bytes. The scratch holds one level's voxels at 14 words of 4 bytes: 131,072 × 56 = 7,340,032 bytes.

   The atlases belong to cascades 1 and 2, because cascade 0 sends its rays into the field. Cascade 1 has 12 × 10 × 12 = 1,440 probes with 64 directions of 8 bytes: 737,280 bytes. Cascade 2 has 180 probes with 256 directions: 368,640 bytes. The atlases total 1,105,920 bytes, and the three terms match the test's values.
   :::

3. **Hard.** Extend the toy so that it also fills the box with winding steps along vertical columns, and print how many voxels are solid and how many are interior.

   :::answer[Worked solution]{tests="explain-fill" solution="sketches/indirect-gi-voxels-fill.cpp"}
   The sketch adds `AddWindingSteps`. For each column it tests whether the line through the column lies inside a triangle seen from above. It takes the height of the crossing and adds +1 or −1 at the first voxel whose center lies above it. A sweep along each column then sums the steps.

   ```cpp sketch="indirect-gi-voxels-fill.cpp"
   // Voxelizes a closed box, then fills its inside by counting winding steps along each column of voxels.
   #include <glm/glm.hpp>

   #include <algorithm>
   #include <array>
   #include <cmath>
   #include <cstdio>
   #include <set>
   #include <vector>

   struct Triangle
   {
   	glm::vec3 A;
   	glm::vec3 B;
   	glm::vec3 C;
   };

   static bool AxisSeparates(const glm::vec3& axis, const Triangle& triangle, const glm::vec3& halfSize)
   {
   	const float p0 = glm::dot(triangle.A, axis);
   	const float p1 = glm::dot(triangle.B, axis);
   	const float p2 = glm::dot(triangle.C, axis);
   	const float radius = halfSize.x * std::abs(axis.x) + halfSize.y * std::abs(axis.y) + halfSize.z * std::abs(axis.z);
   	return std::max({ p0, p1, p2 }) < -radius || std::min({ p0, p1, p2 }) > radius;
   }

   static bool TriangleBoxOverlap(const glm::vec3& center, const glm::vec3& halfSize, Triangle triangle)
   {
   	triangle.A -= center;
   	triangle.B -= center;
   	triangle.C -= center;
   	const std::array<glm::vec3, 3> edges = { triangle.B - triangle.A, triangle.C - triangle.B, triangle.A - triangle.C };
   	const std::array<glm::vec3, 3> axes = { glm::vec3(1, 0, 0), glm::vec3(0, 1, 0), glm::vec3(0, 0, 1) };
   	for (const glm::vec3& axis : axes)
   	{
   		for (const glm::vec3& edge : edges)
   		{
   			if (AxisSeparates(glm::cross(axis, edge), triangle, halfSize))
   				return false;
   		}
   		if (AxisSeparates(axis, triangle, halfSize))
   			return false;
   	}
   	return !AxisSeparates(glm::cross(edges[0], edges[1]), triangle, halfSize);
   }

   static void AddFace(std::vector<Triangle>& triangles, const glm::vec3& origin, const glm::vec3& u, const glm::vec3& v)
   {
   	triangles.push_back({ origin, origin + u, origin + u + v });
   	triangles.push_back({ origin, origin + u + v, origin + v });
   }

   static std::vector<Triangle> MakeBox(float low, float high)
   {
   	const float s = high - low;
   	const glm::vec3 o(low);
   	std::vector<Triangle> triangles;
   	AddFace(triangles, o, glm::vec3(0, 0, s), glm::vec3(0, s, 0));
   	AddFace(triangles, { high, low, low }, glm::vec3(0, s, 0), glm::vec3(0, 0, s));
   	AddFace(triangles, o, glm::vec3(s, 0, 0), glm::vec3(0, 0, s));
   	AddFace(triangles, { low, high, low }, glm::vec3(0, 0, s), glm::vec3(s, 0, 0));
   	AddFace(triangles, o, glm::vec3(0, s, 0), glm::vec3(s, 0, 0));
   	AddFace(triangles, { low, low, high }, glm::vec3(s, 0, 0), glm::vec3(0, s, 0));
   	return triangles;
   }

   static float Edge(const glm::vec2& a, const glm::vec2& b, const glm::vec2& p)
   {
   	return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);
   }

   // Adds +1 where the column's line enters the mesh and -1 where it leaves, at the first voxel whose center lies above the crossing.
   static void AddWindingSteps(const Triangle& triangle, int steps[9][9][9])
   {
   	const float facing = glm::cross(triangle.B - triangle.A, triangle.C - triangle.A).y;
   	if (std::abs(facing) < 1e-9f)
   		return;
   	const glm::vec2 a(triangle.A.x, triangle.A.z);
   	const glm::vec2 b(triangle.B.x, triangle.B.z);
   	const glm::vec2 c(triangle.C.x, triangle.C.z);
   	const float sign = Edge(a, b, c) < 0.0f ? -1.0f : 1.0f;
   	for (int z = 0; z < 9; z++)
   	{
   		for (int x = 0; x < 9; x++)
   		{
   			const glm::vec2 p(float(x) + 0.50137f, float(z) + 0.50291f); // Off the voxel centers, so no mesh edge lies on a line
   			const float w0 = sign * Edge(b, c, p);
   			const float w1 = sign * Edge(c, a, p);
   			const float w2 = sign * Edge(a, b, p);
   			if (w0 < 0.0f || w1 < 0.0f || w2 < 0.0f)
   				continue;
   			const float y = (w0 * triangle.A.y + w1 * triangle.B.y + w2 * triangle.C.y) / (w0 + w1 + w2);
   			const int layer = std::max(int(std::floor(y - 0.5f)) + 1, 0);
   			if (layer < 9)
   				steps[x][layer][z] += facing < 0.0f ? 1 : -1;
   		}
   	}
   }

   int main()
   {
   	const std::vector<Triangle> box = MakeBox(2.4f, 6.6f);
   	std::set<std::array<int, 3>> surface;
   	int steps[9][9][9] = {};
   	for (const Triangle& triangle : box)
   	{
   		AddWindingSteps(triangle, steps);
   		const glm::vec3 low = glm::min(glm::min(triangle.A, triangle.B), triangle.C);
   		const glm::vec3 high = glm::max(glm::max(triangle.A, triangle.B), triangle.C);
   		for (int z = int(std::floor(low.z)); z <= int(std::floor(high.z)); z++)
   		{
   			for (int y = int(std::floor(low.y)); y <= int(std::floor(high.y)); y++)
   			{
   				for (int x = int(std::floor(low.x)); x <= int(std::floor(high.x)); x++)
   				{
   					if (TriangleBoxOverlap(glm::vec3(x, y, z) + 0.5f, glm::vec3(0.5f), triangle))
   						surface.insert({ x, y, z });
   				}
   			}
   		}
   	}
   	int solid = 0;
   	int interior = 0;
   	for (int z = 0; z < 9; z++)
   	{
   		for (int x = 0; x < 9; x++)
   		{
   			int sum = 0;
   			for (int y = 0; y < 9; y++)
   			{
   				sum += steps[x][y][z];
   				if (sum == 0)
   					continue;
   				solid++;
   				interior += surface.count({ x, y, z }) == 0 ? 1 : 0;
   			}
   		}
   	}
   	std::printf("surface %zu, solid %d, interior %d\n", surface.size(), solid, interior);
   }
   ```

   ```text output-of="indirect-gi-voxels-fill.cpp"
   surface 98, solid 125, interior 27
   ```

   1. **Line 86:** the column's line sits off the voxel centers, so no edge of the box lies exactly on one and no crossing counts twice.
   2. **Lines 93–95:** the crossing's layer is the first voxel whose center lies above it, and a downward face adds +1.
   3. **Lines 131–135:** a voxel with a running count that is not 0 is solid, and a solid voxel that no triangle touched is interior.

   The output shows 125 solid voxels, 98 of them the shell and 27 the interior, as the example by hand predicted.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h` and `.cpp`: `ComputeLayout`, `GetVoxelIndex`, `GetWindowMinimum`, `GetTexel`, `GetScrollSlabs`, `GetAnchorVoxel`, `GetVoxelCoordinate`, `PackRGB9E5` and the memory.
- `Strata/src/Strata/Renderer/VoxelClipmap.h` and `.cpp`: `VoxelClipmap::BuildFrame`, `FollowCamera`, `TakeRegion` and the region queues.
- `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp`: `PrepareGlobalIllumination` and `RecordGlobalIllumination`.
- `Strata/shaders/Include/Voxelize.slang` and `Strata/shaders/GI/*.comp.slang`: the four passes `VoxelTriangles`, `VoxelTiles`, `VoxelFill` and `VoxelFinalize`.
- `Strata/src/Strata/Renderer/Mesh.cpp`: `MeshUtils::IsClosed`.
- Settings: `PostProcessComponent::GlobalIllumination`, `GlobalIlluminationIntensity` and the quality row `Renderer.Quality.GlobalIllumination`.
- Tests: `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp`, `VoxelClipmapTests.cpp`, `MeshTests.cpp` and `GPUSceneGlobalIlluminationTests.cpp`.

## Further reading

- Tomas Akenine-Moller, "Fast 3D Triangle-Box Overlap Testing" (journal of graphics tools, 2001; intermediate): the 13-axis test.
- Cyril Crassin and others, "Interactive Indirect Illumination Using Voxel Cone Tracing" (paper, 2011; advanced): the voxel octree that Strata did not choose.
- Zander Majercik and others, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields" (paper, 2019; advanced): probes against real triangles.
- Epic Games, "Lumen: Real-time Global Illumination in Unreal Engine 5" (SIGGRAPH talk, 2022; intermediate): signed distance fields as the software trace.
- Alexander Sannikov, "Radiance Cascades" (paper, 2023; advanced): the cascades that march through these voxels.
