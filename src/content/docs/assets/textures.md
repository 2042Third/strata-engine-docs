---
id: assets/textures
title: "Textures for the GPU: mips, color spaces, block compression"
description: "Why a texture is stored as a chain of small pictures in a block format, and how color, normal and data textures differ."
kind: concept
size: M
tracks: [E]
needs: [basics/color, basics/signals, gpu/how-a-gpu-frame-works]
time: 40
learn:
  - id: texture-size
    text: compute the stored size of a texture with its mip chain in RGBA8, BC1, BC7 and RGBA16F
  - id: color-spaces
    text: choose the usage of a texture and explain what a wrong choice does to its values
  - id: bc1-line
    text: explain why the colors of one BC1 block lie on a line and why data needs BC7
  - id: strata-formats
    text: name the format Strata stores for each usage and quality, and what each costs
since: 0.3.0
status: final
---

Picture a brick wall photographed at 4096 by 4096 texels (the pixels of a texture), a size that an artist or a good camera produces without effort. Stored as it left the paint program, in the format `RGBA8` (four :term[bytes]{id=byte} for each texel: red, green, blue and alpha), it takes $4096 \times 4096 \times 4 = 67{,}108{,}864$ bytes. That is 64 MiB for one wall. A scene has hundreds of textures: a color, a roughness and a normal map for every wall, crate, floor and character.

Two more problems appear on the screen. Walk away from the wall and its bricks begin to shimmer, because each pixel now covers many texels and the :term[graphics processing unit]{id=gpu} (GPU) reads only one of them. Import the wall's normal map as an ordinary picture and the wall looks wrong: the bumps are lit from the wrong side, or a flat part looks tilted. This page explains all three problems and the storage that answers them.

## Full size, one level, four bytes: where it breaks

The naive answer is to keep every texture at full size, as four bytes a texel, and sample level 0, the full-size picture. It breaks three times.

- **Memory.** Video memory is shared with the meshes, the shadow maps and the screen's own targets. Hundreds of 64 MiB textures do not fit in any graphics card.
- **Bandwidth.** The memory bandwidth, the bytes a GPU can read each second, limits a frame as often as the arithmetic does. A pixel that reads four bytes from a texture of a million texels, at a distance, wastes the cache: its neighbors read texels far apart.
- **Aliasing.** A distant wall has far more texels than pixels. Reading one texel for each pixel samples a detailed signal too rarely, and the result changes from frame to frame as the camera moves. [Sampling and aliasing](../basics/signals.md) explains why no cheap filter at the pixel can fix that.

Each problem has a part of the answer. The answer has three parts, and the rest of the page builds them one by one.

## The idea: small pictures, the right numbers, fixed-size blocks

A texture on disk is not a picture. It is a set of smaller pictures made in advance, each stored in a format that suits what its numbers mean and that the GPU reads without unpacking the whole texture.

```mermaid caption="The three parts of the answer. Each part acts on a different cost, and a texture in a game uses all three." alt="A flow from a source image to three steps: a chain of smaller levels, a number format chosen by what the texture holds, and a fixed-size block format. The steps end in the file the GPU reads."
flowchart LR
    A["Source image 4096 x 4096"] --> B["Mips: halved levels"]
    B --> C["Color space: what the numbers mean"]
    C --> D["Blocks: 4x4 texels in 8 or 16 bytes"]
    D --> E["Stored texture"]
```

Mips answer aliasing. The :term[color space]{id=color-space} answers wrong values. Blocks answer memory and bandwidth. The next three sections take them in that order.

## Mips are prefiltered levels for a third more memory

A **mip** (also a **mip level**) is one version of a texture at a power-of-two fraction of its size. Level 0 is the original, level 1 has half its width and height, level 2 a quarter, and so on down to one texel.

A **mip chain** is all the levels of one texture, from level 0 to the one-texel level.

The mips are made once, when the texture is imported, by filtering: each texel of level 1 is a weighted average of the texels of level 0 it covers. That is the prefiltering that [the signals page](../basics/signals.md) describes, done in advance for every size. At run time the GPU picks the level where one texel is about one pixel wide, so the distant wall reads from a small, already smoothed picture. The shimmer goes away, and the reads stay close together in memory.

:::example[How many levels, and how much more memory]
A 4096 by 4096 texture halves 12 times before it reaches one texel, so its chain holds 13 levels: 4096, 2048, 1024, and so on to 1. Each level has a quarter of the texels of the one before. The texel count is a sum:

$1 + \frac14 + \frac1{16} + \frac1{64} + \dots = \frac43$

times level 0, and so the whole chain holds a third more than level 0 alone. At four bytes a texel, level 0 is 64 MiB and the chain is about 85.3 MiB. The exact count of texels in the 13 levels is 22,369,621, times four bytes: 89,478,484 bytes.
:::

The extra third buys the removal of the shimmer, and it also helps bandwidth, because a far-away surface reads the small levels. A texture that is not square halves each side until both reach one, and a level never has a side of zero. The number of levels is $\lfloor \log_2 \max(w, h) \rfloor + 1$, where $w$ and $h$ are the width and height in texels, $\log_2$ is the number of times you halve a value to reach 1, and the brackets round down. For 4096 that gives 12 + 1 = 13.

## Color spaces: what the numbers in a texture mean

Not every texture holds a color. The GPU filters and blends numbers, and the right way to do it depends on what they stand for.

A photo or a painted albedo map holds colors in the sRGB encoding, in which a byte is not proportional to light, as [the color page](../basics/color.md) shows. Averaging two :term[sRGB]{id=srgb} bytes is wrong, because the average of black and white must be half the light, and half the light is stored as byte 188, not 127 or 128. So a texture of color is stored with an sRGB format: the GPU converts each texel to linear light first, and then filters. The importer does the same when it builds mips: it averages in linear space, then stores the result back in the encoded form.

A roughness map is different. Its numbers are **linear data**: values the :term[shader]{id=shader} uses as numbers (a roughness, a metal amount, an occlusion factor), not colors, so no curve applies. A roughness of 0.5 is stored as byte 128, and the GPU must return 0.5 and not the "linear light" that an sRGB decode would make of it (about 0.216). Linear data is stored in a format that has no sRGB conversion and averaged as it is.

Light is not limited to the range 0 to 1 either. A sky has a sun thousands of times brighter than the sky beside it, and a byte cannot hold that. A high dynamic range (HDR) texture in the format **HDR (RGBA16F)** stores each of red, green, blue and alpha as a 16-bit :term[floating-point number]{id=floating-point-number}, the half float of [the color page](../basics/color.md). Values far above 1 survive. It takes 8 bytes a texel, twice a plain `RGBA8` texel.

:::example[A flat normal map read as color]
A normal map stores a direction in tangent space (measured against the surface, with Z leaving it) as three bytes, and a surface that is flat has the direction $(0, 0, 1)$. The map writes it as $(0.5, 0.5, 1.0)$ in the range 0 to 1, because a direction value $v$ is stored as $(v + 1)/2$: the bytes are about $(128, 128, 255)$.

Import this texture as color and the GPU decodes it as sRGB before the shader sees it. Byte 128 is 0.502 encoded, which decodes to about 0.216 linear. The shader then computes $2 \times 0.216 - 1 = -0.57$ for both X and Y and rebuilds Z from them as about 0.60. A flat wall now looks tilted by more than 50 degrees toward one corner.
:::

The cure is the right usage at import. Strata calls it the texture's **Usage**, and it has four values: **Color**, **NormalMap**, **Data** and **HDR**. The importer guesses it from the file name, so `Rock_nor_gl.png` becomes a **NormalMap**, and you can change it afterwards. The usage decides the color space, the mip filter and the stored format.

::figure{id=usage-compare variant=normal-map}

::figure{id=usage-compare variant=color}

## Block compression stores 4x4 texels in 8 or 16 bytes

Memory is still large: the 4096 texture is 85.3 MiB.

**Block compression** is a family of GPU texture formats (`BC1` to `BC7`) that store each 4 by 4 block of texels in a fixed number of bytes. A block takes 8 bytes in `BC1` and `BC4`, and 16 in `BC3`, `BC5` and `BC7`.

A fixed rate matters more than the ratio. A block at column $b_x$ and row $b_y$ of a texture that is $n$ blocks wide starts at byte $(b_y \cdot n + b_x) \times s$, where $s$ is 8 or 16, the size of a block. The GPU finds any texel without unpacking its neighbors, so it reads a block, decodes it in hardware and caches the result. A format that squeezes by the picture's content, like a PNG, could not give this.

`BC1` is the plainest, and one block shows the idea that all the others vary. Its 8 bytes hold two endpoints, each a color in 16 bits (5 bits red, 6 green, 5 blue), and 16 two-bit **indices**, one for each texel. The decoder makes a palette of four colors: the two endpoints and two mixes, one third and two thirds of the way from the first to the second. A texel's index picks one of those four.

:::example[One BC1 block opened]
Take a block whose texels run from dark red to bright red. The encoder picks the endpoints $(255, 0, 0)$ and $(82, 0, 0)$: 82 is the 5-bit red value 10 widened to a byte, since 85 has no 5-bit form. The palette is $(255,0,0)$, $(82,0,0)$ and the mixes $(2 \times 255 + 82 + 1)/3 = 197$ and $(255 + 2 \times 82 + 1)/3 = 140$, rounded down, so $(197, 0, 0)$ and $(140, 0, 0)$.

A texel that was $(190, 0, 0)$ takes index 2, and the decoder gives $(197, 0, 0)$: an error of 7 in one channel. The block's 16 texels cost 4 bytes of indices and 4 bytes of endpoints, which is 4 bits a texel, against 32 for `RGBA8`.
:::

The four palette colors lie on one straight line through the space of colors, from one endpoint to the other. So every texel of a block is rounded to a point of that line. For most color pictures that costs little, because the colors inside a 4 by 4 patch are close to a line: a gradient, a shadow edge, a brick against its mortar.

The channels of data are not like this. A texture that packs occlusion, roughness and metallic in red, green and blue has three numbers that vary on their own. A metallic edge inside a block puts a texel far off the line, and the line then bends toward it, which shifts the roughness beside it. Data needs a format with more freedom than `BC1` gives, and that is `BC7`.

`BC7` has 16 bytes for the same 16 texels, so 8 bits a texel. It has eight modes, each a different split of the block's bits. A mode may divide the block into up to three **partitions**, regions with their own endpoints, so one block can hold several lines. It may add a p-bit to widen the endpoints' precision by one bit, or store one channel, often alpha, apart from the others.

[Texture cooking](texture-cooking.md) teaches the parts with the encoder. What matters here is the result: nearly any 16 texels fit well in `BC7`.

Normal maps have a format of their own. A **normal map** is a texture of surface directions in tangent space. A direction of length one has only two free numbers: knowing $x$ and $y$, the length gives $z = \sqrt{1 - x^2 - y^2}$, where the root is of a value kept at or above 0.

`BC5` stores two channels, each as a `BC4` block: two 8-bit endpoints and a 3-bit index for each texel, so eight values between the endpoints. The shader reads X and Y from the map and rebuilds Z, as [the materials chapter](../light/material-data.md) shows.

`BC4` is the same one-channel block alone, 8 bytes for 16 texels. Strata uses it for data that has a single channel, such as a height map, and the shader reads it as gray, the red value in red, green and blue.

## How engines store textures

Each approach answers a flaw of the one before.

1. **Uncompressed** (`RGBA8`, `RGBA16F`). Exact to the format's precision and cheap to produce, but 32 or 64 bits a texel, so it uses the most memory and bandwidth.
2. **The block formats `BC1` to `BC7`.** Fixed blocks of 4 by 4 texels: 4 bits a texel for `BC1` and `BC4`, 8 for `BC5` and `BC7`. The cost is a slow encoder (`BC7` especially) and a loss of detail. Every desktop and console GPU decodes them in hardware.
3. **`ASTC` and `ETC2`.** Phones and tablets do not decode the `BC` formats. `ASTC` stores a block of 128 bits that covers from 4 by 4 up to 12 by 12 texels, so the rate runs from 8 down to under 1 bit a texel. `ETC2` is older and simpler, at 4 or 8 bits a texel.
4. **Transcoding at load time.** One shipped file, such as Basis Universal, is converted by the :term[central processing unit]{id=processor} (CPU) into whichever format the device can decode. It trades some quality, and some load time, for one file on every device.

| Format | Bits per texel | Quality | Encoding cost | Used on |
| --- | --- | --- | --- | --- |
| `RGBA8` | 32 | Exact at 8 bits | None | Everywhere |
| `RGBA16F` | 64 | Exact, values above 1 | None | HDR images |
| `BC1` | 4 | Fair: one line a block | Low | Desktops and consoles |
| `BC4`, `BC5` | 4, 8 | Good: one or two channels | Low | Desktops and consoles |
| `BC7` | 8 | High: all four channels | High | Desktops and consoles |
| `ASTC` | 0.89 to 8 | High, a size you choose | High | Phones, newer desktops |
| `ETC2` | 4, 8 | Fair | Medium | Phones |
| Basis Universal | that of the target | Fair to good | High | One file for many devices |

## Strata chooses the format from the usage

Strata runs on desktops, so it stores block formats, and the importer picks the format by the usage, the quality and whether the image has alpha. The **Quality** setting is High or Fast and changes only color: at Fast an opaque color texture is `BC1`, half the bytes of `BC7`, and at High every color texture is `BC7`.

| Usage | Default format | Bits per texel | Without compression |
| --- | --- | --- | --- |
| **Color** | `BC7SRGB`; at Fast and opaque, `BC1SRGB` | 8 or 4 | `RGBA8SRGB` |
| **NormalMap** | `BC5` | 8 | `RGBA8` |
| **Data** | `BC7`; one channel, `BC4` | 8 or 4 | `RGBA8`; one channel, `R8` |
| **HDR** | `RGBA16F` | 64 | the same |

The **Compression** setting is **Auto**, which gives the formats above, or **Uncompressed**. **HDR** ignores it. The details of how the importer cooks the mips and encodes the blocks are in [texture cooking](texture-cooking.md).

:::why[Why does data ignore the Fast quality?]
Fast searches only the `BC7` modes that have one partition, and those keep a block's colors on one line, as `BC1` does. Color mostly follows such lines. Data does not: a metallic edge in a block would shift the roughness beside it. So Strata searches data in full at both qualities, and a game maker's Fast setting saves time and bytes only where it does no harm.
:::

Strata never computes a size from bytes a pixel. `GetMipByteSize` in `Strata/src/Strata/Renderer/TextureFormat.cpp` rounds the width and the height up to whole blocks, and multiplies the blocks by the bytes of one. A 2 by 2 level of `BC7` is one whole 16-byte block, not the 4 bytes that one byte a texel suggests.

## What Strata's choice cannot do

Strata has no `BC6H`, the block format for high dynamic range. So a sky takes 8 bytes a texel in `RGBA16F`, which is eight times the cost of `BC7` and sixteen times that of `BC1`. A large sky is an expensive texture, and the importer cannot shrink it except by a smaller `MaxSize`, the import setting that limits the longest side.

Strata also has no formats for phones: no `ASTC` and no `ETC2`, because the engine runs on Windows, Linux and macOS desktops only. A graphics device that cannot sample block formats gets them decoded at load to a plain format, and then pays the full size in memory. The [appendix of what Strata lacks](../appendix/not-in-strata.md) lists the other limits. Loading only some of a texture's levels is the business of [mip streaming](../draw/mip-streaming.md).

## Common mistakes

- **Sizes from bytes per pixel.** Symptom: an upload that fails its check, or a memory total that is too small. Fix: count blocks, with `GetMipByteSize`; a level smaller than 4 by 4 still takes one block.
- **A normal map imported as Color.** Symptom: flat surfaces look tilted, and lighting is wrong everywhere on the material. Fix: set the usage to **NormalMap**.
- **The wrong green channel.** Symptom: bumps that should rise look like dents, and the lit side is the opposite of the light's. Some tools write normal maps with +Y up (OpenGL) and others with +Y down (DirectX). Fix: enable `FlipGreen` for a DirectX map; the importer enables it for a name with a `dx` token.
- **Data imported as Color.** Symptom: a roughness map that looks right as a picture gives the wrong shine, because an sRGB decode bends its values. Fix: usage **Data**.
- **An HDR sky imported as Color.** Symptom: the sun is gray and its light is missing, because a byte stops at 1. Fix: usage **HDR**, which stores `RGBA16F`.

## Summary

- Compute a texture's stored size block by block: width and height rounded up to whole 4 by 4 blocks, times the bytes of a block, summed over a chain that adds a third.
- Choose the usage by what the numbers mean: **Color** for sRGB colors, **NormalMap** for directions, **Data** for linear numbers, **HDR** for light above 1; a wrong choice bends every value.
- A `BC1` block holds two endpoints and a 2-bit index for each texel, so its colors lie on one line; data with independent channels needs `BC7`.
- Strata stores color as `BC7SRGB` (`BC1SRGB` for opaque color at Fast), normal maps as `BC5`, one-channel data as `BC4`, other data as `BC7` and HDR as `RGBA16F`.

## Check yourself

1. A 1024 by 1024 texture in `RGBA8` with a full chain: how many bytes does it take, to the nearest KiB?

   - (a) 4 MiB, because level 0 is 4 MiB.
   - (b) 5,461 KiB (about 5.33 MiB), because the chain adds a third.
   - (c) 8 MiB, because each mip doubles the cost.

   :::answer{tests="texture-size"}
   (b). Level 0 is $1024 \times 1024 \times 4 = 4$ MiB, and the levels after it add a third: 5.33 MiB. Answer (a) forgets the chain. Answer (c) has the wrong direction: each level is a quarter of the one before, not twice as big.
   :::

2. Which usage fits a texture named `Crate_rough.png`, which holds the roughness of a crate? Which goes wrong if you pick **Color**: the stored values, the mip averaging, or both?

   :::answer{tests="color-spaces"}
   Data, because the file holds numbers and not colors. Picked as **Color**, both go wrong. The GPU decodes an sRGB curve that the roughness never had, so a stored 0.5 reads as about 0.22. The mips are averaged in linear light, not in the numbers the shader expects.
   :::

3. A `BC1` block holds the four colors red, green, blue and black. Can it store all four exactly? Say why.

   :::answer{tests="bc1-line"}
   No. A block holds two endpoints and two mixes of them, all on one line, and these four colors do not lie on a line. At best two of them are exact and the other two are rounded to points of the line.
   :::

4. A material's texture is a DirectX normal map, imported with **NormalMap** and the default settings. The bumps look like dents. Which setting do you change, and what does it do to the map?

   :::answer{tests="strata-formats,color-spaces"}
   Enable `FlipGreen`. It inverts the green channel (Y), which a DirectX map has pointing down where Strata's convention points up. The format stays `BC5`, because the usage is still **NormalMap**.
   :::

## Exercises

1. **Basic.** Work out by hand the stored size of a 4096 by 4096 texture with all its mips as `RGBA8`, `BC1`, `BC7` and `RGBA16F`. Then write a program that checks your numbers. Compare them with the cache file that an import writes: an opaque **Color** at **Fast** for `BC1`, **Color** at **High** for `BC7`, **Uncompressed** for `RGBA8`.

   ::::answer[Worked solution]{tests="texture-size,strata-formats" solution="sketches/assets-textures-sizes.cpp"}
   By hand: level 0 holds 16,777,216 texels. `RGBA8` takes 4 bytes each: 64 MiB, and the chain adds a third. `BC1` and `BC7` take 8 and 16 bytes for each block of 16 texels: 8 MiB and 16 MiB. `RGBA16F` takes 8 bytes each: 128 MiB. Each chain is a third more, with the last levels rounded up to a whole block.

   :::question[Is the C++ below new to you?]
   The code uses functions, loops and a structure ([programming 2](../basics/programming-2.md)), and a call such as `std::printf` and a reference ([programming 3](../basics/programming-3.md)).
   :::

   The program follows `GetMipByteSize`: it rounds both sides up to whole blocks and multiplies. Find the two rounding lines and the loop that halves the side.

   ```cpp sketch="assets-textures-sizes.cpp"
   // The stored size of a 4096 by 4096 texture with its whole mip chain, in four formats.
   #include <cstdint>
   #include <cstdio>

   struct Format
   {
   	const char* Name;
   	uint32_t BlockSide;     // Texels along one side of a block: 1 for formats that are not compressed
   	uint32_t BytesPerBlock;
   };

   uint64_t GetMipByteSize(const Format& format, uint32_t width, uint32_t height)
   {
   	const uint64_t blocksX = (width + format.BlockSide - 1) / format.BlockSide;
   	const uint64_t blocksY = (height + format.BlockSide - 1) / format.BlockSide;
   	return blocksX * blocksY * format.BytesPerBlock;
   }

   int main()
   {
   	const Format formats[] = { { "RGBA8", 1, 4 }, { "BC1", 4, 8 }, { "BC7", 4, 16 }, { "RGBA16F", 1, 8 } };
   	for (const Format& format : formats)
   	{
   		uint64_t chain = 0;
   		uint32_t levels = 0;
   		for (uint32_t side = 4096; side >= 1; side /= 2)
   		{
   			chain += GetMipByteSize(format, side, side);
   			levels++;
   		}
   		std::printf("%-8s %u levels, level 0 %llu bytes, chain %llu bytes\n", format.Name, levels,
   			static_cast<unsigned long long>(GetMipByteSize(format, 4096, 4096)), static_cast<unsigned long long>(chain));
   	}
   	return 0;
   }
   ```

   ```text output-of="assets-textures-sizes.cpp"
   RGBA8    13 levels, level 0 67108864 bytes, chain 89478484 bytes
   BC1      13 levels, level 0 8388608 bytes, chain 11184824 bytes
   BC7      13 levels, level 0 16777216 bytes, chain 22369648 bytes
   RGBA16F  13 levels, level 0 134217728 bytes, chain 178956968 bytes
   ```

   1. **Lines 14–15:** each side rounds up to whole blocks, so a 2 by 2 level of `BC7` is one block, not a quarter of one.
   2. **Lines 26–29:** the side halves until it is 1, and the loop counts 13 levels.

   The cache files are named by the asset's handle, with the ending `.bin`, in the project's cache folder. Each should be a little larger than the chain, by a header, a table of levels, the name and padding.
   ::::

2. **Medium.** Open a copy of the Showcase sample. Import one of its normal maps, for example `WeatheredSteel_nor_gl.png`, with Usage **NormalMap** and then with **Color** (command `asset.setImportSettings` with `"settings": {"Usage": "Color"}`). Compare the two in the Scene view on a surface that uses the map, and describe the difference.

   :::answer[Worked solution]{tests="color-spaces"}
   Find a material that uses the map and look at it with a light at a low angle. As **NormalMap** the surface shows small bumps lit from one side. As **Color** the map is decoded as sRGB, so flat parts get a direction tilted by the amounts the page computes (X and Y near -0.57), and the whole surface shades as a slope. Set the usage back to **NormalMap** after the test.
   :::

3. **Hard.** Four colors of one block are red $(255, 0, 0)$, green $(0, 255, 0)$, blue $(0, 0, 255)$ and black $(0, 0, 0)$. Choose the two endpoints of the best `BC1` block you can, compute its palette, and say which colors are lost.

   :::answer[Worked solution]{tests="bc1-line"}
   Any two endpoints give four palette colors on one line, so at most two of the four colors can be exact. Take red and green as endpoints. The palette is $(255,0,0)$, $(0,255,0)$ and the mixes $(2 \times 255 + 0 + 1)/3 = 170$ and $(255 + 0 + 1)/3 = 85$, so $(170, 85, 0)$ and $(85, 170, 0)$.

   Red and green are exact. Black is $36{,}125$ away in squared distance from either mix, and blue is $101{,}150$ away, so each takes one of the two mixes. Blue becomes a dark yellow-brown and its blue is gone. `BC7` can split the block into partitions, each with its own line, and keeps more of the four. Strata sends data to `BC7` for that reason.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/TextureFormat.cpp`: the format table (`GetTextureFormatInfo`) and `GetMipByteSize`.
- `Strata/src/Strata/Asset/TextureImporter.cpp`: the usage, compression and quality settings, the guess from the file name, and `TextureImporter::ChooseFormat`.
- `Strata/src/Strata/Asset/TextureCooker.cpp`: the mips and the block compression code; its details are in [texture cooking](texture-cooking.md).
- `Strata/src/Strata/Renderer/CookedTexture.h`: the stored form of a cooked texture, with the levels' table.
- `Strata/src/Strata/Renderer/BlockCompression.cpp`: the decoder for devices that cannot sample block formats.
- `asset.setImportSettings`: the command that changes `Usage`, `Compression`, `Quality`, `GenerateMips`, `FlipGreen` and the other import settings of a texture; `asset.info` lists them.
- `AssetEdit::FindTextureUsageMismatches` in `StrataEditor/src/Editor/AssetEdit.cpp`: finds a texture whose usage does not fit its material slot.

## Further reading

- Khronos Data Format Specification, the chapters on BC1, BC4, BC5 and BC7: the exact bit layouts; advanced.
- Real-Time Rendering, Akenine-Moller, Haines and Hoffman, the chapter on texturing: mipmaps and compression; intermediate.
- ASTC specification of the Khronos Group: the flexible block format of phones; advanced.
- The Basis Universal project on GitHub: the transcoding format; intermediate.
