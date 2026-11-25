---
id: world/serialization
title: "Scene documents: text, streams and the cooked form"
description: "How Strata stores a scene as JSON text and as the cooked binary form, writes and reads millions of entities as a stream, and refuses bad input."
kind: internals
size: L
tracks: [E]
needs: [world/scene-graph, world/reflection, core/files]
time: 120
learn:
  - id: layout
    text: name the parts of a scene document and explain why Strata writes one entity on each line
  - id: read
    text: predict what the reader does with a parent that is missing, invalid or part of a cycle
  - id: stream
    text: explain what a streamed read and write hold in memory and why the bytes do not depend on the thread count
  - id: cooked
    text: trace how the cooked reader validates its bytes and what it does with an unknown property, a changed type and an unknown component
  - id: sink
    text: write an entity sink that reads a document without making a scene
since: 0.3.0
status: final
---

A scene lives in memory as entities in a registry, but it must also live in files. The editor saves it, the game loads it, the undo stack copies it, and an export ships it. This page is about the forms a scene takes outside memory and how Strata writes and reads each one safely. There are three: a :term[JSON]{id=json} document read as a tree, the same document handled as a stream, and a binary form named `STSC` that exports use.

Other pages cover how a scene asset reaches the running game ([asset loading](../assets/loading.md) and [sub-scenes](../world/sub-scenes.md)) and how a prefab is placed in a scene ([prefabs](../world/prefabs.md)). They also cover when an export cooks documents into packs ([packs and export](../assets/packs-export.md)) and how the editor saves off the :term[main thread]{id=main-thread} ([saving](../editor/saving.md)).

The exercises use the installed Strata, its samples and `StrataCLI` ([How to read this book](../start/how-to-read.md)). The :term[source files]{id=source-file} are in your clone of [your first engine change](../core/first-change.md).

## The problem and how engines solve it

Close the editor and everything in memory is gone. To keep a scene you write it to a file, and to use it again you read the file. Four questions decide how well that goes.

- Text or binary? A person or an agent can read, search and compare a text file. A binary file is smaller and quicker to load.
- A whole tree or a stream? You can load a file into memory as one tree, called a document object model (DOM), or read it piece by piece and keep only what you need.
- What happens when the format changes? An old file must still load in a new engine, and an old engine should not destroy the data of a new file.
- Does the same scene always give the same :term[bytes]{id=byte}? If it does, a comparison of two files shows only real changes, and a :term[hash]{id=hash} says whether anything changed.

A **DOM** is the tree of values you get when you read a whole document into memory at once.

A **streaming parser**, also called an event parser, reads the text from start to end. It calls your code for each piece it meets, such as the start of an object or a number, and builds no tree.

:::example[A million entities]
The sample scene `Samples/OpenWorld/Assets/Scenes/Loading.stscene` takes 3,984 bytes for 7 entities, about 569 bytes for each. A scene of 1,000,000 such entities takes about 569 MB of text. Assume that a tree of values takes four times the text it came from. A DOM of the whole document then needs about 2.3 GB beside the text, while the tree of one entity takes about 2,276 bytes. A stream holds the text, one entity's tree and what the reader builds, so the tree never grows with the document.
:::

| Approach | What it gives | What it costs |
| --- | --- | --- |
| Text read as a tree | The simplest code, and any key order | Memory for the whole tree |
| Text read as a stream | Memory for one entity at a time | Code that keeps its place while events arrive |
| Binary read in one pass | The smallest files and no text to read | People cannot read it, and every change needs a version |

Versions raise a second problem. A new engine reading an old file knows every old field, but an old engine reading a new file meets fields and components it has never heard of. It can refuse the file, skip what it does not know, or keep it and write it back unchanged. Strata refuses a version it cannot read, and keeps the unknown fields and components of a version it can.

Bytes raise a third. A map that lists keys in random order changes the bytes without changing the scene. So does a float that prints as `0.10000000149011612` in one place and `0.1` in another, and so do two threads that finish in a different order each time. Each change is noise in a file comparison, and each breaks a hash that should say whether the content is new.

Strata keeps JSON text as the form that people and agents read and compare. It reads and writes scenes, prefabs and models as a stream, and builds a DOM only for snapshots and small documents. It keeps the binary form for exports, where nobody reads the file and load time matters.

## The map

Three groups of code share the work. `SceneSerializer` owns the format's :term[header]{id=header} and version, the DOM form and the snapshot functions. `SceneDocumentWriter` and `SceneDocumentReader` stream documents, and the reader hands what it finds to an `EntitySink`. `CookedSceneWriter` and `CookedSceneReader` handle the binary form, working from an `EntityPrototype`, a stored set of entities that [prefabs](../world/prefabs.md) teaches.

```mermaid caption="One stream writer makes the text document and one stream reader feeds a sink. The cooked form is made from a prototype and read back into one." alt="A scene goes through the writer into a text document, then through the reader into a sink. The sink is a scene builder, a prototype builder or a reference scan. A prototype goes through the cooked writer into a cooked document, and the cooked reader turns it back into a prototype."
flowchart LR
    S["Scene in memory"] -->|"save"| W["SceneDocumentWriter"]
    W --> T["Text document"]
    T --> R["SceneDocumentReader"]
    R --> K["EntitySink"]
    K --> B["SceneBuilder: a scene"]
    K --> P["EntityPrototypeBuilder: a prototype"]
    K --> A["Reference scan: asset handles"]
    P --> CW["CookedSceneWriter"]
    CW --> C["Cooked document: STSC"]
    C --> CR["CookedSceneReader"]
    CR --> P
```

Both stream classes run on any thread. The writer needs a scene that nothing changes while it runs, so the editor writes a copy of the scene on a background job.

## The contract

Code that calls these classes may rely on five things.

- The same scene and options give the same bytes, whatever the thread count or chunk size.
- A read either fails with a reason or gives entities whose parents are valid and form no cycle.
- Data that is odd but still understood gives a warning, never a failure: an unknown property, an unknown component, a missing parent.
- A failed read can leave part of the document in the scene, so the caller discards that scene.
- A cancelled write or read ends at its next check and reports that it was cancelled.

Code that changes the formats follows rules, each with its reason.

:::rule[Never build a DOM of a whole scene document]
Write with `SceneDocumentWriter` and read with `SceneDocumentReader`. A million entities as a tree cost several GB, and a stream holds one entity. DOMs are for snapshots and small documents.
:::

:::rule[Keep unknown data]
Opening a file in a build without the module that wrote part of it must not erase that part. The build stores what it cannot interpret and writes it back unchanged.
:::

:::rule[Loaders reject truncated or garbage bytes, and a cooked format change extends the corruption tests]
A loader meets files that a crash cut short or a disk damaged. It must refuse them without crashing and stop when asked to cancel. The cooked form has its own corruption tests, and a layout change adds cases to them.
:::

Two more rules follow from the format. The reader skips keys it does not know, so adding a key with a default needs no new version. A change that older readers cannot skip must raise `c_FormatVersion`, because every reader refuses a version above its own. [Robust asset loading](../assets/robustness.md) explains why no file is trusted.

## A toy version

Before the real code, a toy shows the part of reading that is easiest to get wrong: the hierarchy. A document lists entities one per line, each with a parent that may come later in the file, or may not exist. The toy reads all lines first and links parents afterwards. To refuse a cycle it keeps a :term[union-find]{id=union-find}: for each entity, a pointer toward a representative of its group, so that two entities are in one group exactly when they have the same representative. In the code, `FindRoot` and one comparison in `LinkParents` do this.

```cpp sketch="world-serialization-toy.cpp"
// A toy scene reader: one entity per line, parents linked once every entity is read, cycles refused with a union-find.
#include <cstdio>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <vector>

namespace
{
	constexpr size_t c_NoParent = static_cast<size_t>(-1);

	struct Entity
	{
		std::string Id;
		std::string Parent; // "-": top level
	};

	size_t FindRoot(std::vector<size_t>& connected, size_t index)
	{
		size_t root = index;
		while (connected[root] != root)
			root = connected[root];
		while (connected[index] != root) // Path compression: later searches start closer to the root
		{
			const size_t next = connected[index];
			connected[index] = root;
			index = next;
		}
		return root;
	}

	// The index of each entity's parent. A missing parent or one that would close a cycle leaves the entity at the top level.
	std::vector<size_t> LinkParents(const std::vector<Entity>& entities)
	{
		std::map<std::string, size_t> indexOf;
		for (size_t index = 0; index < entities.size(); index++)
			indexOf[entities[index].Id] = index;

		std::vector<size_t> connected(entities.size());
		std::iota(connected.begin(), connected.end(), size_t(0));
		std::vector<size_t> linked(entities.size(), c_NoParent);
		for (size_t index = 0; index < entities.size(); index++)
		{
			const Entity& entity = entities[index];
			if (entity.Parent == "-")
				continue;
			const auto parent = indexOf.find(entity.Parent);
			if (parent == indexOf.end())
			{
				std::printf("warning: %s: parent %s not found\n", entity.Id.c_str(), entity.Parent.c_str());
				continue;
			}
			const size_t childRoot = FindRoot(connected, index);
			const size_t parentRoot = FindRoot(connected, parent->second);
			if (childRoot == parentRoot) // Both ends already connected: this link would close a loop
			{
				std::printf("warning: %s: parent %s would create a cycle\n", entity.Id.c_str(), entity.Parent.c_str());
				continue;
			}
			connected[childRoot] = parentRoot;
			linked[index] = parent->second;
		}
		return linked;
	}
}

int main()
{
	const std::string document = "Root -\nArm Root\nHand Arm\nLamp Ghost\nPing Pong\nPong Ping\n";
	std::vector<Entity> entities;
	std::istringstream lines(document);
	for (Entity entity; lines >> entity.Id >> entity.Parent;)
		entities.push_back(entity);

	const std::vector<size_t> linked = LinkParents(entities);
	for (size_t index = 0; index < entities.size(); index++)
	{
		if (linked[index] == c_NoParent)
			std::printf("%s: top level\n", entities[index].Id.c_str());
		else
			std::printf("%s: child of %s\n", entities[index].Id.c_str(), entities[linked[index]].Id.c_str());
	}
	return 0;
}
```

```text output-of="world-serialization-toy.cpp"
warning: Lamp: parent Ghost not found
warning: Pong: parent Ping would create a cycle
Root: top level
Arm: child of Root
Hand: child of Arm
Lamp: top level
Ping: child of Pong
Pong: top level
```

1. **Lines 19–31:** `FindRoot` follows pointers to the group's representative and shortens the path as it goes.
2. **Lines 54–60:** Equal representatives mean both ends are in one group, so the link would close a loop.
3. **Line 61:** A link that passes joins the child's group to the parent's.

The input has six lines. `Lamp` names a parent that does not exist, and `Ping` and `Pong` name each other. `Ping` links first, because its parent is in a different group. When `Pong` asks, both ends are already in one group, so linking would close a loop, and `Pong` stays at the top level. The order of the lines decides which of the two keeps its parent, and the real reader behaves the same way.

The second toy is the binary side. A cooked document is bytes, and the reader cannot trust any of them. The toy writes a header with a :term[magic number]{id=magic-number}, a version, a count and a :term[CRC-32C]{id=crc-32c} :term[checksum]{id=checksum} of the body, then one record for each entity. Look at the order of the checks in `Check`: the size and the checksum come before any record is read, and the rule that a parent comes before its entity comes last.

```cpp sketch="world-serialization-cooked.cpp"
// A toy cooked document: a header with a checksum, then one record per entity, every part checked before it is used.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <set>
#include <string>
#include <vector>

namespace
{
	constexpr uint32_t c_Version = 1;
	constexpr uint32_t c_NoParent = 0xFFFFFFFFu;
	constexpr size_t c_HeaderBytes = 16;
	constexpr size_t c_RecordBytes = 12; // A u64 ID and a u32 parent index

	uint32_t Crc32C(const uint8_t* data, size_t size)
	{
		uint32_t crc = 0xFFFFFFFFu;
		for (size_t index = 0; index < size; index++)
		{
			crc ^= data[index];
			for (int bit = 0; bit < 8; bit++)
				crc = (crc >> 1) ^ (0x82F63B78u & (0u - (crc & 1u)));
		}
		return ~crc;
	}

	struct Record
	{
		uint64_t Id;
		uint32_t Parent;
	};

	void Put(std::vector<uint8_t>& bytes, size_t offset, const void* value, size_t size)
	{
		std::memcpy(bytes.data() + offset, value, size);
	}

	std::vector<uint8_t> Write(const std::vector<Record>& records)
	{
		std::vector<uint8_t> bytes(c_HeaderBytes + records.size() * c_RecordBytes);
		for (size_t index = 0; index < records.size(); index++)
		{
			Put(bytes, c_HeaderBytes + index * c_RecordBytes, &records[index].Id, 8);
			Put(bytes, c_HeaderBytes + index * c_RecordBytes + 8, &records[index].Parent, 4);
		}
		const uint32_t count = static_cast<uint32_t>(records.size());
		const uint32_t crc = Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes);
		Put(bytes, 0, "TOYC", 4);
		Put(bytes, 4, &c_Version, 4);
		Put(bytes, 8, &count, 4);
		Put(bytes, 12, &crc, 4);
		return bytes;
	}

	// Returns an empty string when the bytes are a valid document, else the reason they are refused.
	std::string Check(const std::vector<uint8_t>& bytes)
	{
		if (bytes.size() < c_HeaderBytes)
			return "shorter than its header";
		uint32_t version = 0, count = 0, crc = 0;
		std::memcpy(&version, bytes.data() + 4, 4);
		std::memcpy(&count, bytes.data() + 8, 4);
		std::memcpy(&crc, bytes.data() + 12, 4);
		if (std::memcmp(bytes.data(), "TOYC", 4) != 0)
			return "wrong magic";
		if (version != c_Version)
			return "unsupported version";
		if ((bytes.size() - c_HeaderBytes) / c_RecordBytes != count || (bytes.size() - c_HeaderBytes) % c_RecordBytes != 0)
			return "count does not match the size";
		if (Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes) != crc)
			return "checksum does not match";
		std::set<uint64_t> seen;
		for (uint32_t index = 0; index < count; index++)
		{
			Record record {};
			std::memcpy(&record.Id, bytes.data() + c_HeaderBytes + index * c_RecordBytes, 8);
			std::memcpy(&record.Parent, bytes.data() + c_HeaderBytes + index * c_RecordBytes + 8, 4);
			if (record.Id == 0 || !seen.insert(record.Id).second)
				return "null or repeated ID";
			if (record.Parent != c_NoParent && record.Parent >= index)
				return "parent does not come before its entity";
		}
		return {};
	}

	void Report(const char* label, const std::vector<uint8_t>& bytes)
	{
		const std::string reason = Check(bytes);
		std::printf("%-22s %s\n", label, reason.empty() ? "accepted" : ("refused: " + reason).c_str());
	}
}

int main()
{
	const std::vector<uint8_t> good = Write({ { 11, c_NoParent }, { 12, 0 }, { 13, 1 } });
	Report("valid", good);
	Report("cut short", std::vector<uint8_t>(good.begin(), good.end() - 5));
	std::vector<uint8_t> flipped = good;
	flipped[20] ^= 0x04;
	Report("one bit flipped", flipped);
	std::vector<uint8_t> forward = good;
	const uint32_t later = 2;
	Put(forward, c_HeaderBytes + 8, &later, 4); // Entity 0 now names entity 2 as its parent
	const uint32_t crc = Crc32C(forward.data() + c_HeaderBytes, forward.size() - c_HeaderBytes);
	Put(forward, 12, &crc, 4); // The checksum is repaired, so the check reaches the parent rule
	Report("parent after child", forward);
	return 0;
}
```

```text output-of="world-serialization-cooked.cpp"
valid                  accepted
cut short              refused: count does not match the size
one bit flipped        refused: checksum does not match
parent after child     refused: parent does not come before its entity
```

1. **Lines 16–26:** The CRC-32C runs bit by bit over each byte of the body.
2. **Lines 69–72:** The count against the size, then the checksum: both before any record is read.
3. **Lines 79–82:** Only then do the rules about identifiers and parents run.
4. **Lines 105–107:** The test repairs the checksum so that the check reaches the parent rule.

Each damaged copy is refused for its own reason. The last one shows why the checks must reach the contents: its checksum was repaired, so only the parent rule could catch the mistake. A checksum shows that the bytes are the ones written, not that the writer wrote a sound document.

## The real code: the text document

### What a scene file looks like

The streamed layout puts the header, the name, the settings and the entity count on the first line, then one entity on each line. This sketch of `Loading.stscene` of the sample `OpenWorld` replaces long values with `…`; the real file has 9 lines for its 7 entities.

```text
{"Strata":{"Format":"Scene","Version":1},"Scene":{"Name":"Loading","Settings":{…},"EntityCount":7,"Entities":[
{"Components":{"Camera":{…},"Name":{"Name":"Camera"},"Transform":{…}},"ID":"091558F6E234E59C"},
{"Components":{…},"ID":"96F962E7E8CDD817"},
…
]}}
```

Each entity line holds its components and its identifier (ID), and a `Parent` key when the entity has a parent. Keys inside an entity are in sorted order, floats print in the shortest form that reads back to the same number, and entities come in hierarchy order, with parents first and siblings in their order. A prefab or model document has the same layout with its own format name and no name or settings.

Compare the older layout of `Samples/Tetris/Assets/Scenes/Main.stscene`, shown here without its middle.

```text
{
	"Scene": {
		"Entities": [ … ],
		"Name": "Main",
		"Settings": { … }
	},
	"Strata": { "Format": "Scene", "Version": 1 }
}
```

The older layout puts a tab before each level and every number of an array on its own line. Its 19 entities take 1,154 lines and 18,210 bytes, about 958 bytes each against 569 for the streamed layout. Its keys are sorted, so the header comes last, after the entities. The reader accepts both layouts.

An older editor wrote the sample, so the first save changes two lines. The first loses `MaxBodyPairs` and an empty `PhysicsLayers`, and the camera's gains five newer keys, such as `Aperture`.

After that save, move the camera from (0, 0, 0) to (0, 2, 0) and save again. In the streamed layout one line changes, and a :term[diff]{id=diff} shows the old and the new entity line whole.

```diff
-{"Components":{"Camera":{"Aperture":2.8,"ClearColor":[0.02,0.04,0.06,1],"DepthOfField":false,"FocusDistance":10,"FocusEntity":"0000000000000000","OrthographicFar":1000,"OrthographicNear":0.1,"OrthographicSize":10,"PerspectiveFOV":60,"PerspectiveFar":1000,"PerspectiveNear":0.1,"Primary":true,"Projection":"Perspective","SensorHeight":24},"Name":{"Name":"Camera"},"Transform":{"Rotation":[0,0,0,1],"Scale":[1,1,1],"Translation":[0,0,0]}},"ID":"091558F6E234E59C"},
+{"Components":{"Camera":{"Aperture":2.8,"ClearColor":[0.02,0.04,0.06,1],"DepthOfField":false,"FocusDistance":10,"FocusEntity":"0000000000000000","OrthographicFar":1000,"OrthographicNear":0.1,"OrthographicSize":10,"PerspectiveFOV":60,"PerspectiveFar":1000,"PerspectiveNear":0.1,"Primary":true,"Projection":"Perspective","SensorHeight":24},"Name":{"Name":"Camera"},"Transform":{"Rotation":[0,0,0,1],"Scale":[1,1,1],"Translation":[0,2,0]}},"ID":"091558F6E234E59C"},
```

The other lines stay as they are.

:::why[One entity on each line]
One choice serves three needs. The writer can turn chunks of entities into text on many threads and write each chunk unchanged, because an entity line does not depend on its neighbours. The reader can split a large file into lines without reading it as JSON, and a diff names the entity that changed. The cost is long lines without spaces, which `git diff --word-diff` marks whole; with `--word-diff-regex=[A-Za-z0-9.-]+` it marks `[-0-]{+2+}` alone.
:::

The `Settings` object holds the scene's gravity, fixed time step, per-frame limits and physics capacity. Reading clamps or ignores bad values: `MaxFixedStepsPerFrame` clamps to 1 to 64, and a `Gravity` that is not a vector is ignored with a warning. Keys that nothing writes now are ignored too, such as the sample's `MaxBodyPairs`, from a physics library the engine no longer uses.

Release 0.5.0 wrote a `PhysicsLayers` table of collision layers into every scene document, and the layers have belonged to the project since. The reader still takes such a table, skipping invalid entries with warnings, and the project's layers replace it when a program with a project takes the scene.

### The DOM form and its three passes

`SceneSerializer::Serialize` builds the document as a DOM: the header, then `Scene` with `Name`, `Settings` and `Entities`. `SceneSerializer::Deserialize` reads such a tree into an empty scene, and `SerializeEntities` and `DeserializeEntities` do the same for a snapshot of some entities. The header check is strict: `Format` must be `Scene`, and `Version` must be at least 1 and at most `c_FormatVersion`, which is 1. Anything else fails with a message before the reader makes a single entity.

Reading entities takes three passes over the list, then two more steps.

1. Pass 1 checks every `ID` and builds the table that maps each ID to the ID the entity will have. An ID that is present but invalid fails the read, an ID that appears twice does too, and a missing ID gets a new one.
2. Pass 2 makes each entity with a name and a transform, then reads each component through the checked path of [reflection](../world/reflection.md), which warns about what it cannot read as written.
3. Pass 3 decides the hierarchy.

The third pass is the reason the passes exist. A child may come before its parent in a hand-written file, so no link can be made until every entity exists. For each entity in document order, pass 3 asks three questions: is the `Parent` value an ID at all, does an entity with that ID exist, and would the link close a cycle? If the answer to the first or second is no, or to the third is yes, the entity goes to the top level with a warning and the load continues.

The cycle question uses the union-find of the toy. An accepted link joins the child's group to the parent's, so a link closes a cycle exactly when both ends are already in one group. The answer comes in nearly :term[constant time]{id=constant-time}, so the check stays linear for a chain of 50,000 entities, which a test of `Scene.Robustness` loads back.

After pass 3 the code links the entities. When the read made new IDs, as a copy does, it points entity references at the copies, as [the snapshots section](#the-real-code-snapshots-and-references) shows. Last, it tells the components' observers about every component, so that systems see the finished state.

### Unknown components

A file may name a component that this build has not registered, because it belongs to a module the build lacks or to a newer engine. **Unknown components** are those components. Strata keeps each one as JSON in an `UnknownComponentsComponent` on the entity. The writer merges the kept JSON back into the entity's components in name order, so the next save writes it as it was. The reader warns once per name, with the count of entities: `Unknown component 'Foo' (3 entities) kept unchanged: no module of this build registers it`.

The component is runtime-only and not registered, so the Inspector does not show it, but `Scene::Copy`, prefab snapshots, `DuplicateEntity` and the editor's undo snapshots carry it. Opening a scene in a build without a module, changing something else and saving therefore keeps the module's data.

## The real code: writing and reading as a stream

### The writer

`SceneDocumentWriter::Write` writes the first line, then the entity lines, then `]}}`. Each entity line is byte for byte what `JsonUtils::Dump` writes for the entity object of the DOM form, and a test checks it on the feature scene and on a generated world. The writer builds no such object: it appends text straight into a string.

The writer works in chunks of 4,096 entities, set by `SceneWriteOptions::ChunkEntities`. A chunk is one job, and the jobs of a batch run in parallel. A batch holds two chunks for each thread plus one more thread, from 4 to 64 chunks. One job writes the chunks in order, not as they finish, while the next batch is being formatted, so at most two batches are in flight.

```mermaid caption="One job writes batch k minus 1 while all threads format batch k, so the bytes reach the file in order." alt="Two chains of boxes: batches one to four, formatted in parallel, and batches one to three, written and hashed in order. A dotted arrow joins each batch to the batch of the same number."
flowchart LR
    subgraph Serialize["Format in parallel"]
        direction LR
        S1["Batch 1"] --> S2["Batch 2"] --> S3["Batch 3"] --> S4["Batch 4"]
    end
    subgraph Write["Write and hash in order"]
        direction LR
        W1["Batch 1"] --> W2["Batch 2"] --> W3["Batch 3"]
    end
    S1 -.-> W1
    S2 -.-> W2
    S3 -.-> W3
```

The next quote is the loop that does this. Search it for the parallel loop over the chunks of a batch, the wait for the earlier write before this batch's references join the result, and the job that writes.

```cpp src="Strata/src/Strata/Scene/SceneDocumentWriter.cpp#L428-L482"
for (size_t firstChunk = 0, batchIndex = 0; firstChunk < chunkCount; firstChunk += batchChunks, batchIndex++)
{
	if (isCancelled())
		break;
	std::vector<Chunk>& batch = batches[batchIndex % 2];
	const size_t count = std::min(batchChunks, chunkCount - firstChunk);
	batch.resize(count);
	JobSystem::ParallelFor(static_cast<uint32_t>(count), 1, [&](uint32_t begin, uint32_t end)
	{
		for (uint32_t index = begin; index < end; index++)
		{
			Chunk& chunk = batch[index];
			chunk.Text.clear();
			chunk.References.Clear();
			if (isCancelled())
				return;
			const size_t firstEntity = (firstChunk + index) * chunkEntities;
			const size_t lastEntity = std::min(entityCount, firstEntity + chunkEntities);
			for (size_t entity = firstEntity; entity < lastEntity; entity++)
			{
				chunk.Text += entity == 0 ? "\n" : ",\n";
				appendEntity(chunk.Text, entity, chunk.References);
			}
			entitiesSerialized.fetch_add(lastEntity - firstEntity, std::memory_order_relaxed);
			reportProgress();
		}
	}, options.Priority);

	// The batch before is written by now; then this one's references join the document's, in order.
	JobSystem::Wait(writing);
	if (writeFailed.load() || isCancelled())
		break;
	for (const Chunk& chunk : batch)
	{
		for (const AssetHandle handle : chunk.References.GetReferences())
		{
			if (seen.insert(handle).second)
				result.References.push_back(handle);
		}
	}
	const size_t batchEnd = std::min(entityCount, (firstChunk + count) * chunkEntities);
	writing = JobSystem::Submit([&hashed, &batch, &writeFailed, &entitiesWritten, &reportProgress, batchEnd]()
	{
		for (const Chunk& chunk : batch)
		{
			if (!hashed.Write(chunk.Text))
			{
				writeFailed.store(true);
				return;
			}
		}
		entitiesWritten.store(batchEnd, std::memory_order_relaxed);
		reportProgress();
	}, options.Priority);
}
```

1. **Lines 435–454:** The chunks of one batch are formatted in parallel, each one into its own string, with a cancel check at its start.
2. **Lines 456–459:** The wait for the earlier write comes before anything else touches the result, so at most two batches exist.
3. **Lines 469–481:** One job writes the batch in order and hashes the bytes as they pass, so the hashes need no second read of the file.

The bytes do not depend on the thread count, and the quote shows why. Chunk boundaries come from the entity index, never from timing. A chunk's text depends only on its entities, and the line break before an entity depends on the entity's index, not on its place in a chunk. The batch size changes only how many chunks are in flight. A test writes one scene with different thread counts and chunk sizes and compares the bytes.

The writer also returns the asset handles of every entity, each once in order of first appearance. It returns two hashes of the bytes: a :term[SHA-256]{id=sha-256} digest, which the editor's recovery journal uses as its base, and an :term[FNV-1a]{id=fnv-1a} hash, which the import records keep as a source hash. `Cancel` is asked between chunks, and `Roots` writes a part of the scene.

A write that fails or is cancelled leaves part of a document in its output. `SceneSerializer::SaveToFile` writes through an atomic writer, as [files](../core/files.md) teaches, so the old file stays until the whole new one is ready.

### The reader

`SceneDocumentReader::Read` reads the text with an event parser and sorts the events. It builds the header and the `Name` and `Settings` fields as small DOMs, builds each entity as a DOM of its own and hands it to the sink, and skips unknown keys. Its memory grows with the document only by the text and whatever the sink keeps.

Four rules of the reader matter.

- Keys may come in any order, so the header may follow the entities. The reader checks it when it arrives, and a document without a valid header fails even after its entities reached the sink.
- `EntityCount`, when it comes before the entities, lets the reader refuse a document over the limit at once and tell the sink how much room to reserve. The reader reserves at most the text's size divided by 3, so a false count cannot cause a huge reservation.
- `SceneReadOptions::MaxEntities` stops a document at its first entity past the limit when no count was declared.
- Every `CancelCheckEntities` entities, 256 by default, the reader asks `IsCancelled`. `Progress` reports the share of the text read, and `SceneReadProgress` collects such shares for each scene asset, so a loading screen can show how far a read has come.

Documents of 16,384 entities or more take a second path when the sink agrees to take entities prepared on other threads. The reader finds the entity lines by splitting the text at line ends, which works for the writer's layout, or by scanning the brackets, which works for any layout. It checks first that every entity reads alone, and falls back to the bracket scan, then to the plain stream, when one does not. Jobs then read chunks of 2,048 entities into columns while the reading thread hands the chunks to the sink in order.

### The sinks

An **entity sink** is the receiver of a streamed document: the class `EntitySink` that the reader calls with the small fields and then with each entity. Its interface is small.

```cpp src="Strata/src/Strata/Scene/EntitySink.h#L29-L50"
class EntitySink
{
public:
	virtual ~EntitySink() = default;

	// The count the document declares (EntityCount) when it declares it before its entities, at most the reader's limit:
	// room to reserve. The entities that follow may be fewer (or more, up to the limit).
	virtual void ReserveEntities([[maybe_unused]] uint64_t count) {}
	// A field of the content object other than the entity list ("Name" and "Settings" of scenes), in any order, before or
	// after the entities.
	virtual void ReadField([[maybe_unused]] std::string_view key, [[maybe_unused]] const nlohmann::json& value) {}
	// One value of the entity list (an entity object when the document is valid). False, with the reason, ends the read.
	virtual bool ReadEntity(const nlohmann::json& entity, std::string* outError) = 0;
	// Whether the sink takes entities prepared on worker threads (ReadPrepared): the reader then reads large documents in
	// the writer's layout in parallel (SceneReadOptions::Parallel).
	virtual bool TakesPreparedEntities() const { return false; }
	// The next entities of the list, read into columns on a worker thread as ReadEntity would read them one by one, in
	// document order. The sink may take the values over. False, with the reason, ends the read.
	virtual bool ReadPrepared([[maybe_unused]] PreparedEntities& entities, [[maybe_unused]] std::string* outError) { return false; }
	// Once the whole document is read and its header validated. False, with the reason, fails the read.
	virtual bool Finish(std::string* outError) = 0;
};
```

1. **Line 41:** The reader calls `ReadEntity` once for each value of the list, in document order, with a DOM of that value only.
2. **Line 44:** A sink that returns true here takes entities read into columns on worker threads, which enables the parallel path.
3. **Line 49:** `Finish` runs after the whole document is read and its header validated, and a false result fails the read.

Three sinks ship. `SceneBuilder` builds a scene. `EntityPrototypeBuilder` builds an `EntityPrototype` without a scene, for prefabs, models and snapshots. The reference scan of `AssetDependencies::Scan` builds nothing at all, and it is short enough to read whole.

```cpp src="Strata/src/Strata/Asset/AssetDependencies.cpp#L99-L116"
class ReferenceSink final : public EntitySink
{
public:
	explicit ReferenceSink(ReferenceList& references)
		: m_References(references)
	{
	}

	bool ReadEntity(const nlohmann::json& entity, std::string*) override
	{
		ScanEntityInto(entity, m_References);
		return true;
	}

	bool Finish(std::string*) override { return true; }
private:
	ReferenceList& m_References;
};
```

1. **Lines 107–111:** For each entity it scans the DOM for asset handles and keeps them, and the entity's DOM is gone when the call returns.
2. **Line 113:** `Finish` has nothing to link, so it returns true.

`SceneBuilder` is the sink with work left at the end. It creates each entity and its components in the scene's registry at once, and keeps only the entity and its parent's ID, because a parent may come later. `EntityColumns` serves the parallel path: workers read entities into one array for each component type, and a `SceneBuilder` copies the values out of those arrays.

```cpp src="Strata/src/Strata/Scene/EntitySink.cpp#L414-L455"
std::vector<std::string> parentWarnings;
const std::vector<uint32_t> linked = LinkParents(m_Parents, m_InvalidParents,
	[&](uint32_t index) { return registry.get<IDComponent>(m_Handles[index]).ID; },
	[&](UUID id)
	{
		const auto it = m_Scene.m_EntityMap.find(id);
		return it != m_Scene.m_EntityMap.end() ? indexOfSlot[entt::to_entity(it->second)] : c_NotLinked;
	},
	m_Warnings ? &parentWarnings : nullptr, m_LinkProgress, 0.0f, c_FinishParentsShare);
m_Parents = {};
m_InvalidParents = {};

// The runtime links (HierarchyComponent) are built now that every entity exists: children may be listed before their
// parents. Linking also fills the RelationshipComponents and the root list.
for (const entt::entity handle : m_Handles)
	registry.emplace<HierarchyComponent>(handle);
std::vector<entt::entity> rootHandles;
for (size_t index = 0; index < count; index++)
{
	ReportFinish(m_LinkProgress, c_FinishParentsShare, c_FinishLinksShare, index, count);
	const entt::entity parent = linked[index] != c_NotLinked ? m_Handles[linked[index]] : entt::null;
	if (parent == entt::null)
		rootHandles.push_back(m_Handles[index]);
	m_Scene.LinkLast(m_Handles[index], parent);
}
// Depths, activity and the (stale) world transforms of the new subtrees.
m_Scene.FinishLinking(rootHandles);
m_Scene.m_HierarchyVersion++;

// Components were constructed with default values and filled in afterwards; now that data and hierarchy are complete,
// systems hear of them (on_update) and see the final state.
const std::vector<const ComponentInfo*>& infos = ComponentRegistry::GetAll();
for (size_t index = 0; index < count; index++)
{
	ReportFinish(m_LinkProgress, c_FinishParentsShare + c_FinishLinksShare, 1.0f - c_FinishParentsShare - c_FinishLinksShare, index, count);
	for (const ComponentInfo* info : infos)
	{
		if (info->Has(registry, m_Handles[index]))
			info->MarkModified(registry, m_Handles[index]);
	}
}
m_Handles = {};
```

1. **Lines 414–424:** `LinkParents` decides every entity's parent in one pass, with the same rules and warnings as the DOM's third pass, and the builder drops its parent list.
2. **Lines 428–440:** The builder links each entity in document order, and `FinishLinking` computes depths and activity for the new :term[subtrees]{id=subtree} once, after all links exist.
3. **Lines 443–454:** Only now does the builder tell the components' observers, so systems see finished data and never a scene half built.

The code that decides the hierarchy is `LinkParents`. It is a template over how to find an entity's ID and how to find an entity by ID, so the scene builder and the prototype builder share it. Read how it treats the three bad cases and where the union-find sits.

```cpp src="Strata/src/Strata/Scene/EntitySink.cpp#L92-L141"
std::vector<uint32_t> LinkParents(std::span<const UUID> parents, std::span<const uint32_t> invalidParents, IdOf&& idOf, IndexOf&& indexOf,
	std::vector<std::string>* outWarnings, const EntityReadProgress& progress, float progressStart, float progressShare)
{
	const size_t count = parents.size();
	std::vector<uint32_t> linked(count, c_NotLinked);
	std::vector<uint32_t> connected(count);
	std::iota(connected.begin(), connected.end(), 0u);
	auto findRepresentative = [&connected](uint32_t index)
	{
		uint32_t representative = index;
		while (connected[representative] != representative)
			representative = connected[representative];
		while (connected[index] != representative) // Path compression
			index = std::exchange(connected[index], representative);
		return representative;
	};

	size_t nextInvalid = 0;
	for (uint32_t index = 0; index < count; index++)
	{
		ReportFinish(progress, progressStart, progressShare, index, count);
		if (nextInvalid < invalidParents.size() && invalidParents[nextInvalid] == index)
		{
			nextInvalid++;
			if (outWarnings)
				outWarnings->push_back(fmt::format("Entity {}: invalid 'Parent'; attached at the top level", idOf(index).ToString()));
			continue;
		}
		const UUID parent = parents[index];
		if (!parent.IsValid())
			continue;
		const uint32_t parentIndex = indexOf(parent);
		if (parentIndex == c_NotLinked)
		{
			if (outWarnings)
				outWarnings->push_back(fmt::format("Entity {}: parent {} not found; attached at the top level", idOf(index).ToString(), parent.ToString()));
			continue;
		}
		const uint32_t childRepresentative = findRepresentative(index);
		const uint32_t parentRepresentative = findRepresentative(parentIndex);
		if (childRepresentative == parentRepresentative)
		{
			if (outWarnings)
				outWarnings->push_back(fmt::format("Entity {}: parent {} would create a cycle; attached at the top level", idOf(index).ToString(), parent.ToString()));
			continue;
		}
		connected[childRepresentative] = parentRepresentative;
		linked[index] = parentIndex;
	}
	return linked;
```

1. **Lines 97–107:** Every entity starts in a group of its own, and `findRepresentative` compresses paths, so later searches are short.
2. **Lines 113–129:** An invalid parent and a parent that does not exist leave the entity at the top level, each with its own warning.
3. **Lines 130–139:** Equal representatives mean the link would close a loop, so the entity stays at the top level; otherwise the groups join and the link is recorded.

## The real code: snapshots and references

A **snapshot** is the DOM form of some entity hierarchies, `{"Entities": [...]}`, and copy and paste, the undo stack and prefab edits all hold snapshots. `SerializeEntities` takes a list of :term[root entities]{id=root-entity}, skips a root that sits below another listed root, and writes each remaining root with all its descendants. It keeps a parent link only when the parent is in the snapshot. `DeserializeEntities` makes the entities again by the same passes as a scene. The `EntityInstantiationOptions` say whether each entity gets a new :term[universally unique identifier]{id=uuid} (UUID), which parent the top-level entities take, and which prefab they link to.

Copies must point at copies. Suppose a door entity `A` has a field that names a trigger entity `B`, and you duplicate both. Without a fix, the copy `A'` still names `B`, so the trigger of the copy opens the original door. The reader builds a map from each old ID to its new one and changes every reference found in the map. A reference to an entity outside the copy is not in the map, so it stays as it was.

`DuplicateEntity` is this machine used on one entity. It takes a snapshot of the entity with its descendants, reads it back under the original's parent with new UUIDs, and moves the copy to the place after the original among its siblings.

```cpp src="Strata/src/Strata/Scene/SceneSerializer.cpp#L73-L122"
void RemapEntityReferences(entt::registry& registry, entt::entity handle, const std::unordered_map<UUID, UUID>& mapping)
{
	auto remap = [&mapping](UUID uuid) -> UUID
	{
		auto it = mapping.find(uuid);
		return it != mapping.end() ? it->second : uuid;
	};

	// Entity references in data the properties do not express (script fields), written once they are all found.
	struct ExtraReference
	{
		uint32_t Slot = 0;
		uint32_t Subslot = 0;
		UUID Target = UUID::Null();
	};
	std::vector<ExtraReference> extraReferences;

	for (const ComponentInfo* info : ComponentRegistry::GetAll())
	{
		if (HasFlag(info->Flags, ComponentFlags::NoSerialize))
			continue;
		void* component = info->Get(registry, handle);
		if (!component)
			continue;

		for (const PropertyInfo& property : info->Properties)
		{
			if (property.Type != PropertyType::Entity)
				continue;
			const UUID current = std::get<UUID>(property.GetValue(component));
			const UUID remapped = remap(current);
			if (remapped != current)
				property.Setter(component, remapped);
		}

		if (!info->ExtraReferences)
			continue;
		extraReferences.clear();
		info->ExtraReferences.Visit(component, [&](uint32_t slot, uint32_t subslot, PropertyType type, UUID current)
		{
			if (type != PropertyType::Entity)
				return;
			const UUID remapped = remap(current);
			if (remapped != current)
				extraReferences.push_back({ slot, subslot, remapped });
		});
		for (const ExtraReference& reference : extraReferences)
			info->ExtraReferences.Set(component, reference.Slot, reference.Subslot, reference.Target);
	}
}
```

1. **Lines 75–79:** A reference changes only when the map holds it, so references that leave the copy stay as they are.
2. **Lines 98–106:** Entity-typed properties are found through reflection, so this function names no component type.
3. **Lines 108–120:** Data that is no property, such as script fields, is visited through `ExtraReferences`, and the new targets are written after all are found.

Finding a reference needs reflection, so this code is one more consumer of the description that [reflection](../world/reflection.md) builds. A component that stores an entity reference outside its properties and gives no `ExtraReferences` keeps pointing at the original after a copy.

## The real code: the cooked form

A **cooked scene** is the binary form of a scene document that exports put into packs.

The name **cooked documents** covers scenes, prefabs and models in that form: a load reads them without reading JSON. The format is `STSC`, version 1, written little endian by `CookedSceneWriter` and read by `CookedSceneReader`.

```text
bytes 0 to 63      header: magic "STSC", version, flags, kind, counts, table position, two CRC-32C values
bytes 64 and on    sections, each starting at a multiple of 16 bytes
end of the file    section table: 32 bytes for each section (kind, index, offset, size, count, CRC-32C)
```

The sections are strings, scene information, entity IDs, parents, component types, one column for each component type, and unknown components. The scene information is the name and settings as compact JSON. The IDs are a 64-bit number for each entity. A parent is the index of an entity that comes before it, or `0xFFFFFFFF` for the top level, so a cooked document cannot hold a cycle.

A column holds all the values of one component type. It starts with a flag that says every entity has the type, or else lists the entity indices in rising order. Then come every property's values together, then each value's :term[extra data]{id=extra-data}.

:::example[A column by hand]
Take three entities that all have a transform. Its properties are a translation of 3 floats, a rotation of 4 and a scale of 3, which take 12, 16 and 12 bytes. The column is dense, so it holds an 8-byte flag and count, then three translations, three rotations and three scales: 8 + 36 + 48 + 36 = 128 bytes, already a multiple of 16. The ID section takes 3 times 8 = 24 bytes, padded to 32, and the parent section 3 times 4 = 12 bytes, padded to 16.
:::

Property values go through `PropertyBinary`. A flag takes one byte that must be 0 or 1, and an :term[integer]{id=integer} or a float takes 4. Vectors, colors and rotations are arrays of floats, an asset or entity reference takes 8 bytes, and a string is a 4-byte length and its :term[UTF-8]{id=utf-8} bytes. A string may hold at most 1 MiB, the limit `c_MaxBinaryStringBytes`, and a float that is not finite is written as 0, as in the JSON form.

Extra data, which is no property, takes the component's own binary form when it has one. Otherwise its JSON becomes **MessagePack**, a compact binary encoding of JSON values, in a block of at most 16 MiB.

The file stores no entity references. The reader computes them from the values, as it does for any prototype.

Validation comes before decoding. The next quote is the head of `CookedSceneReader::Read`. Look at what it checks in order, and at what it has not yet looked at.

```cpp src="Strata/src/Strata/Scene/CookedScene.cpp#L579-L597"
// The header.
if (bytes.size() < sizeof(Header))
	return fail("The cooked document is shorter than its header");
Header header {};
std::memcpy(&header, bytes.data(), sizeof(header));
if (std::memcmp(header.Magic, c_Magic, sizeof(c_Magic)) != 0)
	return fail("Not a cooked document");
if (header.Version != c_Version)
	return fail(fmt::format("Unsupported cooked document version {} (supported: {})", header.Version, c_Version));
if (ComputeHeaderCrc(header) != header.HeaderCrc)
	return fail("The cooked document's header is damaged (its checksum does not match)");
if (header.Flags != 0)
	return fail(fmt::format("The cooked document has unknown flags {:#x}", header.Flags));
if (header.HeaderSize != sizeof(Header))
	return fail(fmt::format("The cooked document's header has {} bytes, not {}", header.HeaderSize, sizeof(Header)));
if (header.Kind > static_cast<uint32_t>(SceneDocumentKind::Model))
	return fail(fmt::format("The cooked document's kind {} is unknown", header.Kind));
if (header.EntityCount > Scene::c_MaxEntities)
	return fail(fmt::format("The cooked document holds {} entities, more than a scene holds ({})", header.EntityCount, Scene::c_MaxEntities));
```

1. **Lines 580–581:** The size is checked before the reader copies a single field, so a truncated file never reads past its end.
2. **Lines 586–589:** The version and the header's checksum come before the header's other fields are trusted.
3. **Lines 594–597:** The kind and the entity count are checked against limits the engine itself has.

The section table gets the same care. Before it allocates anything, the reader checks that the table lies inside the file. Each section must be aligned, lie inside the file and overlap no other, and every count must fit in the bytes that hold it. Then the reader compares each section's CRC-32C. Only after all of that do the columns decode, one job for each component type, with a cancel check every 4,096 values, and one failed column fails the whole read.

A cooked file is read by a build that may differ from the one that wrote it. The next quote is where a column's property meets this build's own description. Look at the two bad results.

```cpp src="Strata/src/Strata/Scene/CookedScene.cpp#L461-L476"
const PropertyInfo* property = nullptr;
if (info)
{
	for (const PropertyInfo& candidate : info->Properties)
	{
		if (candidate.Name == storedProperty.Name)
		{
			property = &candidate;
			break;
		}
	}
	if (!property)
		out.Warnings.push_back(fmt::format("Component '{}': unknown property '{}' skipped", info->Name, storedProperty.Name));
	else if (property->Type != storedProperty.Type)
		return fail(fmt::format("property '{}' is a {} in the document and a {} in this build", storedProperty.Name,
			PropertyTypeToString(storedProperty.Type), PropertyTypeToString(property->Type)));
```

1. **Lines 472–473:** A property the document has and this build lacks is skipped with a warning, and the reader still reads its values so the column stays in step.
2. **Lines 474–476:** A property whose type differs fails the whole read, because the same bytes would mean something else.

The JSON form is less strict: it only warns about a value of the wrong type and loads the rest. A JSON value carries its own type, so a wrong one is one bad value. A binary column has no such markers, and decoding bytes as the wrong type would read garbage for every entity after it. A component type this build lacks is kept: its column decodes as JSON, the same warning as the text form appears once per type, and cooking the prototype again writes the data back. The unknown components kept from a text document sit in their own section as MessagePack.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Binary scene files only | Unreal Engine's packages | Smaller files, faster loads in the editor | Files nobody can compare, and no agent edits |
| One text file read as a DOM | Simple JSON formats | The least code | Several GB of memory for a million entities |
| Text with one value on each line | Unity's YAML scenes, Godot's text scenes | Diffs that show the exact value | No line split into entities, and more bytes |
| A schema :term[compiler]{id=compiler} with generated readers | Protocol Buffers | Compatibility rules made by a tool | A tool in every build, and one description in C++ |

Further reading cites the other engines' documentation.

## How it is tested

The suites live under `StrataTests/src/Scene/`. `Scene.Serialization` (`SerializationTests.cpp`) loads every committed scene without warnings, round trips scenes, and checks that invalid documents fail while unknown components and properties only warn.

`Scene.Documents` (`SceneDocumentTests.cpp`) holds the stream tests: each entity line equals the DOM's dump, the bytes do not depend on thread count or chunk size, and a parallel read equals the stream read.

`Scene.CookedScene` (`CookedSceneTests.cpp`) checks that a cooked scene equals its JSON load. Its corruption test cuts the document at every byte and flips every bit of the header and the section table. It also writes huge counts with repaired checksums and patches contents such as a null ID or a changed property type. Each copy must fail with an error. `Scene.Robustness` (`RobustnessTests.cpp`) holds the regression test for parent cycles.

Run one suite with `build/windows/bin/Debug/StrataTests.exe --test-suite=Scene.Documents`, or all of them with `ctest --preset windows-debug`.

## Changing it safely

A new kind of component needs no format work, because its registration describes it. A new document kind needs an entry in `SceneDocumentKind`, a format version and a reader rule. A sink that takes prepared entities adds `TakesPreparedEntities` and `ReadPrepared`.

Rules that apply, with reasons:

- Keep the entity line byte for byte equal to the DOM's dump, because tests compare them and the parallel reader splits by lines.
- Never let timing, thread count or chunk size reach the bytes.
- Add data that older readers can skip, with a default, and raise `c_FormatVersion` only when they cannot skip it.
- When the cooked layout changes, extend the corruption tests, and check every count before any allocation.
- Keep reads open to cancellation, warn about what is odd but understood, and fail only for what cannot be read.

Checks to pass before a change merges: `Scene.Serialization`, `Scene.Documents`, `Scene.CookedScene` and `Scene.Robustness`, and the feature test, which loads and saves a scene that holds every component.

## Summary

- A scene document is JSON: a header, a name, settings, an entity count and one entity on each line in hierarchy order with sorted keys, so a diff names the entity that changed.
- The reader links parents after every entity exists, with a union-find. A parent that is invalid, missing or part of a cycle leaves the entity at the top level with a warning, and unknown components are kept.
- Scenes, prefabs and models stream, so memory holds one entity's tree and not the document's, and the bytes do not depend on the thread count.
- The cooked form `STSC` has a 64-byte header, aligned sections with CRC-32C checksums and one column for each component type. The reader validates all of it first, skips an unknown property, fails on a changed type and keeps an unknown component.
- An entity sink receives the small fields and each entity of a stream; the builders and the reference scan differ only in what they keep.

## Check yourself

1. You move one entity in a scene file of the streamed layout. How many lines change? How many change in the older layout when you change one number of its position?

   :::answer{tests="layout"}
   One line changes in the streamed layout, the whole entity line. One line also changes in the older layout, the one that holds the number, but it does not name the entity.
   :::

2. A document lists three entities in this order: `A` has parent `C`, `B` has parent `A`, `C` has parent `B`. What does the reader do?

   :::answer{tests="read"}
   The reader links `A` below `C` and `B` below `A`. For `C`, both ends are already in one group, so it leaves `C` at the top level and warns `Entity <C>: parent <B> would create a cycle; attached at the top level`.
   :::

3. A reader loads a scene of 1,000,000 entities. What does it hold at once? (a) The DOM of the whole document. (b) The text, the DOM of one entity and what the sink keeps. (c) Nothing but one entity.

   :::answer{tests="stream"}
   Option (b). The text is in memory, the reader builds one entity's tree at a time, and the sink keeps its results. Option (a) is the DOM read that the rules forbid for whole documents, and option (c) forgets the text and the sink's results.
   :::

4. A cooked document holds a component `Bar` with a float property `Foo`. This build's `Bar` has no `Foo`. In another build `Foo` is an integer. What happens in each?

   :::answer{tests="cooked"}
   In the first build the reader skips `Foo` with a warning, and the other properties load. In the second build the whole read fails with a message that names the property and both types, because float bytes read as an integer give wrong values for every entity of the column.
   :::

5. A tool must list every asset that a million-entity scene document references. Which design holds the least memory?

   :::answer{tests="sink"}
   A sink like the reference scan of `AssetDependencies::Scan`. Its `ReadEntity` collects the handles of one entity and drops that entity's DOM, and `Finish` returns true. A `SceneBuilder` would make a million entities, and a DOM of the whole document would cost the most of all.
   :::

## Exercises

1. **Basic.** Predict, then check. Copy the sample `OpenWorld` with **File ▸ Open Sample**, and commit the copy with `git`. Save its scene `Loading` once, commit again, then move the camera to (0, 2, 0) and save. How many lines does `git diff` show?

   Run these lines in PowerShell in the Strata folder, with your copy's folder for `<copy>`; on Linux and macOS, pipe with `echo`. [Commands](../editor/commands.md) teaches them.

   ```powershell
   git -C <copy> init
   git -C <copy> add -A
   git -C <copy> commit -m "The copy"
   '{"scene": "Scenes/Loading.stscene"}' | .\StrataCLI call scene.open -
   .\StrataCLI call scene.save
   git -C <copy> commit -am "First save"
   '{"entity": "091558F6E234E59C", "component": "Transform", "values": {"Translation": [0, 2, 0]}}' | .\StrataCLI call component.set -
   .\StrataCLI call scene.save
   git -C <copy> diff --numstat
   ```

   The last line prints what changed.

   :::answer[Worked solution]{tests="layout"}
   The prediction is one line: the camera's entity line. The last line prints `1 1 Assets/Scenes/Loading.stscene`. The first save matters: it rewrote two lines of the sample's older file.
   :::

2. **Medium.** Write a sink that counts how many entities have each component type while a document streams, and makes no scene. Say what it does with a component this build does not register.

   :::answer[Worked solution]{tests="sink"}
   The sink needs only `ReadEntity` and `Finish`. It works on the DOM of one entity, so it counts names from the JSON, and a name this build lacks counts like any other. As :term[pseudocode]{id=pseudocode}, because it needs the engine:

   ```pseudocode
   class ComponentCounter : EntitySink
       Counts: map from component name to number of entities

       ReadEntity(entity, outError):
           if entity["Components"] is an object:
               for each name in entity["Components"]:
                   Counts[name] = Counts[name] + 1
           return true

       Finish(outError):
           return true

   counter = ComponentCounter()
   SceneDocumentReader::Read(text, SceneDocumentKind::Scene, counter)
   ```

   1. **Lines 4–8:** The reader calls this once for each entity, in document order, with that entity's DOM only.
   2. **Lines 10–11:** There is nothing to link at the end, so `Finish` returns true.
   3. **Line 14:** The reader owns the loop and the cancel checks, so the sink needs neither.

   Memory stays at the text plus one entity. `TakesPreparedEntities` keeps its default of false, so the reader streams.
   :::

3. **Medium.** Trace it yourself. Write the document below by hand with two entities that name each other as parents, load it as a scene, and find where its warning comes from. Predict the result first.

   ```json
   {"Strata":{"Format":"Scene","Version":1},"Scene":{"Name":"Cycle","EntityCount":2,"Entities":[
   {"Components":{"Name":{"Name":"First"}},"ID":"00000000000000A1","Parent":"00000000000000A2"},
   {"Components":{"Name":{"Name":"Second"}},"ID":"00000000000000A2","Parent":"00000000000000A1"}
   ]}}
   ```

   Each entity names the other as its parent, so one of the two links cannot hold. Save it as `Cycle.stscene` outside the project; these lines import it, open it, and read the warnings and the hierarchy.

   ```powershell
   '{"file": "C:/<folder>/Cycle.stscene", "directory": "Scenes"}' | .\StrataCLI call asset.import -
   '{"scene": "Scenes/Cycle.stscene"}' | .\StrataCLI call scene.open -
   '{"minLevel": "Warn", "newest": true, "limit": 5}' | .\StrataCLI call log.read -
   .\StrataCLI call scene.hierarchy
   ```

   Write the path with `/`, not `\`.

   :::answer[Worked solution]{tests="read"}
   Both entities load. `First` becomes a child of `Second`, and `Second` goes to the top level, with one warning in the log: `Scene 'Cycle': Entity 00000000000000A2: parent 00000000000000A1 would create a cycle; attached at the top level`.

   To trace it, search the source for `would create a cycle`: two places print it. A scene asset reads through `SceneSerializer::DeserializeText` and a `SceneBuilder`, so `LinkParents` in `Strata/src/Strata/Scene/EntitySink.cpp` runs, called from `SceneBuilder::Finish` at line 415. Its branch at lines 130 to 135 compares `childRepresentative` with `parentRepresentative`. The DOM read has the same rule in `SceneSerializer::DeserializeEntities`, at lines 528 and 556 of `Strata/src/Strata/Scene/SceneSerializer.cpp`.
   :::

4. **Hard.** Corrupt a document at random. Write a program that makes the toy cooked document of this page, changes one random byte to a different value 20,000 times, and counts how many damaged copies the checks accept. Predict the count, and explain which checks catch which damage.

   :::answer[Worked solution]{tests="cooked" solution="sketches/world-serialization-fuzz.cpp"}
   The prediction is 0. A change in the body breaks the checksum, because a CRC-32C detects every change of a burst up to 32 bits. A change in the magic, the version or the count fails its own check, and a changed checksum field no longer matches the body. Every header byte has a check, which the toy keeps on purpose: damage to a byte that no check reads goes unnoticed. The program and its output are:

   ```cpp sketch="world-serialization-fuzz.cpp"
   // Random corruption of the toy cooked document: every changed byte must be refused.
   #include <cstdint>
   #include <cstdio>
   #include <cstring>
   #include <random>
   #include <set>
   #include <string>
   #include <vector>

   namespace
   {
   	constexpr uint32_t c_Version = 1;
   	constexpr uint32_t c_NoParent = 0xFFFFFFFFu;
   	constexpr size_t c_HeaderBytes = 16;
   	constexpr size_t c_RecordBytes = 12; // A u64 ID and a u32 parent index

   	uint32_t Crc32C(const uint8_t* data, size_t size)
   	{
   		uint32_t crc = 0xFFFFFFFFu;
   		for (size_t index = 0; index < size; index++)
   		{
   			crc ^= data[index];
   			for (int bit = 0; bit < 8; bit++)
   				crc = (crc >> 1) ^ (0x82F63B78u & (0u - (crc & 1u)));
   		}
   		return ~crc;
   	}

   	struct Record
   	{
   		uint64_t Id;
   		uint32_t Parent;
   	};

   	void Put(std::vector<uint8_t>& bytes, size_t offset, const void* value, size_t size)
   	{
   		std::memcpy(bytes.data() + offset, value, size);
   	}

   	std::vector<uint8_t> Write(const std::vector<Record>& records)
   	{
   		std::vector<uint8_t> bytes(c_HeaderBytes + records.size() * c_RecordBytes);
   		for (size_t index = 0; index < records.size(); index++)
   		{
   			Put(bytes, c_HeaderBytes + index * c_RecordBytes, &records[index].Id, 8);
   			Put(bytes, c_HeaderBytes + index * c_RecordBytes + 8, &records[index].Parent, 4);
   		}
   		const uint32_t count = static_cast<uint32_t>(records.size());
   		const uint32_t crc = Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes);
   		Put(bytes, 0, "TOYC", 4);
   		Put(bytes, 4, &c_Version, 4);
   		Put(bytes, 8, &count, 4);
   		Put(bytes, 12, &crc, 4);
   		return bytes;
   	}

   	// Returns an empty string when the bytes are a valid document, else the reason they are refused.
   	std::string Check(const std::vector<uint8_t>& bytes)
   	{
   		if (bytes.size() < c_HeaderBytes)
   			return "shorter than its header";
   		uint32_t version = 0, count = 0, crc = 0;
   		std::memcpy(&version, bytes.data() + 4, 4);
   		std::memcpy(&count, bytes.data() + 8, 4);
   		std::memcpy(&crc, bytes.data() + 12, 4);
   		if (std::memcmp(bytes.data(), "TOYC", 4) != 0)
   			return "wrong magic";
   		if (version != c_Version)
   			return "unsupported version";
   		if ((bytes.size() - c_HeaderBytes) / c_RecordBytes != count || (bytes.size() - c_HeaderBytes) % c_RecordBytes != 0)
   			return "count does not match the size";
   		if (Crc32C(bytes.data() + c_HeaderBytes, bytes.size() - c_HeaderBytes) != crc)
   			return "checksum does not match";
   		std::set<uint64_t> seen;
   		for (uint32_t index = 0; index < count; index++)
   		{
   			Record record {};
   			std::memcpy(&record.Id, bytes.data() + c_HeaderBytes + index * c_RecordBytes, 8);
   			std::memcpy(&record.Parent, bytes.data() + c_HeaderBytes + index * c_RecordBytes + 8, 4);
   			if (record.Id == 0 || !seen.insert(record.Id).second)
   				return "null or repeated ID";
   			if (record.Parent != c_NoParent && record.Parent >= index)
   				return "parent does not come before its entity";
   		}
   		return {};
   	}
   }

   int main()
   {
   	std::vector<Record> records;
   	for (uint32_t index = 0; index < 40; index++)
   		records.push_back({ 100 + index, index == 0 ? c_NoParent : index / 2 });
   	const std::vector<uint8_t> good = Write(records);
   	std::printf("the valid document: %s\n", Check(good).empty() ? "accepted" : "refused");

   	std::mt19937 random(1);
   	const int trials = 20000;
   	int accepted = 0;
   	for (int trial = 0; trial < trials; trial++)
   	{
   		std::vector<uint8_t> damaged = good;
   		damaged[random() % damaged.size()] ^= static_cast<uint8_t>(1 + random() % 255); // Never zero: a byte always changes
   		if (Check(damaged).empty())
   			accepted++;
   	}
   	std::printf("%d corruptions, %d accepted\n", trials, accepted);
   	return 0;
   }
   ```

   ```text output-of="world-serialization-fuzz.cpp"
   the valid document: accepted
   20000 corruptions, 0 accepted
   ```

   1. **Line 98:** The number of random corruptions.
   2. **Lines 102–105:** Each trial changes one byte to a different value and counts the copy only if `Check` accepts it.

   The engine's test does the same for the real reader. It flips each bit of the header and the table, and it repairs the checksums after changing contents so that the checks behind them run.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Scene/SceneSerializer.h` and `SceneSerializer.cpp`: `SceneSerializer`, the DOM form, settings, snapshots, `RemapEntityReferences`.
- `Strata/src/Strata/Scene/SceneDocumentWriter.h` and `SceneDocumentWriter.cpp`: `SceneDocumentWriter`, `SceneWriteOptions`.
- `Strata/src/Strata/Scene/SceneDocumentReader.h` and `SceneDocumentReader.cpp`: `SceneDocumentReader`, `SceneReadOptions`.
- `Strata/src/Strata/Scene/EntitySink.h` and `EntitySink.cpp`: `EntitySink`, `SceneBuilder`, `EntityPrototypeBuilder`, `EntityColumns`.
- `Strata/src/Strata/Scene/UnknownComponents.h` and `SceneReadProgress.h`: `UnknownComponentsComponent`, `SceneReadProgress`.
- `Strata/src/Strata/Scene/CookedScene.h` and `CookedScene.cpp`: `CookedSceneWriter`, `CookedSceneReader`.
- `Strata/src/Strata/Reflection/PropertyBinary.h`: `WritePropertyValue`, `ReadPropertyValue`.
- Tests: `StrataTests/src/Scene/SerializationTests.cpp`, `SceneDocumentTests.cpp`, `CookedSceneTests.cpp` and `RobustnessTests.cpp`.

## Further reading

- The JSON standard, ECMA-404 (beginner): the whole grammar of the text form in a few pages.
- The documentation of the `nlohmann/json` library on GitHub, its SAX interface (intermediate): the event parser that the reader builds on.
- Unity Technologies, the manual page on its YAML scene format (intermediate): another engine's text scenes, for comparison.
- Godot Engine, the documentation of the `.tscn` file format (intermediate): another engine's text scene format.
- Google, the documentation of Protocol Buffers and FlatBuffers (intermediate): schema-driven binary formats.
- The MessagePack specification (intermediate): the byte layout of the encoding that the cooked form uses for extra data.
