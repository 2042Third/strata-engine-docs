# Notes: `world/serialization`

## New terms

- **union-find**: for each entity, a pointer toward a representative of its group, so two entities are in one group
  exactly when they have the same representative. Home: `basics/trees-graphs` (the brief lists it as "helps"); the page
  gives this one-sentence working definition in bold in "A toy version" because that page is outside the closure and
  nothing marks the term. Aliases: disjoint sets.

The page also defines in bold the glossary's own entries homed here: DOM, streaming parser (event parser), unknown
components, entity sink, snapshot, cooked scene, cooked documents, MessagePack.

## Requests

- Hosts for Further reading, all cited without a link: `ecma-international.org` (ECMA-404, the JSON standard),
  `docs.unity3d.com` (Unity's manual on its YAML scene format), `docs.godotengine.org` (the `.tscn` file format),
  `protobuf.dev` and `flatbuffers.dev` (Protocol Buffers and FlatBuffers), `msgpack.org` (the MessagePack
  specification). `github.com` is already allowed and carries no link on this page either.
- No word beyond the lists: every word-list finding was reworded.

## Since

`since: 0.3.0`: the DOM serializer, the three-pass read, unknown components and settings came with wave 1 (rows
`scene-ecs` 153-154 and 156 give 0.3.0 and 0.3.0 wave 1). The stream writer, reader, sinks and the cooked form STSC
came in 0.4.0 (`scene-ecs` 157-161); the page's subject, scene documents, is older than the first tag in its first
form, so 0.3.0.

## Not verified

- The claims about other engines (Unity's YAML scenes, Godot's text scenes, Unreal's binary packages, Protocol Buffers
  and FlatBuffers as schema-driven binary formats) come from their public documentation as I know it, not checked
  against the cited pages in this session.
- The diff of the camera move in `Loading.stscene` was made by editing the sample's line (Translation `[0,0,0]` to
  `[0,2,0]`), not by running the editor; that a save writes the rest of the line byte for byte as the sample has it
  follows from the sample being in the streamed layout, not from a run.
- Exercise 1: that `scene.save` accepts a scene with no changes (the "save once" step), that `component.set` takes
  `Transform` with `Translation` as written, and that `git diff --word-diff` shows the change as described were not run.
- Exercise 3: that a hand-written `.stscene` placed in a copy of a sample project opens in the editor was not run; the
  chain of calls (`SceneAsset::Deserialize`, `SceneSerializer::DeserializeText`, `SceneBuilder::Finish`, `LinkParents`)
  was read in the code (`Prefab.cpp` 347-380, `SceneSerializer.cpp` 299-313, `EntitySink.cpp` 397-470), and the
  warning text and the logging (`SceneAsset::LogWarnings`, `Scene 'Cycle': ...`) at the pin.
- The factor of four between the text and a tree of values in "A million entities" is stated as an assumption; the
  569 bytes for each entity is 3,984 bytes divided by 7 for the sample.
- The 7 background threads of the write example are an assumption; the formula (two chunks for each thread plus one,
  between 4 and 64) is `SceneDocumentWriter.cpp` 394 and 32-34, and the page keeps only the "two chunks for each
  thread plus one" part.
- "A column by hand" assumes three entities that have only a transform; the sizes (12, 16 and 12 bytes) follow from
  the property types of `TransformComponent` (`glm::vec3`, `glm::quat`, `glm::vec3`) and `PropertyBinary.h`, not from a
  cooked file that was written and measured.
- That the editor's save writes a copy of the scene on a background job and that the recovery journal uses the SHA-256
  and the import records the FNV-1a hash are the comments of `SceneDocumentWriter.h`, not traced into the editor code.
- The doctest filter `--test-suite=Scene.Documents` and the `ctest` line were not run. The test names were read in
  `SerializationTests.cpp`, `SceneDocumentTests.cpp`, `CookedSceneTests.cpp` and `RobustnessTests.cpp`.
- That a chain of 50,000 entities loads in linear time is the comment and the test `Very deep hierarchies never
  exhaust the stack` (`RobustnessTests.cpp` 222-262), which checks the result and the stack, not the time.

## Findings not applied

- The brief names no open findings.
- The brief calls the DOM read a three-pass read. The code has three passes (IDs and mapping, entities and components,
  hierarchy) and then two more steps in `DeserializeEntities` (remap of references when IDs changed, then the
  observers are told); the page says "three passes, then two more steps".
- The brief's figures: the annotated layout, the older layout and the diff are `text` and `diff` fences, not figure
  requests; the streaming read's data flow is the map's diagram and prose, not a separate figure; the write pipeline
  is a Mermaid diagram; the cooked file's layout is a `text` fence and the "A column by hand" example, without the
  byte-level picture of a column (dense flag or indices). No figure manifest.
- The brief's item "the parallel read of documents of 16,384 entities or more, by lines or by a structure scan" is
  taught; the `StructureScanner` and `FindEntityLines` functions are not quoted.
- The brief asks for "unknown component with section 2's paths, about 100 words" in the cooked section: the page covers
  the cooked paths in two sentences (a type this build lacks decodes as JSON and is kept; the unknown-components
  section holds MessagePack) and does not repeat the text paths.
- No "What went wrong before" section: the history has no bug of this subject with a regression test that I found;
  `Parent cycles in entity data are broken instead of corrupting the hierarchy` is named in "How it is tested".
- No `tutorials/` patch: the card asks for one only after `core/first-change`, and the done exercise is a standalone
  sketch (`sketches/world-serialization-fuzz.cpp`).
- The toy is two sketches (`world-serialization-toy.cpp`, 85 lines, and `world-serialization-cooked.cpp`, 109 lines),
  above kind I's 30 to 80: the union-find and the cooked checks did not fit in one sketch of 80 lines in Hazel style.
- The brief's exercise "an `EntitySink` that counts entities per component type" is answered in pseudocode, because it
  needs the engine; the done exercise is the corruption sketch.
- `scene-ecs:33`'s `DuplicateEntity` is taught in prose in "Snapshots and references"; `Scene.cpp` 659-677 is not
  quoted.
- The page has 6,466 prose words, inside L's range but near its top; `passive` (34) and `noun-stack` (4) warnings were
  not all reworded.

## Clerk

- Refused: union-find: homed on `basics/trees-graphs` (only its home words it).
- `external-hosts.txt`: `ecma-international.org`, `protobuf.dev`, `flatbuffers.dev`, `msgpack.org` (front pages fetched: Ecma International, Protocol Buffers, FlatBuffers, MessagePack); `docs.unity3d.com` and `docs.godotengine.org` are listed already.

## Walk E-final-9

Track walk E-final-9 (2026-11-24; work folder `docs-work/walkfix-E9`, `measure.py`, `pagelines.ps1`; the official
0.8.0 package, a `--no-gpu` editor). A copy of `OpenWorld` under git: opening `Scenes/Loading.stscene` and saving it
once changed two lines (`git diff --numstat` 2 2): the first line lost `MaxBodyPairs` and the empty `PhysicsLayers`
table, the camera's line gained `Aperture`, `DepthOfField`, `FocusDistance`, `FocusEntity` and `SensorHeight`, and the
file grew from 3,984 to 4,026 bytes (9 lines still). After a commit, `component.set` of the camera's Translation to
(0, 2, 0) and a save changed one line (1 1); the page's diff now holds that line as the editor writes it. Plain
`git diff --word-diff` marks the whole entity line (no spaces in it); `--word-diff-regex=[A-Za-z0-9.-]+` marks
`[0,[-0-]{+2+},0]`. The cycle document imported with `asset.import` (file outside the project, directory `Scenes`)
and opened with `scene.open`: `scene.hierarchy` lists `Second` at depth 0 and `First` below it, and `log.read`
(`minLevel` Warn) holds the page's warning. The PowerShell lines of both exercises were run as the page writes them.
To stay inside size L the walk's additions were paid for by shortening seven sentences of the body (the batch example
of 7 threads, the 49 chunks of 100,000 entities, the `Progress` clause and four rewordings).

## Engine

- The committed samples were written by an older editor: the first save of `Samples/OpenWorld/Assets/Scenes/Loading.stscene`
  in the 0.8.0 editor drops `MaxBodyPairs` and `PhysicsLayers` from the first line and adds five camera keys, so a
  reader's first diff of an untouched sample is not empty. The page says so; for the engine's agents, saving the
  samples once with the current editor would make a first save change nothing.
