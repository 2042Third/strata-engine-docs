---
id: gpu/binding
title: "Pipelines and binding: layouts, registers and bindless"
description: "How Strata tells the graphics card which resources a draw reads, fixes the rest of its state in one object, and gives every material texture a slot."
kind: internals
size: L
tracks: [E]
needs: [gpu/shaders, gpu/resources-lifetimes]
time: 85
learn:
  - id: register-map
    text: compute the Vulkan set and binding that an HLSL register becomes
  - id: layout-rules
    text: explain why a new scene resource, a push constant and a vertex layout each follow a rule of the contract
  - id: struct-layout
    text: compute the std140 offsets of a struct and find the field that shifts the rest
  - id: pipeline-key
    text: trace how the key of a draw picks a cached pipeline and what a new key costs
  - id: bindless-slot
    text: trace a texture to its bindless slot and explain why the slot waits before it is reused
since: 0.3.0
status: final
---

A draw or a dispatch is useless until the :term[graphics processing unit]{id=gpu} (GPU) knows what it may read and write: which constants, which textures, which buffers, and which vertex streams. This page is about how Strata says so. It covers two things: the binding of resources to the numbered places a :term[shader]{id=shader} reads them from, and the pipeline, one object that fixes everything else about a draw before the draw happens. It does not cover how draws are sorted into batches, what a material holds, or when a resource changes state: those are in [batching](../draw/batching.md), [material data](../light/material-data.md) and [resource lifetimes](resources-lifetimes.md).

## The problem and how engines solve it

A shader is a small program that runs on the GPU. It is compiled once and cannot ask the engine for anything. It reads its inputs from numbered places, so the engine must put each input in the place the shader expects, before the draw starts. Three families of answers exist, and each one fixes a cost of the one before.

The oldest is the **slot** model, used by Direct3D 11. The GPU has a row of numbered slots for textures, another for :term[constant buffers]{id=constant-buffer}, another for samplers. Before each draw you call "put this texture in texture slot 3" for every input that changed. Take a scene with 2,000 objects, each with a material of 4 textures. If every draw sets all 4 again, that is 8,000 calls per frame and 480,000 calls per second at 60 :term[frames per second]{id=frame-rate}.

The driver checks every call, and checking costs processor time.

:term[Vulkan]{id=vulkan} and Direct3D 12 turn that around. A **descriptor** is a small record that tells the GPU where one resource is and how to read it.

A **descriptor set** is a group of descriptors bound with one call. You describe the shape of a set ahead of time and fill it once, so a draw switches a whole group of inputs with one call instead of eight. The cost moves to you: you must build sets, keep them alive while the GPU uses them, and never write one the GPU is reading.

The third family is **bindless**. One big descriptor array holds every texture of the scene, and a shader receives a plain :term[integer]{id=integer}, an index, and reads `textures[index]`. Binding no longer changes between draws that use different textures, so those draws can share one call. The cost is that the array is one shared object with strict rules about when a slot may change. The rest of this page builds that answer in the order a draw meets it.

Two ideas that sound alike are different. A binding model says where a resource is. A pipeline says how the draw is done: shaders, culling, depth test and blending. You need both for a draw, and both are made ahead of time, because making them in the middle of a frame is slow.

## The map: registers, sets and push constants

A shader names its inputs with **registers**, a convention from HLSL (the shading language Slang accepts), as [shaders](shaders.md) shows. A register has a class letter and a number: `t` for sampled textures and read-only buffers, `s` for samplers, `b` for constant buffers and `u` for :term[storage images]{id=uav} and read-write buffers. A register may also name a space: `register(t0, space1)`. The **register and space** pair is the address of an input in the shader. The class and the number choose a place inside a descriptor set, and the space chooses which set.

:::example[Four registers become four bindings]
Vulkan numbers all kinds of binding in one list per set, so `t16` and `b16` would collide. The build adds a shift to each class: t adds 0, s adds 128, b adds 256 and u adds 384. Then `register(t16)` is binding 16, `register(s9)` is binding 137, `register(b0)` is binding 256 and `register(u2)` is binding 386, all in set 0. `register(t0, space1)` is binding 0 in set 1. Each class has room for 128 numbers before it reaches the next.
:::

```mermaid caption="Registers in the shader become bindings in a set. The class letter decides the shift, and the space decides the set. Push constants sit beside the sets." alt="A diagram with three groups. Registers t, s, b and u of space zero go to bindings plus zero, plus 128, plus 256 and plus 384 of set zero, the scene set. The table register of space one goes to set one, the bindless table. Push constants form a third group with no set."
flowchart LR
    T["t N"] -->|"+0"| S0["Set 0: the scene layout"]
    S["s N"] -->|"+128"| S0
    B["b N"] -->|"+256"| S0
    U["u N"] -->|"+384"| S0
    TT["t0 in space1"] -->|"binding 0"| S1["Set 1: the bindless table"]
    PC["Push constants"] -.-> P["No set: written in the command"]
```

Strata's scene passes use two sets. Set 0 is the scene layout, which holds the frame constants, the instance buffers and the lights, and set 1 is the bindless table. A **binding layout** is the shape of a set: which slots exist, of which type, and who may read them.

A **binding set** is a filled-in layout: the actual buffers, textures and samplers in those slots. The position of a layout in the pipeline's list of layouts is its set number, and `desc.bindingLayouts = { m_SceneBindingLayout, Renderer::GetBindlessTextures().GetLayout() }` is how a scene pipeline gets sets 0 and 1.

**Push constants** are a few :term[bytes]{id=byte} written straight into the command stream, with no buffer and no descriptor. They suit one small value that changes per draw. A shadow pass uses one as a four-byte value that names the cascade it draws. In the shader, a push constant is a `[[vk::push_constant]] ConstantBuffer<T>`, and its slot exists only in C++, as `BindingLayoutItem::PushConstants`. :term[NVRHI]{id=nvrhi}, the graphics layer Strata uses, creates no descriptor for it.

A **constant buffer** is a buffer of values a shader reads at a `b` register, the same for every thread of a draw. The scene's is `FrameConstants` at `b0`: the camera matrices, the sun, the fog and the time. Its volatile form, written fresh every frame, is in [resource lifetimes](resources-lifetimes.md). The other shape of input is a structured buffer, an array of records that [compute shaders](compute.md) also use, read at a `t` register.

## The contract: five rules and their reasons

The scene layout is shared by every scene pass, so one change reaches all of them. The layout has a slot list: a comment at the top of `Strata/shaders/Include/Scene.slang` that names every slot in use. Five rules keep it sound.

:::rule[New scene resources take the next free slot; idle passes bind dummies]
The comment in `Include/Scene.slang` names the next free slot of the list, which is 61 at the pin. A pass that does not run still gets its slot filled: it binds a fallback of the right type, such as a black texture of the right dimension. The reason is that one layout serves many passes, so its shape must not change from frame to frame. See [Architecture rules](https://github.com/2042Third/GameEngine/blob/319075e3f92b316db5cdd30560de08c1ffe0ae26/AGENTS.md).
:::

The fallbacks are the 1 by 1 white, black and flat-normal textures and the black cubes and volumes that the :term[renderer]{id=renderer} creates once at startup.

:::rule[A push constant's slot must not equal another layout's constant buffer slot in the same pipeline]
Vulkan itself ignores the number, because a push constant has no descriptor. The slot is still the register a conversion to another graphics interface would give the block, so two blocks on one register would break such a port, and the shadow passes show the pattern. Register `b0` belongs to the frame constants, so the shadow push constant takes slot 1. The rule keeps every constant register of a pipeline unique.
:::

:::rule[A scene vertex shader reads exactly its input layout]
An **input layout** says which vertex streams a draw feeds into the vertex shader: for each attribute, its position in the stream, its type and its format. Strata has four, and each holds exactly what its shaders read, because the :term[validation layer]{id=validation-layer} warns about an attribute that no shader consumes. A new vertex shader gets its line in the table of `SceneVertexLayouts.h`, and a test checks that the shader reads those locations and no others.
:::

The fourth contract rule is a budget. On macOS, :term[MoltenVK]{id=moltenvk}, which translates Vulkan to Metal, limits a shader stage to 31 storage buffers and 16 samplers. The scene set uses 13 storage buffers and 9 samplers, and the GPU culling layout uses 23 storage buffers. A new binding counts against these limits, so a pass that adds a storage buffer to a layout already at 31 would work on a desktop card and fail on macOS.

The last rule is about the layout of data. A constant buffer follows the **std140** rules, and a structured buffer follows **std430**: both are fixed ways to place fields in memory, so that a C++ :term[struct]{id=struct} and a shader struct agree to the byte. Std430 differs from std140 mainly in arrays.

Under std140 a `float3` has the alignment of a `float4`, and an array's element stride rounds up to 16 bytes. Std430 drops the rounding for arrays. Strata keeps every member 16-byte aligned, so most structs behave the same in both. C++ mirrors each struct and a `static_assert` checks its size.

:::example[The vec3 that moves everything after it]
Take a struct with two `float3` fields, `A` then `B`, and a `float`, `C`. On the GPU, `A` is at offset 0, `B` is at 16 (a `float3` starts on a 16-byte boundary), and `C` is at 28 (it fits in the 4 bytes left after `B`'s 12). The size rounds up to 32. In C++ with a plain `glm::vec3`, which is 12 bytes with a 4-byte alignment, `B` is at 12 and `C` at 24. Every field after `A` is 4 bytes off, and nothing fails: the shader reads wrong numbers.
:::

Strata uses `float4` for each field of its large structs, so no field sits where the two rules disagree.

Strata's mirrors are checked by `static_assert(sizeof(FrameConstants) == 8 * 64 + 28 * 16)`: eight 4 by 4 matrices of 64 bytes and 28 four-component values of 16 bytes make 960 bytes. `InstanceData` is 64 bytes: three `float4` rows and four 32-bit integers. When one side changes, the assert fails at :term[compile time]{id=compile-time} and the other side must change with it.

:::question
New to C++ sizes and padding? See [bytes](../basics/bytes.md) and [programming 3](../basics/programming-3.md) first.
:::

## A toy: one layout, one set, one draw

The toy below has the three objects of a binding model and the register shift, and nothing else. A layout lists three slots: a constant buffer, a texture and a sampler. A set names a resource for each slot. `Draw` refuses a set that leaves a slot empty and prints the binding number of each slot. Look at the numbers.

```cpp sketch="gpu-binding-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <vector>

enum class RegisterClass
{
	Texture,
	Sampler,
	ConstantBuffer,
	ReadWrite
};

// The shift the build adds to each register class on Vulkan: t + 0, s + 128, b + 256, u + 384.
constexpr uint32_t GetVulkanBinding(RegisterClass registerClass, uint32_t slot)
{
	constexpr uint32_t c_Shifts[] = { 0, 128, 256, 384 };
	return c_Shifts[static_cast<size_t>(registerClass)] + slot;
}

struct Item
{
	RegisterClass Class;
	uint32_t Slot;
	const char* Resource; // Only the binding set names a resource.
};

using BindingLayout = std::vector<Item>; // The shape the pipeline expects
using BindingSet = std::vector<Item>;    // The resources that fill that shape

// A draw succeeds only when the set fills every slot of the layout.
bool Draw(const char* name, const BindingLayout& layout, const BindingSet& set)
{
	for (const Item& wanted : layout)
	{
		bool found = false;
		for (const Item& given : set)
			found = found || (given.Class == wanted.Class && given.Slot == wanted.Slot);
		if (!found)
		{
			std::printf("%s: no resource for binding %u\n", name, GetVulkanBinding(wanted.Class, wanted.Slot));
			return false;
		}
	}
	for (const Item& given : set)
		std::printf("%s: binding %u <- %s\n", name, GetVulkanBinding(given.Class, given.Slot), given.Resource);
	return true;
}

int main()
{
	const BindingLayout layout = { { RegisterClass::ConstantBuffer, 0, nullptr }, { RegisterClass::Texture, 0, nullptr },
		{ RegisterClass::Sampler, 0, nullptr } };
	const BindingSet complete = { { RegisterClass::ConstantBuffer, 0, "Frame" }, { RegisterClass::Texture, 0, "Albedo" },
		{ RegisterClass::Sampler, 0, "Linear" } };
	const BindingSet missing = { { RegisterClass::ConstantBuffer, 0, "Frame" }, { RegisterClass::Texture, 0, "Albedo" } };
	Draw("complete", layout, complete);
	Draw("missing", layout, missing);
	return 0;
}
```

1. **Lines 14–18:** the shift table of the page, as code: each class has its own start, so slot 0 of a `t` and slot 0 of a `b` get different bindings.
2. **Lines 27–28:** a layout and a set have the same shape. The layout leaves `Resource` empty, and the set fills it.
3. **Lines 33–43:** every slot the layout wants must appear in the set, or the draw stops before it starts.
4. **Line 40:** the message names the Vulkan binding, not the register, since that is the number the GPU sees.

The first draw binds all three: the constant buffer at 256, the texture at 0 and the sampler at 128. The second draw misses its sampler and stops at binding 128.

The real code differs in three ways. The layout also says which shader stages may read each slot. The set is made by the device, which checks its resources against the layout. And the real draw is recorded into a :term[command list]{id=command-list}, so the check happens when the set is made, not when the draw runs.

## Pipelines: everything fixed in one object

A **pipeline**, also called a pipeline state object, is one object that holds everything fixed about a draw. That is the shaders, the input layout, the binding layouts, the culling, the depth test, the blending and the shape of the target. You make it ahead of time because the driver must translate all of those into the code of the GPU, which takes milliseconds. A draw then switches state with one call.

Strata has several kinds of draw, and each needs a different pipeline. The scene's variants are described by a **pipeline key**, a small struct whose fields choose the variant: `PassType`, `DoubleSided`, `Mirrored`, `Skinned`, `Velocity`, `Surface`, `Field` and `AreaLights`. `GetScenePipeline(key)` searches a vector of past keys, and on a miss it builds the pipeline from the key and stores it. Each renderer keeps its own vector.

The quote below is the first part of that function: the key's last field, the search, then the vertex shader and the input layout. Look at how each choice follows from the key and nothing else.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2484-L2514"
nvrhi::IGraphicsPipeline* SceneRenderer::GetScenePipeline(const PipelineKey& requested)
{
	// The forward passes of a frame whose scene has a rect light take the shaders' forms that shade them, and its prepass with
	// the surface target the form that marks light surfaces.
	PipelineKey key = requested;
	key.AreaLights = m_AreaLightsFrame && (key.PassType == Pass::Opaque || key.PassType == Pass::Transparent || key.PassType == Pass::Glass
		|| (key.PassType == Pass::Prepass && key.Surface));
	for (const auto& [cachedKey, pipeline] : m_ScenePipelines)
	{
		if (cachedKey == key)
			return pipeline;
	}

	const bool backFacePass = key.PassType == Pass::LocalShadowBack || key.PassType == Pass::LocalShadowBackMasked;
	const bool localShadowPass = key.PassType == Pass::LocalShadow || key.PassType == Pass::LocalShadowMasked || backFacePass;
	const bool shadowPass = key.PassType == Pass::Shadow || key.PassType == Pass::ShadowMasked || localShadowPass;
	const bool selectionMask = key.PassType == Pass::SelectionMask;
	nvrhi::GraphicsPipelineDesc desc;
	desc.primType = nvrhi::PrimitiveType::TriangleList;
	if (localShadowPass)
		desc.VS = key.Skinned ? m_SkinnedLocalShadowVertexShader : m_LocalShadowVertexShader;
	else if (key.Skinned)
		desc.VS = shadowPass ? m_SkinnedShadowVertexShader : (key.Velocity ? m_SkinnedMeshVelocityVertexShader : m_SkinnedMeshVertexShader);
	else
		desc.VS = shadowPass ? m_ShadowVertexShader : (key.Velocity ? m_MeshVelocityVertexShader : m_MeshVertexShader);
	// The layout follows the vertex shader (the shader library names each shader by its entry), so that no pass
	// can give a shader attributes it does not read.
	const std::optional<SceneVertexLayout> vertexLayout = FindSceneVertexLayout(desc.VS->getDesc().debugName);
	ST_CORE_VERIFY(vertexLayout.has_value(), "SceneRenderer: vertex shader '{}' has no entry in c_SceneVertexEntries",
		desc.VS->getDesc().debugName);
	desc.inputLayout = m_SceneInputLayouts[static_cast<size_t>(*vertexLayout)];
```

1. **Lines 2488–2490:** the function, not the caller, sets `AreaLights` from the frame, so a caller's key never has to know the scene's lights.
2. **Lines 2491–2495:** the cache search. A key that is already in the vector returns its pipeline at once.
3. **Lines 2497–2500:** the passes that draw the back faces for local shadows count as local shadow passes.
4. **Lines 2503–2508:** the vertex shader follows the pass, then `Skinned`, then `Velocity`.
5. **Lines 2511–2514:** the input layout comes from the shader's name, and a name missing from the table stops the program.

The vertex shader depends on the pass and the key: a shadow shader for shadow passes, a velocity shader when motion vectors are on, a skinned one for posed meshes. The input layout is then found from the vertex shader's name, never chosen by the pass, so no pass can feed a shader attributes it does not read. The table behind that lookup is `SceneVertexLayouts.h`.

```cpp src="Strata/src/Strata/Renderer/SceneVertexLayouts.h#L69-L89"
constexpr SceneVertexEntry c_SceneVertexEntries[] = {
	{ "Scene/Mesh.vert", SceneVertexLayout::Mesh },
	{ "Scene/MeshVelocity.vert", SceneVertexLayout::Mesh },
	{ "Scene/MeshSkinned.vert", SceneVertexLayout::SkinnedMesh },
	{ "Scene/MeshSkinnedVelocity.vert", SceneVertexLayout::SkinnedMesh },
	{ "Scene/ShadowMesh.vert", SceneVertexLayout::Shadow },
	{ "Scene/LocalShadowMesh.vert", SceneVertexLayout::Shadow },
	{ "Scene/ShadowMeshSkinned.vert", SceneVertexLayout::SkinnedShadow },
	{ "Scene/LocalShadowMeshSkinned.vert", SceneVertexLayout::SkinnedShadow },
};

// The layout scene pipelines with this vertex shader use, or nullopt for a shader c_SceneVertexEntries does not list.
constexpr std::optional<SceneVertexLayout> FindSceneVertexLayout(std::string_view vertexShader)
{
	for (const SceneVertexEntry& entry : c_SceneVertexEntries)
	{
		if (entry.Shader == vertexShader)
			return entry.Layout;
	}
	return std::nullopt;
}
```

1. **Lines 69–78:** each vertex shader's embedded name beside one of the four layouts.
2. **Lines 80–89:** the lookup returns no value for a shader that is not listed, and the caller then stops with a message.

Because the tables are `constexpr`, the :term[compiler]{id=compiler} checks their shape. The test `Scene vertex shaders read exactly the attributes of their input layout` of the suite `Renderer.ShaderModules` parses the compiled shaders and compares their input locations with the table. NVRHI numbers a layout's attributes from 0 in order, so attribute 3 is read at location 3.

The second part chooses the pixel shader of each pass and the binding layouts. Look at the small helper that every forward pass goes through.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2515-L2557"
// The forward passes' form: with the rect lights' shading (PipelineKey::AreaLights), global illumination's field
// (PipelineKey::Field), both or neither.
const auto forwardShader = [&key](const nvrhi::ShaderHandle& plain, const nvrhi::ShaderHandle& field, const nvrhi::ShaderHandle& area,
	const nvrhi::ShaderHandle& areaField) -> nvrhi::IShader*
{
	if (key.AreaLights)
		return key.Field ? areaField.Get() : area.Get();
	return key.Field ? field.Get() : plain.Get();
};
switch (key.PassType)
{
	case Pass::Prepass:
		if (key.Surface)
			desc.PS = key.AreaLights ? m_PrepassSurfaceAreaPixelShader : m_PrepassSurfacePixelShader;
		else
			desc.PS = key.Velocity ? m_PrepassVelocityPixelShader : m_PrepassPixelShader;
		break;
	case Pass::ShadowMasked:
	case Pass::LocalShadowMasked:
	case Pass::LocalShadowBackMasked: desc.PS = m_ShadowMaskPixelShader; break;
	case Pass::Shadow:
	case Pass::LocalShadow:
	case Pass::LocalShadowBack: desc.PS = nullptr; break; // Depth only
	case Pass::Transparent:  desc.PS = forwardShader(m_ForwardTransparentPixelShader, m_ForwardTransparentFieldPixelShader,
		m_ForwardTransparentAreaPixelShader, m_ForwardTransparentAreaFieldPixelShader); break;
	case Pass::Glass:
		if (key.Velocity)
			desc.PS = forwardShader(m_GlassVelocityPixelShader, m_GlassVelocityFieldPixelShader, m_GlassVelocityAreaPixelShader,
				m_GlassVelocityAreaFieldPixelShader);
		else
			desc.PS = forwardShader(m_GlassPixelShader, m_GlassFieldPixelShader, m_GlassAreaPixelShader, m_GlassAreaFieldPixelShader);
		break;
	case Pass::Opaque:
		desc.PS = forwardShader(m_ForwardPixelShader, m_ForwardFieldPixelShader, m_ForwardAreaPixelShader, m_ForwardAreaFieldPixelShader);
		break;
	case Pass::SelectionMask: desc.PS = m_SelectionMaskPixelShader; break;
	case Pass::Wireframe:    desc.PS = m_WireframePixelShader; break;
}
desc.bindingLayouts = { m_SceneBindingLayout, Renderer::GetBindlessTextures().GetLayout() };
if (shadowPass)
	desc.bindingLayouts.push_back(m_ShadowPushLayout);
if (key.PassType == Pass::Wireframe)
	desc.bindingLayouts.push_back(m_WireframePushLayout);
```

1. **Lines 2517–2523:** the helper picks one of four forms of a forward shader: plain, with the field of global illumination, with area lights, or with both.
2. **Lines 2526–2531:** the prepass takes its form from `Surface`, `AreaLights` and `Velocity`.
3. **Lines 2532–2537:** the masked shadow passes test the material's alpha, and the others write depth only, with no pixel shader.
4. **Lines 2538–2551:** the forward passes go through the helper; the selection mask and the `Wireframe` pass have their own shaders.
5. **Lines 2553–2557:** sets 0 and 1 of every scene pipeline; a shadow pass adds its push layout, and the `Wireframe` pass its own.

The four forms exist so that a frame pays only for what its scene uses. A frame without global illumination or area lights draws with the plain shaders, which hold no code of either. The price is in the key: each such field doubles the pipelines a pass can need.

The third part sets the fixed-function state.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2558-L2603"
// Front faces are counter-clockwise; a mirroring transform reverses the winding on screen, and so do the back faces' passes
// (they cull the front faces).
desc.renderState.rasterState.setFrontCounterClockwise(key.Mirrored == backFacePass);
if (key.DoubleSided)
	desc.renderState.rasterState.setCullNone();
else
	desc.renderState.rasterState.setCullBack();

// Reversed-Z: nearer surfaces have larger depth values.
nvrhi::DepthStencilState& depth = desc.renderState.depthStencilState;
depth.setDepthTestEnable(true);
switch (key.PassType)
{
	case Pass::Prepass:
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		break;
	case Pass::Shadow:
	case Pass::ShadowMasked:
	case Pass::LocalShadow:
	case Pass::LocalShadowMasked:
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		// Push stored depth away from the light against shadow acne. NVRHI enables the depth bias only with a
		// non-zero constant part, which also keeps the slope part working.
		desc.renderState.rasterState.setDepthBias(c_ShadowDepthBias).setSlopeScaleDepthBias(c_ShadowSlopeDepthBias);
		break;
	case Pass::LocalShadowBack:
	case Pass::LocalShadowBackMasked:
		// Where the back faces are, unbiased: the filter counts a path's point as inside a solid only before the back face,
		// so a bias toward the light thins the solids the paths at a box's foot cross, and one away from it thickens
		// them into the space beside. No acne follows: the filter never compares a receiver with the back faces alone.
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		break;
	case Pass::Opaque:
		depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::Equal);
		break;
	case Pass::Glass:
		// Not in the prepass (its depth would hide what lies behind from the scene-color copy): it writes its own, so the
		// blended surfaces behind it stay hidden and the TAA and the overlays see it. No blending: HDR alpha 1.
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		break;
	case Pass::SelectionMask:
		// The selected surfaces where nothing is in front of them, drawn with the camera's own matrices against the
		// jittered depth: with its bias.
		depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		SetJitteredDepthBias(desc.renderState.rasterState);
		break;
```

1. **Lines 2558–2564:** the winding flips for a mirrored instance and for the back-face passes, and a double-sided key turns culling off.
2. **Lines 2566–2568:** the depth test is on for every pass, and nearer means larger.
3. **Lines 2571–2582:** the prepass and the shadow passes write depth; the shadow passes also add a bias.
4. **Lines 2583–2592:** the back-face passes write depth with no bias, and the forward pass writes none and accepts only depth equal to the prepass.
5. **Lines 2593–2603:** glass and the selection mask each choose their own depth rule, with the reason in a comment.

Culling and winding come from the key. Front faces are counter-clockwise, as in [coordinates](coordinates.md), and a mirrored instance reverses the winding on screen, so `Mirrored` flips the rule rather than the mesh; that is the subject of [mirrors](../draw/mirrors-camera-relative.md). Depth is reversed: nearer surfaces have larger values, so the test keeps a fragment when its depth is greater than or equal to the stored one. The depth prepass and the shadow passes write depth. The forward pass writes none and keeps only a fragment equal to the prepass's depth, so the vertex shaders of both passes must produce identical positions.

The shadow passes add a depth bias that pushes stored depth away from the light, which hides false dark patches on lit surfaces. The back-face passes of local shadows flip the winding as well, so they keep the back faces and drop the front ones, and they add no bias.

The last part handles the `Wireframe` pass, transparent surfaces and the creation call.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2604-L2644"
	case Pass::Wireframe:
	{
		// The triangles' edges where nothing is in front of them, blended over the image: drawn with the camera's own matrices
		// against the frame's (jittered, with TAA) depth with its bias, which also lifts the edges off their own surfaces.
		desc.renderState.rasterState.setFillWireframe();
		depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		SetJitteredDepthBias(desc.renderState.rasterState);
		nvrhi::BlendState::RenderTarget blend;
		blend.setBlendEnable(true)
			.setSrcBlend(nvrhi::BlendFactor::SrcAlpha)
			.setDestBlend(nvrhi::BlendFactor::InvSrcAlpha)
			.setSrcBlendAlpha(nvrhi::BlendFactor::One)
			.setDestBlendAlpha(nvrhi::BlendFactor::InvSrcAlpha);
		desc.renderState.blendState.setRenderTarget(0, blend);
		break;
	}
	case Pass::Transparent:
	{
		depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		// The HDR target's alpha becomes the transmittance through the blended surfaces, the product of their 1 - alpha
		// (1 where there are none: everything before writes 1), which the TAA reads as how much of a pixel has no motion
		// of its own.
		nvrhi::BlendState::RenderTarget blend;
		blend.setBlendEnable(true)
			.setSrcBlend(nvrhi::BlendFactor::SrcAlpha)
			.setDestBlend(nvrhi::BlendFactor::InvSrcAlpha)
			.setSrcBlendAlpha(nvrhi::BlendFactor::Zero)
			.setDestBlendAlpha(nvrhi::BlendFactor::InvSrcAlpha);
		desc.renderState.blendState.setRenderTarget(0, blend);
		break;
	}
}

nvrhi::IFramebuffer* framebuffer = localShadowPass ? m_LocalShadowFramebuffer.Get() : shadowPass ? m_ShadowFramebuffers[0].Get()
	: (key.PassType == Pass::Prepass ? (key.Surface ? m_SurfacePrepassFramebuffer.Get() : key.Velocity ? m_MotionPrepassFramebuffer.Get() : m_PrepassFramebuffer.Get())
	: (selectionMask ? m_SelectionMaskFramebuffer.Get() : key.PassType == Pass::Wireframe ? m_OverlayFramebuffer.Get()
	: (key.PassType == Pass::Glass ? (key.Velocity ? m_GlassMotionFramebuffer.Get() : m_GlassFramebuffer.Get()) : m_ForwardFramebuffer.Get())));
nvrhi::GraphicsPipelineHandle pipeline = m_Device->createGraphicsPipeline(desc, framebuffer->getFramebufferInfo());
ST_CORE_VERIFY(pipeline, "SceneRenderer: failed to create a scene pipeline");
m_ScenePipelines.emplace_back(key, pipeline);
return pipeline;
```

1. **Lines 2604–2619:** the `Wireframe` pass draws only the edges of triangles, tests depth without writing it, and blends over the image.
2. **Lines 2623–2625:** the comment says why the target's alpha holds a product of transmittances.
3. **Lines 2626–2632:** color blends by source alpha. The alpha channel multiplies the old value by one minus source alpha.
4. **Lines 2637–2641:** the target description comes from the pass's render target, and the device builds the pipeline here.
5. **Lines 2642–2644:** a failed build stops the program, and a good one joins the cache.

A transparent surface blends its color with the standard source-alpha rule. For the alpha channel the source factor is zero, and the old alpha is multiplied by one minus the surface's alpha. The result is the product of the surfaces' transmittance, and where nothing blended it stays 1. Temporal anti-aliasing later reads that alpha as how much of the pixel has no motion of its own.

Fullscreen passes use no key. `GetFullscreenPipeline` takes a cache of pairs of target description and pipeline, and it makes a pipeline when a pass meets a target format it has not met. All use the same :term[fullscreen triangle]{id=fullscreen-triangle} vertex shader, which builds three corners from their index and needs no vertex buffer. Their pipelines never hide back faces and never test depth.

### When pipelines are made

The cache fills lazily. Strata makes a scene pipeline the first time a frame draws its key, while the draws are recorded: line 2149 of `SceneRenderer.cpp` is the call, in the loop over buckets of draws. A key that is new in a running game therefore compiles inside that frame.

NVRHI creates one in-memory Vulkan pipeline cache per device. It starts empty, and nothing in `Strata/src` saves or loads one. So every run pays for every compile again, and the frame that meets a new key also waits for its compile.

Compute pipelines follow another rule. The renderer makes them when it makes its resources, through `SceneRenderer::CreateComputePipeline(shader, layout)`. A shader that is missing there stops the program with `ST_CORE_VERIFY`, because a renderer without its passes has nothing useful to draw.

## Bindless textures: one table for every material

Each material samples several textures, and each scene draw wants its own. In a binding-set model, a draw whose material differs from the last must switch sets, and every switch breaks a batch. A texture array, one binding that holds N images of the same size, cuts the switches but forces equal sizes and formats.

Virtual texturing cuts a large virtual image into pages that a feedback pass loads. It removes the limit, but it needs an extra lookup for every sample and a feedback pass. Descriptor indexing lets a shader index an array of different textures. Strata uses it and calls the result **bindless**: the shader reads `u_Textures[slot]`, and the slot is only a number stored in material data.

The table is `BindlessTextureTable`: one array of sampled 2D textures in set 1. Descriptors of a normal set are written before a command list is recorded and never again while the list may run. A table of this kind has two flags that lift that rule.

**Update-after-bind** lets you write a descriptor after the set was bound. **Partially bound** lets some slots stay empty, as long as no shader reads them. Both are needed here: textures arrive at any frame, and a table of 32,768 slots is mostly empty.

:::example[Slot life of one texture]
Frames in flight is 2 (see [how a GPU frame works](how-a-gpu-frame-works.md)). A texture finishes loading in frame 10 and takes slot 40. A better version streams in during frame 20: the table allocates slot 41 and releases slot 40. Commands of frames up to 20 may still sample slot 40, and they are all finished when frame 23 starts, since 20 + 2 + 1 = 23. Until then slot 40 keeps its old texture and frames from 21 on read slot 41; from frame 23 slot 40 is free.
:::

The function `Allocate` gives a slot to a texture. Search for the place where the descriptor is written, and for what happens when the table is full.

```cpp src="Strata/src/Strata/Renderer/BindlessTextureTable.cpp#L39-L69" symbol="BindlessTextureTable::Allocate"
uint32_t BindlessTextureTable::Allocate(nvrhi::ITexture* texture)
{
	if (!texture)
		return c_InvalidSlot;

	std::scoped_lock<std::mutex> lock(m_Mutex);
	uint32_t slot = c_InvalidSlot;
	if (!m_FreeSlots.empty())
	{
		slot = m_FreeSlots.back();
		m_FreeSlots.pop_back();
	}
	else if (m_NextSlot < m_MaxCapacity)
	{
		slot = m_NextSlot++;
		if (slot >= m_SlotTextures.size())
			GrowLocked(slot + 1);
	}

	if (slot == c_InvalidSlot)
	{
		ST_CORE_ERROR("Bindless texture table is full ({} slots)", m_MaxCapacity);
		return c_InvalidSlot;
	}

	m_SlotTextures[slot] = texture;
	m_SlotAllocated[slot] = true;
	m_Device->writeDescriptorTable(m_Table, nvrhi::BindingSetItem::Texture_SRV(slot, texture));
	m_Allocated++;
	return slot;
}
```

1. **Lines 44–56:** under one lock, take a slot from the :term[free list]{id=free-list} or the next unused one, growing the table when needed.
2. **Lines 58–62:** a full table logs an error and returns the invalid slot.
3. **Lines 64–67:** the table keeps the texture and writes its descriptor, the only write an allocated slot gets.

The function takes a free slot first, and only then the next unused one; it grows the table on demand, and it logs an error when the table is full. It writes an allocated slot's descriptor exactly once, here, under a :term[mutex]{id=mutex}, because any thread may finish loading a texture. The slot holds a strong reference to the texture, so the texture cannot be destroyed while the slot exists.

```cpp src="Strata/src/Strata/Renderer/BindlessTextureTable.cpp#L95-L108" symbol="BindlessTextureTable::BeginFrame"
void BindlessTextureTable::BeginFrame(uint64_t frameIndex)
{
	std::scoped_lock<std::mutex> lock(m_Mutex);
	m_CurrentFrame = frameIndex;
	// A slot released during frame F may be sampled by frames up to F, which have all completed once the device
	// has started frame F + framesInFlight + 1 (BeginFrame waits for frame slots before we get here).
	while (!m_PendingReleases.empty() && m_PendingReleases.front().Frame + m_FramesInFlight + 1 <= frameIndex)
	{
		const uint32_t slot = m_PendingReleases.front().Slot;
		m_PendingReleases.pop_front();
		m_SlotTextures[slot] = nullptr;
		m_FreeSlots.push_back(slot);
	}
}
```

1. **Lines 99–101:** the condition that frees a slot: its release frame plus frames in flight plus one has come.
2. **Lines 103–106:** only then does the slot drop its texture and join the free list.

`Release` does not free a slot; it queues it with the frame number. `BeginFrame` returns a slot to the :term[free list]{id=free-list} when `Frame + framesInFlight + 1 <= frameIndex`. That is the rule of the example. Slots 0, 1 and 2 are reserved: white, black and flat normal, written once at startup by `SetReservedTexture`, so a material that lacks a texture can point at them.

The table starts at 1,024 slots. `GrowLocked` doubles the capacity until it covers the slot asked for, at most the maximum. Doubling keeps the growth to a handful of steps, and the existing descriptors stay, because growing the table keeps them.

### How big the table may be

The maximum is 32,768, or less. At startup the device asks Vulkan whether a set of that size is allowed. If the answer is no, the size halves until the answer is yes or 1,024 is reached.

MoltenVK is the exception. Its query counts every set against a limit of 1,212 descriptors, even for update-after-bind sets, so it rejects tables that it samples correctly. There the table keeps the size the other limits allow, and the validation layer's complaint about the rejected query is only traced. The tests of `Renderer.BindlessSupport` cover those three paths.

### A full table

When all slots are taken, `Allocate` returns an invalid slot and logs the error. A texture that is finishing its load then fails to load. A texture that streams in more levels keeps the levels it has, since the swap fails and the old slot stays. A full table is a loss of quality, not a crash.

### The texture table: slots that move, materials that do not

A slot changes whenever a texture's levels change, since a replaced texture takes a new slot. If a material stored the slot, every streaming step would have to rewrite the material. Strata puts one more step between them.

The **texture table** is an array of entries, one per texture, indexed by a number that stays the same for the texture's whole life. A material stores that index, and the entry holds the current bindless slot. The entry is one 32-bit word: the slot in bits 0 to 23, the sampler in bits 24 to 30 and a flag for gray textures in bit 31. Beside it sits a minimum level of detail, used to fade in new levels.

```mermaid caption="A material stores a stable index. The entry of that index follows the texture's slot, which changes when more detail streams in, so the material never changes." alt="A chain of boxes. A material holds the index of a texture. The index selects an entry in the texture table. The entry holds a bindless slot, and the slot selects a texture in the bindless table. After a swap, the same index points to a new slot and a new texture."
flowchart LR
    M["Material: texture index 7"] --> E["Texture table entry 7"]
    E -->|"slot 40, then 41"| T["Bindless table: texture"]
```

Strata keeps that table in a structured buffer at `t16` and writes only the entries that changed. Indices 0 to 2 mean the same fallbacks as the reserved slots. Mip streaming changes the entries every frame; that process is in [mip streaming](../draw/mip-streaming.md).

The shader reads them in one function.

```cpp src="Strata/shaders/Include/MaterialTextures.slang#L16-L22"
float4 SampleMaterialTexture(uint textureIndex, float2 uv)
{
	uint2 entry = u_TextureTable[textureIndex];
	uint packedSlot = entry.x;
	uint slot = packedSlot & 0xFFFFFFu;
	uint samplerIndex = min((packedSlot >> 24) & 0x7Fu, uint(ST_SAMPLER_COUNT - 1));
	float minLod = asfloat(entry.y);
```

The function reads the entry, splits the slot and the sampler out of it, and the later lines index `u_Textures[NonUniformResourceIndex(slot)]`. That call is needed because neighboring pixels may carry different slots. The GPU assumes an index is the same across a group of threads unless you say otherwise. The sampler index is clamped to the scene's six material samplers.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Slot binding per draw | Direct3D 11 renderers | Simple code, no lifetime rules for sets | One call per input and per draw; no batching across materials |
| One set per material | Many Vulkan engines | No shared table to manage; each set lives with its material | Set creation per material, a set switch per material, and a break in every batch |
| Texture arrays | Terrain and tile renderers | A smaller, simpler descriptor than a large table | Equal size and format for every layer, so one 4K texture forces all |
| Virtual texturing | Large open worlds | No limit on texture memory; one binding | A feedback pass, a page cache and an extra lookup for every sample |
| Saved pipeline cache | Many engines on PC and consoles | No compile stall on the second run | A file on disk to version and discard for each driver |

Strata's choice costs a table with strict lifetime rules and a texture table to hide the moves. It gains one call for many materials.

## How it is tested

`Renderer.ShaderModules` parses every embedded shader. One test checks that each scene vertex shader reads exactly its layout's locations, another that no :term[entry point]{id=entry-point-gpu} uses two variables on one slot, and a third that the prepass shaders keep their position invariant.

`GPU.Renderer` has two bindless tests: slots are recycled only after frames in flight, and the table grows up to its capacity. `Renderer.BindlessSupport` checks the size choice with a fake query. The `static_assert` lines check struct sizes at compile time.

Run a suite directly with the doctest filter: `StrataTests.exe --test-suite=Renderer.BindlessSupport`. The GPU suites need a graphics card.

## Changing it safely

To add a scene resource, take the next free slot of the list and write it into the comment in `Include/Scene.slang`. Then add the item to `sceneLayout`, and bind a dummy in each pass that does not produce it. Check the MoltenVK counts.

Add a vertex shader by adding it to `c_SceneVertexEntries` with its layout, and let the test run. Add a pipeline variant as a new field of `PipelineKey`, and decide in `GetScenePipeline` what it changes: each new `bool` doubles the possible keys.

Never write a bindless slot except at allocation, and never keep a slot across frames: ask the texture for its slot every frame, because streaming changes it. Replace a texture through a new slot and a `Release`, not a write over a slot that a frame in flight may sample. Run the `Renderer` and `GPU.Renderer` suites with the validation layer before you commit.

## Summary

- A register becomes a Vulkan binding by adding 0, 128, 256 or 384 for `t`, `s`, `b` or `u`, and the space is the set; set 0 is the scene, set 1 the bindless table.
- A new scene resource takes the next free slot of the list and an idle pass binds a dummy. A push constant avoids other constant buffer slots, and a vertex shader reads exactly its layout.
- The std140 and std430 rules place fields, and C++ mirrors with checked sizes keep the processor and the GPU in agreement.
- The pipeline key picks a cached pipeline, which is built on the first frame that draws the key, so a new key costs a compile inside that frame.
- The bindless table gives every texture a slot, recycles it only frames in flight plus one frames after release, and the texture table hides slot changes from materials.

## Check yourself

1. Which Vulkan set and binding does `register(u2, space0)` become, and which does `register(t5, space1)` become?

   :::answer{tests="register-map"}
   The first is set 0, binding 386 (384 + 2). The second is set 1, binding 5, since `t` adds 0 and space 1 is the bindless table.
   :::

2. A pass declares a push constant at slot 0 in a pipeline whose scene layout has `b0`. Which rule does that break, and why is that rule there?
   - A. The slot must be above 128.
   - B. A push constant's slot must not equal another layout's constant buffer slot.
   - C. A push constant must be at least 16 bytes.

   :::answer{tests="layout-rules"}
   B. There is no limit of 128 (A is wrong) and no minimum size of 16 bytes (C is wrong). Vulkan ignores the number, but a conversion to another interface would give both blocks the register `b0`.
   :::

3. A struct holds `float A; float3 B; float C;` in a constant buffer. Give the offset of each field and the size of the struct, and say which field a plain C++ mirror would misplace.

   :::answer{tests="struct-layout"}
   `A` is at 0, `B` at 16 (a `float3` starts on a 16-byte boundary), `C` at 28, and the size is 32. A plain C++ mirror packs `B` at 4 and `C` at 16, so both are wrong.
   :::

4. A game draws a mesh with a mirrored transform for the first time in a long session. What happens in that frame, and why?

   :::answer{tests="pipeline-key"}
   The key has `Mirrored` true. If no pipeline of that key exists, `GetScenePipeline` builds one while recording the draw, and since nothing loads compiled pipelines from disk and no earlier draw used that key, the compile happens inside the frame.
   :::

5. Frames in flight is 3. A slot is released while frame 50 is current. In which frame does `BeginFrame` first return it to the free list?

   :::answer{tests="bindless-slot"}
   Frame 54: it needs `50 + 3 + 1 <= frameIndex`. Frames up to 50 may still sample the old texture, and they are all finished when frame 54 starts.
   :::

## Exercises

1. **Basic.** Run the sketch below. Predict the four slot numbers before you run it. Then change the frames in flight to 1 and predict again.

   :::answer[Worked solution]{tests="bindless-slot" solution="sketches/gpu-binding-slots.cpp"}
   The first texture takes slot 3, the first free slot after the three reserved ones, and is released in frame 0. With 2 frames in flight it can return at frame 3. So frames 1 and 2 allocate new slots 4 and 5, frame 3 gets slot 3 back, and frame 4 allocates slot 6. With 1 frame in flight the slot returns at frame 2, so the lines are 4, 3, 5, 6.

   ```cpp sketch="gpu-binding-slots.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <deque>
   #include <vector>

   // A table of slots whose reuse waits for the frames that may still read them.
   class SlotTable
   {
   public:
   	explicit SlotTable(uint32_t framesInFlight)
   		: m_FramesInFlight(framesInFlight)
   	{
   	}

   	uint32_t Allocate()
   	{
   		if (m_Free.empty())
   			return m_Next++;
   		const uint32_t slot = m_Free.back();
   		m_Free.pop_back();
   		return slot;
   	}

   	void Release(uint32_t slot) { m_Pending.push_back({ slot, m_Frame }); }

   	void BeginFrame(uint64_t frame)
   	{
   		m_Frame = frame;
   		while (!m_Pending.empty() && m_Pending.front().Frame + m_FramesInFlight + 1 <= frame)
   		{
   			m_Free.push_back(m_Pending.front().Slot);
   			m_Pending.pop_front();
   		}
   	}

   private:
   	struct Pending
   	{
   		uint32_t Slot;
   		uint64_t Frame;
   	};
   	uint32_t m_FramesInFlight;
   	uint32_t m_Next = 3; // Slots 0 to 2 are reserved
   	uint64_t m_Frame = 0;
   	std::vector<uint32_t> m_Free;
   	std::deque<Pending> m_Pending;
   };

   int main()
   {
   	SlotTable table(2);
   	const uint32_t first = table.Allocate();
   	table.Release(first);
   	for (uint64_t frame = 1; frame <= 4; frame++)
   	{
   		table.BeginFrame(frame);
   		std::printf("frame %llu: next slot %u\n", static_cast<unsigned long long>(frame), table.Allocate());
   	}
   	return 0;
   }
   ```

   ```text output-of="gpu-binding-slots.cpp"
   frame 1: next slot 4
   frame 2: next slot 5
   frame 3: next slot 3
   frame 4: next slot 6
   ```

   1. **Line 18:** a new slot comes from `m_Next` only when no slot is free.
   2. **Line 24:** a release stores the frame it happened in, and frees nothing.
   3. **Lines 29–33:** a slot returns to the free list when its release frame plus frames in flight plus one has come.
   4. **Line 43:** the first slot is 3, since 0 to 2 are reserved.
   :::

2. **Medium.** A new scene pass needs a read-only structured buffer that no other pass uses. Which slot does it take, in which register class, and what does the pass that does not run bind?

   :::answer[Worked solution]{tests="layout-rules"}
   The pass takes the next free slot of the list, 61, as `register(t61)` in set 0, so binding 61. Both the shader and the layout in `SceneRenderer.cpp` get it, and the comment in `Include/Scene.slang` is updated. A pass that does not run binds a dummy buffer of the same type. The storage buffer count of the scene set grows from 13 to 14, well under the 31 of MoltenVK.
   :::

3. **Hard.** Trace it yourself: find the bindless slot of a material's base color texture on a source build.

   :::answer[Worked solution]{tests="bindless-slot"}
   Build the source with Debug. Put a breakpoint in `BindlessTextureTable::Allocate` in `Strata/src/Strata/Renderer/BindlessTextureTable.cpp` and load a scene. When the breakpoint hits from `Texture::FinalizeOnMainThread` in `Strata/src/Strata/Renderer/Texture.cpp`, the returned `slot` is the texture's bindless slot. `Texture` then allocates an index in `TextureTable`: find the entry for that index and its low 24 bits equal the slot. A second run that lets mip streaming swap the texture hits `SwapResidentTexture`, and the entry then holds a new slot, while the material's index is unchanged.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `GetScenePipeline`, `GetFullscreenPipeline`, `CreateComputePipeline` and the scene binding layout.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `PipelineKey` and the cache vector.
- `Strata/src/Strata/Renderer/SceneVertexLayouts.h`: the four layouts and the table of vertex shaders.
- `Strata/src/Strata/Renderer/BindlessTextureTable.h` and `.cpp`, and `Strata/src/Strata/Renderer/TextureTable.h`.
- `Strata/shaders/Include/Scene.slang`: the slot list, `FrameConstants`, `InstanceData` and the bindless array.
- `Strata/src/Strata/Renderer/SceneRenderData.h`: the C++ mirrors and their `static_assert` lines.
- Tests: `Renderer.ShaderModules`, `GPU.Renderer`, `Renderer.BindlessSupport`.

## Further reading

- Vulkan specification, descriptor sets and push constants: the reference for the binding model (advanced).
- NVRHI's repository, README and source: how the layers wrap descriptors (intermediate).
- "Vulkan Guide", descriptor indexing: a short tutorial on bindless arrays (intermediate).
