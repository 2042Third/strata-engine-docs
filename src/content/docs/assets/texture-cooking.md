---
id: assets/texture-cooking
title: "Cooking textures: Strata's importer, mips and BC7 encoder"
description: "How Strata turns a picture file into a cooked texture: the importer's settings, the mip filter, the BC7 encoder and the STTX file the GPU and the streamer read."
kind: internals
size: L
tracks: [E]
needs: [assets/importing, assets/textures, basics/numbers]
time: 80
learn:
  - id: cooking-flow
    text: explain why Strata encodes one mip level and then filters the next, and what a cook holds in memory
  - id: format-choice
    text: choose the stored format of a texture from its usage, its channels, its alpha and its quality setting
  - id: mip-sizes
    text: compute the byte size and the offset of every level of a BC7 texture in an STTX file
  - id: bc7-fit
    text: explain how the BC7 encoder fits a block's endpoints along the colors' principal axis and refits them by least squares
  - id: name-defaults
    text: trace how the tokens of a file name choose a texture's import settings
since: 0.3.0
status: final
---

An artist hands the engine a picture file: a PNG, a JPEG or a Radiance :term[high dynamic range]{id=high-dynamic-range} (HDR) image. Such a file is made
to be stored and opened by people. The :term[graphics processing unit]{id=gpu} (GPU) cannot sample it. The GPU needs raw texels in one
fixed format, with every :term[mip level]{id=mip} ready, laid out so that a streamer can read the small levels first.

The texture :term[importer]{id=importer} turns the file into that form. It decodes the picture, applies the settings, builds the mip levels,
encodes each level and writes an `STTX` file. It does so as a background job, as fast as the job system allows, and exactly
as the settings say.

The page does not teach how the GPU uses the result. Uploading levels in steps belongs to [Uploads](uploads.md). The
resident tail and the reads of finer levels belong to [Mip streaming](../draw/mip-streaming.md), and what the :term[shader]{id=shader} does
with a :term[normal map]{id=normal-map} to [Material data](../light/material-data.md). What the sun finder sees in a sky is the subject of
[Sky](../light/sky.md), and the textures inside a glTF model belong to [glTF models](models-gltf.md).

## The problem and how engines solve it

[Textures](textures.md) explains why a picture file cannot go to the GPU as it is: the GPU wants fixed block formats, mip
chains and a :term[color space]{id=color-space} for each kind of data. The cook is where those needs meet the artist's file. An engine can cook
when it loads the file, which costs the player time at every start. It can also cook once on the developer's machine, which
costs nothing at play and lets the cook take its time. Strata cooks once, in the editor, into a cache that exports copy into
packs.

Two costs remain: the time of a cook, which blocks only the person waiting for a new asset, and the care a cook
needs, because every wrong choice stays baked in until the next import.

## The map

Seven pieces take part. The diagram shows who calls whom, and the paragraph after it says what each piece owns.

```mermaid caption="A picture file flows through the importer, which may call the sun finder. The cooker filters each level and hands it to an encoder. The cooked texture holds the levels. A loader reads it through the parser, and decodes blocks when the device cannot sample them." alt="A diagram of boxes and arrows. A picture file leads to the importer. The importer leads to a sun finder for sky images and to the cooker. The cooker uses the block encoder and the size arithmetic, and its levels go to the cooked texture writer. A loader reads the cooked texture through the parser and, on a device without block compression, through the block decoder."
flowchart TD
	file["Picture file: .png .jpg .tga .bmp .psd .gif .hdr"] --> importer["TextureImporter: settings, defaults, Decode, ChooseFormat"]
	importer -->|"RemoveSun"| sun["HDRSun: Find, Remove"]
	importer --> cooker["TextureCooker: CookLevels, CookHDRLevels"]
	cooker --> encoder["BC7Encoder: EncodeBlock"]
	cooker --> sizes["TextureFormat: GetMipByteSize"]
	cooker --> writer["CookedTexture: STTX, ComputeCookedTextureLayout"]
	writer --> parser["ParseCookedTexture"]
	parser --> loader["Texture loader"]
	loader -->|"no BC support"| decoder["BlockCompression: DecodeLevel"]
```

`TextureImporter` owns the settings, the defaults guessed from the file name, the decoding of the image (`Decode`) and the
choice of stored format (`ChooseFormat`). `TextureCooker` builds the mips and hands each level to an encoder. `BC7Encoder`
writes the `BC7` blocks, and the other block formats come from the `stb_dxt` library. `HDRSun` paints the sun out of a sky
when the setting asks. `CookedTexture` is the :term[stored form]{id=stored-form}, `TextureFormat` holds the size arithmetic, and
`BlockCompression` decodes blocks for devices that cannot sample them.

The stored form has a name of its own. The **`STTX`** file is Strata's cooked texture: a :term[header]{id=header}, a table of mip levels, a
name, and then the levels of pixels, smallest level first. It lives in the :term[import cache]{id=import-cache} and in packs, and its :term[magic number]{id=magic-number}
spells its name.

## The contract

The importer promises its callers a few things and asks a few of them. The rules fall into five groups: the settings, the
guesses from the file name, the limits of an image, the format of each usage and the stored form.

### Ten settings, four of them conditional

A texture asset has ten :term[import settings]{id=import-settings}. Four of them can be inactive: the editor shows them greyed out, with a reason that
`GetInactiveReason` writes, and the cook ignores them.

| Setting | What it chooses | Inactive when |
| --- | --- | --- |
| `Usage` | How the texels are read: color, normal map, data or HDR | never |
| `Compression` | :term[Block compression]{id=block-compression-bc1-bc7} (`Auto`) or exact texels (`Uncompressed`) | Usage is HDR: those stay 16-bit float |
| `Quality` | How hard color's block compression works: `High` or `Fast` | Usage is HDR, Compression is `Uncompressed`, or Usage is not color |
| `GenerateMips` | A full chain, or the one level | never |
| `Filter` | The sampling filter stored in the file | never |
| `Wrap` | The edge mode stored in the file, also used while filtering | never |
| `MaxSize` | The longest side allowed; 0 means the engine limit | never |
| `FlipVertically` | Reverses the rows | never |
| `FlipGreen` | Inverts the green channel, for normal maps of DirectX's convention | Usage is not `NormalMap` |
| `RemoveSun` | Paints the sun out of an HDR sky | Usage is not HDR |

Each reason exists so that a setting never promises what the cook will not do. `Quality` is the one worth a look. It only
chooses how block compression encodes color. Without compression, with normal maps and with data it would change
nothing, and the editor says so instead of leaving you to wonder.

### Defaults from the file name

A person who drops `Brick_Normal_2k_DX.png` into a project should not have to tell the importer that it holds a normal map.
`GetDefaults` guesses from the extension and the file name. A `.hdr` file is HDR with the clamp wrap mode.

For other files, `GetNameTokens` splits the stem at an underscore, a minus sign, a dot, a space and each change from a small
letter to a capital. It turns the parts into small letters, and drops the resolution tokens (`2k`, `1024`, `2048x2048`) and
the convention tokens such as `gl` and `dx`.

Two groups of tokens then decide the usage, anywhere in the name. Tokens such as `nor`, `nrm`, `normal` and `normaldx` make
a normal map, as does `n` as the last token. Tokens such as `rough`, `metal`, `ao`, `orm`, `mask` and `height` make data.
Every other name is color. On a normal map, a `dx`, `directx` or `normaldx` token also turns `FlipGreen` on, because a DirectX normal map
points its +Y down.

### The limits of an image

An image has at most 16,384 texels on its longest side. A larger one is scaled down with its aspect ratio kept, and `MaxSize`
0 means exactly this limit. A cooked texture holds at most 15 levels, the full chain of that size. An image of more than
268 million texels is refused.

Only Radiance HDR files keep more than 8 bits a channel. A 16-bit PNG imported as color, normals or data is decoded to 8
bits. A `.gif` file gives its first frame. The importer reads `.png`, `.jpg`, `.jpeg`, `.tga`,
`.bmp`, `.psd`, `.gif` and `.hdr`, and nothing else.

### One format per usage

The stored format follows from the usage and a few facts about the image, never from a setting that names the format. The
table lists what `ChooseFormat` returns.

| Usage | Compressed (`Auto`) | `Uncompressed` |
| --- | --- | --- |
| Color | `BC7SRGB`; at `Fast`, `BC1SRGB` when every texel is opaque | `RGBA8SRGB` |
| `NormalMap` | `BC5` | `RGBA8` |
| Data, one channel | `BC4` | `R8` |
| Data, more channels | `BC7` | `RGBA8` |
| HDR | `RGBA16F` | `RGBA16F` |

### The stored form

The cooked :term[bytes]{id=byte} follow four rules, which the real code below shows in place. The levels lie smallest first, so the mip tail
is one range right after the header. Each level starts at a multiple of 16 bytes. Every size comes from `GetMipByteSize`.
Every read of cooked bytes goes through `ParseCookedTexture`.

:::rule[Texture sizes come from `GetMipByteSize`]
`AGENTS.md` forbids computing a level's size from bytes per pixel. A `BC7` level of 2 by 2 texels takes one whole 16-byte
block, not the 4 bytes that one byte per texel suggests. A count that is off by blocks breaks validation, staging and the
residency totals alike.
:::

:::rule[Read cooked textures through `ParseCookedTexture`]
`AGENTS.md` asks every reader to go through this one function, which checks each offset and size. A reader that walks the
header by hand trusts a file that may be cut or damaged, and one bad offset then reads memory it does not own.
:::

:::rule[A change of output bumps the importer's version]
`AGENTS.md` asks that a change in what an importer writes also changes its `GetVersion()`. Two importers cook textures,
`TextureImporter` and `GltfImporter`, so a change to the cooker bumps both. The reason is in [Importing](importing.md): the
version is part of what decides that a cached result is stale.
:::

## A toy version

:::question[What do the loops, the helper functions and the `std::vector` mean?]
Plain C++ of [loops and functions](../basics/programming-2.md) and of [classes and calls](../basics/programming-3.md) builds
the toy; its comments say what each part does.
:::

The toy cooks a gray 8 by 8 image. It builds the mip chain with a box filter, which averages the 2 by 2 texels under each new
texel. For each level it prints two size counts: the whole blocks of `BC7`, and the wrong count of one byte per texel. Look at
the first texel of each level, and at the point where the two size counts part.

```cpp sketch="assets-texture-cooking-toy.cpp"
// A toy cook: a box filter builds the mip chain of a gray image, and two size counts are compared for each level.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <vector>

struct Level
{
	uint32_t Width = 0;
	uint32_t Height = 0;
	std::vector<float> Texels;
};

Level Halve(const Level& source)
{
	Level next;
	next.Width = std::max(1u, source.Width / 2);
	next.Height = std::max(1u, source.Height / 2);
	next.Texels.resize(static_cast<size_t>(next.Width) * next.Height);
	for (uint32_t y = 0; y < next.Height; y++)
	{
		for (uint32_t x = 0; x < next.Width; x++)
		{
			// Each new texel is the mean of the 2x2 texels below it; an odd edge reads its last row or column twice.
			float sum = 0.0f;
			for (uint32_t offset = 0; offset < 4; offset++)
			{
				const uint32_t sourceX = std::min(x * 2 + offset % 2, source.Width - 1);
				const uint32_t sourceY = std::min(y * 2 + offset / 2, source.Height - 1);
				sum += source.Texels[static_cast<size_t>(sourceY) * source.Width + sourceX];
			}
			next.Texels[static_cast<size_t>(y) * next.Width + x] = sum / 4.0f;
		}
	}
	return next;
}

// BC7 stores whole 4x4 blocks of 16 bytes: round the size up to blocks before multiplying.
uint64_t GetBC7Size(uint32_t width, uint32_t height)
{
	const uint64_t blocksX = (width + 3) / 4;
	const uint64_t blocksY = (height + 3) / 4;
	return blocksX * blocksY * 16;
}

int main()
{
	Level level;
	level.Width = 8;
	level.Height = 8;
	for (uint32_t y = 0; y < 8; y++)
	{
		for (uint32_t x = 0; x < 8; x++)
			level.Texels.push_back(static_cast<float>((x + y) * 16));
	}

	for (;;)
	{
		const uint64_t naive = static_cast<uint64_t>(level.Width) * level.Height; // one byte per texel
		std::printf("%ux%u: first texel %.0f, BC7 %llu bytes, one byte per texel %llu\n", level.Width, level.Height, level.Texels[0],
			static_cast<unsigned long long>(GetBC7Size(level.Width, level.Height)), static_cast<unsigned long long>(naive));
		if (level.Width == 1 && level.Height == 1)
			break;
		level = Halve(level);
	}
	return 0;
}
```

```text output-of="assets-texture-cooking-toy.cpp"
8x8: first texel 0, BC7 64 bytes, one byte per texel 64
4x4: first texel 16, BC7 16 bytes, one byte per texel 16
2x2: first texel 48, BC7 16 bytes, one byte per texel 4
1x1: first texel 112, BC7 16 bytes, one byte per texel 1
```

1. **Lines 14–18:** `Halve` builds the next level, half as wide and half as high, never below one texel.
2. **Lines 24–32:** each new texel is the mean of four parents; at an odd edge the last row or column counts twice.
3. **Lines 41–43:** sizes round up to whole blocks of 4 by 4 texels before they multiply by 16 bytes.
4. **Lines 57–64:** the loop prints each level and halves until one texel is left.

The first new texel is the mean of its four parents: (0 + 16 + 16 + 32) / 4 = 16. The chain ends at 112, the mean of the whole
image. The two size counts agree for the 8 by 8 and 4 by 4 levels and part from the 2 by 2 level. There `BC7` stays at 16 bytes,
one whole block, while one byte per texel says 4 and then 1. The toy omits everything that makes a real cook hard: color
spaces, alpha, edges, normals, the encoder and the file.

## The real code, in the order the data flows

### Decoding and the settings

`TextureImporter::Import` reads the source through `ReadImportSource`. It turns the stored settings into a
`TextureImportSettings` (each invalid value keeps its default and adds a warning) and calls `Decode`. `Decode` checks the
cancel flag at each step and fails with the reason, because an import is background work that the editor may cancel.

`Decode` reads the image header first and refuses a size above 2^28 texels before it decodes anything. It then limits the size with
`CalculateTargetSize`, which scales by the longest side and keeps the aspect ratio.

The decode step differs by usage. For HDR it asks stb_image for four float channels. For everything else it asks only for the
channels the stored format needs. Color keeps `RGB` or `RGBA`, a normal map keeps three channels, and data keeps its own channels
(one stays one, so that a gray roughness map can become `BC4`).

When the size changes, the scaling runs once, straight from stb's buffer: color in linear space with its :term[sRGB]{id=srgb} curve, the
others channel by channel. Then the rows flip if `FlipVertically` asks. A DirectX normal map has its green channel inverted
before any mip is made, so every level inherits the flip.

The importer next decides whether the image has alpha: a four-channel image counts only when some texel is not 255. The
format depends on it, and many files carry an alpha channel that is fully opaque.

### Choosing the format

`ChooseFormat` is a switch on the usage. Search the quote for the two comments, which hold the reasons.

```cpp src="Strata/src/Strata/Asset/TextureImporter.cpp#L641-L666" symbol="TextureImporter::ChooseFormat"
TextureFormat TextureImporter::ChooseFormat(const TextureImportSettings& settings, uint32_t channels, bool hasAlpha)
{
	const bool compress = settings.Compression == TextureCompression::Auto;
	switch (settings.Usage)
	{
		case TextureUsage::Color:
			if (!compress)
				return TextureFormat::RGBA8SRGB;
			// Fast trades quality for time and size where it can: opaque color as BC1 (half of BC7's bytes, colors on one
			// line per block). Alpha needs BC7 (BC3's color is BC1's).
			return settings.Quality == TextureQuality::Fast && !hasAlpha ? TextureFormat::BC1SRGB : TextureFormat::BC7SRGB;
		case TextureUsage::NormalMap:
			return compress ? TextureFormat::BC5 : TextureFormat::RGBA8;
		case TextureUsage::Data:
			// The channels of data vary independently (occlusion, roughness and metallic in one texture), which BC1 and
			// BC3 cannot store (the colors of one of their blocks lie on a line through RGB space, so a metallic edge
			// inside a block would shift the roughness next to it by up to a sixth); BC7 can, with partitions and a
			// channel stored apart. One channel is BC4.
			if (channels == 1)
				return compress ? TextureFormat::BC4 : TextureFormat::R8;
			return compress ? TextureFormat::BC7 : TextureFormat::RGBA8;
		case TextureUsage::HDR:
			return TextureFormat::RGBA16F;
	}
	return TextureFormat::RGBA8;
}
```

1. **Lines 647–648:** without compression, color is stored as `RGBA8SRGB`: exact texels need no block format.
2. **Lines 649–651:** at `Fast`, opaque color takes `BC1SRGB`, which halves the bytes; alpha or `High` takes `BC7SRGB`.
3. **Lines 655–658:** the comment says why data takes `BC7`: its channels vary independently, which one line of colors cannot hold.
4. **Lines 659–661:** one channel is `BC4`, and more channels are `BC7`.
5. **Line 663:** HDR is always `RGBA16F`, whatever the other settings say.

The reasons are the part to keep. Fast color becomes `BC1` where it can, because `BC1` takes half of `BC7`'s bytes and keeps
each block's colors on one line through color space, which most color does. Alpha needs `BC7`, since the color half of `BC3`
is `BC1`'s.

Data is different. Roughness, metallic and occlusion are often packed into the channels of one texture, and the values of one
channel have nothing to do with another's. A `BC1` block keeps its colors on a line, so a sharp edge in the metallic channel
inside one block would drag the roughness beside it by up to a sixth. `BC7` has partitions and can store a channel apart, so
data takes `BC7` at either quality.

### Cooking the levels

An 8-bit level reaches `TextureCooker::CookLevels`, where the cook decides what it holds in memory. Two terms come first.

A **Mitchell filter** is a resampling filter that weighs the texels around a new texel by a smooth curve with small negative
lobes, which keeps edges sharper than an average without much ringing. Strata uses it, through the stb_image_resize2 library,
to halve each level from the one before.

**Alpha weighting** filters color weighted by alpha, so a transparent texel's color does not bleed into its opaque
neighbors. A fully transparent texel with red color adds nothing to the red of the texel beside it.

```cpp src="Strata/src/Strata/Asset/TextureCooker.cpp#L275-L309" symbol="CookLevels"
bool CookLevels(Image level0, const CookSettings& settings, std::vector<TextureMip>& outMips, std::string* outError)
{
	if (!CanEncode(settings.Format))
		return Fail(outError, fmt::format("textures cannot be encoded as {}", TextureFormatToString(settings.Format)));
	if (!IsValidImage(level0))
		return Fail(outError, "the image is empty or its size does not match its pixels");

	const uint32_t mipCount = settings.GenerateMips ? TextureUtils::CalculateMipCount(level0.Width, level0.Height) : 1;
	outMips.clear();
	outMips.reserve(mipCount);
	Image current = std::move(level0);
	if (settings.NormalMap)
		NormalizeNormalMap(current);
	for (uint32_t level = 0; level < mipCount; level++)
	{
		TextureMip mip;
		mip.Width = current.Width;
		mip.Height = current.Height;
		if (!EncodeLevel(current, settings.Format, settings.HighQuality, mip.Data, settings.Cancel))
			return Fail(outError, IsCancelled(settings.Cancel) ? std::string(c_CancelledError) : fmt::format("encoding mip {} failed", level));
		outMips.push_back(std::move(mip));
		if (level + 1 == mipCount)
			break;

		if (IsCancelled(settings.Cancel))
			return Fail(outError, c_CancelledError);
		Image next;
		if (!Halve(current, settings, next))
			return Fail(outError, fmt::format("filtering mip {} failed", level + 1));
		if (settings.NormalMap)
			NormalizeNormalMap(next);
		current = std::move(next);
	}
	return true;
}
```

1. **Line 282:** the chain has as many levels as the longest side allows, or one level when `GenerateMips` is off.
2. **Lines 286–287:** a normal map is made unit length before its first level is encoded.
3. **Lines 293–295:** the current level is encoded and stored first.
4. **Lines 299–303:** after a check of the cancel flag, the next level is filtered from the current one.
5. **Line 306:** the next level replaces the current one, so the old texels are freed: two levels exist at most.

The loop encodes the current level, filters it into the next, and drops the current one. Only two levels of texels exist at a
time: the one being encoded and the one being built. A level has a quarter of the texels of the one before, so the cook never
holds more than a quarter above level 0, however long the chain is.

Sizes follow `Halve`: each side divides by two and rounds down, never below 1. That agrees with the file layout's
`Width >> level`.

The settings that shape the filter come from `Decode`. `SRGB` is on for color, so that stb converts to linear light before the
mean and back after; averaging the stored values would darken every level. `AlphaWeighted` is on when color has partly
transparent texels. The wrap mode becomes the edge mode, so a repeating texture filters across its own seam. `NormalMap` makes
every level unit length again, because an average of two :term[unit vectors]{id=unit-vector} is shorter than one.

`EncodeLevel` does the heavy part in parallel. It splits a level into batches of block rows and gives them to
`JobSystem::ParallelFor` at background priority, so the helpers never take processors from the frame. It checks the cancel
flag before every block. A block of `BC7` takes tens of microseconds, and the flag costs nothing beside that, so a cancelled
cook stops within one block's work.

### The HDR path

An HDR image goes through `CookHDRLevels` instead. There the filter is a box filter, a plain mean of the 2 by 2 texels below,
because a sharper filter rings around a bright sun into negative light. The code first clamps every value to the range that a
half float can hold. It also drops values that are not numbers, which some programs write and which filtering would spread
over the chain.

```cpp src="Strata/src/Strata/Asset/TextureCooker.cpp#L321-L325" from="// Clamp to the half-float range" to="for (uint32_t level = 0; level < mipCount; level++)" symbol="CookHDRLevels"
// Clamp to the half-float range and drop NaN and negative values some HDR encoders produce, before filtering spreads
// them.
for (float& value : current.Pixels)
	value = std::isfinite(value) ? std::clamp(value, 0.0f, 65504.0f) : 0.0f;
for (uint32_t level = 0; level < mipCount; level++)
```

The largest half float is 65,504, and the smallest value kept is 0. Each level is then packed into 16-bit values and stored as
`RGBA16F`, with no block compression, which is what the :term[inactive reason]{id=inactive-reason} of `Compression` says.

### Encoding blocks with `BC7Encoder`

A `BC7` block holds 16 texels in 128 bits, which is 8 bits a texel. A block has one, two or three groups of texels. For each
group it stores two **endpoints**, the colors at the two ends of a line, and for each texel an index that says how far along
the line the texel's color lies.

The format has eight modes. A mode fixes how many groups a block has, how many bits an end color's channels get and how many
bits an index gets. Modes 0 to 3 and 7 split the block into two or three groups by one of up to 64 partitions, which are fixed
patterns of which texels belong together.

Modes 4 and 5 keep one group but store alpha with its own indices, after swapping alpha with another channel (a rotation).
Mode 6 has one group, 7-bit endpoints and 16 levels. A p-bit is an extra lowest bit that a mode appends to the stored values
of an end color, or shares it between two of them. It buys one more bit of precision for one bit of storage.

The encoder is Strata's own, written from the format's definition (the layout is in `BC7Format.h`, which the decoder
shares). Every candidate encoding of a block is made the same way. The encoder takes a group's texels and finds their
principal axis, the line along which they spread most.

The extreme texels along that line give first endpoints, which are rounded to the mode's precision, with the p-bits chosen to
land nearest. Each texel takes the index of the nearest color on the line. Then the endpoints are fitted again by least
squares to those indices, as long as the error falls. The other combinations of p-bits are tried on the best result, and the
error is the sum of the squared differences of all four channels.

:::derivation
Take four texels with two channels (red, green): (10, 20), (50, 40), (90, 60) and (130, 80). Their mean is (70, 50).
Subtract it from each texel to get offsets such as (-60, -30). The spread along a direction is the sum of the squared lengths
of the offsets in that direction, and the encoder wants the direction of greatest spread.

The encoder finds it by repeated multiplication. It sums the products of the offsets into a table: red times red, red times
green, green times green.

The encoder starts from the table's column with the largest diagonal entry, multiplies it by the table,
scales it back to a length near one and repeats. Here the table holds 8000, 4000 and 2000, so the first vector is (8000, 4000).
Its direction (1, 0.5) is already right, because the texels lie on a line. The two ends along it are the endpoints (10, 20) and (130, 80).

Least squares then adjusts the endpoints once the indices are known. It picks the endpoints that minimize

$$E = \sum_i \left| (1 - t_i)\, e_0 + t_i\, e_1 - x_i \right|^2$$

$E$ is the error, in squared color steps. $i$ counts the texels of the group. $t_i$ is the weight of the texel's index, between
0 and 1. $e_0$ and $e_1$ are the two endpoints, and $x_i$ is the texel's true color. The bars give the length of a difference.
:::

The 2-bit weights of `BC7` are 0, 21, 43 and 64 sixty-fourths. With endpoints 10 and 130 in red, the four colors on the line
are 10, 49.4, 90.6 and 130. The texels 10, 50, 90 and 130 take indices 0, 1, 2 and 3, with a total squared error in red of about 0.8.
The second fit finds little to gain, and the search stops. This is the limit case: texels on a line cost almost nothing, and
the search spends its time on blocks that do not lie on one.

```cpp src="Strata/src/Strata/Asset/BC7Encoder.cpp#L460-L481" from="const uint8_t* weights = BC7::GetWeights(format.IndexBits);" to="const float determinant = firstFirst * secondSecond - firstSecond * firstSecond;" symbol="FitSubset"
const uint8_t* weights = BC7::GetWeights(format.IndexBits);
for (uint32_t refinement = 0; refinement < effort.Refinements && best.Error > 0; refinement++)
{
	float firstFirst = 0.0f;
	float firstSecond = 0.0f;
	float secondSecond = 0.0f;
	float firstTarget[C] = {};
	float secondTarget[C] = {};
	for (uint32_t texel = 0; texel < points.Count; texel++)
	{
		const float second = static_cast<float>(weights[best.Indices[texel]]) * (1.0f / 64.0f);
		const float first = 1.0f - second;
		firstFirst += first * first;
		firstSecond += first * second;
		secondSecond += second * second;
		for (uint32_t channel = 0; channel < C; channel++)
		{
			firstTarget[channel] += first * static_cast<float>(points.Values[texel][channel]);
			secondTarget[channel] += second * static_cast<float>(points.Values[texel][channel]);
		}
	}
	const float determinant = firstFirst * secondSecond - firstSecond * firstSecond;
```

1. **Line 460:** the weights of the mode's index bits, in sixty-fourths from 0 to 64.
2. **Line 461:** the fit repeats as often as the effort allows, and stops once the error is zero.
3. **Lines 470–471:** a texel's weight toward the second end color, and the rest toward the first.
4. **Lines 472–478:** sums of products of the weights, and of the weights with the texels: the two sides of the equations.
5. **Line 481:** the determinant of the two equations, zero when they say the same thing: every texel has one weight, so nothing can be fitted.

The quality setting decides how much of this work the encoder does. At `High`, it screens candidates cheaply, with their first
endpoints rounded once. It tries mode 6, modes 4 and 5 in the rotation that looks best, and, for each mode with partitions,
the best two partitions by an estimate of their error (one for mode 0).

The search then fits the two best candidates and mode 6 in full, with three more fits and every p-bit combination, so a block never ends
worse than mode 6 alone. Once a candidate has an error of at most one squared step per texel, the modes with partitions are
skipped.

`Fast` fits mode 6, and mode 5 when the block's alpha varies, with one more fit. A block whose texels are all the same goes to
mode 5, which can store any color exactly.

Two properties matter to a caller. The encoder is :term[deterministic]{id=determinism}: the same texels and settings give the same block on every
thread, which is what lets a cook give the same bytes with and without worker threads. It is also thread-safe, because each
call writes only its own block.

### Removing the sun

When `RemoveSun` is on for an HDR image, `Decode` calls the sun finder before the scaling and the clamp, because both would
spread or cut what the sun gives. What `HDRSun` finds, and how it paints the sun out, is the subject of
[Sky](../light/sky.md). Here it is enough to know that it works on the floats of the full-size image and reports a failure to
find a sun as a warning.

```cpp src="Strata/src/Strata/Asset/TextureImporter.cpp#L537-L544" from="if (settings.RemoveSun)" to="outWarnings->push_back" symbol="TextureImporter::Decode"
if (settings.RemoveSun)
{
	const std::span<float> pixels(decoded.get(), static_cast<size_t>(sourceWidth) * sourceHeight * 4);
	std::string reason;
	if (const std::optional<HDRSun::Sun> sun = HDRSun::Find(pixels, sourceWidth, sourceHeight, &reason))
		HDRSun::Remove(pixels, sourceWidth, sourceHeight, *sun);
	else if (outWarnings)
		outWarnings->push_back(fmt::format("Remove Sun found no sun to remove: {}", reason));
```

The warning says that Remove Sun found no sun to remove, and the cook continues. The scene's directional light then gives the
sun's light instead, which is the lighting side of the setting.

### The stored form of an STTX file

The comment above the format spells out the layout, and the figure shows it.

```cpp src="Strata/src/Strata/Renderer/CookedTexture.h#L17-L31"
// The cooked texture format ("STTX"), the stored form of texture assets in the import cache and in packs.
//
// Version 2 (written since texture cooking v2), little-endian:
//
//   CookedTextureHeader   magic "STTX", version, format, width, height, mip count, flags, filter, wrap, name length,
//                         data offset (where the first level's pixels start)
//   mip table             per level, largest (level 0) first: width, height, offset, size (offsets from the start)
//   debug name            UTF-8, name length bytes
//   padding               to the data offset, a multiple of c_CookedTextureAlignment
//   pixel data            the levels smallest first, each at a multiple of c_CookedTextureAlignment: the mip tail is
//                         one contiguous range right after the header, so streaming can read it (and later the
//                         larger levels) by byte range
//
// Block-compressed levels hold whole 4x4 blocks (GetMipByteSize). Version 1 (uncompressed formats, levels largest first
// right after their table) is still read: packs exported before version 2 contain it.
```

1. **Lines 21–23:** the header names the format, the size, the mip count and the data offset; the mip table lists every level,
   largest first, with its offset and size.
2. **Lines 25–28:** padding reaches the data offset, and the pixel data lies smallest level first, so the mip tail is one range.
3. **Lines 30–31:** version 1 is still read, because packs exported before version 2 hold it.

::figure{id=sttx-layout}

The header is 40 bytes and each table entry 24 (width, height, offset and size). Putting the small levels first has one
purpose. The mip tail, which a texture needs before anything else can be drawn, is a single range right after the header. A
streamer reads it with one request and fetches finer levels later, by their offsets in the table.

```cpp src="Strata/src/Strata/Renderer/CookedTexture.cpp#L339-L360" symbol="ComputeCookedTextureLayout"
CookedTextureLayout ComputeCookedTextureLayout(const CookedTextureDescription& description)
{
	CookedTextureLayout layout;
	if (!IsValidDescription(description.Format, description.Width, description.Height, description.MipCount))
		return layout;

	const size_t nameLength = std::min<size_t>(description.DebugName.size(), c_MaxCookedTextureNameLength);
	layout.Format = description.Format;
	layout.MipCount = description.MipCount;
	layout.HeaderSize = AlignUp(sizeof(CookedTextureHeader) + description.MipCount * sizeof(CookedMipEntry) + nameLength, c_CookedTextureAlignment);
	uint64_t offset = layout.HeaderSize;
	for (uint32_t level = description.MipCount; level-- > 0;)
	{
		CookedTextureLevel& entry = layout.Levels[level];
		entry.Width = std::max(1u, description.Width >> level);
		entry.Height = std::max(1u, description.Height >> level);
		entry.Offset = offset;
		entry.Size = GetMipByteSize(description.Format, entry.Width, entry.Height);
		offset = AlignUp(offset + entry.Size, c_CookedTextureAlignment);
	}
	return layout;
}
```

1. **Lines 342–343:** an invalid description gives an empty layout, so callers never see half a layout.
2. **Line 348:** the header, the table and the name are rounded up to the alignment: this is where the pixel data starts.
3. **Line 350:** the loop counts down from the last level, which is the smallest, so the smallest level gets the lowest offset.
4. **Lines 353–354:** a level's sides are the first level's sides shifted right, never below 1.
5. **Lines 355–357:** the offset, the size from `GetMipByteSize` and the next offset, rounded up to 16.

Writing a file and parsing it use the same description, so the offsets cannot drift apart.

:::example[A 300 by 200 albedo, level by level]
A color image of 300 by 200 texels with the default settings is `BC7SRGB`. The longest side, 300, halves down to 1 in nine
levels. They are 300 by 200, 150 by 100, 75 by 50, 37 by 25, 18 by 12, 9 by 6, 4 by 3, 2 by 1 and 1 by 1. Each rounds up to blocks of
4 and multiplies by 16 bytes.

Level 0 has 75 by 50 blocks and takes 60,000 bytes, level 1 takes 15,200, level 2 takes 3,952.
Level 3 takes 1,120, level 4 takes 240 and level 5 takes 96. Levels 6, 7 and 8 take 16 each.

With a name of 8 bytes, the header, the table and the name take 40 + 9 × 24 + 8 = 264 bytes, which rounds up to a data offset
of 272. Level 8 lies at 272, level 7 at 288, level 6 at 304, level 5 at 320, level 4 at 416, level 3 at 656 and level 2 at 1,776.
Level 1 lies at 5,728 and level 0 at 20,928. Level 0 ends at 80,928.

The levels of at most 128 texels a side are levels 2 to 8. They fill the bytes from 272 to 5,728, so a first read of 5,728
bytes out of 80,928 gives the texture something to show.
:::

### Block sizes

The size of a level is where code goes wrong first, so the arithmetic lives in one function.

```cpp src="Strata/src/Strata/Renderer/TextureFormat.cpp#L53-L59" symbol="GetMipByteSize"
uint64_t GetMipByteSize(TextureFormat format, uint32_t width, uint32_t height)
{
	const TextureFormatInfo info = GetTextureFormatInfo(format);
	const uint64_t blocksX = (static_cast<uint64_t>(width) + info.BlockWidth - 1) / info.BlockWidth;
	const uint64_t blocksY = (static_cast<uint64_t>(height) + info.BlockHeight - 1) / info.BlockHeight;
	return blocksX * blocksY * info.BytesPerBlock;
}
```

Each side is divided by the block's side with rounding up, which is the `+ BlockWidth - 1` before the division. The block
counts are then multiplied by the bytes of a block. For formats without compression a block is one texel, so the same line serves
them. A 2 by 2 `BC7` level is one block of 16 bytes. Counting levels with bytes per texel would give 4, and every later offset
would be wrong.

### Reading it back

`ParseCookedTexture` is the only door in. It reads either version and checks the format and the size of every level (whole
blocks). It checks that the offsets lie inside the data, that the levels do not overlap and that version 2 stores them
smallest first. It returns a view that points into the bytes with nothing copied, or an error with the reason.

A prefix form, `ParseCookedTexturePrefix`, checks the first bytes of a version 2 file against the stored size. A first load
then reads only the header and the mip tail.

### Devices without block compression

Not every GPU samples block formats. The :term[renderer]{id=renderer} keeps one flag, `Texture::IsBlockCompressionSupported`, and the texture
loader registered by the renderer module checks it. When a loaded texture is block-compressed and the flag is false, the
loader calls `Texture::Decompress` on the loading worker.

That function runs the decoders of `BlockCompression` and returns levels in a format without compression, with the same channels:
four for `BC1`, `BC3` and `BC7`, one for `BC4` and two for `BC5`. The decoders were written from the formats' specifications,
and `BC7` decodes exactly. The :term[main thread]{id=main-thread} never waits for it. The decoded texture takes more memory, which is the cost of the
fallback.

### When the usage disagrees with the slot

A texture imported with the wrong usage looks wrong in a quiet way. A roughness map imported as color is sRGB-decoded, and a
normal map imported as color gives wrong normals. The editor checks each texture a material uses against its slot
(`FindTextureUsageMismatches`) and reports a disagreement with a message and a fix.

The fix is the command `asset.setImportSettings` with the usage that the slot expects. Slots that read color complain only
about normal maps and data.

### What Strata does not do here

Two things are absent at the pin. HDR textures stay `RGBA16F` because the encoder has no `BC6H`, so a sky takes 8 bytes a
texel. The importer reads no `.exr` files, only the eight extensions of the contract.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| An existing `BC7` encoder library | Many engines and tools; the first entries of Further reading | Years of tuning, and faster encoding on some machines | A dependency to track, and bytes that change when the library does, which the same-bytes tests forbid |
| A compressed intermediate file, such as Basis Universal in `KTX2` | Engines that ship to many kinds of device | One small file that turns into each device's format | A conversion step at load and some lost quality, where Strata already decodes blocks on the worker |
| `BC6H` for HDR | Engines that ship skies and light probes in block form | One byte a texel instead of eight for a sky | An encoder to write and test, and an HDR format with its own artifacts |
| A sharper mip filter, such as Kaiser | Texture tools that run outside the game | Crisper small levels | Ringing into negative light on HDR, and more care on every level |

## How it is tested

The suite `Asset.TextureImport` covers the importer. Its cases check that the stored format follows the usage, the channels
and the alpha, and that mips are filtered in the texture's color space with its edges and alpha. They check that block
compression keeps color close to the source, that data channels stay apart and that `BC5` normals stay within two degrees.

Other cases check that cooking gives the same bytes on every run, with and without worker threads, and that a cancelled cook
stops and fails as cancelled. More check that names choose the usage by their tokens, and that `FlipGreen` inverts the green
channel before the mips. The suite `Asset.HDRSun` checks the sun finder.

The encoder's own tests are in `Renderer.BlockCompression`: blocks that force each mode, flat colors stored exactly, and a
check that the encoder never picks a worse mode than mode 6. Back in `Asset.TextureImport`, the color case measures the peak
signal-to-noise ratio (PSNR) of the decoded result against the source. It demands at least 40 :term[dB]{id=decibel} for `BC7` at `High` and at least 36 dB at `Fast`,
and it prints the measured values. Run the suite with the test binary:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.TextureImport
```

The command runs the importer's suite. Select the case "Block compression keeps color close to the source" with
`--test-case` to read the PSNR lines in its messages.

## Changing it safely

Three extension points exist: a new usage or setting in `TextureImportSettings` and `TextureImporter`, a new stored format in
`ChooseFormat` and the cooker's `CanEncode`, and a new mode of work in the encoder. Each follows the same rules, and each rule
has a reason.

- A change to what the cook writes bumps `GetVersion()` of `TextureImporter` and of `GltfImporter`, so that no cache entry
  keeps the old bytes. The version is 5 at the pin.
- A new setting gets an entry in `GetSettingsProperties` and, where another setting can disable it, an inactive reason.
- New code reads and writes sizes with `GetMipByteSize` and cooked bytes with `ParseCookedTexture`, for the reasons the
  contract gave.
- Cooking stays deterministic and able to stop: check the flag between levels and between blocks, and keep the same bytes with
  and without worker threads.
- Add a regression test that fails without the change, and keep `Asset.TextureImport` and `Renderer.BlockCompression` green.

## Summary

- A cook encodes one level, then filters the next from it, so only two levels of texels are in memory at a time.
- The stored format follows the usage, the channels, the alpha and the quality: color is `BC7` or `BC1`, normals `BC5`, one-channel data `BC4`, other data `BC7` and HDR `RGBA16F`.
- A level's size and offset come from `GetMipByteSize` and `ComputeCookedTextureLayout`: whole blocks, smallest level first, 16-byte aligned.
- The `BC7` encoder fits endpoints along the principal axis of the block's colors, fits them again by least squares and keeps the candidate with the least error.
- The tokens of a file name choose the usage, and on a normal map `dx` turns `FlipGreen` on.

## Check yourself

1. A project holds `Wood_rough.png`, a gray image with one channel, imported with the defaults and with Quality set to `Fast`. Which format is stored: `BC1SRGB`, `BC4`, `BC7` or `BC5`?

   :::answer{tests="format-choice"}
   `BC4`. The tokens make it data, and data with one channel is `BC4` at either quality. `BC1SRGB` is what `Fast` gives to opaque color, but this is data. `BC7` is the choice for data with more channels, and `BC5` is for normal maps.
   :::

2. How many bytes does a `BC7` level of 5 by 5 texels take, and why not 25?

   :::answer{tests="mip-sizes"}
   64 bytes. The 5 sides round up to 2 blocks each, and 2 × 2 blocks × 16 bytes is 64. The count of 25 treats the format as one byte a texel, but `BC7` stores whole blocks, so an edge block costs as much as a full one.
   :::

3. Which usage and settings does `Rock_2k_NormalDX.png` get by default?

   :::answer{tests="name-defaults"}
   The tokens are `rock`, `2k`, `normal` and `dx`. The importer drops `2k` and `dx` from the usage test, keeps `normal`, and so chooses `NormalMap`. The `dx` token also turns `FlipGreen` on.
   :::

4. Why does the cook encode a level before filtering the next, instead of filtering all levels first? (a) Encoding is cheaper when it runs first. (b) The cook then holds two levels of texels instead of the whole chain. (c) A filter cannot read an encoded level.

   :::answer{tests="cooking-flow"}
   (b). Each level is encoded, the next is filtered from the same texels, and the old level is dropped. (a) is wrong: the cost of encoding does not depend on the order. (c) is wrong too: the filter reads the texels, never the encoded blocks.
   :::

5. Four texels lie on one line in color space. Does a least-squares fit of the endpoints, after the first one, help much?

   :::answer{tests="bc7-fit"}
   Very little. The first endpoints, the extremes along the principal axis, already fit the line, so the error is only what the indices lose by rounding. The second fit helps when the colors are scattered and the indices pick the wrong ends.
   :::

## Exercises

1. **Basic.** Write a program that prints the offset and size of every level of a 256 by 256 `BC7` texture with a 9-byte name, smallest level first.

   :::answer[Worked solution]{tests="mip-sizes" solution="sketches/assets-texture-cooking-layout.cpp"}
   The program follows `ComputeCookedTextureLayout`. It adds the 40-byte header, nine 24-byte table entries and the name, rounds up to 16, and then walks from level 8 down to level 0, rounding each next offset up.

   ```cpp sketch="assets-texture-cooking-layout.cpp"
   // Where a cooked texture of 256x256 texels in BC7 keeps its levels: header, mip table, name, then smallest first.
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>

   uint64_t AlignUp(uint64_t value, uint64_t alignment)
   {
   	return (value + alignment - 1) / alignment * alignment;
   }

   uint64_t GetBC7Size(uint32_t width, uint32_t height)
   {
   	return static_cast<uint64_t>((width + 3) / 4) * ((height + 3) / 4) * 16;
   }

   int main()
   {
   	const uint32_t size = 256;
   	const uint32_t mipCount = 9; // 256, 128, 64, 32, 16, 8, 4, 2, 1
   	const uint64_t nameLength = 9; // "Brick.png"
   	const uint64_t headerBytes = 40;
   	const uint64_t tableEntryBytes = 24;

   	const uint64_t dataOffset = AlignUp(headerBytes + mipCount * tableEntryBytes + nameLength, 16);
   	std::printf("pixel data starts at %llu\n", static_cast<unsigned long long>(dataOffset));

   	uint64_t offset = dataOffset;
   	for (uint32_t level = mipCount; level-- > 0;)
   	{
   		const uint32_t side = std::max(1u, size >> level);
   		const uint64_t bytes = GetBC7Size(side, side);
   		std::printf("level %u (%ux%u): offset %llu, size %llu\n", level, side, side, static_cast<unsigned long long>(offset),
   			static_cast<unsigned long long>(bytes));
   		offset = AlignUp(offset + bytes, 16);
   	}
   	std::printf("file ends at %llu\n", static_cast<unsigned long long>(offset));
   	return 0;
   }
   ```

   ```text output-of="assets-texture-cooking-layout.cpp"
   pixel data starts at 272
   level 8 (1x1): offset 272, size 16
   level 7 (2x2): offset 288, size 16
   level 6 (4x4): offset 304, size 16
   level 5 (8x8): offset 320, size 64
   level 4 (16x16): offset 384, size 256
   level 3 (32x32): offset 640, size 1024
   level 2 (64x64): offset 1664, size 4096
   level 1 (128x128): offset 5760, size 16384
   level 0 (256x256): offset 22144, size 65536
   file ends at 87680
   ```

   1. **Lines 6–9:** `AlignUp` rounds a number up to a multiple of the alignment.
   2. **Line 24:** the data offset is the header, the table and the name, rounded up to 16.
   3. **Line 28:** the loop counts down from the last level, so the smallest level comes first.
   4. **Lines 30–31:** a level's side is the first side shifted right, and its bytes follow from whole blocks.
   5. **Line 34:** the next offset starts at the end of this level, rounded up to 16.

   The pixel data starts at 272, and the level of 1 by 1 texel takes one block of 16 bytes. The mip tail, the levels up to 128 texels, ends at 22,144, where the 256 by 256 level begins.
   :::

2. **Medium.** Trace it yourself: find where the tokens of a file name choose the default settings, then say what happens to a normal map named `Brick_n_dx.png`.

   :::answer[Worked solution]{tests="name-defaults"}
   Search the engine for `GetNameTokens`. It lives in `Strata/src/Strata/Asset/TextureImporter.cpp`, and `TextureImportSettings::GetDefaults` calls it. The stem `Brick_n_dx` gives the tokens `brick`, `n` and `dx`. The `dx` token is dropped and sets the DirectX flag.

   The last token is `n`, so the usage is `NormalMap` and `FlipGreen` is on. The decode then inverts green before the mips are made. A material slot that reads color for such a texture would show the usage warning, with the fix `asset.setImportSettings`.
   :::

3. **Medium.** Find the test that measures the PSNR of `BC7` at `High` and at `Fast`, run it and read its messages.

   :::answer[Worked solution]{tests="bc7-fit"}
   The case is "Block compression keeps color close to the source" in `Asset.TextureImport`, in `StrataTests/src/Asset/TextureImportTests.cpp`. Run it with `--test-suite=Asset.TextureImport --test-case="Block compression keeps color close to the source"`. Its messages print the PSNR for the checker and the gradient, for `BC7` at `High`, `BC7` at `Fast`, `BC1` at `High` and the import at `Fast`, which is `BC1`. The case demands 40 dB at `High` and 36 dB at `Fast`, and that `High` is never worse than `BC1`.
   :::

4. **Hard.** Import a large albedo twice, once at `High` and once at `Fast`, and compare the look, the stored size and the import time.

   :::answer[Worked solution]{tests="format-choice cooking-flow"}
   For an opaque 4096 by 4096 albedo, `High` stores `BC7` and `Fast` stores `BC1`. Level 0 takes 16,777,216 bytes as `BC7` and 8,388,608 as `BC1`. The whole chain adds a third: about 22.4 million bytes against 11.2 million. Expect `Fast` to finish sooner, because `BC1` encoding does far less work than a search over the modes of `BC7`.

   Compare smooth gradients and the edges of strongly colored regions, where `BC1`, with each block's colors on one line, may show banding that `BC7` avoids. Measure the import time yourself, and set the quality through `asset.setImportSettings`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Asset/TextureImporter.h` and `TextureImporter.cpp`: the settings, `GetDefaults`, `GetNameTokens`, `Decode`, `ChooseFormat`.
- `Strata/src/Strata/Asset/TextureCooker.h` and `TextureCooker.cpp`: `CookLevels`, `CookHDRLevels`, `EncodeLevel`.
- `Strata/src/Strata/Asset/BC7Encoder.h` and `BC7Encoder.cpp`: the encoder; `Strata/src/Strata/Renderer/BC7Format.h`: the format's tables.
- `Strata/src/Strata/Asset/HDRSun.h` and `HDRSun.cpp`: the sun finder behind `RemoveSun`.
- `Strata/src/Strata/Renderer/CookedTexture.h` and `CookedTexture.cpp`: `STTX`, `ParseCookedTexture`, `ComputeCookedTextureLayout`.
- `Strata/src/Strata/Renderer/TextureFormat.cpp`: `GetMipByteSize`; `Strata/src/Strata/Renderer/BlockCompression.cpp`: the decoders.
- `StrataTests/src/Asset/TextureImportTests.cpp`, `StrataTests/src/Asset/HDRSunTests.cpp` and `StrataTests/src/Renderer/BlockCompressionTests.cpp`: the tests.
- The command `asset.setImportSettings`: changes a texture's settings.

## Further reading

- The Khronos Data Format Specification, section "BC7": the block format that the encoder and the decoder follow. Advanced.
- The ISPC Texture Compressor, bc7enc and Compressonator, open BC7 encoders to compare with. Advanced.
- Strang, G., *Introduction to Linear Algebra*: least squares and eigenvectors, the ideas of the derivation box. Intermediate.
- Mitchell and Netravali, "Reconstruction Filters in Computer Graphics" (1988): where the Mitchell filter comes from. Advanced.
- The documentation of the NVIDIA Texture Tools: mip filters such as Kaiser. Intermediate.
- The Basis Universal project and the KTX 2 specification: compressed intermediate texture files. Intermediate.
