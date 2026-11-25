---
id: light/many-lights
title: "Many lights: culling and clustered forward shading"
description: "How Strata finds the few lights that reach each pixel out of thousands in view: culling, ranking, a grid of clusters and the forward light loop."
kind: internals
size: L
tracks: [E]
needs: [light/lights, gpu/compute, draw/bounds-culling, draw/gpu-driven]
time: 90
learn:
  - id: clustered-idea
    text: explain why a clustered grid gives each pixel fewer lights than tiles or one pass per light
  - id: two-paths
    text: compare the CPU and GPU light paths, and what each does when more lights are in view than fit
  - id: cluster-index
    text: compute the cluster and the buffer offset that a pixel reads from its screen position and view depth
  - id: keep-relevant
    text: predict which lights a full cluster keeps and which the relevance search drops
  - id: measure-grid
    text: measure what a different cluster grid costs in the light passes and in the opaque stage
since: 0.3.0
status: final
---

A scene can hold thousands of lights, yet any one pixel is reached by a handful of them. The job of this part of the :term[renderer]{id=renderer} is to hand each pixel only the lights that reach it. It works in two steps. **Light culling** removes the lights whose region misses the view, and a grid of small boxes then lists, for each box, the lights that touch it. The forward :term[shader]{id=shader} of a pixel reads the list of its own box and shades with those lights alone.

Other pages teach what a light record holds ([Lights](../light/lights.md)) and :term[frustum]{id=view-frustum} tests in general ([Bounds and culling](../draw/bounds-culling.md)). They also teach the shadow slots of shadowed lights ([Local light shadows](../light/local-shadows.md)) and the lobe of a light's source ([Area lights](../light/area-lights.md)).

## The problem and how engines solve it

Start with a count. A 1,920 by 1,080 image has 2,073,600 pixels. If every pixel evaluates each of 1,000 lights, one frame costs 2,073,600,000 evaluations, over two billion. A light has a range, though, and beyond it the light adds nothing, so almost all of those evaluations return zero. The task is to skip them without testing them one by one.

Engines use four answers, and each trades one cost for another.

- **One pass per light.** The renderer draws the scene once per light and adds the results. Every light repeats the draw work of the whole scene, so 1,000 lights mean 1,000 times the geometry.
- **Tiled shading.** The screen is cut into square tiles, commonly 16 by 16 pixels, which gives 120 by 68 = 8,160 tiles at 1,920 by 1,080. Each tile lists the lights whose footprint on the screen touches it.
- **Clustered shading.** The same cut, plus slices along the depth of the view. A pixel reads the list of the cell around its own position and depth.
- **Per-object light lists.** Each object keeps the few lights near it, chosen on the :term[central processing unit]{id=processor} (CPU). A large object, such as a floor, still touches many lights.

A tile is a column that reaches from the camera to the :term[far plane]{id=far-plane}. A tile at the edge of a room can hold a wall at 3 m and a hill at 300 m. A light floating at 150 m, in front of the hill and far from the wall, still lands in the list of that tile, so the wall's pixels test it for nothing. Tiled renderers often store the smallest and largest depth of each tile to trim the column, but one tile that spans a big depth jump defeats the trim.

Cutting the depth too gives a **clustered shading** grid: a view cut into cells in three dimensions, where each cell lists the lights that reach it and each pixel reads the cell it lies in. Researchers published the idea in 2012, and the game Doom (2016) shipped it. Strata uses it with forward shading.

A cell of such a grid is a **froxel**: a small box of the view frustum, bounded by two depth planes and four lines of sight. In this book the froxel and the cluster are the same thing, and the code says "cluster".

| Approach | What a pixel reads | Main cost | Main weakness |
| --- | --- | --- | --- |
| One pass per light | The pass of each light | The scene's geometry drawn once per light | Cost grows with lights times objects |
| Tiled | The list of its screen tile | Building lists per tile | A tile holds lights from every depth |
| Clustered | The list of its screen tile and depth slice | More cells to build and store | Lists must be built every frame |
| Per-object lists | The list of its object | CPU work per object | Big objects collect many lights |

The engine's documents give no reason for choosing forward shading over deferred shading, and this page names none. It states the trade only as the code shows it: the light loop runs inside the material's own shader, so each light can use that surface's clear coat and its source's lobe. [Forward against deferred shading](../gpu/frame-tour.md) is the frame tour's subject.

## The map

Follow a light from its record to the pixel. The renderer has two branches before the cluster step. On a frame where the :term[graphics processing unit]{id=gpu} (GPU) handles the culling of the whole scene, the GPU does the light culling too. That frame takes the GPU-driven path of [GPU-driven rendering](../draw/gpu-driven.md). Otherwise the CPU does the culling while the renderer builds the frame's constants, on the :term[main thread]{id=main-thread}.

```mermaid caption="A light record reaches the cluster lists through the GPU branch or the CPU branch, and the forward shader of each pixel reads the lists." alt="A flow chart. Light records go to a choice. On GPU-driven frames, one pass tests each record against the view and a second packs the visible ones. On other frames the CPU tests, ranks and caps them. Both branches fill the light buffer, which feeds the cluster pass, then the cluster lists, then the forward shader."
flowchart TD
  Record[Light records in the render scene] --> Choice{GPU-driven frame?}
  Choice -- yes --> Cull[LightCull.comp tests each record against the view]
  Cull --> Compact[LightCompact.comp packs the visible lights in record order]
  Choice -- no --> Collect[CollectLights on the CPU: test, rank, cap]
  Compact --> Buffer[Light buffer and view-space bounds]
  Collect --> Buffer
  Buffer --> Clusters[LightClusters.comp: one thread per cluster]
  Clusters --> Lists[Cluster lists]
  Lists --> Forward[Forward.frag: each pixel reads its cluster]
```

The table says who runs what.

| Step | Where | Owns |
| --- | --- | --- |
| `SceneRenderer::CollectLights` (the CPU path) | `Strata/src/Strata/Renderer/SceneRenderer.cpp` | Frame constants, the cluster slice numbers, and on CPU frames the tested, ranked, capped light buffer |
| `RunGPULightCulling` | `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp` | The two culling passes of the GPU path |
| `BuildLightClusters` | `Strata/src/Strata/Renderer/SceneRenderer.cpp` | One dispatch of the cluster pass |
| `Strata/shaders/Scene/Forward.frag.slang` | The material shader | The loop over a cluster's lights |

The second diagram shows the grid itself. The view is cut into screen tiles and depth slices; each cluster gets a box in :term[view space]{id=view-space} and one entry of the cluster buffer. An entry is a count followed by light indices, and its size is one more than the most lights a cluster may hold. That size is the **stride**: 257 for the default 256 lights.

```mermaid caption="The view frustum is cut into screen tiles and depth slices; each cluster owns a box in view space and one entry of the cluster buffer." alt="A flow chart. The view frustum splits into screen tiles and depth slices. Together they make the clusters. Each cluster has a box in view space and an entry in the cluster buffer, which holds a count and then light indices."
flowchart LR
  View[View frustum] --> Tiles[16 x 9 screen tiles]
  View --> Slices[24 exponential depth slices]
  Tiles --> Grid[3,456 clusters]
  Slices --> Grid
  Grid --> Box[A box in view space per cluster]
  Grid --> Entry[A buffer entry per cluster: 1 count plus 256 light indices]
```

## The contract

Callers and shaders rely on these rules, and each has a reason.

1. **A record whose `SpotAngles.z` is zero is not drawn.** Both paths skip it before any test, so a hidden light costs nothing later.
2. **A light's reach is its bounding sphere.** Culling, the cluster test and the relevance ranking all use the sphere (`Bounds`: the center and the radius), never the exact cone of a spot light. One sphere keeps every test to a few multiplications.
3. **The light buffer and the bounds buffer run in parallel.** Entry $i$ of the bounds is the view-space sphere of light $i$, and entry $i$ of a third buffer holds its face when it is a rect light. The cluster shader finds the light of a sphere by its position in the buffer.
4. **Positions are camera-relative.** The shaders work in a space centered on the camera, so every upload subtracts the camera position first.
5. **A cluster lists at most `MaxLightsPerCluster` lights, in buffer order.** The stored count never exceeds the capacity, and the forward shader clamps it again as a guard.
6. **The CPU path caps the buffer at `MaxLights`; the GPU path has no cap.** Each path says which lights it drops, and the statistics report it.

:::rule[Camera-relative space]
Scene shaders work in :term[camera-relative space]{id=camera-relative-rendering}, and what is uploaded relative to the camera is subtracted in double. The reason is precision: a float far from the origin has coarse steps, so subtracting in float would move lights by visible amounts. See [Camera-relative space](../draw/mirrors-camera-relative.md).
:::

## A toy version

:::question
Never read C++ before? The toy uses vectors, functions and calls such as `std::clamp(`. Read [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) first, or skip to its output.
:::

The toy works in two dimensions. It puts five lights on a 1,280 by 720 screen cut into 16 by 9 tiles of 80 pixels. Each light is a circle, and the toy gives the light to every tile that its :term[bounding box]{id=bounding-box} touches. It then asks which lights a pixel loops over, and compares exponential and even depth slices for four depths. Read how the tile numbers come from a division, and how the slice comes from a :term[logarithm]{id=logarithm}.

```cpp sketch="light-many-lights-toy.cpp"
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdio>
#include <initializer_list>
#include <vector>

// A light seen on the screen: its center and its radius, in pixels.
struct ScreenLight
{
	char Name;
	float X;
	float Y;
	float Radius;
};

constexpr int c_TilesX = 16;
constexpr int c_TilesY = 9;
constexpr float c_TileSize = 80.0f;
constexpr int c_Slices = 24;
constexpr float c_Near = 0.1f;
constexpr float c_Far = 1000.0f;

int ClampTile(float pixel, int count)
{
	return std::clamp(static_cast<int>(std::floor(pixel / c_TileSize)), 0, count - 1);
}

int ExponentialSlice(float depth)
{
	const float scale = static_cast<float>(c_Slices) / std::log(c_Far / c_Near);
	return std::clamp(static_cast<int>(std::log(depth / c_Near) * scale), 0, c_Slices - 1);
}

int LinearSlice(float depth)
{
	return std::clamp(static_cast<int>(depth / (c_Far / static_cast<float>(c_Slices))), 0, c_Slices - 1);
}

int main()
{
	const std::vector<ScreenLight> lights = {
		{ 'A', 100.0f, 100.0f, 50.0f }, { 'B', 640.0f, 360.0f, 200.0f }, { 'C', 1200.0f, 700.0f, 30.0f },
		{ 'D', 645.0f, 365.0f, 10.0f }, { 'E', 90.0f, 90.0f, 30.0f }
	};

	// One list of light names per tile: every tile the light's bounding box touches gets the light.
	std::vector<std::vector<char>> tiles(c_TilesX * c_TilesY);
	int entries = 0;
	for (const ScreenLight& light : lights)
	{
		int count = 0;
		for (int y = ClampTile(light.Y - light.Radius, c_TilesY); y <= ClampTile(light.Y + light.Radius, c_TilesY); y++)
		{
			for (int x = ClampTile(light.X - light.Radius, c_TilesX); x <= ClampTile(light.X + light.Radius, c_TilesX); x++)
			{
				tiles[y * c_TilesX + x].push_back(light.Name);
				count++;
			}
		}
		std::printf("Light %c covers %d tiles\n", light.Name, count);
		entries += count;
	}
	std::printf("Tile entries: %d (every light against every tile: %d tests)\n", entries, static_cast<int>(lights.size()) * c_TilesX * c_TilesY);

	size_t busiest = 0;
	for (size_t index = 0; index < tiles.size(); index++)
		if (tiles[index].size() > tiles[busiest].size())
			busiest = index;
	std::printf("Busiest tile (%d,%d) holds %d lights\n", static_cast<int>(busiest) % c_TilesX, static_cast<int>(busiest) / c_TilesX,
		static_cast<int>(tiles[busiest].size()));

	const int pixelX = ClampTile(645.0f, c_TilesX);
	const int pixelY = ClampTile(365.0f, c_TilesY);
	std::printf("Pixel (645,365) is in tile (%d,%d) and loops over:", pixelX, pixelY);
	for (const char name : tiles[pixelY * c_TilesX + pixelX])
		std::printf(" %c", name);
	std::printf("\n");

	for (const float depth : { 0.5f, 5.0f, 50.0f, 480.0f })
		std::printf("Depth %.1f m: exponential slice %d, linear slice %d\n", depth, ExponentialSlice(depth), LinearSlice(depth));

	const size_t clusters = static_cast<size_t>(c_TilesX) * c_TilesY * c_Slices;
	std::printf("Clusters: %zu, buffer: %zu uints\n", clusters, clusters * 257);
	return 0;
}
```

```text output-of="light-many-lights-toy.cpp"
Light A covers 4 tiles
Light B covers 36 tiles
Light C covers 2 tiles
Light D covers 2 tiles
Light E covers 4 tiles
Tile entries: 48 (every light against every tile: 720 tests)
Busiest tile (0,0) holds 2 lights
Pixel (645,365) is in tile (8,4) and loops over: B D
Depth 0.5 m: exponential slice 4, linear slice 0
Depth 5.0 m: exponential slice 10, linear slice 0
Depth 50.0 m: exponential slice 16, linear slice 1
Depth 480.0 m: exponential slice 22, linear slice 11
Clusters: 3456, buffer: 888192 uints
```

1. **Lines 24–27:** the tile number of a pixel is a division, limited to the grid.
2. **Lines 29–33:** the exponential slice multiplies the logarithm of the depth by a scale.
3. **Line 57:** every tile that the bounding box touches receives the light.
4. **Line 80:** the same four depths go through both slice functions.

The output shows three things to carry into the real code. Light B, a big circle, takes 36 of the 48 tile entries, so one large light costs more than the four small ones together. The pixel at (645, 365) loops over two lights instead of five.

At 480 m an exponential slice has number 22, while an even slice has number 11. Even slices put everything near the camera into slice 0, where 5 m and 0.5 m are mixed. They also spend half of their cells on distances beyond 480 m.

The toy omits depth in the lists (its lights have no depth), the sphere-against-box test, the cap, the relevance and the GPU. The real code adds each one, for the reasons below.

## The real code, in the order data flows

### The slices and the first branch

Before any light is tested, the renderer prepares the numbers that cut the depth. The near distance is at least 0.01, and the far distance is the camera's far plane, kept between twice the near distance and a million units, and a million when the plane is infinite. The code then takes the natural logarithm of the ratio, written $\ln$, and spreads the slice count over it. Read the first six lines for those numbers, the two lines after the long comment for rect lights, and the last seven for the GPU branch.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2732-L2757"
const glm::uvec3 grid = m_Specification.LightClusterGrid;
const float sliceNear = std::max(camera.Near, 0.01f);
const float sliceFar = std::isfinite(camera.Far) ? std::clamp(camera.Far, sliceNear * 2.0f, 1.0e6f) : 1.0e6f;
const float scale = static_cast<float>(grid.z) / std::log(sliceFar / sliceNear);
frame.ClusterGrid = glm::uvec4(grid, m_Specification.MaxLightsPerCluster);
frame.ClusterDepth = glm::vec4(scale, -scale * std::log(sliceNear), std::min(camera.Near, 0.0f), c_ClusterDepthEnd);

m_LightCandidates.clear();
m_Lights.clear();
m_LightShapes.clear();
m_LightBounds.clear();
m_LightRecordIndices.clear();
const RenderLights& lights = renderScene.GetLights();
// Both paths alike: whether the scene has a rect light anywhere, not only in view (the GPU-driven path culls on the
// GPU), chooses the forward shaders that shade them. Drawn or not: the forms shade the rest of a pixel's light a little
// differently (the driver compiles the shader differently), so a light that flickers to no intensity, or is turned off
// and on, must not switch every pixel's shader with it; only adding or removing a rect light does.
m_AreaLightsFrame = lights.GetTypeCount(RenderData::c_LightRect) > 0;
m_Stats.AreaLightShading = m_AreaLightsFrame;
m_GPULightsFrame = m_GPUDrivenFrame && m_LightCullPipeline && m_LightCompactPipeline;
if (m_GPULightsFrame)
{
	// The GPU culls every light record into the light buffer (RunGPULightCulling): all lights in view, uncapped.
	m_GPULightRecords = m_SceneGPU->GetLightCapacity();
	frame.LightCounts = glm::uvec4(lights.GetCount() > 0 && m_GPULightRecords > 0 ? 1u : 0u, 1u, 0u, 0u);
	return;
```

1. **Line 2735:** `scale` is the slice count divided by $\ln(\text{far} / \text{near})$, the number of slices per unit of natural logarithm of depth.
2. **Line 2737:** `ClusterDepth` holds the scale, the offset that makes the first slice start at the near distance, and the two ends that catch everything closer or farther.
3. **Lines 2749–2750:** whether the scene holds a rect light anywhere, in view or not, chooses the forward shaders that can shade one. A light that dims to zero therefore leaves the shader of every pixel as it was.
4. **Lines 2751–2757:** on a GPU-driven frame with both light pipelines the function stops here. The GPU tests the records, and every light in view goes through, without a cap. Only `LightCounts` is set.

The slice of a depth $d$ is then the whole part of $\ln(d)$ times the scale plus the offset, which the shader computes in the next section. Take a near distance of 0.1 and a far distance of 1,000: the ratio is 10,000, $\ln(10{,}000) = 9.21$, and the scale is $24 / 9.21 = 2.606$ slices per unit. Slice 6 starts at 1 m, slice 12 at 10 m, slice 18 at 100 m and slice 24 at 1,000 m: every six slices the depth grows ten times.

### The CPU path: test, rank, cap

On a frame that takes the CPU path, `CollectLights` builds a list of candidates. A light whose sphere is outside the view's frustum is counted in `CulledLights` and dropped. The rest receive a **relevance**: a number that says how much a light matters to the view, from the projected size of its sphere.

For a sphere of radius $r$ at distance $d$ from the camera, the relevance is the ratio below. A light whose sphere contains the camera ($d \le r$) gets the largest float, so it ranks first. In an orthographic view distance does not change the projected size, so the relevance is the radius alone.

$$\text{relevance} = \frac{r}{d - r}$$

Here $r$ is the sphere's radius and $d$ is the distance from the camera to its center, both in metres; the ratio has no unit.

Four lights show how it ranks. A has $r = 5$ and $d = 15$: relevance $5 / 10 = 0.5$. B has $r = 1$ and $d = 3$: $1 / 2 = 0.5$, a tie with A. C has $r = 20$ and $d = 100$: $20 / 80 = 0.25$.

D has $r = 3$ and $d = 2$, so it contains the camera and ranks first. The order is D, then A before B (ties go to the lower record index), then C. At the limits, a sphere that grows toward the camera sends the relevance to infinity, and one that shrinks to nothing sends it to zero.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2762-L2810"
const Frustum frustum(camera.Projection * camera.View);
const std::span<const RenderData::LightRecord> records = lights.GetRecords();
for (uint32_t index = 0; index < records.size(); index++)
{
	const RenderData::LightRecord& record = records[index];
	if (record.SpotAngles.z == 0.0f)
		continue;
	LightCandidate candidate;
	candidate.Bounds = record.Bounds;
	if (!frustum.IsSphereVisible(glm::vec3(candidate.Bounds), candidate.Bounds.w))
	{
		m_Stats.CulledLights++;
		continue;
	}
	candidate.Data.PositionRange = record.PositionRange;
	candidate.Data.Color = record.Color;
	candidate.Data.DirectionType = record.DirectionType;
	candidate.Data.SpotAngles = glm::vec4(record.SpotAngles.x, record.SpotAngles.y, 0.0f, record.Source.x);
	// A rect light's face, as LightCompact.comp writes it (zero for point and spot lights).
	candidate.Shape.AxisX = record.AxisX;
	candidate.Shape.AxisY = record.AxisY;
	candidate.Shape.Parameters = glm::vec4(record.Source.y, 4.0f * record.AxisX.w * record.AxisY.w, 0.0f, 0.0f);
	const float distance = glm::length(glm::vec3(candidate.Bounds) - camera.Position);
	if (camera.Orthographic)
		candidate.Relevance = candidate.Bounds.w; // The projected size does not depend on the distance
	else if (distance <= candidate.Bounds.w)
		candidate.Relevance = std::numeric_limits<float>::max();
	else
		candidate.Relevance = candidate.Bounds.w / (distance - candidate.Bounds.w);
	candidate.Order = index;
	m_LightCandidates.push_back(candidate);
}

// The order also decides which lights a full cluster keeps.
std::sort(m_LightCandidates.begin(), m_LightCandidates.end(), [](const LightCandidate& a, const LightCandidate& b)
{
	return a.Relevance != b.Relevance ? a.Relevance > b.Relevance : a.Order < b.Order;
});
if (m_LightCandidates.size() > m_Specification.MaxLights)
{
	m_Stats.DroppedLights = static_cast<uint32_t>(m_LightCandidates.size() - m_Specification.MaxLights);
	m_LightCandidates.resize(m_Specification.MaxLights);
	if (!m_WarnedLightOverflow)
	{
		ST_CORE_WARN("SceneRenderer '{}': more than {} point, spot and rect lights are visible; the least relevant ones are not rendered", m_Specification.DebugName,
			m_Specification.MaxLights);
		m_WarnedLightOverflow = true;
	}
}
```

1. **Line 2771:** the sphere test against the frustum built from the camera's projection and view matrices; a failure counts one light removed and skips the rest.
2. **Lines 2780–2783:** a rect light's face goes with it (zero for point and spot lights), so rect lights are tested, ranked and capped with the others.
3. **Lines 2785–2790:** the three cases of relevance: orthographic, camera inside the sphere, and the ratio.
4. **Lines 2796–2803:** the sort puts the largest relevance first and breaks ties by record order, so the result is the same on every run. When more lights remain than `MaxLights` (4,096), the list is cut and `DroppedLights` records how many: with 5,000 visible lights it reports 904.
5. **Lines 2804–2809:** the warning is logged once for the renderer's life, never every frame.

The sorted order matters beyond the cap. The cluster pass lists lights in buffer order, so a full cluster of the CPU path keeps the most relevant lights without doing anything more.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2814-L2828"
const glm::mat3 viewRotation(camera.View);
const glm::dvec3 cameraPosition(camera.Position);
for (const LightCandidate& candidate : m_LightCandidates)
{
	RenderData::LightData light = candidate.Data;
	light.PositionRange = glm::vec4(glm::vec3(glm::dvec3(glm::vec3(light.PositionRange)) - cameraPosition), light.PositionRange.w);
	m_Lights.push_back(light);
	m_LightShapes.push_back(candidate.Shape);
	if (static_cast<uint32_t>(light.DirectionType.w) >= RenderData::c_LightRect)
		m_Stats.AreaLights++;
	m_LightRecordIndices.push_back(candidate.Order);
	const glm::vec3 relativeCenter(glm::dvec3(glm::vec3(candidate.Bounds)) - cameraPosition);
	m_LightBounds.push_back(RenderData::LightBounds { glm::vec4(viewRotation * relativeCenter, candidate.Bounds.w) });
}
frame.LightCounts = glm::uvec4(static_cast<uint32_t>(m_Lights.size()), 0, 0, 0);
```

1. **Lines 2818–2820:** each position is converted to double, the camera position is subtracted in double, and the result is rounded once to float.
2. **Lines 2821–2823:** the face goes to its own buffer, entry for entry beside the light, and `AreaLights` counts the rect lights.
3. **Line 2826:** the bounds go to view space by the rotation of the :term[view matrix]{id=view-matrix}, which is what the cluster boxes are in.
4. **Line 2828:** the count the shaders loop over.

### The GPU path: test and pack

On a GPU-driven frame, `LightCull.comp` runs one thread per record. It skips a record whose `SpotAngles.z` is zero. Otherwise it computes the sphere's center relative to the camera and tests the six frustum planes: if the center is further outside any plane than the radius, the light is not visible. Each work group counts its visible lights.

`LightCompact.comp` then packs the visible lights. A work group sums the counts of the groups before it. It then runs an inclusive scan of its own visible flags, a running total along the group, as [GPU-driven rendering](../draw/gpu-driven.md) teaches, and writes each visible light at its position. The packing is in record order, so the sums in the lists and the shading do not depend on how the GPU schedules its threads. The pass also writes the camera-relative lights, their view-space bounds and the total.

Two differences from the CPU path follow. There is no cap, so `GetLightCounts(...).Lights` can exceed `MaxLights`. And there is no ranking, since sorting on the GPU is costly. The buffer is in record order, so the cluster pass must find the most relevant lights itself when a cluster is full; that comes after the box test.

### The clusters

The grid has 16 by 9 tiles and 24 slices by default, so 3,456 clusters. A pixel finds its cluster from where it is on the screen and how deep it is. The shader below uses a pair of **exponential depth slices**: slices whose depth ranges grow by a constant ratio, which is slices equal in the logarithm of the view depth.

```slang src="Strata/shaders/Include/Clusters.slang#L13-L42"
uint GetClusterSlice(float viewDepth)
{
	float slice = log(max(viewDepth, 1e-6)) * u_Frame.ClusterDepth.x + u_Frame.ClusterDepth.y;
	return uint(clamp(slice, 0.0, float(u_Frame.ClusterGrid.z - 1u)));
}

// Cluster containing a pixel (framebuffer coordinates) at a view depth.
uint GetClusterIndex(float2 pixel, float viewDepth)
{
	uint2 tile = min(uint2(pixel * u_Frame.ViewportSize.zw * float2(u_Frame.ClusterGrid.xy)), u_Frame.ClusterGrid.xy - 1u);
	return (GetClusterSlice(viewDepth) * u_Frame.ClusterGrid.y + tile.y) * u_Frame.ClusterGrid.x + tile.x;
}

uint GetClusterStride()
{
	return u_Frame.ClusterGrid.w + 1u;
}

// How much a light matters to the view, as SceneRenderer::CollectLights ranks lights (from its view-space bounding sphere):
// lights whose region contains the camera first, then by the projected size of that region (its radius alone in
// orthographic views). A full light cluster keeps the most relevant lights.
float GetLightRelevance(float4 viewBounds)
{
	if (u_Frame.CameraForward.w > 0.5)
		return viewBounds.w;
	float distanceToCenter = length(viewBounds.xyz);
	if (distanceToCenter <= viewBounds.w)
		return 3.402823466e38;
	return viewBounds.w / (distanceToCenter - viewBounds.w);
}
```

1. **Line 15:** the slice is the logarithm of the depth times the scale plus the offset, the same numbers the CPU wrote into `ClusterDepth`; `max(..., 1e-6)` keeps the logarithm defined.
2. **Line 22:** the tile is the pixel's position as a fraction of the viewport times the grid size, so a 16 by 9 grid cuts any resolution the same way.
3. **Line 23:** the index counts tiles along a row, rows in a slice and slices.
4. **Line 28:** the stride is the capacity plus the count's own slot.
5. **Lines 36–41:** the same relevance as on the CPU, evaluated in view space, since the GPU path has no sorted buffer.

A worked pixel shows the whole chain. Take a 1,280 by 720 viewport, the pixel at (900, 500) and a view depth of 5 m, with a near of 0.1 and a far of 1,000. The tile is $\lfloor 900 / 1280 \times 16 \rfloor = 11$ along and $\lfloor 500 / 720 \times 9 \rfloor = 6$ down. The slice is $\lfloor \ln(5) \times 2.606 + 6.0 \rfloor$, where $\ln(5) = 1.609$ gives $4.19$, plus the offset of $-2.606 \times \ln(0.1) = 6.0$, so $10.19$ and slice 10. The cluster index is $(10 \times 9 + 6) \times 16 + 11 = 1547$, and its entry starts at $1547 \times 257 = 397{,}579$ in the buffer.

Here $\lfloor x \rfloor$ is $x$ rounded down. At the limits, a depth below the near distance gives a negative slice that the `clamp` turns into slice 0, and one beyond the far distance lands in the last slice.

The cluster pass builds the lists. One thread owns one cluster, so a dispatch needs the cluster count divided by 64, rounded up, work groups of 64 threads. Each thread first builds the cluster's box in view space.

```slang src="Strata/shaders/Scene/LightClusters.comp.slang#L50-L69"
if (valid)
{
	uint x = cluster % grid.x;
	uint y = (cluster / grid.x) % grid.y;
	uint slice = cluster / (grid.x * grid.y);
	// Tile row 0 is at the top of the screen (NDC +Y).
	float2 ndcMin = float2(float(x) / float(grid.x) * 2.0 - 1.0, 1.0 - float(y + 1u) / float(grid.y) * 2.0);
	float2 ndcMax = float2(float(x + 1u) / float(grid.x) * 2.0 - 1.0, 1.0 - float(y) / float(grid.y) * 2.0);
	float depths[2] = { GetClusterSliceStart(slice), GetClusterSliceStart(slice + 1u) };

	boxMin = float3(3.0e38);
	boxMax = float3(-3.0e38);
	for (int corner = 0; corner < 8; corner++)
	{
		float2 ndc = float2((corner & 1) != 0 ? ndcMax.x : ndcMin.x, (corner & 2) != 0 ? ndcMax.y : ndcMin.y);
		float3 point = ViewPointAtDepth(ndc, depths[corner >> 2]);
		boxMin = min(boxMin, point);
		boxMax = max(boxMax, point);
	}
}
```

1. **Lines 56–57:** the cluster's corners in screen coordinates, from the tile numbers; row 0 is at the top of the screen, where the y of :term[normalized device coordinates]{id=normalized-device-coordinates} (NDC) is largest.
2. **Line 58:** the two depths that bound the slice, from `GetClusterSliceStart`.
3. **Lines 62–67:** each of the eight corners is turned into a view-space point on the ray at that depth, and the box is the smallest one holding all eight.

The pass then tests every light against the box. A sphere with center $c$ and radius $r$ touches a box with limits $b_\text{min}$ and $b_\text{max}$ when the squared distance from $c$ to the nearest point of the box is at most $r^2$. Clamping the center to the box gives that nearest point.

$$\text{offset} = c - \operatorname{clamp}(c, b_\text{min}, b_\text{max}), \qquad \text{touches} \iff \text{offset} \cdot \text{offset} \le r^2$$

Here $\operatorname{clamp}$ limits each coordinate to the box, $\cdot$ is the :term[dot product]{id=dot-product} (the sum of the products of matching coordinates), and the radius is in metres. Take a box with $x$ from 2 to 4, $y$ from $-1$ to 1 and $z$ from $-8$ to $-6$, and a sphere at $(0, 0, -5)$. The nearest point is $(2, 0, -6)$ and the offset is $(-2, 0, 1)$, whose dot product with itself is 5. A radius of 3 gives $r^2 = 9$ and the light reaches the box; a radius of 2 gives 4, and it does not. When the center is inside the box the offset is zero and the test always passes.

The threads of one group test the same lights, so the shader loads the light bounds into group-shared memory, 64 at a time. The 64 threads load a batch together, and a barrier waits until all are done. Each thread then tests its own cluster against the batch. A second barrier keeps the next load from replacing a batch still in use. Compare [Compute shaders](../gpu/compute.md) for shared memory and barriers.

```slang src="Strata/shaders/Scene/LightClusters.comp.slang#L71-L101"
uint capacity = u_Frame.ClusterGrid.w;
uint base = cluster * (capacity + 1u);
uint lightCount = u_Frame.LightCounts.y != 0u ? u_LightCount[0] : u_Frame.LightCounts.x;

// Every light reaching the cluster, the first `capacity` of them listed.
uint count = 0u;
uint reaching = 0u;
for (uint first = 0u; first < lightCount; first += 64u)
{
	uint light = first + st_LocalInvocationIndex;
	s_LightBounds[st_LocalInvocationIndex] = light < lightCount ? u_LightBounds[light] : float4(0.0, 0.0, 0.0, -1.0);
	GroupMemoryBarrierWithGroupSync();

	if (valid)
	{
		uint batch = min(64u, lightCount - first);
		for (uint index = 0u; index < batch; index++)
		{
			if (SphereIntersectsBox(s_LightBounds[index], boxMin, boxMax))
			{
				if (count < capacity)
				{
					o_ClusterLights[base + 1u + count] = first + index;
					count++;
				}
				reaching++;
			}
		}
	}
	GroupMemoryBarrierWithGroupSync();
}
```

1. **Lines 71–73:** the capacity and the entry's start. The light count comes from the GPU culling's total on the GPU path and from the frame constants on the CPU path.
2. **Lines 80–82:** each thread loads one light's bounds, and the barrier makes the batch visible to the group.
3. **Line 89:** the sphere against the box test of the formula above.
4. **Lines 91–94:** the light index is written while there is room, so the entry receives its lights in buffer order.
5. **Line 96:** `reaching` counts every light that touches the cluster, listed or not, so a full cluster is known.

:::note[Advanced: which lights a full cluster keeps on the GPU path]
On the CPU path the buffer is sorted, so the first 256 lights that reach a cluster are the most relevant. On the GPU path the buffer is in record order, so the first 256 could be the least relevant. The shader therefore finds the relevance of the 256th-best light and keeps the lights at least that relevant. It does this with a search over the bits of an **ordered float**: a float whose bit pattern is changed so that comparing the patterns as :term[unsigned integers]{id=unsigned-integer} orders the floats, `EncodeOrderedFloat` in `Strata/shaders/Include/OrderedFloat.slang`.

The search sets the threshold one bit at a time, from the top bit down. For each bit it tries the threshold with that bit set. It counts the lights that reach the cluster with an ordered relevance at least that large, and keeps the bit if the count is at least the capacity.

With four-bit numbers and a capacity of 4, let six lights reach a cluster with relevances 3, 12, 5, 15, 12 and 9. Trying 8: four lights (15, 12, 12, 9) are at least 8, so the bit stays. Trying 12 on top of it gives three lights, so the bit goes; 10 gives three, so no; 9 gives four, so yes. The threshold is 9, the fourth-largest relevance.

The shader then counts the lights above the threshold, three here. It completes the remaining room with lights at the threshold in buffer order, one. Lights 3 and 5 are dropped. All 32 bits cost 32 passes over the lights, but only clusters that overflow pay, and a work group runs the passes only when one of its clusters overflowed.

```slang src="Strata/shaders/Scene/LightClusters.comp.slang#L115-L138"
uint threshold = 0u;
for (int bit = 31; bit >= 0; bit--)
{
	uint candidate = threshold | (1u << uint(bit));
	uint atLeast = 0u;
	for (uint first = 0u; first < lightCount; first += 64u)
	{
		uint light = first + st_LocalInvocationIndex;
		s_LightBounds[st_LocalInvocationIndex] = light < lightCount ? u_LightBounds[light] : float4(0.0, 0.0, 0.0, -1.0);
		GroupMemoryBarrierWithGroupSync();
		if (overflow)
		{
			uint batch = min(64u, lightCount - first);
			for (uint index = 0u; index < batch; index++)
			{
				if (SphereIntersectsBox(s_LightBounds[index], boxMin, boxMax) && EncodeOrderedFloat(GetLightRelevance(s_LightBounds[index])) >= candidate)
					atLeast++;
			}
		}
		GroupMemoryBarrierWithGroupSync();
	}
	if (overflow && atLeast >= capacity)
		threshold = candidate;
}
```

1. **Line 115:** the threshold starts at zero.
2. **Lines 116–118:** the bits are tried from 31 to 0, each as `candidate`.
3. **Lines 130–131:** a light counts when it reaches the cluster and its ordered relevance is at least the candidate.
4. **Lines 136–137:** the bit stays when at least `capacity` lights qualify.

:::

You can see the lists. The Clusters debug view colors each pixel by how many lights its cluster lists, in bands: none, 1, 2 to 3, 4 to 7, and so on up to a full cluster of 256. The forward loop walks that list for every pixel, so the crowded bands show where many lights cost the most. Its statistics read shares of the capacity, not counts. An agent switches the viewport to it with one command.

```json
{ "command": "viewport.setSettings", "parameters": { "debugView": "clusters" } }
```

The same name goes in the `debugView` of `viewport.capture`. [Measuring light](measuring-light.md) teaches the other views and their legends.

### The forward loop

The forward shader reads the lists. The sun comes first, and its shadow comes from a screen-space mask; the loop below visits every light in the cluster. Watch where a rect light leaves the loop for its own branch.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L320-L331"
if (u_Frame.LightCounts.x > 0u)
{
	uint clusterBase = GetClusterIndex(st_FragCoord.xy, viewDepth) * GetClusterStride();
	uint clusterLights = min(u_ClusterLights[clusterBase], u_Frame.ClusterGrid.w);
	for (uint index = 0u; index < clusterLights; index++)
	{
		uint lightIndex = u_ClusterLights[clusterBase + 1u + index];
		LightData light = u_Lights[lightIndex];
#ifdef ST_AREA_LIGHTS
		// Rect lights take their own branch, the same for every pixel of the light: point and spot lights never enter it.
		// Their face rides in u_LightShapes beside the light.
		if (uint(light.DirectionType.w) >= ST_LIGHT_RECT)
```

1. **Lines 322–323:** the cluster index of the pixel, times the stride, is the start of its entry, and the count is clamped to the capacity as a guard.
2. **Lines 326–327:** the light's index is kept, since it also finds a rect light's face in the buffer of faces.
3. **Lines 328–331:** the rect branch exists only in the shaders chosen for a scene with rect lights, and every pixel of one light takes the same branch.

The rect branch shades the face and its shadow, then continues with the next light; [Area lights](../light/area-lights.md) teaches it. The rest of the loop handles point and spot lights.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L369-L394"
float3 toLight = light.PositionRange.xyz - surface.Position;
float distanceSquared = dot(toLight, toLight);
float range = light.PositionRange.w;
if (distanceSquared >= range * range)
	continue;

float attenuation = DistanceAttenuation(distanceSquared, light.Color.w);
if (uint(light.DirectionType.w) == ST_LIGHT_SPOT)
	attenuation *= SpotAttenuation(-toLight, light.DirectionType.xyz, light.SpotAngles.x, light.SpotAngles.y);
if (attenuation <= 0.0)
	continue;
float3 lightDirection = normalize(toLight);
// A light behind the surface adds nothing without a clear coat (EvaluateLightWeighted returns 0 for N.L <= 0, also
// for glass): skipped before its shadow's taps.
if (coat.Strength <= 0.0 && dot(surface.Normal, lightDirection) <= 0.0)
	continue;
// A shadowed light's slot plus one (SceneRenderer's local shadows).
uint shadowSlot = uint(light.SpotAngles.z + 0.5);
if (shadowSlot > 0u)
{
	float3 geometricNormal = normalize(v_Normal) * (st_FrontFacing ? 1.0 : -1.0);
	attenuation *= SampleLocalShadow(shadowSlot - 1u, surface.Position, geometricNormal, st_FragCoord.xy);
}
// The highlight takes the bulb's or flame's angular size (SpotAngles.w: its radius; 0, a point, skips it).
float sourceAlpha2 = GetSourceLobeAlpha2(light.SpotAngles.w, distanceSquared);
color += LightSurface(surface, coat, diffuseWeight, lightDirection, light.Color.rgb * attenuation, sourceAlpha2);
```

1. **Lines 372–373:** outside the light's range the light adds nothing, so the loop skips it before any other work.
2. **Lines 375–379:** the distance attenuation, times the spot cone's attenuation for a spot light; no attenuation, no work.
3. **Lines 380–384:** without a clear coat, a light behind the surface adds nothing, so the loop skips it before the shadow's samples.
4. **Lines 386–391:** a shadowed light stores its shadow slot plus one; zero means no shadow, and a slot multiplies the attenuation by the shadow sample.
5. **Lines 393–394:** the source's lobe widens the highlight, and `LightSurface` shades the surface with the light's color already multiplied by its attenuation.

:::why
Forward shading with clusters keeps the material in charge of each light, so the clear coat of a surface and the size of a light's source reach the loop as ordinary arguments. The price is that every covered pixel runs the loop, with its own list of lights.
:::

:::example
One pixel of a thousand-light scene. Take the pixel at (900, 500) at a depth of 5 m from the worked chain above: it reads cluster 1547. Suppose 1,000 point lights of radius 1.5 m stand on a grid of 2.0 m, 40 by 25, on the floor. With a 60-degree vertical :term[field of view]{id=field-of-view}, the cluster at 4.6 to 6.8 m deep is about 0.6 m wide and tall at that range. Perhaps 4 spheres touch its box and the loop runs 4 times, not 1,000.

The cluster pass tested 3,456 clusters against 1,000 lights, 3,456,000 sphere tests, spread over 3,456 threads; the 2,073,600 pixels of the frame then loop 4 times each, 8,294,400 light evaluations instead of 2,073,600,000.
:::

The picture below is such a scene in Strata. It uses the Lighting debug view of [Measuring light](measuring-light.md), which shows only the light that reaches each surface.

::figure{id=thousand-lights}

### The statistics

The renderer reports what it did. `SceneRendererStats::CulledLights` counts the point, spot and rect lights outside the view and `DroppedLights` those cut by `MaxLights`, both from the CPU path. On the GPU path `SceneRendererGPUStats` carries `Lights`, the visible lights, and `CulledLights`. Nothing is cut there, so the test reads zero dropped lights. The tests read them with `Tests::GetLightCounts`, and `editor.perf` reports `lights` and `droppedLights` in its `renderStats`.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Deferred shading, one light pass over a G-buffer | Many engines of the 2000s | Lights that cost only where they cover pixels, however many | The material's own shader per light, and cheap transparency |
| Tiled deferred or forward+ with 2D tiles | Engines that want a small light build | A smaller build pass: 8,160 tiles at 1,080p against 3,456 clusters of a fixed grid | Depth precision: a tile holds lights from every depth |
| Per-object light lists | Older forward engines | No grid, no build pass | Cost per object on the CPU, and big objects with long lists |
| One cluster grid with a fixed cap and no ranking | Simple clustered renderers | A smaller shader, no search | Lights that vanish by chance when a cluster is full |

Sources are in Further reading. The first row weighs a G-buffer against forward shading; that comparison belongs to [the frame tour](../gpu/frame-tour.md).

## How it is tested

The suite `GPU.SceneRenderer.Lighting`, in `StrataTests/src/Renderer/GPUSceneLightingTests.cpp`, runs on a GPU (label `gpu`) and has three cases for this page.

- `Clustered lighting matches shading every pixel with every light` renders 500 point lights and four spot lights twice, once with the default grid and once with a grid of one cluster that holds every light, and compares the pictures. The CPU path renders the same scene too.
- `Lights outside the view are culled and the most relevant lights are kept when there are too many` places two lights in view and three out of it, checks the counts, then caps the renderer at one light, which must be the near one. It repeats with one cluster of capacity one on both paths.
- `The GPU-driven path draws every light in view, beyond the CPU path's MaxLights` renders 10,000 lights on both paths. The GPU path counts 10,000, the CPU path 4,096 with 5,904 dropped, and the GPU image is brighter.

Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Lighting`, or `ctest --preset windows-debug` with the label `gpu` enabled.

## Changing it safely

- **Change both paths together.** The CPU path ranks by one formula and the shader ranks by the same one (`GetLightRelevance`). A change to one that leaves the other behind gives a picture that depends on the path.
- **Keep the stride in sync.** The cluster buffer is sized at creation as clusters times capacity plus one, in `uint`s, and the shaders read the capacity from the frame constants. A new field in the entry changes the buffer size, `GetClusterStride` and the cluster pass together.
- **Mind the limits.** The renderer clamps the grid to 64 along each axis, the capacity to 1,024 and the whole buffer to 256 MiB, with a warning when the capacity must shrink.
- **Bump what the picture depends on.** Lights, their order and the cap decide the image, so keep the three tests above passing.
- **Keep positions camera-relative.** Anything uploaded for the shaders follows the rule in the contract.

## Summary

- A clustered grid cuts the view in depth as well as on the screen, so a pixel loops over the lights near it instead of every light or the lights of a whole tile.
- The CPU path tests by :term[bounding sphere]{id=bounding-sphere}, ranks by relevance and caps at 4,096 with one warning; the GPU path tests and packs in record order and has no cap.
- A pixel's cluster comes from its tile and its logarithmic depth slice, and its entry starts at the index times the stride of 257.
- A full cluster on the GPU path keeps the most relevant lights by a bit-by-bit search over ordered float bits, with ties kept in buffer order.
- The grid costs time in the cluster pass and in the opaque stage, which the exercises measure with `editor.perf`.

## Check yourself

1. A scene has 1,000 lights and a 1,920 by 1,080 view. Which statement about tiled shading with 16 by 16 pixel tiles is right?
   - (a) It lists lights per tile, so a tile that shows a near wall and a far hill collects the lights of both depths.
   - (b) It needs no build pass.
   - (c) It gives each pixel exactly the lights that reach it.
   - (d) It draws the scene once per light.

   :::answer{tests="clustered-idea"}
   (a) is right: a tile is a column through the whole depth. (b) is wrong, since tiles need lists built every frame. (c) is wrong: a tile lists every light whose footprint touches it, also where the light misses the pixel. (d) describes one pass per light, a different approach.
   :::

2. A cluster is reached by 300 lights and holds 256. On the CPU path, which lights stay?
   - (a) Random ones.
   - (b) The first 256 in record order.
   - (c) The 256 most relevant, since the buffer is sorted.
   - (d) The 256 nearest the camera.

   :::answer{tests="keep-relevant"}
   (c). The CPU path sorts by relevance and the cluster pass lists in buffer order. (a) is a mistake the design avoids, (b) describes the GPU path before its search, and (d) ignores size: relevance is the projected size.
   :::

3. 5,000 point lights are in view. What do `DroppedLights` and the warning report on the CPU path, and on the GPU path?

   :::answer{tests="two-paths"}
   The CPU path keeps 4,096, reports 904 dropped and logs one warning. The GPU path draws all 5,000, drops none and logs nothing, since it has no cap. A cluster can still fill, at 256 lights.
   :::

4. Take the default grid, a near of 0.1 and a far of 1,000. Which cluster does the pixel at (320, 180) of a 1,280 by 720 viewport read at a view depth of 50 m, and where does its entry start?

   :::answer{tests="cluster-index"}
   The tile is 4 along ($320 / 1280 \times 16 = 4$) and 2 down ($180 / 720 \times 9 = 2.25$, rounded down). The slice is $\lfloor \ln(50) \times 2.606 + 6.0 \rfloor = \lfloor 16.2 \rfloor = 16$. The index is $(16 \times 9 + 2) \times 16 + 4 = 2340$ and the entry starts at $2340 \times 257 = 601{,}380$.
   :::

5. Four lights reach a cluster of capacity 2 on the GPU path, with four-bit relevances 6, 14, 9 and 14, in that buffer order. Which are kept?

   :::answer{tests="keep-relevant"}
   The second-largest relevance is 14, so the threshold is 14. No light is above it, so there is room for two at the threshold, taken in buffer order: the second and the fourth lights. The lights with 6 and 9 are dropped.
   :::

6. You double the grid on every axis, from 16 by 9 by 24 to 32 by 18 by 48. How many clusters does the cluster pass handle, and how big is the buffer at 257 numbers of four :term[bytes]{id=byte} each?

   :::answer{tests="measure-grid"}
   Each axis doubles, so the count grows eight times, from 3,456 to 27,648. The buffer holds $27{,}648 \times 257 = 7{,}105{,}536$ numbers, which is 28,422,144 bytes, about 28 MB. Each cluster thread still tests every visible light, so the pass costs eight times more; measure it with `editor.perf` before keeping the change.
   :::

## Exercises

1. **Basic.** For one pixel of the scene, find with a search which cluster it reads, and which function builds the list it loops over. Name the files and functions.

   :::answer[Worked solution]{tests="cluster-index"}
   Search `Forward.frag.slang` for `GetClusterIndex`. The forward loop at line 322 calls it with the fragment's position and its view depth. Its definition is in `Strata/shaders/Include/Clusters.slang` (`GetClusterIndex`, using `GetClusterSlice`). The list comes from `Strata/shaders/Scene/LightClusters.comp.slang`, dispatched by `SceneRenderer::BuildLightClusters` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, which the frame records after the light culling, on the GPU path after `RunGPULightCulling`.
   :::

2. **Medium.** Change the grid to 32 by 18 by 32 and measure what it costs. Measure once on the GPU-driven path and once on the CPU path.

   :::answer[Worked solution]{tests="measure-grid"}
   1. In `Strata/src/Strata/Renderer/SceneRenderer.h` change `LightClusterGrid` to `{ 32, 18, 32 }`. The buffer grows from 3,456 to 18,432 clusters, about 19 MB, far below the 256 MiB limit.
   2. Build the editor, open a scene with many lights, and run `editor.perf`. Read the `stages` entries `Cull` and `Opaque`, whose full names begin with `GPU` and a dot; on a GPU-driven frame the light passes are timed in the `Cull` stage.
   3. To force the CPU path set `GPUDriven` in the same specification to `GPUDrivenMode::Off`, rebuild, and read the `Setup` stage, where the light passes are then timed.
   4. Compare against the 16 by 9 by 24 numbers. The cluster pass has 5.3 times the threads and each tests all lights, so its time grows; the opaque stage may shrink where finer boxes shorten the lists. Record the numbers of your machine; the engine documents give none.
   :::

3. **Hard.** The toy gives a light to every tile its bounding box touches. Write a program that tests the circle against each tile as the cluster shader tests a sphere, and count the entries.

   :::answer[Worked solution]{tests="clustered-idea" solution="sketches/light-many-lights-circle.cpp"}
   The program clamps the circle's center to the tile and compares the squared distance with the squared radius, as in the shader.

   ```cpp sketch="light-many-lights-circle.cpp"
   #include <algorithm>
   #include <cstdio>
   #include <vector>

   struct ScreenLight
   {
   	char Name;
   	float X;
   	float Y;
   	float Radius;
   };

   constexpr int c_TilesX = 16;
   constexpr int c_TilesY = 9;
   constexpr float c_TileSize = 80.0f;

   // The same test as the cluster shader's: the distance from the circle's center to the nearest point of the tile.
   bool CircleTouchesTile(const ScreenLight& light, int tileX, int tileY)
   {
   	const float minX = static_cast<float>(tileX) * c_TileSize;
   	const float minY = static_cast<float>(tileY) * c_TileSize;
   	const float dx = light.X - std::clamp(light.X, minX, minX + c_TileSize);
   	const float dy = light.Y - std::clamp(light.Y, minY, minY + c_TileSize);
   	return dx * dx + dy * dy <= light.Radius * light.Radius;
   }

   int main()
   {
   	const std::vector<ScreenLight> lights = {
   		{ 'A', 100.0f, 100.0f, 50.0f }, { 'B', 640.0f, 360.0f, 200.0f }, { 'C', 1200.0f, 700.0f, 30.0f },
   		{ 'D', 645.0f, 365.0f, 10.0f }, { 'E', 90.0f, 90.0f, 30.0f }
   	};

   	int entries = 0;
   	for (const ScreenLight& light : lights)
   	{
   		int count = 0;
   		for (int y = 0; y < c_TilesY; y++)
   			for (int x = 0; x < c_TilesX; x++)
   				if (CircleTouchesTile(light, x, y))
   					count++;
   		std::printf("Light %c touches %d tiles\n", light.Name, count);
   		entries += count;
   	}
   	std::printf("Tile entries: %d\n", entries);
   	return 0;
   }
   ```

   ```text output-of="light-many-lights-circle.cpp"
   Light A touches 4 tiles
   Light B touches 34 tiles
   Light C touches 2 tiles
   Light D touches 2 tiles
   Light E touches 4 tiles
   Tile entries: 46
   ```

   1. **Lines 22–23:** the center is clamped to the tile, so the offset is the distance to the nearest point.
   2. **Line 24:** the squared distance is compared with the squared radius, with no square root.
   3. **Line 40:** the test runs for every tile of the grid, which is affordable for a toy.

   The circle test gives fewer entries than the box test, because the corners of a bounding box lie outside the circle. The same holds for clusters, which is why the shader tests spheres and not the boxes of spheres.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `CollectLights`, `BuildLightClusters`, the slice constants.
- `Strata/src/Strata/Renderer/SceneRendererGPUDriven.cpp`: `RunGPULightCulling`.
- `Strata/shaders/Scene/LightCull.comp.slang`, `LightCompact.comp.slang`, `LightClusters.comp.slang`, `Forward.frag.slang`.
- `Strata/shaders/Include/Clusters.slang` and `OrderedFloat.slang`.
- Settings: `MaxLights`, `LightClusterGrid` and `MaxLightsPerCluster` of `SceneRendererSpecification` (see [Renderer settings](../reference/renderer.md)).
- Tests: `GPU.SceneRenderer.Lighting` in `StrataTests/src/Renderer/GPUSceneLightingTests.cpp`.
- Command: `editor.perf`, with `renderStats`.

## Further reading

- Ola Olsson, Markus Billeter and Ulf Assarsson, "Clustered Deferred and Forward Shading" (2012): the paper that introduced clusters (advanced).
- Tiago Sousa and Jean Geoffroy, "The Devil is in the Details: idTech 666" (SIGGRAPH 2016): how Doom ships its light lists (advanced).
- Ola Olsson and Ulf Assarsson, "Tiled Shading" (2011): the 2D tile approach (intermediate).
