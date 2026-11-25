---
id: assets/extending
title: "Tutorial: adding an asset type"
description: "Add a plain text asset type to Strata, from its enum value to a file the editor imports and a game loads, with the tests the engine demands."
kind: tutorial
size: L
tracks: [E]
needs: [assets/uploads, assets/robustness, world/tutorial-component]
time: 120
learn:
  - id: append-type
    text: explain why a new asset type is appended to the enum and what its two name functions are used for
  - id: write-loader
    text: write a loader that takes the stored bytes over and rejects text that is not valid UTF-8 or too large
  - id: write-importer
    text: add an importer that checks a source file and stores it as written, and register it in the asset pipeline
  - id: test-loader
    text: write a round trip test and a test of truncated and garbage stored forms for a new loader
  - id: feature-asset
    text: explain what the feature test demands of a new asset type and add the asset that satisfies it
since: 0.3.0
status: final
---

## What you will make

You will add a new kind of asset to Strata: a plain text file with the extension `.sttxt`. You write its type, its asset class, its :term[loader]{id=loader} and its :term[importer]{id=importer}, then the tests that the engine's rules ask for.

```mermaid caption="The change in five parts: the type, the loader, the importer, the tests and the feature test asset, which together make every check of the engine pass." alt="Five boxes in a row, joined by arrows: the type and its class, the loader, the importer, the tests, and the feature test asset. A last box at the end reads engine checks pass."
flowchart LR
    T["Type and class"] --> L["Loader"]
    L --> I["Importer"]
    I --> X["Tests"]
    X --> F["Feature test asset"]
    F --> C["Engine checks pass"]
```

## What you need

- The source build of [your first engine change](../core/first-change.md): a clone at the book's commit, its :term[submodules]{id=submodule} and a `Debug` build of your system's :term[CMake preset]{id=cmake-preset}. Every command below writes `<preset>` for that preset: `windows`, `linux` or `macos`.
- The habits of [the component tutorial](../world/tutorial-component.md): the patch is shown in blocks, you copy the lines that start with `+`, and you build and test after each section.
- Time: about two hours. The first build after the new files appear is the longest wait, because it compiles every file that includes the asset :term[header files]{id=header-file}.
- No file to import. You change the engine: seven existing files and seven new ones, two of them an asset of the feature test project.

The engine keeps a checklist for a new type in its developer guide, in the section "Adding an :term[asset type]{id=asset-type}". The five sections of this page follow it: the type and its class, the loader, the importer, the tests, and the feature test. Everything the checklist asks for a toy type like this one is here. Types that upload to the :term[graphics card]{id=gpu} in steps ([budgeted uploads](uploads.md)) or that name other assets ([references](references.md)) need more, and the exercises point to it.

:::files[The files of the change]

- `GameEngine/` your clone
  - `Strata/src/Strata/Asset/`
    - **AssetTypes.h**, **AssetTypes.cpp**: the list of types and their names
    - **AssetImporters.cpp**: the importers of the engine; you add one here
  - `Strata/src/Strata/Scene/`
    - **TextAsset.h**, **TextAsset.cpp**: the new asset class
    - **SceneRegistration.cpp**: where the loader of the new type is registered
  - `StrataEditor/src/UI/`
    - **PropertyWidgets.cpp**: the icon and the name the editor shows for each type
  - `StrataTests/`
    - `src/Scene/`: three new test files for the type
    - `src/Asset/AssetTests.cpp`: two lists of types that you extend
    - `src/Editor/AssetCommandTests.cpp`: the count of types that the editor lists
    - `FeatureTest/Assets/Text/`: the asset that the feature test demands

:::

## Add the type and its class

A **text asset** is a file of text that a game reads by name through the asset system: dialogue, a list of tips, a level described as lines. Strata has no such type yet, so the first job is to say that it exists. Every asset has a type, a number the engine stores next to the asset's handle. The type decides which loader reads the :term[bytes]{id=byte}, which importer made them and where the editor shows them.

A text file has nothing to cook. A texture is converted to a form the graphics card reads, but text needs no conversion. The :term[stored form]{id=stored-form} of a text asset is the file itself, as written, which the engine calls [storing the source directly](importing.md). Fonts are stored this way too, and the new importer copies the font importer later.

:::::steps

1. Open `Strata/src/Strata/Asset/AssetTypes.h` and read the enum `AssetType`. Count from `None`, which is 0: `Scene` is 1, `Font` is 8 and `ColorLookup`, the last value, is 13. Add `Text` after `ColorLookup`, which gives it the number 14.

   ```diff src="book:tutorials/assets/extending.patch#hunk-6"
    		AnimationClip,      // Joint channels of an imported animation (Animation/AnimationClip.h)
    		AnimationController, // States, transitions and parameters (".stanimator", Animation/AnimationController.h)
    		World,               // Layers and cells of a streamed world (".stworld", World/WorldAsset.h)
   -		ColorLookup          // 3D color lookup table of a grade, applied after the tone curve (".cube", Renderer/ColorLookup.h)
   +		ColorLookup,         // 3D color lookup table of a grade, applied after the tone curve (".cube", Renderer/ColorLookup.h)
   +		Text                 // Plain UTF-8 text stored as written (".sttxt", Scene/TextAsset.h)
    	};
    
    	const char* AssetTypeToString(AssetType type);
   ```

   The new value goes last, never in the middle. :term[Asset packs]{id=asset-pack} and the :term[import records]{id=import-record} of a project store the numbers of the types (a `.meta` file stores the name), so inserting `Text` after `Font` would turn every stored `Skeleton` (9) into a `Text`. The comment on the enum says the same: the values are stored in packs and import records, so you only append.

   **You should see:** `ColorLookup,` with a `,` after it now, and `Text` as the last value, each with a comment.

   **If you do not see it:** the build in step 6 stops with an error at the line of `Text` when the `,` after `ColorLookup` is missing.

2. Teach the two name functions about the new value. `AssetTypeToString` turns a type into its name, and `AssetTypeFromString` turns a name back into a type.

   ```diff src="book:tutorials/assets/extending.patch#hunk-4"
    			case AssetType::AnimationController: return "AnimationController";
    			case AssetType::World:               return "World";
    			case AssetType::ColorLookup:         return "ColorLookup";
   +			case AssetType::Text:                return "Text";
    		}
    		return "None";
    	}
   ```

   The first function is a `switch` with one `case` per value. The second walks the array of every type and compares names, so the new value must stand in that array as well.

   ```diff src="book:tutorials/assets/extending.patch#hunk-5"
    			AssetType::None, AssetType::Scene, AssetType::Prefab, AssetType::Model, AssetType::Mesh,
    			AssetType::Material, AssetType::Texture, AssetType::AudioClip, AssetType::Font,
    			AssetType::Skeleton, AssetType::AnimationClip, AssetType::AnimationController, AssetType::World,
   -			AssetType::ColorLookup
   +			AssetType::ColorLookup, AssetType::Text
    		};
    		for (AssetType type : types)
    		{
   ```

   The two functions are the place where the engine knows the types by name, and others rely on it. The pack reader accepts an entry only when its type survives the round trip from number to name and back, so a type missing from either function makes a pack that holds your asset invalid. The feature test finds the types by counting through their names, as the last section shows.

   **You should see:** the name `"Text"` in the `switch` and `AssetType::Text` after `ColorLookup` in the array.

   **If you do not see it:** a :term[compiler]{id=compiler} warning that a `switch` does not handle `AssetType::Text` points at a function you missed.

3. Create `TextAsset.h` in the `Scene` folder of the engine. It declares the asset class.

   ```diff src="book:tutorials/assets/extending.patch#hunk-10"
   +#pragma once
   +
   +#include "Strata/Asset/Asset.h"
   +
   +#include <cstdint>
   +#include <string>
   +#include <string_view>
   +#include <vector>
   +
   +namespace Strata
   +{
   +
   +	// A plain text file, stored as written. Text files are untrusted input: Create accepts valid UTF-8 up to c_MaxBytes and
   +	// nothing else, so every reader of the asset can rely on both.
   +	class TextAsset : public Asset
   +	{
   +	public:
   +		// The most bytes a text asset holds: a load or an import of a larger file fails.
   +		static constexpr uint64_t c_MaxBytes = 1ull << 20;
   +
   +		static AssetType GetStaticType() { return AssetType::Text; }
   +		AssetType GetType() const override { return GetStaticType(); }
   +
   +		// Takes the bytes over. Null, with the reason in outError, when they are too many or not valid UTF-8.
   +		static Ref<TextAsset> Create(std::vector<uint8_t> bytes, std::string* outError = nullptr);
   +
   +		std::string_view GetText() const { return std::string_view(reinterpret_cast<const char*>(m_Bytes.data()), m_Bytes.size()); }
   +		AssetMemoryUsage GetMemoryUsage() const override { return AssetMemoryUsage { m_Bytes.size() }; }
   +	private:
   +		TextAsset() = default;
   +	private:
   +		std::vector<uint8_t> m_Bytes;
   +	};
   +
   +}
   ```

   1. **Line 13:** the comment states the promise: every `TextAsset` holds valid :term[UTF-8]{id=utf-8} of at most `c_MaxBytes`, so code that reads one never checks again. UTF-8 is the way [bytes become text](../basics/bytes.md).
   2. **Line 19:** the limit, 1 MiB, which is 1,048,576 bytes. The limit is this page's choice, not an engine rule: a text asset is read whole into memory, and a file without a limit could fill a large share of it.
   3. **Lines 21–22:** `GetStaticType` returns the type for code that knows the class, and `GetType` overrides the :term[base class's]{id=base-class} pure function with the same value.
   4. **Line 25:** `Create` takes the bytes by value, so a caller that has no more use for them moves them in. It is the only way to make a `TextAsset`; the :term[constructor]{id=constructor} on line 30 is private.
   5. **Line 28:** `GetMemoryUsage` reports the bytes the asset holds, in the system :term[memory pool]{id=memory-pool}. :term[Asset managers]{id=asset-manager} read it once an asset is ready, for their budgets and statistics. A text asset keeps no data on the graphics card, so the other pools stay 0.

   **You should see:** a new file with those 35 lines, including the blank ones.

   **If you do not see it:** the file belongs in the `Scene` folder, beside `Prefab.h`, not in `Asset`. The note after these steps explains the choice.

4. Create `TextAsset.cpp` beside it. It checks the bytes and makes the asset.

   ```diff src="book:tutorials/assets/extending.patch#hunk-9"
   +#include "stpch.h"
   +#include "Strata/Scene/TextAsset.h"
   +
   +#include "Strata/Core/Log.h"
   +#include "Strata/Core/StringUtils.h"
   +
   +namespace Strata
   +{
   +
   +	Ref<TextAsset> TextAsset::Create(std::vector<uint8_t> bytes, std::string* outError)
   +	{
   +		if (bytes.size() > c_MaxBytes)
   +		{
   +			if (outError)
   +				*outError = fmt::format("The text is {} bytes: a text asset holds at most {}", bytes.size(), c_MaxBytes);
   +			return nullptr;
   +		}
   +
   +		// MakeValidUTF8 replaces every invalid sequence and returns valid text unchanged, so any difference is an error.
   +		const std::string_view text(reinterpret_cast<const char*>(bytes.data()), bytes.size());
   +		if (StringUtils::MakeValidUTF8(text) != text)
   +		{
   +			if (outError)
   +				*outError = "The text is not valid UTF-8";
   +			return nullptr;
   +		}
   +
   +		Ref<TextAsset> asset(new TextAsset());
   +		asset->m_Bytes = std::move(bytes);
   +		return asset;
   +	}
   +
   +}
   ```

   1. **Lines 4–5:** `Log.h` brings `fmt::format` with it, from the copy of the formatting library that the engine's logging library bundles. The engine's targets have no other path to that library, so an include of `<fmt/format.h>` does not compile.
   2. **Lines 12–17:** the size check comes first, because it costs nothing, and the reason goes into `outError` for the person who sees the failure.
   3. **Lines 19–21:** `MakeValidUTF8` replaces every invalid sequence of a text with a replacement character, and returns valid text unchanged. So the result differs from the input exactly when the input is not valid UTF-8.
   4. **Line 28:** `new` is needed because the constructor is private, and a `Ref` takes the pointer at once.
   5. **Line 29:** `std::move` hands over the vector's memory without a copy.

   **You should see:** 33 lines in the new file, and includes of `Log.h` and of `StringUtils.h`, which holds `MakeValidUTF8`.

   **If you do not see it:** a build error about `TextAsset::Create` being defined twice means the function is also in the :term[header]{id=header}. Keep only its declaration there.

5. Give the editor's icon and name of a type a line each for `Text`. `StrataEditor/src/UI/PropertyWidgets.cpp` holds `GetAssetTypeIcon` and `GetAssetTypeDisplayName`, which the content browser and the asset inspector call. Each is a `switch` over the types without a `default`.

   ```diff src="book:tutorials/assets/extending.patch#hunk-11"
    				case AssetType::AnimationController: return Icons::Network;
    				case AssetType::World:     return Icons::Earth;
    				case AssetType::ColorLookup: return Icons::Blend;
   +				case AssetType::Text:      return Icons::FileText;
    				case AssetType::None:      break;
    			}
    			return Icons::File;
   ```

   The first function picks the icon. `FileText`, a page with lines, is an icon the editor already has. The second function gives the name a person reads, here the same word as the type's.

   ```diff src="book:tutorials/assets/extending.patch#hunk-12"
    				case AssetType::AnimationController: return "Animation Controller";
    				case AssetType::World:     return "World";
    				case AssetType::ColorLookup: return "Color Lookup";
   +				case AssetType::Text:      return "Text";
    				case AssetType::None:      break;
    			}
    			return "Asset";
   ```

   The compilers of Linux and macOS warn about a `switch` that misses a value of its enum, and the engine's build treats warnings as errors. Without these two lines the build stops there.

   **You should see:** `AssetType::Text` before `AssetType::None` in both functions, with the icon `Icons::FileText` and the name `"Text"`.

   **If you do not see it:** a Windows build passes without the lines, because its compiler gives no such warning by default. A build on Linux or macOS then fails with an error about `Text` in this file.

6. Run the :term[configure step]{id=configure-step} again, because you added :term[source files]{id=source-file}, then build.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   ```

   The build collects its source files with a pattern at the configure step, as [your first change](../core/first-change.md) explains. Without the first command, the new `TextAsset.cpp` is not compiled, and the link fails later with a missing function.

   **You should see:** the build ends without an error. It compiles many files, because every file that includes `Asset.h` or `AssetTypes.h` sees the changed enum.

   **If you do not see it:** an error that names `AssetType::Text` in a file you did not touch means that file has a `switch` over the types without a `default`. Add the missing case there.

:::::

:::why[Why the type's class lives in the Scene module]
The checklist of the developer guide sends a loader to the module that owns its type. The `Asset` folder has no registration function of its own, and it knows no scenes. Text is stored as its source and read as one document, like prefabs and scenes, so it sits with them in `Scene`, whose function `RegisterSceneModule` already registers their loaders. The cost: text assets come with the scene module, so a program without that module cannot load them.
:::

## Register the loader

An asset's bytes are read from a file or a pack by a worker thread, and a **loader** turns them into an asset object. The engine keeps one loader per type in a registry. When something requests an asset, the manager finds the loader of its type, calls it on a worker with the stored bytes, and publishes the result. A loader that returns no asset marks the asset as failed, with the reason it wrote.

The engine already has a loader that behaves like yours: the font loader, which also keeps the file as it is. The first line of the quote closes the loader before it.

```cpp src="Strata/src/Strata/Renderer/RendererRegistration.cpp#L110-L114"
});
AssetLoaderRegistry::Register(AssetType::Font, [](const AssetMetadata&, AssetLoadData& data, std::string* outError) -> Ref<Asset>
{
	return Font::Create(data.TakeBytes(), outError);
});
```

The loader receives an `AssetLoadData`, not a plain span of bytes. Its function `TakeBytes` moves the bytes out of the manager's buffer into the loader's hands. A loader that kept the bytes by copying them would hold two copies while the load finished, which matters for large assets. The font loader passes the taken bytes straight to `Font::Create`, and yours does the same with `TextAsset::Create`.

:::::steps

1. Open `Strata/src/Strata/Scene/SceneRegistration.cpp`. Add the include of the new header.

   ```diff src="book:tutorials/assets/extending.patch#hunk-7"
    #include "Strata/Scene/ProjectCollisionLayers.h"
    #include "Strata/Scene/ProjectSceneTiming.h"
    #include "Strata/Scene/SceneReadProgress.h"
   +#include "Strata/Scene/TextAsset.h"
    
    namespace Strata
    {
   ```

   **You should see:** the include in sorted order, after `SceneReadProgress.h`.

   **If you do not see it:** includes in the engine's files go in order, each group sorted. A wrong place still compiles, and a review would ask you to move it.

2. Register the loader at the end of `RegisterSceneModule`.

   ```diff src="book:tutorials/assets/extending.patch#hunk-8"
    			SceneReadProgress::Tracker progress(metadata.Handle);
    			return SceneAsset::Deserialize(data.GetBytes(), outError, [&progress](float share) { progress.Report(share); }, [&data]() { return data.IsCancelled(); });
    		});
   +		// Text is stored as written and checked as it loads; the bytes become the asset's own, with no second copy.
   +		AssetLoaderRegistry::Register(AssetType::Text, [](const AssetMetadata&, AssetLoadData& data, std::string* outError) -> Ref<Asset>
   +		{
   +			return TextAsset::Create(data.TakeBytes(), outError);
   +		});
    	}
    
    }
   ```

   1. **Line 4:** the comment says why: the bytes become the asset's own.
   2. **Line 5:** the registry call names the type and gives a :term[lambda]{id=lambda}. The lambda receives a record of the asset, which this loader does not need, the load data and a place for an error message.
   3. **Line 7:** `TakeBytes` and `Create`, in one line. When `Create` returns null, the loader returns null and the message stays in `outError`.

   **You should see:** the registration after the one for scenes, inside the function.

   **If you do not see it:** a :term[compile error]{id=compile-error} about `AssetLoadData` means the include of `AssetManager.h` is missing; the file has it already, so check that you edited `SceneRegistration.cpp`.

3. Build again.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** a short build, because only one file changed.

   **If you do not see it:** the error names the first wrong line. A missing `;` after the closing `)` of `Register(...)` is the usual cause.

:::::

The loader runs on a worker thread and may not touch engine state, so it holds nothing but the bytes and the function that checks them. It has no state of its own and never asserts: bytes that are not valid are data, not a programmer's mistake, so the loader reports them and returns no asset.

:::rule[A loader rejects garbage without crashing]
Stored forms come from disks, packs and the network, and any of them can be truncated or damaged. The engine's rule is that every loader rejects truncated or garbage bytes without a crash, and the section on tests shows how you prove it. See [the page on robust loading](robustness.md).
:::

## Import the file

A loader reads the stored form. The stored form of a text asset is the file, but the editor must still accept a new file in a project, and it must not accept a broken one. That is the job of an **importer**: it recognizes a file by its extension, checks it and produces the stored form. The engine registers its importers in one function, `RegisterAssetPipeline`, which only tools call. A shipped game has loaders and no importers.

The font importer is the model. It also stores its source as written.

```cpp src="Strata/src/Strata/Asset/AssetImporters.cpp#L141-L156"
// TrueType and OpenType fonts, stored as-is.
class FontImporter final : public AssetImporter
{
public:
	AssetType GetType() const override { return AssetType::Font; }
	std::vector<std::string> GetExtensions() const override { return { ".ttf", ".otf" }; }
	uint32_t GetVersion() const override { return 1; }
	bool StoresSourceDirectly() const override { return true; }

	bool Import(const ImportContext& context, ImportResult& result, std::string* outError) const override
	{
		if (!ReadSource(context, result.Data, outError))
			return false;
		return Font::Create(result.Data, outError) != nullptr;
	}
};
```

1. **Line 145:** the importer's type, the one its loader reads.
2. **Line 146:** its extensions, lower case with the dot.
3. **Line 147:** the version, 1 for a new importer. The number goes up whenever the importer's output changes, and the editor then imports the stale files again by itself.
4. **Line 148:** `StoresSourceDirectly` says that the stored form is the source file. The editor caches nothing for such a type and reads the file itself when it loads the asset.
5. **Lines 152–154:** the import reads the source, then asks the asset class to make an asset of it. The check is the loader's own function, so the importer and the loader can never disagree about what is valid.

:::::steps

1. Open `Strata/src/Strata/Asset/AssetImporters.cpp` and add the include of the new header.

   ```diff src="book:tutorials/assets/extending.patch#hunk-1"
    #include "Strata/Core/FileSystem.h"
    #include "Strata/Core/JsonUtils.h"
    #include "Strata/Renderer/Font.h"
   +#include "Strata/Scene/TextAsset.h"
    
    #if ST_WITH_AUDIO
    	#include "Strata/Audio/AudioClipAsset.h"
   ```

   **You should see:** the include after the one for `Font.h`.

   **If you do not see it:** this file sits in the asset pipeline layer, which may include the scene layer. If a :term[layering test]{id=layer-table} fails later, the include is in the wrong file.

2. Add the importer class after the font importer, inside the :term[namespace]{id=namespace} that has no name.

   ```diff src="book:tutorials/assets/extending.patch#hunk-2"
    			}
    		};
    
   +		// Plain text files, stored as written once they are valid.
   +		class TextImporter final : public AssetImporter
   +		{
   +		public:
   +			AssetType GetType() const override { return AssetType::Text; }
   +			std::vector<std::string> GetExtensions() const override { return { ".sttxt" }; }
   +			uint32_t GetVersion() const override { return 1; }
   +			bool StoresSourceDirectly() const override { return true; }
   +
   +			bool Import(const ImportContext& context, ImportResult& result, std::string* outError) const override
   +			{
   +				if (!ReadSource(context, result.Data, outError))
   +					return false;
   +				return TextAsset::Create(result.Data, outError) != nullptr;
   +			}
   +		};
   +
    	}
    
    	void RegisterAssetPipeline()
   ```

   1. **Line 4:** the comment names what the importer does, in the words of the font importer's.
   2. **Line 9:** `.sttxt` is the only extension, spelled in lower case.
   3. **Line 10:** version 1: no import of this type exists yet, so nothing is stale.
   4. **Lines 15–17:** the source is read into `result.Data`, and the check stops a file the loader would refuse. `Import` returns false, and the message in `outError` reaches the person who dropped the file.

   **You should see:** your class between the font importer and the end of the namespace without a name, the same shape as its neighbor.

   **If you do not see it:** a build error that `ReadSource` is not declared means the class is outside the namespace without a name, where the helper lives.

3. Register the importer at the end of `RegisterAssetPipeline`.

   ```diff src="book:tutorials/assets/extending.patch#hunk-3"
    		AssetImporterRegistry::Register(CreateScope<AudioClipImporter>());
    #endif
    		AssetImporterRegistry::Register(CreateScope<FontImporter>());
   +		AssetImporterRegistry::Register(CreateScope<TextImporter>());
    		AssetImporterRegistry::Register(CreateScope<ColorLookupImporter>());
    	}
    
   ```

   Registering is one line, and the order only matters when two importers claim the same extension: a later registration wins. `.sttxt` is new, so no importer claims it yet.

   **You should see:** the line after the one for the font importer and before the closing brace.

   **If you do not see it:** the content browser reports dropped files that no importer reads. A missing line appears as that report for your `.sttxt` file.

4. Build again.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ```

   **You should see:** the build ends without an error.

   **If you do not see it:** an error that `TextAsset` is not declared in the importer file means step 1 landed in another file.

:::::

:::why[The importer checks, although the loader checks too]
The two checks run in different places. The importer runs in the editor, when you add a file, and fails with a message that names the file. The loader runs in the game, where a broken file can only mean damage after the import, and there it fails the one asset and logs the reason. A file that the importer refuses never reaches the game at all. The cost is one more pass over the bytes at import time, which for a file of at most 1 MiB takes a few milliseconds.
:::

## Test the type

The engine's first rule for new behavior is that it ships with tests, and for a loader there are two kinds. A round trip shows that a good stored form becomes the asset you expect. A rejection test shows that truncated and garbage forms fail cleanly. The checklist asks for both, and so does [the page on robust loading](robustness.md).

The tests go in a new suite named after the module, as the engine names every suite: `Scene`, a dot and the class. The suite prefix `Scene` already has a shard, a group of suites that `ctest` runs together, so no shard file changes.

The tests use a sample text of 19 bytes. `Line one` and its line end take 9. `Caf` takes 3, the letter é takes 2 bytes in UTF-8, a space takes 1, the euro sign takes 3, and the final line end takes 1. The numbers 9, 3, 2, 1, 3 and 1 add up to 19, and the tests rely on that sum.

:::::steps

1. Create `TextAssetTestUtils.h` in the folder `StrataTests/src/Scene`. It holds the sample and two helpers for the tests.

   ```diff src="book:tutorials/assets/extending.patch#hunk-19"
   +#pragma once
   +
   +#include "Strata/Asset/AssetManager.h"
   +
   +#include <doctest/doctest.h>
   +
   +#include <string>
   +#include <vector>
   +
   +namespace Strata::Tests
   +{
   +
   +	// 19 bytes: "Line one\n" is 9, "Caf" 3, the e with an acute accent 2, a space 1, the euro sign 3 and the final line end 1.
   +	inline const std::string c_TextSample = "Line one\nCaf\xC3\xA9 \xE2\x82\xAC\n";
   +
   +	inline std::vector<uint8_t> TextToBytes(const std::string& text)
   +	{
   +		return std::vector<uint8_t>(text.begin(), text.end());
   +	}
   +
   +	// What the loader the Scene module registered makes of stored bytes: the asset, or null with the reason in `error`.
   +	inline Ref<Asset> LoadText(std::vector<uint8_t>& bytes, std::string& error)
   +	{
   +		const AssetLoadFunction* loader = AssetLoaderRegistry::Find(AssetType::Text);
   +		REQUIRE(loader);
   +		AssetMetadata metadata;
   +		metadata.Type = AssetType::Text;
   +		metadata.Path = "Text/Notes.sttxt";
   +		AssetLoadData data(bytes);
   +		return (*loader)(metadata, data, &error);
   +	}
   +
   +}
   ```

   1. **Line 14:** the sample as a C++ string. Each `\x` escape is one byte of the UTF-8 form, so the test does not depend on the encoding of the source file.
   2. **Lines 16–19:** the sample as the vector of bytes a loader receives.
   3. **Lines 22–31:** the helper that calls the loader the module registered, exactly as the manager does, and returns the asset or null with the reason. `REQUIRE(loader)` fails the test when the type has no loader at all.

   **You should see:** 33 lines, in the namespace `Strata::Tests`.

   **If you do not see it:** helpers defined in a header must be `inline`, or the :term[linker]{id=linker} finds them in every test file that includes the header.

2. Create `TextAssetTests.cpp` beside it. Its first test case is the round trip, its second the importer.

   ```diff src="book:tutorials/assets/extending.patch#hunk-20"
   +#include <doctest/doctest.h>
   +
   +#include "Scene/TextAssetTestUtils.h"
   +#include "Strata/Asset/AssetImporter.h"
   +#include "Strata/Scene/TextAsset.h"
   +#include "TestHelpers.h"
   +
   +#include <filesystem>
   +#include <fstream>
   +#include <string>
   +#include <vector>
   +
   +using namespace Strata;
   +
   +TEST_SUITE("Scene.TextAsset")
   +{
   +	TEST_CASE("A text round-trips through its loader, which takes the bytes over")
   +	{
   +		std::vector<uint8_t> bytes = Tests::TextToBytes(Tests::c_TextSample);
   +		REQUIRE(bytes.size() == 19);
   +		std::string error;
   +		const Ref<Asset> loaded = Tests::LoadText(bytes, error);
   +		REQUIRE_MESSAGE(loaded, error);
   +		CHECK(bytes.empty());
   +		CHECK(loaded->GetType() == AssetType::Text);
   +		CHECK(std::static_pointer_cast<TextAsset>(loaded)->GetText() == Tests::c_TextSample);
   +		CHECK(loaded->GetMemoryUsage().Cpu == 19);
   +		CHECK(loaded->GetMemoryUsage().GetGpu() == 0);
   +	}
   +
   +	TEST_CASE("The importer stores a valid file as written and refuses an invalid one")
   +	{
   +		const AssetImporter* importer = AssetImporterRegistry::FindByExtension(".sttxt");
   +		REQUIRE(importer);
   +		CHECK(importer->GetType() == AssetType::Text);
   +
   +		const std::filesystem::path directory = Tests::CreateTemporaryDirectory("TextImporter");
   +		const std::filesystem::path path = directory / "Notes.sttxt";
   +		ImportContext context;
   +		context.SourcePath = path;
   +		context.AssetDirectory = directory;
   +
   +		std::ofstream(path, std::ios::binary) << "Line one\nLine two\n";
   +		ImportResult result;
   +		std::string error;
   +		REQUIRE_MESSAGE(importer->Import(context, result, &error), error);
   +		CHECK(result.Data == Tests::TextToBytes("Line one\nLine two\n"));
   +
   +		std::ofstream(path, std::ios::binary) << "\xFF\xFE broken";
   +		ImportResult rejected;
   +		error.clear();
   +		CHECK_FALSE(importer->Import(context, rejected, &error));
   +		CHECK_FALSE(error.empty());
   +	}
   +}
   ```

   1. **Lines 19–24:** the sample is 19 bytes, which the test requires first, so a changed sample fails at once, with a message. The loader takes the bytes over, so the vector the test holds is empty afterwards.
   2. **Lines 26–28:** the asset holds the same text, and reports 19 bytes in the system memory pool and nothing in video memory.
   3. **Lines 33–35:** the importer is found by its extension, as the editor finds it.
   4. **Lines 43–47:** a valid file imports, and the stored form is the file's bytes.
   5. **Lines 49–53:** a file that starts with the bytes `FF FE`, which no UTF-8 text can, fails with a message.

   **You should see:** 55 lines with two test cases.

   **If you do not see it:** the suite name must start with `Scene`, because the shard that runs it matches `Scene*`.

3. Create `TextAssetRobustnessTests.cpp` beside them, the test of damaged stored forms.

   ```diff src="book:tutorials/assets/extending.patch#hunk-18"
   +#include <doctest/doctest.h>
   +
   +#include "Scene/TextAssetTestUtils.h"
   +#include "Strata/Scene/TextAsset.h"
   +
   +#include <cstddef>
   +#include <string>
   +#include <vector>
   +
   +using namespace Strata;
   +
   +TEST_SUITE("Scene.TextAsset")
   +{
   +	TEST_CASE("Truncated, garbage and oversized stored forms are rejected")
   +	{
   +		// Cutting the sample inside a multi-byte character leaves invalid UTF-8: after 13 bytes (the first byte of the
   +		// accent) and after 16 or 17 (one or two bytes of the euro sign). Every other length ends between characters.
   +		const std::vector<uint8_t> whole = Tests::TextToBytes(Tests::c_TextSample);
   +		for (size_t length = 0; length <= whole.size(); length++)
   +		{
   +			CAPTURE(length);
   +			std::vector<uint8_t> prefix(whole.begin(), whole.begin() + static_cast<std::ptrdiff_t>(length));
   +			std::string error;
   +			const bool cutInsideCharacter = length == 13 || length == 16 || length == 17;
   +			CHECK((Tests::LoadText(prefix, error) != nullptr) == !cutInsideCharacter);
   +			CHECK(error.empty() == !cutInsideCharacter);
   +		}
   +
   +		const std::vector<std::vector<uint8_t>> garbage = {
   +			{ 0xFF, 0xFE, 0xFD },  // bytes that start no sequence
   +			{ 0xC0, 0x80 },        // an overlong form of NUL
   +			{ 0xED, 0xA0, 0x80 },  // a surrogate
   +			{ 0x80 } };            // a continuation byte alone
   +		for (std::vector<uint8_t> bytes : garbage)
   +		{
   +			std::string error;
   +			CHECK(Tests::LoadText(bytes, error) == nullptr);
   +			CHECK_FALSE(error.empty());
   +		}
   +
   +		std::vector<uint8_t> atLimit(TextAsset::c_MaxBytes, 'a');
   +		std::string error;
   +		CHECK(Tests::LoadText(atLimit, error) != nullptr);
   +		std::vector<uint8_t> tooLarge(TextAsset::c_MaxBytes + 1, 'a');
   +		CHECK(Tests::LoadText(tooLarge, error) == nullptr);
   +		CHECK_FALSE(error.empty());
   +	}
   +}
   ```

   1. **Lines 16–17:** the comment predicts the result before the test runs. Cutting the sample after 13 bytes leaves the first byte of é; after 16 or 17 bytes it leaves one or two bytes of the euro sign.
   2. **Lines 19–27:** every prefix of the sample from 0 to 19 bytes is loaded. A prefix that ends between characters is valid text, and the three that end inside one must fail with a message.
   3. **Lines 29–39:** four byte patterns that are never valid: bytes that start no sequence, a two-byte form of the byte 0, which UTF-8 forbids, a surrogate and a lone continuation byte.
   4. **Lines 41–46:** the limit. Exactly 1,048,576 bytes load, and one more fails.

   **You should see:** 48 lines with one test case.

   **If you do not see it:** if the compiler rejects the nested braces of `garbage`, check that every inner list sits in its own pair of braces.

4. Add the new type to the two lists of types that the engine's own asset tests walk, so that the name round trip and the loader lookup cover `Text` as well. The first list checks that every type converts to its name and back.

   ```diff src="book:tutorials/assets/extending.patch#hunk-15"
    	TEST_CASE("Asset types convert to names and back")
    	{
    		for (AssetType type : { AssetType::None, AssetType::Scene, AssetType::Prefab, AssetType::Model, AssetType::Mesh, AssetType::Material,
   -			AssetType::Texture, AssetType::AudioClip, AssetType::Font, AssetType::World, AssetType::ColorLookup })
   +			AssetType::Texture, AssetType::AudioClip, AssetType::Font, AssetType::World, AssetType::ColorLookup,
   +			AssetType::Text })
    			CHECK(AssetTypeFromString(AssetTypeToString(type)) == type);
    		CHECK_FALSE(AssetTypeFromString("Shader").has_value());
    
   ```

   The second list checks that each type has a loader, which fails if the loader's registration is forgotten.

   ```diff src="book:tutorials/assets/extending.patch#hunk-16"
    	{
    		// The loaders of a module's types come with the module.
    		for (AssetType type : { AssetType::Scene, AssetType::Prefab, AssetType::Model, AssetType::Mesh, AssetType::Material, AssetType::Texture,
   -			AssetType::Font, AssetType::ColorLookup })
   +			AssetType::Font, AssetType::ColorLookup, AssetType::Text })
    		{
    			CAPTURE(AssetTypeToString(type));
    			CHECK(AssetLoaderRegistry::Find(type) != nullptr);
   ```

   Both lists live in `StrataTests/src/Asset/AssetTests.cpp`. A third check counts the types: the editor's command `asset.types` lists every named type, and its test in `StrataTests/src/Editor/AssetCommandTests.cpp` expects as many as the number of the last value. With `Text` appended the last value is `Text`.

   ```diff src="book:tutorials/assets/extending.patch#hunk-17"
    			types[type["type"].get<std::string>()] = type;
    		// Every named type once, and nothing else.
    		CHECK(types.size() == listing["types"].size());
   -		CHECK(types.size() == static_cast<size_t>(AssetType::ColorLookup));
   +		CHECK(types.size() == static_cast<size_t>(AssetType::Text));
    		for (const auto& [name, type] : types)
    		{
    			CAPTURE(name);
   ```

   The count works because `None` is 0 and is never listed, so the last value's number is the number of named types.

   **You should see:** `AssetType::Text` at the end of each list, and in the count.

   **If you do not see it:** the lists are plain braces in a `for` loop. A missing `,` before `AssetType::Text` gives a compile error.

5. Configure again, because the test files are new, build and run the suite.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Scene.TextAsset,Asset,Editor.AssetOperations
   ```

   On Windows write `StrataTests.exe`. The flag runs every suite named in its list.

   **You should see:** doctest ends with a summary that counts no failed test cases. The new suite holds three test cases, the suite `Asset` holds the old ones plus your two extended lists, and `Editor.AssetOperations` counts 14 types.

   **If you do not see it:** a failed check prints its file and line. The most likely cause is the length list in the rejection test: the three failing lengths are 13, 16 and 17, and every other length must load.

6. Run the layering check, which tests that every file includes only what its layer allows.

   ```sh
   build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering
   ```

   **You should see:** no failed test case. `TextAsset.h` includes the asset layer and the core only, and the importer file includes the scene layer, which the asset pipeline layer may do.

   **If you do not see it:** a failure names the file and the include. Never add the file to the :term[allowlist]{id=allowlist}: move the include, or invert the dependency.

7. Show that the rejection test can fail. Change the line `if (StringUtils::MakeValidUTF8(text) != text)` in `TextAsset.cpp` to `if (text.empty() && StringUtils::MakeValidUTF8(text) != text)`, which never rejects anything. Build and run the suite again.

   **You should see:** the rejection test fails at lengths 13, 16 and 17 and for each garbage pattern, because the broken text now loads. The importer's test case fails too, since it imports the broken file. The round trip still passes. Restore the line and run the suite until it passes.

   **If you do not see it:** if nothing fails, the build did not compile your change: build again and read its last lines.

:::::

The check in step 7 is the rule's second half: a test you have never seen fail may test nothing. Here the failing lengths also confirm the arithmetic of the sample.

## Satisfy the feature test

The engine has one project, `StrataTests/FeatureTest/`, that exercises everything the engine registers. Its test fails when a registered type has no asset of that type in the project. The check is a loop over the type numbers from 1 until the name function says `None`, which is why step 2 of the first section had to cover the new value.

```cpp src="StrataTests/src/FeatureTest/FeatureTests.cpp#L104-L109"
// The project has an asset of every type (the types are found through their names, so new ones are included).
for (uint16_t value = 1; std::string_view(AssetTypeToString(static_cast<AssetType>(value))) != "None"; value++)
{
	INFO(MissingAssetMessage(static_cast<AssetType>(value)));
	CHECK(types.contains(static_cast<AssetType>(value)));
}
```

An asset of the new type needs two files: the asset itself and its `.meta` file, which holds its handle, its type and its :term[import settings]{id=import-settings}. The test also requires that the committed `.meta` equals what the engine writes after importing. So the file must be exactly in the engine's form: keys sorted by name, one tab for each level, and a final line end. You copy the form of an existing `.meta` and change two values.

:::::steps

1. Create the folder `Text` in the folder `StrataTests/FeatureTest/Assets`, and in it the file `Notes.sttxt`, a short file of valid text.

   ```diff src="book:tutorials/assets/extending.patch#hunk-13"
   +Strata text asset
   +A plain text file that the feature test imports and loads.
   ```

   **You should see:** two lines of text, ending with a line end.

   **If you do not see it:** an editor that adds a :term[byte order]{id=endianness} mark at the start of the file breaks the test, because the importer keeps the file as written. Save it as plain UTF-8.

2. Create its `.meta` file beside it, `Notes.sttxt.meta`.

   ```diff src="book:tutorials/assets/extending.patch#hunk-14"
   +{
   +	"Handle": "F7A0000000000013",
   +	"ImportSettings": {},
   +	"Strata": {
   +		"Format": "AssetMeta",
   +		"Version": 1
   +	},
   +	"Type": "Text"
   +}
   ```

   The handle is a 64-bit number written in :term[hexadecimal]{id=hexadecimal}. The feature project's handles all start with `F7A` and count up, and the highest of that series at this commit is `F7A0000000000012`, so yours is the next, `F7A0000000000013`. Two assets with one handle would break the project. `ImportSettings` is empty because the importer has no settings yet; the first exercise adds some and shows what the test then demands.

   **You should see:** nine lines: the handle, the empty settings, the block that names the format and its version 1, and the type `"Text"`.

   **If you do not see it:** the name of the type in the `.meta` is the one `AssetTypeFromString` knows, spelled exactly: `Text`.

3. Run the feature test.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"
   ```

   **You should see:** the test `Passed`. The test imported `Notes.sttxt` with your importer and loaded it with your loader, with no warning in the log.

   **If you do not see it:** the output names the failed check. An import error means the importer refused the file, so search for a byte order mark. A failed comparison of `.meta` files means the file differs from the engine's form in a tab or a line end.

4. Show that the test demands the asset. Move the new folder `Text` out of `StrataTests/FeatureTest/Assets` and run the test again.

   **You should see:** the test fails, and its message reads: `Asset type Text: add an asset of this type to StrataTests/FeatureTest/Assets`. Move the folder back and run the test until it passes.

   **If you do not see it:** if the test still passes, you moved a copy. The test reads the assets of `StrataTests/FeatureTest/Assets` in your clone.

5. Run every test that needs no graphics card, the last check before a commit.

   ```sh
   ctest --preset <preset>-debug -LE gpu -j 8
   ```

   **You should see:** all tests `Passed`. The full run takes the longest of the page. Tests that fail without your change, in an area you did not touch, are a sign that the clone has local changes, so check `git status`.

   **If you do not see it:** run the failed test alone with its suite name, as in the last section, and read the first failed check.

:::::

What remains is what a real type needs on top of the toy: a filter chip in the content browser, a thumbnail, and a note in the documentation. The engine's checklist also asks for a review of the whole :term[diff]{id=diff} before a commit, and the exercises below take the type further.

## Summary

- A new asset type starts as a value appended to `AssetType`, never inserted, and as entries in `AssetTypeToString` and `AssetTypeFromString`, which packs and the feature test depend on.
- The loader is registered by the module that owns the type. It takes the bytes over with `TakeBytes`, rejects invalid or oversized text by returning no asset with a reason, and the asset reports its bytes in the system memory pool.
- The importer is a short class on the font importer's model: it reads the source, checks it with the loader's own function, stores it as written, and starts at version 1. `RegisterAssetPipeline` registers it.
- The tests are a round trip and a rejection test over every prefix and several garbage patterns. The two lists and the count of types in the engine's own tests take the new type, and the layering check keeps passing.
- The feature test fails until the project holds an asset of the new type with a `.meta` in the engine's exact form.

## Check yourself

1. A colleague inserts `Text` between `Font` and `Skeleton` in `AssetType`, because the list looks tidier. The build passes and the tests of the type pass. What breaks, and when?

   :::answer{tests="append-type"}
   The numbers of `Skeleton`, `AnimationClip`, `AnimationController`, `World` and `ColorLookup` each rise by 1. A pack or a project record written before the change stores the old numbers, so a stored `Skeleton` (9) is read as a `Text`, and a stored `ColorLookup` (13) as a `World`. The new tests cannot see this, because they never read old data. Appending avoids the problem, which is why the enum's comment says the values are append only.
   :::

2. You add `Text` to `AssetTypeToString` but forget the array in `AssetTypeFromString`. Which of the page's checks still pass, and what fails when a game is exported?

   :::answer{tests="append-type"}
   The loader test and the importer test still pass, because they use the enum value directly. The name list of the engine's tests fails, since `AssetTypeFromString("Text")` gives nothing. In an exported pack, the reader accepts an entry only if its type survives the trip through both functions, so the pack that holds a text asset is refused as invalid.
   :::

3. The loader receives the three bytes `FF FE FD`. What does it return, where does the reason go, and what does the asset manager show for that asset?

   :::answer{tests="write-loader"}
   `Create` finds that `MakeValidUTF8` changes the text, writes "The text is not valid UTF-8" into `outError` and returns null. The loader returns null, so no asset is published, and the manager marks the asset as failed and keeps the reason. The game continues, and the code that asked for the asset gets no asset and handles that case, as every code that loads assets must.
   :::

4. The loader already checks the text. Why does the importer check it too?

   :::answer{tests="write-importer"}
   The two checks run at different times and show the failure to different people. The importer runs in the editor when a file is added, so the person who dropped the file sees which file is wrong, and the broken file never enters the project. The loader runs in the game, where the same bytes can only be wrong through damage, and it must not crash. Both call `TextAsset::Create`, so they agree on what valid means.
   :::

5. The rejection test loads every prefix of the 19-byte sample. Which lengths must fail, and why do the others pass?

   :::answer{tests="test-loader"}
   Lengths 13, 16 and 17 fail. Length 13 ends after the first of the two bytes of é, and lengths 16 and 17 end after one or two of the three bytes of the euro sign. Every other length ends between two whole characters, and valid UTF-8 may end anywhere between characters. Length 0 passes too: empty text is valid, and the asset holds 0 bytes.
   :::

6. Your pull request adds the type, the loader, the importer and the tests, and everything passes on your machine except the feature test, which says `Asset type Text: add an asset of this type to StrataTests/FeatureTest/Assets`. What do you add?

   :::answer{tests="feature-asset"}
   A file of the new type and its `.meta` under `StrataTests/FeatureTest/Assets`, for example `Notes.sttxt` and `Notes.sttxt.meta` in a new folder. The `.meta` holds a handle that no other asset of the project uses, empty import settings, the format block and `"Type": "Text"`. All of it is in the engine's exact form: keys sorted by name, tabs, and a final line end. The test imports the file, loads it, and compares the `.meta` with what the engine writes.
   :::

## Exercises

1. **Medium.** Give the importer two settings. `NormalizeLineEndings` is a switch, on by default, that stores every line end in one form. `Newline` is a choice between `LF` and `CRLF`, and applies only when the switch is on. It must show an :term[inactive reason]{id=inactive-reason} when the switch is off; bump the importer's version and keep the feature test passing.

   Hint: the importer then changes the bytes, so it no longer stores its source directly. Look at `ColorLookupImporter` for `GetDefaultSettings` and `GetSettingsProperties`, and at `TextureImporter::GetInactiveReason` for the shape of a reason.

   :::answer{tests="write-importer" solution="tutorials/assets/extending/exercise-1.patch"}
   The importer's version becomes 2, because with the switch on by default the stored form of a file with Windows line ends changes, and old imports are stale. `GetDefaultSettings` returns both keys, and `GetSettingsProperties` builds a `Bool` and an `Enum` with `ImportSettingsBuilder`. `GetInactiveReason` returns, for `Newline` with the switch off, a text that says the choice applies only when line ends are :term[normalized]{id=normalization}. The stored form is no longer the source, so the importer drops `StoresSourceDirectly` and writes the converted bytes into `result.Data`. A line feed after a carriage return is skipped, and each lone carriage return or line feed becomes the chosen end.

   The feature test then fails until the `.meta` of `Notes.sttxt` holds both settings with their defaults, because the committed `.meta` must hold every setting the importer writes. The worked solution is the patch of this exercise, which applies on top of the page's change: these edits, a new test case and the extended `.meta`.
   :::

2. **Medium.** Write an asset manager extension that counts how many times the manager updates, and show the count among the manager's statistics. It has no effect on text assets: the point is to learn the extension point.

   Hint: `Strata/src/Strata/Asset/AssetManagerExtension.h` declares four functions you must override, and the texture streamer in the :term[renderer]{id=renderer} is the engine's one example. Its `AddStats` writes into `AssetManagerStats::Detail`, a structure you extend with a new field. The factory is registered in a module's registration function, with `AssetManagerExtensionRegistry::Register`.

   :::answer{tests="append-type"}
   The class derives from `AssetManagerExtension` and overrides four functions. `RefinesPartialAssets` returns false, because it keeps no partial assets. `OnUpdate` adds 1 to a counter, and `ReleaseMemory` frees nothing and returns 0. `AddStats` adds the counter to a new field of `AssetManagerStats::Detail`.

   The module registers a factory that makes one extension per manager. `AddStats` reads the counter on any thread, while `OnUpdate` runs on the :term[main thread]{id=main-thread}. So the counter is atomic or guarded by a :term[mutex]{id=mutex}, as the streamer guards its own. A test makes a manager, calls `Update` three times and checks that the statistic is 3.
   :::

3. **Hard.** Make a second type, a list of assets (`.stlist`, a :term[JSON]{id=json} document with an array of :term[asset handles]{id=asset-handle}), whose references the engine knows without loading it. Add it to the pruned exports and the delete checks.

   Hint: start with `GetDocumentKey` and the `World` branch of the scanner in `Strata/src/Strata/Asset/AssetDependencies.cpp`, and read [the page on references](references.md). Each valid handle is recorded once, and never the asset's own.

   :::answer{tests="test-loader"}
   The type needs everything this page built, and one thing more: its documents must record their references, because pruned exports, delete checks and :term[prefetches]{id=prefetch-assets} know an asset's references only from such records. The scanner chooses a document's key by type in `GetDocumentKey`, and reads the references of a type in its own branch, as the `World` branch reads the persistent scene and the cells. Alternatively an importer returns the handles in `ImportResult::References`. A test makes a list that names two assets and a copy of one, then checks that the scan returns two handles, each once. The feature project needs a list asset that names another of its assets.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetTypes.h` and `AssetTypes.cpp`: the enum `AssetType`, its two name functions and the native extensions.
- `Strata/src/Strata/Asset/Asset.h`: the base class `Asset`, `AssetMemoryUsage` and the :term[finalize]{id=finalize} contract.
- `Strata/src/Strata/Asset/AssetManager.h`: `AssetLoadData`, `AssetLoadFunction` and `AssetLoaderRegistry`.
- `Strata/src/Strata/Asset/AssetImporter.h` and `AssetImporters.cpp`: the importer interface, the registry and `RegisterAssetPipeline`.
- `Strata/src/Strata/Scene/SceneRegistration.cpp` and `Strata/src/Strata/Renderer/RendererRegistration.cpp`: where modules register their loaders.
- `Strata/src/Strata/Asset/AssetPack.cpp`: the pack reader that checks every entry's type through the name functions.
- `StrataTests/src/FeatureTest/FeatureTests.cpp` and `StrataTests/FeatureTest/Assets/`: the check and the assets it demands.
- `StrataTests/Architecture/Layers.json`: the layer table behind `Architecture.Layering`.
- `Docs/DeveloperGuide.md`, section "Adding an asset type": the engine's own checklist, which this page follows.

## Further reading

- Robert Nystrom, "Game Programming Patterns", chapter "Type Object", on gameprogrammingpatterns.com: why a program keeps its kinds as data and looks behavior up by kind. Beginner.
- The Unicode Consortium, "The Unicode Standard", chapter 3, section on UTF-8: which byte sequences are well formed, and why overlong forms and surrogates are refused. Advanced.
- [doctest's documentation of its command line](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): `--test-suite` and the other filters. Beginner.
