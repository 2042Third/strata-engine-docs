# Brief: `world/serialization`

| Field | Value |
| --- | --- |
| Title | Scene documents: text, streams and the cooked form |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/scene-graph`, `world/reflection`, `core/files` |
| From | scene-ecs §1.9 (the DOM serializer, the three-pass read, leniency, unknown components, the parallel streaming writer and its deterministic bytes, the event-parser reader, sinks, the cooked form STSC and its validation); retitled, the formats only; takes as given that an asset is named by an `AssetHandle` and read by a loader, and links forward to `assets/loading` |
| Unit | `plan/allocation/world.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `world/serialization` — Scene documents: text, streams and the cooked form

**Covers.** The job: the forms a scene takes outside memory (the JSON document, read and written as a DOM for snapshots
and small documents and as a stream for scenes, prefabs and models; the cooked binary form STSC) and how each is written
and read safely. It takes as given that an asset is named by an `AssetHandle` and read by a loader, and links forward to
`assets/loading`; loading a scene as an asset is `world/sub-scenes`'. This page carries the full section on the problem:
text against binary, a DOM against streaming, versions, forward compatibility, and bytes that do not change without a
reason, for diffs and hashes. The map: `SceneSerializer`, `SceneDocumentWriter`, `SceneDocumentReader` with its sinks,
`CookedScene`. Then, in this order:

1. What a scene file looks like: the header (`{"Strata":{"Format","Version":1}}`), the name, the settings, the entity
   count and one entity per line, shown on `Samples/OpenWorld/Assets/Scenes/Loading.stscene` against the older layout of
   `Samples/Tetris/Assets/Scenes/Main.stscene`; scene settings, and the collision layers that 0.5.0 documents still hold.
2. The DOM serializer and its three-pass read: IDs and their mapping, entities and components, then the hierarchy linked
   with a union-find: a parent that is invalid, missing or would close a cycle is dropped with a warning, the entity is
   attached at the top level, and the load goes on.
3. Unknown components kept verbatim in `UnknownComponentsComponent`, one warning per name, written back unchanged;
   keeping unknown data as a rule.
4. The streaming writer: each entity's line byte for byte what the DOM would dump; chunks of 4,096 entities serialized
   in parallel while an ordered job writes and hashes the batch before (two batches in flight); references collected;
   SHA-256 and FNV-1a hashes; cancel and progress; subsets by root; why the bytes do not depend on the number of threads.
5. The streaming reader: an event parser feeding an `EntitySink`, keys in any order, the header checked whenever it
   arrives, `MaxEntities`, cancellation and progress (`SceneReadProgress`), and a parallel read of documents of 16,384
   entities or more, by lines or by a structure scan; the sinks: `SceneBuilder` links parents once every entity exists
   (with the DOM read's rules for a bad parent) and signals last, `EntityPrototypeBuilder` builds no scene,
   `EntityColumns` parses into columns on workers.
6. Snapshots and references: `SerializeEntities` and `DeserializeEntities` with fresh UUIDs, `DuplicateEntity`, and
   `RemapEntityReferences` through reflection and `ExtraReferences`, so copies point at the copies.
7. The cooked form, STSC version 1: a 64-byte header with a CRC-32C, aligned sections (strings, scene information, IDs,
   parents, component types, one column per type, unknown components), properties through `PropertyBinary` (strings up
   to 1 MiB), extra data as binary or MessagePack; everything validated before use, the columns decoded in parallel;
   across builds, an unknown property is skipped with a warning, a property whose type changed fails the whole read
   (the JSON form only warns), and a type this build lacks is kept as an unknown component (with section 2's paths,
   about 100 words).

Then the alternatives, the tests (`Scene.Serialization`, `Scene.Documents`, `Scene.CookedScene` with its corruption
tests, `Scene.Robustness`), changing it safely, and the exercises: an `EntitySink` that counts entities per component
type without making a scene; random corruption of a cooked scene's bytes that the reader must refuse; one entity moved in
the editor, the scene saved and the file diffed; and the "trace it yourself" exercise, a hand-written document whose two
entities name each other as parents, loaded and followed from its warning back to the union-find of `LinkParents`. At
the end the reader can read a scene file, say what a build without a module does with it, and write a sink.

**Leaves out.**

- Loading a scene asset, prepared scenes and the hand-over → `world/sub-scenes`
- Instantiating a prototype into a scene → `world/prefabs`
- When the export cooks documents into packs → `assets/packs-export`
- Saves off the main thread in the editor → `editor/saving`
- Untrusted input and checksums in general → `assets/robustness`
- Hashes, checksums (CRC-32C among them), JSON and UTF-8 → `basics/bytes`, `basics/data-formats`
- Atomic writes → `core/files`
- Lenient reads of property values → `world/reflection`

**Fit.** `over`: about 6,550 words against L (5,000). XL by S2: the estimate is at L's top (6,500) and inside XL's
range (6,501 to 10,000); four exercises, four excerpts and five figures take most of it.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scene-ecs:33` | feature | home | `DuplicateEntity`: a deep copy with fresh UUIDs, inserted after the original, references inside remapped |
| `scene-ecs:153-154` | feature | home | The DOM form and `SceneSerializer`'s functions; the three-pass read with a union-find: a parent that is invalid, missing or would close a cycle is dropped with a warning and the entity attached at the top level, and the load goes on (`SceneSerializer.cpp:509-556`, `EntitySink.cpp:85-135`) |
| `scene-ecs:156-162` | feature | home | Unknown components, the streaming writer, the streaming reader, the sinks, `SceneReadProgress`, the cooked form STSC with its reader's rules across builds (an unknown property skipped with a warning, a changed type failing the whole read, a type this build lacks kept as an unknown component: `CookedScene.cpp:381`, `:447`, `:459-476`), scene settings and the old collision layers in documents |
| `scene-ecs:205` | feature | home | `PropertyBinary`: binary property values for cooked scenes, strings up to 1 MiB |
| `scene-ecs:155` | feature | link | Lenient reads, taught in `world/reflection` |
| `scene-ecs:342`, `scene-ecs:347` | concept | home | Serialization formats and their trade-offs; references between entities and assets in data, remapped on copies |
| `scene-ecs:398` | code | home | `Strata/src/Strata/Scene/SceneSerializer.cpp:73-122`: `RemapEntityReferences`, through reflection and `ExtraReferences` |
| `scene-ecs:399` | code | home | `Strata/src/Strata/Scene/SceneDocumentWriter.h:77-94`: the writer's contract, one entity per line; with the two sample files of section 1 |
| `scene-ecs:400` | code | home | `Strata/src/Strata/Scene/SceneDocumentWriter.cpp:380-507`: `WriteEntities`, two batches: parallel serialization, ordered writing, deterministic bytes |
| `scene-ecs:401` | code | home | `Strata/src/Strata/Scene/EntitySink.cpp:397-470`: `SceneBuilder::Finish`, link once all entities exist and signal last; with the interface at `EntitySink.h:29-50` |
| `scene-ecs:449`, `scene-ecs:451`, `scene-ecs:453`, `scene-ecs:454`, `scene-ecs:493` | figure | home | The document's layout annotated, against the old layout; the streaming read and its parallel path; the write pipeline as a timeline; the cooked file's layout; a diff after one entity moved |
| `scene-ecs:548`, `scene-ecs:550`, `scene-ecs:559` | rule | home | Never a DOM of a whole document; loaders reject truncated or garbage bytes and honour cancellation, and a cooked format change extends the corruption tests; keep unknown data |
| `scene-ecs:586`, `scene-ecs:590`, `scene-ecs:605` | hands-on | home | The counting sink; the corrupted cooked scene; the diff of a saved scene |
| `new:21` | hands-on | home | The "trace it yourself" exercise (D27): a hand-written scene document of two entities that name each other as parents is loaded; the reader predicts the result (both load, the second at the top level, one warning), then follows the warning with a search or a breakpoint back to `LinkParents` in `EntitySink.cpp`, where the union-find finds both ends already connected, and to the DOM reader's third pass, which does the same (about 250 words). Evidence: `Strata/src/Strata/Scene/EntitySink.cpp:85-92`, `:130-135`, `:415`; `Strata/src/Strata/Scene/SceneSerializer.cpp:509-511`, `:556` |
| `scene-ecs:657`, `scene-ecs:659-663`, `scene-ecs:665` | term | home | Unknown component, DOM, streaming or event parser, entity sink, snapshot (the scene's meaning), cooked scene, MessagePack |
| `scene-ecs:664` | term | link | CRC-32C, the checksum of the cooked header, named in section 7; taught in `basics/data-formats` |
| `worlds-runtime:550` | term | home | Cooked documents (scenes, prefabs and models read without parsing JSON): one glossary entry with cooked scene |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| JSON, UTF-8, hashes and checksums | `basics/data-formats` | must |
| Bytes in a binary file: sizes, offsets and alignment | `basics/bytes` | must |
| Files that may be cut short; atomic writes | `core/files` | must |
| Jobs, and results kept in order from parallel work | `core/jobs` | must |
| `ComponentInfo`, `PropertyInfo`, extra data and `ExtraReferences` | `world/reflection` | must |
| The hierarchy, `RelationshipComponent` and change signals | `world/scene-graph` | must |
| Union-find (disjoint sets) | `basics/trees-graphs` | helps |
| An asset is named by an `AssetHandle` and read by a loader | `assets/loading` | helps |
| Input that cannot be trusted | `assets/robustness` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cooked-documents` | Cooked documents | - |
| `cooked-scene` | Cooked scene | CookedScene |
| `dom` | DOM | - |
| `entity-sink` | Entity sink | - |
| `messagepack` | MessagePack | - |
| `snapshot-world` | Snapshot (world) | - |
| `streaming-parser` | Streaming parser | event parser |
| `unknown-component` | Unknown component | - |
