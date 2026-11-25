---
id: animation/skinning
title: "Skinning"
description: "How a skeleton's pose bends a mesh: bind pose, inverse bind matrices, weighted influences, the palette, normals, and why Strata blends linearly."
kind: concept
size: L
tracks: [E]
needs: [animation/skeletons, draw/skinned]
time: 60
learn:
  - id: skin-vertex
    text: compute the skinned position of a vertex that two joints influence, by hand
  - id: palette-matrices
    text: name the three matrices of a palette entry and the space each one leaves and enters
  - id: normal-cofactor
    text: explain why a skinned normal goes through the cofactor of the blended matrix
  - id: models-compare
    text: compare rigid binding, linear blend skinning and dual quaternion skinning by artifact and cost
  - id: strata-palette
    text: trace how Strata builds a palette entry from the animator's pose and its drawn transform
since: 0.3.0
status: final
---

A character's arm is modelled once, held straight, with its elbow where an artist put it. Then the game plays a clip in which the elbow bends. The skeleton knows how: [Skeletons and forward kinematics](skeletons.md) describes joints that move in a pose. The mesh knows nothing. It is a cloud of points, thousands of them, each sitting where it was modelled, and no point has heard that an elbow moved.

**Skinning** is the step that connects the two: it moves every vertex of a mesh according to the joints of a skeleton, so that the surface follows the bones. This page builds that step from the beginning. It ends with the matrices that Strata's :term[renderer]{id=renderer} computes for each posed mesh, which [Skinned meshes in the renderer](../draw/skinned.md) takes as given, and with a vertex that you can move by hand.

The pose the skeleton publishes lives in the space of the animator, the entity that carries the Animator component (the page [Importing animation](../animation/importing.md) teaches it). Read it as "the robot's own coordinates". The mesh was modelled in yet another space, so the first job is to relate the two.

## One joint per vertex tears the surface

The simplest answer gives every vertex one master joint. When the joint moves, its vertices move with it, rigidly, as if glued to a bone. Engines call this **rigid binding**, and it is how a car's wheel or a sword in a hand is attached: the wheel is one object that follows one joint.

Try it on the elbow. Put the shoulder joint at the origin and the elbow joint one unit above it, and model the arm as a tube along the vertical axis, 0.2 units from the axis. Take two neighbouring points of the tube, A at height 0.95 and B at height 1.05, 0.1 units apart. A belongs to the shoulder joint, because it is below the elbow, and B belongs to the elbow joint.

Now bend the elbow by a quarter turn, counterclockwise, so that the forearm leans to the left. A does not move, because the shoulder does not move. B turns about the elbow: it was 0.05 above the elbow and 0.2 to the right of the axis, and it ends 0.2 above the elbow and 0.05 to the left of the axis. A stays at (0.2, 0.95); B lands at (-0.05, 1.2). The two points that touched are now 0.35 units apart, 3.5 times the gap they had, and the triangles between them stretch into a visible crack.

A real character has this crack at every elbow, knee and shoulder, and a soft surface such as skin or cloth cannot afford it. Skinning needs a rule under which the points near a joint move part of the way with each of its neighbours. Before that rule, you need the three matrices that put a vertex where a joint says it goes.

## Three matrices carry a vertex from the model into the pose

A vertex is stored where it was modelled, with the skeleton held in one fixed arrangement. This arrangement is the **bind pose**: the pose in which the mesh was attached to the skeleton, so the pose in which no vertex has to move. In a bind-pose arm the forearm points up; the vertex data and every joint's place are measured in that arrangement.

A joint does not tell you where a vertex goes. It tells you where the joint is now. To use it, you first ask: where is this vertex relative to the joint? That is a position in the joint's own space, and it is the same in every pose, because the vertex does not slide along its bone. The matrix that takes a vertex from the mesh's space in the bind pose into one joint's space is that joint's **inverse bind matrix**: the inverse of the joint's own transform at bind time.

Then the pose moves the joint. The skeleton gives, for each joint, a transform that takes the joint's own space into the animator's space: the joint's posed model transform. Applying it to the vertex in joint space puts the vertex where the joint now carries it, measured in the animator's space.

One step is left, because the animator and the drawn mesh are different entities. The mesh is drawn by a proxy, a record the renderer keeps for it, with its own placement. The pose is relative to the animator, so a last matrix takes animator space into proxy space. Strata calls it `AnimatorToProxy`; it is the inverse of the proxy's :term[world transform]{id=world-transform} times the animator's world matrix. For a mesh on the animator itself, it is the identity.

Joining the three gives one matrix per joint. The list of these matrices, one for each joint that the mesh uses, is the **skinning palette**; the renderer computes it on the processor for each posed mesh and the graphics hardware reads it.

```mermaid caption="A vertex travels from the bind pose into one joint's space, out to the animator's space with the posed joint, and into the drawn mesh's space. The three matrices multiplied are one palette entry." alt="A chain of four boxes joined by three arrows. The first box is the vertex in the bind space of the mesh. The first arrow, labelled inverse bind matrix, leads to the vertex in the joint's space. The second arrow, labelled posed model transform of the joint, leads to the vertex in the animator's space. The third arrow, labelled animator to proxy, leads to the vertex in the drawn mesh's space."
flowchart LR
    A["Vertex in bind space"] -->|"inverse bind matrix B"| B["Vertex in joint space"]
    B -->|"posed model transform P"| C["Vertex in animator space"]
    C -->|"AnimatorToProxy A"| D["Vertex in proxy space"]
```

Read the diagram from left to right and the matrices from right to left, as in any product of matrices. The entry of joint $j$ is

$$M_j = A \, P_j \, B_j$$

In this formula $M_j$ is the palette entry of joint $j$ (a 4 by 4 matrix). $A$ is the matrix from the animator's space to the proxy's space, $P_j$ is the posed model transform of joint $j$, and $B_j$ is its inverse bind matrix. The product is read from the right: first $B_j$ acts on the vertex, then $P_j$, then $A$. The vertex stands on the right of the whole expression, which is why the nearest matrix acts first.

Check the limits. If the pose is the bind pose, then $P_j$ is the inverse of $B_j$, the two cancel, and $M_j = A$: the vertex stays where it was, apart from the placement. If a vertex is exactly at its joint's origin in the bind pose, the matrix moves it exactly to where the pose puts that joint. Both limits match what a skeleton should do.

A mesh does not store a matrix per joint of the whole skeleton. It stores a **skin** (a glTF word; also called a skin binding), the list of joints that bend this mesh, each with its inverse bind matrix. A character may have 70 joints and a skin that names 55 of them. The palette has one entry per joint of the skin, and the skin says which skeleton joint each entry follows.

:::note
The inverse bind matrix is a constant: it comes from the file and never changes while the game runs. The posed model transform changes with every frame of a clip. The third matrix changes whenever the animator or the mesh is drawn somewhere else. A palette entry therefore changes when any of the three changes, which is why the renderer watches all three ([Skinned meshes in the renderer](../draw/skinned.md) teaches when it computes the palette again).
:::

## A vertex follows up to four joints with weights

A palette entry tells you where a vertex would go if one joint owned it. Now give the elbow's neighbourhood a rule. A vertex that sits right at the elbow follows the shoulder and the forearm equally; a vertex a little way down the forearm follows the forearm mostly. Each joint that moves a vertex is an **influence**, and each influence has a weight, the share of the vertex that follows it. The weights of a vertex are fractions that add up to 1.

**Linear blend skinning** (LBS) is the rule that makes this concrete: the skinned vertex is the weighted sum of the positions that each influence alone would give. In symbols,

$$v' = \sum_{i=1}^{4} w_i \, M_i \, v$$

Here $v$ is the vertex in bind space (extended to four numbers, with 1 as the last) and $v'$ is the skinned vertex. The counter $i$ runs over the influences from 1 to 4, $w_i$ is the weight of influence $i$, and $M_i$ is the palette entry of the joint that influence $i$ names. Read the sum sign as "add up the terms for $i$ equal to 1, then 2, then 3, then 4".

Because the matrix product is linear in its matrix, you may add the weighted matrices first and apply the sum to the vertex once: $v' = (\sum w_i M_i) \, v$. The :term[shader]{id=shader} does exactly that, so a vertex costs one blended matrix and one product, however many influences it has.

Four is the number Strata keeps. It is enough for almost every real vertex, because a point rarely lies between more than two or three bones, and four fit exactly in a small record. The record, in the engine's mesh :term[header]{id=header}, stores four 16-bit joint indices and four 16-bit weights per vertex, and describes the skin beside it.

```cpp src="Strata/src/Strata/Renderer/Mesh.h#L28-L56"
// The skinning data of a vertex (stream 2 of skinned meshes): four influences, each a joint of the mesh's skin (an index
// into MeshSkinBinding::Joints) and its weight in 1/65535ths. The weights of a vertex add up to 65535; unused influences
// have weight 0.
struct MeshSkinVertex
{
	uint16_t Joints[4] = { 0, 0, 0, 0 };
	uint16_t Weights[4] = { 65535, 0, 0, 0 };
};
static_assert(sizeof(MeshSkinVertex) == 16, "MeshSkinVertex layout is part of the cooked mesh format and the skinned vertex input");

// How a skinned mesh is bound to its skeleton (one glTF skin): for each joint of the skin, the skeleton joint that moves
// it, its inverse bind matrix (from the mesh's space into the joint's space at bind time) and the bind-pose extent of the
// vertices it influences (empty for joints that influence none). The skinning palette of a posed instance holds, per skin
// joint, the joint's model-space transform times its inverse bind matrix; the vertex shader blends the palette entries
// of a vertex's influences. A posed instance's bounds are the union of each joint's extent transformed by its palette
// entry: every skinned vertex is a weighted average of points inside those boxes.
struct MeshSkinBinding
{
	static constexpr uint32_t c_MaxJoints = 4096;

	std::vector<uint16_t> Joints;               // Skeleton joint of each skin joint
	std::vector<glm::mat4> InverseBindMatrices; // Affine, per skin joint
	std::vector<AABB> JointBounds;              // Per skin joint, in the mesh's (bind) space; computed by Mesh::CreateSkinned
	// The farthest a vertex lies from the origin of a joint that influences it, in that joint's space (its inverse bind
	// matrix times the vertex): in any pose, the skinned vertices lie within this distance (times the joints' scale) of
	// their joints' origins. Bounds where joints may go, not where they are (SkeletonPose::Reach), grow by it. Computed by
	// Mesh::CreateSkinned.
	float MaxJointExtent = 0.0f;
};
```

1. **Line 31:** the record of one vertex: 16 :term[bytes]{id=byte}, which line 36 asserts, because the cooked mesh format and the vertex input depend on it.
2. **Lines 33–34:** four joint indices and four weights; the defaults give one influence of full weight on joint 0.
3. **Line 44:** the skin of one mesh.
4. **Lines 48–50:** one entry per skin joint: the skeleton joint that moves it, its inverse bind matrix and the box of the vertices it influences, in bind space.
5. **Line 55:** one number for the whole skin, the farthest a vertex lies from a joint that influences it; the page on animation culling uses it.

Two details of the record matter later. A weight is a whole number of 65535ths, so that 16 bits store it without a floating-point value. The weights of a vertex must add up to 65535, and creating a mesh whose weights add up to anything else fails. An unused influence has weight 0, but it still holds a joint index, and the index must name a joint of the skin. That rule has a reason you meet in the shader below.

A glTF file may give a vertex more than four influences, in sets of four. The :term[importer]{id=importer} reads up to two sets, eight influences, keeps the four strongest and scales their weights back to a sum of 65535 ([Importing animation](../animation/importing.md) describes how).

:::example[Skinning one vertex between two joints by hand]
Take the arm of the last section, in its bind pose. Joint 0 is the shoulder at the origin; joint 1 is the elbow at (0, 1, 0). The vertex is $v = (0.2, 1.1, 0)$, a little above the elbow and to the right of the axis. It has two influences: joint 0 with weight 16384 and joint 1 with weight 49151. As fractions, those are 0.25 and 0.75 (each off by a tiny rounding, far below what the eye sees).

The pose bends the elbow by a quarter turn counterclockwise about the z axis and leaves the shoulder alone. Take the animator and the proxy to be the same entity, so $A$ is the identity and drops out.

Joint 0: the inverse bind matrix is the identity, and so is the pose. The palette entry is the identity, so the vertex stays at $(0.2, 1.1, 0)$.

Joint 1: its inverse bind matrix moves the vertex down by 1, to $(0.2, 0.1, 0)$. The pose turns the vertex a quarter turn counterclockwise, which sends $(x, y)$ to $(-y, x)$: it becomes $(-0.1, 0.2, 0)$. Then the pose carries the elbow up by 1 again: $(-0.1, 1.2, 0)$.

The blend adds 0.25 times the first result to 0.75 times the second. For x: $0.25 \cdot 0.2 + 0.75 \cdot (-0.1) = 0.05 - 0.075 = -0.025$. For y: $0.25 \cdot 1.1 + 0.75 \cdot 1.2 = 0.275 + 0.9 = 1.175$. The skinned vertex is $(-0.025, 1.175, 0)$.

Look at where it lies. The shoulder alone would leave it at (0.2, 1.1) and the elbow alone would move it to (-0.1, 1.2). The result sits between them, three quarters of the way toward the elbow's answer, exactly as the weights say. This is the smooth skin that rigid binding could not make. The exercises at the end let you check the numbers by program.
:::

## Normals do not move like positions

A mesh has more than points. Every vertex carries a normal, the direction its surface faces, and lighting reads it. After skinning, the normal must still face away from the surface. The obvious move is to push it through the same blended matrix as the position, and that is wrong whenever the matrix scales its axes by different amounts (a stretched arm, a squashed spine).

Take the matrix that stretches x by 2 and leaves y and z alone, and a surface that runs at 45 degrees, with the normal $(1, 1, 0)$. The surface runs along $(1, -1, 0)$; stretched, it runs along $(2, -1, 0)$, closer to the x axis, so its normal must turn toward y. The plain matrix gives $(2, 1, 0)$, which leans toward x, and the lighting turns the wrong way. The right answer is proportional to $(1, 2, 0)$: its :term[dot product]{id=dot-product} with $(2, -1, 0)$ is $2 - 2 = 0$, so it stands perpendicular to the stretched surface.

The fix is the **cofactor matrix**: the matrix of the :term[cross products]{id=cross-product} of the columns of the 3 by 3 part, which is the inverse :term[transpose]{id=transpose} of that part times its determinant.

Its columns are $c_1 \times c_2$, $c_2 \times c_0$ and $c_0 \times c_1$ when the matrix has columns $c_0$, $c_1$ and $c_2$. The symbol $\times$ is the cross product. Try the stretch: the columns are $(2,0,0)$, $(0,1,0)$ and $(0,0,1)$. The new columns are $(0,1,0) \times (0,0,1) = (1,0,0)$, $(0,0,1) \times (2,0,0) = (0,2,0)$ and $(2,0,0) \times (0,1,0) = (0,0,2)$. Applied to $(1,1,0)$ they give $(1, 2, 0)$, the right answer.

Dividing by the determinant to get the true inverse transpose is unnecessary here: the shader :term[normalizes]{id=normalization} the result afterwards, which removes any positive scale. The sign is another matter. A matrix with a negative determinant mirrors the mesh, and the cofactor of a mirror points the wrong way, so the shader flips the sign in that case.

The same blended matrix also moves directions that are not normals, such as a surface's tangent. A tangent runs along the surface, so it moves like a position's difference: the plain 3 by 3 part, with no translation. The shader offers a function for each use, shown later.

## How engines bend a mesh, and what each model gets wrong

Rigid binding is the cheapest model: one matrix per vertex, one multiplication. Its flaw is the crack you computed. It is still right where a thing really is rigid: a weapon in a hand, a wheel on a car, a sword on a belt. Engines attach such parts to joints without any blend.

Linear blend skinning is the next step, and the answer in most real-time engines. Its flaw is that it blends positions, and an average of two points lies inside the segment between them. Take the vertex at $(0.2, 0, 0)$ on the surface of a forearm, 0.2 from the bone's axis. Twist the wrist by half a turn about the bone axis while the elbow end stays still.

The twisted joint sends the vertex to $(-0.2, 0, 0)$. With weights 0.5 and 0.5 the blend is the middle point of $(0.2, 0, 0)$ and $(-0.2, 0, 0)$: the origin, on the axis. The tube's radius shrinks to zero at the middle of the twist.

The forearm pinches like a twisted sleeve. Engines call this artifact the twist collapse. A smaller twist loses less: a quarter turn leaves 71 % of the radius.

**Dual quaternion skinning** removes the collapse by blending rotations instead of positions. Each joint's rigid motion, a rotation and a translation, is stored in a dual :term[quaternion]{id=quaternion}; the blend of these keeps the result a rigid motion, so the volume near a twist is kept. It costs more: eight numbers per joint instead of a 3 by 4 matrix, a normalization of the blend for every vertex, and scales that need another treatment, because a dual quaternion holds no scale. Its own flaw is a bulge at bent joints, where a limb swells slightly.

| Model | Cost per vertex | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Rigid binding | One matrix | Cracks at every joint | Lowest | Props, weapons, vehicle parts |
| Linear blend skinning | A weighted sum of up to four matrices | Smooth bends; twist collapse | Low | The glTF format and most real-time engines |
| Dual quaternion skinning | A weighted sum of dual quaternions, then a normalization | No collapse; a bulge at bends; no scale | Moderate | Engines and tools that offer it as an option |

Sources: the paper on dual quaternions and the glTF specification, both in the list of further reading, give the dual-quaternion model and the rule of the glTF format. Where skinning runs (on the processor, in the vertex shader, or in a pass of its own that writes new vertices) is a separate choice, which [Skinned meshes in the renderer](../draw/skinned.md) explains.

## Strata blends linearly on the graphics card, from palettes made on the processor

Strata uses linear blend skinning, per draw, in the vertex shader. For each posed mesh the processor computes the palette once and the card reads it; no new vertices are stored. The first piece is the palette loop in `RenderScene::ComputePalette`.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1344-L1349" from="for (size_t joint = 0; joint < skin.Joints.size(); joint++)" to="outBounds.Expand(skin.JointBounds[joint].Transformed(matrix));" symbol="RenderScene::ComputePalette"
for (size_t joint = 0; joint < skin.Joints.size(); joint++)
{
	// Fourth rows stay 0, 0, 0, 1: every factor is affine.
	const glm::mat4 matrix = pose.AnimatorToProxy * pose.Joints[skin.Joints[joint]] * skin.InverseBindMatrices[joint];
	outPalette[joint] = RenderData::AffineTransform::FromMatrix(matrix);
	outBounds.Expand(skin.JointBounds[joint].Transformed(matrix));
```

The product on the loop's first line is the formula from earlier: `AnimatorToProxy` is $A$, the pose of the skeleton joint that the skin names is $P_j$, and the skin's inverse bind matrix is $B_j$. The palette keeps three rows of each matrix, because every factor is affine (its last row is 0, 0, 0, 1), so the fourth row is known and not stored. That saves a quarter of the memory and :term[bandwidth]{id=bandwidth}. The last line of the loop grows the :term[posed bounds]{id=posed-bounds}; that belongs to the page on skinned meshes, which also teaches when the loop runs.

Where do the three inputs come from? The function `RenderScene::EvaluatePose` gathers them for one proxy. It finds the animator that the mesh's skin names, asks the :term[scene service]{id=scene-service} `ISkinningPoses` for the animator's pose, and reads the animator's transform.

```cpp src="Strata/src/Strata/Renderer/RenderScene.cpp#L1316-L1326" from="// Where the animator is drawn" to="inputs.AnimatorToProxy = InverseAffine(proxyWorld) * animatorMatrix;" symbol="RenderScene::EvaluatePose"
// Where the animator is drawn (between fixed steps while the scene interpolates), as its proxy is: against its world
// transform an interpolated skin would be posed back to its simulated place.
const glm::mat4* drawnAnimator = m_Scene->FindDrawnTransform(inputs.Animator);
const glm::mat4& animatorMatrix = drawnAnimator ? *drawnAnimator : animatorWorld->Matrix;

// The pose is relative to the animator's entity; the proxy draws in its own space.
const glm::mat4 proxyWorld = m_Transforms[proxy].ToMatrix();
const float determinant = glm::determinant(glm::mat3(proxyWorld));
if (!std::isfinite(determinant) || std::abs(determinant) < c_MinDeterminant || !IsFiniteMatrix(proxyWorld) || !IsFiniteMatrix(animatorMatrix))
	return inputs;
inputs.AnimatorToProxy = InverseAffine(proxyWorld) * animatorMatrix;
```

1. **Lines 1316–1319:** the animator's matrix: the :term[drawn transform]{id=drawn-transform} when the scene has one, the world matrix otherwise.
2. **Lines 1321–1322:** the placement of the proxy that is being posed.
3. **Lines 1323–1325:** a placement that cannot be inverted, or a matrix that is not finite, ends the function with no pose.
4. **Line 1326:** the matrix $A$ of the formula, from the animator's space to the proxy's.

The two lines at the top choose the animator's matrix: its :term[drawn transform]{id=drawn-transform} when the scene has one, its world transform otherwise. During interpolation the scene draws a body between its last two :term[fixed steps]{id=fixed-step} ([Interpolation](../world/interpolation.md)), so its drawn transform is not its simulated one. A skin posed against the simulated place would be skinned where the animator is, but drawn where the animator appears, and the two disagree by a fraction of a step. Using the drawn transform keeps an interpolated character whole.

The last line builds $A$ as the inverse of the proxy's placement times the animator's matrix. The function also stops, and does not pose the proxy, when the pose is missing, has too few joints, or a matrix is not finite; the page on skinned meshes lists those cases.

The shader then does the blend. The scene vertex shader calls these functions in its skinned variant ([The geometry pool](../gpu/geometry-pool.md) quotes the shader). First the palette and the blend.

```slang src="Strata/shaders/Include/Scene.slang#L187-L209"
struct JointMatrix
{
	float4 Rows[3];
};

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
}
```

1. **Lines 187–190:** a palette entry as the :term[graphics card]{id=gpu} reads it: the upper three rows of an affine matrix.
2. **Line 192:** the palettes of all posed instances, in one buffer.
3. **Line 195:** the function takes the instance (which holds where its palette starts), four joint indices and four weights.
4. **Lines 201–207:** the loop reads all four entries and adds each row times its weight, also when the weight is 0.
5. **Line 208:** the blended matrix, which is applied to the vertex.

Then the three ways to move a vector.

```slang src="Strata/shaders/Include/Scene.slang#L232-L251"
float3 SkinPosition(JointMatrix skin, float3 position)
{
	float4 point = float4(position, 1.0);
	return float3(dot(skin.Rows[0], point), dot(skin.Rows[1], point), dot(skin.Rows[2], point));
}

float3 SkinDirection(JointMatrix skin, float3 direction)
{
	return float3(dot(skin.Rows[0].xyz, direction), dot(skin.Rows[1].xyz, direction), dot(skin.Rows[2].xyz, direction));
}

// A normal through the skinning matrix: its cofactor matrix, like TransformNormal (callers normalize).
float3 SkinNormal(JointMatrix skin, float3 normal)
{
	float3 column0 = float3(skin.Rows[0].x, skin.Rows[1].x, skin.Rows[2].x);
	float3 column1 = float3(skin.Rows[0].y, skin.Rows[1].y, skin.Rows[2].y);
	float3 column2 = float3(skin.Rows[0].z, skin.Rows[1].z, skin.Rows[2].z);
	float3 transformed = cross(column1, column2) * normal.x + cross(column2, column0) * normal.y + cross(column0, column1) * normal.z;
	return dot(column0, cross(column1, column2)) < 0.0 ? -transformed : transformed;
}
```

1. **Lines 232–236:** a position gets a fourth coordinate of 1, so the translation in each row's last entry counts.
2. **Lines 238–241:** a direction uses only the first three entries of each row, so it is turned and scaled but not moved.
3. **Lines 246–248:** the three columns of the 3 by 3 part, read from the rows.
4. **Line 249:** the cofactor applied to the normal, with the cross products of the text.
5. **Line 250:** the sign flip for a matrix with a negative determinant, a mirror.

:::why[Why linear blend skinning in the vertex shader?]
Three reasons decide it. First, the models: linear blending is the format that glTF assets are authored and checked for, and an artist sees the same bending in the editor as in a modelling tool. Second, the cost: a palette entry is 48 :term[bytes]{id=byte}, a vertex reads four of them, and the work grows with the vertices drawn, not the vertices stored. Third, the rest of the renderer: the shadow passes and the :term[depth prepass]{id=depth-prepass} must produce the same positions to the bit, and one function that every pass calls guarantees it.

The cost of the choice is the collapse in twists and the lack of other models, below. A dual-quaternion path would need a second palette format and a second set of shader variants for every pass, and the engine has not paid for it.
:::

Every influence must name a joint of the skin, even a weight-0 one. The loop in `BlendJoints` reads all four palette entries for every vertex, with no test of the weight. The loop has no branch on the weight, so every vertex does the same work. An index past the end of the skin would read an entry that is not this skin's, although its weight is 0. Mesh creation therefore refuses such a skin and reports the vertex and joint at fault.

## What this choice cannot do

Linear blend skinning collapses a twisting joint, as you computed. A forearm that turns through half a turn pinches to a point, and close-ups show it. The usual remedy is in the rig. An extra joint in the middle of the forearm carries half of the twist, so no pair of neighbours differs by more than a quarter turn (the third exercise computes it).

Strata has no dual quaternion skinning and no skinning in a compute pass; [Animation limits](../animation/limits.md) lists what the animation system omits. [What Strata does not do](../appendix/not-in-strata.md) lists the engine as a whole.

The pose is not the same everywhere in the engine. Physics' mesh colliders keep the bind pose: a collider built from the arm's mesh stays upright while the arm bends ([Building bodies](../physics/building-bodies.md)). The entity-ID buffer, which picking and outlines read, shows the posed mesh ([Scene view](../editor-ui/scene-view.md)).

The feature test checks the entity-ID buffer with a skinned arm. While nothing poses it, the entity-ID buffer names the arm under a point of the upright forearm. Under a point of the bent forearm it names something else. The test then drives the arm with an animation preview and checks the pose in the same buffer.

## Common mistakes

- **Forgetting the inverse bind matrix.** Symptom: the mesh explodes: each vertex is moved as if it sat at its joint's origin, so it lands away from the character by that joint's distance, even in the bind pose. Fix: multiply by the inverse bind matrix first. With $B_j$ missing in the bind pose, $M_j$ is the joint's own transform and not the identity.
- **Moving normals with the plain matrix.** Symptom: lighting on a stretched or squashed limb looks tilted, and surfaces look dented when the matrix scales unevenly. Fix: use the cofactor, as `SkinNormal` does, and normalize.
- **Culling with the bind-pose bounds.** Symptom: an arm that has bent out of its bind-pose box disappears at the screen's edge. Fix: bound the posed mesh by the posed boxes, which the renderer does ([Skinned meshes in the renderer](../draw/skinned.md)).
- **Giving a weight-0 influence an arbitrary joint index.** Symptom: mesh creation fails with the vertex and joint named. Fix: point unused slots at a real joint of the skin, usually joint 0.
- **Weights that do not add up.** Symptom: creation fails with the sum named; a vertex whose weights add up to less than 1 would shrink toward the origin. Fix: normalize the weights to 65535.

## Summary

- Skinning moves a vertex that two joints influence by weighting what each joint alone would give: for weights 0.25 and 0.75 the example's vertex moves to (-0.025, 1.175, 0).
- A palette entry is the product of three matrices.
  The inverse bind matrix takes bind space into joint space, the joint's posed model transform takes joint space into animator space, and `AnimatorToProxy` takes animator space into the drawn mesh's space.
- A normal goes through the cofactor of the blended 3 by 3 matrix, never the plain matrix, with a sign flip for a mirror, and the result is normalized.
- Rigid binding cracks the surface at a joint, linear blend skinning smooths it but collapses a twist, and dual quaternion skinning keeps the volume at a higher cost.
- Strata builds each palette entry on the processor from the animator's pose and its drawn transform, so an interpolated character stays whole.

## Check yourself

1. A vertex at $(0.2, 1.1, 0)$ has weights 0.5 and 0.5 on the shoulder and the elbow of the worked example (the elbow bent a quarter turn). Where does it land?

   :::answer{tests="skin-vertex"}
   The shoulder leaves it at $(0.2, 1.1, 0)$ and the elbow gives $(-0.1, 1.2, 0)$. The average of the two is $(0.05, 1.15, 0)$. It is the middle point, as equal weights say.
   :::

2. Which matrix takes a vertex from the bind pose into one joint's space?
   (a) the joint's posed model transform; (b) the inverse bind matrix; (c) `AnimatorToProxy`; (d) the :term[cofactor matrix]{id=cofactor-matrix}.

   :::answer{tests="palette-matrices"}
   (b). Option (a) takes joint space into the animator's space, so it comes second; (c) comes last and moves into the drawn mesh's space; (d) is for normals only. Applying (a) without (b) is the exploding mesh of the mistakes list.
   :::

3. A blended matrix stretches x by 3 and keeps y and z. What does the shader give for the normal $(1, 1, 0)$, up to a positive scale?

   :::answer{tests="normal-cofactor"}
   The cofactor columns are $(1,0,0)$, $(0,3,0)$ and $(0,0,3)$, so the result is $(1, 3, 0)$. The plain matrix would give $(3, 1, 0)$, tilting the wrong way. The shader normalizes afterwards.
   :::

4. A vertex at $(0.2, 0, 0)$ is blended half and half between two joints, and the second joint turns half a turn about the y axis. Which artifact appears, and why?

   :::answer{tests="models-compare"}
   The second joint sends the vertex to $(-0.2, 0, 0)$ and the blend lands on the origin: the twist collapse. Linear blending averages positions, so opposite points meet on the axis. Dual quaternion skinning blends rotations and avoids it, at the cost of more numbers per joint.
   :::

5. In a game with fixed-step physics, why does `EvaluatePose` ask `Scene::FindDrawnTransform` for the animator's matrix and not use its world matrix alone?

   :::answer{tests="strata-palette"}
   Between fixed steps the scene draws a body at an interpolated place, and its proxy is placed there. A pose built against the simulated world matrix would be a fraction of a step away from where the proxy is. The drawn matrix keeps the skin and its placement together.
   :::

## Exercises

1. **Basic.** A vertex has weights 40000 and 20000 on joints 0 and 1. Does mesh creation accept it, and what happens if the weights are 40000 and 25535?

   :::answer[Worked solution]{tests="skin-vertex"}
   The first sum is 60000, not 65535, so creation fails with a message that the weights add up to 60000 instead of 65535. The second sum is exactly 65535 and passes: the weights are 0.61 and 0.39 as fractions, to two places.
   :::

2. **Medium.** Write a complete program that skins one vertex between two joints with a palette, and print the vertex with the shoulder alone, the elbow alone and the blend, for the worked example.

   :::answer[Worked solution]{tests="skin-vertex,palette-matrices" solution="sketches/animation-skinning-vertex.cpp"}
   Step 1: write the structure of an influence, a joint index and a weight in 65535ths. Step 2: build the inverse bind matrices (identity for the shoulder, a move down by 1 for the elbow) and the pose. Step 3: form each palette entry as pose times inverse bind. Step 4: add the entries by weight, then apply the sum once to the vertex.

   ```cpp sketch="animation-skinning-vertex.cpp"
   // Skins one vertex between two joints, the way a palette and four weighted influences do.
   #include <cstdint>
   #include <cstdio>

   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>

   struct Influence
   {
   	uint16_t Joint = 0;
   	uint16_t Weight = 0; // In 1/65535ths; the weights of a vertex add up to 65535
   };

   // Blends the palette entries of the influences by weight, then moves the bind-pose vertex with the result.
   glm::vec3 SkinVertex(const glm::vec3& position, const Influence (&influences)[2], const glm::mat4* palette)
   {
   	glm::mat4 blended(0.0f);
   	for (const Influence& influence : influences)
   		blended += palette[influence.Joint] * (static_cast<float>(influence.Weight) / 65535.0f);
   	return glm::vec3(blended * glm::vec4(position, 1.0f));
   }

   int main()
   {
   	// Joint 0 is the shoulder at the origin; joint 1 is the elbow, one unit up.
   	const glm::mat4 inverseBind[2] = { glm::mat4(1.0f), glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -1.0f, 0.0f)) };
   	// The pose: the shoulder stays, the forearm turns a quarter turn about z at the elbow.
   	const glm::mat4 elbowBent = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.0f, 0.0f)) * glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f));
   	const glm::mat4 pose[2] = { glm::mat4(1.0f), elbowBent };

   	glm::mat4 palette[2];
   	for (int joint = 0; joint < 2; joint++)
   		palette[joint] = pose[joint] * inverseBind[joint];

   	const glm::vec3 vertex(0.2f, 1.1f, 0.0f);
   	const Influence influences[2] = { { 0, 16384 }, { 1, 49151 } };
   	const glm::vec3 skinned = SkinVertex(vertex, influences, palette);
   	const glm::vec3 withShoulder = glm::vec3(palette[0] * glm::vec4(vertex, 1.0f));
   	const glm::vec3 withElbow = glm::vec3(palette[1] * glm::vec4(vertex, 1.0f));
   	std::printf("shoulder alone: %.3f %.3f %.3f\n", withShoulder.x, withShoulder.y, withShoulder.z);
   	std::printf("elbow alone:    %.3f %.3f %.3f\n", withElbow.x, withElbow.y, withElbow.z);
   	std::printf("blended:        %.3f %.3f %.3f\n", skinned.x, skinned.y, skinned.z);
   	return 0;
   }
   ```

   ```text output-of="animation-skinning-vertex.cpp"
   shoulder alone: 0.200 1.100 0.000
   elbow alone:    -0.100 1.200 0.000
   blended:        -0.025 1.175 0.000
   ```

   1. **Lines 8–12:** an influence is a joint index and a weight in 65535ths, as in the mesh record.
   2. **Lines 17–20:** the palette entries are added by weight, then applied to the vertex once.
   3. **Lines 31–33:** each palette entry is the pose times the inverse bind matrix.
   4. **Line 36:** the weights 16384 and 49151 add up to 65535.

   The last line is the hand-made result (-0.025, 1.175, 0.000), the same as the example.
   :::

3. **Hard.** Add a middle joint to the twisting forearm: the elbow end at 0 degrees of twist, the middle at a quarter turn and the wrist at a half turn. A vertex at $(0.2, 0, 0)$ lies halfway between the elbow end and the middle. How far from the axis is it after skinning, and how does it compare with the collapse?

   :::answer[Worked solution]{tests="models-compare"}
   The elbow end leaves the vertex at $(0.2, 0, 0)$. A quarter turn about y sends $(x, y, z)$ to $(z, y, -x)$, so the middle joint gives $(0, 0, -0.2)$. The half-and-half blend is $(0.1, 0, -0.1)$, at distance $0.1 \cdot \sqrt{2} \approx 0.141$ from the axis: 71 % of the radius, against 0 for the plain half turn. Weights shared across more joints keep each pair's angle small, which keeps the radius.
   :::

## Where it lives in Strata

- Palette and inputs: `RenderScene::ComputePalette` and `RenderScene::EvaluatePose` in `Strata/src/Strata/Renderer/RenderScene.cpp`; the palette entry type is `RenderData::AffineTransform`.
- The data a mesh carries: `MeshSkinBinding` and `MeshSkinVertex` in `Strata/src/Strata/Renderer/Mesh.h`, checked when `Mesh::CreateSkinned` runs.
- The pose provider: the scene service `ISkinningPoses` and `SkeletonPose` in `Strata/src/Strata/Scene/SceneServices.h`; the mesh names its animator in `SkinComponent`.
- The blend: `BlendJoints`, `SkinPosition`, `SkinDirection` and `SkinNormal` in `Strata/shaders/Include/Scene.slang`, called by `Strata/shaders/Scene/Mesh.vert.slang`.
- Tests: `StrataTests/src/Renderer/GPUAnimationTests.cpp` renders a posed tube and compares it with a mesh skinned on the processor; `StrataTests/src/FeatureTest/GPUFeatureTests.cpp` holds the arm in the entity-ID view.

## Further reading

- Kavan, Collins, Zara and O'Sullivan, "Skinning with Dual Quaternions" (I3D 2007): the dual quaternion model and its comparison with linear blending (advanced).
- The glTF 2.0 specification, the section on skins (registry.khronos.org): how skins, joints and weights are stored in a file (intermediate).
- Magnenat-Thalmann, Laperriere and Thalmann, "Joint-dependent local deformations for hand animation and object grasping" (1988): an early form of weighted joint blending (advanced).
