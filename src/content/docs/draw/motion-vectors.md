---
id: draw/motion-vectors
title: "Motion vectors and motion history"
description: "How Strata tells every drawn pixel where it was a frame ago, and why each renderer keeps its own copy of the previous instances."
kind: internals
size: M
tracks: [E]
needs: [draw/render-scene-gpu, draw/skinned]
time: 65
since: 0.6.0
learn:
  - id: previous-position
    text: explain where a pixel's previous position comes from for a moving object, a skinned mesh and a still camera
  - id: history-per-renderer
    text: explain why the motion history belongs to each renderer and not to the shared GPU copy
  - id: history-copy
    text: trace which elements the history copies after one entity moves
  - id: unjittered-double
    text: explain why motion uses matrices without jitter, built in double
  - id: velocity-passes
    text: name why the prepass and the forward pass both draw with the velocity variant
status: final
---

A **motion vector** is the screen distance a drawn point has moved since the :term[renderer's]{id=renderer} previous frame, and the picture of all of them is the **velocity target**. Strata computes one for every pixel it draws, whether the cause is a moving object, a bending skinned mesh or a camera that turns while the world stands still. Temporal anti-aliasing (the subject of [Temporal anti-aliasing](../image/taa.md), which this page does not need) and motion blur are the two users: both must know where a pixel was a frame ago. This page does not teach what they do with the vectors. It teaches how the vectors come to exist, and why that costs the renderer a copy of the previous frame's instances.

## The problem and how engines solve it

Think of a flip book. To say how far a drawn ball moved, you hold two pages side by side and compare the ball's position on each. A renderer has the same task, but it only has the current frame: the previous image is gone. What matters is not the old colors but the old position of each surface point.

Engines use three approaches, in rising cost. The first is **camera-only reprojection**: read the pixel's depth, rebuild its world position, and push that position through the previous camera's matrices. It is cheap and needs no data beyond the depth, but it assumes the point did not move. A running character gets the motion of the wall behind it.

The second approach adds the previous transform of each object. The vertex :term[shader]{id=shader} draws the vertex twice in effect: once with this frame's world matrix and once with last frame's, then compares the two screen positions. Rigid movers are now right. A character whose arm bends is still wrong, because a bone moves the vertex, not the object's matrix.

The third approach also keeps the previous skinning, meaning the previous joint palette, and poses the vertex with it. Everything that moves is now right, at the price of storing last frame's instances and palettes.

Strata takes the third approach. It stores last frame's data in a copy that belongs to the renderer, and it adds velocity variants of the scene vertex shaders that read it.

## The map

Three owners hold data, and the picture shows how it flows.

```mermaid caption="The shared GPU copy of the scene writes instances and joint matrices and logs each write. Each renderer copies only the logged writes into its own history at the end of its frame, and the next frame's vertex shaders read that history." alt="A flow from the render scene through the shared GPU copy and its write log, then into one history for each of two renderers, which feed the velocity pass of the next frame."
flowchart LR
  RS[RenderScene] --> GPU["RenderSceneGPU: instances, palette, write logs"]
  GPU -->|"writes since version"| HA["Renderer A history"]
  GPU -->|"writes since version"| HB["Renderer B history"]
  HA --> VA["Renderer A velocity variants"]
  HB --> VB["Renderer B velocity variants"]
  GPU --> VA
  GPU --> VB
```

The :term[main thread]{id=main-thread} submits all of it, and the :term[graphics processing unit]{id=gpu} (:term[GPU]{id=gpu}) runs it. `RenderSceneGPU` owns the shared buffers and the logs. `SceneRenderer` owns its history buffers, the velocity target and the copy. `Mesh.vert` and `Include/Motion.slang` do the arithmetic in the shader. The sections below follow the data in that order.

## The contract

A caller asks for motion with `SceneRenderOptions::MotionVectors`. The debug view, temporal anti-aliasing, motion blur and the spatial modes of screen-space reflections ask for it too. Strata promises these things.

- The target holds each surface's position in this frame's screen coordinates (:term[UV]{id=texture-coordinates}) minus its position in the previous frame, both without jitter, for every opaque, alpha-masked and glass surface. UV runs from 0 at the top-left corner to 1 at the bottom-right.
- A camera that did not move gives exactly zero motion, and the sub-pixel jitter that temporal anti-aliasing adds, a tiny shift of the camera each frame, never appears as motion.
- Where nothing was drawn, the target holds zero; the shaders that need more derive the camera's own motion from the depth.
- The image is the same with and without motion vectors, bit for bit.

The caller must accept one limit. A frame has a previous frame to compare with only if the renderer's last frame also asked for motion. That frame must also have drawn the same :term[render scene]{id=render-scene} or its source. Otherwise the frame has no motion, and `SceneRendererStats::MotionHistory` says so.

:::rule
**Keep each frame's "previous" data out of the shared GPU copy.** Several renderers draw one scene at different times, for example the editor's viewport and a thumbnail. One "previous" in the shared buffers would belong to whichever renderer drew last, and every other renderer would compute wrong motion. See [the render scene's GPU copy](../draw/render-scene-gpu.md).
:::

## A toy version

The toy answers one question: given two world positions and two camera matrices, where did the point move on screen? It projects each position with its own frame's view-projection matrix, converts to UV, and subtracts. The projection chosen keeps the numbers small. With a :term[field of view]{id=field-of-view} of 90 degrees and a square picture, a point's clip $x$ equals its view-space $x$, and its clip $w$ equals its distance in front of the camera.

:::question
The code below uses functions, references, `std::printf(` and a call such as `glm::vec2(`: if they are new, read [loops, functions and structs](../basics/programming-2.md) and [classes and references](../basics/programming-3.md) first.
:::

The program prints the motion of one point in four cases. Look at the signs in the output, and at which case moves the point and which moves only the camera.

```cpp sketch="draw-motion-vectors-toy.cpp"
// A pixel's motion from two positions and two view-projection matrices: where the point lands on screen now, minus
// where it landed in the previous frame, in UV units (x to the right, y downward).
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cstdio>

namespace
{

	glm::vec2 ToUV(const glm::mat4& viewProjection, const glm::vec3& point)
	{
		const glm::vec4 clip = viewProjection * glm::vec4(point, 1.0f);
		const glm::vec2 ndc = glm::vec2(clip) / clip.w;
		return glm::vec2(ndc.x * 0.5f + 0.5f, 0.5f - ndc.y * 0.5f);
	}

	glm::mat4 MakeViewProjection(const glm::vec3& cameraPosition)
	{
		const glm::mat4 view = glm::translate(glm::mat4(1.0f), -cameraPosition);
		const glm::mat4 projection = glm::perspective(glm::radians(90.0f), 1.0f, 0.1f, 100.0f);
		return projection * view;
	}

	glm::vec2 Motion(const glm::mat4& current, const glm::vec3& currentPoint, const glm::mat4& previous, const glm::vec3& previousPoint)
	{
		return ToUV(current, currentPoint) - ToUV(previous, previousPoint);
	}

	void Print(const char* name, const glm::vec2& motion)
	{
		std::printf("%-26s x %+.4f  y %+.4f\n", name, motion.x, motion.y);
	}

}

int main()
{
	const glm::mat4 still = MakeViewProjection(glm::vec3(0.0f));
	const glm::mat4 panned = MakeViewProjection(glm::vec3(0.2f, 0.0f, 0.0f));
	const glm::vec3 before(1.0f, 1.0f, -4.0f);
	const glm::vec3 after(1.4f, 1.4f, -4.0f);

	Print("still point, still camera", Motion(still, before, still, before));
	Print("cube moved, still camera", Motion(still, after, still, before));
	Print("still point, camera pans", Motion(panned, before, still, before));
	Print("both moved", Motion(panned, after, still, before));
	return 0;
}
```

```text output-of="draw-motion-vectors-toy.cpp"
still point, still camera  x +0.0000  y +0.0000
cube moved, still camera   x +0.0500  y -0.0500
still point, camera pans   x -0.0250  y +0.0000
both moved                 x +0.0250  y -0.0500
```

1. **Line 15:** the conversion from :term[clip space]{id=clip-space} to UV flips y, because UV rows grow downward.
2. **Line 27:** the whole idea: this frame's position minus the previous one.
3. **Lines 44–47:** the four cases; the previous point and matrix are the second pair.

The first case is the still scene: the same position through the same matrix twice gives exactly zero. The second case moves the cube by $(0.4, 0.4, 0)$ with the camera still. The camera sits at the origin, so the point at $(1, 1, -4)$ has :term[normalized device coordinates]{id=normalized-device-coordinates} $(0.25, 0.25)$. Its UV is $(0.625, 0.375)$, because UV y grows downward.

After the move the point is at $(1.4, 1.4, -4)$, whose coordinates are $(0.35, 0.35)$ and whose UV is $(0.675, 0.325)$. The motion is $(+0.05, -0.05)$: right and up on screen, up being negative in UV.

The third case moves only the camera, 0.2 to the right. The still point is now 0.8 to the right of the camera, so its UV x is 0.6 where it was 0.625, and the motion is $-0.025$. A camera that moves right makes the world slide left. The fourth case adds the two, and the two motions add.

:::example[Motion in pixels]
A viewport is 1280 pixels wide and 720 high. The cube's motion of $(+0.05, -0.05)$ UV is $0.05 \times 1280 = 64$ pixels to the right and $0.05 \times 720 = 36$ pixels up. The panning camera's $-0.025$ is 32 pixels to the left. The motion debug view of the page's last section draws exactly these pixel counts as colors, full strength at 16 pixels a frame.
:::

The toy fakes the hard part. It knows each point's previous world position because the program wrote it down. A renderer receives a vertex of a mesh and no memory of where it was, and a skinned vertex has no single "world position" to remember, since a blend of joint matrices made it. The real code exists to recover that previous position.

## The real code, in the order data flows

### The frame's matrices

Before any vertex is drawn, the renderer builds two matrices that every pixel's motion uses. The lines below build the current matrix without jitter and the previous one.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3239-L3248"
// Built in double, from the same products, so a camera that did not move gives the same matrix twice (no motion).
frame.UnjitteredViewProjection = glm::mat4(glm::dmat4(camera.Projection) * glm::dmat4(frame.View));
frame.PreviousViewProjection = frame.UnjitteredViewProjection;
if (m_Stats.MotionHistory)
{
	const glm::dvec3 offset = glm::dvec3(camera.Position) - glm::dvec3(m_MotionCamera.Position);
	frame.PreviousViewProjection = glm::mat4(glm::dmat4(m_MotionCamera.Projection) * glm::dmat4(m_MotionCamera.RelativeView)
		* glm::translate(glm::dmat4(1.0), offset));
}
// Per-pixel noise turns by the golden ratio's fraction of a turn each frame of the history (from its reset on, so captures
```

1. **Line 3240:** the matrix without jitter, built in double.
2. **Line 3241:** with no history the previous matrix equals the current one, so motion is zero.
3. **Lines 3244–3246:** the previous camera's matrices, moved by the double-precision offset between the two camera positions.

Temporal anti-aliasing nudges the projection by a sub-pixel jitter in the matrix called `ViewProjection`. If motion used it, the jitter would appear as motion: a still camera would seem to move a fraction of a pixel back and forth. `UnjitteredViewProjection` leaves the jitter out. Strata also builds it in double precision from the same products, so a camera that did not move gives the same matrix twice and the difference is exactly zero.

In single precision, two products that mathematically agree can differ in the last bit, and zero would not be zero. The previous matrix is built relative to the current camera position: the double-precision offset between the two positions is added in, so a world far from the origin keeps its precision.

### The vertex shader

The velocity variants of `Mesh.vert`, one for plain meshes and one for skinned meshes, compute the previous clip position of every vertex. They carry both clip positions to the pixel shader. Read the lines for three tests: is the history's record the same entity's, did the palette keep its range, and did anything actually change.

```slang src="Strata/shaders/Scene/Mesh.vert.slang#L61-L82"
#ifdef ST_VELOCITY
// The instance as the previous frame drew it: the history's record when it is the same entity's (a slot another entity
// held, or a new instance, moves with the camera only), posed by its palette as then when that is the same range. What did
// not change takes this frame's values, so it does not move however the two would round.
InstanceData previous = u_PreviousInstances[instanceIndex];
bool sameEntity = u_Frame.TemporalParams.x > 0.5 && previous.EntityID == instance.EntityID;
float3 previousPosition = position;
#ifdef ST_SKINNED
if (sameEntity && (previous.Flags & ST_INSTANCE_SKINNED) != 0u && previous.SkinPalette == instance.SkinPalette)
{
	JointMatrix previousSkin = BlendPreviousJoints(previous, a_Joints, a_Weights);
	if (any(previousSkin.Rows[0] != skin.Rows[0]) || any(previousSkin.Rows[1] != skin.Rows[1]) || any(previousSkin.Rows[2] != skin.Rows[2]))
		previousPosition = SkinPosition(previousSkin, a_Position);
}
#endif
float3 previousRelative = relativePosition;
if (sameEntity && (any(previous.WorldRows[0] != instance.WorldRows[0]) || any(previous.WorldRows[1] != instance.WorldRows[1])
	|| any(previous.WorldRows[2] != instance.WorldRows[2]) || any(previousPosition != position)))
	previousRelative = TransformPositionRelative(previous, previousPosition);
v_CurrentClip = mul(u_Frame.UnjitteredViewProjection, float4(relativePosition, 1.0));
v_PreviousClip = mul(u_Frame.PreviousViewProjection, float4(previousRelative, 1.0));
#endif
```

1. **Line 66:** the history counts only when it holds the previous frame and the same entity drew this slot.
2. **Lines 69–73:** the previous pose, used only when the palette range is the same and the pose changed.
3. **Lines 77–79:** the previous world position, used only when something changed.
4. **Lines 80–81:** the two clip positions the pixel shader subtracts.

The camera-relative positions come from [Camera-relative space](../draw/mirrors-camera-relative.md), which taught the part of this shader above the quote.

`TemporalParams.x` is 1 only when the history holds the previous frame. The entity test protects against a slot taken again: an instance slot freed and taken by another entity holds the old entity's matrix, and trusting it would draw a long streak. A new instance has no record, so it moves with the camera only. The palette test does the same for skinning: the previous pose counts only when the instance still points at the same range of joint matrices.

The code compares each value with the current one and keeps the current when they are equal. This avoids a quiet problem: two paths to the same position can differ by rounding, which would appear as tiny motion on still objects. So whatever did not change takes this frame's values.

### The pixel shaders and the target

The :term[depth prepass]{id=depth-prepass} writes the velocity target. Its shader subtracts the two clip positions after converting each to UV, by `GetClipMotion`. The target is `RG16_FLOAT`, two :term[half-floats]{id=half-float} per pixel, about 4 :term[bytes]{id=byte} a pixel, in UV units.

Both the depth prepass and the forward pass draw with the velocity variant when a frame has motion. The forward pass ignores the extra outputs, but it needs the same vertex module.

The forward pass draws opaque geometry with an `EQUAL` depth test, which accepts a pixel only if its depth equals the prepass's depth to the last bit. A different vertex shader may compute a slightly different position, and then surfaces would flicker or vanish. The shadow passes and blended transparent surfaces keep their modules. Glass, which the transparent pass draws first without blending, writes its own motion with a velocity variant.

Where nothing was drawn, as in the sky, the target holds zero, and the shaders that need more call `GetCameraMotion`.

```slang src="Strata/shaders/Include/Motion.slang#L6-L15"
// The motion (UV units, current minus previous position, as the velocity target holds it) of a point that did not move, seen
// at a pixel's UV and depth: the camera's motion alone. Where nothing was drawn (depth 0: the sky) the point is infinitely far,
// a direction, which the camera's translation does not move; orthographic views take the far plane there.
float2 GetCameraMotion(float2 uv, float depth)
{
	float4 point = mul(u_Frame.InverseViewProjection, float4(UVToNDC(uv), depth, 1.0));
	if (depth <= 0.0 && u_Frame.CameraForward.w < 0.5)
		point = float4(point.xyz / point.w, 0.0);
	return GetClipMotion(mul(u_Frame.UnjitteredViewProjection, point), mul(u_Frame.PreviousViewProjection, point));
}
```

1. **Line 11:** the pixel's UV and depth give back a point in space.
2. **Lines 12–13:** the sky becomes a direction (w of 0), which camera translation cannot move.
3. **Line 14:** the same two matrices as the vertex shader, applied to that point.

For the sky (depth 0) the point is infinitely far away, a direction, so the camera's translation does not move it; only its turn does. Orthographic views take the :term[far plane]{id=far-plane} there instead.

### The motion history

The shader above reads `u_PreviousInstances`, a buffer that must hold every instance exactly as the renderer's previous frame drew it. The renderer keeps this copy, called the **motion history**: its own copy of the instance and joint-palette buffers as its latest frame drew them. It costs 64 bytes for each instance slot of the scene and 48 bytes for each joint matrix, and exists only for a renderer that asks for motion.

Copying every slot each frame would be wasteful for a scene where one cube moves. So the shared :term[GPU copy]{id=gpu-copy} keeps a **write log**. Each time it uploads a range of instances or of joint matrices, it records the range under a **write version**: a number that grows with every update and is unique within the process. A renderer remembers the version it last copied at. At the end of its frame, `RecordMotionCopy` asks the log for every range written after that version.

The first part of the function builds, for each of the two buffers, a list of the elements to copy.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1360-L1391"
m_MotionCopyList.clear();
for (size_t index = 0; index < parts.size(); index++)
{
	Part& part = parts[index];
	m_MotionRanges.clear();
	const bool logged = !full
		&& (index == 0 ? m_SceneGPU->GetInstanceWrites(m_MotionSceneId, m_MotionWriteVersion, m_MotionRanges)
			: m_SceneGPU->GetPaletteWrites(m_MotionSceneId, m_MotionWriteVersion, m_MotionRanges));
	if (!logged)
	{
		part.Full = true;
		continue;
	}
	part.ListOffset = static_cast<uint32_t>(m_MotionCopyList.size());
	std::sort(m_MotionRanges.begin(), m_MotionRanges.end());
	uint64_t covered = 0; // Elements before it are listed
	for (const auto& [first, count] : m_MotionRanges)
	{
		const uint64_t end = std::min<uint64_t>(static_cast<uint64_t>(first) + count, part.Capacity);
		for (uint64_t element = std::max<uint64_t>(first, covered); element < end; element++)
			m_MotionCopyList.push_back(static_cast<uint32_t>(element));
		covered = std::max(covered, end);
	}
	part.Count = static_cast<uint32_t>(m_MotionCopyList.size() - part.ListOffset);
	// A list of half the buffer copies no faster than the whole buffer.
	if (static_cast<uint64_t>(part.Count) * 2 > part.Capacity)
	{
		m_MotionCopyList.resize(part.ListOffset);
		part.Count = 0;
		part.Full = true;
	}
}
```

1. **Lines 1365–1372:** ask the log for the writes since the history's version; when it cannot answer, the whole buffer is copied.
2. **Lines 1375–1382:** sort the ranges and list each element once, even when ranges overlap.
3. **Lines 1384–1390:** a list longer than half the buffer is dropped for a whole copy.

The second part copies. When the list is long, or something is missing, it copies the whole buffer; otherwise it dispatches a small compute shader over the list.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L1431-L1444"
	// At most 65535 groups of 64 elements per dispatch.
	constexpr uint32_t c_GroupSize = 64;
	constexpr uint32_t c_MaxEntriesPerDispatch = 65535 * c_GroupSize;
	nvrhi::ComputeState state;
	state.pipeline = m_MotionCopyPipeline;
	state.bindings = { m_MotionCopySets[index] };
	commandList->setComputeState(state);
	for (uint32_t first = 0; first < part.Count; first += c_MaxEntriesPerDispatch)
	{
		const RenderData::MotionCopyParameters parameters = { first, part.Count, part.ElementSize / 4, part.ListOffset };
		commandList->setPushConstants(&parameters, sizeof(parameters));
		commandList->dispatch((std::min(part.Count - first, c_MaxEntriesPerDispatch) + c_GroupSize - 1) / c_GroupSize, 1, 1);
	}
}
```

1. **Lines 1431–1433:** a dispatch has a limit of 65535 groups, each of 64 threads.
2. **Lines 1438–1443:** a long list takes several dispatches, each told its first entry through a push constant, a small value sent with the dispatch.

The compute shader is short. Each thread takes one entry of the list and copies one element, word by word.

```slang src="Strata/shaders/Scene/MotionCopy.comp.slang#L5-L30"
// A renderer's motion history (SceneRenderer): copies the listed elements of the render scene's instance or palette buffer
// into the renderer's copy of it, a thread per element.

StructuredBuffer<uint> u_Source : register(t0);
StructuredBuffer<uint> u_List : register(t1);
RWStructuredBuffer<uint> u_Destination : register(u0);

// RenderData::MotionCopyParameters
struct MotionCopyParameters
{
	uint First;
	uint Count;
	uint StrideWords;
	uint ListOffset;
};
[[vk::push_constant]] ConstantBuffer<MotionCopyParameters> u_Parameters;

void st_Main()
{
	uint entry = u_Parameters.First + st_GlobalInvocationID.x;
	if (entry >= u_Parameters.Count)
		return;
	uint base = u_List[u_Parameters.ListOffset + entry] * u_Parameters.StrideWords;
	for (uint word = 0u; word < u_Parameters.StrideWords; word++)
		u_Destination[base + word] = u_Source[base + word];
}
```

1. **Lines 8–10:** the shared buffer, the list of elements and the history.
2. **Lines 24–26:** a thread past the end of the list does nothing.
3. **Lines 27–29:** the thread copies the words of one element.

The copy runs at the end of the frame, after every pass that reads the history, so the history then holds this frame for the next one. A renderer further behind than the log remembers, a new history, or a different render scene copies whole buffers. A still scene copies nothing.

### The history in miniature

The next sketch has the same shape with eight float slots instead of instance records: a shared buffer, a log of writes under versions, and two histories that each remember their own version.

```cpp sketch="draw-motion-vectors-history.cpp"
// A motion history in miniature: a shared buffer of eight instance slots, a log of what was written under each write
// version, and a renderer's own copy that takes only the slots written since the version it last saw.
#include <cstdint>
#include <cstdio>
#include <vector>

namespace
{

	struct Write
	{
		uint64_t Version;
		uint32_t Slot;
	};

	struct SharedBuffer
	{
		std::vector<float> Slots = std::vector<float>(8, 0.0f);
		std::vector<Write> Log;
		uint64_t Version = 0;

		void Set(uint32_t slot, float value)
		{
			Slots[slot] = value;
			Log.push_back({ ++Version, slot });
		}
	};

	struct History
	{
		std::vector<float> Copy = std::vector<float>(8, 0.0f);
		uint64_t Version = 0;

		uint32_t Update(const SharedBuffer& shared)
		{
			uint32_t copied = 0;
			for (const Write& write : shared.Log)
			{
				if (write.Version <= Version)
					continue;
				Copy[write.Slot] = shared.Slots[write.Slot];
				copied++;
			}
			Version = shared.Version;
			return copied;
		}
	};

}

int main()
{
	SharedBuffer shared;
	History historyA;
	History historyB;
	shared.Set(3, 1.0f);
	const uint32_t firstA = historyA.Update(shared);
	const uint32_t firstB = historyB.Update(shared);
	std::printf("frame 1: A copies %u, B copies %u\n", firstA, firstB);
	shared.Set(3, 2.0f);
	shared.Set(5, 7.0f);
	std::printf("frame 2: A copies %u\n", historyA.Update(shared));
	std::printf("frame 3: A copies %u\n", historyA.Update(shared));
	const uint32_t lateB = historyB.Update(shared);
	std::printf("frame 4: B copies %u, its slot 3 holds %.1f\n", lateB, historyB.Copy[3]);
	return 0;
}
```

```text output-of="draw-motion-vectors-history.cpp"
frame 1: A copies 1, B copies 1
frame 2: A copies 2
frame 3: A copies 0
frame 4: B copies 2, its slot 3 holds 2.0
```

1. **Line 25:** each write gets the next version number, and the log records it.
2. **Lines 39–41:** a history takes only writes newer than the version it saw.
3. **Line 44:** the history remembers the newest version for next time.

The output shows the idea behind the two-renderer rule. History A copies nothing in a still frame. History B was never updated since version 1, so the log lets it catch up on exactly the two writes it missed, and its slot 3 holds the newest value. If the "previous" values lived in the shared buffer, B would have no way to ask what it had last drawn.

## The motion debug view

The motion view colors each pixel by the direction of its motion: right red, up yellow-green, left blue-green, down violet. The strength grows with the speed, to a limit of 16 pixels a frame, and a pixel that does not move shows the image darker. The editor's viewport shows it as **Motion** among its debug views, and the option is `SceneRenderOptions::ShowMotionVectors`.

::figure{id=motion-view}

Strata's own samples show it well. In the Third-Person sample, run the robot sideways or pan the camera while it runs: the world turns one color together, the robot shows its own mix, and the swinging limbs differ from the body.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Camera-only reprojection from depth | Simple temporal effects | No history buffers and no velocity shader variants | Wrong motion for every moving object |
| Previous transforms only | Many forward renderers | Half the history: no palettes | Skinned meshes would smear or blur wrongly |
| Previous data in the shared GPU copy | Engines with a single viewport | No per-renderer memory | Several renderers would corrupt each other's motion |
| Full copy of the history every frame | The simplest correct design | No write logs and no copy shader | A copy of every slot even when nothing moved |

## How it is tested

The suite `GPU.SceneRenderer.MotionVectors` renders small scenes and reads the target back. Its cases check these things:

- the history holds what the renderer's latest frame drew and copies only what was written since;
- a still view has no motion and a moving camera moves every pixel as the :term[depth buffer]{id=depth-buffer} predicts;
- moved entities, skinned poses and mirrored instances carry their own motion;
- slots that change hands and instances whose upload waited start without motion;
- level-of-detail cross-fades carry the instance's motion through both levels;
- two renderers of one scene each compare with their own previous frame;
- the motion view colors by direction, and asking for motion leaves the image bit-identical.

The tests compare motion with a reprojection on the processor, within 0.01 pixels plus 0.1 % of the motion. The cases that draw moving scenes run on both the CPU-driven path and the GPU-driven path. The tests need a GPU, so on a machine without one skip them:

```sh
ctest --preset linux-debug -LE gpu
```

Run the suite directly with `StrataTests --test-suite=GPU.SceneRenderer.MotionVectors*`. A case that fails shows the pixel and the expected motion.

## Changing it safely

Three rules apply when you change this code. Each has a reason.

- Give the prepass and the forward pass the same vertex module: an `EQUAL` depth test needs the same bits. Never give one of the two a velocity module alone.
- Keep "previous" out of the shared copy: renderers draw at different times.
- Build matrices for motion in double and leave the jitter out: a still camera must give zero.

When you add a per-instance field that the vertex shader reads, decide whether the previous frame's value matters. If it does, the history copies it with the instance, since the copy treats each element as a block of words. A new buffer that the velocity variants read needs its own history and its own write log, and tests like those above.

## Summary

- A motion vector is the current UV position minus the previous one, both without jitter. The previous position comes from last frame's instance record, palette and camera, and from the camera alone where nothing was drawn.
- The history is each renderer's own copy of the instance and palette buffers, because renderers draw at different times and the shared copy has no single "previous".
- After a frame the renderer copies only what the write log says changed since its last version, with one compute thread for each listed element.
- Motion uses matrices without jitter, built in double, so a still camera gives exactly zero and the jitter never appears as motion.
- Both the prepass and the forward pass use the velocity variant, so the `EQUAL` depth test sees equal positions.

## Check yourself

1. A cube stands still while the camera turns. Which part of the shader gives the cube its motion?

   - A. The cube's previous world matrix from the history.
   - B. The camera's previous view-projection matrix, since the cube's record did not change.
   - C. The jitter offset.

   :::answer{tests="previous-position"}
   B. The shader compares the two world matrices, finds them equal, and keeps the current position, so only the two camera matrices differ. A is wrong because it did not change: the history is read but gives the same values. C is wrong because motion uses matrices without jitter.
   :::

2. An engine keeps one "previous instance" buffer in the shared GPU copy. The editor draws its viewport and a thumbnail from one scene. Say what goes wrong.

   :::answer{tests="history-per-renderer"}
   Each renderer replaces the buffer's contents with its own frame. The viewport then compares its frame with the thumbnail's, drawn at a different time, from a different camera, so its motion is wrong. Per-renderer histories avoid this.
   :::

3. A scene of 1,000 instances moves one entity. How many instance elements does the history copy at the end of the frame, and how many joint matrices?

   :::answer{tests="history-copy"}
   One instance and no joint matrices, as the test with a cube shows. The write log lists the entity's slot only, and the palette log is empty.
   :::

4. A world sits 20 kilometers from the origin, and the camera does not move. Why must the motion be exactly zero, and what keeps it so?

   :::answer{tests="unjittered-double"}
   Any non-zero value would drive temporal effects to smear still pixels. The matrices are built in double, relative to the camera, from the same products, so the same camera gives the same matrix twice and the difference is zero.
   :::

5. Someone gives only the depth prepass the velocity variant to save time in the forward pass. What happens?

   :::answer{tests="velocity-passes"}
   The forward pass uses an `EQUAL` depth test, which needs the prepass's depth bit for bit. Two different vertex modules can differ in rounding, so surfaces would fail the test and flicker or vanish.
   :::

## Exercises

1. **Basic.** Change the toy so the camera moves by 0.4 to the right and the cube stays at $(1, 1, -4)$. Compute the motion by hand first, then predict the sign.

   :::answer[Worked solution]{tests="previous-position"}
   The point is 0.6 right of the camera, so its :term[normalized]{id=normalization} x is $0.15$ and its UV x is $0.575$. Before it was $0.625$. The motion is $-0.05$ in x and $0$ in y. The sign is negative, because the world slides left.
   :::

2. **Medium.** Extend the toy's idea to depth. A camera moves 0.4 to the right while three points at x = 1 stand 2, 4 and 8 in front of it. Write a program that prints each point's motion in pixels on a 1280-pixel-wide viewport, and say what it shows about camera-only reprojection.

   :::answer[Worked solution]{tests="previous-position"}
   Each point's motion is the difference of two screen positions, so the program asks for the position twice, once for each camera.

   ```cpp sketch="draw-motion-vectors-parallax.cpp"
   // The same camera move seen by points at three depths: nearer points move farther on screen.
   #include <array>
   #include <cstdio>

   namespace
   {

   	// Screen x in UV for a point at `pointX` and `depth` in front of a camera at `cameraX` (field of view 90 degrees).
   	float ScreenX(float pointX, float cameraX, float depth)
   	{
   		return ((pointX - cameraX) / depth) * 0.5f + 0.5f;
   	}

   }

   int main()
   {
   	const float width = 1280.0f;
   	const std::array<float, 3> depths = { 2.0f, 4.0f, 8.0f };
   	for (const float depth : depths)
   	{
   		const float motion = ScreenX(1.0f, 0.4f, depth) - ScreenX(1.0f, 0.0f, depth);
   		std::printf("depth %.0f: %+.1f pixels\n", depth, motion * width);
   	}
   	return 0;
   }
   ```

   ```text output-of="draw-motion-vectors-parallax.cpp"
   depth 2: -128.0 pixels
   depth 4: -64.0 pixels
   depth 8: -32.0 pixels
   ```

   1. **Line 11:** the screen position of a point seen by a camera.
   2. **Line 22:** the same point asked of the current camera and of the previous one.

   Nearer points move farther, so the depth of each pixel matters. Camera-only reprojection reads that depth from the depth buffer, which is right only for points that did not move.
   :::

3. **Hard.** Trace it yourself. Find where a renderer decides that a frame has no motion history, and where the copy at the end of the frame is recorded for it.

   :::answer[Worked solution]{tests="history-copy"}
   Search `Strata/src/Strata/Renderer/SceneRenderer.cpp` for `motionHistory`: the frame sets it when the previous frame asked for motion too, and when that frame drew this render scene or the one this scene was cloned from. `SceneRenderer::RecordMotionCopy` does the copy, after the transparent pass. Put a breakpoint there and move one cube, as the test `GPU.SceneRenderer.MotionVectors` does: the list holds one instance element.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer::RecordMotionCopy` and the frame constants.
- `Strata/src/Strata/Renderer/RenderSceneGPU.h`: the write logs, `GetInstanceWrites`, `GetPaletteWrites`.
- `Strata/shaders/Scene/Mesh.vert.slang`, `Strata/shaders/Include/Motion.slang`, `Strata/shaders/Scene/MotionCopy.comp.slang`, `Strata/shaders/Overlay/MotionView.frag.slang`.
- Tests: `GPU.SceneRenderer.MotionVectors` in `StrataTests/src/Renderer/GPUSceneMotionTests.cpp`.
- Option: `SceneRenderOptions::MotionVectors`, `SceneRenderOptions::ShowMotionVectors`; statistics: `SceneRendererStats::MotionHistory`.

## Further reading

- Brian Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014: how temporal anti-aliasing uses motion (intermediate).
- Tomas Akenine-Moller and others, "Real-Time Rendering", fourth edition: the sections on motion blur and temporal anti-aliasing (intermediate).
