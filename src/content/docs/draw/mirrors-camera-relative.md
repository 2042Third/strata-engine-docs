---
id: draw/mirrors-camera-relative
title: "Mirrors, normals and camera-relative positions"
description: "How Strata keeps mirrored meshes right side out, builds normals without an inverse, and draws far from the origin without jitter."
kind: internals
size: M
tracks: [E]
needs: [draw/batching, basics/numbers, gpu/coordinates]
time: 45
learn:
  - id: mirrored-instance
    text: explain what a mirrored instance changes in the pipeline, the sort key and the shader
  - id: cofactor-normal
    text: compute a normal through the cofactor matrix and the winding of a mirrored triangle
  - id: camera-relative
    text: explain why a new pass uploads positions relative to the camera, subtracted in double
since: 0.4.0
status: final
---

Two small problems follow every scene :term[shader]{id=shader}. A mirrored mesh shows its inside, and a mesh far from the origin shakes.
Strata answers both in the same few lines of the scene vertex shader and in the pipeline state around it. This page
follows those answers from the moment a proxy is placed to the clip position of a vertex. It does not teach floating point numbers ([Numbers in a computer](../basics/numbers.md)), the 20 km limit of worlds, normal maps or the whole vertex shader: each has its own page.

## The problem and how engines solve it

A **mirrored transform** is a transform whose upper 3 by 3 part has a negative determinant: it turns a left hand into a right hand. You make one when you give an entity a scale such as $(-1, 1, 1)$. For a scale alone, the determinant is the product of the three scale factors, so an odd number of negative scales is enough, since two of them cancel.

A triangle that ran counter-clockwise on screen now runs clockwise. The :term[graphics card]{id=gpu} discards the back faces, and it decides which face is the back from that direction of travel. The mirrored mesh then loses its outside and shows its inside, with every light and shadow pointing the wrong way.

The mirror also hurts normal maps. Each vertex of a mesh with a normal map has a :term[tangent frame]{id=tangent-space}: three perpendicular directions, the normal, the tangent along the texture's horizontal direction and the :term[bitangent]{id=bitangent} along its vertical one. The map stores its normals in that frame. The mesh keeps only the normal, the tangent and one sign, and the shader rebuilds the bitangent as the :term[cross product]{id=cross-product} of the two, times the sign.

**Tangent handedness** is that sign: it says on which side of the cross product the bitangent lies. A mirror turns the frame over, so the sign must flip too.

Engines solve it in three steps. They detect the mirror from the sign of the determinant of the transform's upper 3 by
3 part. They tell the pipeline to treat clockwise as the front for those draws. They flip the sign of the tangent's
:term[handedness]{id=handedness} so that normal maps still lean the right way. Engines that skip the second step, for example by flipping
the triangle indices in a copy of the mesh, pay in memory and in time to build the copy.

The second problem is in the numbers. A 32-bit float keeps about seven digits, so the gap between neighboring values
grows with the value. At 100 km, a float steps by 7.8 mm, as the page on numbers showed. Vertices
snap to those steps from frame to frame as the camera moves, and the picture jitters.

Four approaches exist.

- **Origin rebasing** moves the whole world when the player gets far from the origin, so the player stays near
  zero. It costs a pass over every position and breaks anything that holds a world position, such as physics bodies
  and saved data. Strata does not use it.
- **Double precision** on the :term[central processing unit]{id=processor} (CPU) keeps all transforms in 64 bits. The values stay exact, but a graphics card works
  in 32 bits, so the engine must still convert before drawing.
- **Camera-relative rendering** subtracts the camera's position from everything before the card sees it. Near the
  camera the numbers are small, so the gaps are small. Strata does this.
- **Large world coordinates** give every position two floats or a float and an :term[integer]{id=integer} cell. This is exact over a vast
  range but touches every shader and every buffer.

**Origin rebasing** is the shifting of the whole world so that the player stays near the origin.

**Camera-relative rendering** is drawing every position as its offset from the camera, so that what is near the camera
has small coordinates and keeps its precision.

Strata keeps its scene transforms in float32. An entity's own origin therefore still moves in steps of about 7.8 mm at
100 km. The :term[renderer]{id=renderer} only makes sure that this coarse step is the only error: the vertices of a mesh keep their fine
shape.

## The map

The mirror flag travels from the :term[render scene]{id=render-scene} to the pipeline and the shader. The camera's offset travels from the
frame constants into the same shader.

```mermaid caption="From a placed proxy to a pixel: the mirror flag decides the sort key, the pipeline and the tangent sign, and the camera position is subtracted in the vertex shader." alt="A flow chart. A proxy placement sets a mirrored flag. The flag feeds the sort key, the graphics processing unit bucket and the instance flags. The sort key and bucket choose a pipeline with clockwise fronts. The instance flags and the camera position feed the vertex shader, which writes a relative position, a normal and a tangent."
flowchart LR
	A[UpdateProxyPlacement] -->|Mirrored flag| B[Sort key bit 59]
	A -->|Mirrored flag| C[GPU bucket bit 0]
	A -->|c_InstanceMirrored| D[InstanceData Flags]
	B --> E[GetScenePipeline]
	C --> E
	E -->|clockwise front| F[Draw]
	D --> G[Mesh.vert]
	H[GetRelativeView and CameraPosition] --> G
	G -->|relative position, normal, tangent| F
```

A mirrored instance runs on two kinds of paths. The :term[CPU]{id=processor} path sorts draws by a 64-bit key, and a bit of that key holds
the mirror flag. The path that the graphics processing unit (GPU) drives files each draw in a bucket, and the lowest bit of the bucket index holds the
flag. Both reach `GetScenePipeline`, which sets the :term[front face]{id=winding-order}.

## The contract

Each rule below has its reason.

1. **A mirroring transform sets the proxy's `Mirrored` flag when the proxy is placed.** The flag comes from the
   determinant of the upper 3 by 3 part, so no later code has to compute it again.
2. **Mirrored draws never share a batch with others.** Their key bit differs, and the pipeline's front face differs
   with it. A batch is one draw with one pipeline, so the bit must separate them.
3. **Mirrored draws use clockwise-front pipelines.** After the mirror, the outside of the mesh runs clockwise on
   screen. The convention of counter-clockwise fronts comes from [the camera and clip-space page](../gpu/coordinates.md); these draws only reverse it.
4. **A shader flips the tangent's handedness for a mirrored instance and flips the sign of its cofactor normal.** The mirror
   reverses the frame, and without the flips the normal map leans the wrong way.
5. **A shader derives normals through `TransformNormal`.** It works from the instance's rows, so the CPU computes no
   inverse and keeps no second matrix.
6. **A scene shader takes positions relative to the camera, and the CPU subtracts the camera in double.** The
   subtraction in float would round the values first and lose what the scheme saves.
7. **A pass never uploads a world position.** A light, a debug line or a piece of text 100 km out would round to steps of 7.8
   mm, and it would no longer line up with the scene drawn beside it.

:::rule
Mirrored instances need clockwise pipelines and flipped tangents. Positions that reach scene shaders are camera-relative, and the CPU does the subtraction in double. The reasons are above: a mirror reverses the winding, and a world position loses its precision on the way to a 32-bit shader. The camera's side is on [the camera and clip-space page](../gpu/coordinates.md).
:::

## A toy version

The first sketch builds the two mirror answers by hand. It makes a scale of 2 on the x axis, then the same scale with the sign flipped. For each, it prints the determinant, the normal of a slanted plane and the winding of the triangle with corners at $(0, 0)$, $(1, 0)$ and $(0, 1)$. Watch the sign of the winding and of the normal's x part.

```cpp sketch="draw-mirrors-camera-relative-mirror.cpp"
#include <cstdio>
#include <glm/glm.hpp>
#include <initializer_list>

// The normal through the cofactor matrix of the 3x3, with its sign flipped when the determinant is negative.
glm::vec3 TransformNormal(const glm::mat3& matrix, const glm::vec3& normal)
{
	const glm::vec3 sum = glm::cross(matrix[1], matrix[2]) * normal.x + glm::cross(matrix[2], matrix[0]) * normal.y + glm::cross(matrix[0], matrix[1]) * normal.z;
	return glm::determinant(matrix) < 0.0f ? -sum : sum;
}

int main()
{
	for (const float scaleX : { 2.0f, -2.0f })
	{
		const glm::mat3 matrix(glm::vec3(scaleX, 0.0f, 0.0f), glm::vec3(0.0f, 1.0f, 0.0f), glm::vec3(0.0f, 0.0f, 1.0f));
		const glm::vec3 normal = TransformNormal(matrix, glm::vec3(1.0f, 1.0f, 0.0f));
		const glm::vec3 b = matrix * glm::vec3(1.0f, 0.0f, 0.0f);
		const glm::vec3 c = matrix * glm::vec3(0.0f, 1.0f, 0.0f);
		const float winding = b.x * c.y - b.y * c.x;
		std::printf("scale %+.0f: determinant %+.0f, normal (%+.0f, %+.0f), winding %+.0f\n", static_cast<double>(scaleX),
			static_cast<double>(glm::determinant(matrix)), static_cast<double>(normal.x), static_cast<double>(normal.y), static_cast<double>(winding));
	}
	return 0;
}
```

```text output-of="draw-mirrors-camera-relative-mirror.cpp"
scale +2: determinant +2, normal (+1, +2), winding +2
scale -2: determinant -2, normal (-1, +2), winding -2
```

1. **Line 8:** the cofactor sum, one cross product of two matrix columns for each part of the normal.
2. **Line 9:** the sign flip for a negative determinant; without it the normal would point into the surface.
3. **Lines 18–20:** the winding of the transformed triangle, twice its signed area; a positive value means counter-clockwise.

The positive scale gives the normal $(1, 2)$: the plane is stretched along x, so its normal leans more toward y. The negative scale turns the triangle clockwise, with a winding of $-2$. The normal becomes $(-1, 2)$, which still points outward, now to the left.

The second sketch shows the numbers of the other problem. An instance sits at 100003 m and the camera at 100001.5 m.
A vertex lies a few mm from the instance's origin. The program places each vertex two ways and prints the
error against the exact position.

```cpp sketch="draw-mirrors-camera-relative-precision.cpp"
#include <cstdio>
#include <initializer_list>

int main()
{
	// An instance 100 km from the world's origin and a camera 1.5 m from it: both exact as 32-bit floats.
	const float translation = 100003.0f;
	const float camera = 100001.5f;
	std::printf("vertex  world-space error  camera-relative error (millimeters)\n");
	for (const float local : { 0.001f, 0.002f, 0.004f, 0.006f, 0.008f })
	{
		const float world = translation + local;
		const float worldError = (world - camera - 1.5f - local) * 1000.0f;
		const float relative = (translation - camera) + local;
		const float relativeError = (relative - 1.5f - local) * 1000.0f;
		std::printf("%.3f   %+.3f              %+.3f\n", static_cast<double>(local), static_cast<double>(worldError),
			static_cast<double>(relativeError));
	}
	return 0;
}
```

```text output-of="draw-mirrors-camera-relative-precision.cpp"
vertex  world-space error  camera-relative error (millimeters)
0.001   -1.000              +0.000
0.002   -2.000              -0.000
0.004   +3.812              -0.000
0.006   +1.812              +0.000
0.008   -0.188              +0.000
```

1. **Lines 12–13:** the world-space way: the vertex joins the translation first, and the sum rounds to a step of 7.8 mm.
2. **Lines 14–15:** the camera-relative way: the exact difference of translation and camera comes first, and the small vertex offset joins it.

The world-space column jumps between whole steps of 7.8 mm and never shows the 2 mm vertices. The camera-relative column stays within a tiny fraction of 1 mm. Strata does the second, because it subtracts the camera from the translation while both are still exact.

:::example
A worked case with real numbers. A prop sits 100 km out, and its triangle has corners 0.004 m apart on one axis. In :term[world space]{id=world-space} the float spacing at 100 km is 0.0078125 m, since $2^{16} \le 100000 < 2^{17}$ gives a step of $2^{16-23} = 2^{-7}$.

Both corners round to the same value or to neighbors a whole step apart, so the triangle's width is 0 or 7.8 mm. In camera-relative space the corner is the instance's offset (1.5 m, exact) plus 0.004 m. A float holds that sum with a step of about 0.0001 mm, so the triangle keeps its shape.

For the mirror, take the scale $(-2, 1, 1)$ and the normal $(1, 1, 0)$ of a plane. The columns of the matrix are $(-2,0,0)$, $(0,1,0)$ and $(0,0,1)$. Their cross products in pairs give $(1,0,0)$, $(0,-2,0)$ and $(0,0,-2)$. The weighted sum is $(1, -2, 0)$.

The determinant is $-2$, so the shader flips the sign to $(-1, 2, 0)$. A tangent of the plane, $(1, -1, 0)$, becomes $(-2, -1, 0)$. The product $(-1)(-2) + (2)(-1) = 0$ shows that the new normal stands perpendicular to it.
:::

## The real code

The real code differs from the toy in where each decision lives. The sign is read when the proxy is placed. Every later
stage reads a flag. The page on [the render scene's GPU copy](render-scene-gpu.md) shows how the flag reaches the shader.

### Placement

`UpdateProxyPlacement` runs when a proxy's transform changes. Search for the line that computes the determinant and the
line that sets the flag. A proxy whose determinant is almost zero or not finite shows nothing, so a flat scale never
reaches the shader.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L666-L675"
const glm::mat4 world = m_Transforms[proxy].ToMatrix();
const float determinant = glm::determinant(glm::mat3(world));
const bool active = (m_Flags[proxy] & RenderProxyFlags::Active) != 0;
const uint32_t meshSlot = m_MeshSlots[proxy];
const MeshEntry* mesh = meshSlot != c_InvalidIndex ? &m_Meshes[meshSlot] : nullptr;

uint32_t flags = m_Flags[proxy] & (RenderProxyFlags::Active | RenderProxyFlags::CastShadows | RenderProxyFlags::Skin | RenderProxyFlags::Skinned
	| RenderProxyFlags::LightSurface);
if (determinant < 0.0f)
	flags |= RenderProxyFlags::Mirrored;
```

1. **Lines 672–673:** The new flags keep only what the proxy already carried, so a mirror bit from an earlier placement never lingers.

The flag later copies into `InstanceData::Flags` as `c_InstanceMirrored`. A new proxy draws once its upload has arrived.

### Pipeline state

`GetScenePipeline` builds the pipeline for a batch from a key that holds the mirror bit. The next quote shows how the
front face and the culling follow from it. A double-sided material turns culling off, and a mirrored instance only
changes which winding counts as the front.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2558-L2564"
// Front faces are counter-clockwise; a mirroring transform reverses the winding on screen, and so do the back faces' passes
// (they cull the front faces).
desc.renderState.rasterState.setFrontCounterClockwise(key.Mirrored == backFacePass);
if (key.DoubleSided)
	desc.renderState.rasterState.setCullNone();
else
	desc.renderState.rasterState.setCullBack();
```

The toy had no pipeline. Here a key with `Mirrored` set means a clockwise front. The back faces' pass of a local light's shadow flips the front once more, so a mirrored mesh there counts its counter-clockwise faces as the front again. A mirrored and an ordinary mesh never share a pipeline, which is what the key bit and the bucket bit guarantee.

### The two shader functions

The first function places a point. It takes the instance's translation, subtracts the camera, and only then adds the
rotated and scaled vertex. The subtraction happens while the translation is still a plain world value, and the result
is small when the instance is near the camera.

```slang src="Strata/shaders/Include/Scene.slang#L254-L260"
// A point of the instance in camera-relative world space: the instance's translation minus the camera's position is taken
// before anything is added to it, so vertices near the camera keep full precision far from the world's origin.
float3 TransformPositionRelative(InstanceData instance, float3 position)
{
	float3 translation = float3(instance.WorldRows[0].w, instance.WorldRows[1].w, instance.WorldRows[2].w) - u_Frame.CameraPosition.xyz;
	return float3(dot(instance.WorldRows[0].xyz, position), dot(instance.WorldRows[1].xyz, position), dot(instance.WorldRows[2].xyz, position)) + translation;
}
```

The vertex stays in the instance's :term[local space]{id=local-space} until this call, and a local position is small. So the only large
numbers are the translation and the camera, and their difference is exact for anything near the camera. This is the
step that the toy's second column did.

The second function carries a normal. Its three columns come from the instance's rows, and each pair of columns gives a cross product. The sum weights those products by the parts of the normal.

The result is the :term[cofactor matrix]{id=cofactor-matrix} of the upper 3 by 3 part, applied to the normal. It equals the inverse :term[transpose]{id=transpose} of the matrix times the determinant, so the direction is right under any scale and only the length is off. [The page on bases](../basics/math-bases.md) derives this. The caller :term[normalizes]{id=normalization}, and a negative determinant flips the sign of the whole result, as in the toy.

```slang src="Strata/shaders/Include/Scene.slang#L270-L277"
float3 TransformNormal(InstanceData instance, float3 normal)
{
	float3 column0 = float3(instance.WorldRows[0].x, instance.WorldRows[1].x, instance.WorldRows[2].x);
	float3 column1 = float3(instance.WorldRows[0].y, instance.WorldRows[1].y, instance.WorldRows[2].y);
	float3 column2 = float3(instance.WorldRows[0].z, instance.WorldRows[1].z, instance.WorldRows[2].z);
	float3 transformed = cross(column1, column2) * normal.x + cross(column2, column0) * normal.y + cross(column0, column1) * normal.z;
	return (instance.Flags & ST_INSTANCE_MIRRORED) != 0u ? -transformed : transformed;
}
```

The flag costs one bit test per vertex. A uniform scale pays the same as a skewed one, since the shader builds the matrix from the rows either way.

### The vertex shader

`Mesh.vert` calls both functions. Read the lines in order: the relative position, the normal, then the tangent's
sign. The sign multiplies two factors, the mesh's own tangent sign and the mirror's.

```slang src="Strata/shaders/Scene/Mesh.vert.slang#L50-L56"
float3 relativePosition = TransformPositionRelative(instance, position);
v_RelativePosition = relativePosition;
v_Normal = normalize(TransformNormal(instance, normal));
// A mirroring transform reverses the handedness of the tangent frame: cross(N, T) then points opposite to the
// transformed bitangent, so its sign flips.
float handedness = (a_Tangent.w < 0.0 ? -1.0 : 1.0) * ((instance.Flags & ST_INSTANCE_MIRRORED) != 0u ? -1.0 : 1.0);
v_Tangent = float4(normalize(TransformDirection(instance, tangent)), handedness);
```

The tangent's direction goes through `TransformDirection`, which uses the rows without a translation. Only its sign
needs the mirror test. The page on [the geometry pool](../gpu/geometry-pool.md) reads the rest of the shader from the :term[draw list]{id=draw-list} to the clip
position; skinning and velocity have their own pages.

The same function builds a previous-frame position for motion vectors. It subtracts the camera from the previous
instance's translation too, so the previous position keeps the same precision as this one.

```slang src="Strata/shaders/Scene/Mesh.vert.slang#L76-L81"
float3 previousRelative = relativePosition;
if (sameEntity && (any(previous.WorldRows[0] != instance.WorldRows[0]) || any(previous.WorldRows[1] != instance.WorldRows[1])
	|| any(previous.WorldRows[2] != instance.WorldRows[2]) || any(previousPosition != position)))
	previousRelative = TransformPositionRelative(previous, previousPosition);
v_CurrentClip = mul(u_Frame.UnjitteredViewProjection, float4(relativePosition, 1.0));
v_PreviousClip = mul(u_Frame.PreviousViewProjection, float4(previousRelative, 1.0));
```

The shader computes the previous position again only where the instance changed. Otherwise it takes the current value again, so unchanged vertices show no motion however two roundings fall. The page on [motion vectors](motion-vectors.md) teaches the rest, and [skinned meshes](skinned.md) the pose part.

### The CPU side of the rule

The shader gets a relative position from the matrices, and the view matrices have the camera's translation removed.
`GetRelativeView` keeps only the 3 by 3 rotation of the camera's view. Everything the CPU uploads in world terms must
agree with it. The debug lines show how: each vertex is converted to double, the camera subtracted, and the result
rounded to float.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L4322-L4327"
// Camera-relative, as the scene's shaders draw (the subtraction in double for lines far from the origin).
m_DebugLineScratch.assign(tested.begin(), tested.end());
m_DebugLineScratch.insert(m_DebugLineScratch.end(), onTop.begin(), onTop.end());
const glm::dvec3 cameraPosition(camera.Position);
for (DebugLineVertex& vertex : m_DebugLineScratch)
	vertex.Position = glm::vec3(glm::dvec3(vertex.Position) - cameraPosition);
```

The same rule applies to light positions, the clusters' light bounds, text and canvases in the world, and the boxes of
the sun's cascades. The culling shader tests boxes that are relative too. The CPU's :term[spatial index]{id=spatial-index} stays in
world space, and so do the screen-size and level-of-detail measures; both paths agree because they measure distances,
not absolute positions.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Origin rebasing | Games that shift the world under the player | Small numbers everywhere, including physics | A pass over every position, and stored world positions must change with it |
| Double-precision transforms on the CPU | Games with very large worlds | Exact entity origins at any distance | Twice the memory for transforms, and the graphics card still needs a conversion |
| Large world coordinates | Games with very large worlds | Exact positions without moving the world | Every shader and buffer that holds a position changes |
| Flipping triangle indices for mirrored meshes | Tools that bake a mirror into a mesh | No change to the pipeline | A second copy of each mirrored mesh |

## How it is tested

A case of the suite `GPU.SceneRenderer.CameraRelative` renders one scene three times: at the origin, then moved by 20 km and by 100 km along both the x and the z axis. A second case, in `StrataTests/src/Renderer/GPUSceneMotionTests.cpp`, checks that the screen motion of a scene 20 km out is as exact as at the origin.

The scene holds a finely cut sphere, a ground with a pattern of squares, the sun with shadows and a point light. The camera stands about a meter and a half away, so a pixel spans about 7 mm. The test passes when at least 99.9 % of the pixels of each far image are within 2 of 255 of the origin's image. It runs with GPU-driven drawing in automatic mode and with it off.

The suite `GPU.SceneRenderer.GPUDriven` holds a case that draws meshes, masks and mirrors on both paths and compares them.

Run a suite with a GPU, through a filter on its name.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.CameraRelative
```

The runner prints each failing check and ends with a summary line that counts the cases and the checks.

## Changing it safely

- **A new pass that places positions** takes them relative to the camera, subtracts in double on the CPU and uses
  `GetRelativeView`. Reason: one pass that uploads a world position shows jitter far out while all others look fine.
- **A new shader that carries normals** calls `TransformNormal` and normalizes. Reason: the cofactor matrix makes the
  direction right under any scale, and the mirror's sign flip lives there.
- **A new pipeline that draws instances** takes its front face from the key's `Mirrored` field. Reason: a mirrored
  mesh would otherwise show its inside.
- **A new per-instance flag** goes in the flags word, with its bit in the :term[sort key]{id=sort-key} or bucket when it changes the
  pipeline. Reason: batches must not share state.
- **Checks to pass:** `GPU.SceneRenderer.CameraRelative` and `GPU.SceneRenderer.GPUDriven`, then the whole suite.

## Summary

- A mirrored instance has a negative determinant. Strata marks the proxy when it is placed, gives the draw its own sort
  key bit and bucket bit, draws it with clockwise fronts and flips the tangent's sign in the vertex shader.
- Normals come from the cofactor matrix of the instance's rows, with its sign flipped for a mirrored instance, with no inverse on the CPU.
- Scene shaders work relative to the camera. The vertex shader subtracts the camera from the instance's translation
  first, and the CPU subtracts uploaded positions in double.

## Check yourself

1. A mesh is placed with scale $(1, 1, -1)$. Which of these is wrong? (a) Its proxy gets the `Mirrored` flag. (b) Its
   draws use a clockwise-front pipeline. (c) Its triangles keep their counter-clockwise winding on screen.
   :::answer{tests="mirrored-instance"}
   Option (c) is wrong. The mirror reverses the winding on screen, which is why (b) is needed. Option (a) is right
   because the determinant is $-1$.
   :::
2. A scale $(3, 1, 1)$ is applied to the normal $(1, 1, 0)$. What does `TransformNormal` return?
   :::answer{tests="cofactor-normal"}
   The columns are $(3,0,0)$, $(0,1,0)$ and $(0,0,1)$, so the products are $(1,0,0)$, $(0,3,0)$ and $(0,0,3)$. The sum
   is $(1, 3, 0)$, and the determinant $3$ is positive, so it stays. The caller normalizes it.
   :::
3. A light is 100 km out and its position is uploaded as float32 without subtraction. What happens?
   :::answer{tests="camera-relative"}
   The position rounds to a step of 7.8 mm before the shader sees it, so the light moves in jumps as the camera
   moves, and it no longer matches the geometry drawn camera-relative. Subtracting in double first fixes both.
   :::
4. Why must the subtraction for a debug line happen in double and not in float?
   :::answer{tests="camera-relative"}
   A float already rounded the vertex to 7.8 mm before the subtraction, so the error is kept. In double the difference
   is exact, and the rounding to float happens after, on a small number.
   :::

## Exercises

1. **Basic.** Find where a draw's sort key gets its mirror bit. Use a search, not memory.
   :::answer[Worked solution]{tests="mirrored-instance"}
   Search for `SceneDrawKey::Make(`. The CPU path calls it in `SceneRenderer::GatherDraws`, in
   `Strata/src/Strata/Renderer/SceneRendererExtraction.cpp`, passing the draw's mirror flag. The key places it at bit
   59, `c_MirroredShift` in `Strata/src/Strata/Renderer/SceneDrawKey.h`.
   :::
2. **Medium.** Compute the float spacing at 50 km, and say what a vertex 3 mm from the camera does in float32 world
   space.
   :::answer[Worked solution]{tests="camera-relative"}
   Since $2^{15} \le 50000 < 2^{16}$, the spacing is $2^{15-23} = 2^{-8}$ m, about 3.9 mm. A vertex 3 mm from the
   camera, at 50 000.003 m, rounds to the nearest step, 50 000.0039 m, so it is drawn 0.9 mm off. As the camera moves, that error changes by up to half a step, about 2 mm, and the vertex jumps.
   :::
3. **Hard.** Audit a debug line 100 km out. Write a sketch that subtracts the camera in float and in double and prints
   both.
   :::answer[Worked solution]{tests="camera-relative"}
   The sketch below holds a line end 3 mm past the camera. Subtracting in float gives the wrong value; subtracting in
   double gives about 3 mm, as `SceneRenderer.cpp` does when it uploads debug lines.

   ```cpp sketch="draw-mirrors-camera-relative-audit.cpp"
   #include <cstdio>
   #include <initializer_list>

   int main()
   {
   	// A debug line end 100 km out, 3 mm beyond the camera's position along one axis.
   	const double cameraX = 100000.0;
   	const double lineX = 100000.003;
   	const float floatCamera = static_cast<float>(cameraX);
   	const float floatLine = static_cast<float>(lineX);
   	const float subtractedInFloat = floatLine - floatCamera;
   	const float subtractedInDouble = static_cast<float>(lineX - cameraX);
   	std::printf("float minus float:   %.4f m\n", static_cast<double>(subtractedInFloat));
   	std::printf("double, then float:  %.4f m\n", static_cast<double>(subtractedInDouble));
   	return 0;
   }
   ```

   ```text output-of="draw-mirrors-camera-relative-audit.cpp"
   float minus float:   0.0000 m
   double, then float:  0.0030 m
   ```

   1. **Line 11:** the float subtraction: both ends already rounded to 7.8 mm steps, so the 3 mm are gone.
   2. **Line 12:** the double subtraction, exact, then one rounding to float, as the renderer does for debug lines.
   :::

## Where it lives in Strata

- Placement: `RenderScene::UpdateProxyPlacement` in `Strata/src/Strata/Renderer/RenderScene.cpp`.
- Sort key and buckets: `Strata/src/Strata/Renderer/SceneDrawKey.h`, `Strata/src/Strata/Renderer/GPUSceneData.h`.
- Pipeline: `GetScenePipeline` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`.
- Shader: `Strata/shaders/Include/Scene.slang` and `Strata/shaders/Scene/Mesh.vert.slang`.
- Tests: `GPU.SceneRenderer.CameraRelative`, `GPU.SceneRenderer.GPUDriven`.

## Further reading

- A graphics textbook on transforms and normals: what the inverse transpose is, advanced.
- A graphics course on floating point precision: where the error comes from, intermediate.
