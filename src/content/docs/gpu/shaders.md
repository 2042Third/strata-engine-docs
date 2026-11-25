---
id: gpu/shaders
title: "Shaders: Slang, the build and the dialect"
description: "How a Strata shader goes from a Slang file to a shader object, and the rules that keep its source portable and correct."
kind: internals
size: L
tracks: [E]
needs: [gpu/vulkan-nvrhi, basics/build, core/first-change]
time: 85
learn:
  - id: build-path
    text: trace a shader from its Slang file through the build to the shader object that the shader library returns
  - id: register-shader
    text: add a shader to the entry list and predict when the build needs a new configure step
  - id: slangc-flags
    text: explain what each flag of the shader compiler does and why Strata leaves other flags out
  - id: dialect
    text: write the HLSL forms that differ silently from GLSL and predict what the wrong form computes
  - id: checks
    text: name the checks that guard the dialect and choose the one that would find a given slip
since: 0.3.0
status: final
---

A :term[shader]{id=shader} is a small program that runs on the :term[graphics card]{id=gpu}, once for every vertex or every pixel. This page follows one
shader from a text file in `Strata/shaders` to the object that the :term[renderer]{id=renderer} binds to a pipeline, and it teaches the rules
of the language the shaders are written in. The page covers how a shader is built, listed, found and checked. It does
not cover how resources reach a shader, which [Binding resources](binding.md) teaches, nor the custom commands of the
build, which belong to [Generated code](../engineering/generated-code.md).

## The problem and how engines solve it

A graphics card cannot read text. It runs :term[machine code]{id=machine-code} of its own maker, and that code differs between makers and
between generations of one maker. A game that must run on all of them cannot ship machine code. :term[Vulkan]{id=vulkan} solves the
problem with a middle form that the driver, the part of the system that talks to the card, turns into machine code
when a pipeline is created.

That form is **SPIR-V**, a compact binary format of numbered instructions that Vulkan accepts as the code of a shader.

Nobody writes SPIR-V by hand, so a :term[compiler]{id=compiler} writes it from a language made for shaders. The oldest such language of
the OpenGL world is **GLSL**, the shading language of OpenGL and Vulkan, which looks like C.

The other big family is **HLSL**, the high-level shading language that Microsoft made for Direct3D. It also looks like
C, but its details differ from GLSL in ways that matter below.

A third choice is **Slang**, a shading language whose compiler, slangc, accepts HLSL notation, adds features of its own,
and writes SPIR-V among other targets.

The second choice is when to compile. A game can ship the source text and compile it while it runs. Or the engine's build
can compile it once and ship the result.

Compiling while the game runs costs time at the first use of every shader,
and that time shows as a stall of a frame. It also puts a compiler in every installed game, and different compiler
versions on different machines produce different code. Compiling in the build costs the engine's developers a build step.
In return, every player runs :term[bytes]{id=byte} that were tested before release.

The table sums up the three languages. A GLSL program reaches Vulkan through the compiler `glslang`. An HLSL program
reaches it through Microsoft's compiler `DXC`, which writes SPIR-V as well as Direct3D code. Strata uses the third
row.

| Choice | Gain | Cost |
| --- | --- | --- |
| GLSL, compiled to SPIR-V | Close to Vulkan; one small tool | Another language for every other platform |
| HLSL through `DXC` | The language of Direct3D; many examples | A large tool to ship or pin |
| Slang | HLSL notation; one pinned compiler for all targets | A younger tool; HLSL rules that GLSL readers must learn |

:::why[Why Strata compiles Slang at build time]
Strata's shaders are HLSL-notation Slang, compiled when the engine is built by one pinned slangc to SPIR-V 1.5,
checked, and embedded in the program as arrays of numbers.

The reasons are three. HLSL notation keeps the road open to
the shader compilers of other platforms. No game ships a compiler, so there is nothing to install and nothing that can
fail on a player's machine. Every configuration, Debug, Release and :term[Dist]{id=dist}, runs the same bytes.

The cost is that every change to a shader needs a build, and that the dialect has traps that GLSL does not have. The rest
of the page is about both.
:::

Before the conversion to Slang, the shaders were GLSL compiled by `glslang`. The conversion was mechanical, which is why a
lighting bug in code that nobody changed can be a conversion slip. The last sections return to that.

## The map

The first picture shows the build of one shader. Read it from the left: the source and the files it includes go into
the compiler, and the compiler writes a raw module. A small host tool of the engine checks and patches that module, and
the result becomes a file and a :term[header]{id=header}. A generated :term[source file]{id=source-file} lists all headers, and the run-time lookup reads that
list.

```mermaid caption="One shader becomes a raw module, a patched module and a header; a generated list of all headers is what the library searches when the renderer asks for a name." alt="A flow from left to right. A source file and the include files go into the compiler, which writes a raw module, and a small tool writes the final module and a header. A generated registry lists all headers, and the library searches it at run time. A dotted arrow shows that one source with extra defines becomes several entries."
flowchart LR
	S["source .slang and includes"] --> C["slangc"] --> R[".raw.spv"] --> T["StrataShaderTool"] --> H[".spv and .h"] --> G["generated registry"] --> L["ShaderLibrary::Get"] --> O["shader object"]
	S -. "defines" .-> V["variants: one source, many entries"] --> C
```

Two words in the picture need a name. An **entry point** is the function of a shader file where the card starts to
run. The compiler needs its name and its stage, vertex or pixel or compute, to make a module.

A **variant** is one more entry that compiles the same source with extra :term[preprocessor]{id=preprocessor} defines, so that one file makes
several shaders that differ in a few lines. The `.raw.spv` file is the compiler's output before the engine's tool
patches it.

Strata keeps all of this in a few places. The sources live in the folder `Strata/shaders`, in folders by use, such as
`Scene`, `PostProcess`, `Effects` and `GI`. The shared include files live in `Strata/shaders/Include`: there are
42 of them. The build rules live in `CMake/StrataShaders.cmake`, the list of
entries in `Strata/CMakeLists.txt`, and the run-time side in `Strata/src/Strata/Renderer/`.

## The contract

The contract has two halves. Callers of the library may assume how a name finds its shader. Writers of shaders must
follow the language rules. Each rule below comes with the mistake that it prevents.

### Names, stages and entry points

A stage file is named `<registered name>.slang`: the file `Scene/Forward.frag.slang` is the source of the shader
`Scene/Forward.frag`. An include file lives in `Include/<Name>.slang` and protects itself with a :term[macro]{id=macro} such as
`STRATA_COMMON_SLANG`. Every stage file begins by including `Include/Common.slang`. The registered name keeps its
suffix, `.vert`, `.frag`, `.comp` or `.geom`, and the library reads the stage from that suffix.

Every entry point is called `main`. That is why the library needs no table of entry names: one name, one function. A
shader that needs values from the previous stage, or system values, declares them as parameters of `main`. A **system
value** is an input or output that the pipeline itself provides or reads, such as `SV_Position`, which carries the final
screen position out of a vertex shader.

The shaders converted from GLSL differ here. They keep GLSL's global variables in a block at the end of
`Include/Common.slang`, named `st_FragCoord`, `st_Position`, `st_VertexIndex` and so on. Each converted file ends with a
small `main` that fills those globals from its real parameters and calls the old body, `st_Main`. A new shader skips that
layer and takes its inputs as parameters.

### Registering a shader

A file in `Strata/shaders` does nothing until its registered name stands in the list `strata_add_shaders` in
`Strata/CMakeLists.txt`. Nothing searches the folder, at run time or at build time. The list is what creates the compile
commands, and :term[CMake]{id=cmake} writes them while it configures. A new line therefore takes effect only after the :term[configure step]{id=configure-step} runs
again: run `cmake --preset <preset>` once more, then build.

CMake also checks the list while it configures. A duplicate registered name, a name without a stage suffix and a missing
source file each stop the configure with a message that names the entry.

The usual mistake is to add a file, build, and then read that the renderer cannot find the name. The file exists, but no
command compiles it, and the generated registry does not mention it.

A variant is one more line of the same list, written `"<source>|<new name>|<defines>"`. The line
`"Scene/Forward.frag|Scene/ForwardGlass.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS"` compiles `Forward.frag.slang`
with two defines under another registered name. Editing an include compiles all shaders again, because every entry
depends on every include. Editing `Forward.frag.slang` compiles its 24 entries again.

### The dialect

HLSL and GLSL look alike, and that is the danger: several forms compile in both languages and mean different things.
Strata's rules list the forms that differ, and each exists because a conversion met it.

- **Multiply with `mul` only when one side is a matrix.** `mul(M, v)` is a matrix times a vector and `mul(A, B)` a
  matrix product. `mul(v, w)` of two vectors is their :term[dot product]{id=dot-product}, and `M * N` multiplies element by element. Both
  compile without a word.
- **Vector comparisons give vectors of booleans.** `a < b` on two `float3` values is three answers. Wrap it in `all()`
  or `any()` where one answer is meant.
- **Matrix constructors take rows.** `float2x2(a, b, c, d)` fills the first row with `a` and `b`, but GLSL's `mat2` fills
  a column. `M[row][col]` indexes a matrix, and a GLSL column is a transposed row.
- **`select` reverses `mix`.** `select(condition, ifTrue, ifFalse)` is GLSL's `mix(ifFalse, ifTrue, condition)`.
- **Compute shaders read with `SampleLevel` or `Load`.** `Sample` needs derivatives in compute, a capability that a
  device need not have. [Compute shaders](compute.md) teaches this.
- **Vertex and instance numbers come from `SV_VulkanVertexID` and `SV_VulkanInstanceID`.** Strata indexes its draw list by the
  instance number plus the base instance, and `SV_InstanceID` leaves the base out. [Batching](../draw/batching.md) shows
  the draw list.
- **Storage images state their format** with `[vk::image_format("...")]`, and bindless reads index with
  `NonUniformResourceIndex`. The word `precise` marks math that the compiler must not fuse or put in another order.
- **Constants are `static const`.** Generics, modules, interfaces and extensions are not used. `__target_switch` and
  `spirv_asm` appear only in `Include/Common.slang`, each with an HLSL form. Those are Slang's own features, and using
  them elsewhere would close the road to other compilers.

:::example[What the wrong form computes]
Take two vectors, v = (1, 2, 3) and w = (4, 5, 6). The dot product is 1 × 4 + 2 × 5 + 3 × 6 = 32, a single number. A
shader that meant a per-component product wanted (4, 10, 18).

Now take two 2×2 matrices, A with rows (1, 2) and (3, 4)
and B with rows (5, 6) and (7, 8). The element-by-element product `A * B` has rows (5, 12) and (21, 32). The matrix
product `mul(A, B)` has the first row (1 × 5 + 2 × 7, 1 × 6 + 2 × 8) = (19, 22). Its second row is (3 × 5 + 4 × 7,
3 × 6 + 4 × 8) = (43, 50).
:::

The program below does that arithmetic. Look at the three results: the dot product has no vector shape, and the two
matrix results differ in every element.

```cpp sketch="gpu-shaders-traps.cpp"
#include <cstdio>

struct Vec3
{
	float X;
	float Y;
	float Z;
};

struct Mat2
{
	float M[2][2]; // M[row][column], the order of HLSL's float2x2(...)
};

// What HLSL's mul(v, w) of two vectors does: a dot product, one number.
static float MulVectors(const Vec3& v, const Vec3& w)
{
	return v.X * w.X + v.Y * w.Y + v.Z * w.Z;
}

// What HLSL's M * N does: each element times its partner.
static Mat2 Componentwise(const Mat2& a, const Mat2& b)
{
	Mat2 result;
	for (int row = 0; row < 2; row++)
		for (int column = 0; column < 2; column++)
			result.M[row][column] = a.M[row][column] * b.M[row][column];
	return result;
}

// What HLSL's mul(A, B) does: the matrix product.
static Mat2 MatrixProduct(const Mat2& a, const Mat2& b)
{
	Mat2 result;
	for (int row = 0; row < 2; row++)
		for (int column = 0; column < 2; column++)
			result.M[row][column] = a.M[row][0] * b.M[0][column] + a.M[row][1] * b.M[1][column];
	return result;
}

static void Print(const char* label, const Mat2& m)
{
	std::printf("%s: [%g %g] [%g %g]\n", label, m.M[0][0], m.M[0][1], m.M[1][0], m.M[1][1]);
}

int main()
{
	const Vec3 v = { 1.0f, 2.0f, 3.0f };
	const Vec3 w = { 4.0f, 5.0f, 6.0f };
	std::printf("mul(v, w) = %g, one number where a vector was meant\n", MulVectors(v, w));

	const Mat2 a = { { { 1.0f, 2.0f }, { 3.0f, 4.0f } } };
	const Mat2 b = { { { 5.0f, 6.0f }, { 7.0f, 8.0f } } };
	Print("A * B  ", Componentwise(a, b));
	Print("mul(A,B)", MatrixProduct(a, b));
	return 0;
}
```

```text output-of="gpu-shaders-traps.cpp"
mul(v, w) = 32, one number where a vector was meant
A * B  : [5 12] [21 32]
mul(A,B): [19 22] [43 50]
```

1. **Line 16:** the function does what `mul(v, w)` of two vectors does: one number comes out.
2. **Line 22:** each element meets only its partner, as with `M * N` in a shader.
3. **Line 32:** the matrix product sums a row times a column, which is what `mul(A, B)` means.

A shader that mixes up the forms returns plausible values of the wrong kind. The same trap holds for :term[constructors]{id=constructor}. In
HLSL, `float2x2(1, 2, 3, 4)` has the rows (1, 2) and (3, 4). GLSL's `mat2(1, 2, 3, 4)` has the columns (1, 2) and (3, 4),
which as rows are (1, 3) and (2, 4). Multiplied with the vector (1, 1), the GLSL matrix gives (4, 6) and the HLSL one
(3, 7).

:::rule[Rule of the engine: `mul` only with a matrix]
`AGENTS.md` keeps the shader rules short, and `Docs/DeveloperGuide.md` states them in full: vector comparisons through
`all()` and `any()`, row constructors, the order of `select`, and `mul` only with a matrix. The reason is that none of
the wrong forms is an error.
:::

#### The bug that passed every test

The conversion met one slip that compiled, ran and passed every graphics test: a `mul` of two vectors. In the filter of
the local lights' shadows it collapsed the filter into a dot product, a single number where a pattern of samples was
meant. Only a look-dev picture, a capture of a whole lit scene, showed the shadows going wrong. The last
sections return to how such a slip is found.

#### Derivatives and discard

A **derivative** says how fast a value changes from one pixel to its neighbour. The card computes it by comparing a pixel
with its neighbours in a block of 2 by 2 pixels called a quad, so every pixel of the quad must run. Sampling a texture
without an explicit level uses derivatives to choose a mip level.

A **discard** is the pixel shader statement that ends the run of one pixel without writing a colour. If one pixel of a
quad discards before the others have sampled, the derivatives of the rest are undefined. Some open-source Linux drivers
drop the discarded pixel from the quad, and edges come out with wrong widths and wrong mip levels. :term[MoltenVK]{id=moltenvk} keeps the
pixel, so no image on macOS shows the mistake.

The rule is that fragment shaders take every derivative before their first `discard` or `clip`. Either sample every texture
before any discard, or fold the coverage into the result and discard once, last. `Architecture.Shaders` reads every fragment
shader's source for this.

## A toy version

The toy has the same two halves as the real thing: a gradient shader, and a small library that finds a module by name,
takes the stage from the suffix, and keeps what it made. The shader is a fullscreen gradient. The vertex shader gives
every pixel its place `uv`, from 0 to 1 across the image, and the pixel shader turns that into a colour. At the pixel
(0.25, 0.75) the colour is (0.25, 0.75, 0.25) in display values, before the conversion to linear light.

```slang sketch="gpu-shaders-gradient.frag.slang"
#include "Include/Common.slang"

// A fullscreen gradient: the vertex shader hands over the pixel's place in the image, uv, from 0 to 1.
float4 main([[vk::location(0)]] float2 uv : TEXCOORD0) : SV_Target0
{
	float3 display = float3(uv.x, uv.y, 0.25);
	return float4(SRGBToLinear(display), 1.0);
}
```

The shader takes its input as a parameter of `main`, as the rules say new shaders do, and includes `Common.slang` first.
It needs one line in the list: add `Toy/Gradient.frag` below the other shaders of the one existing `strata_add_shaders`
call, re-run configure, then build. A second call would fail, because the generated registry defines the lookup functions
and only one target may hold them.

```cmake
strata_add_shaders(Strata_Renderer
	SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/shaders"
	SHADERS
		PostProcess/Fullscreen.vert
		Toy/Gradient.frag
```

Now the library. The program below stands in for the build with a hand-written registry of two modules. It finds a
name, reads the stage from the suffix, creates the entry once, and answers the second request from its cache. Watch
the count of created entries: it stays at 1 for the second request, and the unknown name creates nothing.

```cpp sketch="gpu-shaders-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <map>
#include <mutex>
#include <string>
#include <string_view>
#include <vector>

enum class ShaderStage
{
	None,
	Vertex,
	Pixel,
	Compute
};

// What the build would generate: a name and the words of its module.
struct EmbeddedShader
{
	std::string_view Name;
	std::vector<uint32_t> Words;
};

static const std::vector<EmbeddedShader> s_Registry = {
	{ "PostProcess/Fullscreen.vert", { 0x07230203, 0x00010500, 1, 2, 3 } },
	{ "Toy/Gradient.frag", { 0x07230203, 0x00010500, 4, 5 } },
};

class ToyShaderLibrary
{
public:
	static ShaderStage GetStageFromName(std::string_view name)
	{
		auto endsWith = [name](std::string_view suffix)
		{
			return name.size() >= suffix.size() && name.substr(name.size() - suffix.size()) == suffix;
		};
		if (endsWith(".vert"))
			return ShaderStage::Vertex;
		if (endsWith(".frag"))
			return ShaderStage::Pixel;
		if (endsWith(".comp"))
			return ShaderStage::Compute;
		return ShaderStage::None;
	}

	// Returns the stage of the named shader, or None when the name is unknown.
	ShaderStage Get(std::string_view name)
	{
		std::scoped_lock<std::mutex> lock(m_Mutex);
		auto cached = m_Stages.find(std::string(name));
		if (cached != m_Stages.end())
			return cached->second;

		for (const EmbeddedShader& embedded : s_Registry)
		{
			if (embedded.Name != name)
				continue;
			m_Created++;
			return m_Stages.emplace(std::string(name), GetStageFromName(name)).first->second;
		}
		return ShaderStage::None;
	}

	int GetCreatedCount() const { return m_Created; }

private:
	std::mutex m_Mutex;
	std::map<std::string, ShaderStage> m_Stages;
	int m_Created = 0;
};

int main()
{
	ToyShaderLibrary library;
	const char* names[] = { "PostProcess/Fullscreen.vert", "PostProcess/Fullscreen.vert", "Toy/Missing.frag" };
	for (const char* name : names)
	{
		const ShaderStage stage = library.Get(name);
		std::printf("%s: stage %d, objects created so far: %d\n", name, static_cast<int>(stage), library.GetCreatedCount());
	}
	return 0;
}
```

```text output-of="gpu-shaders-toy.cpp"
PostProcess/Fullscreen.vert: stage 1, objects created so far: 1
PostProcess/Fullscreen.vert: stage 1, objects created so far: 1
Toy/Missing.frag: stage 0, objects created so far: 1
```

1. **Line 24:** the registry is a table of names and words. The build writes the real one.
2. **Lines 34–44:** the stage comes from the end of the name, as in the real library.
3. **Line 50:** one :term[mutex]{id=mutex} guards the cache, because several threads may ask for shaders.
4. **Line 59:** an entry is created only once for a name, and every later request returns the same one.

The output shows both facts: the vertex stage, and one created entry for two requests. The unknown name returns no stage,
and the caller decides what to do.

The real library differs in four ways. Its registry is generated and holds real
modules. It creates the object through the graphics device. It keeps a list of names that tests mark as unavailable. It
logs every failure.

## The real code

### The entry list

The list in `Strata/CMakeLists.txt` is plain text that CMake reads. A variant names its source, its new name and its
defines. The excerpt shows the first variants.

```text src="Strata/CMakeLists.txt#L178-L185"
VARIANTS
	"Scene/Forward.frag|Scene/ForwardTransparent.frag|ST_FORWARD_TRANSPARENT"
	"Scene/Forward.frag|Scene/ForwardGlass.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS"
	"Scene/Forward.frag|Scene/ForwardGlassNoEntityIDs.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_NO_ENTITY_IDS"
	"Scene/Forward.frag|Scene/ForwardGlassVelocity.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_VELOCITY"
	"Scene/Forward.frag|Scene/ForwardGlassNoEntityIDsVelocity.frag|ST_FORWARD_TRANSPARENT,ST_FORWARD_GLASS,ST_NO_ENTITY_IDS,ST_VELOCITY"
	"Scene/Forward.frag|Scene/ForwardAreaLights.frag|ST_AREA_LIGHTS"
	"Scene/Forward.frag|Scene/ForwardTransparentAreaLights.frag|ST_FORWARD_TRANSPARENT,ST_AREA_LIGHTS"
```

Each line holds the source, the new registered name and the defines, separated by bars. The names show what variants are
for: the same lighting code with or without the transparent, glass, velocity and area-light features.

### A converted entry point

`PostProcess/Fullscreen.vert` draws one triangle that covers the screen, with no vertex buffer. The excerpt is the whole
file. Look at the end: `main` fills the globals, calls `st_Main`, and copies the results into a structure that carries
the semantics. The file includes `Common.slang` twice, a leftover of the conversion that the include's guard makes
harmless.

```slang src="Strata/shaders/PostProcess/Fullscreen.vert.slang#L1-L33"
#include "Include/Common.slang"

#include "Include/Common.slang"

// Fullscreen triangle without vertex buffers: draw 3 vertices.
static float2 v_UV;

void st_Main()
{
	float2 ndc = float2(float((st_VertexIndex << 1) & 2), float(st_VertexIndex & 2)) * 2.0 - 1.0;
	v_UV = NDCToUV(ndc);
	st_Position = float4(ndc, 0.0, 1.0);
}

// --- Entry point ---
struct ST_Input
{
};
struct ST_Output
{
	[[vk::location(0)]] float2 v_UV : TEXCOORD0;
	float4 st_Position : SV_Position;
};
ST_Output main(ST_Input input, int vertexIndex : SV_VulkanVertexID, int instanceIndex : SV_VulkanInstanceID)
{
	st_VertexIndex = vertexIndex;
	st_InstanceIndex = instanceIndex;
	st_Main();
	ST_Output output;
	output.v_UV = v_UV;
	output.st_Position = st_Position;
	return output;
}
```

1. **Line 10:** the vertex number alone gives the corner. The number 0 gives (-1, -1), the number 1 gives (3, -1) and
   the number 2 gives (-1, 3), a triangle larger than the screen, so every pixel is inside it.
2. **Line 11:** `NDCToUV` turns the corner (-1, -1) into the texture position (0, 1).
3. **Lines 21–22:** the structure names the outputs: `v_UV` at location 0 for the pixel shader, and the position as a
   system value.
4. **Line 24:** the entry point is `main`, and the vertex and instance numbers are the Vulkan system values.
5. **Lines 26–28:** the globals are filled before the old body runs.

### The flags

The next excerpt is the build's side. Its comments give the reason of each flag, and `slangFlags` is the list.

```cmake src="CMake/StrataShaders.cmake#L64-L86"
# slangc's flags (Docs/DeveloperGuide.md, "Shaders", says why each is or is not passed):
# - SPIR-V 1.5: Vulkan 1.2's highest, the version the engine's modules always had.
# - Column-major matrices: glm's bytes in every buffer.
# - NVRHI's VulkanBindingOffsets: register(tN) is binding N, sN 128 + N, bN 256 + N, uN 384 + N; spaceS is set S.
# - A storage image without [vk::image_format] is Unknown, not a format Slang guesses from its element type (a silent
#   mismatch with the view); Unknown needs a capability Renderer.ShaderModules rejects, so every one states its format.
# - Warning 39001 (explicit binding overlap) is wrong here: passes that include a header for its helpers declare their
#   own resources at slots the header gives to resources they never read, in separate binding layouts;
#   Renderer.ShaderModules checks that no module binds two used variables to one slot.
# - Warning 41012 (profile implicitly upgraded) is wrong here: Slang widens the profile by the capability atoms of the
#   intrinsics an entry calls, which are not what the module declares; Renderer.ShaderModules checks the declared
#   capabilities against what the device enables.
# - Shaders follow the C++ warning policy.
# Not passed: -fvk-invert-y and -fvk-use-dx-position-w (NVRHI already flips the viewport), -fvk-use-dx-layout and
# -fvk-use-scalar-layout (they would change the std140/std430 offsets the C++ structs follow), -g (outputs would depend
# on the configuration and the source paths), -O (Slang's default), -source-embed-style (it would write the header
# before StrataShaderTool's patch), -depfile (every entry depends on every include), -emit-spirv-via-glsl.
set(slangFlags -target spirv -profile spirv_1_5 -matrix-layout-column-major
	-fvk-t-shift 0 all -fvk-s-shift 128 all -fvk-b-shift 256 all -fvk-u-shift 384 all
	-default-image-format-unknown -warnings-disable 39001,41012)
if(STRATA_WARNINGS_AS_ERRORS)
	list(APPEND slangFlags -warnings-as-errors all)
endif()
```

1. **Lines 65–67:** the SPIR-V version, the :term[matrix order]{id=matrix-order} and :term[NVRHI's]{id=nvrhi} binding offsets, with their reasons.
2. **Lines 68–69:** a storage image must state its format, so that no format is guessed.
3. **Lines 70–75:** the two warnings that are switched off, each with the check that replaces it.
4. **Lines 77–80:** the flags that are not passed, with a reason each.
5. **Lines 81–86:** the list itself: `-fvk-*-shift` moves the register classes, and every other warning is an error when
   the option for warnings as errors is on.

`-target spirv` picks the output format. `-profile spirv_1_5` is the highest version of SPIR-V that Vulkan 1.2 accepts,
and the version the engine's modules always had. `-matrix-layout-column-major` stores the matrices in every buffer in
the :term[byte order]{id=endianness} of glm, the C++ math library, so a matrix copied from C++ is read correctly.

The four `-fvk-*-shift` flags move the register classes into the ranges that :term[NVRHI's]{id=nvrhi} Vulkan backend expects:
`register(t3)` becomes binding 3, `s3` becomes 131, `b3` becomes 259 and `u3` becomes 387. [Binding
resources](binding.md) teaches why. `-default-image-format-unknown` stops Slang from guessing the format of a storage
image from its element type, which would hide a disagreement with the view.

Two warnings are switched off, each with a reason. Warning 39001 reports an explicit binding overlap.

Passes that include
a header for its helpers declare their own resources at slots that the header gives to resources they never read, in
separate binding layouts, so the warning is wrong here. Warning 41012 reports a profile upgrade. Slang widens the
profile by the capabilities of the functions an entry calls, which is not what the module declares. `Renderer.ShaderModules`
checks both facts properly.

:::why[The flags Strata does not pass]
`-fvk-invert-y` and `-fvk-use-dx-position-w` stay out because NVRHI already flips the viewport. `-fvk-use-dx-layout` and
`-fvk-use-scalar-layout` would move buffer offsets away from the layouts that the C++ :term[structs]{id=struct} follow. `-g` would make
the output depend on the configuration and on source paths, while the aim is the same bytes everywhere. `-O` is Slang's
default already.

`-source-embed-style` would write a header before the engine's tool patches the module, and `-depfile`
is not needed because every entry depends on every include. The cost of these choices is that each is a decision that
someone must remember when the compiler changes.
:::

### The shared include

`Include/Common.slang` is the first include of every stage file. Its first lines give the register convention, the
constants, the conversion from device coordinates to texture coordinates, and the :term[sRGB transfer functions]{id=srgb-transfer-function}.

```slang src="Strata/shaders/Include/Common.slang#L4-L39"
// Bindings are HLSL registers: register(tN) sampled textures and read-only buffers, sN samplers, bN constant buffers, uN
// storage images and read-write buffers; spaceS is descriptor set S, the binding set's position in the pipeline state. The
// build shifts each class to NVRHI's Vulkan ranges, t +0, s +128, b +256, u +384 (VulkanBindingOffsets,
// CMake/StrataShaders.cmake).

static const float PI = 3.14159265358979323846;
static const float TWO_PI = 6.28318530717958647692;
static const float INV_PI = 0.31830988618379067154;

// Fullscreen-pass UV from NDC. NVRHI flips the Vulkan viewport to the D3D convention: NDC +Y is up and
// texture/framebuffer row 0 is at the top.
float2 NDCToUV(float2 ndc)
{
	return float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
}

float2 UVToNDC(float2 uv)
{
	return float2(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
}

// sRGB transfer functions (IEC 61966-2-1).
float3 LinearToSRGB(float3 color)
{
	color = max(color, float3(0.0));
	float3 low = color * 12.92;
	float3 high = 1.055 * pow(color, float3(1.0 / 2.4)) - 0.055;
	return select((color <= float3(0.0031308)), low, high);
}

float3 SRGBToLinear(float3 color)
{
	float3 low = color / 12.92;
	float3 high = pow((color + 0.055) / 1.055, float3(2.4));
	return select((color <= float3(0.04045)), low, high);
}
```

1. **Lines 4–7:** the register convention: `t`, `s`, `b` and `u` classes, shifted by the build into NVRHI's ranges.
2. **Lines 13–18:** `NDCToUV` is the formula of every fullscreen pass. NVRHI flips the viewport to the Direct3D
   convention, so +Y is up and row 0 of a texture is at the top.
3. **Lines 26–39:** the two :term[sRGB]{id=srgb} functions use `select`, whose order is the reverse of `mix`.

At the device corner (-1, 1), the top left of the screen, `NDCToUV` returns (0, 0). `SanitizeHDR`, which follows in the
file, keeps infinite and not-a-number values out of high-range targets; [the lighting page](../light/brdf.md) teaches it.

The file's one use of the features that Strata otherwise forbids is the pair of :term[half-float]{id=half-float} functions.

```slang src="Strata/shaders/Include/Common.slang#L194-L215"
// Slang lowers f32tof16 and f16tof32 to 16-bit floats on SPIR-V (Float16, which the engine's device does not enable).
uint PackHalf2x16(float2 value)
{
	__target_switch
	{
	case spirv:
		return spirv_asm { result:$$uint = OpExtInst glsl450 PackHalf2x16 $value };
	default:
		return f32tof16(value.x) | (f32tof16(value.y) << 16);
	}
}

float2 UnpackHalf2x16(uint value)
{
	__target_switch
	{
	case spirv:
		return spirv_asm { result:$$float2 = OpExtInst glsl450 UnpackHalf2x16 $value };
	default:
		return float2(f16tof32(value & 65535u), f16tof32(value >> 16));
	}
}
```

1. **Line 194:** the comment gives the reason: Slang makes 16-bit floats of `f32tof16`, a capability the device does not
   enable.
2. **Lines 197–202:** the `__target_switch` writes the SPIR-V instruction in `spirv_asm` and gives every other target the
   plain HLSL form after `default:`. That `default` is what lets `slangc -target hlsl` pass.

### The registry's interface

The generated registry is one source file in the build folder, and a header in the engine declares what it offers. The
excerpt is that header's contract. Each module is a name, a pointer to its words and a size in bytes.

```cpp src="Strata/src/Strata/Renderer/EmbeddedShaders.h#L11-L23"
// SPIR-V compiled at build time from Strata/shaders (see CMake/StrataShaders.cmake).
struct EmbeddedShader
{
	std::string_view Name; // Path relative to Strata/shaders, e.g. "ImGui.vert"
	const uint32_t* Code = nullptr;
	size_t Size = 0;       // Bytes
};

namespace EmbeddedShaders
{
	std::span<const EmbeddedShader> GetAll(); // Defined by the generated registry source
	const EmbeddedShader* Find(std::string_view name);
}
```

1. **Lines 12–16:** an embedded shader is a name and the bytes of its module, and the name is a path relative to
   `Strata/shaders`.
2. **Line 21:** `GetAll` is defined by the generated file, which lists every header the build wrote.
3. **Line 22:** `Find` searches that list by registered name, and returns no pointer for a name that is absent.

### The library

The library finds a module by its registered name in four steps: the cache, the embedded registry, the stage and the
device. Look at where each failure logs and returns no handle.

```cpp src="Strata/src/Strata/Renderer/ShaderLibrary.cpp#L47-L87" symbol="ShaderLibrary::Get"
nvrhi::ShaderHandle ShaderLibrary::Get(std::string_view name)
{
	std::scoped_lock<std::mutex> lock(m_Mutex);
	const std::string key(name);
	if (!m_Unavailable.empty() && m_Unavailable.contains(key))
	{
		ST_CORE_ERROR("Shader '{}' is unavailable", name);
		return nullptr;
	}
	auto it = m_Shaders.find(key);
	if (it != m_Shaders.end())
		return it->second;

	const EmbeddedShader* embedded = EmbeddedShaders::Find(name);
	if (!embedded)
	{
		ST_CORE_ERROR("Shader '{}' is not part of the engine's embedded shaders", name);
		return nullptr;
	}

	const nvrhi::ShaderType stage = GetStageFromName(name);
	if (stage == nvrhi::ShaderType::None)
	{
		ST_CORE_ERROR("Cannot determine the stage of shader '{}'", name);
		return nullptr;
	}

	nvrhi::ShaderDesc desc;
	desc.shaderType = stage;
	desc.debugName = key;
	desc.entryName = "main";
	nvrhi::ShaderHandle shader = m_Device->createShader(desc, embedded->Code, embedded->Size);
	if (!shader)
	{
		ST_CORE_ERROR("Failed to create shader '{}'", name);
		return nullptr;
	}

	m_Shaders.emplace(key, shader);
	return shader;
}
```

1. **Line 49:** one lock covers the cache, so two threads never create the same shader twice.
2. **Lines 51–58:** a name that tests marked unavailable fails first, and a cached shader returns at once.
3. **Lines 60–65:** `EmbeddedShaders::Find` searches the generated registry; a missing name is logged and returns no handle.
4. **Lines 67–72:** the suffix gives the stage, and a name without one fails.
5. **Lines 74–78:** the entry name is always `main`, and the device creates the shader from the module's words.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Compile shaders while the game runs | OpenGL, whose drivers compile GLSL text | Code specialised to the machine and the state | Stalls, a compiler in every game, different bytes per machine |
| GLSL with `glslang` | Strata before the conversion | A shorter road to Vulkan | The road to other platforms' compilers |
| HLSL through `DXC` | Programs of Direct3D, whose language is HLSL | A large body of examples | A bigger tool to pin on every platform |
| Search the folder for shaders | Engines that compile on demand | No list to maintain | Compile commands that must exist at configure time |
| Pass `-g` for debug information | Debug builds of many programs | Source lines in graphics debuggers | Different bytes in each configuration |

## How it is tested

Strata guards the dialect with several checks, each aimed at one slip.

- `Architecture.Shaders` reads the sources: derivatives before the first discard, Slang sources only, HLSL notation with
  target switches only in `Include/Common.slang` and no GLSL left. It needs no graphics card.
- `Renderer.ShaderModules` reads the embedded modules: SPIR-V 1.5, entry point `main` of the name's stage, only
  capabilities that every accepted device enables, and invariant positions in the four `Scene/Mesh*.vert` entries. It
  also checks that no two used variables share one slot, and that every scene vertex shader reads exactly the inputs that its
  vertex layout provides.
- `Renderer.ShaderTool` tests the engine's host tool.
- `GPU.Renderer` creates every module under the :term[validation layer]{id=validation-layer}, so a module that the driver rejects fails there.
- `StrataShaders.TargetHLSL` runs `slangc -target hlsl` over every entry. It has no label, so every continuous
  integration (CI) job that runs the tests runs it, and a `spirv_asm` outside a `__target_switch` with a default case
  fails there.
- Outside the test program, CI's Linux job runs `spirv-val` on the final modules. Its macOS job converts every module to
  Metal and compiles it, with a list of known failures that only shrinks.

Run one suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Architecture.Shaders`, or all tests with
`ctest --preset windows-debug`. None of these checks finds the `mul` bug of the earlier section, because that bug is a
valid program that computes the wrong thing.

## Changing it safely

To add a shader, write the stage file, list its registered name, re-run configure and build. A new scene vertex shader
also gets a line in `Strata/src/Strata/Renderer/SceneVertexLayouts.h`, because `Renderer.ShaderModules` compares its
inputs with that layout. The registers and push constants of its pipeline belong to [Binding resources](binding.md).

When an image changes where no code did, suspect a conversion slip. Capture the suspect build with
`Tools/LookDev.py capture`, then compare it with the saved set of the earlier release using `compare --signed-gain 32`.
Then study the signed images for a pattern. A region of one sign that follows a shape, a light's reach, a shadow's rim or
a surface material points at a line of the conversion. The look-dev harness is the subject of [Look-dev](../engineering/look-dev.md).

A Direct3D-style target would still need five things. `SV_VulkanInstanceID` and `SV_VulkanVertexID` would be replaced,
with the base instance passed another way. The push constant blocks would get registers from their C++ slots.

NVRHI's
`registerSpace` would carry set 1, and HLSL's constant buffer packing, which differs from std140, would need care. Each element of the forward variants'
reflection probe buffer, 3,600 bytes, would have to fit in the 2,048 bytes that `DXC` allows. Metal
runs only through the conversion of MoltenVK.

The custom commands and the tool of the build are [Generated code](../engineering/generated-code.md). The compiler's
pinned download is [Third-party code](../engineering/third-party.md), and the shader steps of CI are
[CI](../engineering/ci.md).

## Summary

- A shader goes from `<name>.slang` through slangc, the engine's tool and a generated registry to the object that
  `ShaderLibrary::Get` returns.
- A new shader needs a line in `strata_add_shaders` and a new configure step.
- The flags fix the SPIR-V version, the matrix order, the binding ranges and the storage formats, and the flags that Strata omits
  have reasons.
- The dialect differs from GLSL in `mul`, comparisons, constructors, `select`, instance numbers and derivatives.
- Several checks guard the dialect, and a look-dev compare finds the slips they cannot.

## Check yourself

1. You add `Effects/Haze.frag.slang` and build, but the renderer logs that the shader is not part of the embedded
   shaders. Why? (a) The file needs the suffix `.glsl`. (b) The name is not in `strata_add_shaders`, or configure did not
   run again. (c) `slangc` ignores new files until the next release.

   :::answer{tests="register-shader"}
   (b). The list creates the compile commands at configure time. (a) is wrong because the suffix `.frag` gives the stage.
   (c) is wrong because slangc keeps no memory between builds.
   :::

2. What does `mul(float3(1, 2, 3), float3(2, 0, 1))` compute, and what did the author probably want?

   :::answer{tests="dialect"}
   The call computes the dot product 1 × 2 + 2 × 0 + 3 × 1 = 5, a single number. The author probably wanted a matrix times a
   vector, or the per-component product (2, 0, 3), which `*` writes.
   :::

3. A matrix is written `float2x2(2, 0, 1, 3)` in HLSL. How would GLSL's `mat2` write the same matrix?

   :::answer{tests="dialect"}
   The rows are (2, 0) and (1, 3), so the columns are (2, 1) and (0, 3), and GLSL writes `mat2(2, 1, 0, 3)`.
   :::

4. A shader declares a storage image without `[vk::image_format("...")]`. Which flag causes the problem, and which check
   rejects the module?

   :::answer{tests="slangc-flags checks"}
   The flag `-default-image-format-unknown` makes a missing format Unknown instead of a guess, and
   `Renderer.ShaderModules` rejects a module that needs the capability for it.
   :::

5. A shader draws correctly on macOS, but on Linux its edges come out with wrong widths and wrong mip levels. It
   discards a pixel and then samples a texture without a level. Which rule is broken, and which test reads the sources
   for it?

   :::answer{tests="checks dialect"}
   The derivatives rule: a discard before a derivative leaves the quad's derivatives undefined. Some Linux drivers drop
   the discarded pixel, while MoltenVK keeps it and hides the mistake. `Architecture.Shaders` reads the sources for it.
   :::

6. Which stage does the library choose for `Foo/Bar.comp`, and which entry does it use?

   :::answer{tests="build-path"}
   Compute, and the entry `main`. The suffix `.comp` gives the stage, and every entry point is `main`.
   :::

## Exercises

1. **Basic.** Trace it yourself: find where `PostProcess/Fullscreen.vert` becomes the bytes that `ShaderLibrary::Get`
   returns. Use a breakpoint in `Get`, then step into `EmbeddedShaders::Find`.

   :::answer[Worked solution]{tests="build-path"}
   The registered name stands in the list in `Strata/CMakeLists.txt`. `ShaderLibrary::Get` in
   `Strata/src/Strata/Renderer/ShaderLibrary.cpp` checks the cache, calls `EmbeddedShaders::Find`, reads the stage with
   `GetStageFromName` and calls the device with the entry name `main`. The generated header `PostProcess/Fullscreen.vert.h`
   lies under `EmbeddedShaders` in the `Strata` folder of your own build folder, next to the `.raw.spv` file.
   :::

2. **Medium.** Write a program that prints the result of GLSL's `mat2(1, 2, 3, 4)` times (1, 1), then that of the HLSL
   constructor with the same four numbers, then the constructor that restores the GLSL result.

   :::answer[Worked solution]{tests="dialect" solution="sketches/gpu-shaders-rows.cpp"}
   The first and third matrices have the rows (1, 3) and (2, 4) and give (4, 6). The second has the rows (1, 2) and
   (3, 4) and gives (3, 7).

   ```cpp sketch="gpu-shaders-rows.cpp"
   #include <cstdio>

   struct Vec2
   {
   	float X;
   	float Y;
   };

   // A 2x2 matrix stored by rows, as HLSL's float2x2(a, b, c, d) fills it: first row a, b; second row c, d.
   struct RowMatrix
   {
   	float A;
   	float B;
   	float C;
   	float D;
   };

   static Vec2 Multiply(const RowMatrix& m, const Vec2& v)
   {
   	return { m.A * v.X + m.B * v.Y, m.C * v.X + m.D * v.Y };
   }

   static void Print(const char* label, const Vec2& v)
   {
   	std::printf("%s -> (%g, %g)\n", label, v.X, v.Y);
   }

   int main()
   {
   	const Vec2 v = { 1.0f, 1.0f };

   	// GLSL's mat2(1, 2, 3, 4) fills columns: column 0 is (1, 2), column 1 is (3, 4). As rows that is (1, 3) and (2, 4).
   	const RowMatrix glslMeaning = { 1.0f, 3.0f, 2.0f, 4.0f };
   	Print("GLSL mat2(1, 2, 3, 4) times (1, 1)", Multiply(glslMeaning, v));

   	// The same four numbers typed into HLSL's float2x2 fill rows: a different matrix.
   	const RowMatrix hlslTyped = { 1.0f, 2.0f, 3.0f, 4.0f };
   	Print("HLSL float2x2(1, 2, 3, 4) times (1, 1)", Multiply(hlslTyped, v));

   	// The translation writes the rows out: float2x2(1, 3, 2, 4).
   	const RowMatrix translated = { 1.0f, 3.0f, 2.0f, 4.0f };
   	Print("HLSL float2x2(1, 3, 2, 4) times (1, 1)", Multiply(translated, v));
   	return 0;
   }
   ```

   ```text output-of="gpu-shaders-rows.cpp"
   GLSL mat2(1, 2, 3, 4) times (1, 1) -> (4, 6)
   HLSL float2x2(1, 2, 3, 4) times (1, 1) -> (3, 7)
   HLSL float2x2(1, 3, 2, 4) times (1, 1) -> (4, 6)
   ```

   1. **Line 33:** the GLSL meaning, written as rows.
   2. **Line 37:** the same four numbers typed into HLSL, a different matrix.
   3. **Line 41:** the translation, which writes the rows out.
   :::

3. **Hard.** Write the line that adds a variant of the toy gradient with the define `FLIP_V`, and say what the build
   does when you edit `Common.slang` afterwards.

   :::answer[Worked solution]{tests="register-shader build-path"}
   Add `"Toy/Gradient.frag|Toy/GradientFlip.frag|FLIP_V"` to `VARIANTS`, and run configure again. The build then has two
   commands for the new name: slangc with `-DFLIP_V`, then the engine's tool. Editing `Common.slang` compiles all shaders
   again, because every entry depends on every include.
   :::

## Where it lives in Strata

- `Strata/shaders/` holds the sources, with `Include/Common.slang` and `PostProcess/Fullscreen.vert.slang`.
- `Strata/CMakeLists.txt` holds the `strata_add_shaders` list, and `CMake/StrataShaders.cmake` the flags.
- `Strata/src/Strata/Renderer/ShaderLibrary.cpp` and `EmbeddedShaders.h` hold the lookup.
- Tests: `Architecture.Shaders`, `Renderer.ShaderModules`, `Renderer.ShaderTool`, `GPU.Renderer` and
  `StrataShaders.TargetHLSL`.

## Further reading

- The SPIR-V specification (Khronos, <https://registry.khronos.org/SPIR-V/>): the instruction set of the format. Advanced.
- The HLSL documentation (<https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl>): the language
  reference of the notation Slang accepts. Intermediate.
- The Slang user guide (shader-slang.org): Slang's features and targets. Intermediate.
