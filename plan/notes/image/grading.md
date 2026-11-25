# Notes: image/grading

## New terms

None proposed. The page defines the nine terms the brief lists (3d-lut, color-temperature, daylight-locus, half-texel-remap, planckian-locus, slope, tint, trilinear-interpolation, white-balance) and uses "mired", "chromatic adaptation", "von Kries" and "CAT02" in plain prose, without a bold definition.

## Requests

- Words for `tools/data/extra-words.txt`: von, Kries (the name of the adaptation model), CDL (the color decision list), magenta.
- Hosts for Further reading, cited without a link: the ASC CDL specification (theasc.com), the Cube LUT specification (helpx.adobe.com), Fairchild, Color Appearance Models (a book).
- Figures: `white-balance-sweep`, `grading-compare` and `lookup-sweep` are scene figures for phase B. The brief names an interior lit by lamps for the sweep; the recipe uses the Basic 3D view because the pin lists no such scene. The planner may replace the project.
- Figure not drawn: the CIE 1960 uv diagram of the Planckian and daylight loci with the blend from 4000 to 5000 K and the tint normal (render-image:454). No Mermaid form fits; it needs a reference figure (a sketch that plots the 91 entries of `WhiteBalanceLocus.inl`).

## Since

0.7.0: `Tools/GenerateWhiteBalance.py` and `Strata/src/Strata/Asset/ColorLookupImporter.cpp` first appear in commits contained in tag v0.7.0 and no earlier tag (git tag --contains in the pin clone).

## Not verified

- The numbers of the gray-patch table and of the 4,500 K and 3,200 K examples were computed in Python from the 91 entries of `WhiteBalanceLocus.inl` with the formulas of `GetWhiteBalanceMatrix`; no engine program was run.
- The 44 % blend weight at 4,500 K assumes a weight linear in mireds from 200 to 250, as the generator's header says.
- The statement that the daylight white is shifted by at most 0.00005 follows the generator's header, not a run of the script.
- Which frame first applies a lookup after its import: the page says the first frame in which `ResolveColorLookup` finds the loaded asset with a texture; the order of the finalize step and the frame's resolve was not traced.
- The dummy textures are described as dummies; their exact size was not checked.

## Findings not applied

- Item `new:2` (the Developer Guide's names `m_ColorLookupLayout` and `GetColorLookupSet`): applied; the page uses `m_TonemapInputLayout` and `GetTonemapInputSet`.
- Item `render-image:593` and `render-image:595`: the night look and the LUT exercise are applied; the LUT exercise writes the table by program with a 3-point grid instead of 17, which the brief allows ("written by hand").
- The `Active` flag's role in `GetColorGrading` (the or of the two parts) is described; the line numbers of the brief's `SceneRendererPost.cpp:1335-1348` hold at the pin.
- Item `render-image:454` (the locus diagram): not drawn, see Requests.
- Item `render-image:496` (`tp.lut` crops of the robot and the sky): the recipe keeps the shot without crops because the figure check refuses crops beside a shot.

## Clerk

- Admitted to names.txt: von Kries.
- Admitted to extra-words.txt: CDL, magenta.
- Admitted to external-hosts.txt: theasc.com (its front page is the ASC's). Not admitted: helpx.adobe.com (access denied to one fetch); left for the planner.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken at the pin's Release build, two rounds in one page hold each; all three figures published.

- `white-balance-sweep` (Basic 3D, 5 variants): round 1 passed. Means of the frame against 6,500 K (125, 127, 128):
  3,200 K (51, 127, 183) strongly blue, 9,000 K (138, 129, 114) light tan, tint -1 green, tint +1 magenta. The caption
  now names the mired distances (about 159 against about 43) that make the blue cast far stronger; alt says gray ground.
- `grading-compare`: round 1 (Basic 3D) had no dark parts, so the offset and power had nothing to show. Round 2 uses the
  ThirdPerson sample's `Scenes/Course.stscene` (the sample's start scene is the main menu, whose camera looks at the title
  menu) with the HUD and Menus canvases set inactive. Shadow on the grass (33, 80, 65) -> (33, 76, 52), lit grass
  (76, 158, 114) -> (78, 166, 104): darker, less blue shadows and yellower lit parts. Alt rewritten to that.
- `lookup-sweep` (shot `tp.lut`): round 1 showed the game's HUD; round 2 sets HUD and Menus inactive. The pin's only
  lookup (`StrataTests/FeatureTest/Assets/Lighting/Feature/Warm.cube`) is a mild grade: frame mean (78, 119, 98) ->
  (84, 120, 92) at full intensity, half way at 0.5. Caption and alt now say the grade is gentle (yellower grass, warmer
  clouds) instead of "much warmer, with an orange cast". A stronger lookup would need a file in the pin.
- Rechecked at v0.8.0 (319075e3): `tp.lut` (`Tools/LookDev/Shots.json:61`) opens the ThirdPerson project's
  `Scenes/Course.stscene` (line 6), where `4BC76BF041EAD086` is still the "Post Process" entity holding the scene's
  `PostProcess` component, and `HUD` and `Menus` still name the canvases. The shot, `Course.stscene` and `Warm.cube` did
  not change since 822a7a46, so the recipe and the taken pictures stand. Nothing on the page changed.
- Retaken at v0.8.0 (319075e3) in one hold, one round each, and compared with the published files (`figures.py
  compare`): the five `white-balance-sweep` pictures are pixel-identical; `grading-compare` and `lookup-sweep` (with its
  robot and sky crops) differ by at most 8 levels on single pixels, mean 0.01 of 255, largest block 0.05, below the
  thresholds. Looked at again: same framing and the same off/on and 0/1 differences the captions name. The published
  files stay; their stamps record the check at 319075e3. Captions, alt and numbers unchanged.
- Mended after a viewer's report (2026-11-23), words only; the pictures stay (the result files hold no caption, so
  nothing was retaken or republished):
  - `lookup-sweep`: the caption never named the robot crop. Measured on the crops (yellow pixels of the robot crop):
    red 149.2 -> 155.4, blue 52.3 -> 48.2 from intensity 0 to 1; caption, alt and shows now name the crop and that
    change; numbers says how it was measured.
  - `grading-compare`: the pair follows the paragraph on `ColorLookupIntensity`, so a reader takes it for the lookup.
    The caption now opens with "the slope, offset and power of the grade off and on; no lookup is set in either picture"
    (the results record `colorLookup: false`). For the page's writer: the two `::figure{id=grading-compare}` lines
    belong after the paragraph on the grading shader ("The three `dot` calls ..."), before the lookup's code block.
  - `white-balance-sweep`: the caption used mireds before "Naming the light" defines them; it now says "(a million
    divided by the kelvin)" at first use.
