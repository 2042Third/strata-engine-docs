---
id: animation/importing
title: "Importing animated models"
description: "How the glTF importer turns skins, animated nodes and animations into a skeleton, clips, skin bindings and a model's entities, with stable handles."
kind: internals
size: M
tracks: [E]
needs: [animation/clips, animation/skinning, assets/models-gltf]
time: 70
learn:
  - id: skeleton
    text: predict the joints, their order and the root motion joint that a glTF node tree produces
  - id: clips
    text: name the key of each clip and the channels the importer skips
  - id: skins
    text: compute the four 16-bit weights of a vertex and say when a skin imports without skinning
  - id: entities
    text: predict which nodes of a rigged file become entities and which components they carry
  - id: version
    text: explain why a change to the importer's output bumps its version
since: 0.3.0
status: final
---

An artist rigs a character in a modeling program and saves one glTF file. The file holds a tree of nodes, skins and animations, and it never says which nodes are bones and which are ordinary objects. The animation part of the :term[importer]{id=importer} `GltfImporter` decides that. It turns the file into one `Skeleton` :term[sub-asset]{id=sub-asset}, one clip per animation, a skin binding on each skinned mesh and the model's entities. It keeps every handle the same when you import the file again.

The importer reads no meshes, materials or textures (see [Models and the glTF importer](../assets/models-gltf.md)), and it plays nothing: what its components do in a running scene belongs to later pages of this part.

## The problem and how engines solve it

A glTF file describes animation with three loose pieces. A **node** is a point in a tree with a position, a rotation and a scale. A skin lists the nodes that bend a mesh, with an :term[inverse bind matrix]{id=inverse-bind-matrix} for each. An animation holds samplers (lists of times and values) and channels that point a sampler at one property of one node.

Nothing marks a node as "bone" or "object". A node that a skin lists is a bone, and so is a node that only moves because an animation drives it.

An engine must answer three questions from that tree. Which nodes form the skeleton? Which nodes stay entities that you can select and attach things to? And how does a second import, after the artist fixes one bone, keep every reference in your scenes valid?

One answer makes an entity for every node. A bone is then an object in the scene, and a game can attach anything to it. The cost is that a character of 80 bones makes 80 entities, each with a transform that the scene must update every frame.

The other answer keeps bones out of the scene: a skeleton is one asset, a pose is a list of matrices, and only nodes with real content become entities. Strata takes this route. The cost is that the importer must decide which nodes are only bones, and the few attachment entities need a way to follow their bone.

Handles raise the second problem. A scene stores the handle of a clip, never a :term[file path]{id=path}, so a clip that got a new handle would be lost to every animator that played it. Strata derives a sub-asset's handle from the model's handle and the sub-asset's key, as [handles and sub-assets](../assets/handles-meta.md) explains. The same file with the same keys then gives the same handles, and this page shows how the importer picks the keys.

## The map

The importer runs a fixed order of steps inside an import job on a background thread. It asks the job's :term[cancellation flag]{id=cancellation-flag} between channels, so a long animation never holds up a cancel. The skeleton comes first, because skins, clips and entities all name joints.

```mermaid caption="The order of the animation steps of an import. The skeleton comes first; skins, clips and the entity tree read its joint numbers." alt="A flow chart. A glTF file goes to the skeleton step, which writes the skeleton sub-asset and a node-to-joint table. The table feeds three steps: skins, which write skin bindings into the meshes; animations, which write one clip each; and the model's entity tree, which adds the animator, skin and attachment components."
flowchart LR
  File["glTF file"] --> Skel["ImportSkeleton"]
  Skel --> SkelAsset["Skeleton sub-asset"]
  Skel --> Table["Node to joint table"]
  Table --> Skins["ReadSkin, ReadSkinVertices"]
  Table --> Anims["ImportAnimations"]
  Table --> Tree["AddHierarchy, BuildModel"]
  Skins --> Meshes["Skin bindings in the meshes"]
  Anims --> Clips["One clip per animation"]
  Tree --> Model["Model entities"]
```

All of it lives in `Strata/src/Strata/Asset/GltfImporter.cpp`, inside `#if ST_WITH_ANIMATION`, because the animation module is optional (the [layers and registries](../core/layers-registries.md) page explains optional modules). Without the module, the importer finds no skeleton and skinned meshes import rigid. A file with skins or animations then adds "skins (the engine has no animation module)" or "animations (the engine has no animation module)" to the skipped features that the import reports.

## The contract

The importer promises its callers the following, and each promise has a reason.

- **One skeleton per model.** The sub-asset has the key `Skeleton`. All meshes and clips of a model address the same joint numbers.
- **Parents come first.** A joint's parent has a smaller index, so a pose is computed in one pass over the joints.
- **Joint names are unique.** Clips find their joints by name, so two joints with one name would make a clip move the wrong one.
- **Every influence names a joint of the skin.** The skinning :term[shader]{id=shader} reads all four influences of a vertex, even with weight zero, and a joint number outside the skin would read outside the matrices.
- **The same file gives the same handles.** Sub-asset keys and entity ids derive from the model's handle, never from a counter.
- **A bad skin never stops the import.** The mesh imports without skinning and the import warns.

:::rule
A bone is not an entity. The pose lives in the animator, and the scene holds no entity for a plain joint, because each one would cost a transform update every frame. The importer follows the rule, and the section on entities shows how. See [skeletons](skeletons.md).
:::

:::rule
Change the importer's output, bump its version. The import records of [importing](../assets/importing.md) compare the version, and a record with another version makes the file import again. Without a bump, projects keep the old output.
:::

## A toy version

The toy decides what is a joint, and which joint is the root motion joint: the one whose motion can move the whole character in a scene, as [root motion](root-motion.md) shows. Its tree has a root `Armature` with a shoulder, an elbow and a wrist, a door that an animation moves, and a body mesh. The door and the elbow share a name. The skin lists the shoulder, the elbow and the wrist.

```cpp sketch="animation-importing-toy.cpp"
#include <algorithm>
#include <cstdio>
#include <set>
#include <string>
#include <vector>

struct Node
{
	std::string Name;
	int Parent = -1;
};

int main()
{
	// The file's node tree: an armature with three bones, an animated door and a body mesh.
	const std::vector<Node> nodes = {
		{ "Armature", -1 }, { "Shoulder", 0 }, { "Elbow", 1 }, { "Wrist", 2 }, { "Elbow", -1 }, { "Body", -1 }
	};
	const std::vector<int> skinJoints = { 1, 2, 3 };
	const std::vector<int> animatedNodes = { 4 };

	// Step 1: mark the skin's joints and the animated nodes, then every ancestor of a marked node.
	std::vector<bool> inSkeleton(nodes.size(), false);
	for (int index : skinJoints)
		inSkeleton[index] = true;
	for (int index : animatedNodes)
		inSkeleton[index] = true;
	for (size_t index = 0; index < nodes.size(); index++)
	{
		if (!inSkeleton[index])
			continue;
		for (int parent = nodes[index].Parent; parent >= 0 && !inSkeleton[parent]; parent = nodes[parent].Parent)
			inSkeleton[parent] = true;
	}

	// Step 2: walk from the roots with a stack, so a parent always gets its joint index before its children.
	std::vector<int> jointOfNode(nodes.size(), -1);
	std::vector<std::string> jointNames;
	std::set<std::string> usedNames;
	std::vector<int> stack;
	for (int root = static_cast<int>(nodes.size()) - 1; root >= 0; root--)
	{
		if (nodes[root].Parent < 0)
			stack.push_back(root);
	}
	while (!stack.empty())
	{
		const int node = stack.back();
		stack.pop_back();
		if (!inSkeleton[node])
			continue;
		std::string name = nodes[node].Name;
		if (!usedNames.insert(name).second)
		{
			name += "_" + std::to_string(node); // Clips find joints by name, so a name must be unique.
			usedNames.insert(name);
		}
		jointOfNode[node] = static_cast<int>(jointNames.size());
		jointNames.push_back(name);
		for (int child = static_cast<int>(nodes.size()) - 1; child >= 0; child--)
		{
			if (nodes[child].Parent == node)
				stack.push_back(child);
		}
	}

	// Step 3: the root motion joint is the topmost joint of any skin: the smallest joint index.
	int rootMotion = static_cast<int>(jointNames.size());
	for (int index : skinJoints)
		rootMotion = std::min(rootMotion, jointOfNode[index]);

	for (size_t joint = 0; joint < jointNames.size(); joint++)
		std::printf("joint %zu: %s\n", joint, jointNames[joint].c_str());
	std::printf("root motion joint: %d (%s)\n", rootMotion, jointNames[rootMotion].c_str());
	return 0;
}
```

```text output-of="animation-importing-toy.cpp"
joint 0: Armature
joint 1: Shoulder
joint 2: Elbow
joint 3: Wrist
joint 4: Elbow_4
root motion joint: 1 (Shoulder)
```

1. **Lines 22–34:** mark the skin's joints and the animated nodes, then every ancestor of a marked node.
2. **Line 55:** a repeated name gets its node number added, because clips find joints by name.
3. **Lines 68–70:** the root motion joint is the smallest joint number of any skin's joints.

The output shows five joints, and the body is not one of them (the walk of lines 36 to 65 skips it). `Armature` is a joint although no skin lists it, because it is an ancestor. The door's name gained its node number, and the root motion joint is the shoulder: the topmost joint of the skin, which has the smallest number. The real code does the same three steps over glTF's own structures.

## Building the skeleton

`ImportSkeleton` runs first. The excerpt marks the nodes: look at the two loops that set `inSkeleton`, and at the ancestor loop that stops at a node that is already marked.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1014-L1052"
std::vector<uint8_t> inSkeleton(m_Data->nodes_count, 0);
bool any = false;
for (cgltf_size skinIndex = 0; skinIndex < m_Data->skins_count; skinIndex++)
{
	const cgltf_skin& skin = m_Data->skins[skinIndex];
	for (cgltf_size joint = 0; joint < skin.joints_count; joint++)
	{
		inSkeleton[cgltf_node_index(m_Data.get(), skin.joints[joint])] = 1;
		any = true;
	}
}
for (cgltf_size animationIndex = 0; animationIndex < m_Data->animations_count; animationIndex++)
{
	const cgltf_animation& animation = m_Data->animations[animationIndex];
	for (cgltf_size channel = 0; channel < animation.channels_count; channel++)
	{
		const cgltf_animation_channel& source = animation.channels[channel];
		if (source.target_node && source.target_path != cgltf_animation_path_type_weights && source.target_path != cgltf_animation_path_type_invalid)
		{
			inSkeleton[cgltf_node_index(m_Data.get(), source.target_node)] = 1;
			any = true;
		}
	}
}
if (!any)
	return;
// Ancestors carry their descendants' transforms: they are joints too (ValidateHierarchy bounded the chains).
for (cgltf_size index = 0; index < m_Data->nodes_count; index++)
{
	if (!inSkeleton[index])
		continue;
	for (const cgltf_node* parent = m_Data->nodes[index].parent; parent; parent = parent->parent)
	{
		uint8_t& marked = inSkeleton[cgltf_node_index(m_Data.get(), parent)];
		if (marked)
			break;
		marked = 1;
	}
}
```

1. **Line 1033:** a channel marks its target node, except channels of morph target weights.
2. **Lines 1045–1050:** walk up from each marked node and stop at the first ancestor that is marked already.

The real code differs from the toy in three ways. A channel that animates morph target weights (blended shapes of a mesh, which Strata does not import) marks no node, because weights move no joint. When nothing is marked, a file with no skin and no animation gets no skeleton at all. And an earlier check, `ValidateHierarchy`, bounded the depth of the tree, so the ancestor walk cannot run away.

The next excerpt numbers the joints. It starts from the model's roots and then from every other node without a parent, because a skin may name nodes outside the scene. It never recurses, so a deep file cannot overflow the call stack.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1056-L1103"
m_NodeJoints.assign(m_Data->nodes_count, c_NoJoint);
std::vector<std::string> names;
std::vector<JointIndex> parents;
std::vector<JointPose> restPose;
std::unordered_set<std::string> usedNames;
std::vector<uint8_t> visited(m_Data->nodes_count, 0);
std::vector<const cgltf_node*> starts = GetRootNodes();
for (cgltf_size index = 0; index < m_Data->nodes_count; index++)
{
	if (!m_Data->nodes[index].parent)
		starts.push_back(&m_Data->nodes[index]);
}
std::vector<const cgltf_node*> stack;
for (const cgltf_node* start : starts)
{
	stack.push_back(start);
	while (!stack.empty())
	{
		const cgltf_node* node = stack.back();
		stack.pop_back();
		const cgltf_size nodeIndex = cgltf_node_index(m_Data.get(), node);
		if (visited[nodeIndex])
			continue;
		visited[nodeIndex] = 1;
		if (!inSkeleton[nodeIndex])
			continue; // Below a node outside the skeleton nothing is in it (ancestors of joints are joints)
		if (names.size() >= Skeleton::c_MaxJoints)
		{
			Warn(fmt::format("The model's skeleton has more than {} joints; skins and animations are not imported", Skeleton::c_MaxJoints));
			m_NodeJoints.clear();
			return;
		}
		// Joint names are unique: clips bind to joints by name.
		std::string name = GetName(node->name, "Node", nodeIndex);
		if (!usedNames.insert(name).second)
		{
			name = fmt::format("{}_{}", name, nodeIndex);
			while (!usedNames.insert(name).second)
				name += "_";
		}
		m_NodeJoints[nodeIndex] = static_cast<JointIndex>(names.size());
		names.push_back(std::move(name));
		parents.push_back(node->parent ? m_NodeJoints[cgltf_node_index(m_Data.get(), node->parent)] : c_NoJoint);
		restPose.push_back(GetNodePose(*node, nodeIndex));
		for (cgltf_size child = node->children_count; child > 0; child--)
			stack.push_back(node->children[child - 1]);
	}
}
```

1. **Lines 1062–1066:** the walk starts at the model's roots, then at every other node without a parent.
2. **Lines 1090–1094:** a repeated name gets the node index, and underscores until it is unique.
3. **Line 1101:** children move onto the stack in reverse, so they come out in file order.

A duplicate name gets the node's index added, and an underscore follows in the rare case that this name is taken too. A skeleton of more than 4,096 joints (`Skeleton::c_MaxJoints`) imports no skeleton, skins or clips, and the import warns. The root motion joint is the smallest joint number among all skins' joints, which is the topmost one, because parents come first. The skeleton then becomes the sub-asset `Skeleton`, whose handle derives from the model's handle and that word alone.

:::example
The test file of `StrataTests/src/Asset/GltfSkinImportTests.cpp` is an arm: a node `Armature` with a chain `Shoulder`, `Elbow`, `Wrist`, a skin that lists the last three, and two animations. The step marks the three skin joints, then marks `Armature` as their ancestor. Parents first gives the joints `Armature`, `Shoulder`, `Elbow`, `Wrist` with the parents none, 0, 1 and 2. The skin's joints are 1, 2 and 3 in skeleton numbers, so the root motion joint is 1: the shoulder. The test `Skinned glTF files import a skeleton, clips and a skinned mesh without skipping anything` checks exactly these lists.
:::

## Building the clips

`ImportAnimations` makes one clip per animation. It first counts how often each name occurs. An animation whose name occurs once gets the key `Animation/<name>`. An animation without a name, or with a name that another animation shares, gets `Animation/<index>`, its place in the file.

The cost is stability: swap the order of two animations without names and their keys, and so their handles, swap too. Give every animation a unique name. The channel loop is the second half.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1628-L1655"
std::vector<AnimationChannelData> channels;
std::set<std::pair<JointIndex, int>> animated;
for (cgltf_size channelIndex = 0; channelIndex < animation.channels_count; channelIndex++)
{
	// A long baked animation is seconds of unpacking and key reduction: checked per channel, and within the
	// reduction.
	if (m_Context.IsCancelled())
		return; // Run fails the import
	const cgltf_animation_channel& source = animation.channels[channelIndex];
	if (source.target_path == cgltf_animation_path_type_weights)
	{
		m_SkippedFeatures.insert("morph target animation");
		continue;
	}
	std::optional<AnimationChannelData> channel = ReadChannel(source, name);
	if (!channel)
		continue;
	const JointIndex joint = m_NodeJoints[cgltf_node_index(m_Data.get(), source.target_node)];
	if (!animated.insert({ joint, static_cast<int>(channel->Path) }).second)
	{
		Warn(fmt::format("Animation '{}' animates the {} of '{}' twice; the first channel is kept", name, AnimationPathToString(channel->Path), channel->Target));
		continue;
	}
	if (!AnimationClip::ReduceKeys(*channel, [this]() { return m_Context.IsCancelled(); }))
		return; // Cancelled: Run fails the import
	channels.push_back(std::move(*channel));
}
if (channels.empty())
```

1. **Line 1637:** a morph target weights channel is skipped and reported.
2. **Line 1646:** a second channel for the same joint and property is a duplicate.
3. **Line 1651:** key reduction asks the cancellation flag as it works.

Two kinds of channel never reach a clip. A weights channel (morph targets) is skipped and recorded in the skipped features. A second channel for the same joint and property is a duplicate: the first is kept and the import warns. Each channel that stays goes through `AnimationClip::ReduceKeys`, which removes keys that :term[interpolation]{id=interpolation} reproduces (see [clips](clips.md)). An animation with no channel left is skipped with a warning.

## Reading the skins

`ReadSkin` validates a skin and returns its binding. A skin needs 1 to 4,096 joints (`MeshSkinBinding::c_MaxJoints`), and every inverse bind matrix must be finite and affine: its fourth row is (0, 0, 0, 1) after rounding. A skin that fails returns an empty binding, its meshes import without skinning and the import warns, so the mesh draws in its :term[bind pose]{id=bind-pose}.

`ReadSkinVertices` reads each vertex's weights. glTF stores up to eight influences in two sets (`JOINTS_0`, `WEIGHTS_0` and `JOINTS_1`, `WEIGHTS_1`), while Strata's skin vertex holds four, so the importer keeps the four strongest. Each kept weight is stored as a 16-bit whole number in 65,535ths, so the four weights of a vertex sum to 65,535. A weight that is negative, not finite or names a joint outside the skin counts as none.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1235-L1285"
		{
			Warn(fmt::format("Primitive '{}' has unreadable joint indices", primitiveName));
			return false;
		}
		for (size_t influence = 0; influence < 4; influence++)
		{
			const float weight = weightValues[vertex][static_cast<int>(influence)];
			// A weight for a joint the skin does not have, or a negative or non-finite one, counts as none.
			const bool valid = std::isfinite(weight) && weight > 0.0f && indices[influence] < jointCount;
			influences[vertex][set * 4 + influence] = Influence { valid ? indices[influence] : 0u, valid ? weight : 0.0f };
		}
	}
	sets++;
}
if (sets == 0)
	return false;
if (sets > 1)
	m_SkippedFeatures.insert("skin influences beyond the four strongest of a vertex");

outVertices.resize(vertexCount);
bool unweighted = false;
for (size_t vertex = 0; vertex < vertexCount; vertex++)
{
	std::array<Influence, 8>& candidates = influences[vertex];
	std::stable_sort(candidates.begin(), candidates.end(), [](const Influence& a, const Influence& b) { return a.Weight > b.Weight; });
	const float total = candidates[0].Weight + candidates[1].Weight + candidates[2].Weight + candidates[3].Weight;
	MeshSkinVertex& skin = outVertices[vertex];
	if (!(total > 0.0f))
	{
		// No influence at all: the vertex follows the skin's first joint.
		unweighted = true;
		skin = MeshSkinVertex();
		continue;
	}
	uint32_t sum = 0;
	for (int influence = 0; influence < 4; influence++)
	{
		skin.Joints[influence] = static_cast<uint16_t>(candidates[static_cast<size_t>(influence)].Joint);
		skin.Weights[influence] = static_cast<uint16_t>(std::lround(candidates[static_cast<size_t>(influence)].Weight / total * 65535.0f));
		sum += skin.Weights[influence];
	}
	// Rounding leaves the sum a few units off: the strongest influence takes the difference.
	skin.Weights[0] = static_cast<uint16_t>(static_cast<int64_t>(skin.Weights[0]) + 65535 - static_cast<int64_t>(sum));
	for (int influence = 0; influence < 4; influence++)
	{
		if (skin.Weights[influence] == 0)
			skin.Joints[influence] = 0;
	}
}
if (unweighted)
	Warn(fmt::format("Primitive '{}' has vertices without skin weights; they follow the skin's first joint", primitiveName));
```

1. **Line 1243:** a weight counts only when it is finite, above zero and names a joint of the skin.
2. **Line 1259:** a :term[stable sort]{id=stable-sort} puts the strongest first, and equal weights keep their order.
3. **Lines 1273–1277:** each share is rounded to 16 bits, and the strongest takes the difference to 65,535.
4. **Line 1281:** a zero weight points at joint 0.

Take five influences with the weights 0.04, 0.50, 0.30, 0.10 and 0.06. The four strongest total 0.96, so the shares are 0.5208, 0.3125, 0.1042 and 0.0625. Times 65,535 and rounded, they are 34,133, 20,480, 6,827 and 4,096. That sum is 65,536, one too many, so the strongest weight becomes 34,132.

A vertex whose four weights total zero has no influence: the skin's first joint moves it and the import warns once per primitive. A zero weight is stored with joint 0, which keeps the contract's rule that every influence names a joint of the skin ([skinning](skinning.md) explains why the shader needs it).

## The model's entities

The last step builds the model as an entity template (see [prefabs](../world/prefabs.md)). The root is the **animator**: the entity with an `AnimatorComponent`, which owns a skeleton and plays clips on it. A mesh that a skin binds becomes a child of the root with a `SkinComponent` that names the root. A joint with content of its own becomes an entity with an `AttachToJointComponent`. A joint without content is no entity.

Content means a rigid mesh, a camera or a light that the :term[import settings]{id=import-settings} allow, or a child that is not a joint. The sword in a hand is the usual case. The `Wrist` joint has a child node `Sword` that draws a mesh, so the `Wrist` becomes an entity that follows its joint, and `Sword` becomes its child.

```cpp src="Strata/src/Strata/Asset/GltfImporter.cpp#L1924-L1963"
const bool skinned = mesh && mesh->Skinned;
const JointIndex joint = skinned ? c_NoJoint : GetNodeJoint(node);
if (joint != c_NoJoint && !HasEntityContent(node))
{
	// Only a joint: its children are joints too, each placed on its own.
	for (cgltf_size child = node.children_count; child > 0; child--)
		stack.push_back(PendingNode { node.children[child - 1], parent, pending.Depth + 1 });
	continue;
}
// Entity ids derive from the model handle, so re-imports produce the same ids.
Entity entity = scene.CreateEntityWithUUID(DeriveSubAssetHandle(m_Context.Handle, fmt::format("Node/{}", nodeIndex)), GetName(node.name, "Node", nodeIndex));
if (!entity)
{
	outError = "the model has more nodes than a scene can hold";
	return false;
}
// Skinned meshes are placed by their joints and joints by the pose, both relative to the model's root (the
// animator), whatever their place in the file's hierarchy.
scene.SetParent(entity, skinned || joint != c_NoJoint ? parent : pending.Parent, false);
SetupEntity(entity, node);
#if ST_WITH_ANIMATION
if (skinned)
	entity.AddComponent<SkinComponent>().Animator = parent.GetUUID();
if (joint != c_NoJoint)
{
	// At the joint's rest pose until the animator poses it.
	AttachToJointComponent& attachment = entity.AddComponent<AttachToJointComponent>();
	attachment.Animator = parent.GetUUID();
	attachment.Joint = m_JointNames[joint];
	TransformComponent& transform = entity.GetComponent<TransformComponent>();
	glm::vec3 translation;
	glm::quat rotation;
	glm::vec3 scale;
	if (Math::DecomposeTransform(m_JointRestModel[joint], translation, rotation, scale))
	{
		transform.Translation = translation;
		transform.Rotation = rotation;
		transform.Scale = scale;
	}
}
```

1. **Line 1926:** a joint without content makes no entity, and its children keep the same parent.
2. **Line 1934:** the entity's id derives from the model's handle and the node's index.
3. **Line 1942:** skinned meshes and joints hang under the root, wherever the file places them.
4. **Lines 1946–1957:** the skin or attachment component names the root, and a joint starts at its :term[rest pose]{id=rest-pose}.

Entity ids come from `DeriveSubAssetHandle` with the key `Node/<index>`, so a second import makes the same ids and the scenes that refer to them stay valid. Each joint entity starts at the joint's :term[rest pose]{id=rest-pose}, so it sits right before any animation plays. After the tree, `BuildModel` gives the root its animator with the skeleton and the first clip (a controller can take over later). The table lists the fields the import sets.

| Component | Field | Value at the import |
| --- | --- | --- |
| `AnimatorComponent` | `Skeleton` | The model's `Skeleton` sub-asset |
| `AnimatorComponent` | `Clip` | The first imported clip, or none |
| `AnimatorComponent` | `Controller` | None: you assign one later |
| `AnimatorComponent` | `Speed`, `Loop`, `PlayOnStart` | The defaults: 1, on, on |
| `AnimatorComponent` | `ApplyRootMotion`, `CullingMode` | The defaults: off, `AlwaysAnimate` |
| `SkinComponent` | `Animator` | The id of the model's :term[root entity]{id=root-entity} |
| `AttachToJointComponent` | `Animator` | The id of the model's root entity |
| `AttachToJointComponent` | `Joint` | The joint's unique name in the skeleton |

What each field does while a scene plays is in [state machines](state-machines.md), [root motion](root-motion.md) and [culling](culling.md).

## The import scale and the loaders

The import setting `Scale` is baked into the content. The root keeps scale 1, and the vertices, joint translations, inverse bind matrices and clips are multiplied instead. The reason is that instances placed in scenes keep their own root transform when you change the setting. The price is that a change of `Scale` imports the model again.

Three :term[loaders]{id=loader} in `Strata/src/Strata/Animation/AnimationRegistration.cpp` read the sub-assets back. The `Skeleton` and `AnimationClip` loaders read cooked binary :term[bytes]{id=byte} that the importer wrote. The `AnimationController` loader reads :term[JSON]{id=json} source, because Strata stores a controller as its source, with no cooked form (extension `.stanimator`).

The importer's version is 11 (`GltfImporter::GetVersion` in `Strata/src/Strata/Asset/GltfImporter.h`). `Docs/Architecture.md` of the engine still says 9: trust the code. Version 8 moved the scale into the content.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| An entity for every node | Engines whose scenes are trees of objects | Every bone can carry anything, and tools show the whole tree | A transform update per bone, every frame |
| A skeleton from the skins only | Simple viewers | A smaller skeleton | Motion of animated nodes that no skin lists |
| Eight influences per vertex | Film :term[renderers]{id=renderer} | Better blends on dense joints | A doubled skin stream for little visible gain |
| The scale on the model's root | Many importers | A setting that is cheap to change | Skins, joints and clips scaled unlike the mesh |

Sources for the engines are in Further reading.

## How it is tested

`StrataTests/src/Asset/GltfSkinImportTests.cpp` holds six cases in the suite `Asset.Gltf`. They import small generated files: an arm with three skin joints and two animations, `Wave` and `Reach`.

- The skeleton case checks the joint names, parents, the root motion joint, the binding and that every vertex's weights sum to 65,535.
- The attachment case puts a sword below the wrist and checks the entities and their `AttachToJointComponent`.
- The stability case imports twice and compares every key, its data and the handles.
- The variants case covers skins without inverse bind matrices and animations without names.
- The broken case feeds bad skins and channels, including a morph weights channel, and expects warnings and no crash.
- The scale case imports at 1.0 and 0.01 and checks that the root stays at scale 1 while the content scales.

Run them with `StrataTests --test-suite=Asset.Gltf`, which also runs the other glTF cases of `StrataTests/src/Asset/GltfImporterTests.cpp`.

## Changing it safely

- Change the output and bump `GetVersion`; the comment above the function lists the reasons since version 6.
- Give a new sub-asset a fixed key and derive its handle from the model's handle, never from a counter.
- Keep every error path a warning, and ask the cancellation flag in any loop that can run for seconds.
- Keep ids derived: a scene saved before the change must find the same entities after it.
- Put new animation code inside `#if ST_WITH_ANIMATION`, so builds without the module compile.

## Summary

- The importer marks the joints of every skin, the animated nodes and their ancestors. It numbers them parents first with a loop and a stack, makes names unique, and takes the topmost skin joint as the root motion joint.
- Each animation becomes a clip with the key `Animation/<name>`, or `Animation/<index>` when its name is missing or shared; weights channels and duplicate channels are skipped.
- A skin imports with 1 to 4,096 joints and affine matrices; each vertex keeps its four strongest weights as 16-bit values that sum to 65,535.
- The root is the animator; skinned meshes get a `SkinComponent`, joints with content get an `AttachToJointComponent` at their rest pose, and plain joints are no entities.
- A change of the importer's output bumps its version, now 11, so projects import their models again.

## Check yourself

1. A glTF file has the node chain `Root`, `Hips`, `Spine`, a skin that lists only `Spine`, and an animation that moves `Root`. Which joints does the skeleton have?

   1. `Spine` only, because only the skin's joints count.
   2. `Root`, `Hips` and `Spine`.
   3. `Spine` and `Root`, the nodes that a skin or an animation names.
   4. No skeleton, because the animation moves a node that no skin lists.

   :::answer{tests="skeleton"}
   The answer is 2. The skin marks `Spine`, the animation marks `Root`, and `Hips` is an ancestor of a marked node. Option 1 forgets the animation and the ancestors, option 3 forgets the ancestors, and option 4 is wrong because animated nodes are marked as well.
   :::

2. A file has two animations named `Walk` and one named `Idle`, in the order walk, idle, walk. What are the three keys?

   :::answer{tests="clips"}
   `Animation/0`, `Animation/Idle` and `Animation/2`. The name `Walk` occurs twice, so both walks use their index in the file.
   :::

3. A vertex has the weights 0.5 and 0.5 for two joints and nothing else. What are the stored 16-bit values?

   :::answer{tests="skins"}
   Each share is 0.5 over the total 1.0, times 65,535, which is 32,767.5. It rounds to 32,768 twice, and the sum is 65,536. The sort keeps the order of equal weights, so the first joint is the strongest and takes the difference: 32,767 and 32,768.
   :::

4. A wrist joint has a child node that draws a sword. Which entities does the import make for the wrist and the sword?

   :::answer{tests="entities"}
   Both become entities. The wrist has a child that is not a joint, so it counts as having content. It becomes an entity under the model's root, with an `AttachToJointComponent` that names the animator and the wrist, placed at the rest pose. The sword is an ordinary child of that entity and follows the wrist through its parent.
   :::

5. A teammate changes how the importer orders joints and commits without a version bump. What happens in a project that already imported its models?

   :::answer{tests="version"}
   The import records still hold version 11, so the editor treats every model as current and keeps the old cooked skeleton, while a new import would give another joint order. The bump makes every record out of date, so each model imports again.
   :::

## Exercises

1. **Basic.** A file has the chain `Armature`, `Shoulder`, `Elbow`, `Wrist` and a skin that lists only `Wrist`. There is no animation. Predict the joint names, their order and the root motion joint.

   :::answer[Worked solution]{tests="skeleton"}
   The skin marks `Wrist`, and the ancestor walk marks `Elbow`, `Shoulder` and `Armature`. The walk from the root numbers them 0 to 3 in chain order. The only skin joint is the wrist, number 3, so it is the topmost joint of any skin and the root motion joint.
   :::

2. **Medium.** Write a program that rounds five influences, 0.04, 0.50, 0.30, 0.10 and 0.06, as the importer does, and prints the four weights and the strongest one after the fix. Predict the values first.

   :::answer[Worked solution]{tests="skins" solution="sketches/animation-importing-quantize.cpp"}
   The four strongest weights total 0.96, so the values are 34,133, 20,480, 6,827 and 4,096, and the sum is one too many. The program does these steps.

   ```cpp sketch="animation-importing-quantize.cpp"
   #include <algorithm>
   #include <array>
   #include <cmath>
   #include <cstdint>
   #include <cstdio>

   struct Influence
   {
   	uint32_t Joint = 0;
   	float Weight = 0.0f;
   };

   int main()
   {
   	// Five influences of one vertex (a skin of 8 joints): the importer keeps the four strongest.
   	std::array<Influence, 8> candidates = {};
   	candidates[0] = { 3, 0.04f };
   	candidates[1] = { 5, 0.50f };
   	candidates[2] = { 2, 0.30f };
   	candidates[3] = { 7, 0.10f };
   	candidates[4] = { 1, 0.06f };

   	std::stable_sort(candidates.begin(), candidates.end(), [](const Influence& a, const Influence& b) { return a.Weight > b.Weight; });
   	const float total = candidates[0].Weight + candidates[1].Weight + candidates[2].Weight + candidates[3].Weight;

   	uint16_t weights[4] = {};
   	uint32_t sum = 0;
   	for (int influence = 0; influence < 4; influence++)
   	{
   		weights[influence] = static_cast<uint16_t>(std::lround(candidates[influence].Weight / total * 65535.0f));
   		sum += weights[influence];
   		std::printf("joint %u: %u\n", candidates[influence].Joint, static_cast<unsigned>(weights[influence]));
   	}
   	std::printf("sum before the fix: %u\n", sum);

   	// Rounding leaves the sum a few units off: the strongest influence takes the difference.
   	weights[0] = static_cast<uint16_t>(static_cast<int64_t>(weights[0]) + 65535 - static_cast<int64_t>(sum));
   	std::printf("strongest after the fix: %u\n", static_cast<unsigned>(weights[0]));
   	return 0;
   }
   ```

   ```text output-of="animation-importing-quantize.cpp"
   joint 5: 34133
   joint 2: 20480
   joint 7: 6827
   joint 1: 4096
   sum before the fix: 65536
   strongest after the fix: 34132
   ```

   1. **Line 23:** the sort puts the strongest influence first, and the fifth one drops out.
   2. **Line 37:** the strongest weight takes the rounding difference.
   :::

3. **Hard.** Trace it yourself: set a breakpoint in `ReadSkinVertices` and run the case `Skinned glTF files import a skeleton, clips and a skinned mesh without skipping anything` in a source build of the engine. Read one vertex's influences before and after the rounding.

   :::answer[Worked solution]{tests="skins"}
   The function is `ReadSkinVertices` in `Strata/src/Strata/Asset/GltfImporter.cpp`, and the case is the first one in `StrataTests/src/Asset/GltfSkinImportTests.cpp`. Stop after the loop that fills `influences`: a vertex of the ring at height 1 holds the weights 128 and 127 of 255, about 0.502 and 0.498. Step over the `stable_sort` and read `candidates`, then step to the line that adds the difference to `skin.Weights[0]`. Because 65,535 is 257 times 255, the rounded shares are 32,896 and 32,639. They already sum to 65,535, so the difference is zero and the strongest weight stays 32,896.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/GltfImporter.cpp`: `ImportSkeleton`, `ImportAnimations`, `ReadSkin`, `ReadSkinVertices`, `AddHierarchy`, `BuildModel`.
- `Strata/src/Strata/Asset/GltfImporter.h`: `GetVersion`.
- `Strata/src/Strata/Animation/AnimationComponents.h`: `AnimatorComponent`, `AttachToJointComponent`; `Strata/src/Strata/Scene/Components.h`: `SkinComponent`.
- `Strata/src/Strata/Animation/AnimationRegistration.cpp`: the three loaders.
- `Strata/src/Strata/Renderer/Mesh.h`: `MeshSkinBinding`, `MeshSkinVertex`.
- `StrataTests/src/Asset/GltfSkinImportTests.cpp`: the six import cases.

## Further reading

- The glTF 2.0 specification, sections on nodes, skins and animations (Khronos Group): the file format itself (intermediate).
- The manuals of other engines on importing skinned models: how they map bones to objects (beginner).
- A graphics textbook on skinning, such as Real-Time Rendering: why four weights per vertex are enough (advanced).
