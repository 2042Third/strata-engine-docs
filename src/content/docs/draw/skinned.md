---
id: draw/skinned
title: "Skinned meshes in the renderer"
description: "How the renderer draws meshes a skeleton bends: palettes only for changed poses, bounds that follow the pose, and no cost for scenes without skins."
kind: internals
size: M
tracks: [E]
needs: [draw/gpu-driven]
time: 55
learn:
  - id: skinning-place
    text: explain where skinning can run, and why Strata blends four joints in the vertex shader from palettes that the CPU computes
  - id: posed-bounds
    text: compute the posed bounds of a skinned mesh from its joint boxes and palette entries
  - id: palette-skip
    text: trace when the renderer recomputes the palettes of a skinned proxy and when it skips them
  - id: same-variant
    text: explain why every pass of a skinned mesh uses the same ST_SKINNED variant, and why scenes without skins pay nothing
since: 0.3.0
status: final
---

A character is one mesh that bends. Its vertices rest where an artist modelled them, in the **bind pose**, and a skeleton moves them every frame. The :term[renderer's]{id=renderer} job here is to draw such meshes. It hands the :term[shaders]{id=shader} the matrices that move the vertices and draws and shadows the mesh against bounds that follow the pose. It does all of this at no cost to a scene without skins.

The page takes the pose's joint matrices as given. How they are made, and the model that turns them into a moved vertex, belong to [Skinning](../animation/skinning.md). Skeletons, the animation system that publishes poses and the animators that pose only what is seen belong to other pages of the animation part.

## The problem and how engines solve it

Every vertex of a character has to move with the skeleton, and a character has thousands of vertices. Each vertex follows up to four joints, each with a weight. The new position is a blend of what each joint would do to it. Where that blend runs is the first choice, and there are three common answers.

The first answer is the processor: the central processing unit (CPU) moves every vertex and uploads the result. A character of 5,152 vertices, a size the speed tests use, takes 5,152 blends per frame, so 1,000 such characters take 5.2 million, plus a fresh upload of all their vertices. Nothing on the :term[graphics processing unit]{id=gpu} (GPU) has to know about skeletons, but the cost grows with the vertex count and the CPU is the scarcer resource.

The second answer is the vertex shader. The CPU computes one matrix per joint, the **palette**, and uploads only those: a joint's matrix is three rows of four floats, 48 :term[bytes]{id=byte}. The vertex shader reads the four palette entries a vertex names and blends them. The 20 joints of the same character cost 960 bytes instead of 5,152 vertices. The cost is that every pass that draws the character blends again: the :term[depth prepass]{id=depth-prepass}, the forward pass and each shadow pass.

The third answer is a compute pre-pass: a compute shader skins every vertex once per frame into a buffer, and every pass then draws that buffer like a static mesh. Passes get cheaper, but the buffer costs memory per character and the pre-pass costs time even for characters nobody sees. It pays when many passes draw many vertices.

A different question is how the blend is formed. Blending matrices can squeeze a twisting limb into a thin neck. **Dual quaternion** skinning blends rotations in another form that avoids it. [Skinning](../animation/skinning.md) teaches the model of bending and skins a vertex by hand.

Strata chooses the second answer with matrix blending. The vertex shader blends four joints. The CPU computes palettes only for poses that changed, spread over the job system. The choice costs a repeated blend in each pass and gains a small upload, a vertex buffer that never changes and no extra pass. Compute skinning is later work, listed in `Docs/Roadmap.md`, and Strata has no code for dual :term[quaternions]{id=quaternion}.

A second problem hides behind the first. A renderer decides what to draw from bounds, boxes around each mesh, and the bounds of a mesh in its bind pose are wrong once it moves. [Bounds and culling](../draw/bounds-culling.md) shows what a wrong box costs: the mesh vanishes. Strata computes **posed bounds**, the bounds of a skinned mesh computed from its pose rather than from its bind pose.

## The map

```mermaid caption="The path of a pose through the renderer: the animation system publishes it, the render scene turns it into palettes and bounds, and the passes draw with them." alt="A flow diagram. The animation system publishes poses through a scene service. The render scene computes palettes and posed bounds on the job system. Posed bounds feed the culling, palettes feed the joint buffer of the vertex shaders, and the renderers report which animators they drew back to the animation system."
flowchart LR
  A[Animation system] -->|"ISkinningPoses: poses and versions"| B[RenderScene::UpdateSkinnedPoses]
  B -->|"palettes: job system, batches of 16"| C[(Joint buffer t15)]
  B -->|"posed bounds"| D[Culling: CPU and GPU]
  D --> E[Instances with c_InstanceSkinned]
  E --> F[ST_SKINNED vertex shaders]
  C --> F
  D -->|"ReportVisibleAnimators"| A
```

The animation system lives in the Animation module and the renderer never includes it. They meet in one scene service, `ISkinningPoses`, which publishes each animator's pose and a version number that changes when any pose changes ([scene services](../world/systems.md)). The :term[main thread]{id=main-thread} owns `RenderScene::UpdateSkinnedPoses`; it hands the arithmetic to the job system and waits for it.

## The contract

A proxy is the :term[render scene's]{id=render-scene} record of one mesh renderer. A **skin proxy** is a proxy whose entity has a `SkinComponent` and whose mesh has a skin binding. The binding lists the skin's joints with their inverse bind matrices and the bind-pose box of each joint's vertices. A joint's inverse bind matrix takes a vertex from the mesh's space into that joint's own space as it stood in the bind pose. The scene's `ISkinningPoses` service poses it.

What callers may assume:

- A posed proxy owns a range of the palette: one entry per joint of its skin, found through the instance's first-joint field.
- Each entry is `AnimatorToProxy * pose joint * inverse bind matrix`: the pose's joint, taken from the animator's space into the proxy's own space. Read from the right: into the joint's bind space, out by the joint's new pose, then into the proxy's space.
- The proxy's bounds are posed bounds as soon as it is posed, and bind-pose bounds before and after.

What callers must do:

- Give each influence of a skinned vertex a joint of the skin, also one with weight 0, because the shader reads all four entries.
- Write palettes only through `RenderScene`, which records the changed joints so renderers upload only those.

:::rule[Work for skinned meshes costs scenes without skins nothing]
Most scenes have no skins, so a check that every proxy pays would be a tax on every game. `RenderScene::HasSkinProxies` gates each skinning check, and meshes without skins keep their pipelines, data and uploads.
:::

:::rule[Skinned proxies take part in culling with posed bounds, never bind-pose bounds]
A swung limb leaves its bind-pose box. A renderer that tests visibility with the old box drops the limb when that box is off screen, and drops the limb's shadow when the box cannot reach the view.
:::

:::rule[Every pass of a skinned mesh draws with the skinned variant]
The forward pass tests depth with an equal comparison against the depth prepass, so both passes must produce the same position to the last bit. The same blend, in the same shader variant, gives the same bits.
:::

## A toy version

The toy blends four palette entries by their weights into one matrix, as the shader's `BlendJoints` does, and skins a vertex with it. The palette holds three entries: one leaves a vertex alone, one moves it 2 along x and one moves it 4 along y.

:::question
The code of this page uses functions, loops, classes and calls like `glm::translate(`. If these are new, read [Programming 2](../basics/programming-2.md) and [Programming 3](../basics/programming-3.md) first.
:::

Look at the first output line: weights of one half for entries 0 and 1 put the vertex halfway between where each alone would put it.

```cpp sketch="draw-skinned-toy.cpp"
// Blends the palette entries of a vertex's four influences into one matrix, as BlendJoints does in the vertex shader.
#include <array>
#include <cstdio>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

glm::mat4 BlendJoints(const std::array<glm::mat4, 3>& palette, const glm::uvec4& joints, const glm::vec4& weights)
{
	glm::mat4 blended(0.0f);
	for (int influence = 0; influence < 4; influence++)
		blended += palette[joints[influence]] * weights[influence];
	return blended;
}

void Skin(const std::array<glm::mat4, 3>& palette, const glm::uvec4& joints, const glm::vec4& weights)
{
	const glm::vec4 bindPosition(1.0f, 1.0f, 0.0f, 1.0f);
	const glm::vec4 posed = BlendJoints(palette, joints, weights) * bindPosition;
	std::printf("joints (%u, %u), weights (%.2f, %.2f): vertex (1, 1, 0) goes to (%.2f, %.2f, %.2f)\n", joints[0], joints[1], weights[0], weights[1],
		posed.x, posed.y, posed.z);
}

int main()
{
	// Entry 0 leaves the vertex alone, entry 1 moves it 2 along x, entry 2 moves it 4 along y.
	const std::array<glm::mat4, 3> palette = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(2.0f, 0.0f, 0.0f)),
		glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 4.0f, 0.0f)) };
	// Unused influences name joint 0 with weight 0: they must still name a real joint, because the shader reads all four.
	Skin(palette, glm::uvec4(0, 1, 0, 0), glm::vec4(0.5f, 0.5f, 0.0f, 0.0f));
	Skin(palette, glm::uvec4(0, 2, 0, 0), glm::vec4(0.75f, 0.25f, 0.0f, 0.0f));
	Skin(palette, glm::uvec4(1, 2, 0, 0), glm::vec4(1.0f, 0.0f, 0.0f, 0.0f));
}
```

```text output-of="draw-skinned-toy.cpp"
joints (0, 1), weights (0.50, 0.50): vertex (1, 1, 0) goes to (2.00, 1.00, 0.00)
joints (0, 2), weights (0.75, 0.25): vertex (1, 1, 0) goes to (1.00, 2.00, 0.00)
joints (1, 2), weights (1.00, 0.00): vertex (1, 1, 0) goes to (3.00, 1.00, 0.00)
```

1. **Lines 7–13:** `BlendJoints` adds each influence's palette entry times its weight, as the shader does with three rows.
2. **Line 9:** the sum starts from the zero matrix, not the identity, because the weights of a vertex add up to 1.
3. **Lines 15–21:** `Skin` moves the bind-pose vertex with the blended matrix, as the vertex shader moves each vertex.
4. **Lines 28–31:** the unused influences name entry 0 with weight 0: they still name a real entry.

The blended matrix gives the weighted average of the positions each entry would give: the first vertex goes to $(2, 1, 0)$, between $(1, 1, 0)$ and $(3, 1, 0)$. The second goes to $(1, 2, 0)$, a quarter of the way from the first entry's place to the second's. A vertex with one weight of 1 follows its joint exactly. The toy keeps one matrix per joint as four rows; the shader keeps three, because the last row of an affine matrix is always 0, 0, 0, 1.

## Posed bounds

Every skinned vertex is a weighted average of the points that its joints would give it, and the weights are not negative and add up to 1. Each of those points lies inside the box of its joint, moved by the joint's palette entry. A weighted average of points inside a set of boxes lies inside the smallest box around all of them.

So the **union** of the moved joint boxes bounds every vertex of the mesh, in every pose. The bound is not tight: a joint's box includes space no vertex occupies. It is safe, and it costs only eight corner transforms per joint.

:::example[A forearm bent by 90 degrees]
An arm of two joints stands in its bind pose along the y axis. The upper arm covers $x \in [-0.2, 0.2]$ and $y \in [0, 1]$, the forearm $y \in [1, 2]$ with the same width; $z$ is $[-0.2, 0.2]$ for both. The bind-pose box is $x \in [-0.2, 0.2]$, $y \in [0, 2]$.

The pose bends the elbow at $(0, 1, 0)$ by 90 degrees about $z$, so the forearm points along $-x$. The upper arm's palette entry is the identity: its box stays. The forearm's entry first moves a point so the elbow lies at the origin, turns it, and moves it back: $(x, y)$ goes to $(-(y - 1), x + 1)$. For $y$ from 1 to 2, the new $x$ runs from 0 down to $-1$; for $x$ from $-0.2$ to $0.2$, the new $y$ runs from 0.8 to 1.2.

The union has $x \in [-1, 0.2]$ and $y \in [0, 1.2]$. A limb lies at $x = -1$, outside the bind-pose box, and a view that sees only the area around $x = -1$ finds the arm. The bind-pose box would have missed it.
:::

Animators that pose only when seen add one more term. Such an animator may skip poses while no view sees its character, so its newest pose can be old.

The pose then carries a reach: the box of every place its clips can take the joints. The renderer widens the bounds by that reach, plus a margin of the largest vertex distance from a joint's origin. A view that looks at where the character will be then finds it, and the animator poses it there. The animation part explains how those animators choose.

## The real code

The data flows from palette entries, to the skip decision, to the work on the job system, and to the shader. First the arithmetic of one proxy, `ComputePalette`. It builds each palette entry and, in the same loop, the bounds.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1341-L1358" symbol="RenderScene::ComputePalette"
void RenderScene::ComputePalette(const MeshSkinBinding& skin, const PoseInputs& pose, RenderData::AffineTransform* outPalette, AABB& outBounds)
{
	outBounds = AABB();
	for (size_t joint = 0; joint < skin.Joints.size(); joint++)
	{
		// Fourth rows stay 0, 0, 0, 1: every factor is affine.
		const glm::mat4 matrix = pose.AnimatorToProxy * pose.Joints[skin.Joints[joint]] * skin.InverseBindMatrices[joint];
		outPalette[joint] = RenderData::AffineTransform::FromMatrix(matrix);
		outBounds.Expand(skin.JointBounds[joint].Transformed(matrix));
	}
	// An animator that does not compute its pose every update: the bounds also take in wherever its clips take the joints
	// (and the vertices around them), so views of those places find it and it gets posed there.
	if (pose.Reach.IsValid())
	{
		const glm::vec3 margin(skin.MaxJointExtent * pose.ReachScale);
		outBounds.Expand(AABB(pose.Reach.Min - margin, pose.Reach.Max + margin).Transformed(pose.AnimatorToProxy));
	}
}
```

1. **Line 1347:** the palette entry multiplies three matrices: animator space to proxy space, the pose's joint, and the inverse bind matrix.
2. **Line 1348:** the entry stores only the upper three rows of the matrix.
3. **Line 1349:** the same matrix moves the joint's bind-pose box, so the palette and the bounds can never disagree.
4. **Lines 1353–1357:** an animator that poses only when seen adds its reach, widened by a margin.

`UpdateSkinnedPoses` runs once per frame from `RenderScene::Sync`. Its first part decides whether anything can have changed. Watch the versions it compares.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1366-L1383" from="// Nothing that palettes depend on changed" to="m_SkinDrawnVersion = drawnVersion;" symbol="RenderScene::UpdateSkinnedPoses"
// Nothing that palettes depend on changed: not the poses, not a transform, not a mesh layout, not a skin.
const ISkinningPoses* poses = m_Scene->GetService<ISkinningPoses>();
const uint64_t posesVersion = poses ? poses->GetPosesVersion() : 0;
const uint64_t transformsVersion = m_Scene->GetTransformsVersion();
const uint64_t hierarchyVersion = m_Scene->GetHierarchyVersion(); // Animator entities created or destroyed
const uint64_t drawnVersion = m_Scene->GetDrawnTransformsVersion(); // Animators drawn between fixed steps
if (!m_SkinDirty && poses == m_PosesProvider && posesVersion == m_PosesVersion && transformsVersion == m_SkinTransformsVersion
	&& hierarchyVersion == m_SkinHierarchyVersion && drawnVersion == m_SkinDrawnVersion)
	return;
m_SkinDirty = false;
// Versions are a provider's own: another provider's (the play copy's animation system after the editor's rest poses,
// which a clone's palettes come from) may repeat them for other poses.
const bool providerChanged = poses != m_PosesProvider;
m_PosesProvider = poses;
m_PosesVersion = posesVersion;
m_SkinTransformsVersion = transformsVersion;
m_SkinHierarchyVersion = hierarchyVersion;
m_SkinDrawnVersion = drawnVersion;
```

1. **Lines 1372–1374:** the skip: when the provider, the four versions and the :term[dirty flag]{id=dirty-flag} are all unchanged, the function returns before it visits a proxy.
2. **Line 1375:** the dirty flag clears once the pass runs.
3. **Lines 1376–1378:** versions belong to their provider, so a new provider forces new palettes.
4. **Lines 1379–1383:** the pass keeps the versions for the next frame's comparison.

Its second part walks the skin proxies. It learns which are posed, which return to the bind pose and which need new palettes.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1390-L1421" from="const PoseInputs inputs = EvaluatePose(proxy, poses);" to="m_PoseWork.push_back(PoseWork { index, inputs });" symbol="RenderScene::UpdateSkinnedPoses"
const PoseInputs inputs = EvaluatePose(proxy, poses);
skin.Animator = inputs.Animator; // Resolved for visibility reports also without a pose
const bool wasPosed = (m_Flags[proxy] & RenderProxyFlags::Skinned) != 0;
if (!inputs.Posed)
{
	if (wasPosed)
	{
		// Back to the bind pose.
		ReleasePalette(skin);
		m_Flags[proxy] &= ~RenderProxyFlags::Skinned;
		m_Stats.PosedProxies--;
		UpdateProxyPlacement(proxy);
		WriteInstances(proxy);
		MarkUpdated(proxy);
	}
	continue;
}
const Ref<const MeshSkinBinding>& binding = m_Meshes[m_MeshSlots[proxy]].Skin;
const uint32_t joints = static_cast<uint32_t>(binding->Joints.size());
if (wasPosed && !providerChanged && inputs.Version == skin.PoseVersion && skin.Binding == binding && skin.PaletteCount == joints
	&& SameBytes(inputs.AnimatorToProxy, skin.AnimatorToProxy))
	continue;
if (skin.PaletteCount != joints)
{
	ReleasePalette(skin);
	skin.PaletteFirst = AllocatePalette(joints);
	skin.PaletteCount = joints;
}
skin.PoseVersion = inputs.Version;
skin.AnimatorToProxy = inputs.AnimatorToProxy;
skin.Binding = binding;
m_PoseWork.push_back(PoseWork { index, inputs });
```

1. **Lines 1393–1406:** a proxy that lost its pose returns to the bind pose: its palette is released and its instances are written again.
2. **Lines 1409–1411:** the per-proxy skip: the same pose version, binding, joint count and animator-to-proxy bytes mean nothing to do.
3. **Lines 1412–1417:** the palette range is allocated again only when the joint count changes.
4. **Line 1421:** the proxy joins the work list; the arithmetic comes next.

Its last part does the arithmetic in parallel and publishes the results on the main thread.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1428-L1453" from="JobSystem::ParallelFor(" to="m_Stats.LastSyncPoses = static_cast<uint32_t>(m_PoseWork.size());" symbol="RenderScene::UpdateSkinnedPoses"
JobSystem::ParallelFor(static_cast<uint32_t>(m_PoseWork.size()), c_PoseBatchSize, [this](uint32_t begin, uint32_t end)
{
	for (uint32_t item = begin; item < end; item++)
	{
		const PoseWork& work = m_PoseWork[item];
		SkinEntry& skin = m_Skins[work.Skin];
		const MeshSkinBinding& binding = *m_Meshes[m_MeshSlots[skin.Proxy]].Skin;
		ComputePalette(binding, work.Inputs, m_Palette.data() + skin.PaletteFirst, skin.PosedBounds);
	}
});

for (const PoseWork& work : m_PoseWork)
{
	const SkinEntry& skin = m_Skins[work.Skin];
	const uint32_t proxy = skin.Proxy;
	if ((m_Flags[proxy] & RenderProxyFlags::Skinned) == 0)
	{
		m_Flags[proxy] |= RenderProxyFlags::Skinned;
		m_Stats.PosedProxies++;
	}
	UpdateProxyPlacement(proxy);
	WriteInstances(proxy);
	RecordPaletteChange(skin.PaletteFirst, skin.PaletteCount);
	MarkUpdated(proxy);
}
m_Stats.LastSyncPoses = static_cast<uint32_t>(m_PoseWork.size());
```

1. **Line 1428:** each job takes a batch of `c_PoseBatchSize` proxies, 16 of them.
2. **Line 1435:** a job writes only its proxy's palette range and bounds, so jobs share nothing and the result does not depend on their order.
3. **Lines 1439–1452:** after the jobs finish, the main thread alone sets the flag, places the proxy with its posed bounds, writes the instances and records the palette change.
4. **Line 1453:** `LastSyncPoses` counts the palettes computed this frame.

The build makes the skinned variants from the same sources as the others. Each line of the list names a source, the variant and its defines.

```cmake src="Strata/CMakeLists.txt#L211-L216"
"Scene/Mesh.vert|Scene/MeshSkinned.vert|ST_SKINNED"
"Scene/Mesh.vert|Scene/MeshVelocity.vert|ST_VELOCITY"
"Scene/Mesh.vert|Scene/MeshSkinnedVelocity.vert|ST_SKINNED,ST_VELOCITY"
"Scene/ShadowMesh.vert|Scene/ShadowMeshSkinned.vert|ST_SKINNED"
"Scene/ShadowMesh.vert|Scene/LocalShadowMesh.vert|ST_LOCAL_SHADOW"
"Scene/ShadowMesh.vert|Scene/LocalShadowMeshSkinned.vert|ST_SKINNED,ST_LOCAL_SHADOW"
```

1. **Line 211:** the first column is the source, the second the variant, the third the defines: here the mesh vertex shader with its skinned define.
2. **Lines 213–214:** the skinned variants also exist with motion vectors, and for the shadow vertex shader.
3. **Line 216:** the shadows of point and spot lights have their own skinned variant.

On the GPU, the joint buffer sits at register `t15`. The skinned vertex shaders of the mesh and its shadows call `BlendJoints` and then move the position, the normal and the tangent with the blended matrix.

```slang src="Strata/shaders/Include/Scene.slang#L192-L208"
StructuredBuffer<JointMatrix> u_Joints : register(t15);

// The skinning matrix of a vertex: its influences' palette entries blended by weight (linear blend skinning).
JointMatrix BlendJoints(InstanceData instance, uint4 joints, float4 weights)
{
	JointMatrix blended;
	blended.Rows[0] = float4(0.0);
	blended.Rows[1] = float4(0.0);
	blended.Rows[2] = float4(0.0);
	for (int influence = 0; influence < 4; influence++)
	{
		JointMatrix joint = u_Joints[instance.SkinPalette + joints[influence]];
		blended.Rows[0] += joint.Rows[0] * weights[influence];
		blended.Rows[1] += joint.Rows[1] * weights[influence];
		blended.Rows[2] += joint.Rows[2] * weights[influence];
	}
	return blended;
```

1. **Line 192:** the joint buffer, register `t15`, holds the palettes of every posed instance.
2. **Lines 201–207:** four influences, each reading the entry at the instance's first joint plus the vertex's joint index.
3. **Line 208:** the blended matrix returns to the caller, which moves the position, the normal and the tangent.

### The differences from the toy

The toy blends 4 by 4 matrices; the real code stores three rows. The toy has one proxy; the real code has a range of the palette per proxy, found through `InstanceData::SkinPalette`, the first joint of the proxy's range, so `InstanceData` stays 64 bytes. Its flag `c_InstanceSkinned` marks the posed instances. A skinned mesh that is not posed, for example before its first pose, is drawn in its bind pose with the ordinary pipelines.

The :term[sort key]{id=sort-key} of a draw has one bit for skinned meshes, bit 57, so skinned draws and others never share a batch. The GPU path adds a geometry class to its buckets: the skinned vertex arena drawn in its bind pose uses the ordinary pipelines, and the same arena posed uses the skinned ones ([GPU-driven path](../draw/gpu-driven.md)).

Two parts of the toy's world are missing. First, `HasSkinProxies` is a one-line test, whether the list of skin entries is empty, and the extraction and the shadow gathering start with it; `UpdateSkinnedPoses` starts with the same test on its list. Second, after the renderer collects the proxies it will draw, it reports the animators of those that are in view, and of off-view shadow casters whose shadows can fall into the view, through `ISkinningPoses::ReportVisible`. An animator that poses only when seen learns from the report that its character is seen, and the report says whether its pose is older than its time, so the animator poses it next frame.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Skinning on the CPU | Older engines and tools that need skinned vertices on the CPU | No skeleton knowledge on the GPU | CPU time per vertex and a vertex upload each frame |
| Compute skinning | Many current engines for crowds and many passes | One blend per vertex per frame for all passes | A buffer per character and a pre-pass |
| Dual quaternion skinning | Engines that need volume-preserving joints | No squeezed limbs at twisted joints | A new palette format and a shader path that Strata lacks |
| Bind-pose bounds | Simple renderers | No bounds work per pose | Limbs that vanish or lose their shadow |

## How it is tested

The suite `GPU.Animation` in `StrataTests/src/Renderer/GPUAnimationTests.cpp` renders skinned meshes on a real device. Its cases compare the forward, entity-ID and shadow passes with a reference skinned on the CPU. Others check that unchanged poses upload no palette bytes, and that a limb swung outside its bind-pose bounds is still drawn and still shadows the floor. Another case checks that shadow casters out of view report their animators only when their shadows can fall into the view.

The speed test `Skinned1000` of the `PerfGPU.Renderer` suite poses 1,000 characters of about 5,000 vertices again every frame. In `StrataTests/Perf/Budgets.json` its measured time is 0.7554 ms against a budget of 0.9567 ms; [Performance](../reference/performance.md) lists every budget. Run the suite with `StrataTests --test-suite=GPU.Animation` on a machine with a GPU.

## Changing it safely

- A new pass that draws skinned meshes must use the skinned variants of the same vertex shader as the other passes, or its depth differs from the prepass.
- Work added for skinned meshes goes behind `HasSkinProxies`.
- A change to what the palette or the bounds depend on needs a version the skip test compares, or the skip would hide the change. `m_SkinDirty` is the switch for changes that have no version.
- Anything per instance goes to a parallel buffer; `InstanceData` stays 64 bytes.
- Run `GPU.Animation`, the suites of the GPU-driven path and the metric `Skinned1000`.

## Summary

- Skinning can run on the CPU, in the vertex shader with a palette or in a compute pre-pass; Strata blends four joints in the vertex shader from palettes the CPU computes only for changed poses.
- Posed bounds are the union of each joint's bind-pose box moved by its palette entry, and they bound every vertex because a weighted average stays inside the union.
- `UpdateSkinnedPoses` returns when the versions of poses, transforms, hierarchy and :term[drawn transforms]{id=drawn-transform} and the :term[dirty flag]{id=dirty-flag} are unchanged; it skips unchanged proxies and computes the others again in batches of 16.
- Every pass of a skinned mesh uses the skinned variants so the depth tests agree, and `HasSkinProxies` makes scenes without skins pay nothing.

## Check yourself

1. Where does Strata blend the joints of a skinned vertex?

   - A. On the CPU, once per vertex per frame.
   - B. In the vertex shader, from palette entries.
   - C. In a compute pre-pass.

   :::answer{tests="skinning-place"}
   B. The CPU computes one matrix per joint and uploads those; the vertex shader reads four entries per vertex. A is the cost Strata avoids: all vertices pass through the CPU. C is later work: the pin has no compute skinning.
   :::

2. Use the joint boxes of the example, but bend the forearm by 180 degrees about $z$. What are the posed bounds?

   :::answer{tests="posed-bounds"}
   The forearm turns to point down. A point $(x, y)$ goes to $(-x, 2 - y)$, so the box has $y \in [0, 1]$ and the same width. The union with the upper arm is $x \in [-0.2, 0.2]$, $y \in [0, 1]$: smaller than the bind-pose box.
   :::

3. A robot stands still for 100 frames while nothing else in the scene moves. What does `LastSyncPoses` count in those frames, and why?

   :::answer{tests="palette-skip"}
   The answer is 0. The function sets `LastSyncPoses` to 0 and returns at its version test: the pose version, the transform version, the :term[hierarchy version]{id=hierarchy-version} and the drawn-transform version equal the saved ones, and the dirty flag is clear. No palette is computed, nothing is uploaded.
   :::

4. A mesh uses `Mesh.vert` without skinning in the depth prepass and the skinned variant in the forward pass. What goes wrong?

   :::answer{tests="same-variant"}
   The forward pass draws opaque geometry with an equal depth test. The two passes then compute positions by different code, the depths differ in the last bits and pixels fail the test, so holes appear. Both passes must use the same variant.
   :::

## Exercises

1. **Medium.** Write the two-joint arm as a program: a proxy holds its bind bounds until `Sync` gives it a pose. Print its bounds before and after `Sync` for a forearm bent by 90 and by 180 degrees.

   :::answer[Worked solution]{tests="posed-bounds" solution="sketches/draw-skinned-bounds.cpp"}
   The proxy starts with the union of the joint boxes, which is the bind-pose box. `Sync` replaces that union by the union of each box moved by `pose * inverse bind`.

   ```cpp sketch="draw-skinned-bounds.cpp"
   // A two-joint arm: its bounds before and after Sync, as RenderScene computes posed bounds.
   #include <array>
   #include <cmath>
   #include <cstdio>
   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>

   struct Box
   {
   	glm::vec3 Min = glm::vec3(1.0e9f);
   	glm::vec3 Max = glm::vec3(-1.0e9f);

   	void Expand(const Box& other)
   	{
   		Min = glm::min(Min, other.Min);
   		Max = glm::max(Max, other.Max);
   	}

   	// The box around the eight corners after the matrix moved them.
   	Box Transformed(const glm::mat4& matrix) const
   	{
   		Box result;
   		for (int corner = 0; corner < 8; corner++)
   		{
   			const glm::vec3 point((corner & 1) ? Max.x : Min.x, (corner & 2) ? Max.y : Min.y, (corner & 4) ? Max.z : Min.z);
   			const glm::vec3 moved = glm::vec3(matrix * glm::vec4(point, 1.0f));
   			result.Expand(Box { moved, moved });
   		}
   		return result;
   	}
   };

   struct Skin
   {
   	std::array<glm::mat4, 2> InverseBindMatrices;
   	std::array<Box, 2> JointBounds; // Bind-pose extent of the vertices of each joint
   };

   class Proxy
   {
   public:
   	explicit Proxy(const Skin& skin)
   		: m_Skin(skin)
   	{
   		for (const Box& box : skin.JointBounds)
   			m_LocalBounds.Expand(box); // Before the first Sync: the bind pose
   	}

   	void Sync(const std::array<glm::mat4, 2>& pose)
   	{
   		m_LocalBounds = Box();
   		for (size_t joint = 0; joint < 2; joint++)
   		{
   			const glm::mat4 palette = pose[joint] * m_Skin.InverseBindMatrices[joint];
   			m_LocalBounds.Expand(m_Skin.JointBounds[joint].Transformed(palette));
   		}
   	}

   	const Box& GetLocalBounds() const { return m_LocalBounds; }

   private:
   	Skin m_Skin;
   	Box m_LocalBounds;
   };

   // Rounds to hundredths and drops the sign of zero, so that rounding noise never prints as "-0.00".
   float Clean(float value)
   {
   	return std::round(value * 100.0f) / 100.0f + 0.0f;
   }

   void Print(const char* label, const Box& box)
   {
   	std::printf("%-10s min (%.2f, %.2f, %.2f) max (%.2f, %.2f, %.2f)\n", label, Clean(box.Min.x), Clean(box.Min.y), Clean(box.Min.z), Clean(box.Max.x),
   		Clean(box.Max.y), Clean(box.Max.z));
   }

   int main()
   {
   	// The upper arm stands from the origin to y = 1, the forearm from the elbow at y = 1 to y = 2; both are 0.4 wide.
   	Skin skin;
   	skin.InverseBindMatrices = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -1.0f, 0.0f)) };
   	skin.JointBounds = { Box { glm::vec3(-0.2f, 0.0f, -0.2f), glm::vec3(0.2f, 1.0f, 0.2f) }, Box { glm::vec3(-0.2f, 1.0f, -0.2f), glm::vec3(0.2f, 2.0f, 0.2f) } };

   	Proxy proxy(skin);
   	Print("before", proxy.GetLocalBounds());
   	for (const float degrees : { 90.0f, 180.0f })
   	{
   		// The elbow joint sits at (0, 1, 0) and turns about z.
   		const glm::mat4 elbow = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::rotate(glm::mat4(1.0f), glm::radians(degrees), glm::vec3(0.0f, 0.0f, 1.0f));
   		proxy.Sync({ glm::mat4(1.0f), elbow });
   		Print(degrees == 90.0f ? "bent 90" : "folded 180", proxy.GetLocalBounds());
   	}
   }
   ```

   ```text output-of="draw-skinned-bounds.cpp"
   before     min (-0.20, 0.00, -0.20) max (0.20, 2.00, 0.20)
   bent 90    min (-1.00, 0.00, -0.20) max (0.20, 1.20, 0.20)
   folded 180 min (-0.20, 0.00, -0.20) max (0.20, 1.00, 0.20)
   ```

   1. **Lines 45–46:** before the first `Sync`, the proxy holds the union of the bind-pose boxes.
   2. **Lines 51–56:** `Sync` starts empty and adds each joint's box through that joint's palette entry.
   3. **Line 54:** the palette is the pose's joint times the inverse bind matrix, the same product as in the engine.
   4. **Lines 66–70:** `Clean` rounds and removes the sign of zero, so noise never prints as a minus.
   5. **Lines 87–93:** each angle turns the elbow about the z axis through its own joint position.

   The 90 degree line matches the worked example. The 180 degree line is the upper arm's box alone, because the folded forearm lies inside it.
   :::

2. **Hard.** Trace it yourself. Set a breakpoint in `RenderScene::UpdateSkinnedPoses`. Find why the robot of the Third-Person sample costs no palette work in a frame where nothing it depends on changed, and which version changes first when it dances.

   :::answer[Worked solution]{tests="palette-skip"}
   The function is in `Strata/src/Strata/Renderer/RenderScene.cpp`. In a quiet frame, the test of the four versions and `m_SkinDirty` is false for the change, so the function returns before it visits a proxy, and `LastSyncPoses` is 0. When the robot dances, the animation system raises the pose version that `ISkinningPoses::GetPosesVersion` returns, so `posesVersion` differs from `m_PosesVersion` and the pass runs.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RenderScene.cpp` and `RenderScene.h`: `EvaluatePose`, `ComputePalette`, `UpdateSkinnedPoses`, `HasSkinProxies`.
- `Strata/src/Strata/Renderer/Mesh.h`: `MeshSkinBinding`. `Strata/src/Strata/Scene/SceneServices.h`: `ISkinningPoses`.
- `Strata/src/Strata/Renderer/SceneRenderData.h`, `SceneDrawKey.h` and `GPUSceneData.h`: the skinned flag, key bit and geometry class.
- `Strata/shaders/Scene/Mesh.vert.slang`, `ShadowMesh.vert.slang` and `Strata/shaders/Include/Scene.slang`: the variants and `BlendJoints`.
- `StrataTests/src/Renderer/GPUAnimationTests.cpp` and `StrataTests/src/Perf/AnimationPerfTests.cpp`.

## Further reading

- Real-Time Rendering, chapter on animation: skinning, morphing and the cost of each. Intermediate.
- Kavan, Collins, Zara and O'Sullivan, "Skinning with Dual Quaternions": the paper behind the technique named above. Advanced.
