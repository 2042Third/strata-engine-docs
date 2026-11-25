# Notes: editor/program

## New terms

None proposed. Defined in bold: editor (a separate program that links the engine), model and view, editor core, editor host, EditorContext (glossary homes).

## Requests

- Figure editor-docked (src/content/figures/editor/program.json): needs the layout layouts/editor-program.ini (Hierarchy, Scene view, Inspector, Content Browser docked), project sample ThirdPerson; waitsFor tier 2: editor screenshot.
- The Mermaid diagrams (editor and game, three layers, one frame) are not rendered by me.

## Not verified

- The table's "Used by" column and the claim that Unity, Unreal Engine and Godot run the game inside the editor: from general knowledge, cited only in Further reading.
- That the recovery journal keeps changes after a crash (named from inventory and the idle-timeout message, SceneRecovery not read).
- That the command-line client's and runtime's usage errors use exit code 3 (comment in CommandLineOptions.h).
- PowerShell Start-Process -Wait -PassThru line of exercise 1 was not run.

## Findings not applied

None open in the brief; new:47 (two headless options) applied.

## Since

0.3.0: inventory editor-core:39 lists the core/UI split as release 0.3.0.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- editor-docked: layout layouts/editor-program.ini made (960 x 540, copied from first-game-960 with the Inspector widened
  to 340 px and the bottom tabs raised to 160 px). The steps open Scenes/Course.stscene (the project opens MainMenu),
  build the scripts, select the Crate and frame it. Round 1 failed because Crate is not in MainMenu. Round 2 cut the
  Translation's Z value and showed only the Content Browser's toolbar. Round 3 is readable and taken with the
  provisional build only; waitsFor stays. The page's example selects the first game's cube; the picture uses
  ThirdPerson's Crate, and the caption names it.
  Round 4 (viewer's faults): the Crate was about 25 px wide under the gizmo; camera.set now stands at [2.5, 3, -26]
  looking at [0, 1, -30.5], so the outlined Crate is about 70 px wide, a sixth of the Scene view. The caption now
  begins with the ThirdPerson sample's Course and says the Crate stands in for the example's cube. Provisional only;
  waitsFor stays.
  Pin v0.8.0 (319075e3): taken without --provisional in one round with the same recipe and published. It shows the
  Hierarchy with the Crate selected, the outlined Crate in the Scene view, the Inspector with Translation 0, 1.05,
  -30.5, the Content Browser and the toolbar with Play; caption, alt and shows hold. The manifest had no waitsFor line
  left to remove.
