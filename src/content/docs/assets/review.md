---
id: assets/review
title: "Review: assets"
description: "The questions of every page of the part on assets, and exercises that use several of its pages together."
tracks: [E]
status: final
generated: review
---

## Cumulative exercises

These exercises need more than one page of the part. Try each before you open its worked solution.

1. **Basic.** A color picture `Brick.png` of 100 by 60 texels, opaque, is imported with the defaults and stored as `BC7SRGB` with a full chain. The name takes 9 bytes. Compute the size of every level, the size of the chain, the offset of level 0 in the stored file and the size of the same chain in `RGBA8`.

   :::answer[Worked solution]
   Halve each side and round down, with a floor of 1. The sides are 100 by 60, 50 by 30, 25 by 15, 12 by 7, 6 by 3, 3 by 1 and 1 by 1: seven levels.

   A `BC7` level rounds each side up to whole blocks of 4 and takes 16 bytes a block. The block counts are 25 by 15, 13 by 8, 7 by 4, 3 by 2, 2 by 1, 1 by 1 and 1 by 1. The sizes are 6,000, 1,664, 448, 96, 32, 16 and 16 bytes, and the chain takes 8,272 bytes.

   The data starts after the header (40 bytes), the table (7 × 24 = 168 bytes) and the name (9 bytes): 217 bytes, which rounds up to 224. The smallest level comes first, so level 6 lies at 224, level 5 at 240, level 4 at 256, level 3 at 288, level 2 at 384 and level 1 at 832. Level 0 lies at 832 + 1,664 = 2,496 and the file ends at 8,496.

   In `RGBA8` every texel takes 4 bytes: 24,000, 6,000, 1,500, 336, 72, 12 and 4 bytes, which is 31,924 bytes. The block form is about a quarter of that. The chain is 38 % larger than level 0 and not 33 %, because the small levels round up to a whole block.
   :::

2. **Basic.** `Hero.glb` has two meshes, one material and one image that serves as base color and as metallic-roughness. A teammate copies it in a file manager together with its `.meta` file, as `Hero - Copy.glb`. Which file keeps the handle, how many assets does the copy add, and does any of them share a handle with an asset of the original?

   :::answer[Worked solution]
   Two files now claim one handle. The scan keeps the handle for the file that an import record names, and with no record for the file with the shortest path: `Hero.glb`. The copy gets a new random handle, the scan logs a warning, and it writes the new `.meta` file.

   The importer makes a model and its sub-assets: `Mesh/0`, `Mesh/1`, `Material/0`, `Texture/0/Color/00` and `Texture/0/Data/00`, because one image used in two ways gives two textures. The copy adds the model and these five sub-assets: six assets.

   A sub-asset has no `.meta` file. Its handle comes from hashing its key and mixing in its parent's handle. The keys are the same as the original's, but the parent's handle is not, so no handle of the copy equals one of the original. Scenes that use the original continue to work, and the original's sub-assets keep their handles.
   :::

3. **Medium.** The streaming queue holds five waiting requests.

   The requests are Sky (`High`, score 0, 60 MiB), Grass (`Normal`, score 7, 30 MiB), Rock (`Normal`, score 2, 30 MiB), Door (`Normal`, score 2, 4 MiB) and Tree (`Low`, score 0, 10 MiB). They arrived in the order Rock, Sky, Door, Grass, Tree. Nothing is in flight and the limit is 128 MiB. There are 2 I/O threads. Which loads does one `Pump` dispatch, and which limit stops it?

   Then Sky arrives as a texture with 60 MiB to upload, at 5 MiB per millisecond and with the default budgets. In how many frames does the upload end?

   :::answer[Worked solution]
   The queue sorts by level, then by score (a higher score first), then by request order. The order is Sky, Grass, Rock, Door, Tree.

   The first load always starts: Sky, 60 MiB in flight, 1 read. The queue dispatches while the bytes in flight are below 128 MiB and the reads are below 4 (2 per I/O thread). Grass makes 90 MiB and 2 reads, Rock 120 MiB and 3 reads, and Door 124 MiB and 4 reads.

   Then the reads reach 4, so the queue stops, although 124 is below 128. Four loads go, and Tree waits. The reads stop it, not the bytes.

   For the upload, the first call of a frame has 2 ms, less a tenth kept in reserve. Step one takes 4 MiB and 0.8 ms, step two sees 1.0 ms and takes 4 MiB again, and step three sees 0.2 ms and takes 1 MiB. A frame uploads 9 MiB.

   Six frames upload 54 MiB, and the seventh needs 6 MiB, which two steps give. The upload ends in 7 frames.
   :::

4. **Medium.** An entry of an asset pack is 700,000 bytes, so the pack holds it in blocks of 262,144 bytes. How many blocks, and how large is the last? Block 0 would compress to 240,000 bytes and block 1 to 200,000: which of these two are stored as they are?

   A read of 1,000 bytes starts at offset 262,000. Which blocks does it decode? A byte of block 2 is damaged: does that read fail, and when does Strata find the damage?

   :::answer[Worked solution]
   700,000 / 262,144 is 2.67, so the entry has 3 blocks: two full ones of 262,144 bytes and a last one of 700,000 − 524,288 = 175,712 bytes. The blocks must cover the entry exactly, or `Open` refuses the pack.

   A block is compressed only when that saves an eighth, which is 262,144 / 8 = 32,768 bytes. Block 0 saves 22,144, so it is stored as it is. Block 1 saves 62,144, so it is compressed.

   The read covers offsets 262,000 to 262,999. Offset 262,000 lies in block 0, which ends at 262,143, and the rest lies in block 1. The read covers the end of block 0 and the start of block 1. Block 0 is stored, so the reader checks its checksum and copies the covered bytes straight from it. Block 1 is compressed, so the reader checks it, decodes it into a block of its own and copies only the covered bytes.

   The damaged byte lies in block 2, which this read never touches, so the read succeeds. The checksum of a block is checked when a read decodes it, before anything else: a read that covers block 2 fails with an error. A damaged byte in the tables is different, because `Open` checks their checksum and refuses the whole pack at once.
   :::

5. **Medium.** A group load of a scene pins its `Load` closure, which includes the texture `Planks` of 600,000 bytes in the texture pool. The pool's budget is 500,000 bytes. It also holds the stale textures `Moss` and `Fern` of 100,000 bytes each, outside the grace window, and every texture here loads whole. What does the manager drop, how much memory does the pool use afterwards, and what changes when the group is released?

   :::answer[Worked solution]
   The pool holds 800,000 bytes, which is 300,000 above the budget. The manager walks the recency order from the least recently requested asset and skips protected ones. `Planks` is pinned by the group, so it stays. It drops `Moss`, which leaves 700,000 bytes, and `Fern`, which leaves 600,000.

   The pool now uses 600,000 bytes, still above its budget, because nothing left is allowed to go. A pin keeps an asset until it is released, so a pin defeats the budget by the size of what it holds. A script that pins everything leaves no budget at all.

   When the group ends, `Planks` is no longer pinned. If nothing has requested it within the grace window, the next walk over the budgets drops it, and the pool comes to 0 bytes. A held `Ref` in a component would have kept it as well, and would have done so without anyone intending it.
   :::

6. **Hard.** A project has the scenes `Town` (the start scene), `Cave` and `Menu`. `Town` uses the prefab `Cart` and the scene `Cave`. `Cart` uses the mesh `Wheel` and the material `Wood`, `Wheel` uses `Wood`, and `Wood` uses the texture `Planks`.

   `Cave` uses the mesh `Rock` and `Planks`. `Menu` uses `Logo`, and nothing uses `Spare`.

   Every list is recorded in the order written here. The export prunes, with an empty `AlwaysInclude`. Give the order of the pack's entries and the omitted assets.

   Then give the `Load` closure of `Town` and its progress when `Planks` (600,000 bytes) and `Wheel` (100,000 bytes) have finished. The other members are `Town` (20,000), `Cart` (10,000) and `Wood` (10,000).

   :::answer[Worked solution]
   The pack plan starts with the start scene's closure in the `All` scope, breadth first. `Town` comes first. Its references give `Cart` and `Cave`. `Cart` adds `Wheel` and `Wood`, and `Cave` adds `Rock` and `Planks`. `Wheel` names `Wood` again and `Wood` names `Planks`, but both are already in.

   The order so far is `Town`, `Cart`, `Cave`, `Wheel`, `Wood`, `Rock`, `Planks`.

   Every other scene follows with its closure: `Menu` and `Logo`. With pruning, `Spare` is omitted, because no scene reaches it and `AlwaysInclude` is empty. The pack holds 9 entries. A script that loaded `Spare` by a path would not find it.

   The `Load` scope stops at other scenes. From `Town` it takes `Cart`, skips `Cave`, then takes `Wheel` and `Wood`, and last `Planks`. `Rock` is never reached. The closure is `Town`, `Cart`, `Wheel`, `Wood`, `Planks`, with 740,000 bytes stored.

   Progress counts stored bytes: `Planks` and `Wheel` are 700,000 of 740,000, so the progress is 94.6 %. Counting assets would say 40 %, and the bar would jump at the end.
   :::

7. **Hard.** A developer changes how the glTF importer clamps a value. The output of the importer differs, but the developer does not raise its version. After the change the developer's own project, whose cache was cleared, shows the new result. A teammate's project still shows the old one.

   Diagnose it, state the fix and say what happens to scenes after the fix. Then say what would happen to scenes if the same change had also renamed the key `Mesh/0` to `Mesh/00`.

   :::answer[Worked solution]
   A cached import is current when every key of its record matches. The record holds the format version, the importer version, the settings hash, the success flag, the source's size, time and hash, and the dependencies. The change altered none of these: the source file is the same, and so are the settings and the version. The teammate's record therefore says current, and the cache serves the old output. The developer's cache was cleared, so it was made again by the new code.

   The fix is to raise `GetVersion()` of the importer. At the next scan the version in each record differs from the importer's, so every model is imported again in the background. The old object stays in use until the new one is ready. The keys are the same, so the sub-assets keep their handles, and scenes keep their references.

   A handle comes from hashing the key and mixing in the parent's handle. The key `Mesh/00` hashes to another number, so the first mesh of every model gets a new handle. Scenes that held the old handles name assets that no longer exist, and the meshes disappear. The rule is that keys never change.
   :::

8. **Hard.** A team adds a `Dialogue` asset type. A dialogue file is text that names sound clips by handle. The file `Intro` has the handle `0x3000` and names, in order, the clips `0x2000`, `0x2400`, `0x2000`, `0` and `0x3000`.

   A colleague wants to insert the type in the middle of the enum, and the importer to record no references, since the loader checks the text. Say what each shortcut costs, and what the importer records for `Intro`.

   :::answer[Worked solution]
   Packs and import records store the numbers of the type enum. A type inserted in the middle moves the numbers of every later type, so a pack or record made before the change reads the wrong type for those assets. The type is appended at the end, with entries in both name functions, which packs and the feature test use.

   Recording references is the importer's duty. The manager normalizes the list: it keeps a handle only if it is valid, not the asset itself and not seen before. For `Intro`, `0` is not valid, `0x3000` is `Intro` itself and the second `0x2000` was seen. The record holds `0x2000` and `0x2400`.

   Without a record, a scene that uses `Intro` has a closure without the clips. A pruned export omits them, so the game plays no sound, and deleting a clip in the editor gives no warning. The loader's check of the text cannot repair this, because it reads only the bytes it is given, and a closure is built from the table of references. The importer also checks the text, because the file may be bad before it is ever loaded.
   :::
