---
id: animation/skeletons
title: "Skeletons and forward kinematics"
description: "How Strata stores a character's joints, parents and rest pose, and turns local poses into model-space matrices in one pass."
kind: internals
size: M
tracks: [E]
needs: [basics/math-rotations, assets/importing]
time: 60
learn:
  - id: fk-by-hand
    text: compute the model-space transforms of a pose by hand
  - id: one-pass
    text: explain why the joint order makes forward kinematics a single loop
  - id: trs-order
    text: explain why a joint pose applies scale first and translation last
  - id: poses-not-entities
    text: explain why Strata keeps joints out of the scene
  - id: reject-bytes
    text: name the checks that make the skeleton loader refuse corrupt bytes
since: 0.3.0
status: final
---

A character bends. The upper arm swings from the shoulder, the forearm follows the upper arm, and the hand follows the forearm. The `Skeleton` asset stores what that needs for one model: the names of its joints, the parent of each joint, the pose each joint takes at rest and the joint that carries root motion. Its one calculation turns a list of local poses into one matrix per joint. A skeleton plays nothing: clips, controllers and the animator that mixes and plays them come on later pages.

## The problem and how engines solve it

Imagine you must move a robot's arm. The first idea of most beginners is one scene entity for each part of the arm, each one a child of the part above it. You turn the elbow entity and the scene moves everything below it. A scene already does this for any hierarchy, so it looks like free work.

The idea fails once the robot is a real character. A **joint** (also called a bone) is a point of the character that moves relative to another point, such as a shoulder, an elbow or a knuckle. A character has dozens of them, and an animation changes every one of them in every frame. Take 60 joints and 100 characters: that is 6,000 entity changes per frame.

Each change is not cheap. The scene caches :term[world transforms]{id=world-transform}, the hierarchy and the drawn positions it blends between physics steps, so every change marks caches as stale and asks for work. Strata therefore keeps joints out of the scene, as the rule below says.

Most engines choose another way. A **skeleton** (also called a rig) is the set of all joints of one character, stored as a few plain arrays: one entry per joint with its name, its parent and its pose at rest. Strata uses this layout too. The scene sees one entity for the whole character, and the pose lives in a separate structure that the animation system owns.

A parent link is only an index into the arrays. The arrays hold a useful promise: each joint stands after its parent. A list that keeps this promise is in **topological order** (parents first). With that order, a program that walks the list once always meets a parent before its children, and that single fact turns the whole calculation into one loop.

:::rule
**Poses are not entities.** Strata never makes an entity for each joint and never writes joint transforms into the scene, so a character adds no transform changes. The reason is the cost above. The glTF :term[importer]{id=importer} follows the rule and makes entities only for joints that carry content.
:::

## The map

`Strata/src/Strata/Animation/AnimationTypes.h` holds the pose type, the joint index and the matrix helpers. `Strata/src/Strata/Animation/Skeleton.h` and `Strata/src/Strata/Animation/Skeleton.cpp` hold the asset, its validation, its cooked form and the pass over the joints. `Strata/src/Strata/Animation/RestPose.h` and `Strata/src/Strata/Animation/RestPose.cpp` hold one function that shows the skeleton at rest.

```mermaid caption="Who calls whom. The model importer and the loader both make a skeleton through create. The animator asks it for model-space matrices. " alt="A flow chart with four boxes. The importer and the loader point to a box named Skeleton create, which checks its input. That box points to a skeleton asset. The animator points to the asset's pass over the joints, which uses the pose types and matrix helpers."
flowchart LR
  Importer["Model importer"] --> Create["Skeleton::Create (validates)"]
  Loader["Loader: Skeleton::Deserialize"] --> Create
  Create --> Skeleton["Skeleton asset"]
  Animator["Animator"] --> FK["ComputeModelTransforms"]
  Skeleton --> FK
  Types["AnimationTypes.h: JointPose, ToMatrix"] --> FK
```

You can see a skeleton in the editor. Select the skeleton :term[sub-asset]{id=sub-asset} of a model, and the **Joints** section of the Asset Inspector lists the tree, one row for each joint, set in by its depth. The bone icon of the root motion joint has the accent color.

::figure{id=robot-skeleton}

A model's skeleton is its sub-asset "Skeleton", with the joints of all its skins and the nodes its animations move. [The importing page](../animation/importing.md) shows how the importer builds it.

Take an arm with three joints. The first array holds the names, the second the parent of each joint, the third the rest pose. The root has no parent, so Strata writes `c_NoJoint` there. Every other parent index is smaller than the joint's own index, so each arrow from a joint to its parent points left.

```mermaid caption="The memory layout of a three-joint arm. Names, parents and rest poses are three arrays with one entry per joint. Each parent entry holds the index of an entry further left, and the root holds a special value for none." alt="Three rows of three cells. The first row holds the names Shoulder, Elbow and Wrist at indexes zero, one and two. The second row holds the parents none, zero and one. The third row holds the rest translations zero, zero up one, and zero up one. Arrows from the parent cells of Elbow and Wrist point left to the cells of their parents."
flowchart LR
  subgraph Names
    N0["0: Shoulder"]
    N1["1: Elbow"]
    N2["2: Wrist"]
  end
  subgraph Parents
    P0["none"]
    P1["0"]
    P2["1"]
  end
  subgraph Rest["Rest pose (translation)"]
    R0["0, 0, 0"]
    R1["0, 1, 0"]
    R2["0, 1, 0"]
  end
  P2 -- "parent 1" --> N1
  P1 -- "parent 0" --> N0
```

## The contract

A caller of the skeleton may assume the following, and must do the following.

- **Names are unique and never empty.** Clips bind to joints by name, so clips of another model with the same joint names play on this skeleton. The match is exact and case-sensitive.
- **Parents come first.** A joint's parent index is `c_NoJoint` or smaller than the joint's own index. The reason is the single pass of the next sections.
- **Poses are finite and rotations are unit quaternions.** `Skeleton::Create` :term[normalizes]{id=normalization} each rest rotation and refuses :term[NaN]{id=nan} and infinity. A rotation that is not of unit length would distort the matrices.
- **A skeleton has 1 to 4,096 joints.** Meshes and clips store joint indices in 16 bits, and the value 0xFFFF is reserved for none.
- **Poses are relative.** A joint's pose is relative to its parent, and the pose of a root joint is relative to the animator: the entity that carries the Animator component, taught on [the importing page](../animation/importing.md).

:::rule
**Skeleton joints are parents first.** `Skeleton::Create` and `Skeleton::Deserialize` refuse a skeleton where a joint comes before its parent. Without the order, the pass over the joints would read a matrix that is not computed yet.
:::

The inverse bind matrices belong to a mesh's skin, not to the skeleton; [the skinning page](../animation/skinning.md) teaches them.

## A toy version

Here is the whole idea in a small program. It has a pose with a translation and an angle about the Z axis, a joint with a parent index, and one loop. The joints are the arm of the arrays above: a shoulder at the origin, an elbow one unit up and a wrist one unit above the elbow.

:::question
New to C++? The sketch uses :term[structs]{id=struct}, functions, vectors and calls such as `glm::translate(`. Read [the programming basics](../basics/programming-3.md) first.
:::

The program prints where each joint's origin lands in **model space**: the space of the animator's entity, where every joint's matrix says where the joint stands and how it is turned.

A pose given relative to the parent is **local**: it says nothing about the world, only about the step from the parent to the joint.

```cpp sketch="animation-skeletons-toy.cpp"
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr uint16_t c_NoJoint = 0xFFFF;

struct ToyJoint
{
	const char* Name;
	uint16_t Parent;
	glm::vec3 Translation;
	float AngleDegrees; // About the Z axis
};

// Translation, then rotation: the joint turns about its own origin.
glm::mat4 ToMatrix(const ToyJoint& joint)
{
	const glm::mat4 moved = glm::translate(glm::mat4(1.0f), joint.Translation);
	return glm::rotate(moved, glm::radians(joint.AngleDegrees), glm::vec3(0.0f, 0.0f, 1.0f));
}

// One pass: every parent comes before its children, so its matrix is ready.
std::vector<glm::mat4> ComputeModelTransforms(const std::vector<ToyJoint>& joints)
{
	std::vector<glm::mat4> model(joints.size());
	for (size_t joint = 0; joint < joints.size(); joint++)
	{
		const glm::mat4 local = ToMatrix(joints[joint]);
		const uint16_t parent = joints[joint].Parent;
		model[joint] = parent == c_NoJoint ? local : model[parent] * local;
	}
	return model;
}

float Clean(float value)
{
	return std::round(value * 10.0f) / 10.0f + 0.0f; // + 0.0f turns -0.0 into 0.0
}

void Print(const char* title, const std::vector<ToyJoint>& joints)
{
	std::printf("%s\n", title);
	const std::vector<glm::mat4> model = ComputeModelTransforms(joints);
	for (size_t joint = 0; joint < joints.size(); joint++)
		std::printf("  %-8s (%.1f, %.1f, %.1f)\n", joints[joint].Name, Clean(model[joint][3].x), Clean(model[joint][3].y), Clean(model[joint][3].z));
}

int main()
{
	std::vector<ToyJoint> arm = {
		{ "Shoulder", c_NoJoint, glm::vec3(0.0f), 0.0f },
		{ "Elbow", 0, glm::vec3(0.0f, 1.0f, 0.0f), 0.0f },
		{ "Wrist", 1, glm::vec3(0.0f, 1.0f, 0.0f), 0.0f },
	};
	Print("Rest pose", arm);
	arm[1].AngleDegrees = 90.0f;
	Print("Elbow turned 90 degrees", arm);
	arm[0].AngleDegrees = 90.0f;
	Print("Shoulder and elbow turned 90 degrees", arm);

	// The wrong order, rotation before translation, swings the elbow about the world origin.
	const glm::mat4 wrong = glm::translate(glm::rotate(glm::mat4(1.0f), glm::radians(90.0f), glm::vec3(0.0f, 0.0f, 1.0f)), glm::vec3(0.0f, 1.0f, 0.0f));
	std::printf("Elbow with the wrong order (%.1f, %.1f, %.1f)\n", Clean(wrong[3].x), Clean(wrong[3].y), Clean(wrong[3].z));
	return 0;
}
```

1. **Line 23:** The rotation is applied last in the product, so it acts first on a point: the joint turns about its own origin.
2. **Line 34:** The whole of forward kinematics: a root keeps its local matrix, any other joint multiplies its parent's finished matrix by its own.
3. **Line 66:** The same joint built in the wrong order, for the last line of the output.

```text output-of="animation-skeletons-toy.cpp"
Rest pose
  Shoulder (0.0, 0.0, 0.0)
  Elbow    (0.0, 1.0, 0.0)
  Wrist    (0.0, 2.0, 0.0)
Elbow turned 90 degrees
  Shoulder (0.0, 0.0, 0.0)
  Elbow    (0.0, 1.0, 0.0)
  Wrist    (-1.0, 1.0, 0.0)
Shoulder and elbow turned 90 degrees
  Shoulder (0.0, 0.0, 0.0)
  Elbow    (-1.0, 0.0, 0.0)
  Wrist    (-1.0, -1.0, 0.0)
Elbow with the wrong order (-1.0, 0.0, 0.0)
```

The loop is **forward kinematics** (FK): computing every joint's model-space matrix from the local poses by walking from the root to the leaves. A parent's matrix is ready when its child is reached, because of the order. The output shows the point of the method: one angle at the root moves every joint below it.

:::example
Check the second block of the output by hand. The elbow's local matrix is a translation of (0, 1, 0) followed by a turn of 90 degrees about Z. Its model matrix equals the shoulder's, the identity, times that matrix, so the elbow's origin stays at (0, 1, 0).

The wrist's local matrix is a translation of (0, 1, 0). Its model matrix is the elbow's times that matrix. The elbow's turn takes the wrist's step of (0, 1, 0) to (−1, 0, 0), because a turn by 90 degrees takes the up direction to the left. The wrist's origin is (0, 1, 0) plus (−1, 0, 0), which is (−1, 1, 0), as the program prints.

Now turn the shoulder too. Everything below it turns with it: the elbow's origin moves from (0, 1, 0) to (−1, 0, 0), and the wrist, which hangs below a total turn of 180 degrees, lands at (−1, −1, 0).
:::

The last line of the output shows the order mistake.

A joint's pose is a translation, a rotation and a scale, and they apply **scale first, then rotation, then translation**. In matrix form the translation stands on the left, so the pose reads $T R S$ and acts on a point from the right. Write the product the other way and the rotation turns the joint's own offset too. The elbow then swings about the world origin and lands at (−1, 0, 0) instead of turning about itself at (0, 1, 0). Strata uses the order of a scene entity's transform.

## The real code, in the order data flows

The toy has one angle, no scale, no checks and no :term[file format]{id=file-format}. Strata's code has all of them.

### The pose and the joint index

Each joint pose stores a translation, a unit :term[quaternion]{id=quaternion} and a scale. The comment names the space of the root joints.

```cpp src="Strata/src/Strata/Animation/AnimationTypes.h#L15-L22"
struct JointPose
{
	glm::vec3 Translation = glm::vec3(0.0f);
	glm::quat Rotation = glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	glm::vec3 Scale = glm::vec3(1.0f);

	bool operator==(const JointPose&) const = default;
};
```

`JointPose` is the unit of animation: the same three fields as a scene entity's transform, with the same order. A joint index is 16 bits wide, and `c_NoJoint` is the largest 16-bit value, as in the toy. A quaternion of length zero has no direction, so one helper repairs such input.

```cpp src="Strata/src/Strata/Animation/AnimationTypes.h#L32-L39"
inline glm::quat Normalize(const glm::quat& q)
{
	const float lengthSquared = q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w;
	if (!(lengthSquared > 1.0e-20f) || !std::isfinite(lengthSquared))
		return glm::quat(1.0f, 0.0f, 0.0f, 0.0f);
	const float inverse = 1.0f / std::sqrt(lengthSquared);
	return glm::quat(q.w * inverse, q.x * inverse, q.y * inverse, q.z * inverse);
}
```

`AnimationMath::Normalize` returns the quaternion of unit length that is closest to its input. For input that is nearly zero or not a finite number it returns the identity rotation, which means no turn. The test `!(lengthSquared > 1.0e-20f)` puts a not in front, so that NaN, for which every comparison fails, also lands in the repair branch. Mathematics of quaternions and of q and −q is on [the rotations page](../basics/math-rotations.md).

### From a pose to a matrix

Two helpers turn poses into matrices and combine them. In glm, `matrix[0]` is the first column, not the first row. Watch the column writes in the first and the skipped fourth row in the second.

```cpp src="Strata/src/Strata/Animation/AnimationTypes.h#L60-L85"
// The joint's transform as a matrix (translation * rotation * scale).
inline glm::mat4 ToMatrix(const JointPose& pose)
{
	glm::mat4 matrix = glm::mat4_cast(pose.Rotation);
	matrix[0] *= pose.Scale.x;
	matrix[1] *= pose.Scale.y;
	matrix[2] *= pose.Scale.z;
	matrix[3] = glm::vec4(pose.Translation, 1.0f);
	return matrix;
}

// The product of two affine matrices (fourth rows 0, 0, 0, 1), without the work of the fourth row.
inline glm::mat4 MultiplyAffine(const glm::mat4& a, const glm::mat4& b)
{
	glm::mat4 result;
	for (int column = 0; column < 4; column++)
	{
		const glm::vec4& source = b[column];
		result[column] = a[0] * source.x + a[1] * source.y + a[2] * source.z + (column == 3 ? a[3] : glm::vec4(0.0f));
	}
	result[0].w = 0.0f;
	result[1].w = 0.0f;
	result[2].w = 0.0f;
	result[3].w = 1.0f;
	return result;
}
```

1. **Lines 64–66:** Each column of the rotation matrix is scaled, which is a scale applied before the rotation.
2. **Line 67:** The translation fills the last column.
3. **Line 78:** Three columns of `a` are combined with the first three numbers of a column of `b`; only the translation column of `b` adds the translation of `a`.
4. **Lines 80–83:** The fourth row is written directly: 0, 0, 0, 1.

Scaling the columns equals multiplying by a scale matrix on the right, which is the order scale first.

A joint matrix is affine: its last row is always (0, 0, 0, 1). `MultiplyAffine` uses that fact: it never reads the fourth row of `b`, and it writes the last row of the result by hand. That needs 48 multiplications instead of 64, a quarter fewer, for every joint of every animator in every frame. The cost is a function that is wrong for a matrix that is not affine.

### Forward kinematics in one pass

The pass reads one local pose per joint and writes one matrix per joint.

```cpp src="Strata/src/Strata/Animation/Skeleton.cpp#L178-L187" symbol="Skeleton::ComputeModelTransforms"
void Skeleton::ComputeModelTransforms(std::span<const JointPose> local, std::span<glm::mat4> outModel) const
{
	const size_t count = std::min({ local.size(), outModel.size(), m_Parents.size() });
	for (size_t joint = 0; joint < count; joint++)
	{
		const glm::mat4 matrix = AnimationMath::ToMatrix(local[joint]);
		const JointIndex parent = m_Parents[joint];
		outModel[joint] = parent == c_NoJoint ? matrix : AnimationMath::MultiplyAffine(outModel[parent], matrix);
	}
}
```

1. **Line 180:** The count is the smallest of the three sizes, so no write passes the end of a buffer.
2. **Line 183:** The local pose becomes a matrix.
3. **Line 185:** A root keeps its matrix; any other joint multiplies its parent's matrix, already computed, by its own.

The matrix of a joint $j$ follows from its parent's matrix:

$$M_j = M_{p(j)} \, L_j$$

$M_j$ is the model matrix of joint $j$, $p(j)$ is the index of its parent, $M_{p(j)}$ is the model matrix of that parent, and $L_j$ is the local matrix of joint $j$ from `ToMatrix`. Read the product as: first apply $L_j$, which places the joint relative to the parent, then apply the parent's whole chain. For a root joint there is no parent and $M_j = L_j$, which is the `parent == c_NoJoint` branch.

The pass is a single loop with no calls of itself, because `outModel[parent]` is already written when `joint` is reached. It also never trusts the caller's sizes: the count is the smallest of the three spans, so a short buffer gives a short result instead of a write past the end.

### What makes the pass safe

`Skeleton::Create` is the only way to make a skeleton, so the pass needs no checks of its own. The loop below holds the checks that the pass relies on; watch the order test.

```cpp src="Strata/src/Strata/Animation/Skeleton.cpp#L61-L75"
for (size_t joint = 0; joint < count; joint++)
{
	if (names[joint].empty() || names[joint].size() > c_MaxNameLength)
		return fail(fmt::format("Joint {} has an empty or too long name", joint));
	// Parents come first: a pose is computed in one pass over the joints.
	if (parents[joint] != c_NoJoint && parents[joint] >= joint)
		return fail(fmt::format("Joint '{}' comes before its parent", names[joint]));
	JointPose& pose = restPose[joint];
	if (!IsFinite(pose.Translation) || !IsFinite(pose.Scale) || !IsFinite(pose.Rotation))
		return fail(fmt::format("Joint '{}' has a non-finite rest pose", names[joint]));
	const float lengthSquared = glm::dot(pose.Rotation, pose.Rotation);
	if (!(lengthSquared > 1.0e-12f))
		return fail(fmt::format("Joint '{}' has a zero rotation", names[joint]));
	pose.Rotation = AnimationMath::Normalize(pose.Rotation);
}
```

1. **Lines 63–64:** A name must exist and stay within 1,024 :term[bytes]{id=byte}.
2. **Line 66:** A parent must be `c_NoJoint` or an earlier joint.
3. **Line 69:** NaN and infinity in any pose value fail.
4. **Line 72:** A rotation of length zero fails, because it has no direction.
5. **Line 74:** The accepted rotation is normalized, so a stored skeleton always holds unit quaternions.

The order test refuses a parent that is the joint itself or comes later, which also rules out cycles. The loop then refuses NaN, infinity and a zero rotation, and normalizes the rest. Duplicate names are refused after the loop, when the name index is built, and a check before it refuses more than 4,096 joints.

### The rest pose

The **rest pose** is the pose every joint takes when nothing animates it: the rest transform of each joint, taken through its parents. It is not the bind pose. The bind pose belongs to a skin, since two skins may bind one joint in different poses, and [the skinning page](../animation/skinning.md) teaches it.

```cpp src="Strata/src/Strata/Animation/RestPose.cpp#L9-L13"
void ComputeRestPose(const Skeleton& skeleton, std::vector<glm::mat4>& outModel)
{
	outModel.resize(skeleton.GetJointCount());
	skeleton.ComputeModelTransforms(skeleton.GetRestPose(), outModel);
}
```

`ComputeRestPose` is the pass above fed with the skeleton's own rest poses. An animator with nothing playing returns this result, and by default the editor shows the same result on animators in scenes that are not playing. Both use one function, so a character stands the same way in edit mode and in play mode.

### The cooked form

An imported skeleton is stored in a cooked file. The format is called **STSK**, the four letters of its :term[magic number]{id=magic-number}, and this is version 1. The file holds a :term[header]{id=header} of four 32-bit values (magic, version, joint count and root motion joint), then one 44-byte record for each joint, then the names.

| Part | Size | Content |
| --- | --- | --- |
| Header | 16 :term[bytes]{id=byte} | Magic, version, joint count, root motion joint |
| One joint | 44 bytes | Parent (4), translation (12), rotation x, y, z, w (16), scale (12) |
| One name | 4 bytes and the text | Length, then the :term[UTF-8]{id=utf-8} bytes |

Clips have a sibling format, the Strata animation clip (STAC) format, taught on [the clips page](../animation/clips.md). The skeleton loader is the first code in the animation part that reads bytes it cannot trust: a file can be truncated, damaged or made by an attacker. The rule of the engine is that a loader refuses such bytes and never crashes.

:::rule
**Loaders reject truncated and garbage bytes.** A loader of a :term[stored form]{id=stored-form} checks every size against the bytes that remain before it allocates, and refuses bad input with a message. A crash or a huge allocation on a damaged file would take the editor down. General methods are on [the robustness page](../assets/robustness.md).
:::

The loader below reads a header, the joint records and the names. Watch the order of the checks and what each one compares against the bytes left.

```cpp src="Strata/src/Strata/Animation/Skeleton.cpp#L121-L161" symbol="Skeleton::Deserialize"
Ref<Skeleton> Skeleton::Deserialize(std::span<const uint8_t> data, std::string* outError)
{
	auto fail = [outError](const std::string& message) -> Ref<Skeleton>
	{
		if (outError)
			*outError = message;
		return nullptr;
	};

	BinaryReader reader(data);
	const CookedSkeletonHeader header = reader.Read<CookedSkeletonHeader>();
	if (!reader.IsValid() || header.Magic != c_SkeletonMagic)
		return fail("Not a cooked Strata skeleton");
	if (header.Version != c_CookedVersion)
		return fail(fmt::format("Unsupported cooked skeleton version {}", header.Version));
	if (header.JointCount == 0 || header.JointCount > c_MaxJoints || header.JointCount > reader.GetRemaining() / sizeof(CookedJoint)
		|| header.RootMotionJoint >= header.JointCount)
		return fail("Cooked skeleton header is corrupt");

	std::vector<JointIndex> parents(header.JointCount);
	std::vector<JointPose> restPose(header.JointCount);
	for (uint32_t joint = 0; joint < header.JointCount; joint++)
	{
		const CookedJoint cooked = reader.Read<CookedJoint>();
		if (cooked.Parent != c_NoJoint && cooked.Parent >= joint)
			return fail("Cooked skeleton joints are out of order");
		parents[joint] = static_cast<JointIndex>(cooked.Parent);
		JointPose& pose = restPose[joint];
		pose.Translation = glm::vec3(cooked.Translation[0], cooked.Translation[1], cooked.Translation[2]);
		pose.Rotation = glm::quat(cooked.Rotation[3], cooked.Rotation[0], cooked.Rotation[1], cooked.Rotation[2]);
		pose.Scale = glm::vec3(cooked.Scale[0], cooked.Scale[1], cooked.Scale[2]);
	}
	std::vector<std::string> names(header.JointCount);
	for (std::string& name : names)
		name = reader.ReadString(c_MaxNameLength);
	if (!reader.IsValid())
		return fail("Cooked skeleton is truncated");
	if (reader.GetRemaining() != 0)
		return fail("Cooked skeleton has trailing data");
	return Create(std::move(names), std::move(parents), std::move(restPose), static_cast<JointIndex>(header.RootMotionJoint), outError);
}
```

1. **Lines 132–135:** A wrong magic or version ends the load before anything else is read.
2. **Line 136:** The joint count must lie in 1 to 4,096 and fit in the bytes left, divided by the size of a joint record; this check comes before any vector is sized.
3. **Line 145:** A parent at or after its own joint is refused while reading, as `Create` would refuse it later.
4. **Lines 156–159:** A damaged or cut name, or bytes left over after the last name, fail the load.
5. **Line 160:** `Create` then repeats the checks of the contract, including unique names.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One scene entity per joint | Many beginner projects and tools that show a hierarchy | Tools that work on entities would work on joints | Dozens of cache updates per character and frame |
| Sort the joints when a skeleton loads | Loaders of many engines | Files in any order would load | A sort at every load, and a loader that hides a bad importer |
| Matrices stored as 4 by 4 with a full multiply | Simple animation code | No function that needs affine input | A third more multiplications per joint (64 instead of 48) |

## How it is tested

The suite `Animation.Assets` holds the tests of this page, in `StrataTests/src/Animation/AnimationAssetTests.cpp`. The test "Skeletons validate, round trip and find joints by name" makes the arm skeleton, writes it, loads it again and compares. It then calls `Skeleton::Create` with input that must fail: no joints, a parent after its child, duplicate names, an empty name, a root motion joint that does not exist, a NaN and a zero rotation.

The test "Skeleton loading rejects truncated and garbage bytes" feeds the cooked arm to `Deserialize` in many forms. It cuts the file at every length, adds one byte, breaks the magic and damages every byte with three patterns. Whatever still loads must satisfy the order rule.

The arm skeleton comes from `CreateArmSkeleton` in `StrataTests/src/Animation/AnimationTestUtils.h`: a shoulder at the origin, an elbow one unit up and a wrist one more unit up, the same arm as the toy. The same file holds the helper clips and the test assets that the later animation pages use. Run the suite with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Animation.Assets
```

The filter runs only the suite's tests, in seconds.

## Changing it safely

A new cooked layout needs a new `c_CookedVersion` and new corruption tests. Keep these rules in mind:

- **Validate in `Create`.** Every new rule goes into `Skeleton::Create`, because both the importer and the loader pass through it.
- **Keep the order.** An importer that writes a joint before its parent produces a file that the loader refuses.
- **Do not create entities per joint.** Poses stay in the animation system, as the rule above says.
- **Change the joint order only with the meshes.** A mesh's skin binding stores the skeleton's joint indices, so a new order breaks it. Clips bind by name and bind again.

Run `Animation.Assets` before every commit.

## Summary

- You compute model-space transforms by hand: multiply each joint's local matrix on the right of its parent's model matrix, root first.
- The single loop works because every parent comes before its children, so the parent's matrix is ready.
- A joint pose applies scale, then rotation, then translation; the other order swings the joint about the world origin.
- Joints are array entries, not entities, because per-joint entities would add dozens of scene changes per character and frame.
- The loader refuses a bad magic or version, a count larger than the bytes left, a parent after its child, truncated or trailing data.

## Check yourself

1. A skeleton has joints Hip (root), Knee (parent Hip) and Ankle (parent Knee). Hip's local pose is a translation of (0, 1, 0), Knee's is (0, 1, 0) and Ankle's is (0, 1, 0), all without rotation. Where is the Ankle's origin in model space?

   - A. (0, 1, 0)
   - B. (0, 3, 0)
   - C. (0, 0, 0)

   :::answer{tests="fk-by-hand"}
   B. Each matrix is the parent's times the local one, so the translations add: (0, 1, 0) three times. A forgets the parents. C forgets the translations.
   :::

2. Why can `ComputeModelTransforms` be a single loop with no calls of itself?

   - A. Because the loop runs on many threads.
   - B. Because every parent has a smaller index than its children, so its matrix is written before it is read.
   - C. Because a skeleton has at most one root.

   :::answer{tests="one-pass"}
   B. The order is checked when the skeleton is made. A is wrong: the pass is serial. C is wrong: a skeleton can have several roots.
   :::

3. A joint's rest translation is (0, 1, 0) and its rotation is 90 degrees about Z. Which product puts its origin at (0, 1, 0)?

   - A. Translation times rotation.
   - B. Rotation times translation.

   :::answer{tests="trs-order"}
   A. With the rotation on the right, the point is turned first and moved after, so the origin stays at the translation. B turns the translation too, and the origin lands at (−1, 0, 0).
   :::

4. Which sentence gives Strata's reason for not making an entity per joint?

   - A. Entities cannot have parents.
   - B. Joint entities would force dozens of changes per character and frame on the scene's caches, hierarchy and interpolation.
   - C. Entities cannot store quaternions.

   :::answer{tests="poses-not-entities"}
   B. Entities have parents and store quaternions, so A and C are wrong. The cost of the changes is the reason.
   :::

5. A cooked skeleton's header says it has 4,000,000 joints, and the file is 300 bytes long. Which check refuses it, and why before any allocation?

   :::answer{tests="reject-bytes"}
   The check of `header.JointCount > reader.GetRemaining() / sizeof(CookedJoint)`, inside the header test, refuses it: 300 bytes hold at most 6 joint records. It also fails the limit of 4,096. It runs before the vectors are sized, so a damaged count never reserves memory.
   :::

## Exercises

1. **Basic.** In the toy's arm, turn only the shoulder by 90 degrees about Z. Give the origins of Elbow and Wrist.

   :::answer[Worked solution]{tests="fk-by-hand"}
   The elbow's local step (0, 1, 0) is turned to (−1, 0, 0) by the shoulder. The elbow origin is (−1, 0, 0). The elbow has no turn of its own, so the wrist's step is also turned to (−1, 0, 0): the wrist origin is (−2, 0, 0).
   :::

2. **Medium.** Write a function that checks that every parent comes before its child and returns the engine's message for the first fault. Test it on the arm and on the arm listed backwards.

   :::answer[Worked solution]{tests="one-pass" solution="sketches/animation-skeletons-order.cpp"}
   Walk the joints in order. A parent that is not `c_NoJoint` must be smaller than the joint's index, else return the message. The reversed arm has Wrist first with parent 1, which is not smaller than 0, so the first joint fails.

   ```cpp sketch="animation-skeletons-order.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <string>
   #include <vector>

   constexpr uint16_t c_NoJoint = 0xFFFF;

   // An empty string when every parent comes before its child, else the first error.
   std::string CheckOrder(const std::vector<std::string>& names, const std::vector<uint16_t>& parents)
   {
   	for (size_t joint = 0; joint < names.size(); joint++)
   	{
   		if (parents[joint] != c_NoJoint && parents[joint] >= joint)
   			return "Joint '" + names[joint] + "' comes before its parent";
   	}
   	return "";
   }

   int main()
   {
   	const std::string good = CheckOrder({ "Shoulder", "Elbow", "Wrist" }, { c_NoJoint, 0, 1 });
   	const std::string bad = CheckOrder({ "Wrist", "Elbow", "Shoulder" }, { 1, 2, c_NoJoint });
   	std::printf("Arm: '%s'\n", good.c_str());
   	std::printf("Reversed arm: '%s'\n", bad.c_str());
   	return 0;
   }
   ```

   ```text output-of="animation-skeletons-order.cpp"
   Arm: ''
   Reversed arm: 'Joint 'Wrist' comes before its parent'
   ```

   1. **Line 13:** A parent that is not `c_NoJoint` must be smaller than the joint's index.
   2. **Line 14:** The message is the one the engine's `Skeleton::Create` gives.
   :::

3. **Hard.** Trace it yourself: in the engine's source build, put a breakpoint in `Skeleton::Deserialize` and run the test "Skeleton loading rejects truncated and garbage bytes". For three corrupted inputs, name the check that refuses each.

   :::answer[Worked solution]{tests="reject-bytes"}
   The function is `Skeleton::Deserialize` in `Strata/src/Strata/Animation/Skeleton.cpp`. A wrong magic fails the first test with "Not a cooked Strata skeleton". A joint count above the bytes left fails with "Cooked skeleton header is corrupt". A parent index at or above the joint's own index fails with "Cooked skeleton joints are out of order". Truncated names fail with "Cooked skeleton is truncated", and the extra byte fails with "Cooked skeleton has trailing data".
   :::

## Where it lives in Strata

- Files: `Strata/src/Strata/Animation/AnimationTypes.h`, `Strata/src/Strata/Animation/Skeleton.h`, `Strata/src/Strata/Animation/Skeleton.cpp`, `Strata/src/Strata/Animation/RestPose.h`, `Strata/src/Strata/Animation/RestPose.cpp`.
- Classes and functions: `Skeleton`, `JointPose`, `ComputeRestPose`, `AnimationMath::ToMatrix`, `AnimationMath::MultiplyAffine`.
- Tests: the suite `Animation.Assets` in `StrataTests/src/Animation/AnimationAssetTests.cpp`, and `CreateArmSkeleton` in `StrataTests/src/Animation/AnimationTestUtils.h`.
- Editor: the **Joints** section of the Asset Inspector for a skeleton asset.

## Further reading

- Jason Gregory, "Game Engine Architecture", chapter on animation systems: the standard book treatment of skeletons and poses (intermediate).
- The glTF 2.0 specification, the section on skins and nodes: where Strata's imported joints come from (intermediate).
- Eric Lengyel, "Foundations of Game Engine Development, Volume 1: Mathematics": affine matrices and rotations (advanced).
