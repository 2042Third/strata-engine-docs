# Notes: assets/extending

## New terms

None proposed. The page defines **text asset** and **loader** in bold for its own use; the glossary homes no term on it.

## Requests

- Host for two Further reading entries, cited without a link: gameprogrammingpatterns.com (Nystrom, "Type Object") and unicode.org (The Unicode Standard, chapter 3).
- The words "comma", "unnamed", "overlong" and "NUL" were avoided instead of requested; no word is requested.

## Since

since 0.3.0: the asset type enum, the loader and importer registries and the feature test's asset check exist from the first tag's asset system (the enum's first values are Scene to Font); the page's steps use only those parts (ColorLookup, the last value, is newer but is only a position in the list).

## Not verified

- That a pack with a Text entry is refused by an engine without the name functions: shown only by IsKnownAssetType in AssetPack.cpp (lines 41-45, 252, 367).
- That the editor reports a dropped `.sttxt` file when no importer reads it: only the comment at ContentBrowserPanel.cpp (dropped files no importer reads) was read.
- That the feature test reads the assets from the clone's StrataTests/FeatureTest/Assets (inferred from GetFeatureProjectSourceDirectory in FeatureTests.cpp).
- Exercise 2 and 3 answers are outlines from the headers (AssetManagerExtension.h, AssetDependencies.cpp), not tried.
- The test name for ctest, `^StrataTests\.FeatureTest$`, is taken from tools/tutorials.py and the component tutorial.

## Names of this page

- `Icons::FileText`: declared at the pin in `namespace Strata::Icons` (StrataEditor/src/UI/Icons.h line 805), which the scope check's `namespace Icons` pattern does not match; the page's patch uses it.

## Tutorial run

- 2026-11-24 at the pin 319075e3: `tutorials.py patch` passes the page's patch and exercise-1.patch (Architecture.Layering, Scene.TextAsset, Asset, Editor.AssetOperations and the feature test). Mended from the 822a7a46 files: the feature handle F7A0000000000012 is taken at the pin (FeatureLightPanel.stmat), so Notes.sttxt takes F7A0000000000013; Editor.AssetOperations (new at the pin) counts the types up to the last value, so the patch changes its `AssetType::ColorLookup` to `AssetType::Text` (hunk 17, a new paragraph in step 4 of "Test the type", suite added to the test command and the tutorial's tests); TextAsset.cpp's `<fmt/format.h>` does not compile in Strata_Scene, so it includes `Strata/Core/Log.h` (spdlog's bundled fmt); exercise-1.patch was a whole diff against the pin and is now the diff on top of the page's patch, as the tool applies it.
- Not run: step 7's sabotage of the rejection test and the feature test's message with the folder moved away (step 4 of the last section).

## Findings not applied

None: the brief listed no open findings.

## Tool problems

- tools/booklib/tutorials.py line 130 skips the folder tutorials/assets, so a tutorial of the part `assets` is never found (`tutorials.py check` reports "a tutorial page needs its tutorial file"). The files stand where the card puts them: tutorials/assets/extending.tutorial.json, extending.patch and extending/exercise-1.patch. The folder name collides with the tutorial assets folder.
- No figures file and no sketches: the only picture is a Mermaid diagram, and an engine-changing tutorial has no checkpoints.

## Clerk

- Not admitted: unicode.org, whose front page answered with the title "Index" and did not show the Unicode Consortium in one fetch; left for the planner. gameprogrammingpatterns.com is already a host.
