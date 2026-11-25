---
id: image/grading
title: "White balance, grading and lookup tables"
description: "How Strata gives the image a white point and a grade on scene-linear light, and applies a lookup table made in another tool after the tone curve."
kind: internals
size: L
tracks: [E]
needs: [image/tone-mapping, assets/importing]
time: 80
learn:
  - id: wb-matrix
    text: explain how a temperature and a tint become one matrix, and what that matrix does to a gray patch
  - id: cdl-grade
    text: compute what slope, offset and power do to a pixel around middle gray
  - id: lut-read
    text: compute the texture coordinate and the trilinear weights of one lookup read
  - id: cube-import
    text: trace a .cube file from the importer to the frame and say when it first applies
  - id: grade-order
    text: choose whether a grade belongs on scene-linear light before the curve or on display values after it
since: 0.7.0
status: final
---

A rendered frame holds light, not colors that a screen can show, so before the :term[tone curve]{id=tone-mapping-image} squeezes it into display values Strata gives it a :term[white point]{id=white-point} and a grade. The white point lets a lamp-lit room look neutral or stay warm, and the grade is a slope, an offset and a power around :term[middle gray]{id=middle-gray}. After the curve, a lookup table from another tool can map every color. This page follows that work from the settings of the `PostProcess` component to the :term[shader's]{id=shader} lines, and through the :term[importer]{id=importer} that turns a `.cube` file into a texture. The curve belongs to [tone mapping](../image/tone-mapping.md), the encoding to [encoding](../image/encoding.md) and the editor's grading to [look](../make/look.md).

## The problem and how engines solve it

Put a camera in a room lit by one warm lamp. A person in the room sees white walls, because the eye adjusts to the lamp. A camera that does not adjust records orange walls, and so does a :term[renderer]{id=renderer}: it computes the light that reaches the lens, and that light is orange. The pictures below show one view at three settings of the control that fixes this, then at two settings of a second control.

::figure{id=white-balance-sweep variant=k3200}

::figure{id=white-balance-sweep variant=k6500}

::figure{id=white-balance-sweep variant=k9000}

::figure{id=white-balance-sweep variant=tint-minus}

::figure{id=white-balance-sweep variant=tint-plus}

### Naming the light

**White balance** is the step that names the color of the light that should look white, and scales the image so that this light does.

To name a light with one number, photographers use its **color temperature**: the temperature, in kelvin (K), of an ideal glowing body that sends light of the same color. A warm indoor lamp is near 3,200 K, and the standard daylight of :term[sRGB]{id=srgb} is 6,500 K. Low numbers are orange and high numbers are blue. Engines often count the inverse, in **mireds**: a million divided by the kelvin, so 3,200 K is 312.5 mireds and 6,500 K is 153.8. Equal steps in mireds change the cast by about equal amounts, which makes mireds the better axis for a table.

The color of a light, without its brightness, is a chromaticity, a point on the plane you know from [color](../basics/color.md). The International Commission on Illumination, the standards body of light and color, defined the plane in 1931 as the coordinates $x$ and $y$. In 1960 it defined a second plane, $u$ and $v$, in which equal distances look more equal. As temperature rises, the chromaticity of a glowing body draws a curve. The **Planckian locus** is that curve, computed from the light that an ideal glowing body radiates at each temperature.

Sky light is not a glowing body. The same body measured daylight and fitted a second curve, and the **daylight locus** is that curve, a little off the first. A white balance control needs one of them as its reference, and Strata uses the daylight locus at and above 5,000 K and the Planckian locus at and below 4,000 K.

### Adapting the image

Naming the light is half of the work. The other half is to change the image so that the named light turns neutral. The simplest way is to divide each of the red, green and blue (RGB) values by the light's own RGB. That is not an adaptation, and the reason is the eye.

In 1902 von Kries proposed that the eye adapts by scaling the response of each of its three cone types, long, medium and short, on its own. Doing the same on a screen means a change of axes: convert the colors to the commission's `XYZ` values, from which $x$ and $y$ come, then to cone-like responses. Scale each response by the target white over the light, and convert back. The chromatic adaptation transform of 2002 (CAT02) is a standard matrix that gives such responses. The primaries of a screen are far more saturated than any cone, so scaling them skews hues, and the toy below shows by how much.

### Grading and lookup tables

After the white point comes the grade. The film industry defined a color decision list (CDL) so that a grade made on one system moves to another. Per channel it has three numbers: a slope that multiplies, an offset that adds, and a power that raises the result to an :term[exponent]{id=exponent}. A grading tool can also keep a table instead of three numbers. A 3D lookup table holds a new color for a grid of input colors, so that any mapping of colors, including ones no formula describes, fits in one file.

A last question is where in the pipeline each tool works. On :term[scene-linear]{id=scene-linear} light a doubling is one stop of exposure, an offset adds light, and a power bends the tones around a gray. After the curve, the values are display codes, and the lookup tables that grading tools export were made while the artist watched a display. Strata therefore grades before the curve and applies the lookup after it, as the next section shows.

## The map

The color work sits in the tone-mapping pass, the last pass that still sees light. The diagram shows its order for one pixel. The first four steps run on scene-linear light, the next three turn that light into display values, and the lookup comes after the encoding.

```mermaid caption="The order of the color work in the tone-mapping pass: the grade on scene-linear light, the curve, saturation, the encoding, and last the lookup on display values." alt="A chain of boxes from scene-linear light to grain and dither. The first four boxes grade the light, the next three make display values, and the lookup comes after the encoding."
flowchart LR
  A[Scene-linear light] --> B[White balance and slope: one matrix]
  B --> C[Offset]
  C --> D[Power around middle gray]
  D --> E[Contrast]
  E --> F[Tone curve]
  F --> G[Saturation]
  G --> H[sRGB encoding]
  H --> I[Color lookup mixed in by intensity]
  I --> J[Grain and dither]
```

The lookup is a **3D LUT** (3D lookup table): an N by N by N grid of output colors, indexed by the red, green and blue of the input. Other names for it are a color lookup and, after its :term[file format]{id=file-format}, a `.cube`. Six pieces make the work happen.

- `Strata/src/Strata/Renderer/PostProcessMath.cpp` builds the white balance matrix and the grading.
- `Strata/src/Strata/Renderer/WhiteBalanceLocus.inl` holds the locus table, written by `Tools/GenerateWhiteBalance.py`.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp` fills the pass's constants and resolves the lookup each frame.
- `Strata/shaders/PostProcess/Tonemap.frag.slang` runs the grading and the lookup for every pixel.
- `Strata/src/Strata/Asset/ColorLookupImporter.cpp` reads `.cube` files in a background import job.
- `Strata/src/Strata/Renderer/ColorLookup.cpp` holds the asset: its cooked form and its :term[graphics processing unit]{id=gpu} (GPU) texture, made on the :term[main thread]{id=main-thread}.

## The contract

The pass obeys five rules. Each has a reason that a change must keep.

1. Neutral settings render bit-identically. The defaults, 6,500 K, tint 0, slope 1, offset 0, power 1 and no lookup, must give the same pixels as a pass without the code. The grading has an `Active` flag, and when it is false the shader skips the whole block. A lookup at intensity 0 is skipped too. Every pixel takes the same branch, so a skipped branch costs nothing, and games that never grade keep their images.
2. The grade comes before the curve, the lookup after it. The grade works on scene-linear light around middle gray, 0.18, and the lookup works on the encoded values it was made for. :term[Saturation]{id=saturation} stays after the curve.
3. Inputs are clamped, never trusted. Strata clamps a temperature to 2,000 to 15,000 K, a slope to 0 to 4, an offset to -0.1 to 0.1, a power to 0.2 to 5 and a tint to -1 to 1. A value that is not finite becomes its default.
4. A lookup that loads never blocks and never changes the bindings. Nothing applies until the asset is loaded and uploaded. While it loads, the frame counts it as pending, and the pass binds dummy textures in its place.
5. A `.cube` file is untrusted text. The importer refuses a bad file with its line number and the reason, and it stops when the import is cancelled.

:::rule
No frame may wait for an asset: a pass skips what has not loaded, or draws a stand-in. The lookup obeys that twice: the frame draws without the grade until the table is there, and the :term[binding set]{id=binding-set} never waits for it. See [loading](../assets/loading.md) for the general rule.
:::

## A toy version

:::question
The code uses functions, `glm` calls and `const` references: where do I learn them? Read [functions](../basics/programming-2.md), [classes and calls](../basics/programming-3.md) and [templates](../basics/cpp-generic.md) first.
:::

In the CDL, the **slope** is the factor that multiplies a channel, the offset is the number added to it, and the power is the exponent applied last.

The toy shows the two ideas with real numbers. `MakeAdaptation` builds a von Kries adaptation in CAT02's cone space for a light given by its chromaticity. `ScaleRGB` is the shortcut, dividing the channels by the light's RGB.

`ApplyCDL` is the grade, with the offset in fractions of middle gray as Strata has it. The program uses the 3,200 K lamp of the pictures: its chromaticity on the Planckian locus is $x = 0.4234$, $y = 0.3990$. Read the lines of `main` and predict whether the lamp's white turns to (1, 1, 1).

```cpp sketch="image-grading-toy.cpp"
#include <glm/glm.hpp>

#include <cstdio>

namespace
{
	// Linear sRGB to XYZ, and CAT02's matrix from XYZ to cone responses (rows as published; glm is column-major).
	const glm::dmat3 c_SRGBToXYZ = glm::transpose(glm::dmat3(0.4124564, 0.3575761, 0.1804375, 0.2126729, 0.7151522, 0.0721750, 0.0193339, 0.1191920, 0.9503041));
	const glm::dmat3 c_CAT02 = glm::transpose(glm::dmat3(0.7328, 0.4296, -0.1624, -0.7036, 1.6975, 0.0061, 0.0030, 0.0136, 0.9834));
	const glm::dvec2 c_D65 = { 0.3127, 0.3290 };

	glm::dvec3 XYToXYZ(const glm::dvec2& xy)
	{
		return glm::dvec3(xy.x / xy.y, 1.0, (1.0 - xy.x - xy.y) / xy.y);
	}

	// Von Kries: scale each cone response by (response of the target white) / (response of the light), then return to RGB.
	glm::dmat3 MakeAdaptation(const glm::dvec2& lightXY)
	{
		const glm::dvec3 gains = (c_CAT02 * XYToXYZ(c_D65)) / (c_CAT02 * XYToXYZ(lightXY));
		const glm::dmat3 scale(gains.x, 0.0, 0.0, 0.0, gains.y, 0.0, 0.0, 0.0, gains.z);
		return glm::inverse(c_SRGBToXYZ) * glm::inverse(c_CAT02) * scale * c_CAT02 * c_SRGBToXYZ;
	}

	// The shortcut: divide each RGB channel by the light's own RGB. The sRGB primaries stand in for cones.
	glm::dvec3 ScaleRGB(const glm::dvec2& lightXY, const glm::dvec3& color)
	{
		return color / (glm::inverse(c_SRGBToXYZ) * XYToXYZ(lightXY));
	}

	// The ASC CDL around middle gray: the offset is in fractions of middle gray, as in Strata.
	glm::dvec3 ApplyCDL(const glm::dvec3& color, const glm::dvec3& slope, const glm::dvec3& offset, const glm::dvec3& power)
	{
		const glm::dvec3 shifted = glm::max(color * slope + offset * 0.18, glm::dvec3(0.0));
		return 0.18 * glm::pow(shifted / 0.18, power);
	}

	void Print(const char* label, const glm::dvec3& color)
	{
		std::printf("%-26s %.4f %.4f %.4f\n", label, color.x, color.y, color.z);
	}
}

int main()
{
	const glm::dvec2 tungsten(0.4234, 0.3990); // The light of a 3200 K lamp, on the Planckian locus.
	const glm::dmat3 adaptation = MakeAdaptation(tungsten);
	const glm::dvec3 lamp = glm::inverse(c_SRGBToXYZ) * XYToXYZ(tungsten);
	const glm::dvec3 orange(0.8, 0.3, 0.05);
	Print("lamp white", lamp);
	Print("lamp white, adapted", adaptation * lamp);
	Print("gray 0.18, adapted", adaptation * glm::dvec3(0.18));
	Print("orange, von Kries", adaptation * orange);
	Print("orange, RGB scaling", ScaleRGB(tungsten, orange));
	Print("CDL slope 2", ApplyCDL(glm::dvec3(0.18, 0.36, 0.72), glm::dvec3(2.0), glm::dvec3(0.0), glm::dvec3(1.0)));
	Print("CDL offset 0.05", ApplyCDL(glm::dvec3(0.0, 0.18, 0.72), glm::dvec3(1.0), glm::dvec3(0.05), glm::dvec3(1.0)));
	Print("CDL power 1.2", ApplyCDL(glm::dvec3(0.045, 0.18, 0.72), glm::dvec3(1.0), glm::dvec3(0.0), glm::dvec3(1.2)));
	return 0;
}
```

```text output-of="image-grading-toy.cpp"
lamp white                 1.6796 0.8660 0.3256
lamp white, adapted        0.9998 1.0000 1.0002
gray 0.18, adapted         0.0673 0.2045 0.4706
orange, von Kries          0.5247 0.3509 0.2042
orange, RGB scaling        0.4763 0.3464 0.1536
CDL slope 2                0.3600 0.7200 1.4400
CDL offset 0.05            0.0090 0.1890 0.7290
CDL power 1.2              0.0341 0.1800 0.9500
```

1. **Line 9:** the CAT02 matrix, which turns `XYZ` values into cone-like responses.
2. **Line 20:** the gains: the target white's cone responses divided by the light's.
3. **Line 22:** the whole adaptation as one matrix: to `XYZ`, to cones, scale, and back.
4. **Line 28:** the shortcut: each channel divided by the light's own value.
5. **Lines 34–35:** the grade: slope and offset first, then the power around middle gray.

The lamp's white, (1.6796, 0.8660, 0.3256) in linear sRGB, becomes (1, 1, 1) within 0.0002. A gray of 0.18 becomes (0.0673, 0.2045, 0.4706): the gray surface under the lamp is orange, so the correction turns it blue. Now compare the orange patch. The von Kries result has a blue value of 0.2042, and the shortcut gives 0.1536, a quarter less, so the shortcut makes the patch more saturated than the cones would.

:::example[The grade by hand]
Take a gray of 0.18 and a darker value of 0.045, two stops below it, and apply a power of 1.2. The value 0.18 divided by middle gray is 1, and 1 raised to any power is 1, so middle gray stays at 0.18. The dark value divided by middle gray is 0.25, and $0.25^{1.2}$ is 0.1895, so the result is $0.18 \cdot 0.1895 = 0.0341$. A bright value of 0.72 is 4 times middle gray, $4^{1.2}$ is 5.278, and the result is 0.950. The power pivots on middle gray: darks go down and brights go up.

An offset of 0.05 adds $0.05 \cdot 0.18 = 0.009$ to every value, black included, and a slope of 2 doubles 0.18, 0.36 and 0.72 to 0.36, 0.72 and 1.44. The last three lines of the output say the same.
:::

The adaptation is the product of five matrices. The paragraph after the formula names them.

$$M = T^{-1}\, C^{-1}\, D\, C\, T$$

Here $M$ is the matrix that applies to linear sRGB colors, and $T$ turns linear sRGB into `XYZ`. $C$ is CAT02, which turns `XYZ` into cone responses, and $D$ is the diagonal matrix of the three gains, which multiplies each response by its own gain and mixes none of them. The product reads right to left, because the matrix nearest the color acts first. That order is $T$, then $C$, then $D$, then the two inverses. With the gains of line 20, a light equal to the target gives gains of 1, so $D$ and $M$ are the identity.

## The real code

### White balance in double

`GetWhiteBalanceMatrix` does what the toy does, with two differences. It finds the light's chromaticity from a temperature and a tint instead of taking it as given, and it computes in double precision, because the gains divide numbers that are close. The quote shows the body of the function. Search for the early return, the locus and the product of matrices.

```cpp src="Strata/src/Strata/Renderer/PostProcessMath.cpp#L165-L175"
if (kelvin == 6500.0f && tint == 0.0f)
	return glm::mat3(1.0f);
const glm::dvec4 locus = GetWhiteLocus(std::clamp(static_cast<double>(FiniteOr(kelvin, 6500.0f)), 2000.0, 15000.0));
const double shift = 0.02 * std::clamp(static_cast<double>(FiniteOr(tint, 0.0f)), -1.0, 1.0);
const glm::dvec2 light = glm::dvec2(locus.x, locus.y) + shift * glm::dvec2(locus.z, locus.w);
const glm::dvec3 lightCones = c_CAT02 * XYToXYZ(UVToXY(light));
const glm::dvec3 referenceCones = c_CAT02 * XYToXYZ(c_D65);
const glm::dvec3 gains = referenceCones / lightCones;
const glm::dmat3 toXYZ = GetSRGBToXYZ();
const glm::dmat3 scale(gains.x, 0.0, 0.0, 0.0, gains.y, 0.0, 0.0, 0.0, gains.z);
return glm::mat3(glm::inverse(toXYZ) * glm::inverse(c_CAT02) * scale * c_CAT02 * toXYZ);
```

1. **Line 165:** the default pair, 6,500 K and tint 0, returns the :term[identity matrix]{id=identity-matrix} exactly, so the neutral case is bit-identical by construction.
2. **Line 167:** the temperature is made finite and clamped, and `GetWhiteLocus` returns the chromaticity and the normal of the locus at that temperature: the direction perpendicular to the curve there.
3. **Line 168:** the tint is clamped to -1 to 1 and scaled by 0.02, the distance in $u$ and $v$ that a full tint moves the light.
4. **Line 172:** the gains are the same ratio as the toy's line 20.
5. **Line 175:** the matrix is $T^{-1} C^{-1} D C T$ as in the formula, rounded to single precision only at the end.

A **tint** is a second axis for the named light: it moves the light's chromaticity along the normal of the locus, which points toward green. A positive tint names a greener light, so the correction adds magenta, and a negative tint adds green. Strata moves the light by 0.02 in $(u, v)$ per unit, so tint 1 is a shift of 0.02. The table gives what the matrix does to a gray of 0.18, computed from the engine's locus table with the toy's method.

| Setting | Light named, in mireds | Gray 0.18 becomes (red, green, blue) |
| --- | --- | --- |
| 3,200 K, tint 0 | 312.5 | 0.067, 0.205, 0.470 |
| 4,500 K, tint 0 | 222.2 | 0.131, 0.188, 0.277 |
| 9,000 K, tint 0 | 111.1 | 0.207, 0.178, 0.135 |
| 6,500 K, tint -1 | 153.8 | 0.129, 0.200, 0.145 |
| 6,500 K, tint +1 | 153.8 | 0.226, 0.163, 0.225 |

A low temperature turns the gray blue, a high one turns it orange, a negative tint turns it green and a positive tint turns it magenta, as the pictures at the start showed. The tests check these directions. They also check that at every temperature and tint the light the setting names comes out neutral, to within a thousandth of the green value.

### The locus

`GetWhiteLocus` reads a table of 91 entries, one every 5 mireds from 60 to 510, which is 16,667 K down to 1,961 K. Each entry holds the locus's $(u, v)$ and its unit normal toward green. The function converts the kelvin to mireds, clamps it into the table, finds the two entries around it and mixes them linearly in mireds. The mix of the normals is made a :term[unit vector]{id=unit-vector} again.

A script writes the table, so that nobody types 91 rows by hand and the source of every number is known. `Tools/GenerateWhiteBalance.py` integrates the light of a glowing body against the 1931 color matching functions for temperatures at and below 4,000 K, 250 mireds. It uses the standard daylight formula at and above 5,000 K, 200 mireds. Between them it blends the two linearly in mireds, so the curve has no jump. At 4,500 K, 222.2 mireds, the entry is 44 % of the way from the daylight value to the glowing body's.

The script also shifts the daylight part by the small gap between the formula and the listed white of sRGB, at most 0.00005 in $(u, v)$. Then 6,500 K is exactly that white, and the default stays an exact identity.

### Slope, offset and power

`MakeColorGrading` joins the white balance and the CDL into one structure. The quote omits the clamps of the first lines, which follow the ranges of rule 3.

```cpp src="Strata/src/Strata/Renderer/PostProcessMath.cpp#L190-L200"
const float temperature = std::clamp(FiniteOr(kelvin, 6500.0f), 2000.0f, 15000.0f);
const float clampedTint = std::clamp(FiniteOr(tint, 0.0f), -1.0f, 1.0f);
// Slope scales the white-balanced channels: diag(slope) * M.
const glm::mat3 whiteBalance = GetWhiteBalanceMatrix(temperature, clampedTint);
const glm::mat3 slopeMatrix(clampedSlope.x, 0.0f, 0.0f, 0.0f, clampedSlope.y, 0.0f, 0.0f, 0.0f, clampedSlope.z);
grading.Matrix = slopeMatrix * whiteBalance;
grading.Offset = clampedOffset * FilmicConstants::c_MiddleGray;
grading.Power = clampedPower;
grading.Active = temperature != 6500.0f || clampedTint != 0.0f || clampedSlope != glm::vec3(1.0f) || clampedOffset != glm::vec3(0.0f)
	|| clampedPower != glm::vec3(1.0f);
return grading;
```

1. **Line 193:** the white balance matrix, from the clamped temperature and tint.
2. **Line 195:** the slope is a diagonal matrix, and the product with the white balance gives one matrix for both.
3. **Line 196:** the offset is stored in units of light: the setting times middle gray, 0.18.
4. **Lines 198–199:** `Active` is true when any setting differs from its default; otherwise the grade is skipped.

One more function matters for speed. `GetColorGrading` in `SceneRendererPost.cpp` keeps the white balance matrix for as long as the temperature and tint stay the same, so the table lookup and the double-precision product run only when the person moves a slider.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1338-L1347"
const glm::vec2 key(postProcess.WhiteBalanceTemperature, postProcess.WhiteBalanceTint);
if (key != m_GradingKey || !m_Grading)
{
	m_Grading = PostProcessMath::MakeColorGrading(key.x, key.y, glm::vec3(1.0f), glm::vec3(0.0f), glm::vec3(1.0f));
	m_GradingKey = key;
}
PostProcessMath::ColorGrading grading = PostProcessMath::MakeColorGrading(6500.0f, 0.0f, postProcess.ColorSlope, postProcess.ColorOffset, postProcess.ColorPower);
grading.Matrix = grading.Matrix * m_Grading->Matrix;
grading.Active = grading.Active || m_Grading->Active;
return grading;
```

1. **Line 1338:** the cache key is the pair of temperature and tint, as the component holds them.
2. **Line 1339:** a new key, or an empty cache, rebuilds the white balance alone, with neutral slope, offset and power.
3. **Line 1344:** the slope, offset and power of this frame go through the same function at 6,500 K, which costs a few clamps.
4. **Line 1345:** the two matrices multiply: the slope's after the cached white balance.
5. **Line 1346:** the flag is the or of both parts.

The pass copies the three rows of the matrix, the offset and the power into its :term[constant buffer]{id=constant-buffer}, `TonemapConstants`, and sets the bit `c_TonemapColorGrading` in `ColorFlags` when the grading is active.

### The shader

The shader repeats the grading in four lines. Search for the matrix as three :term[dot products]{id=dot-product}, the clamp at zero and the pivot at 0.18.

```slang src="Strata/shaders/PostProcess/Tonemap.frag.slang#L239-L244"
if ((u_Parameters.ColorFlags & ST_COLOR_GRADING) != 0u)
{
	color = float3(dot(u_Parameters.ColorRows[0].xyz, color), dot(u_Parameters.ColorRows[1].xyz, color), dot(u_Parameters.ColorRows[2].xyz, color));
	color = max(color + u_Parameters.ColorOffset.xyz, float3(0.0));
	color = min(0.18 * pow(color / 0.18, u_Parameters.ColorPower.xyz), float3(c_MaxExposedValue));
}
```

The three `dot` calls multiply the color by the matrix. The `max` keeps negative light from entering the power, which a negative number cannot take. The `0.18 * pow(color / 0.18, power)` is the CDL's power around middle gray, and the `min` caps the result at a very large finite number so that a huge power cannot make infinities in the :term[high dynamic range]{id=high-dynamic-range} target.

::figure{id=grading-compare variant=off}

::figure{id=grading-compare variant=on}

Contrast and the tone curve follow, and then saturation. After that comes the encoding, and the lookup uses the encoded color.

```slang src="Strata/shaders/PostProcess/Tonemap.frag.slang#L265-L270"
if (u_Parameters.ColorLookupIntensity > 0.0)
{
	float size = float(TextureSize(u_ColorLookup, 0).x);
	float3 graded = u_ColorLookup.Sample(u_ColorLookupSampler, encoded * ((size - 1.0) / size) + 0.5 / size).rgb;
	encoded = clamp(lerp(encoded, graded, u_Parameters.ColorLookupIntensity), 0.0, 1.0);
}
```

The shader reads the table through a trilinear read of the hardware. **Trilinear interpolation** is the extension of :term[linear interpolation]{id=linear-interpolation} to a grid in three dimensions. The result is the weighted mean of the eight points that surround the input, and each weight is the product of three 1D weights. Say the input stands one fifth of the way from a point to the next along red, and half way along green and blue. The weight of the corner nearest the origin is $0.8 \cdot 0.5 \cdot 0.5 = 0.2$, and the eight weights add up to 1.

The coordinate of the sample is the **half-texel remap**: the correction that places a grid of N points at the centers of N texels. A texture coordinate of 1 is the far edge of the last texel, so the range 0 to 1 spans N whole texels, but the table's points sit at texel centers, only $N - 1$ steps apart. With 17 points, an input of 0.25 would read at texel position 4.25, a mix of points 3 and 4, although point 4 is the right answer and sits at position 4.5. The first point sits at $\tfrac{1}{2N}$ and the last at $1 - \tfrac{1}{2N}$, so an input of 0 must read at 0.0294 and an input of 1 at 0.9706.

$$c = e \cdot \frac{N-1}{N} + \frac{1}{2N}$$

In this formula $c$ is the texture coordinate to sample, $e$ is the encoded input of one channel from 0 to 1, and $N$ is the number of points each way. The first term shrinks the input range so that it spans $N - 1$ steps of a texel each, and the second term moves it half a texel inward. Check the limits: $e = 0$ gives $\tfrac{1}{2N}$, and $e = 1$ gives $\tfrac{N-1}{N} + \tfrac{1}{2N} = 1 - \tfrac{1}{2N}$. Check a middle value with $N = 17$ and $e = 0.25$: $c = 4/17 + 0.5/17 = 4.5/17$, which is the center of texel 4, so the read lands on point 4 and gives its color unchanged.

The result mixes with the plain color by `ColorLookupIntensity`, so 0 gives the plain image, 1 gives the full grade and 0.5 the mean of both. Film grain and dither come after the lookup.

### The `ColorLookup` asset

A `ColorLookup` asset is a table of N by N by N colors, with N from 2 to 65, kept as a 3D texture of four half floats per point. Its cooked form, called `STLU`, starts with the four numbers of 4 :term[bytes]{id=byte} each, the magic `STLU`, a format version, the size and a zero, followed by $N^3$ points of four half floats. Memory grows with the cube: 17 points are 39 KB, 33 points 287 KB, and 65 points 2.2 MB. The path from a file to a frame has two sides: the import runs in the background, and the upload and the frame belong to the main thread.

```mermaid caption="The path of a lookup to a frame: a background import makes a cooked table, the main thread uploads it, and the frame binds it once it is there." alt="A chain of boxes from a cube file through parsing, a new grid, the cooked table and the upload, to the frame's resolve and the tone-mapping shader."
flowchart LR
  A[.cube file] --> B[ParseCubeFile]
  B --> C[CubeTable]
  C --> D[ResampleCubeTable]
  D --> E[Cooked STLU]
  E --> F[FinalizeOnMainThread: 3D texture]
  F --> G[ResolveColorLookup]
  G --> H[GetTonemapInputSet]
  H --> I[Tonemap shader]
```

`ParseCubeFile` reads the file as untrusted text, one line at a time. A `.cube` file holds keyword lines, such as `LUT_3D_SIZE 33` and `DOMAIN_MIN 0 0 0`, comments that start with `#`, and then $N^3$ lines of three numbers, with red changing fastest. The first quote shows the loop and its cancel check. Search for the line counter, which every error message uses.

```cpp src="Strata/src/Strata/Asset/ColorLookupImporter.cpp#L201-L208"
while (!text.empty())
{
	lineNumber++;
	const size_t end = text.find('\n');
	std::string_view line = text.substr(0, end);
	text.remove_prefix(end == std::string_view::npos ? text.size() : end + 1);
	if (lineNumber % c_CancelCheckLines == 0 && cancel && cancel->load(std::memory_order_relaxed))
		return fail("cancelled");
```

The counter starts at 1 for the first line and counts every line, so an error names the line a person sees in a text editor. The cancel flag is read once in every 4,096 lines, which is cheap for a file of 274,625 values and still stops a long import promptly. The next quote shows the size keyword, the most checked line of the format.

```cpp src="Strata/src/Strata/Asset/ColorLookupImporter.cpp#L231-L244"
else if (keyword == "LUT_3D_SIZE")
{
	const std::string_view token = NextToken(rest);
	const std::optional<double> size = ParseNumber(token);
	if (table.Size != 0)
		return fail("LUT_3D_SIZE is given twice");
	if (!size || !Trim(rest).empty() || *size != std::floor(*size))
		return fail(fmt::format("LUT_3D_SIZE needs a whole number, not {}", Quote(Trim(line.substr(keyword.size())))));
	if (*size < ColorLookup::c_MinSize || *size > ColorLookup::c_MaxSize)
		return fail(fmt::format("LUT_3D_SIZE {} is outside {} to {}", Quote(token), ColorLookup::c_MinSize, ColorLookup::c_MaxSize));
	table.Size = static_cast<uint32_t>(*size);
	expected = static_cast<uint64_t>(table.Size) * table.Size * table.Size;
	table.Colors.reserve(static_cast<size_t>(expected));
}
```

1. **Line 235:** a second `LUT_3D_SIZE` is an error, because the first one already fixed the count of values.
2. **Line 237:** the size must be a whole number with nothing after it.
3. **Line 239:** the size must lie in the asset's range, 2 to 65, so that a file cannot ask for billions of values.
4. **Line 243:** the vector reserves the room once, only after the size passed both checks.

Values need a size first, and keywords may not follow values. A file may give its input range as `DOMAIN_MIN` and `DOMAIN_MAX`, or as `LUT_3D_INPUT_RANGE`, but not both. A 1D table (`LUT_1D_SIZE`) is refused with a message that asks for a 3D export. An unknown keyword is ignored, with a warning that names its line. The value lines decide the rest.

```cpp src="Strata/src/Strata/Asset/ColorLookupImporter.cpp#L279-L286"
if (table.Size == 0)
	return fail(fmt::format("the value {} comes before LUT_3D_SIZE", Quote(line)));
if (table.Colors.size() >= expected)
	return fail(fmt::format("more than the {}^3 values LUT_3D_SIZE gives", table.Size));
float values[3] = {};
if (!ParseNumbers(line, values, 3))
	return fail(fmt::format("expected three numbers, found {}", Quote(line)));
table.Colors.emplace_back(values[0], values[1], values[2]);
```

Each value line must hold exactly three finite numbers. The error quotes the offending text as valid :term[UTF-8]{id=utf-8}, so that a binary file cannot put garbage in a log. Too few values, too many values and an empty domain are errors as well.

`Import` calls the :term[parser]{id=parser}, then reads the `Size` setting. The setting offers `File`, 17, 33 and 65, with 33 as the default, and an unknown value becomes a warning and 33. A table of another size is rebuilt on a new grid. `ResampleCubeTable` maps each point of the new grid into the file's domain, clamps it to the edge and reads the old table trilinearly.

A table that already has the requested size and the domain from 0 to 1 passes unchanged. A size of $(n - 1) k + 1$ refines a table of $n$ points exactly, so 33 points refine a table of 17, 9 or 5 points without error.

```cpp src="Strata/src/Strata/Asset/ColorLookupImporter.cpp#L363-L383"
std::optional<CubeTable> table = ParseCubeFile(*source, &error, context.Cancel);
if (!table)
	return Fail(outError, context.IsCancelled() ? std::string("cancelled") : fmt::format("{}: {}", name, error));

std::optional<uint32_t> size = ParseSize(context.Settings);
if (!size)
{
	result.Warnings.push_back(fmt::format("Unknown color lookup size '{}'; expected File, 17, 33 or 65", JsonUtils::GetString(context.Settings, "Size", "")));
	size = c_DefaultSize.Size;
}
if (*size == 0)
	size = table->Size;
const std::vector<glm::vec3> colors = ResampleCubeTable(*table, *size, context.Cancel);
if (context.IsCancelled())
	return Fail(outError, "cancelled");
result.Data = ColorLookup::Serialize(*size, colors, &error);
if (result.Data.empty())
	return Fail(outError, fmt::format("{}: {}", name, error));
for (std::string& warning : table->Warnings)
	result.Warnings.push_back(fmt::format("{}: {}", name, warning));
return true;
```

1. **Line 363:** the parser gets the file's bytes and the import's cancel flag.
2. **Line 367:** the size setting is read, and the check for an unknown name follows.
3. **Line 373:** the choice `File` stores zero, and zero means the file's own size.
4. **Line 375:** the new grid checks the cancel flag too, once for every slice of blue.
5. **Line 378:** `Serialize` rounds the colors to half floats and refuses sizes or values the format cannot hold.

### The frame's side

A frame needs the texture, and it needs it without waiting. `ResolveColorLookup` asks the frame's asset cache for the asset at high priority, and it returns the texture only when the asset is loaded and uploaded.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1159-L1165"
nvrhi::ITexture* SceneRenderer::ResolveColorLookup(const PostProcessComponent& postProcess)
{
	if (!postProcess.ColorLookup.IsValid() || !(postProcess.ColorLookupIntensity > 0.0f))
		return nullptr;
	const Ref<ColorLookup> lookup = m_Assets.Resolve<ColorLookup>(postProcess.ColorLookup, AssetPriority::High);
	return lookup ? lookup->GetTexture() : nullptr;
}
```

With no handle, or with intensity 0, the function returns null and never asks for the asset. Otherwise the request is recorded, and the frame's statistics count a lookup that is still loading as pending, so the frame is not reported as complete. The call stands in `RenderFrame` before the statistics are read, for that reason.

The binding sets of the post passes must not change while the lookup loads. `GetTonemapInputSet` holds the code's second set of the pass, laid out by `m_TonemapInputLayout`. It holds the lookup at slot 3, the lens flare at slot 4 and a sampler at slot 2. When a texture is missing, the function binds a dummy texture in its place.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L1192-L1199"
nvrhi::ITexture* lookupTexture = lookup ? lookup : m_ColorLookupDummy.Get();
nvrhi::ITexture* flareTexture = flare ? flare : m_LensFlareDummy.Get();
if (!m_TonemapInputSet || m_TonemapInputLookup != lookupTexture || m_TonemapInputFlare != flareTexture)
{
	nvrhi::BindingSetDesc set;
	set.bindings = { nvrhi::BindingSetItem::Texture_SRV(3, lookupTexture), nvrhi::BindingSetItem::Texture_SRV(4, flareTexture),
		nvrhi::BindingSetItem::Sampler(2, m_LinearClampSampler) };
	nvrhi::BindingSetHandle inputSet = m_Device->createBindingSet(set, m_TonemapInputLayout);
```

The set is rebuilt only when one of the two textures changes, and the old set goes through `Renderer::ReleaseDeferred` so that :term[frames in flight]{id=frames-in-flight} can still read it. The shader never reads the dummy, because the intensity stays 0 until `m_TonemapInputLookup` equals the resolved texture. If the set cannot be created, the function reports the error and draws without the lookup and without the flare.

::figure{id=lookup-sweep variant=intensity-0}

::figure{id=lookup-sweep variant=intensity-half}

::figure{id=lookup-sweep variant=intensity-1}

::figure{id=lookup-sweep variant=intensity-0 crop=sky}

::figure{id=lookup-sweep variant=intensity-half crop=sky}

::figure{id=lookup-sweep variant=intensity-1 crop=sky}

::figure{id=lookup-sweep variant=intensity-0 crop=robot}

::figure{id=lookup-sweep variant=intensity-half crop=robot}

::figure{id=lookup-sweep variant=intensity-1 crop=robot}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Scale RGB by the light's color | Simple image editors and many small engines | One multiply and no locus table | Hues that skew for saturated colors, as the toy's orange shows |
| A different adaptation matrix | Standards for color profiles | A matrix that profiles already use | A second matrix to keep, for a difference most scenes do not show |
| A 1D curve before the 3D table | Color management libraries | Better precision for tables made on log images | A second texture, and grading tools that export 3D only |
| Four points instead of eight | Color management libraries | Smaller errors along the gray axis | A shader of its own: the hardware's trilinear read is free |
| Grade in a log encoding, then the lookup | Film pipelines | One space for the CDL and the lookup | An extra conversion pair and a new pass to test |

## How it is tested

Four suites cover the work, from the math to the pixels.

- `Renderer.PostProcessMath` checks that 6,500 K with tint 0 is the identity. It checks that every temperature and tint names a light that comes out neutral, and that low temperatures turn the image blue. It also checks the locus against the physics of a glowing body below 4,000 K and against the daylight formula above 5,000 K. Last, slope, offset and power must act around middle gray and clamp wild input.
- `Renderer.ColorLookup` checks that a table survives its cooked form at :term[half precision]{id=half-float}. It checks that bad sizes are refused with a reason, that truncated, padded and garbage bytes are rejected, and that the read is the grid at its points and trilinear between.
- `GPU.SceneRenderer.ColorLookup` renders a wall with a 9-point grade and compares every pixel with a trilinear lookup computed in plain code, to within one code, at intensity 1 and 0.5. It also checks that a missing or zero-intensity lookup leaves the image unchanged, and that the lookup uploads once.
- `Asset.ColorLookupImporter` checks that the parser reads titles, domains and values whatever the line endings and comments, and that broken files are refused with the line and the reason. It checks that a new grid keeps a table of its size, refines exactly and maps the file's domain, and that the importer stores the size its setting names.

Run them with the test :term[executable]{id=executable} of a Debug build. The GPU suite needs a graphics card.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.PostProcessMath
build/windows/bin/Debug/StrataTests.exe --test-suite=Renderer.ColorLookup
build/windows/bin/Debug/StrataTests.exe --test-suite=Asset.ColorLookupImporter
build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.ColorLookup
```

The first three need no graphics card. A change to the importer's output also needs a new test in the importer suite, with the line and the reason of each new refusal.

## Changing it safely

The place to start depends on the change.

- A new grading control goes into `ColorGrading` and `MakeColorGrading`, the pass's constants and the shader together, with `ApplyColorGrading` kept equal to the shader, because the tests compare the plain function with the pixels. Add no field to the frame constants: post effects have their own.
- A new keyword of the `.cube` format goes into `ParseCubeFile` with a test of its error cases. The parser stays a reader of untrusted text.
- A change to what the importer writes bumps `GetVersion()`, which is 1 now, so that the editor imports old files again.
- A change to the locus goes through `Tools/GenerateWhiteBalance.py`, never into `WhiteBalanceLocus.inl` by hand, and 6,500 K must stay the exact identity.
- A new input of the tone-mapping set goes through `GetTonemapInputSet` with its own dummy.

:::rule
Bump an importer's `GetVersion()` whenever its output changes. Without the bump, files imported before the change keep the old output. See [importing](../assets/importing.md).
:::

## Summary

- A temperature and a tint choose a light on the white locus. CAT02 turns that light into one 3 by 3 matrix, computed in double, and 6,500 K with tint 0 gives the exact identity.
- Slope, offset and power act on scene-linear light before the curve: the slope multiplies, the offset adds light in fractions of middle gray, and the power pivots on 0.18.
- A lookup read uses the coordinate $e (N-1)/N + 1/(2N)$ and the trilinear mean of eight points, so a grid of N points sits at the centers of N texels.
- A `.cube` file is read as untrusted text, rebuilt at a size of 17, 33, 65 or its own, stored as `STLU` and bound through dummies until it is loaded.
- A grade made by numbers belongs on scene-linear light before the curve, and a grade made in another tool belongs on display values after it.

## Check yourself

1. A lamp of 3,200 K lights a gray wall. You set the white balance to 3,200 K. What does a gray of 0.18 become, and why?

   - A. It stays (0.18, 0.18, 0.18), because the setting only changes the lamp.
   - B. It becomes about (0.067, 0.205, 0.470): the correction scales each cone response so that the lamp's own color turns neutral, which turns every gray blue.
   - C. It becomes about (0.470, 0.205, 0.067): low temperatures warm the picture.
   - D. It becomes (0, 0, 0.18): only blue is kept.

   :::answer{tests="wb-matrix"}
   B. The setting names the light that should look white, so the matrix removes that light's orange, and a gray that carries no orange is pushed toward blue. A forgets that the matrix is not the identity away from 6,500 K. C reverses the direction, and D has no basis in the gains.
   :::

2. A pixel has a red value of 0.12. Slope is 1.5, offset 0.1 and power 1 for red. What does the red value become?

   :::answer{tests="cdl-grade"}
   0.198. The slope gives $0.12 \cdot 1.5 = 0.18$. The offset is stored as $0.1 \cdot 0.18 = 0.018$ and is added, which gives 0.198. A power of 1 changes nothing, and the value is above 0, so the clamp does nothing.
   :::

3. A lookup has 17 points each way. At which texture coordinate does the shader sample for an encoded value of 0.5, and which point does it read?

   :::answer{tests="lut-read"}
   $c = 0.5 \cdot 16/17 + 0.5/17 = 8.5/17 = 0.5$. That is the center of texel 8, so the read lands on point 8, whose input is $8/16 = 0.5$, and gives its color without mixing: all the weight is on one corner.
   :::

4. A person adds a 65-point `.cube` file and sets the lookup on the camera at intensity 1. Which statement about the first frames is true?
   - A. The frame waits until the table is loaded, then draws.
   - B. Until the asset is loaded and uploaded, `ResolveColorLookup` returns null: the pass binds the dummy texture, keeps the intensity at 0 and draws without the lookup, and the frame counts the asset as pending.
   - C. The shader reads the dummy and mixes it in, so the image flashes black.
   - D. The binding set is rebuilt on every frame while the asset loads.

   :::answer{tests="cube-import"}
   B. A is wrong: no frame waits for an asset. C is wrong because the intensity stays 0, and the shader skips the lookup then. D is wrong because the set is rebuilt only when a texture changes: the dummy stays bound.
   :::

5. A grading artist exports a lookup after grading on a display, and a designer wants a slope that doubles the scene's light, exactly one stop. Where does each belong in the pass?

   - A. Both after the curve, on display values.
   - B. The lookup after the curve and the encoding, and the slope before the curve on scene-linear light.
   - C. Both before the curve.
   - D. The lookup before the curve, because tables are made for light.

   :::answer{tests="grade-order"}
   B. On scene-linear light, doubling is one stop. On display codes, doubling a value is not a stop, since the codes are not proportional to light. A and C each put one in the wrong place. D is wrong because the table was made by looking at display values.
   :::

## Exercises

1. **Basic.** The Camera manual's night recipe sets Auto Exposure on with Exposure -1 to -2, White Balance Temperature 4000 to 5000, Toe 0.6 and Bloom Intensity 0.06. Take the middle of each range, -1.5 and 4500, and justify each of the four numbers.

   :::answer[Worked solution]{tests="wb-matrix,grade-order"}
   An exposure of -1.5 stops multiplies the light by $2^{-1.5}$, about 0.35, so the night does not look like a dim day. A temperature of 4,500 K names a warmer light than moonlight, so the image turns cool: the table gives a gray of 0.18 as (0.131, 0.188, 0.277), a blue cast. The toe of 0.6 crushes the darkest tones and the bloom of 0.06 lets bright lamps glow; both belong to [tone mapping](../image/tone-mapping.md) and the bloom pass, not to the grade.
   :::

2. **Medium.** Write a program that prints a 3-point `.cube` file lifting blue by a tenth of its distance to 1, then say what the importer does with it.

   :::answer[Worked solution]{tests="lut-read,cube-import"}
   The loops run blue outermost and red innermost, because a `.cube` file changes red fastest. The program prints the :term[header]{id=header} and 27 lines.

   ```cpp sketch="image-grading-cube.cpp"
   #include <cstdio>

   // Writes a 3D .cube table of N points each way that lifts blue by a tenth of its distance to 1: cool shadows, white unchanged.
   int main()
   {
   	const int size = 3;
   	std::printf("TITLE \"Cool shadows\"\nLUT_3D_SIZE %d\n", size);
   	for (int blue = 0; blue < size; blue++)
   	{
   		for (int green = 0; green < size; green++)
   		{
   			for (int red = 0; red < size; red++)
   			{
   				const double last = size - 1;
   				const double b = blue / last;
   				std::printf("%.6f %.6f %.6f\n", red / last, green / last, b + 0.1 * (1.0 - b));
   			}
   		}
   	}
   	return 0;
   }
   ```

   ```text output-of="image-grading-cube.cpp"
   TITLE "Cool shadows"
   LUT_3D_SIZE 3
   0.000000 0.000000 0.100000
   0.500000 0.000000 0.100000
   1.000000 0.000000 0.100000
   0.000000 0.500000 0.100000
   0.500000 0.500000 0.100000
   1.000000 0.500000 0.100000
   0.000000 1.000000 0.100000
   0.500000 1.000000 0.100000
   1.000000 1.000000 0.100000
   0.000000 0.000000 0.550000
   0.500000 0.000000 0.550000
   1.000000 0.000000 0.550000
   0.000000 0.500000 0.550000
   0.500000 0.500000 0.550000
   1.000000 0.500000 0.550000
   0.000000 1.000000 0.550000
   0.500000 1.000000 0.550000
   1.000000 1.000000 0.550000
   0.000000 0.000000 1.000000
   0.500000 0.000000 1.000000
   1.000000 0.000000 1.000000
   0.000000 0.500000 1.000000
   0.500000 0.500000 1.000000
   1.000000 0.500000 1.000000
   0.000000 1.000000 1.000000
   0.500000 1.000000 1.000000
   1.000000 1.000000 1.000000
   ```

   1. **Line 8:** the blue loop is outermost, so red changes fastest in the output.
   2. **Line 16:** blue goes to $b + 0.1 (1 - b)$, so black becomes (0, 0, 0.1) and white stays white.

   Import the output with `asset.import`, giving the file's :term[absolute path]{id=absolute-path}. The default `Size` is 33, so the importer rebuilds the table of 3 points on a grid of 33 points, and the grid of 3 is exact because $33 = (3 - 1) \cdot 16 + 1$. Then set `ColorLookup` on the `PostProcess` component to the asset and `ColorLookupIntensity` to 0.5, and a black pixel reads (0, 0, 0.05).
   :::

3. **Medium.** Trace it yourself: find where a `.cube` file's first frame with a lookup is decided, and say what the frames before it draw.

   :::answer[Worked solution]{tests="cube-import"}
   Start at `ColorLookupImporter::Import` in `Strata/src/Strata/Asset/ColorLookupImporter.cpp`, which calls `ParseCubeFile`. The frame's side starts at the call of `ResolveColorLookup` in `SceneRenderer::RenderFrame` in `Strata/src/Strata/Renderer/SceneRenderer.cpp`, which returns a texture only once the asset is loaded and uploaded. `GetTonemapInputSet` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp` then binds it, and the pass sets the intensity. Until that frame the pass binds the dummy, the intensity stays 0, the branch at the end of `Tonemap.frag.slang` is skipped, and the frame counts the asset as pending.
   :::

## Where it lives in Strata

- Math: `Strata/src/Strata/Renderer/PostProcessMath.cpp`, `GetWhiteLocus`, `GetWhiteBalanceMatrix`, `MakeColorGrading` and `ApplyColorGrading`.
- Locus: `Strata/src/Strata/Renderer/WhiteBalanceLocus.inl`, written by `Tools/GenerateWhiteBalance.py`.
- Pass: `SceneRenderer::GetColorGrading`, `ResolveColorLookup` and `GetTonemapInputSet` in `Strata/src/Strata/Renderer/SceneRendererPost.cpp`; the shader `Strata/shaders/PostProcess/Tonemap.frag.slang`.
- Asset: `Strata/src/Strata/Renderer/ColorLookup.cpp` and `Strata/src/Strata/Asset/ColorLookupImporter.cpp`, with its setting `Size`.
- Settings: the properties `WhiteBalanceTemperature`, `WhiteBalanceTint`, `ColorSlope`, `ColorOffset`, `ColorPower`, `ColorLookup` and `ColorLookupIntensity` of `PostProcessComponent` in `Strata/src/Strata/Renderer/RendererComponents.h`.
- Tests: the suites `Renderer.PostProcessMath`, `Renderer.ColorLookup`, `GPU.SceneRenderer.ColorLookup` and `Asset.ColorLookupImporter`.

## Further reading

- The ASC CDL specification (intermediate): the slope, offset, power and saturation, as the industry defines them.
- Fairchild, Color Appearance Models (advanced): von Kries, CAT02 and the models around them.
- The Cube LUT specification of Adobe (beginner): the keywords of the `.cube` format.
- Physically Based Rendering, the chapter on color (intermediate): spectra, chromaticity and the color matching functions, at [the book's site](https://pbr-book.org/).
