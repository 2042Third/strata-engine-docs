---
id: engineering/generated-code
title: "Generated code: shaders, embedded files, version stamps and committed generators"
description: "How the build writes shader modules, embedded data and version headers, and how the committed generators keep their outputs in the repository."
kind: internals
size: L
tracks: [E]
needs: [engineering/cmake, gpu/shaders]
time: 80
learn:
  - id: follow-shader
    text: trace a shader from its source file to the bytes the renderer looks up
  - id: patch-spirv
    text: write a safe patch of a binary format that collects its edits first and applies them from the back
  - id: change-generator
    text: change a committed generator's output the right way and check it
since: 0.3.0
status: final
---

A :term[game engine]{id=game-engine} contains files that nobody typed: compiled :term[shader]{id=shader} modules, a font turned into numbers, a :term[header]{id=header} that says which commit built the program. This page is about the code and data that the build writes instead of people, and about the generators whose outputs people do commit. It does not teach how to write a shader or what slangc's flags mean; those belong to [the shaders page](../gpu/shaders.md). The page follows one shader from its source to the :term[bytes]{id=byte} the :term[renderer]{id=renderer} finds, then covers the other generated files and the scripts behind the committed ones.

## The problem and how engines solve it

A shader is a small program that runs on the :term[graphics card]{id=gpu}. The card's driver does not read the language you write it in. A :term[compiler]{id=compiler} turns the source into :term[SPIR-V]{id=spir-v}, the binary form that :term[Vulkan]{id=vulkan} accepts. The question is when and where that compile happens. Engines give three answers.

- **Compile at run time.** The engine ships the compiler and the sources, and compiles when the program starts or when a material first needs a shader. Changing a shader needs no rebuild. The costs: the player's machine pays the :term[compile time]{id=compile-time} as a pause, the player must trust the compiler that ships with the game, and a mistake in the source appears on a stranger's computer.
- **Compile offline, load files.** A build step writes one module file per shader and the program reads them from a folder. The player pays nothing. The costs: a game is now an :term[executable]{id=executable} plus a folder that can be missing or out of date, and the engine needs paths.
- **Compile offline, embed.** The build writes each module as an array of numbers in a C++ :term[source file]{id=source-file}, and the compiler places the array inside the executable. The costs: any shader change forces the library that holds them to link again, and the executable grows.

Strata takes the third. A game is then one executable and its asset pack, and a shader that the program names always exists. The embedded bytes also do not depend on the :term[build configuration]{id=build-configuration}: Debug, Release and :term[Dist]{id=dist} hold the same modules, so a test that reads them in Debug tests what ships.

The same question comes up for other data. The default font, a 162,588-byte file, must be available even when no asset pack is loaded. Strata turns it into a C++ array at configure time. Each byte becomes `0x` and two :term[hex]{id=hexadecimal} digits followed by a comma, 32 bytes to a line, so the font becomes 5,081 lines of source: 5,080 full lines and one of 28 bytes. The build compiles that file like any other.

Generated files bring one danger, the one that costs the most time. Suppose a build writes a version header on every run, even when the version has not changed. The file's modification time is new, so the :term[build system]{id=build-system} compiles everything that includes it again. If 300 source files include the header, every build, even one that changed no code, compiles 300 files.

The rule that prevents this: write a generated file only when its content changed. :term[CMake's]{id=cmake} `file(CONFIGURE)` does this for you, because it leaves an existing file alone when the new content is identical. Every generator on this page follows the rule, or uses the command that follows it.

The last kind of generated data is data that no build rule can recreate cheaply: a table that took a long calculation, a texture drawn by a script, a generated sample scene. Strata commits these outputs to the :term[repository]{id=repository} and keeps the script beside them. Section "Committed generators" below defines the term and lists them.

## The map

The diagram shows what a build runs for every shader entry, and which files feed which.

```mermaid caption="From a shader source to the engine: slangc writes a raw module, the shader tool checks and patches it and writes the final module and a header, and a generated registry includes every header. The manifest feeds three side checks." alt="A flow from the Slang source and its includes through slangc to a raw module, then the shader tool, which writes a final module and a header. All headers go into a generated registry compiled into the renderer library. A manifest file lists every entry and feeds three side checks: a SPIR-V validation on Linux, a Metal conversion on macOS and a HLSL target check."
flowchart LR
	S[".slang source and includes"] --> C["slangc"]
	C --> R["name.raw.spv"]
	R --> T["StrataShaderTool"]
	T --> F["name.spv"]
	T --> H["name.h"]
	H --> G["EmbeddedShaderRegistry.cpp"]
	G --> L["Strata_Renderer"]
	M["ShaderEntries.txt"] --> V["spirv-val (Linux)"]
	M --> X["Metal conversion (macOS)"]
	M --> D["HLSL target check"]
```

Everything in the diagram runs on the build machine, in the order the arrows give, on the build system's own threads. The engine's :term[main thread]{id=main-thread} meets the result only at run time: `ShaderLibrary` looks a name up in the registry once and keeps the shader it made. The files `CMake/StrataShaders.cmake` and the folder `CMake/StrataShaderTool/` own the pipeline. Pinning and fetching slangc itself belongs to [the third-party page](../engineering/third-party.md), and the continuous integration (CI) jobs that run the side checks to [the CI page](../engineering/ci.md).

One definition before the details. The **embedded shader registry** is the generated source file `EmbeddedShaderRegistry.cpp`: it includes every shader's header and lists each shader's registered name, array and byte size in one table that the renderer searches at run time.

## The contract

What callers may assume and what a change must do, each with its reason.

1. **A shader has a registered name that ends in its stage.** The path without `.slang` is the name, and the suffix `.vert`, `.frag`, `.comp` or `.geom` gives the stage. The reason: the build and the renderer both derive the stage from the name, so no table of stages can disagree with it. A name without a stage suffix stops the :term[configure step]{id=configure-step}.
2. **Every entry depends on every include.** A file under the shader folder without a stage suffix is shared code, and all entries depend on all of it. The reason: slangc can write a dependency file, but reading it has problems, and compiling every shader again after an include changes is cheap enough.
3. **The bytes do not depend on the configuration.** The build passes no debug-information flag, which would put source paths into the module. The reason: a Debug test then examines the same bytes that Dist ships.
4. **A failed build leaves no output a later build takes as current.** The tool writes a temporary file and renames it. The reason: the build system decides what to redo from file times, so a half-written module with a new time looks finished.
5. **Binary input is untrusted.** The tool checks every length before it reads. The reason: a compiler bug or a damaged file must produce an error message, not a crash or a silent wrong module.
6. **Only one target embeds shaders**, because the registry defines the lookup functions.
7. **Generated files say "do not edit", and a person edits the source or the generator.** The reason: the next build replaces the edit.

:::rule[Register every shader in the build]
`AGENTS.md` says every shader entry is listed in `strata_add_shaders` in `Strata/CMakeLists.txt`, and that you re-run the configure step after adding one. A shader that is not listed has no registered name, so the renderer cannot find it. [The shaders page](../gpu/shaders.md) shows how to write and register one.
:::

## A toy version

A SPIR-V module is a sequence of 32-bit words, and five header words come first. Every instruction after them starts with one word that holds its length in words (the high 16 bits) and its `opcode`, the number that says which instruction it is (the low 16 bits). The `operands` follow, one word each.

The toy below builds a small module by hand. It does the job of the shader tool's patch: after each decoration that makes a value the built-in vertex position, it inserts a decoration that marks the position invariant. Invariant means that two shaders computing the same position produce the same bits. [The frame tour](../gpu/frame-tour.md) explains why the depth prepass needs that.

The table shows the words of the instruction the toy searches for and of the one it adds.

| Instruction | Word 0 | Word 1 | Word 2 | Word 3 |
| --- | --- | --- | --- | --- |
| Decorate value 3 as the built-in Position | `0x00040047`: four words, instruction number 71 | 3, the value | 11, the decoration for built-ins | 0, the built-in Position |
| Decorate value 3 as Invariant, added | `0x00030047`: three words, instruction number 71 | 3, the value | 18, the decoration Invariant | none |

:::question
Which C++ should I know first?
Classes and calls: [the third C++ basics page](../basics/programming-3.md); templates and algorithms: [the generic C++ page](../basics/cpp-generic.md).
:::

The toy collects its edits in a list before it makes any, then applies them from the last to the first. Notice the two `insertions` lines and the reverse :term[iterators]{id=iterator}.

```cpp sketch="engineering-generated-code-toy.cpp"
// A toy of StrataShaderTool's patch: after every "BuiltIn Position" decoration of a hand-made SPIR-V module,
// insert an "Invariant" decoration. Insertions are collected first and made from the back.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <utility>
#include <vector>

namespace
{
	using Words = std::vector<uint32_t>;

	constexpr size_t c_HeaderWords = 5;
	constexpr uint32_t c_OpDecorate = 71;
	constexpr uint32_t c_OpMemberDecorate = 72;
	constexpr uint32_t c_BuiltIn = 11;
	constexpr uint32_t c_Position = 0;
	constexpr uint32_t c_Invariant = 18;

	uint32_t Op(uint32_t opcode, uint32_t wordCount)
	{
		return (wordCount << 16) | opcode;
	}

	void Print(const char* title, const Words& words)
	{
		std::printf("%s (%zu words)\n", title, words.size());
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
			std::printf("  word %2zu: opcode %2u, %u words\n", offset, words[offset] & 0xFFFFu, words[offset] >> 16);
	}

	void DecoratePositionInvariant(Words& words)
	{
		std::vector<std::pair<size_t, Words>> insertions;
		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
		{
			const uint32_t opcode = words[offset] & 0xFFFFu;
			const size_t end = offset + (words[offset] >> 16);
			if (opcode == c_OpDecorate && words[offset + 2] == c_BuiltIn && words[offset + 3] == c_Position)
				insertions.push_back({ end, { Op(c_OpDecorate, 3), words[offset + 1], c_Invariant } });
			if (opcode == c_OpMemberDecorate && words[offset + 3] == c_BuiltIn && words[offset + 4] == c_Position)
				insertions.push_back({ end, { Op(c_OpMemberDecorate, 4), words[offset + 1], words[offset + 2], c_Invariant } });
		}
		for (auto it = insertions.rbegin(); it != insertions.rend(); ++it)
			words.insert(words.begin() + static_cast<std::ptrdiff_t>(it->first), it->second.begin(), it->second.end());
	}
}

int main()
{
	Words module = { 0x07230203u, 0x00010500u, 0u, 12u, 0u,   // magic, version 1.5, generator, id bound, schema
		Op(17, 2), 1u,                                          // OpCapability Shader
		Op(c_OpDecorate, 4), 3u, c_BuiltIn, c_Position,         // OpDecorate %3 BuiltIn Position
		Op(c_OpDecorate, 4), 4u, 30u, 0u,                       // OpDecorate %4 Location 0
		Op(c_OpMemberDecorate, 5), 5u, 0u, c_BuiltIn, c_Position, // OpMemberDecorate %5 0 BuiltIn Position
		Op(19, 2), 2u };                                        // OpTypeVoid %2
	Print("before", module);
	DecoratePositionInvariant(module);
	Print("after", module);
	return 0;
}
```

```text output-of="engineering-generated-code-toy.cpp"
before (22 words)
  word  5: opcode 17, 2 words
  word  7: opcode 71, 4 words
  word 11: opcode 71, 4 words
  word 15: opcode 72, 5 words
  word 20: opcode 19, 2 words
after (29 words)
  word  5: opcode 17, 2 words
  word  7: opcode 71, 4 words
  word 11: opcode 71, 3 words
  word 14: opcode 71, 4 words
  word 18: opcode 72, 5 words
  word 23: opcode 72, 4 words
  word 27: opcode 19, 2 words
```

1. **Line 34:** the list of pending edits: a position and the words to put there. Nothing in the module changes yet.
2. **Lines 39–42:** both forms of the position decoration, on a value and on a member of a structure, record the end of their instruction as the place to insert.
3. **Lines 44–45:** reverse iterators visit the edits from the last to the first, so every earlier position is still right.
4. **Lines 51–56:** the hand-made module, written as words with a comment for each instruction.

The output shows two decorations added: seven instructions where there were five. Here is why the order matters, by hand. The first decoration ends at word 11 and the member decoration at word 20.

Make the word-11 edit first, and the member decoration moves to words 18 to 22. The stored position 20 now points into the middle of it, so the second edit of four words tears that instruction in two. Make the word-20 edit first, and word 11 has not moved. The toy trusts its input and checks nothing; the real code, next, trusts nothing.

## The real code, in the order a build runs it

### Two commands for every entry

`strata_add_shaders` loops over the entries. For every one it makes two custom commands. A custom command is a :term[command line]{id=terminal-command} that the build runs to make the files it names, and it is the unit of work of this pipeline. Notice each command's `OUTPUT`, which tells the build system what the command makes, and its `DEPENDS`, which tells it when to run again.

```cmake src="CMake/StrataShaders.cmake#L172-L190"
add_custom_command(
	OUTPUT "${rawModule}"
	COMMAND "${CMAKE_COMMAND}" -E env SLANG_RUN_SPIRV_VALIDATION=1
		"${slangc}" "${source}" -entry main -stage ${stage} ${slangFlags} ${includeArgs} ${defineArgs} -o "${rawModule}"
	DEPENDS "${source}" ${includeFiles} "${slangc}"
	COMMENT "Compiling shader ${name}"
	VERBATIM)
add_custom_command(
	OUTPUT "${module}" "${header}"
	COMMAND StrataShaderTool --input "${rawModule}" --spirv "${module}" --header "${header}"
		--variable "${variableName}" --name "${name}" ${invariantArgument}
	DEPENDS "${rawModule}" StrataShaderTool
	COMMENT "Embedding shader ${name}"
	VERBATIM)

list(APPEND generatedHeaders "${header}")
string(APPEND registryIncludes "#include \"${name}.h\"\n")
string(APPEND registryEntries "\t\t{ \"${name}\", ${variableName}, sizeof(${variableName}) },\n")
string(APPEND manifest "${name}|${sourceInRepository}|${stage}|${defines}\n")
```

1. **Line 173:** the raw module is the output; the build system runs the command when it is missing or older than an input.
2. **Line 174:** the :term[environment variable]{id=environment-variable} makes slangc validate what it writes, before the tool patches anything.
3. **Line 176:** every shader depends on every include file, and on the compiler itself.
4. **Lines 181–182:** the tool takes the raw module, the two outputs, the array's name and, for some entries, the invariant argument.
5. **Line 190:** the manifest line of this entry, collected for the file written next.

The first command runs slangc and writes `<name>.raw.spv`; the :term[environment variable]{id=environment-variable} makes slangc validate its own output and fail the compile on an error. The second runs `StrataShaderTool` and writes the final module and the header. The last four lines collect what the registry and the manifest need.

A worked example with real names. The entry `Scene/MeshSkinned.vert` is a variant: the source `Scene/Mesh.vert` compiled with an extra define. Its stage is vertex, from the suffix, and the array's name comes from `string(MAKE_C_IDENTIFIER ...)`. The build writes three files under `build/<preset>/Strata/EmbeddedShaders/` and adds one line to the manifest, shown below.

```text
Scene/MeshSkinned.vert.raw.spv   written by slangc
Scene/MeshSkinned.vert.spv       written by StrataShaderTool
Scene/MeshSkinned.vert.h         holds g_StrataShader_Scene_MeshSkinned_vert
Scene/MeshSkinned.vert|Strata/shaders/Scene/Mesh.vert.slang|vertex|ST_SKINNED
```

The manifest line holds the name, the source relative to the repository, the stage and the defines. Because `Scene/Mesh.vert` is listed under `INVARIANT_POSITION`, every variant of that source, this one among them, gets the argument `--invariant-position`.

### The manifest and the registry

The loop's last step writes two files with `file(CONFIGURE)`, so neither changes when its content does not.

```cmake src="CMake/StrataShaders.cmake#L198-L221"
	set(manifestFile "${outputDir}/ShaderEntries.txt")
	file(CONFIGURE OUTPUT "${manifestFile}" CONTENT "${manifest}")
	set_property(GLOBAL PROPERTY STRATA_SHADER_ENTRIES "${manifestFile}")

	set(registrySource "${outputDir}/EmbeddedShaderRegistry.cpp")
	file(CONFIGURE OUTPUT "${registrySource}" CONTENT
"// Generated by CMake/StrataShaders.cmake - do not edit.
#include <cstddef>
#include <cstdint>

${registryIncludes}
#include \"Strata/Renderer/EmbeddedShaders.h\"

namespace Strata::EmbeddedShaders
{
	static const EmbeddedShader s_Shaders[] = {
${registryEntries}	};

	std::span<const EmbeddedShader> GetAll()
	{
		return s_Shaders;
	}
}
")
```

1. **Line 199:** the manifest is written through `file(CONFIGURE)`, so it changes only with its content.
2. **Line 208:** one `#include` per shader header, completed from the loop.
3. **Lines 213–214:** the table: a name, the array and its size in bytes for every shader.
4. **Line 216:** the one function other code calls to see the whole table.

The manifest `ShaderEntries.txt` is the one list of what was built; CI's scripts and the tests that compile every entry read it, so none of them keeps a second list. The registry is plain C++: an include per header and one row per shader in a static array. The generated source holds data only.

The page never types how many entries there are, because the number changes with every shader added. To learn it, count the lines of `ShaderEntries.txt` in your build folder.

### The lookup at run time

A name asked for at run time is found by a loop over the table. `ShaderLibrary::Get` calls `EmbeddedShaders::Find` once per name, makes the shader from the words and keeps it in a map, so the loop does not run again for that name.

```cpp src="Strata/src/Strata/Renderer/ShaderLibrary.cpp#L12-L20"
const EmbeddedShader* Find(std::string_view name)
{
	for (const EmbeddedShader& shader : GetAll())
	{
		if (shader.Name == name)
			return &shader;
	}
	return nullptr;
}
```

A name that is not in the table gives a :term[null pointer]{id=null-pointer}, and `ShaderLibrary::Get` logs that the shader is not part of the engine's embedded shaders. The renderer never reads a file.

### `StrataShaderTool` reads words

The tool is a host program: it links nothing of the engine, only the :term[standard library]{id=standard-library}, and lands in `build/<preset>/tools`. Its first job is to read the module defensively. The compiler's file is trusted less than it seems, because a compiler bug is possible, and a patch that starts from garbage writes garbage.

```cpp src="CMake/StrataShaderTool/SpirvModule.cpp#L27-L65"
std::optional<std::vector<SpirvInstruction>> ParseSpirv(std::span<const uint32_t> words, std::string& error)
{
	if (words.empty())
	{
		error = "the module is empty, so it has no SPIR-V magic number";
		return std::nullopt;
	}
	if (words[0] != Spirv::c_MagicNumber)
	{
		error = "word 0 is " + Hex(words[0]) + ", not the SPIR-V magic number " + Hex(Spirv::c_MagicNumber);
		return std::nullopt;
	}
	if (words.size() < Spirv::c_HeaderWords)
	{
		error = "the module ends at word " + std::to_string(words.size()) + ", inside its five-word header";
		return std::nullopt;
	}

	std::vector<SpirvInstruction> instructions;
	size_t offset = Spirv::c_HeaderWords;
	while (offset < words.size())
	{
		const uint32_t wordCount = words[offset] >> 16;
		if (wordCount == 0)
		{
			error = "the instruction at word " + std::to_string(offset) + " has a word count of 0";
			return std::nullopt;
		}
		if (wordCount > words.size() - offset)
		{
			error = "the instruction at word " + std::to_string(offset) + " has " + std::to_string(wordCount) +
				" words and runs past the module's end at word " + std::to_string(words.size());
			return std::nullopt;
		}
		instructions.push_back({ static_cast<uint16_t>(words[offset] & 0xFFFFu), offset, words.subspan(offset + 1, wordCount - 1) });
		offset += wordCount;
	}
	return instructions;
}
```

1. **Line 34:** a wrong first word means the file is not SPIR-V at all, so nothing after it is read.
2. **Line 39:** a module shorter than its header is refused before any header word is read.
3. **Lines 50–54:** a word count of 0 would make the loop stand still forever, so it is an error.
4. **Lines 55–59:** the count is compared with the words that remain; the subtraction cannot go below zero, because the offset is inside the module.
5. **Line 61:** each instruction records its arguments as a view into the module's words, which is why the patch must collect its edits first.

The function returns the list of instructions or an error that names the first problem.

### Inserting from the back

`DecoratePositionInvariant` is the toy's job with every case handled. Read the second half: the loop that records `insertions`, and the loop that applies them.

```cpp src="CMake/StrataShaderTool/SpirvModule.cpp#L129-L166"
	// Where each decoration goes (the word after the BuiltIn Position one) and what it is, collected before any
	// insertion moves the words the operands point into.
	std::vector<std::pair<size_t, std::vector<uint32_t>>> insertions;
	bool hasPosition = false;
	for (const SpirvInstruction& instruction : *instructions)
	{
		const size_t end = instruction.Offset + 1 + instruction.Operands.size();
		if (instruction.Opcode == Spirv::c_OpDecorate && instruction.Operands.size() >= 3 &&
			instruction.Operands[1] == Spirv::c_DecorationBuiltIn && instruction.Operands[2] == Spirv::c_BuiltInPosition)
		{
			hasPosition = true;
			const uint32_t variable = instruction.Operands[0];
			if (!invariantVariables.contains(variable))
				insertions.push_back({ end, { MakeOpcodeWord(Spirv::c_OpDecorate, 3), variable, Spirv::c_DecorationInvariant } });
		}
		if (instruction.Opcode == Spirv::c_OpMemberDecorate && instruction.Operands.size() >= 4 &&
			instruction.Operands[2] == Spirv::c_DecorationBuiltIn && instruction.Operands[3] == Spirv::c_BuiltInPosition)
		{
			hasPosition = true;
			const uint32_t structure = instruction.Operands[0];
			const uint32_t member = instruction.Operands[1];
			if (!invariantMembers.contains({ structure, member }))
			{
				insertions.push_back({ end, { MakeOpcodeWord(Spirv::c_OpMemberDecorate, 4), structure, member,
					Spirv::c_DecorationInvariant } });
			}
		}
	}
	if (!hasPosition)
		return InvariantResult::NoPositionOutput;
	if (insertions.empty())
		return InvariantResult::AlreadyInvariant;

	// From the back, so the earlier positions stay where they were.
	for (auto it = insertions.rbegin(); it != insertions.rend(); ++it)
		words.insert(words.begin() + static_cast<std::ptrdiff_t>(it->first), it->second.begin(), it->second.end());
	return InvariantResult::Added;
}
```

1. **Line 131:** the pending edits: a position and the words to insert there.
2. **Lines 136–142:** a position decoration on a value gives an edit unless that value is already invariant.
3. **Lines 157–160:** no position at all is an error, and no edit needed means the module was already patched.
4. **Lines 162–165:** the edits are applied from the back, so the earlier positions stay where they were.

An :term[entry point]{id=entry-point-gpu} that is not a vertex shader is refused, since only a vertex shader has a position output. A decoration that already exists is left alone, so a second run changes nothing. A module with no position at all is an error, because the compiler must have changed how it writes the position. The tool prefers failing the build to shipping an unchanged shader.

### Writing atomically

The tool writes two files, and a build that stops between them must not look finished. `WriteFileAtomically` writes `<path>.tmp` and renames it over the target; [the files page](../core/files.md) covers atomic writes in general.

```cpp src="CMake/StrataShaderTool/StrataShaderTool.cpp#L83-L116" symbol="WriteFileAtomically"
// Writes `size` bytes to `path` through a temporary file renamed into place, so a failed write leaves no output a
// later build would take as current.
bool WriteFileAtomically(const std::filesystem::path& path, const char* data, size_t size, std::string& error)
{
	std::filesystem::path temporary = path;
	temporary += ".tmp";
	{
		std::ofstream file(temporary, std::ios::binary | std::ios::trunc);
		if (!file)
		{
			error = "cannot be created";
			return false;
		}
		file.write(data, static_cast<std::streamsize>(size));
		file.close();
		if (!file)
		{
			error = "cannot be written";
			std::error_code ignored;
			std::filesystem::remove(temporary, ignored);
			return false;
		}
	}
	std::error_code renameError;
	std::filesystem::rename(temporary, path, renameError);
	if (renameError)
	{
		error = "cannot be replaced: " + renameError.message();
		std::error_code ignored;
		std::filesystem::remove(temporary, ignored);
		return false;
	}
	return true;
}
```

1. **Lines 87–88:** the temporary file sits next to the target, on the same disk, so the rename cannot copy.
2. **Lines 96–103:** a failed write removes the temporary file and reports it.
3. **Line 107:** the rename is the moment the new output appears, whole or not at all.

On every error path the tool removes the temporary file and leaves the target alone. After a failure the old output stays, and the build system sees that the command did not complete, so it runs the command again.

The header the tool writes comes from `FormatShaderHeader`: eight words per line, each as `0x` and eight hex digits. A module of 11 words is a header of two array lines, eight words and three.

### Embedding a file

`strata_embed_file` runs when CMake configures, with no tool. It reads the file as one hex string, then rewrites it with two :term[regular expressions]{id=regular-expression}. A regular expression describes a pattern of text; each `[0-9a-f][0-9a-f]` below matches one byte's two digits.

```cmake src="CMake/StrataEmbeddedFiles.cmake#L13-L20"
file(READ "${file}" contents HEX)
string(LENGTH "${contents}" hexLength)
if(hexLength EQUAL 0)
	message(FATAL_ERROR "strata_embed_file: '${file}' is empty")
endif()
# Two hex digits per byte, 32 bytes per line.
string(REGEX REPLACE "([0-9a-f][0-9a-f])" "0x\\1," bytes "${contents}")
string(REGEX REPLACE "((0x[0-9a-f][0-9a-f],){32})" "\\1\n\t\t\t" bytes "${bytes}")
```

The first expression turns each pair into `0x..,`. The second finds 32 of those in a row and adds a line break and three tabs after them. The generated function returns a `std::span<const uint8_t>` over the array, so the caller gets a pointer and a length in one value. Editing the font re-runs the configure step, because the function adds the file to the configure dependencies. The call site is one line right after the shader list in `Strata/CMakeLists.txt`, and `Font.cpp` reads the result through `EmbeddedFiles::GetDefaultFont()`.

### Version and commit headers

There are two headers, made at two times. `Version.h` is made at configure from a template with `configure_file`; it holds the major, minor and patch numbers and the version string, and `configure_file` also writes only when the content differs. The commit changes between builds without a configure, so a header for it must be made at build time.

```cmake src="CMake/StrataVersionCommit.cmake#L10-L24"
if(GIT_EXECUTABLE)
	execute_process(COMMAND "${GIT_EXECUTABLE}" rev-parse --short=12 HEAD
		WORKING_DIRECTORY "${SOURCE_DIR}" RESULT_VARIABLE result OUTPUT_VARIABLE output OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
	if(result EQUAL 0 AND output MATCHES "^[0-9a-f]+$")
		set(commit "${output}")
	endif()
endif()

file(CONFIGURE OUTPUT "${OUTPUT}" CONTENT "#pragma once

// Generated by CMake/StrataVersionCommit.cmake at build time - do not edit.

// Short hash of the git commit the build was made from (\"unknown\" outside a git checkout).
#define ST_VERSION_COMMIT \"@commit@\"
" @ONLY)
```

1. **Lines 11–12:** the script asks for the short name of the current commit and drops the error output.
2. **Line 13:** only a clean answer made of hex digits is accepted; anything else leaves the name as `unknown`.
3. **Line 18:** `file(CONFIGURE)` writes only when the text differs from the file.
4. **Line 23:** the :term[hash]{id=hash} goes in where `@commit@` stands.

A target named `StrataVersionCommit`, declared in `Strata/CMakeLists.txt`, runs this script at every build in :term[script mode]{id=script-mode}. The script asks :term[git]{id=git} for the short :term[hash]{id=hash}; without git, or outside a clone of the repository, the hash is `unknown`. Then it writes the header with `file(CONFIGURE)`, which leaves the file alone unless the hash changed. After a commit, only the files that include the header compile again. The generated `Version.h` includes the commit header and defines `c_EngineVersion` and `c_EngineCommit`.

### The samples beside the programs

The target `StrataSamples` in `StrataEditor/CMakeLists.txt` runs `CMake/StrataCopySamples.cmake` at every build. It copies the sample projects next to the editor, where its launcher offers them. It copies only files that differ and removes files that no longer exist in the source, and it omits the data the editor keeps locally, the `.strata` folders. The same idea again: a build step that can run every time because it does nothing when nothing changed.

## Committed generators

A **committed generator** is a script whose outputs are checked into the repository beside it. A build then needs neither the script nor Python, and a person runs the script again only to change the output. The shader pipeline above is the opposite: nothing it writes is committed, and every build runs it. A generator stays committed when running it costs a long calculation, needs a tool that not every machine has, or must give the same answer forever.

| Generator | What it writes | How it is checked | Explained on |
| --- | --- | --- | --- |
| `Tools/GenerateBlueNoise.py` | `Renderer/BlueNoise.h`, a 64 by 64 blue-noise tile | `--check` by hand | [the sun shadows page](../light/sun-shadows-2.md) |
| `Tools/FitFilmic.py` | Filmic's :term[gamut]{id=gamut} constants, a Slang file and a C++ header | `--check` by hand; `--rewrite` writes from the committed numbers | [the tone mapping page](../image/tone-mapping.md) |
| `Tools/FitAOMultiBounce.py` | the ambient-occlusion fit for the shaders and tests | none; `--write` writes | [the ambient occlusion page](../indirect/ao.md) |
| `Tools/GenerateAreaTable.py` | the morphological anti-aliasing area table | none | [the spatial anti-aliasing page](../image/spatial-aa.md) |
| `Tools/GenerateWhiteBalance.py` | the white locus table | none | [the grading page](../image/grading.md) |
| `Tools/GenerateBrandAssets.py` | the Strata mark as PNG files, raw pixel bytes and an icon file | none | no page: the mark is a brand file |
| `Tools/GenerateIslandTerrain.py` | the Open World sample's terrain and a scatter command script | none | the sample's own folder |
| `Tools/GenerateShowcaseTerrain.py` | the Showcase's ground, layout and stations | the CTest `StrataTools.ShowcaseTerrain` | [the look-dev page](../engineering/look-dev.md) |
| `Tools/GenerateShowcaseProps.py` | the Showcase's props, steel maps and command scripts | the CTest `StrataTools.ShowcaseProps` | [the look-dev page](../engineering/look-dev.md) |
| `StrataTests/FeatureTest/Tools/GenerateAssets.py` | the feature test project's tiny assets | none | [the feature test page](../engineering/feature-test.md) |
| `StrataEditor/Tools/GenerateIconHeader.py` | `UI/Icons.h` from the icon font | none; run with a release number | [the design system page](../editor-ui/design-system.md) |
| `Tools/ConvertLTCTable.py` | `Renderer/LTCTable.inl`, the rect lights' tables, converted from a published fit | `--check` by hand; the CTest `StrataTools.LTCTable` | [the area lights page](../light/area-lights.md) |

Two rules hold for all of them. Each uses only Python's standard library, so a machine needs no packages. Where the engine's documents say so, a generator runs as `python -I`, isolated mode. In that mode Python ignores environment variables and the :term[current folder]{id=current-folder}, so a stray file named like a library cannot be loaded in its place.

How a check works, in the smallest one. The excerpt is from `Tools/GenerateBlueNoise.py`. Python differs from C++ here in two ways. The spaces at the start of a line group a function's lines, where C++ uses braces. A string that starts with `f` inserts the values named between its braces.

```python src="Tools/GenerateBlueNoise.py#L143-L159"
def main():
    parser = argparse.ArgumentParser(description="Generates Strata's blue-noise tile header.")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT, help="the header to write")
    parser.add_argument("--check", action="store_true", help="fail when the header differs from what the tool generates")
    arguments = parser.parse_args()

    header = render_header(generate())
    if arguments.check:
        existing = arguments.output.read_text(encoding="utf-8") if arguments.output.is_file() else ""
        if existing != header:
            print(f"{arguments.output} differs from what the tool generates", file=sys.stderr)
            return 1
        print(f"{arguments.output} is up to date")
        return 0
    arguments.output.write_text(header, encoding="utf-8", newline="\n")
    print(f"Wrote {arguments.output}")
    return 0
```

1. **Line 146:** the flag that makes the run a comparison instead of a write.
2. **Line 149:** the header text is made in memory in both modes.
3. **Lines 150–154:** with the flag, a difference prints a message and returns 1, the :term[exit code]{id=exit-code} that fails a check.
4. **Line 157:** without the flag, the file is written with the same line ends on every system.

With `--check`, the script makes the header text in memory, compares it with the committed file and fails when they differ; without it, the script writes the file.

Three generators have a CTest, and each runs the generator's `selftest`. `StrataTools.ShowcaseTerrain` and `StrataTools.ShowcaseProps` write the files again into a work folder and compare them with the committed files. `StrataTools.LTCTable` checks that the committed table is what `ConvertLTCTable.py` writes for the values it pins. `GenerateBlueNoise.py --check` and `FitFilmic.py --check` are run by hand. When CMake found no Python 3.10 or later at configure time, `StrataTests/Tools/PythonMissing.cmake` stands in: that test fails with a message, so a missing Python does not hide a missing check.

:::example[Change a generator the right way]
You decide the blue-noise tile's kernel should be a little wider. First change the constant in the script, run it, and read the header's :term[diff]{id=diff}: the file is all numbers, and a change of the kernel changes most of them.

Run `python -I Tools/GenerateBlueNoise.py --check` and see it pass. Run the script once more and see the header unchanged, since the output is :term[deterministic]{id=determinism}. Then commit the script and the header in one commit. If you committed only the header, the next person to run `--check` would see a failure and not know which of you was right. If you edited the header by hand, the same would happen.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Compile shaders at run time | Engines with user-written shaders and many variants | No rebuild after a shader change; variants made on demand | A pause on the player's machine and a shipped compiler |
| Files written before the run, kept in a folder | Engines that stream shader packs | A smaller executable; shaders replaced without a link | A folder to lose; paths and a loader |
| A binary resource linked into the program | Programs with a platform resource format | No generated source; a smaller compile | One more platform-specific path |
| A dependency file for the shaders' includes | Builds with many large shaders | Only the shaders that include a changed file compile again | Parsing problems; Strata's rebuild is cheap already |
| Generating the committed tables in every build | Projects with a fast generator | No stale output | Python on every build machine and a slower build |

## How it is tested

Two suites cover the pipeline, and both run in the main test program: `build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.ShaderTool`, or the same with `Renderer.ShaderModules`.

`Renderer.ShaderTool` tests the tool's library on hand-made modules. One case checks the framing: a wrong :term[magic number]{id=magic-number}, a short header, a word count of 0 and a count that runs past the end each give an error that names the word. One case cuts a module at every length and checks that the :term[parser]{id=parser} refuses it or reads inside it. The cases that follow decorate a position once, decorate through a block member, and refuse a module that is not a vertex shader or has no position. The last checks the header's eight words per line.

`Renderer.ShaderModules` reads the modules the build embedded and checks five things:

- Each is SPIR-V 1.5 with an entry point named `main` of its name's stage.
- Each declares only capabilities and extensions that every accepted device enables.
- The depth prepass's four vertex entries are invariant, and no other module is.
- Scene vertex shaders read exactly the attributes their input layout supplies.
- No module binds two used variables to one slot.

The suite tests what shipped, not what the tool meant to write.

The target check `StrataShaders.TargetHLSL` compiles every manifest entry for the :term[HLSL]{id=hlsl} target; it has no label, so every CI test job runs it. The Showcase generators and `ConvertLTCTable.py` have their CTests, shown above, with the label `tools`.

## Changing it safely

Extension points: a new shader goes into `strata_add_shaders`; a new embedded file is one `strata_embed_file` line; a new generated table is a committed generator.

- **Re-run configure** after you add or remove a source file or a shader, because the build collects them with a :term[glob]{id=glob}.
- **Write a generated file only on change**, with `file(CONFIGURE)` or `configure_file`. A header written at every build makes every file that includes it compile again at every build.
- **Insert, then check.** When a tool patches a binary format, check the framing first, collect the edits, apply them from the back, and check the framing of the result. Add a test that cuts the input at every length.
- **Never edit a generated file.** Change the source or the generator, run it, commit both.
- **Bump what depends on the output.** A change to a shader entry list changes the expected counts of tests such as the depth prepass's four.

Before you commit, run `Renderer.ShaderTool` and `Renderer.ShaderModules`, and `ctest -L tools` when you touched a Showcase generator or `ConvertLTCTable.py`.

## Summary

- A shader entry becomes a raw module, a final module and a header through two custom commands, and a generated registry lists every header's array under the shader's registered name, which the renderer finds.
- `StrataShaderTool` reads SPIR-V words defensively, collects its edits before it makes them from the back, and writes each file through a temporary file that it renames.
- A committed generator keeps its script beside its committed output; you change the script, run it, check it with `--check` or its CTest, and commit both together.

## Check yourself

1. A build step writes `Version.h` with a new build time on every run. What goes wrong, and what is the fix?
   - A. Nothing: a header costs nothing to write.
   - B. Every file that includes it compiles again at every build; write the header only when its content changes.
   - C. The header is not found; add its folder to the include path.

   :::answer{tests="follow-shader"}
   B. A is wrong: the new file time starts a rebuild of every file that includes it. C is wrong: the problem is the time, not the path. `file(CONFIGURE)` and `configure_file` leave an identical file alone.
   :::

2. The word `0x00040047` starts an instruction. How many words does it have, and which instruction number is it?
   :::answer{tests="patch-spirv"}
   The high 16 bits are `0x0004`, so four words. The low 16 bits are `0x0047`, 71 in decimal: `OpDecorate`.
   :::

3. The font has 162,588 bytes. How many lines does `strata_embed_file` write for its bytes?
   :::answer{tests="follow-shader"}
   32 bytes fit on a line. 162,588 divided by 32 is 5,080 with 28 left over, so 5,081 lines: 5,080 full ones and one with 28 bytes.
   :::

4. Which generators have a CTest that compares the committed output with a fresh run?
   - A. All of them.
   - B. `GenerateBlueNoise.py` and `FitFilmic.py`.
   - C. `GenerateShowcaseTerrain.py`, `GenerateShowcaseProps.py` and `ConvertLTCTable.py`.

   :::answer{tests="change-generator"}
   C. A is wrong: most generators have no test. B is wrong: those two have `--check`, which a person runs by hand.
   :::

5. Two edits are due at words 11 and 20. The tool makes the one at 11 first. What breaks, and how does the real code avoid it?
   :::answer{tests="patch-spirv"}
   The first edit moves everything after word 11, so word 20 is no longer where the second instruction ends, and the second edit lands inside an instruction. The real code stores all positions first and edits from the last to the first.
   :::

## Exercises

1. **Basic.** Add a shader variant of `Scene/Mesh.vert`, named `Scene/MeshProbe.vert` with a define of your choice, `MY_DEFINE` below. Find its three output files and its manifest line, then run `Renderer.ShaderModules`.
   :::answer[Worked solution]{tests="follow-shader"}
   Add one line to the `VARIANTS` list of the `strata_add_shaders` call in `Strata/CMakeLists.txt`, and run `cmake --preset windows`.

   ```cmake
   "Scene/Mesh.vert|Scene/MeshProbe.vert|MY_DEFINE"
   ```

   The line holds the source, the new registered name and the define. Build. In `build/windows/Strata/EmbeddedShaders/Scene/` you find `MeshProbe.vert.raw.spv`, `MeshProbe.vert.spv` and `MeshProbe.vert.h`, and `ShaderEntries.txt` there gains `Scene/MeshProbe.vert|Strata/shaders/Scene/Mesh.vert.slang|vertex|MY_DEFINE`. The depth-prepass case of `Renderer.ShaderModules` now fails, since the variant inherits the invariant position and the case expects four mesh entries; that failure shows how the tests tie to the list. Remove the line again.
   :::

2. **Medium.** Write a separate program that refuses a module with a wrong magic number, a zero word count or an instruction that runs past the end, and lists the instruction numbers of one that is sound.
   :::answer[Worked solution]{solution="sketches/engineering-generated-code-inspector.cpp" tests="patch-spirv"}
   The program checks word 0, the header size and then every instruction's count, the three checks of `ParseSpirv`, before it lists anything.

   ```cpp sketch="engineering-generated-code-inspector.cpp"
   // A small SPIR-V inspector: refuses a module whose framing is wrong, lists the opcodes of one that is right.
   #include <cstddef>
   #include <cstdint>
   #include <cstdio>
   #include <string>
   #include <vector>

   namespace
   {
   	using Words = std::vector<uint32_t>;

   	constexpr size_t c_HeaderWords = 5;
   	constexpr uint32_t c_MagicNumber = 0x07230203u;

   	uint32_t Op(uint32_t opcode, uint32_t wordCount)
   	{
   		return (wordCount << 16) | opcode;
   	}

   	// The first problem with the module's framing, or an empty string when there is none.
   	std::string Check(const Words& words)
   	{
   		if (words.empty() || words[0] != c_MagicNumber)
   			return "word 0 is not the magic number";
   		if (words.size() < c_HeaderWords)
   			return "the module ends inside its header";
   		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
   		{
   			const size_t count = words[offset] >> 16;
   			if (count == 0)
   				return "word count 0 at word " + std::to_string(offset);
   			if (count > words.size() - offset)
   				return "the instruction at word " + std::to_string(offset) + " runs past the end";
   		}
   		return "";
   	}

   	void Inspect(const char* title, const Words& words)
   	{
   		const std::string problem = Check(words);
   		if (!problem.empty())
   		{
   			std::printf("%s: refused, %s\n", title, problem.c_str());
   			return;
   		}
   		std::printf("%s: accepted\n", title);
   		for (size_t offset = c_HeaderWords; offset < words.size(); offset += words[offset] >> 16)
   		{
   			const uint32_t opcode = words[offset] & 0xFFFFu;
   			const bool builtIn = opcode == 71 && words[offset + 2] == 11;
   			std::printf("  word %zu: opcode %u%s\n", offset, opcode, builtIn ? " (decorates a built-in)" : "");
   		}
   	}
   }

   int main()
   {
   	const Words good = { c_MagicNumber, 0x00010500u, 0u, 8u, 0u, Op(17, 2), 1u, Op(71, 4), 3u, 11u, 0u };
   	Words wrongMagic = good;
   	wrongMagic[0] = 0x03022307u;
   	Words zeroCount = good;
   	zeroCount[5] = Op(17, 0);
   	Words pastTheEnd = good;
   	pastTheEnd[7] = Op(71, 9);
   	Inspect("good", good);
   	Inspect("wrong magic", wrongMagic);
   	Inspect("zero count", zeroCount);
   	Inspect("past the end", pastTheEnd);
   	return 0;
   }
   ```

   ```text output-of="engineering-generated-code-inspector.cpp"
   good: accepted
     word 5: opcode 17
     word 7: opcode 71 (decorates a built-in)
   wrong magic: refused, word 0 is not the magic number
   zero count: refused, word count 0 at word 5
   past the end: refused, the instruction at word 7 runs past the end
   ```

   1. **Line 23:** word 0 must be the magic number; an empty module is refused here too.
   2. **Line 25:** a module shorter than its header is refused before the loop reads any header word.
   3. **Lines 30–33:** a count of 0 and a count that runs past the end are the two ways a length can lie.
   :::

3. **Hard.** Trace it yourself. The renderer asks for a shader by name. Find, with a search or a debugger, where the program finds that name, and follow it back to the commands that wrote its words.
   :::answer[Worked solution]{tests="follow-shader"}
   `ShaderLibrary::Get` in `Strata/src/Strata/Renderer/ShaderLibrary.cpp` calls `EmbeddedShaders::Find`, defined above it in the same file; `Find` loops over `GetAll()`. `GetAll()` is defined in the generated `EmbeddedShaderRegistry.cpp` under `build/<preset>/Strata/EmbeddedShaders/`, which returns the array whose rows name each header's variable. Each header, `<name>.h`, is an output of the second custom command in `strata_add_shaders` in `CMake/StrataShaders.cmake`, made by `StrataShaderTool` from `<name>.raw.spv`, which the first custom command made with slangc.
   :::

## Where it lives in Strata

- `CMake/StrataShaders.cmake`: `strata_add_shaders`, the manifest, the registry.
- `CMake/StrataShaderTool/`: `SpirvModule.cpp`, `SpirvModule.h`, `StrataShaderTool.cpp`.
- `CMake/StrataEmbeddedFiles.cmake`, `CMake/StrataVersionCommit.cmake`, `CMake/StrataCopySamples.cmake`.
- `Strata/src/Strata/Renderer/EmbeddedShaders.h` and `ShaderLibrary.cpp`; `Strata/src/Strata/Core/EmbeddedFiles.h` and `Version.h.in`.
- Tests: `Renderer.ShaderTool`, `Renderer.ShaderModules`, `StrataShaders.TargetHLSL`, `StrataTools.ShowcaseTerrain`, `StrataTools.ShowcaseProps`, `StrataTools.LTCTable`.
- Generators: `Tools/*.py`, `StrataEditor/Tools/GenerateIconHeader.py` and `StrataTests/FeatureTest/Tools/GenerateAssets.py`.

## Further reading

- The SPIR-V specification (Khronos, registry.khronos.org): the word layout, instruction numbers and decorations. Advanced.
- The CMake documentation for `file(CONFIGURE)`, `add_custom_command` and script mode (cmake.org). Intermediate.
