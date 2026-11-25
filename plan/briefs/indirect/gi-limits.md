# Brief: `indirect/gi-limits`

| Field | Value |
| --- | --- |
| Title | Global illumination III: moving objects, limits and what comes next |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `indirect/gi-cascades` |
| From | new; what Strata's GI does not do (local lights, moving and skinned objects: render-indirect 1.8) and how other engines do it; home of "a feature that is off is invisible bit for bit" for GI · W8 |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/gi-limits` — Global illumination III: moving objects, limits and what comes next

**Covers.** A concept page. It opens with three honest pictures: the row of small dark notches under the Cornell box's
sphere, a wall thinner than two voxels that the voxels view shows two-sided, and the edge of the field around the
camera outdoors in the yard. The naive answer, "GI is free bounce light everywhere", breaks on each of them. The idea:
what a voxel copy of the static world and a probe field around the camera can hold, and what they cannot. Only static
geometry enters (movers wait 30 frames, skinned meshes never enter); only the sun and glowing surfaces light the voxels;
the field changes diffuse light only, and specular stays today's; it resolves no more than its probes (0.5 m apart at
High, 1 m at Low); it reaches only a box around the camera (High full within 7.5 m across and 5.5 m up and down, Low
within 7 m and 2.8 m, faded to today's light over 2 m more); an ambient cube is exact only for normals along the axes;
textures count by their means. The limits of the guide's "What it cannot do" follow, each with its cause in one
sentence: a surface that sees none of its eight probes gets no field light, so it is dark, never the sky, and darker
than without GI, outdoors too (gaps, ledges, wall feet); thin props become blobs of whole voxels; a model colored from
one palette texture takes the palette's mean everywhere; double-sided materials' voxels have no facing; glowing values
above 65,408 nits clamp; an editor top view far above a scene shows only the coarse levels; submeshes past a mesh's
256th are left out (logged once); Low bounces once; and the field does not reach baked probe captures (a bake renders
at Medium's row, where GI is Off: `indirect/probes`).

The approaches engines use for what Strata lacks, each with its cost: moving objects in a dynamic occupancy or traced by
rays (DDGI, Lumen); local lights injected into the voxels; skinned meshes voxelized as they pose; specular GI; hardware
ray queries. Strata's choice and its reason: GI is experimental, deterministic and free of history, and global
illumination that is off is invisible bit for bit, while what it still costs is measured and stated. This page is that
decision's home for GI, in a `:::why` aside: when the scene does not ask, when the row is Off, and while the field is
pending, the frame keeps the indirect light's old expression bit for bit (the join's `x * 1 + 0`, the dummy views); off,
GI still spends 0.010 to 0.014 ms more in `GPU.Opaque` (Medium with TAA at 3840 x 2160, measured at the tag), because
the forward shader's gather is compiled in although it does not run; and one exception runs GI where nothing asks for
it: a GI debug view, which at Off shows High's layout. What Strata does not do: GI from local lights, from moving
objects and from skinned objects; specular light from GI (the field changes only the diffuse indirect light); and the
rest of the spec's list "below the cut" (the open share in specular occlusion, an Ultra layout, textured albedo per
voxel, hardware ray queries), with nested probe-field levels and denser probes near surfaces, each quoted from the
documents and never dated (probe relocation, the spec's item 7, is at the pin and taught on `indirect/gi-cascades`); it
links `appendix/not-in-strata`. The exercises predict which limit decides three scenes and break, in a patch, the rule
that movers wait 30 frames. Common mistakes: walls thinner than two voxels, a moving door expected to change the bounce
at once, judging GI before it has settled, and reading the GI stage's time as stable when the release notes record it
varying between runs. The reader can say before trying it whether GI will help a scene.

**Leaves out.**

- How the voxels are made → `indirect/gi-voxels`
- How the field is traced, sampled and joined → `indirect/gi-cascades`
- "A feature that is off is invisible bit for bit" as a rule of the whole renderer → `gpu/frame-tour`
- Trying GI in a game and avoiding its pitfalls → `make/gi`
- Local lights and their records → `light/lights`
- The general techniques of dynamic GI that Strata lacks → `appendix/not-in-strata`

**Fit.** `fits`: about 3,650 words against M (3,000). The three honest pictures, what the voxels and the field can hold,
the guide's limits one by one and the approaches engines use for what Strata lacks take the most words. Phase B must
look again at: every absence at the new pin (`v0.8.0`, then `v0.8.1`), since the spec's list may shrink; the guide's
paragraph "What it cannot do" (`Docs/DeveloperGuide.md:5259-5296` at the pin) and the numbers it gives, with the limits
of `new:31`; the 0.8.0 release notes' "Known issues"; the cost of GI when off, measured again at the tag; the entry of
book.md's table "Checked when the W8 page is written" that names this page (`new:15`: GI from local lights and from
moving or skinned objects, specular light from GI, the open share in specular occlusion, an Ultra level, textured albedo
per voxel, hardware ray queries, nested probe-field levels, denser probes near surfaces); the page's movable claims.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:153` | feature | home | What the pin has (stages 1 to 4, the batches "smooth light between probes" and "light at contacts") and what it has not (the spec's list below the cut, nested field levels, denser probes near surfaces, the octahedral and SH fields tried and not landed) |
| `render-indirect:112` | feature | home | The open share in specular occlusion, planned and not landed (spec D18.4) |
| `render-indirect:510` | rule | home | A frame without GI (not asked, the row Off, pending) keeps the old expression bit for bit, the join in `x * 1 + 0` form; what GI still costs when off is measured and stated (0.010 to 0.014 ms more in `GPU.Opaque`, the gather compiled in: `Docs/Plans/Wave8/ReleaseNotes.md:383-386`); a GI debug view runs GI where nothing asks for it, at Off with High's layout (`Strata/src/Strata/Renderer/SceneRenderer.cpp:3069-3074`): the design decision's home for GI, in a `:::why` aside (`AGENTS.md:405-406`; book.md's design decisions) |
| `render-indirect:515` | rule | home | Movers stay out of the voxels for 30 frames and skinned meshes never enter: no voxel work per frame for moving things, no popping of light |
| `render-indirect:459` | figure | home | The artefacts: dark notches under the Cornell sphere (`lookdev.cornell`, whose scene asks for GI), a thin wall two-sided in the voxels view (no shot at the pin is named for it: a recipe), the field's edge in the yard (`lookdev.yard.lit.gi`) (`Tools/LookDev/Shots.json:148`, `:150`; `Tools/LookDev/LookDevScene.json:259`) |
| `render-indirect:704` | open | home | The GI stage's time varies between runs of one build (4.4 against 6.5 ms) for a cause the release notes leave open; stated as a known issue, quoted |
| `new:15` | not-done | home | No global illumination from local lights, from moving objects or from skinned objects; no specular light from global illumination (the field changes only the diffuse indirect light); no open share in specular occlusion, no Ultra level, no textured albedo per voxel, no hardware ray queries for global illumination, no nested probe-field levels and no denser probes near surfaces (book.md's row in "Checked when the W8 page is written"; probe relocation, the spec's item 7, is at the pin). Evidence: `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` (D18 "Below the cut", items 1 to 6 and 8; item 7 is at the pin: `Docs/DeveloperGuide.md:5090`); `Docs/DeveloperGuide.md:4960-4961` (nested probe-field levels and local lights follow), `:5164` (specular is untouched), `:5271` (denser probes near surfaces are the next step); movers excluded for 30 frames (`Strata/src/Strata/Renderer/SceneRenderData.h:686`) |
| `new:31` | feature | home | The limits of the guide's "What it cannot do", each with its cause in one sentence: a surface that sees none of its eight probes gets no field light (dark, never the sky, darker than without GI, outdoors too: gaps, ledges, wall feet); thin props become blobs of whole voxels; a palette texture gives the whole model one mean color; double-sided materials' voxels have no facing; glowing values above 65,408 nits clamp; an editor top view far above a scene shows only the coarse levels; submeshes past a mesh's 256th are left out (logged once); Low bounces once; a baked probe capture holds no GI (the bake renders at Medium's row). Evidence: `Docs/DeveloperGuide.md:5272-5277`, `:5287-5289`, `:4968`; `Docs/Manual/Lighting.md:346-352`; `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp:605-611`; `Strata/src/Strata/Renderer/SceneRenderData.h:799`; `StrataTests/src/Renderer/GlobalIlluminationLayoutTests.cpp:525` |
| `new:32` | hands-on | home | The page's exercises (R32, D27): **Basic.** predict which limit of the page decides each of three scenes (a cave lit only by torches, a sunlit hall whose door swings, a grove of thin poles); **Medium.** modify: a patch against the pin that lets a moved mesh back into the voxels in the frame after it stops (`c_GIMovingFrames` 1); predict whether the CPU test "A moved proxy queues its old and new bounds", which counts its frames by the constant, still passes and what a door that swings back and forth would then cost the voxelizer, and run it. Evidence: `StrataTests/src/Renderer/VoxelClipmapTests.cpp:303-352` (suite `Renderer.VoxelClipmap`, `:253`); `Strata/src/Strata/Renderer/SceneRenderData.h:686`; `Strata/src/Strata/Renderer/VoxelClipmap.cpp:398-458`; `Docs/Plans/Wave8/specs/radiance-cascades-world.md:896-917` |
| `render-indirect:517` | rule | use | Walls thinner than two voxels go two-sided; taught on `indirect/gi-voxels` |
| `render-indirect:166` | feature | use | What enters the voxels, as the source of the limits on movers and textures |
| `render-indirect:178` | feature | use | The join, specular untouched |
| `render-indirect:367` | code | use | The join's `x * 1 + 0` form, shown in one line |
| `render-indirect:519` | rule | use | Waiting for GI to settle, as a common mistake's fix |
| `render-indirect:329` | concept | link | The renderer's rule that an off feature changes no bit, on `gpu/frame-tour` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The GI pipeline from the voxels to the join | `indirect/gi-cascades` | must |
| The voxel classes and two-sided walls | `indirect/gi-voxels` | must |
| The renderer's rule that an off feature changes no bit | `gpu/frame-tour` | must |
| Point and spot lights and their records | `light/lights` | helps |
| Skinned meshes in the renderer | `draw/skinned` | helps |
| Temporal accumulation, as other engines' GI uses it | `image/taa` | helps |
| What a probe bake renders with (`ForBake`, Medium's row) | `indirect/probes` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
