---
id: reference/notation
title: "Conventions and notation"
description: "The coordinate, unit and color conventions Strata follows, each with its evidence in the engine and the page that teaches it."
kind: reference
size: M
tracks: []
needs: []
status: final
---

Two programs that both draw a cube can disagree about which way is up, which way a triangle faces, or whether a number means metres or centimetres. Each disagreement is a bug that no compiler reports. This page lists the choices Strata makes, so that you can check a number, a shader or a command against them. It defines nothing: every row names the page that teaches the idea.

Each table has the same shape. A row is one convention. The columns say what Strata does, where the engine shows it, and which page of this book explains the idea. When a page of the book uses a different convention, for example a matrix drawn with rows in a diagram, that page says so in its own text and links back here.

## Space and geometry

The first table covers where things are and which way they point. Read the **Strata does** column as a rule for every number you write: a position, a direction, an angle, a depth stored in a texture.

| Convention | Strata does | Evidence | Taught in |
| --- | --- | --- | --- |
| Handedness and axes | Right-handed coordinates, +Y up, -Z forward, which the engine calls the glTF convention. The forward direction of a rotation is that rotation applied to the vector (0, 0, -1). | `Strata/src/Strata/Math/Math.h` | [Coordinate systems](../gpu/coordinates.md) |
| Imported models | A glTF model faces +Z, the opposite of the forward direction, so a model that must look forward is turned 180 degrees about Y, or a script computes its facing for +Z. | `.claude/skills/strata-make-a-game/SKILL.md` | [Positions, rotations and units](../make/transforms-units.md) |
| Clip space | Direct3D style, reached through NVRHI on every backend: the framebuffer origin is at the top left, +Y is up in normalized device coordinates (NDC), and depth runs from 0 to 1. | `Strata/shaders/Include/Common.slang` | [Coordinate systems](../gpu/coordinates.md) |
| Reversed Z | The near plane is depth 1 and the far plane is depth 0. Depth is cleared to 0 and the depth test is `GreaterOrEqual`. | `Strata/src/Strata/Renderer/SceneRenderer.cpp` | [Projection](../basics/math-projection.md) |
| Fullscreen texture coordinates | A fullscreen pass turns NDC into texture coordinates (UV) with `uv = (ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5)`. | `Strata/shaders/Include/Common.slang` | [Coordinate systems](../gpu/coordinates.md) |
| Winding | Front faces are counter-clockwise. A mirrored instance (a negative scale on an odd number of axes) uses clockwise pipelines and flipped tangents. | `Strata/src/Strata/Renderer/SceneRenderer.cpp` | [Matrices](../basics/math-matrices.md) |
| Matrix storage | Matrices are column-major: the numbers of each column are stored side by side, the byte order of glm. Shaders are compiled with `-matrix-layout-column-major`. | `CMake/StrataShaders.cmake` | [Matrices](../basics/math-matrices.md) |
| Matrices in shaders | A vector is transformed as `mul(M, v)`, and a matrix :term[constructor]{id=constructor} such as `float3x3(...)` takes its rows. | `AGENTS.md` | [Matrices](../basics/math-matrices.md) |
| Quaternions | Across the script interface a rotation is a unit quaternion written x, y, z, w. | `StrataScriptCore/Include/StrataScript/ScriptABI.h` | [Rotations](../basics/math-rotations.md) |
| Euler angles | Degrees in the Inspector and in commands, radians in code that takes an angle such as a field of view. The order is pitch about X, yaw about Y, roll about Z. | `Strata/src/Strata/Math/Math.h` | [Rotations](../basics/math-rotations.md) |
| Camera-relative positions | Scene shaders work in world space with the camera at the origin. The view matrices carry rotation only, and the central processing unit (CPU) subtracts the camera position in double precision before it uploads. | `Strata/shaders/Include/Scene.slang` | [Coordinate systems](../gpu/coordinates.md) |

Two rows deserve a worked number. A camera at the origin that has no rotation looks along (0, 0, -1), so an object at (0, 0, -5) is five metres in front of it. An object at (2, 0, -5) is to its right, because +X is right when +Y is up and -Z is forward. In reversed Z, a point on the near plane has depth 1.0 and a point at infinity has depth 0.0, so a larger depth value means closer to the camera. The test `GreaterOrEqual` keeps a new surface at a pixel when its depth is larger than or equal to the one already stored.

:::why
Reversed Z spends the precision of a floating point number where a scene needs it. A float stores values near 0 with much finer steps than values near 1, and a perspective projection already crowds distant depths together. Mapping far to 0 puts the fine steps at a distance, which cancels most of the crowding. The cost is a convention every depth comparison, clear value and shader must follow, which is why the table lists it.
:::

The matrix rows hold one more trap. A matrix stored column-major has the same bytes in the C++ library glm and in the shader, so no transpose is needed when a buffer is uploaded. A shader's constructor still reads its arguments row by row, so `float3x3(a, b, c)` puts `a` in the first row, not the first column.

## Units and light

Strata uses metric units for space, mass and time: metres, kilograms and seconds. A unit cube is one metre wide, and a scene's gravity starts at 9.81 metres per second squared, pointing down -Y. Light uses the photometric units, so that a value in a light or sky field means a physical quantity and nothing changes its scale behind your back.

| Quantity | Unit | Used for | Taught in |
| --- | --- | --- | --- |
| Distance | metre | Positions, sizes, physics | [Positions, rotations and units](../make/transforms-units.md) |
| Mass | kilogram | Rigid bodies | [Positions, rotations and units](../make/transforms-units.md) |
| Time | second | Delta time, timers, audio | [Positions, rotations and units](../make/transforms-units.md) |
| Illuminance | lux | The sun's intensity | [Light units and exposure](../light/units-exposure.md) |
| Luminous intensity | candela | Point and spot lights | [Light units and exposure](../light/units-exposure.md) |
| Luminance | nit, which is candela per square metre | The sky, ambient light, emission and the face of a rect light | [Light units and exposure](../light/units-exposure.md) |
| Luminous power | lumen | A rect light whose `Units` field is `Lumens` | [Light units and exposure](../light/units-exposure.md) |
| Exposure | exposure value (EV), one stop | Camera exposure and its limits | [Exposure](../image/exposure.md) |
| Memory | KiB and MiB, powers of 1,024 bytes | Pack blocks, upload budgets | [Numbers](../basics/numbers.md) |

The light units come from `Strata/src/Strata/Renderer/RendererComponents.h`, where the comment on the light components states that the shading computes physical quantities on one scale and that exposure alone maps them to the display. A rect light, new in 0.8.0, gives its face a luminance in nits. With `Units` set to `Lumens` its value is the power it sends out, and the engine spreads that over the face as $L = P / (\pi A)$, half as much for a light with two faces. Here $P$ is the power in lumens, $A$ is the face's area in square metres, and $L$ is in nits. Exposure compensation is in stops: one more stop doubles the brightness, and the manual multiplier is $M = 2^{E}$, where $E$ is the `Exposure` field in stops and $M$ has no unit.

The next table gives light levels from the engine's developer guide, so that you can choose a value that looks right. The exposure column is the manual `Exposure` that shows an average surface at middle gray; such a surface has an albedo of 0.18, which means it reflects 18 % of the light that reaches it. It is hand-written from `Docs/DeveloperGuide.md` at the pin.

| Source | Level | Manual exposure |
| --- | --- | --- |
| Sunlight from morning to noon | 32,000 to 100,000 lux | -13 to -15 |
| Cloudless sky, looking away from the sun | 3,000 to 8,000 nits, or on the ground 10,000 to 25,000 lux | -12 |
| Cloudy day | 300 to 3,000 nits of sky, or 1,000 to 10,000 lux on the ground | -8 to -12 |
| Lit office | 300 to 500 lux | -7 |
| Moon at full | 0.1 to 0.3 lux | +3.5 to +5 |
| Lamp of 800 lumens | 64 candela | none given |
| Candle | 1 candela | none given |
| Screen or lit sign | 100 to 300 nits, about 1,000 nits | none given |

For a worked check, take the office row: 300 lux on a surface of albedo 0.18 gives about $300 \times 0.18 / \pi \approx 17$ nits. An exposure of -7 multiplies that by $2^{-7} = 0.0078$, which gives about 0.13, near the middle gray of 0.18. The estimate is rough, which is why the table gives ranges.

## Color

Strata does its lighting arithmetic in linear light, where doubling a value doubles the energy. A screen and most image files hold values that are not linear: they are encoded with the sRGB curve, which spends more of its steps on dark tones, where the eye is sensitive. The rules below say which side of that encoding each stage of the engine is on.

| Stage | Convention | Evidence | Taught in |
| --- | --- | --- | --- |
| Scene values | Linear. A value is luminance in nits, not a number from 0 to 1. | `Strata/src/Strata/Renderer/RendererComponents.h` | [Color](../basics/color.md) |
| Scene color target | The high dynamic range (HDR) target is `RGBA16_FLOAT`, four 16-bit floats. Every writer multiplies by a power of two, the pre-exposure, so that bright values fit. | `Strata/src/Strata/Renderer/SceneRenderer.h` | [Pre-exposure](../image/pre-exposure.md) |
| Color textures | Albedo, emissive and interface images are marked sRGB, and the :term[graphics processing unit]{id=gpu} (GPU) decodes them to linear on every read. | `Strata/src/Strata/Asset/TextureImporter.h` | [Color](../basics/color.md) |
| Data textures | Roughness, metallic, occlusion and masks are linear: their numbers are not colors. | `Strata/src/Strata/Asset/TextureImporter.h` | [Color](../basics/color.md) |
| Normal maps | Linear. Only X and Y are stored, and the shader rebuilds Z from them. | `Strata/shaders/Include/MaterialTextures.slang` | [Materials](../light/materials.md) |
| Output | The sRGB curve is applied last, after tone mapping, by `LinearToSRGB`. | `Strata/shaders/Include/Common.slang` | [Encoding](../image/encoding.md) |

Z can be rebuilt because a normal has length 1: if X is 0.6 and Y is 0.0, then $Z = \sqrt{1 - 0.6^2 - 0^2} = 0.8$. The square root needs X and Y inside the unit circle, which is why the importer restores the length of each normal at every smaller size.

:::note
A page of this book that must use another convention, such as a diagram with +Y pointing down in image space, or a matrix written with rows, says so where it appears. That page links to this page. A symbol that a page introduces is explained on that page, at its first use.
:::

## Where it lives in Strata

- `Strata/src/Strata/Math/Math.h`: the comment on the engine's conventions, the reversed-Z projections, the Euler helpers and the forward direction.
- `.claude/skills/strata-make-a-game/SKILL.md`: the facing of glTF models, +Z, against the engine's -Z forward.
- `Strata/shaders/Include/Common.slang`: the conversion from NDC to UV and the sRGB functions.
- `Strata/shaders/Include/Scene.slang`: camera-relative transforms of positions.
- `CMake/StrataShaders.cmake`: the compiler flag that makes matrices column-major.
- `AGENTS.md`: the paragraph "Renderer conventions" and the rule on matrix constructors.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: the depth clear, the depth test and the winding of mirrored instances.
- `StrataScriptCore/Include/StrataScript/ScriptABI.h`: the transform with its quaternion in x, y, z, w order.
- `Strata/src/Strata/Renderer/RendererComponents.h`: the light units and the exposure fields.
