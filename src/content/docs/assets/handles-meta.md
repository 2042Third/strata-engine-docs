---
id: assets/handles-meta
title: "Handles, `.meta` files and sub-assets"
description: "How Strata gives every asset a name that survives renames, moves and re-imports: the handle, the .meta file, derived sub-asset handles and the built-in range."
kind: internals
size: L
tracks: [E]
needs: [core/files, assets/what-is-an-asset]
time: 70
learn:
  - id: identity
    text: explain why Strata names an asset by a handle and not by its path, and what each other way of naming costs
  - id: meta-contents
    text: name what a .meta file holds and predict what a scan does with a missing, an invalid and a copied one
  - id: derive
    text: compute the handle of a sub-asset from its parent's handle and its key, and say what makes it the same on every machine
  - id: reserved
    text: name the range of handles that belong to built-in assets and what a pack or a copied .meta file may not use
  - id: append-only
    text: explain why the asset type enum only grows at its end
since: 0.3.0
status: final
---

Every asset in a Strata project has to be found again: by a scene that uses it, by a material that points to a texture, by a saved game, by a pack that ships it. This page teaches how Strata names an asset so that the name stays true when the file is renamed, moved, imported again or copied to another machine. It teaches the handle, the `.meta` file beside each :term[source file]{id=source-file}, the handles of assets that live inside another asset, and the numbers Strata keeps for itself. It does not teach what an import writes into the cache, which [Importing](importing.md) covers. Nor does it teach how the editor moves and deletes files, which [The trash and references](../editor/trash-references.md) covers, or handles in general, which [Entities and the registry](../world/ecs.md) covers.

## The problem and how engines solve it

[What an asset is](what-is-an-asset.md) showed that a game's data lives in files that an import turns into a stored form. Now ask how one thing refers to another. A scene says "this crate uses that wood material", and the material says "my colour comes from that texture". Each of these references has to name its target in a way that still works tomorrow.

The plainest name is the path, such as `Props/Crate/Wood.png`. A path is plain to read and costs nothing to make. But a person who renames the folder `Props` to `Scenery` breaks every reference at once. If 40 materials of a game point to files in `Props`, that one rename leaves 40 references pointing at nothing. Two files may also share a name in different folders, and two machines may spell the same path with different letter cases.

The other ways give each asset an identity that is not its place. Table 1 shows the four common ones.

| Way | Where the name lives | Survives a rename | Survives an edit of the file | Main cost |
| --- | --- | --- | --- | --- |
| Path | In the references only | No | Yes | Every move breaks references |
| Number in a sidecar file | In a small file next to the asset | Yes, if the sidecar moves too | Yes | A second file must travel with the first |
| Number inside the asset | In the asset file | Yes | Yes | Each format needs room for it |
| :term[Hash]{id=hash} of the content | Computed from the :term[bytes]{id=byte} | Yes | No | Any edit makes a new name |

A hash of the content looks perfect for a cache, since equal bytes give an equal name. But a person who fixes one pixel of a texture then changes its name, and every reference must follow. An identity inside the asset needs a format that has a place for it, and a plain picture file has none. A number in a sidecar file works with any format, at the price that the sidecar must stay with its file.

:::elsewhere
Unity chose the sidecar: each asset file has a `.meta` file holding a globally unique identifier, as its [manual](https://docs.unity3d.com/Manual/index.html) describes. Unreal keeps identity in its own package files, where the asset's format has room for it. Both are choices of the same trade that Table 1 shows.
:::

Strata chose the sidecar number. A person can open a picture in any program, rename it in any file manager and commit it to any :term[version control]{id=version-control} system. The number sits in a plain text file that does all of this too. The price is the second file. The rest of the page shows how Strata keeps the two together and what it does when they part.

## The map

Five files of `Strata/src/Strata/Asset/` carry the whole subject. Figure 1 shows who owns what.

```mermaid caption="A source file and its sidecar file feed the scan, which registers the asset under its handle; the importer derives handles for sub-assets, and the built-in assets come from a separate list." alt="A flow from a source file and its sidecar file to the scan of the editor's asset manager, which reads the sidecar and registers the asset. The importer derives handles for sub-assets. The built-in list supplies handles one to two hundred fifty-five. All entries end in the registry of asset records, and the cache holds files named by handle."
flowchart LR
  A[Rock.png] --> S[Scan: EditorAssetManager]
  M[Rock.png.meta] --> R[AssetRegistration: read and write]
  R --> S
  S --> G[AssetMetadata records]
  I[AssetImporter: DeriveSubAssetHandle] --> G
  B[BuiltinAssets: handles 1 to 255] --> G
  G --> C[Cache: handle.bin]
```

`AssetTypes.h` holds the handle and the type list: two small declarations that every other file includes. `AssetRegistration.h` and its source read and write `.meta` files, walk the asset folder and resolve handles that several files claim. `AssetImporter.cpp` derives the handles of sub-assets. `BuiltinAssets.h` and its source list the assets that every project has. `Asset.h` holds `AssetMetadata`, the record that the registry keeps for each asset.

The scan itself runs in `EditorAssetManager`, on background threads for the reading and on the :term[main thread]{id=main-thread} for the inserting. The :term[runtime]{id=runtime} manager of an exported game reads no `.meta` file: a pack holds the handles and the records, and the pack's reader never trusts a pack to replace a built-in asset.

## The contract

A caller of this part may rely on a few facts, and must obey a few rules. Each rule has its reason.

An **asset handle** is the number that names one asset: in the code it is `AssetHandle`, another name for `UUID`. A `UUID` is a random 64-bit number that is never zero, and its text form is 16 upper-case :term[hexadecimal]{id=hexadecimal} digits, such as `CAA58AB49C5FCF59`. Zero is the null handle: it means "no asset", and the engine never generates it. Code asks `IsValid()` before it trusts a handle.

A **`.meta` file**, also called a **sidecar**, is the file that sits next to a source file and has the same name with `.meta` added: `Rock.png` has `Rock.png.meta`. It holds the asset's handle, its type and the import settings. It is a small :term[JSON]{id=json} text file, and it is committed to version control together with its source file. A scan that finds a source file without a `.meta` file makes a new random handle and writes the file.

An **asset type** is the kind of an asset, a value of the enum `AssetType`: scene, prefab, model, mesh, material, texture and so on, 13 in all. Packs and import records store the type as a number, so the enum only grows: a new type goes at the end and an old one never moves. The `.meta` file stores the type by its name.

A **sub-asset** is an asset that an import produces inside another asset: a model file yields meshes, materials, textures, a skeleton and animation clips. A sub-asset has no `.meta` file of its own. Its record names its parent and a key, and its handle follows from the two.

Two more kinds of name, the handle of a sub-asset and the handle of a built-in asset, are defined where the real code meets them.

The rules that follow from this are:

1. Code that holds an asset keeps its handle and never its path ([why](#by-handle-never-by-path)).
2. Files move, rename and delete through the editor, or their `.meta` files move with them ([why](#move-through-the-editor)).
3. A `.meta` file that cannot be read is reported and never replaced ([why](#never-replace-an-invalid-meta-file)).
4. Handles 1 to 255 are reserved, for the built-in assets and for nothing else ([why](#reserved-handles)).
5. The type enum is append only, and the way sub-asset handles are computed never changes ([changing it safely](#changing-it-safely)).

## A toy version

Before the real code, a small program does the same job with strings instead of files. It reads a handle from each sidecar text, keeps a table from path to handle, renames a file together with its sidecar, and derives a handle for a key inside a model. It copies the two :term[hash functions]{id=hash-function} from the engine, so that its numbers match the real ones.

```cpp sketch="assets-handles-meta-toy.cpp"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <string_view>

namespace
{

	constexpr uint64_t c_MaxBuiltin = 0xFF;

	uint64_t Fnv1a(std::string_view text)
	{
		uint64_t hash = 14695981039346656037ull;
		for (char character : text)
		{
			hash ^= static_cast<uint8_t>(character);
			hash *= 1099511628211ull;
		}
		return hash;
	}

	uint64_t Combine(uint64_t seed, uint64_t value)
	{
		value *= 0xff51afd7ed558ccdull;
		value ^= value >> 33;
		return seed ^ (value + 0x9e3779b97f4a7c15ull + (seed << 6) + (seed >> 2));
	}

	// The same handle on every machine: only the parent's handle and the key go in.
	uint64_t DeriveChild(uint64_t parent, std::string_view key)
	{
		uint64_t value = Combine(Fnv1a(key), parent);
		if (value <= c_MaxBuiltin)
			value += c_MaxBuiltin + 1;
		return value;
	}

	// A sidecar is one line, "Handle: <16 hex digits>". Zero means invalid: report it, never overwrite it.
	uint64_t ReadSidecar(const std::string& text)
	{
		if (text.rfind("Handle: ", 0) != 0)
			return 0;
		char* end = nullptr;
		const uint64_t handle = std::strtoull(text.c_str() + 8, &end, 16);
		return *end == '\0' ? handle : 0;
	}

}

int main()
{
	std::map<std::string, std::string> files = {
		{ "Rock.png", "Handle: 1A2B3C4D5E6F7081" },
		{ "Notes.png", "<<<<<<< HEAD" },
	};
	std::map<std::string, uint64_t> handleOf;
	for (const auto& [path, sidecar] : files)
	{
		const uint64_t handle = ReadSidecar(sidecar);
		if (handle == 0)
			std::printf("%s: invalid sidecar, file ignored\n", path.c_str());
		else
			handleOf[path] = handle;
	}

	// A rename that carries the sidecar keeps the handle.
	files["Stone.png"] = files["Rock.png"];
	files.erase("Rock.png");
	handleOf.clear();
	for (const auto& [path, sidecar] : files)
		if (const uint64_t handle = ReadSidecar(sidecar); handle != 0)
			handleOf[path] = handle;
	for (const auto& [path, handle] : handleOf)
		std::printf("%s -> %016llX\n", path.c_str(), static_cast<unsigned long long>(handle));

	const uint64_t model = 0x1A2B3C4D5E6F7081ull;
	for (std::string_view key : { "Mesh/0", "Material/0", "Skeleton" })
		std::printf("%.*s -> %016llX\n", static_cast<int>(key.size()), key.data(),
			static_cast<unsigned long long>(DeriveChild(model, key)));
	return 0;
}
```

```text output-of="assets-handles-meta-toy.cpp"
Notes.png: invalid sidecar, file ignored
Stone.png -> 1A2B3C4D5E6F7081
Mesh/0 -> 488CDD4ECF6A82CF
Material/0 -> F8F20C4595833704
Skeleton -> F21AFC255F263667
```

1. **Line 11:** the reserved range ends at 255, the same constant as the engine's.
2. **Lines 24–29:** the engine's mixing function, copied so that the numbers match the real ones.
3. **Lines 35–36:** a result in the reserved range moves out of it, by 256.
4. **Lines 41–48:** text that is not a handle gives zero, which the caller treats as invalid.
5. **Lines 62–63:** an invalid file is reported and skipped, never given a new handle.

Read the output from the top. The merge-conflict text of `Notes.png` is not a handle, so the program reports it and skips the file. It does not invent a new handle, because that would hide the conflict and break every reference to the file. After the rename, `Stone.png` has the handle that `Rock.png` had, since the sidecar text came along. Last, the three keys give three different handles for the same parent.

The toy omits what makes the real code long: threads, a record store, the type, import settings, copied files, built-in handles in the scan, and writing a new `.meta` file atomically.

## The real code, in the order a file meets it

### The handle and the type

The first lines of `AssetTypes.h` hold the two declarations. Search for the comment on the type list: it is the contract of the enum.

```cpp src="Strata/src/Strata/Asset/AssetTypes.h#L11-L31"
// Assets are referenced by handle (a UUID that stays stable across renames and moves), never by path.
using AssetHandle = UUID;

enum class AssetType : uint16_t
{
	None = 0,
	Scene,
	Prefab,
	Model,    // Imported model file (e.g. glTF): owns mesh/material/texture sub-assets, instantiates as a hierarchy
	Mesh,
	Material,
	Texture,
	AudioClip,
	Font,
	// Animation (the values are stored in packs and import records: append only)
	Skeleton,           // Joint hierarchy and rest pose of an imported model (Animation/Skeleton.h)
	AnimationClip,      // Joint channels of an imported animation (Animation/AnimationClip.h)
	AnimationController, // States, transitions and parameters (".stanimator", Animation/AnimationController.h)
	World,               // Layers and cells of a streamed world (".stworld", World/WorldAsset.h)
	ColorLookup          // 3D color lookup table of a grade, applied after the tone curve (".cube", Renderer/ColorLookup.h)
};
```

1. **Line 12:** the whole idea of the handle: a `UUID` under another name, stable across renames and moves.
2. **Line 14:** the type is a 16-bit number, and `None` is zero.
3. **Line 25:** the note that the values are stored in packs and import records, so only appending is safe.
4. **Line 30:** the newest type stands last, as every new type must.

The `UUID` class is in `Strata/src/Strata/Core/`, because entities use it too. Look at its comment for the null value and the text form.

```cpp src="Strata/src/Strata/Core/UUID.h#L13-L33"
// 64-bit random identifier used for entities and assets. Zero is reserved as the invalid/null value
// and is never generated. The canonical text form is 16 upper-case hexadecimal digits.
class UUID
{
public:
	UUID(); // Generates a new random, non-zero UUID
	constexpr UUID(uint64_t uuid)
		: m_UUID(uuid)
	{
	}

	constexpr operator uint64_t() const { return m_UUID; }
	constexpr bool IsValid() const { return m_UUID != 0; }

	std::string ToString() const;
	static std::optional<UUID> FromString(std::string_view text);

	static constexpr UUID Null() { return UUID(uint64_t(0)); }
private:
	uint64_t m_UUID;
};
```

1. **Lines 13–14:** zero is the null value, and the text form is 16 upper-case hexadecimal digits.
2. **Line 18:** the default :term[constructor]{id=constructor} draws a random, non-zero number.
3. **Lines 19–22:** a handle can be made from a plain number, which is how derived and built-in handles are made.
4. **Line 30:** the null handle, spelled out for the code that means "no asset".

### A real `.meta` file

The Showcase sample has a texture called `WeatheredSteel_arm.png`, and beside it a `.meta` file. Search for the handle, the settings and the small `Strata` block that names the format.

```json src="Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta#L1-L20"
{
	"Handle": "CAA58AB49C5FCF59",
	"ImportSettings": {
		"Compression": "Auto",
		"Filter": "Linear",
		"FlipGreen": false,
		"FlipVertically": false,
		"GenerateMips": true,
		"MaxSize": 0,
		"Quality": "High",
		"RemoveSun": false,
		"Usage": "Data",
		"Wrap": "Repeat"
	},
	"Strata": {
		"Format": "AssetMeta",
		"Version": 1
	},
	"Type": "Texture"
}
```

1. **Line 2:** the handle in its text form.
2. **Lines 3–14:** the import settings of this texture.
3. **Lines 15–18:** the format name and version of the file.
4. **Line 19:** the type, written by name.

### Reading and writing it

`ReadAssetMeta` returns one of three states: `Missing`, `Invalid` and `Valid`. A file that exists but cannot be read, is not a :term[JSON object]{id=json-object}, or lacks a handle that parses and is not zero, is `Invalid`, and the result says why in its `Error` text.

`WriteAssetMeta` writes the whole file at once and atomically, as [Files and paths](../core/files.md) teaches, so that a crash never leaves half a `.meta` file. Both may run on any thread, which is why the scan can read thousands of them in the background.

The scan treats the three states differently. For `Invalid` it logs an error that names the file and the cause, and ignores the source file "until the .meta is fixed or deleted". It writes nothing.

For `Missing` it draws a new random handle, which is not zero, not in 1 to 255 and not taken by another file, and writes the `.meta` file. If that write fails it logs that the handle "will change on the next scan". For `Valid` it keeps the handle.

### The record

Each registered asset becomes an `AssetMetadata` record: the handle, the type, the path, the parent, the sub-asset key, a display name and `StoredSize`, the bytes that a load reads. The path uses slashes (`/`) and is relative to the project's asset folder, such as `Models/Helmet.gltf`. A sub-asset shares its parent's path, and `IsSubAsset()` is true when the parent is valid. A built-in asset has the path `Builtin/<Name>`.

### Sub-assets and their keys

A model :term[importer]{id=importer} returns a list of `ImportedSubAsset` values. Each has a key, a name, a type and its cooked bytes. The key identifies the sub-asset inside its parent, and the glTF importer builds it from the model's own numbering:

| Key | What it names |
| --- | --- |
| `Mesh/0` | the first mesh of the model |
| `Material/2` | the third material |
| `Texture/<image>/<usage>/<sampler>` | an image used in one role, with the wrap and filter numbers of its sampler |
| `Skeleton` | the joint tree of the model |
| `Animation/<name>` | a clip, by its name, or by its number when names repeat |

A mesh that a skin moves has a longer key, with `Skin` or `Rigid` in it. The key is part of the contract: a handle is computed from it.

### Deriving the handle

A **derived handle** is the handle of a sub-asset, computed from the parent's handle and the key by a fixed function, so that it comes out the same on every machine and in every import.

A file has a `.meta` file because a person adds files. A sub-asset appears by itself when an import runs, and an import can run again on another machine with a cleared cache. So its handle cannot be random and stored: it must come out the same each time. `DeriveSubAssetHandle` computes it.

```cpp src="Strata/src/Strata/Asset/AssetImporter.cpp#L269-L276" symbol="DeriveSubAssetHandle"
AssetHandle DeriveSubAssetHandle(AssetHandle parent, std::string_view key)
{
	uint64_t value = Hash::Combine(Hash::FNV1a(key), static_cast<uint64_t>(parent));
	// Never collide with the null handle or the range reserved for built-in assets.
	if (value <= c_MaxBuiltinAssetHandle)
		value += c_MaxBuiltinAssetHandle + 1;
	return UUID(value);
}
```

The function hashes the key with :term[FNV-1a]{id=fnv-1a}, a hash that gives the same 64 bits for the same text on every machine. It then mixes the parent's handle in with `Hash::Combine`. If the result is 255 or less it adds 256, so a derived handle never equals the null handle or a built-in one.

:::example[A material's handle, by hand and by machine]
A model `Helmet.gltf` has the handle `1A2B3C4D5E6F7081`, and its importer makes a material with the key `Material/0`. The hash of the text `Material/0` is `73EB7D35473E1F77`. Mixing that with the parent gives `F8F20C4595833704`, which is above 255, so it stays. The cache file of this material is `.strata/Cache/F8F20C4595833704.bin`.

The key `Mesh/0` under the same parent gives `488CDD4ECF6A82CF`, and `Skeleton` gives `F21AFC255F263667`. Import the model on a second machine, after deleting the cache, and the same three numbers come out. A scene that stored `F8F20C4595833704` as a material's handle finds it.

Now check the limits. If the mix gave `0x42`, the rule moves it to `0x142`. If it gave `0`, it moves to `0x100`. A value of `0xFF` becomes `0x1FF`, and `0x100` stays.
:::

Two things can go wrong, and both are costs of the design. A changed key gives a new handle, so an importer that renames `Mesh/1` to `Mesh/one` breaks every reference to it. A model whose meshes change order in the source file also changes what `Mesh/1` means. Chance is the other: two different sub-assets could in theory get one handle. With one million assets the chance that any two of the 64-bit numbers match is about 1 in 37 million, which Strata accepts.

### Built-in assets

A **built-in asset** is an asset that every project has without a file, and its handle is one of 1 to 255.

`BuiltinAssets.h` lists them: the meshes `Cube`, `Sphere`, `Plane`, `Quad`, `Cylinder`, `Capsule`, `Cone` and `Torus` with handles 1 to 8, and the default material with the handle 16 (`0x10`). The other numbers up to 255 are free for later built-in assets. A scene or a script may use these handles directly, such as `BuiltinAssets::CubeMesh`.

The asset layer cannot create the objects, since a mesh needs the :term[renderer]{id=renderer}. So `BuiltinAssets` holds a registry of factories, functions that each create one asset when called, and the renderer's module registers one factory per handle at start. `BuiltinAssets::Register` runs each factory and adds the result to a manager as a memory asset: an asset that exists only in memory and has no file. A build without the renderer has no factory and so no built-in meshes, and nothing breaks.

An exported game's manager refuses a pack entry that uses a built-in handle. It logs a warning that names the entry's path and ignores the entry, so a pack can never replace the engine's cube.

### Copied files

A person copies `Brick.png` and `Brick.png.meta` together in a file manager. Now two files claim one handle. The scan finds this with `FindDuplicateHandles`: it keeps the handle for the file that the import records name, and when no record names one, for the file with the shortest path.

The shortest path is the original under the usual file manager names, "Brick - Copy" and "Brick (1)". Every other file gets a fresh handle, the scan logs a warning that names both files, and it writes the new `.meta` file. The same step gives a new handle to any file whose `.meta` holds a built-in handle.

```cpp src="Strata/src/Strata/Asset/AssetRegistration.h#L113-L119"
struct DuplicateHandle
{
	size_t File = 0;
	size_t Keeper = 0;
};
std::vector<DuplicateHandle> FindDuplicateHandles(std::span<const AssetHandle> handles, std::span<const std::string> paths,
	const std::unordered_map<AssetHandle, std::string>& recordedPaths);
```

The function takes the handle of each file, its path and the paths that the records store. It returns the files that need a new handle, each with the file that keeps its handle.

### From a handle to the bytes

A reference holds a handle, and a load has to turn it into stored bytes. The registry maps the handle to its `AssetMetadata` record. The cache is a folder of files named by handle: the editor's `GetCachePath` joins the cache folder, the handle's 16 digits and `.bin`. For a sub-asset the name uses its derived handle, so `.strata/Cache/F8F20C4595833704.bin` holds the material of the worked example.

The name has a consequence for cleaning. At the end of a scan the editor collects every handle that is still valid: each source file's and each sub-asset's derived one. It then asks `RemoveUnusedCacheFiles` to drop the cache files that name none of them. A file that gets a new handle therefore leaves its old cache file behind for the next scan to remove. [Importing](importing.md) teaches what the cache file holds.

:::example[One scan, four files]
The asset folder holds four sources. `Brick.png` has a `.meta` file with a handle. `Brick - Copy.png` has a byte-for-byte copy of that same `.meta` file. `Moss.png` has no `.meta` file. `Notes.png` has a `.meta` file that holds `<<<<<<< HEAD`.

| File | State of its `.meta` file | What the scan does |
| --- | --- | --- |
| `Brick.png` | Valid | Keeps its handle, as the shortest path of the two claims |
| `Brick - Copy.png` | Valid, but the handle is taken | Logs a warning, draws a new random handle and writes the file |
| `Moss.png` | Missing | Draws a new random handle and writes the file |
| `Notes.png` | Invalid | Logs an error and ignores the source; the `.meta` file is not touched |

Two of the four files end the scan with a new `.meta` file written, one keeps what it had, and one is untouched and absent from the project until a person fixes it.
:::

## Four rules, with their reasons

### By handle, never by path

:::rule[Assets are referenced by handle at run time]
A scene, a material, a script and a save file hold an `AssetHandle`. The path may change when someone moves a folder, but the handle does not, and a path costs a text comparison at every use.

A script may call `Assets::Find` to turn a path into a handle. That works in the editor, where every file exists. An exported game keeps only what its scenes use, so a path that no scene mentions is not in the pack, so the script finds nothing. A game that finds assets by path names them in `AlwaysInclude`, the list of the project's export settings that [Packs and export](packs-export.md) teaches.
:::

### Move through the editor

:::rule[Move, rename and delete through the editor]
The handle lives in the `.meta` file. A file that a person moves in a file manager leaves its `.meta` file behind. The scan then finds a source with no sidecar and makes a new handle, so every reference to the old one is lost. `EditorAssetManager::MoveAsset` moves both files and updates the registry, and a delete goes to the trash.

If you must move files outside the editor, move each `.meta` file with its source. [The trash and references](../editor/trash-references.md) teaches the editor's side.
:::

### Never replace an invalid `.meta` file

:::why[A damaged sidecar is a message, not a blank]
After a merge that conflicts, a `.meta` file holds lines such as `<<<<<<< HEAD`, and it no longer parses. If the scan wrote a new file over it, the asset would get a new random handle and silently break every reference, and the conflict would vanish with its evidence. So the scan reports the file and ignores the source until a person fixes the text. The cost is that an asset disappears from the project while its sidecar is broken, and the error in the log is the only sign. [Git](../basics/git.md) teaches how to resolve a conflict.
:::

### Reserved handles

:::why[The first 255 numbers are the engine's]
A scene may store the handle 1 and mean the cube, in every project and every pack. That only works if no asset of the project can ever hold 1. So three places keep the range clean.

A random handle is drawn again when it falls in 1 to 255. A derived handle is moved out of it, and the scan gives a new handle to a `.meta` file that holds one. The cost is the small set of unused numbers.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Paths as names | Small engines, many hand-made tools | No sidecar files and clear references | Every move or rename breaks references |
| One sidecar per file with a random number | Unity, Strata | Works for any :term[file format]{id=file-format} | A sidecar must travel with the file |
| A number inside the asset file | Engines with their own asset formats | One file per asset | No identity for plain pictures and sounds |
| A hash of the content | Build caches, content-addressed stores | Equal bytes share one stored copy | Each edit makes a new name, so references would break |
| A central table in a database | Large studios' asset servers | One place to move and search | A server, and no plain files for version control |
| Sequential numbers | Old games with a fixed asset list | Short handles | Two people adding assets at once pick the same number |

## How it is tested

The suite `Asset.Registration` in `StrataTests/src/Asset/AssetRegistrationTests.cpp` tests the parts that need no editor. One test case gives `FindDuplicateHandles` six files, with names such as `Copy of Brick.png` and `Moss - Copy.png`. It checks which file keeps the handle, first without records and then with a record that names a path. Others check that a scan of 10,000 assets inserts in time slices, and that a file added during a scan registers once.

`StrataTests/src/Asset/EditorAssetManagerTests.cpp` and `GltfImporterTests.cpp` test the scan and the keys. Run the suite with:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.Registration
```

Run the same command with `Asset*` to run all asset suites. The tests need no :term[graphics processing unit]{id=gpu} (GPU).

## Changing it safely

To add an asset type, append its name to the end of `AssetType`, give it a string in `AssetTypeToString` and `AssetTypeFromString`, and teach an importer to make it. Never insert it in the middle and never change the order of the others, because packs and import records hold the numbers. A type inserted between `Texture` and `AudioClip` would take the audio clip's old number, so an old pack's audio clips would read as the new type and its fonts as audio clips.

To add a sub-asset kind, choose its key with care and treat it as permanent, since the handle comes from it. To change the order or the numbering of an existing key you would change the handles of assets that games already reference. Never change `DeriveSubAssetHandle`. Any change to the hash or the mix gives every sub-asset in every project a new handle at the next import, and every scene, prefab and saved game that points to one breaks. If a fix cannot wait, add a new function and a new key form, and keep the old one for old data.

To add a built-in asset, append its handle in the range of 1 to 255 and its entry to the list, and register a factory in the module that owns its type. Never use a number twice: scenes already store it.

The checks to pass: `Asset.Registration`, the asset suites, and the feature test, which exercises each asset type. A change to a stored form also extends the pack tests, as the engine's guide asks.

## Summary

- Strata names every asset by a handle, a random non-zero 64-bit number kept in a `.meta` file, because paths break on every move and content hashes change on every edit.
- A `.meta` file holds the handle, the type and the import settings; a scan writes a missing one, reports an invalid one without touching it, and gives a new handle to copies.
- A sub-asset has no `.meta` file: its handle is derived by hashing its key and mixing in its parent's handle, so it is the same on every machine.
- Handles 1 to 255 belong to the built-in assets, and no file, pack or derived handle may use them.
- The type enum only grows at its end, because packs and import records store its numbers.

## Check yourself

1. A teammate renames the folder `Props` to `Scenery` in a file manager, moving the `.meta` files with it. What happens to a scene that uses a texture in the folder?

   :::answer{tests="identity,meta-contents"}
   Nothing breaks. The scene holds the handle, and the handle is in the `.meta` file that moved with the texture. A scene that held the path would break.
   :::

2. A `.meta` file shows `<<<<<<< HEAD` after a merge. Choose what the scan does: (a) writes a new handle, (b) reports the error and ignores the source file, (c) reads what it can and fixes the rest.

   :::answer{tests="meta-contents"}
   Option (b). The file is invalid, so the scan logs the cause and skips the source until the text is fixed. Option (a) would silently break every reference, and the scan never reads half a file as in (c).
   :::

3. A model has the handle `0x2000`. Which is true of the handle of its sub-asset with the key `Mesh/0`: it is random and stored, it is derived, or it is the model's handle plus one?

   :::answer{tests="derive"}
   The handle is derived. The importer computes it with `DeriveSubAssetHandle` from the key and the parent's handle, so the same model gives the same handle after a re-import on any machine.
   :::

4. Which of these handles can a new `.meta` file hold: `0`, `0x10`, `0x100`?

   :::answer{tests="reserved"}
   Only `0x100`. Zero is the null handle, and `0x10` is the default material, inside the reserved range 1 to 255. A scan gives a new handle to a `.meta` file that holds `0x10`; one that holds `0` is invalid, so the scan reports it and ignores its source.
   :::

5. Someone inserts a new type `Video` after `Texture` in the enum. Predict what happens when the engine reads a pack made before the change.

   :::answer{tests="append-only"}
   Every type after `Texture` moves up one number. The old number of an audio clip now means `Video`, so an old audio clip reads as a video, an old font as an audio clip, and so on down the list. A new type belongs at the end.
   :::

## Exercises

1. **Basic.** Write the text form of the handle 255 and of the handle 4096.

   :::answer[Worked solution]{tests="reserved"}
   The text form has 16 upper-case hexadecimal digits, padded with zeros on the left. 255 is `FF`, so the text is `00000000000000FF`. 4096 is `0x1000`, so the text is `0000000000001000`. The first is the last handle of the reserved range.
   :::

2. **Medium.** Extend the toy: given file paths and handles, report each file that needs a new handle, keeping the handle for the file with the shortest path.

   :::answer[Worked solution]{tests="meta-contents" solution="sketches/assets-handles-meta-dup.cpp"}
   The sketch keeps, for each handle, the index of the shortest path so far, and then reports every other file with that handle. The real function also lets the import records name the keeper first. Look at the two loops: the first chooses keepers, the second reports.

   ```cpp sketch="assets-handles-meta-dup.cpp"
   #include <cstddef>
   #include <cstdint>
   #include <cstdio>
   #include <map>
   #include <string>
   #include <vector>

   int main()
   {
   	const std::vector<uint64_t> handles = { 0x11, 0x11, 0x22, 0x11 };
   	const std::vector<std::string> paths = { "Brick - Copy.png", "Brick.png", "Moss.png", "Brick (1).png" };

   	// For each handle, the file with the shortest path keeps it.
   	std::map<uint64_t, size_t> keeper;
   	for (size_t index = 0; index < handles.size(); index++)
   	{
   		auto found = keeper.find(handles[index]);
   		if (found == keeper.end() || paths[index].size() < paths[found->second].size())
   			keeper[handles[index]] = index;
   	}
   	for (size_t index = 0; index < handles.size(); index++)
   	{
   		if (keeper[handles[index]] != index)
   			std::printf("%s needs a new handle; %s keeps it\n", paths[index].c_str(), paths[keeper[handles[index]]].c_str());
   	}
   	return 0;
   }
   ```

   ```text output-of="assets-handles-meta-dup.cpp"
   Brick - Copy.png needs a new handle; Brick.png keeps it
   Brick (1).png needs a new handle; Brick.png keeps it
   ```

   1. **Lines 13–19:** one pass over the files remembers the shortest path for each handle.
   2. **Lines 21–25:** a second pass reports each file that is not its handle's keeper.
   :::

3. **Hard.** Trace it yourself. A model has the handle `1A2B3C4D5E6F7081`. Find the function that gives its first material's handle, compute the handle, and find the cache file of that name in `.strata/Cache` of an open project.

   :::answer[Worked solution]{tests="derive"}
   Search the engine for `DeriveSubAssetHandle`: it is in `Strata/src/Strata/Asset/AssetImporter.cpp`, and the glTF importer calls it with the key `Material/0`. The result is `F8F20C4595833704`, as in the worked example. `EditorAssetManager::GetCachePath` in `Strata/src/Strata/Asset/EditorAssetManager.cpp` adds `.bin`, so the file is `.strata/Cache/F8F20C4595833704.bin`. In a real project, the model's own handle is in its `.meta` file; with another handle the number differs.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/AssetTypes.h`: `AssetHandle` and `AssetType`; names in `AssetTypes.cpp`.
- `Strata/src/Strata/Core/UUID.h`: the 64-bit identifier.
- `Strata/src/Strata/Asset/AssetRegistration.h`: `ReadAssetMeta`, `WriteAssetMeta`, `FindDuplicateHandles`.
- `Strata/src/Strata/Asset/AssetImporter.cpp`: `DeriveSubAssetHandle`.
- `Strata/src/Strata/Asset/BuiltinAssets.h`: the built-in list and the factory registry; the factories are in `Strata/src/Strata/Renderer/RendererRegistration.cpp`.
- `Strata/src/Strata/Asset/Asset.h`: `AssetMetadata` and `c_MaxBuiltinAssetHandle`.
- Tests: the suite `Asset.Registration`.
- Sample: `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta`.

## Further reading

- Unity Manual, "Asset Metadata" (<https://docs.unity3d.com/Manual/index.html>): the same sidecar design in another engine. Level: beginner.
- Glenn Fowler, Landon Curt Noll and Phong Vo, "FNV hash": the hash family that Strata uses for keys. Level: intermediate.
- Unreal Engine documentation on asset references and redirectors: how an engine whose assets carry their own identity moves them. Level: intermediate.
