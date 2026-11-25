---
id: image/quality-settings
title: "Quality settings and players' graphics options"
description: "How Strata keeps a scene's look apart from a machine's cost: rows, presets, the players' choices, and why no setting renders below native resolution."
kind: internals
size: L
tracks: [E]
needs: [image/taa, light/sun-shadows-2, world/projects-settings]
time: 75
learn:
  - id: native
    text: explain why Strata never renders below native resolution and what that choice costs
  - id: layers
    text: name the layers that make the quality in effect and say which one wins for a row
  - id: player-rules
    text: predict the options in effect after a sequence of a player's Set, SetPreset and Reset calls
  - id: trace
    text: trace a script's Graphics::Set to the renderer's SetQuality and say what a frame with no change costs
  - id: add-row
    text: name every place a new quality row touches
since: 0.7.0
status: final
---

A scene says what it should look like: where the lights are, how bright, what the exposure is, how the picture is graded. A machine decides how much of that it can afford. This page covers the part of Strata that keeps those two apart: rows of cost, grouped into presets, which a project, a player or a :term[command line]{id=terminal-command} chooses without touching the scene. It also covers the options a game offers its players. Each effect's own row sits on the effect's page.

::figure{id=presets-compare variant=low}

::figure{id=presets-compare variant=medium}

::figure{id=presets-compare variant=high}

::figure{id=presets-compare variant=ultra}

## The problem and how engines solve it

Think of one game on two computers. A player with a new :term[graphics card]{id=gpu} wants every shadow sharp. A player with a laptop wants the game to run at a steady :term[frame rate]{id=frame-rate}, even if some shadows turn soft. The scene is the same for both: the same lamp, the same sun, the same sky. What differs is how much work the computer spends to draw them.

Most of the cost of a frame comes from a few settings. A sun shadow is a picture of the scene from the sun, and its size in texels decides both its sharpness and its memory. Ambient occlusion takes samples around each pixel, and more samples give smoother results for more time. Each such number is a row: one named setting that costs time or memory.

Engines group the rows. A **quality preset** is a named set of values for every cost row, such as `Low`, `Medium`, `High` and `Ultra`, which a person chooses with one click. Presets let a game maker test four setups instead of dozens of combinations. The danger is that a row quietly changes the look. If `Low` turned a scene's warm grade into a cold one, the game would no longer look like the artist's work, only cheaper.

So Strata applies one separation. The scene, through its lights, Post Process and sky, owns the look. A quality row owns only the cost of drawing what the scene asks for. A row can scale the cost, with fewer samples or smaller maps. It can drop what a scene asked for when that costs too much, as the lowest preset drops screen-space reflections.

A row never changes exposure, the :term[tone curve]{id=tone-mapping-image} or the grade, and it never adds an effect the scene did not ask for.

A second family of techniques saves cost differently: it draws fewer pixels. A **render scale** below 1 draws the image at a fraction of the screen's size and stretches it up. Dynamic resolution moves that fraction frame by frame to hold the frame rate. Temporal upscaling goes further: it combines several small frames, with the help of motion data, into one large image. Each of the three is a render scale in this book, and each trades sharpness for speed.

:::why[Why does Strata never draw below native resolution?]
The owner's direction for the image is a realistic, :term[filmic]{id=filmic-strata} look at the screen's own resolution. An image drawn small and stretched is softer, and an image rebuilt from earlier frames smears where things move. Strata therefore has no render scale below 1, no dynamic resolution and no temporal upscaling, and no effect may need temporal accumulation to look right. [Temporal anti-aliasing](taa.md) stays one anti-aliasing choice among others.

The price is real. The graphics processing unit (GPU) cost of a frame does not adapt: a scene too heavy for a machine stays too heavy until a person lowers a row, because the engine never shrinks the image. Sampling several points in each pixel, and :term[supersampling]{id=supersampling-ssaa}, keep every pixel at native size. The engine's plan keeps the first for later, and the second only for still pictures.
:::

## The map: who decides the quality

One value of quality reaches every :term[renderer]{id=renderer}, and four layers decide it. Read them from the bottom. The section `Renderer.Quality`, a [settings section](../world/projects-settings.md) of the project, has a default: `High`.

A project may store its own value, a preset or custom values. A player's choices, made in a game's options menu, lie over the project's value. Over both lies the command line's preset, `--quality`, which fixes the preset for one run.

```mermaid caption="Four layers make the value in effect. The renderer asks the service for a version number and reads the value only when the number changed." alt="A diagram with four boxes stacked from the section's default through the project's value and the player's choices to the command line. An arrow leads to the value in effect, and from there to the game renderer, which compares a version number and calls the scene renderer's set quality."
flowchart TB
    D["Renderer.Quality section: default High"] --> P["Project's value"]
    P --> Y["Player's choices (GraphicsOptions.json)"]
    Y --> C["--quality preset, one run"]
    C --> E["Value in effect + version number"]
    E --> G["GameRenderer: compares the version"]
    G --> S["SceneRenderer::SetQuality"]
```

A row follows the preset when a named preset decides its value. Under the preset **Custom**, which takes its values from the section's own fields instead of from a row of presets, the field decides it.

The **graphics preset** of a game is the value of its `Preset` option: `Low`, `Medium`, `High`, `Ultra` or `Custom`, whichever layer chose it.

Two presets have a fixed meaning. `Medium` keeps the costs the renderer had before presets existed. It is also the default of `SceneRendererSpecification`, so tests, tools and performance scenes keep their cost. A new row's default is the value of `Medium`.

`High` is the default of the section, so the editor and exported games start there. A program that never provides the project's settings, such as a test, renders at `Medium`.

:::history
Before the 0.7.0 release the renderer had one fixed set of costs, those of 0.6.0. The presets were added around those costs, and Medium is that set. A test written for the old renderer therefore still measures the same work.
:::

The same value does not reach every picture in the editor. The next diagram shows who follows which quality.

```mermaid caption="Who follows which quality. The game and the Game view follow the game's options; the Scene view's chip may choose its own; thumbnails and bakes never follow anyone." alt="A diagram with the game's quality at the center. The game, the Game view and the Scene view looking through the scene's camera follow it. The Scene view's editor camera follows the chip, which may pick a preset. Captures follow the view they show unless asked. Thumbnails and bakes use fixed old costs."
flowchart LR
    Q["Game's quality: project, player, --quality"] --> A["Exported game"]
    Q --> B["Game view"]
    Q --> C["Scene view through the scene camera"]
    V["Scene view chip: project or own preset"] --> D["Scene view, editor camera"]
    D --> E["Captures: the view's quality, or a preset asked for"]
    F["Fixed 0.6.0 costs"] --> G["Thumbnails and bakes"]
```

A bake never depends on a person's settings: a probe baked on a fast machine must equal one baked on a slow one. That is why thumbnails and bakes draw with the old fixed costs.

The picture below shows the chip's case. The Scene view's quality chip reads Low, so this view alone draws at the Low preset, while the project, the Game view and the game keep High.

::figure{id=graphics-page}

## The contract

A few rules hold for every row and every caller. Each has a reason.

One kind of row needs a name first. The **players' rows** are the settings that no preset decides and that a player chooses under every preset.

:::rule[Costly settings are rows, and Medium keeps its costs]
`AGENTS.md` asks that every costly setting is a row of `RendererQualitySettings` and a field of the `Renderer.Quality` section, with its four presets on one line. It also asks that `Medium` keeps the costs of the last release before presets. The reason is that a row added later must not change what an old test or a performance scene costs. See [the renderer reference](../reference/renderer.md) for every row with its values.
:::

1. **A row never changes a look control and never adds an effect.** It scales or drops the cost of what a scene asks for. Some presets drop a scene's reflections or motion blur, and others give global illumination to scenes that ask for it. The reason is trust: a game maker must be able to say that a preset shows the same picture, drawn more finely or more coarsely.
2. **The players' rows are comfort and taste, not cost.** The five are `AntiAliasing`, `MotionBlur`, `DepthOfField`, `FilmGrain` and `ChromaticAberration`. The last four only disable: their values are `Scene`, the scene's own, or `Off`. A player may switch off a blur the scene uses, never switch on one it lacks.
3. **The `AntiAliasing` row is a preference, and it may enable anti-aliasing.** Its values are `Scene`, `Off`, `FXAA`, `TAA` and `Morphological`. The last three set the method even for a scene that had anti-aliasing off, because a player who prefers one method should get it. The reason: edge smoothing is a taste, and it adds no new light or shape to the scene.
4. **Choices go by name, never by number.** The files and the script calls store `High`, never a number, so a new preset cannot shift what a stored name means.
5. **Only `GameGraphicsService` touches `GraphicsOptions.json`.** One owner of the player's file avoids two writers racing and keeps the validation in one place.

The game's side of these rules is the :term[engine service]{id=scene-service} `IGameGraphics`. Its **graphics options** are the fields of the section by name, ignoring case. A game's menu reads and changes them through the service, and a script reaches the service through the script software development kit (SDK) class `Graphics`. The next sections show the toy, then the real code.

## A toy version

The toy models three rows, one players' row and the layers of a player's choices. A table of arrays holds the presets, one row of four values per setting. The service's rule that a cost row switches the player to Custom is a function. Read the output for the order of events, which the real service follows.

:::question
Does this C++ look familiar? A struct, an array and a function are in [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md); `std::optional` is in [modern C++](../basics/cpp-modern.md).
:::

The program prints what is in effect after five events. Look at which events change the shadow size and which keep it.

```cpp sketch="image-quality-settings-toy.cpp"
#include <array>
#include <cstddef>
#include <cstdio>
#include <optional>

enum class Preset { Low, Medium, High, Ultra, Custom };

struct Quality
{
	Preset Level = Preset::High;
	int ShadowSize = 0;
	int Cascades = 0;
	bool Reflections = false;
	bool MotionBlur = true; // A players' row: shown (true) or turned off (false)
};

// One row per setting, with one value for each of Low, Medium, High and Ultra.
constexpr std::array<int, 4> c_ShadowSizeRow = { 1024, 2048, 4096, 8192 };
constexpr std::array<int, 4> c_CascadesRow = { 3, 4, 5, 5 };
constexpr std::array<bool, 4> c_ReflectionsRow = { false, true, true, true };

Quality GetPreset(Preset level)
{
	const size_t index = static_cast<size_t>(level);
	return { level, c_ShadowSizeRow[index], c_CascadesRow[index], c_ReflectionsRow[index], true };
}

struct Player
{
	std::optional<Preset> Level; // Nothing: the project's preset applies
	Quality Custom;              // The rows' values while the level is Custom
	bool BlurOff = false;        // Kept under every preset
};

Quality InEffect(Preset project, const Player& player)
{
	Quality result = player.Level == Preset::Custom ? player.Custom : GetPreset(player.Level.value_or(project));
	if (player.BlurOff)
		result.MotionBlur = false;
	return result;
}

void SetCascades(Player& player, Preset project, int cascades)
{
	if (player.Level != Preset::Custom)
	{
		player.Custom = InEffect(project, player); // Custom starts from the look in effect
		player.Level = Preset::Custom;
	}
	player.Custom.Cascades = cascades;
}

void Print(const char* step, const Quality& quality)
{
	constexpr std::array<const char*, 5> names = { "Low", "Medium", "High", "Ultra", "Custom" };
	std::printf("%-22s %-6s shadows %4d, cascades %d, reflections %d, blur %d\n", step, names[static_cast<size_t>(quality.Level)],
		quality.ShadowSize, quality.Cascades, quality.Reflections, quality.MotionBlur);
}

int main()
{
	Player player;
	Print("project High", InEffect(Preset::High, player));
	player.BlurOff = true;
	Print("blur off", InEffect(Preset::High, player));
	SetCascades(player, Preset::High, 3);
	Print("cascades 3", InEffect(Preset::High, player));
	Print("project turns Ultra", InEffect(Preset::Ultra, player));
	player.Level = Preset::Low;
	Print("player chooses Low", InEffect(Preset::Ultra, player));
}
```

```text output-of="image-quality-settings-toy.cpp"
project High           High   shadows 4096, cascades 5, reflections 1, blur 1
blur off               High   shadows 4096, cascades 5, reflections 1, blur 0
cascades 3             High   shadows 4096, cascades 3, reflections 1, blur 0
project turns Ultra    High   shadows 4096, cascades 3, reflections 1, blur 0
player chooses Low     Low    shadows 1024, cascades 3, reflections 0, blur 0
```

1. **Lines 18–20:** the three rows, one line each, with a value for each preset in order.
2. **Lines 28–33:** the player's layer: an optional preset, the Custom values, and one players' row that holds under every preset.
3. **Lines 35–41:** the value in effect: the Custom values or the preset's, then the players' row on top.
4. **Lines 43–51:** setting a cost row first switches to Custom, starting from what was in effect.

The first line shows the project's preset. The second disables blur, a players' row: the preset stays. The third sets a cost row, `Cascades`, and the player's level becomes Custom, starting from the look in effect, so only the cascades change.

The fourth line shows the point of the rule: when the project moves to `Ultra`, the player's tuning keeps its meaning and the shadow size does not jump. The fifth chooses a preset, which drops the player's Custom values and keeps the blur choice.

## The real code

The real code has the same pieces, with more rows and more care. Follow the data: the rows, then the settings struct, then the section, then the traits, then the players' overrides on the frame's copy, and last the service and the renderer.

### The rows and the preset function

Every setting has one line with a value for each preset, in preset order, so that two changes adding rows never touch the same line. Look at how one row is one line, and at the comment on :term[contact shadows]{id=contact-shadows}, which no preset enables.

```cpp src="Strata/src/Strata/Renderer/RendererQuality.cpp#L32-L58"
// The presets, a knob per line with its four values in preset order, so that rows added by different changes are
// separate lines. Medium is Strata 0.6.0's costs.
template<typename T>
using PresetRow = std::array<T, c_RendererQualityPresetCount>; // Low, Medium (0.6.0), High, Ultra

// High and Ultra buy back with texels, and a fifth cascade near the camera, the detail the stable cascades' spheres give up
// against squares fitted to the receivers.
constexpr PresetRow<ShadowMapResolution> c_ShadowResolutionRow = { ShadowMapResolution::Size1024, ShadowMapResolution::Size2048, ShadowMapResolution::AutoFine, ShadowMapResolution::Size8192 };
constexpr PresetRow<uint32_t> c_ShadowCascadesRow = { 3, 4, 5, 5 };
constexpr PresetRow<uint32_t> c_LocalShadowAtlasSizeRow = { 2048, 4096, 4096, 8192 };
constexpr PresetRow<uint32_t> c_LocalShadowMaxTileRow = { 512, 1024, 1024, 2048 };
// High and Ultra shadow more point and spot lights at the same atlas sizes, and draw more of their views a frame so that
// they settle as fast.
constexpr PresetRow<uint32_t> c_MaxShadowedLocalLightsRow = { 4, 16, 64, 256 };
constexpr PresetRow<uint32_t> c_LocalShadowViewsPerFrameRow = { 12, 12, 24, 48 };
constexpr PresetRow<float> c_LODErrorPixelsRow = { 2.0f, 1.0f, 1.0f, 0.5f };
constexpr PresetRow<float> c_MinProjectedPixelsRow = { 1.0f, 0.5f, 0.5f, 0.25f };
constexpr PresetRow<uint32_t> c_ShadowFilterQualityRow = { 8, 16, 24, 32 };
// Off in every preset: binary hits in a thin shell under screen-locked noise shimmer in motion (DG "Sun shadows");
// Custom turns them on.
constexpr PresetRow<uint32_t> c_ContactShadowsRow = { 0, 0, 0, 0 };
constexpr PresetRow<AmbientOcclusionLevel> c_AmbientOcclusionQualityRow = { AmbientOcclusionLevel::Low, AmbientOcclusionLevel::Medium, AmbientOcclusionLevel::High, AmbientOcclusionLevel::Ultra };
constexpr PresetRow<uint32_t> c_EnvironmentResolutionRow = { 256, 256, 512, 512 };
constexpr PresetRow<ReflectionsQuality> c_ReflectionsRow = { ReflectionsQuality::Off, ReflectionsQuality::Checkerboard, ReflectionsQuality::Spatial, ReflectionsQuality::SpatialHigh };
constexpr PresetRow<MotionBlurSamples> c_MotionBlurQualityRow = { MotionBlurSamples::Off, MotionBlurSamples::Samples8, MotionBlurSamples::Samples12, MotionBlurSamples::Samples16 };
constexpr PresetRow<GlobalIlluminationLevel> c_GlobalIlluminationRow = { GlobalIlluminationLevel::Off, GlobalIlluminationLevel::Off, GlobalIlluminationLevel::High, GlobalIlluminationLevel::High };
constexpr PresetRow<uint32_t> c_ReflectionProbeResolutionRow = { 128, 128, 256, 256 };
```

1. **Lines 34–35:** `PresetRow` is an array with one value for each preset, in preset order.
2. **Lines 39–49:** each setting is one line, so two changes that add rows never meet on one line.
3. **Lines 43–46:** the point and spot lights' two rows. The higher presets shadow more lights in atlases of the same size. The second row lets them draw more of those lights' views a frame, so the shadows settle as fast.
4. **Line 52:** contact shadows are off in every preset, because they shimmer in motion; only Custom enables them.
5. **Lines 55–56:** the first value of the reflections and motion blur rows is `Off`, so the lowest preset drops both for scenes that ask.

`GetPreset` reads the same arrays into a `RendererQualitySettings`, and `Custom` is High's values labeled Custom, the section's own defaults. `Clamp` keeps every value in its range: cascades from 1 to the maximum and sizes floored to powers of two. An unknown value of a cost choice becomes Medium's, and of a players' row `Scene`. `ResolveShadowMapSize` turns the `Auto` and `AutoFine` values into a number from the output's rows.

### The row traits

The Graphics Quality page and the players' options need to know a little more about each row than its value. A **row traits** line says whether the row follows the preset, which :term[GPU stage]{id=gpu-stage-strata} its time lands in, and how many :term[bytes]{id=byte} its resources take.

```cpp src="Strata/src/Strata/Renderer/RendererQuality.cpp#L163-L186"
constexpr RendererQuality::RowTraits c_RowTraits[] = {
	{ "ShadowResolution", true, "GPU.Shadows", &CascadeBytes },
	{ "ShadowCascades", true, "GPU.Shadows", nullptr }, // Counted with ShadowResolution
	{ "LocalShadowAtlasSize", true, "GPU.Shadows", &LocalShadowAtlasBytes },
	{ "LocalShadowMaxTile", true, "GPU.Shadows", nullptr },
	{ "MaxShadowedLocalLights", true, "GPU.Shadows", nullptr }, // The atlas's tiles, counted with LocalShadowAtlasSize; sampled in GPU.Opaque
	{ "LocalShadowViewsPerFrame", true, "GPU.Shadows", nullptr },
	{ "LODErrorPixels", true, "GPU.Opaque", nullptr },
	{ "MinProjectedPixels", true, "GPU.Opaque", nullptr },
	{ "ShadowFilterQuality", true, "GPU.ScreenShadows", nullptr }, // The filter runs in the mask's pass; taps allocate nothing
	{ "ContactShadows", true, "GPU.ScreenShadows", nullptr },      // Marches through the mask's own two targets
	{ "AmbientOcclusionQuality", true, "GPU.AO", nullptr },        // More samples into the same targets
	{ "EnvironmentResolution", true, "", &EnvironmentBytes },      // Filtered only when the sky changes: no stage of its own
	{ "Reflections", true, "GPU.Reflections", &ReflectionsBytes },
	{ "MotionBlurQuality", true, "GPU.MotionBlur", &MotionBlurBytes },
	{ "ReflectionProbeResolution", true, "GPU.Reflections", &ReflectionProbeBytes }, // Conversions run in the reflections' stage
	{ "GlobalIllumination", true, "GPU.RadianceCascades", &GlobalIlluminationBytes },
	// The players' rows: comfort and preference, not cost.
	{ "AntiAliasing", false, "", nullptr },                 // Its cost is the chosen method's (GPU.TAA or GPU.Post)
	{ "MotionBlur", false, "GPU.MotionBlur", nullptr },     // Counted with MotionBlurQuality
	{ "DepthOfField", false, "GPU.DepthOfField", nullptr }, // The scene's lens sizes its targets, not the quality
	{ "FilmGrain", false, "GPU.Post", nullptr },            // Added by the pass that writes the display image
	{ "ChromaticAberration", false, "GPU.Post", nullptr },  // Applied by the tone mapping
};
```

1. **Line 164:** one line holds the row's name, a flag that says a preset decides it, its GPU stage and a function that returns its bytes of memory.
2. **Line 165:** a null function means that another row counts the memory: the cascades belong to `ShadowResolution`.
3. **Lines 181–185:** the players' rows say `false` for `FollowsPreset`: no preset decides them, and `FromSectionValue` reads them under every preset.

### The players' rows applied to the frame's copy

The scene's Post Process holds what the scene asks for. The renderer never writes the players' choices into the scene. It applies them to the frame's own copy, so the scene's stored settings stay as the artist left them.

```cpp src="Strata/src/Strata/Renderer/SceneRendererPost.cpp#L458-L485"
void SceneRenderer::ApplyQualityOverrides(PostProcessComponent& settings, const RendererQualitySettings& quality)
{
	switch (quality.AntiAliasing)
	{
		case AntiAliasingChoice::Scene:
			break;
		case AntiAliasingChoice::Off:
			settings.AntiAliasing = false;
			break;
		case AntiAliasingChoice::FXAA:
			settings.AntiAliasing = true;
			settings.AntiAliasingMethod = AntiAliasingMode::FXAA;
			break;
		case AntiAliasingChoice::TAA:
			settings.AntiAliasing = true;
			settings.AntiAliasingMethod = AntiAliasingMode::TAA;
			break;
		case AntiAliasingChoice::Morphological:
			settings.AntiAliasing = true;
			settings.AntiAliasingMethod = AntiAliasingMode::Morphological;
			break;
	}
	if (quality.MotionBlur == SceneEffectChoice::Off || quality.MotionBlurQuality == MotionBlurSamples::Off)
		settings.MotionBlur = false;
	if (quality.FilmGrain == SceneEffectChoice::Off)
		settings.FilmGrain = 0.0f;
	if (quality.ChromaticAberration == SceneEffectChoice::Off)
		settings.ChromaticAberration = 0.0f;
```

1. **Lines 460–479:** the anti-aliasing choice. `Scene` changes nothing; `Off` disables the effect; the three methods enable it and pick the method, whatever the scene had.
2. **Lines 480–485:** the comfort rows only clear. A motion blur row of `Off`, or no samples in the preset, disables the blur; grain and chromatic aberration become zero. No line sets any of them to a new, non-zero value.

The depth of field row is not in this function. The renderer reads it where it decides whether a camera's lens blurs, and `SetQuality` frees the lens targets when the row is `Off`.

### The service and its value

A game changes quality through `IGameGraphics`. Its declaration shows what a caller may assume: the value is valid until the version changes, and a refused change changes nothing.

```cpp src="Strata/src/Strata/Core/EngineServices.h#L152-L184"
class IGameGraphics
{
public:
	virtual ~IGameGraphics() = default;

	// The section whose fields are the options, in field order; null when the program has none (a registry without the
	// renderer's section): every other function then reports nothing and refuses every change.
	virtual const SettingsSection* GetSection() const = 0;
	// The value in effect: an object with every field of the section at its version (a named preset's rows spelled
	// out). Valid until GetVersion changes.
	virtual const nlohmann::json& GetEffectiveValue() = 0;
	// Changes whenever the value in effect, a source or the player's choices change (the project's settings, a SetOption,
	// a reset, a load, the session's end); unique among the process's providers, so a renderer notices a provider
	// replaced by another.
	virtual uint64_t GetVersion() = 0;
	// Where the value in effect of an option comes from; nullopt for an unknown option.
	virtual std::optional<GameGraphicsSource> GetSource(std::string_view option) = 0;
	// The player's choices: an object of field names and values as the section stores them (what SaveOptions writes).
	// Valid until GetVersion changes.
	virtual const nlohmann::json& GetPlayerOptions() = 0;

	// Sets the player's choice of an option (its stored form: a choice's name, ignoring case, a number, a boolean): a row
	// that follows the preset switches the preset to Custom first, starting from the look in effect. False, changing
	// nothing, with the reason: an unknown option or a value the section refuses.
	virtual bool SetOption(std::string_view option, const nlohmann::json& value, std::string* outError = nullptr) = 0;
	// Removes the player's choice of an option ("": of every option; Preset: the preset and the rows that follow it, so
	// the project's quality applies again; a row that follows the preset under the player's Custom takes the project's
	// value for it). False for an unknown option.
	virtual bool ResetOptions(std::string_view option, std::string* outError = nullptr) = 0;
	// Writes the player's choices to <save directory>/GraphicsOptions.json, atomically (the disk is written before it
	// returns). False, with the reason, without a save directory or when the write fails; the choices stay.
	virtual bool SaveOptions(std::string* outError = nullptr) = 0;
};
```

1. **Lines 160–166:** the value in effect with every field spelled out, and the version that changes whenever the value, a source or the player's choices change. The version is unique among providers, so a renderer notices a replaced provider.
2. **Line 168:** `GetSource` says where the value of one option comes from: the project, the player or the command line.
3. **Lines 173–176:** `SetOption` switches to Custom first when the row follows the preset; it returns false, with the reason, and changes nothing for a value the section refuses.

`GameGraphicsService` implements it. These lines are the heart of how a player's choice combines with the rest.

```cpp src="Strata/src/Strata/Runtime/GameGraphicsService.cpp#L533-L565"
auto choosePreset = [&](const nlohmann::json& preset)
{
	nlohmann::json player = data.GetComfortChoices();
	if (preset.is_string() && preset.get_ref<const std::string&>() == RendererQuality::PresetToString(RendererQualityPreset::Custom))
	{
		const nlohmann::json start = RendererQuality::MakeCustomStart(base, data.Model);
		for (const RendererQuality::RowTraits& row : data.Model.Rows)
		{
			if (row.FollowsPreset)
				player[std::string(row.Field)] = start[std::string(row.Field)];
		}
	}
	player["Preset"] = preset;
	return player;
};
nlohmann::json player = data.Player;
if (field->Name == "Preset")
{
	player = choosePreset(stored);
}
else if (data.FollowsPreset(*field))
{
	// Unless the player's own preset is Custom, Custom first, from the look in effect (also under the project's Custom:
	// the player's tuning then holds every row and keeps its meaning when the project's preset changes).
	const nlohmann::json* preset = JsonUtils::Find(data.Player, "Preset");
	if (!preset || *preset != RendererQuality::PresetToString(RendererQualityPreset::Custom))
		player = choosePreset(RendererQuality::PresetToString(RendererQualityPreset::Custom));
	player[field->Name] = stored;
}
else
{
	player[field->Name] = stored;
}
```

1. **Lines 533–547:** a switch to a preset keeps the comfort choices. A switch to Custom takes every row that follows the preset from `MakeCustomStart`, the look in effect, so a later change of the project's preset cannot lose the player's tuning.
2. **Lines 549–551:** choosing `Preset` drops the player's cost rows and keeps the preset and the players' rows.
3. **Lines 553–560:** setting a row that follows the preset, while the player's preset is not Custom, first switches the player to Custom, also under the project's Custom.
4. **Lines 562–564:** a players' row, which no preset decides, only stores the choice.

The service validates the merged value with the section before it keeps it, then computes a new version. A reset removes choices. The empty name removes every choice; `Preset` removes the player's preset with its cost rows, and the project's quality applies again.

The file holds the options, the section's id and version, and a format version, written with tabs for layout. `Save` writes it atomically. A load reads at most 64 KiB and never rewrites the file. A file that is no options file gets one warning and is ignored; members the section no longer has are dropped with one warning.

### The renderer pulls the value

The service does almost no work per frame: it compares the project's settings version with the one it last read. The renderer asks for the version, an :term[integer]{id=integer}, and rebuilds the value only when it changed.

```cpp src="Strata/src/Strata/Runtime/GameRenderer.cpp#L58-L78"
const RendererQualitySettings& GameRenderer::FollowQuality(IGameGraphics& graphics)
{
	const uint64_t version = graphics.GetVersion();
	if (version != m_GraphicsVersion)
	{
		m_GraphicsQuality = RendererQuality::FromSectionValue(&graphics.GetEffectiveValue());
		m_GraphicsPresetSource = graphics.GetSource("Preset").value_or(GameGraphicsSource::Project);
		m_GraphicsVersion = version;
	}
	return m_GraphicsQuality;
}

void GameRenderer::ApplyQuality()
{
	IGameGraphics* graphics = m_QualityOverride ? nullptr : EngineServices::Get<IGameGraphics>();
	if (graphics && !graphics->GetSection())
		graphics = nullptr;
	const RendererQualitySettings& quality = m_QualityOverride ? *m_QualityOverride : graphics ? FollowQuality(*graphics)
		: RendererQuality::GetProjectQuality();
	// Equal knobs cost one comparison; a change makes again only what it sizes (SceneRenderer::SetQuality).
	m_Renderer->SetQuality(quality);
```

1. **Lines 60–66:** a changed version makes the renderer read the effective value again and remember where the preset came from; an unchanged version costs one comparison.
2. **Lines 72–76:** the quality is the override's (tests and tools), else the service's, else the project's cached value, which falls back to the specification's default where no program provides settings.
3. **Line 78:** `SetQuality` clamps the request and returns at once when every setting is equal. Otherwise it releases only what a changed row sizes, such as the cascades or the local shadows' atlas, and the next frame makes them again.

A log line, `Graphics quality: <preset> (<source>)`, appears when the preset or its source changes.

:::example[A player changes the cascades, then the project changes preset]
Take a game that uses the section's default preset, drawn at 1080 rows. Its shadow row is `AutoFine`: 4096 texels a side below 1440 rows, 8192 from them. With five cascades, the depth maps take 5 × 4096 × 4096 × 4 bytes, which is 320 MiB. The player sets `ShadowCascades` to 3. The service switches to Custom from the look in effect, so the shadow row stays `AutoFine`, and the three cascades take 192 MiB.

Now the project moves to the largest preset, whose shadow row is fixed at 8192. The player's Custom value still holds `AutoFine`, so the game still draws 4096-texel cascades at 1080 rows: three cascades, 192 MiB. A player who had changed nothing would see the larger maps. Custom keeps the meaning of the player's choice, at the price that the player no longer follows the project's improvements until the player resets.
:::

### From a script to a picture

A choice in a game's options menu ends in a picture in a fixed order. The script calls `Graphics`; the call crosses the host function table to the service. The service computes the value and a new version; the renderer sees the version at its next draw and calls `SetQuality`.

The SDK offers `Options`, `Get`, `Set`, `SetPreset`, `Reset` and `Save`, with `GraphicsOption` and `QualityPreset`. Seven host functions carry them across the script boundary: the option count, one option's description, a value read, a value set, a choice's name, a reset and a save.

The script below, written in the style of the Manual's example, is :term[pseudocode]{id=pseudocode} for a menu handler. Check which call changes the picture and which only writes a file.

```cpp pseudocode
void OnUIValueChanged(Entity widget, float value)
{
	if (widget == UltraToggle && value != 0.0f)
	{
		Graphics::SetPreset(QualityPreset::Ultra); // Shows from the next frame
		Graphics::Save();                           // Kept for the next run
	}
}
```

`SetPreset` changes the value in effect and its version. `Save` changes no picture; it writes `GraphicsOptions.json` beside the game's save files, and the game reads that file at its start. In the editor, play loads the player's file when it starts and forgets the choices when it stops. The command `graphics.resetPlayerOptions` deletes the file: while a saved choice sets the preset, a change of the project's preset does not show in play.

The Third-Person sample has such a menu. Its settings panel holds one toggle per preset, and the handler of each calls `Graphics::SetPreset` and then `Graphics::Save`. The picture below shows the panel after a click on **Settings** in the main menu, during play in the editor's Game view.

::figure{id=third-person-settings crop=view}

:::caution
Do not call `Graphics::Set` on a cost row in a script and then compare it with the preset: the preset has become Custom. Read `Graphics::GetPreset()` after the call to see what is in effect.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Dynamic resolution | Games that must hold a frame rate on one fixed machine | A :term[frame time]{id=frame-time} that adapts to load | A softer picture whenever the load rises, and a look that changes with the scene |
| Temporal upscaling | Games that rebuild a large image from small frames | A large saving at high resolutions | Smear in motion, and a look that depends on history |
| Sampling several points per pixel, and supersampling | Games that keep native size and pay for edges | Smooth edges without a history | A cost on every frame; the plan keeps the first for later, the second for stills |
| A benchmark at the first run | Games that pick the preset for the player | A good starting preset without a menu | Engine code to measure a machine, and a wrong guess on a new one |
| One scene-wide quality asset | Engines that store quality in the scene | Per-scene control | A scene that carries machine facts, which breaks the separation of look and cost |

## How it is tested

The suite `Renderer.Quality` checks the presets table against the section: every row has traits, every field reads back, and `Clamp` keeps values in range. `GPU.SceneRenderer.Quality` runs on a GPU. Its case `SetQuality makes again only what a changed knob sizes` checks what a change releases. Its case `Changing the quality and back draws the same image` renders, changes, changes back and compares the pixels, which must match exactly.

`Runtime.GameGraphics` tests the service: preset choices, cost rows, resets, the command line, the version rules, a bad file with one warning, and saving and loading. Its sweep, `Runtime.GameGraphics.Sweep`, cuts a valid file at many lengths and changes single bytes; every result must load or be refused without a crash. `Scripting.Graphics` tests the script kit against a test module, and `Editor.GameGraphics` the editor's side. The feature test sets a Custom value of the section, so a new row gets exercised.

Run one suite with the doctest filter, for example `StrataTests.exe --test-suite=Runtime.GameGraphics*`, or run them all through `ctest`. The GPU suite needs a GPU.

## Changing it safely

Adding a row touches many places, and the tests fail for the ones you forget. The row's member goes into `RendererQualitySettings`, with the value of `Medium` as its default. Its line of values goes in `RendererQuality.cpp`, with a line in `GetPreset`, `FromSectionValue` and `ToSectionValue`, one field of the section, and a line in `Clamp`.

The renderer uses the row on both draw paths, and any cache keyed on the row learns of it. The traits table gets a line, and `Renderer.Quality` checks the new column. The feature test project gets a Custom value. Last, the section's version goes up by one, because an older stored value then reads the new field's default.

A field's title and description reach players through `Graphics::Options`, so they say what the option changes and what it costs. They never mention engine versions or where the editor shows them.

The other rules that apply:

- Never read or write `GraphicsOptions.json` outside the service: two writers corrupt it.
- Apply the quality directly after `SetViewportSize` in a frame, so `Auto` resolves for the renderer's rows.
- Never add a row that renders below native resolution, or one that needs history to look right.

## Summary

- Strata never renders below native resolution: no render scale below 1, no dynamic resolution, no temporal upscaling. The price is a GPU cost that does not adapt.
- Four layers make the quality in effect: the section's default, the project's value, the player's choices and the command line's preset. The renderer reads the result by a version number.
- A cost row switches a player to Custom, from the look in effect. A preset choice keeps only the preset and the players' rows. A bad options file gets ignored and never rewritten.
- A script's `Graphics::Set` reaches the service, which changes the version; the renderer's next draw calls `SetQuality`; a frame with no change costs a few comparisons.
- A new row needs a member, a line of values, `GetPreset`, `FromSectionValue`, `ToSectionValue`, a field, `Clamp`, renderer use, a traits line, tests and a section version.

## Check yourself

1. A scene enables motion blur. A player sets the `MotionBlur` option to `Off`, then another player sets `AntiAliasing` to `TAA` for a scene that had anti-aliasing off. Which statement is right?

   - A. Both choices only disable effects.
   - B. The first disables the blur; the second enables anti-aliasing, which the row allows.
   - C. The second is refused, because players may never enable an effect.
   - D. Both are refused, because the preset decides them.

   :::answer{tests="player-rules"}
   B is right. The four comfort rows only disable, and the anti-aliasing row is a preference that may choose a method. A is wrong for the second choice. C is wrong because anti-aliasing is the one row that may enable. D is wrong because no preset decides a players' row.
   :::

2. A project sets its preset to `Medium`, and a player chose `High` last week and saved. The designer changes the project to `Ultra`. What does the player see, and why?

   :::answer{tests="layers"}
   The player still sees `High`. The player's choice lies over the project's value, so the preset keeps its source `Player`. A `--quality` option on the command line would win over both. The editor's page says so, and **Reset Player Options** deletes the file.
   :::

3. Why does a frame in which nothing changed cost only a few comparisons?

   :::answer{tests="trace"}
   The service compares the project's settings version with the one it read, and the renderer compares the service's version, which changes only when the effective value, its source or the player's choices change. With an equal version it keeps the settings it has. `SetQuality` then compares the knobs and returns at once when they are equal, so it makes nothing again.
   :::

4. A friend proposes a `Low` preset that draws at three quarters of the screen's size. Give one reason Strata refuses, and one cost of refusing.

   :::answer{tests="native"}
   The image would be softer than the screen can show, against the owner's direction for a realistic image that is never smeared. The cost is that a machine that is too slow has no automatic remedy: someone must lower a cost row, because the engine never shrinks the picture.
   :::

5. Which statement about the file `GraphicsOptions.json` is wrong?

   - A. Only `GameGraphicsService` reads, writes and deletes it.
   - B. A load never rewrites a file it finds bad.
   - C. `Save` writes it atomically.
   - D. A file with two members for one field is read and the later one wins.

   :::answer{tests="player-rules"}
   D is wrong: a file in which two members name one field is no options file, and it is ignored with one warning. A, B and C are true: one owner avoids two writers, a bad file keeps its evidence, and an :term[atomic write]{id=atomic-write} never leaves a half file.
   :::

6. Which change does a new quality row not need?

   - A. A line in the traits table.
   - B. A rise of the section's version.
   - C. A change in the scene file of every sample.
   - D. A Custom value in the feature test project.

   :::answer{tests="add-row"}
   C is right: a row changes the cost of drawing, never a scene's stored look. A is needed because the page and the players' options read the traits. B is needed because stored values at an older version must read the new default. D is needed because the feature test fails for a row it never exercised.
   :::

## Exercises

1. **Basic.** A row set to `AutoFine` resolves to 4096 below 1440 output rows and 8192 from them. With five cascades of 4 bytes a texel, compute the memory of the cascades at 1080 and at 2160 rows. Then check it with the sketch.

   :::answer[Worked solution]{tests="native" solution="sketches/image-quality-settings-cascades.cpp"}
   At 1080 rows the side is 4096, so the memory is 5 × 4096 × 4096 × 4 = 335,544,320 bytes, which is 320 MiB. At 2160 rows the side is 8192, so it is 5 × 8192 × 8192 × 4 = 1,342,177,280 bytes, which is 1280 MiB. The sketch repeats the same sum, and it shows the jump at the threshold.

   ```cpp sketch="image-quality-settings-cascades.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <initializer_list>

   constexpr uint32_t c_HighResolutionRows = 1440;

   // The side of one cascade for a row set to AutoFine: it follows the output's rows.
   uint32_t ResolveAutoFine(uint32_t outputRows)
   {
   	return outputRows >= c_HighResolutionRows ? 8192 : 4096;
   }

   int main()
   {
   	const uint64_t cascades = 5;
   	for (const uint32_t rows : { 1080u, 1439u, 1440u, 2160u })
   	{
   		const uint64_t side = ResolveAutoFine(rows);
   		const uint64_t bytes = cascades * side * side * 4; // One 32-bit depth value per texel
   		std::printf("%u rows: side %llu, %llu MiB\n", rows, static_cast<unsigned long long>(side),
   			static_cast<unsigned long long>(bytes / (1024 * 1024)));
   	}
   }
   ```

   ```text output-of="image-quality-settings-cascades.cpp"
   1080 rows: side 4096, 320 MiB
   1439 rows: side 4096, 320 MiB
   1440 rows: side 8192, 1280 MiB
   2160 rows: side 8192, 1280 MiB
   ```

   1. **Line 10:** the row resolves by the output's rows, with a jump at the threshold.
   2. **Lines 15–19:** five cascades, each a square of 32-bit depth values.
   :::

2. **Medium.** Trace it yourself: a script calls `Graphics::Set("ShadowCascades", 3)`. Name the file and function of each step from the SDK to the call of `SceneRenderer::SetQuality`. Say on which frame the picture changes, and what a frame with no change costs.

   :::answer[Worked solution]{tests="trace"}
   The SDK's `Graphics::Set` in `StrataScriptCore/Include/StrataScript/Graphics.h` calls the host function `GraphicsSetOption`. `HostGraphicsSetOption` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` checks the value and calls `GameGraphicsService::SetOption` in `Strata/src/Strata/Runtime/GameGraphicsService.cpp`, which switches to Custom, validates the merged value and computes a new version. `GameRenderer::FollowQuality` in `Strata/src/Strata/Runtime/GameRenderer.cpp` sees the new version at the next draw and reads the value; `ApplyQuality` then calls `SceneRenderer::SetQuality`, which releases and makes again the cascades. The picture changes from the next frame the renderer draws. A frame with no change costs one version comparison and one comparison of the knobs.
   :::

3. **Hard.** Add a row: a cap on the levels of the bloom. List every place you change, in order, and say what happens if you forget the section's version.

   :::answer[Worked solution]{tests="add-row"}
   First, a member of `RendererQualitySettings` with the value of `Medium` as default. Second, a line `c_BloomLevelsRow` with a value for each preset, and a line in `GetPreset`. Third, lines in `FromSectionValue`, `ToSectionValue` and `Clamp`, and a field of the section, with a title and a description of its effect and cost. Fourth, the renderer's use on both draw paths, and any cache keyed on the value. Fifth, a traits line with its GPU stage and, if the row allocates, a memory function.

   Sixth, a check in `Renderer.Quality`, a Custom value in the feature test project and a cost line in the guide's table. Last, raise `c_SectionVersion` by one, so that values stored at the old version read the new field's default.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/RendererQuality.h` and `RendererQuality.cpp`: the settings struct, the rows, `GetPreset`, `Clamp`, the section and the traits.
- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: `SceneRenderer::ApplyQualityOverrides`.
- `Strata/src/Strata/Core/EngineServices.h`: `IGameGraphics`.
- `Strata/src/Strata/Runtime/GameGraphicsService.cpp` and `GameRenderer.cpp`: the service and the renderer's pull.
- `StrataScriptCore/Include/StrataScript/Graphics.h`: the SDK.
- Suites: `Renderer.Quality`, `GPU.SceneRenderer.Quality`, `Runtime.GameGraphics`, `Scripting.Graphics`, `Editor.GameGraphics`.
- Command: `graphics.resetPlayerOptions`; option: `StrataRuntime --quality`; section: `Renderer.Quality`.

## Further reading

- The engine's own Manual page on graphics quality (beginner): the presets, where quality is chosen, the players' options.
- The engine's Developer Guide, "Quality settings" (advanced): every row, the traits and the rules in full.
