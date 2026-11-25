---
id: appendix/credits
title: "Credits and licenses"
description: "What the book shows or quotes that others made, where it comes from, and the terms of the book itself."
kind: reference
size: S
tracks: []
needs: []
status: final
---

This page lists what the book shows or quotes that other people made. These are the libraries the engine uses, its fonts, code derived from another project and the sample assets that pictures show. The engine itself is listed too.

A row names the work, its author or version, its license and where it came from. A license is the permission its author gives; the page gives its name, never its text. The full texts stand in the site's file `third-party-notices.txt`. The license of the book is in `license.txt`.

The tables are written by hand from `ThirdPartyNotices.md` and the `CREDITS.md` files of the samples. The engine's repository is their only source.

## The engine

Every excerpt and every picture of the book comes from the Strata engine of its owner, the account 2042Third, at one fixed version. The repository holds no license file at its root. This page therefore says nothing about the engine's own terms beyond what its repository says: it names its owner and lists the work of others that the engine includes. An excerpt of the engine stays the engine's.

## Libraries

Strata includes these libraries as pinned copies under `Strata/vendor/`, and exported games ship `ThirdPartyNotices.md` beside the program. The column "In games" says whether a game that you export contains the library. A page of this book may quote a library's source only when the library stands in this table: the pages quote `box3d` and `EnTT` so far. How the engine pins and upgrades its libraries is the subject of [Third-party code](../engineering/third-party.md).

| Library | Version | License | In games | Purpose |
| --- | --- | --- | --- | --- |
| `GLFW` | 3.4 | `zlib/libpng` | Yes | Windowing and input |
| `NVRHI` | 6b96fb0 | `MIT` | Yes | Rendering hardware interface |
| `Vulkan-Headers` | 1.4.352 | `Apache-2.0 OR MIT` | Yes | Vulkan headers |
| `glm` | 1.0.3 | `MIT` | Yes | Math |
| `EnTT` | 3.16.0 | `MIT` | Yes | Entity-component system |
| `box3d` | efca0c1 | `MIT` | Yes | Physics |
| `miniaudio` | 0.11.25 | `Public domain (Unlicense) or MIT-0` | Yes | Audio |
| `spdlog`, with `fmt` | 1.17.0 | `MIT` | Yes | Logging |
| `nlohmann/json` | 3.12.0 | `MIT` | Yes | JSON files |
| Dear ImGui (docking) | 1.92.9 | `MIT` | Yes | Immediate-mode interface |
| `ImGuizmo` | 18cef5e | `MIT` | Editor only | Transform gizmos |
| `stb` | 2c980bb | `MIT or public domain` | Yes | Images, mip filtering, block compression, font rasterization |
| `cgltf` | 1.15 | `MIT` | Editor only | glTF import |
| `meshoptimizer` | 1.3 | `MIT` | Editor only | Mesh optimization and levels of detail |
| `MikkTSpace` | 3e895b4 | `zlib` | Editor only | Tangent generation |
| `Slang` | 2026.20 | `Apache-2.0 WITH LLVM-exception` | No, a build tool | Shader compiler |
| `nativefiledialog-extended` | 1.4.1 | `zlib` | Editor only | Native file dialogs |
| `doctest` | 2.5.3 | `MIT` | No, tests | Unit testing |
| `Tracy` | 0.14.1 | `BSD-3-Clause` | Optional | Profiler hooks |
| `Zstandard` | 1.5.7 | `BSD-3-Clause`, used under that license | Yes, to unpack; packing in the editor only | Asset pack compression |

Slang is no pinned copy: the build fetches a release archive once. The stb row lists both of its licenses, and a user may pick either.

## Fonts

The editor embeds three fonts, committed as release files with their license texts in `StrataEditor/Resources/Fonts/`. The pictures of the editor show them. Games do not ship them.

| Font | Version | License | Used for |
| --- | --- | --- | --- |
| `Inter`, by its project authors | 4.1 | `SIL OFL 1.1` | Interface text and headers |
| `JetBrains Mono`, by its project authors | 2.304 | `SIL OFL 1.1` | Logs, identifiers and numbers |
| `Lucide`, by its contributors | 1.47.0 | `ISC`; the icons derived from Feather also `MIT` | Icons |

The default font of text in every game is Roboto Medium by its designer, under the license `Apache-2.0`. The engine compiles it in from the copy that Dear ImGui distributes, and it ships in every game.

## Code derived from other projects

Strata adapted parts of two projects that are not pinned copies. Each keeps its notice in `ThirdPartyNotices.md`, with its full license text.

The project radiance-cascades-lab (`MIT` license, copyright 2026 by its author) gave parts of the shaders of global illumination, the engine's indirect light. The files are `Strata/shaders/Include/Voxelize.slang`, `GIMarch.slang`, `GIProbes.slang` and `GIField.slang` in the same folder, and eight of the shaders of `Strata/shaders/GI/`: `VoxelTriangles.comp.slang`, `VoxelFill.comp.slang`, `VoxelFinalize.comp.slang`, `VoxelInject.comp.slang`, `CascadeMarch.comp.slang`, `ProbeWeights.comp.slang`, `FieldReduce.comp.slang` and `VoxelMovers.comp.slang`. The other shaders of that folder are Strata's own.

The project `ltc_code`, at the commit `31e5e96b`, gave the shading of rect lights. Its authors are `Eric Heitz`, `Jonathan Dupuy`, `Stephen Hill` and `David Neubelt`, with copyright 2017. Strata took its fitted tables value for value and ported its shading of a rectangle to C++ and Slang. The files are `Strata/src/Strata/Renderer/LTCTable.inl`, `Strata/src/Strata/Renderer/AreaLights.h`, `Strata/src/Strata/Renderer/AreaLights.cpp` and `Strata/shaders/Include/AreaLights.slang`. Its license is `BSD 2-Clause` with a third condition: work that uses or adapts the code names the paper of the four authors from 2016, `Real-Time Polygonal-Light Shading with Linearly Transformed Cosines`.

Whoever copies an excerpt of those files takes the notice of its project with it: the license text in `ThirdPartyNotices.md`, and for `ltc_code` the reference to the paper.

## Sample assets

The samples that pictures show use the packs below; each sample's `CREDITS.md` lists every file. `CC0` means **Creative Commons Zero**: the author gave the work to the public domain, and no credit is required. One exception follows the table. The Tetris sample holds only files that Strata made.

| Sample | Pack | Author | License |
| --- | --- | --- | --- |
| Physics Playground | ambientCG: Tiles101, Bricks076C, Planks037B, Concrete034, Plastic010, Metal032 | ambientCG | `CC0 1.0` |
| Physics Playground | Kenney: Impact Sounds, Interface Sounds, `UI Pack`, `Fonts` | Kenney | `CC0 1.0` |
| Open World | Kenney: Nature Kit, `Fonts` | Kenney | `CC0 1.0` |
| Open World | `Khronos glTF Sample Assets`: Fox | see the next section | `CC0 1.0` and `CC BY 4.0` |
| Third-Person Adventure | `three.js` example models: `RobotExpressive` | `Tomás Laulhé` (`Quaternius`); changes by `Don McCurdy` | `CC0 1.0` |
| Third-Person Adventure | Kenney: Platformer Kit, Impact Sounds, Interface Sounds, `UI Pack`, `Fonts` | Kenney | `CC0 1.0` |
| Third-Person Adventure | Poly Haven: `Kloofendal 48d Partly Cloudy (Pure Sky)` | `Greg Zaal`; sky edits by `Jarod Guest` | `CC0 1.0` |
| High Desert Outpost | Poly Haven: 22 scans of materials and props | Poly Haven artists, named in the sample's `CREDITS.md` | `CC0 1.0` |

### The fox

The fox of the Open World sample is the Fox model of the `Khronos glTF Sample Assets`, at the [commit `edc7c9e`](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/edc7c9e67c639d230715049ee31f9a96a6babbbe/Models/Fox). Its parts have three authors and two licenses:

- The model: © `PixelMannen`, `CC0 1.0`.
- Rigging and animation: © 2014, `tomkranis`. `CC BY 4.0`.
- Conversion to glTF: © 2017, `@AsoboStudio` and `@scurest`. `CC BY 4.0`.

The two copyright lines come from the "Legal" section of the model's notes at that commit. The engine's own credit in `ThirdPartyNotices.md` gives the same authors, licenses and copyright lines. `CC BY 4.0` is the license **Creative Commons Attribution**: you may use the work if you name its authors and the license. Every picture of the book that shows the fox therefore carries this credit in its caption or beside it. The figures that show it are the foxes seen from far away in [Culling animation](../animation/culling.md) and the fox prefab in the pages of the editor's prefab instances.

## The book's own files

The files of `tutorials/assets/` are patches that the book's author wrote for its exercises. They fall under the permission for the book's code, below. The book keeps no pictures from other books or engines.

## The book's terms

The book carries the statement "Copyright © 2026 2042Third. All rights reserved." Except where otherwise noted, that holds for the whole book. It has two exceptions: the code of the book, and third-party material, which keeps its own terms.

You may put the code and project files that the book gives into your own programs and games, and ship them, also commercially, without asking and without naming the book. These files are the listings written for the book, the tutorial files, the command scripts, the lab files, the worked solutions and the checkpoint projects. You may not publish them as a collection of examples, a course or a book. The text, the pictures, the diagrams and the site are for reading and for printing for your own use. Third-party files keep their own terms, as the tables above show.

## Where it lives in Strata

- `ThirdPartyNotices.md`: the libraries, fonts, derived code and sample packs, and the license texts of the derived code.
- `StrataEditor/Resources/Fonts/`: the editor's fonts with `Inter-OFL.txt`, `JetBrainsMono-OFL.txt` and `Lucide-LICENSE.txt`.
- `Samples/OpenWorld/CREDITS.md`: the fox's row and the credits of the other files of that sample.
- `Samples/PhysicsPlayground/CREDITS.md`, `Samples/ThirdPerson/CREDITS.md`, `Samples/Showcase/CREDITS.md`, `Samples/Tetris/CREDITS.md`: the other samples' credits.
