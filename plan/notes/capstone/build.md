# Notes: capstone/build

## New terms

None. The page defines no term in bold.

## Requests

- Editor figures `result`, `both-zones`, `radius-reason`: layout `layouts/capstone-build.ini` (Scene view, Hierarchy and Inspector open). They name the basic3d template as a stand-in and wait for `tier 2: editor screenshot`: the real recipe needs the checkpoint project of `editor/tutorial-command` (two zones, a floor, dynamic crates) and the patched editor.
- The tutorial file names no `patch.pictures`: the schema allows only `file` and `tests` under `patch`.

## Not verified

- The checkpoint scene's coordinates are unknown, so the terminal steps use an empty scene with their own zones.
- Layout and look of the three editor figures.

## Findings not applied

- critic-capstone-8 (layers): applied as a one-clause decision in section 1 (every layer; Radius never scaled by the entity's scale, as the chain's sphere gizmo already does); a mask property is left for later.
- critic-capstone-1, -2, -15: applied (selection step with `allColliders` command; Gust of the feature scene moved to (8, 1, -40) because it reached the Compound body at 6.2 m; edits while playing).
- critic-capstone-11 concerns capstone/land.
- Brief section 7 and each section's "checkpoint and text capture": no checkpoints (the card forbids them in a patch tutorial); build and test results are told in words.
- Brief's second exercise patch: only the gust exercise (exercise 3) has a worked patch; the Falloff exercise (2) has a written solution without a patch.
- Chain inconsistency: `IWindZones::GetStrengthAt` (host-function chapter) still tests Radius for both modes; this patch leaves it, so `Wind::GetStrength` and `Wind::GetForceAt` differ for a directional zone beyond its radius.

## Figures

Photographer, 2026-11-18, round 0 for all three: nothing taken. The pin has no wind zone (no `WindZone` in `Strata/src` or in the dumps' `components.json`), and the provisional build has none either (`StrataEditor.exe` holds no `WindZone` string). The component, the wind system, the arrow gizmo and the inactive reason exist only in an editor built from the capstone chain's patches, which is the reader's own work: no later pin will carry them, and `tools/figures.py` has no kind that builds a patched engine. The recipes stay as the writer left them (basic3d stand-in, placeholder steps, the missing layout `layouts/capstone-build.ini`, `waitsFor` kept).

- `result`: needs the patched editor and the checkpoint project of `editor/tutorial-command` (two zones, a floor, dynamic crates). Its caption also tells motion ("drift", "scatter"), which a still shows only against a picture of the crates before play. Proposed instead: a drawn top view (an SVG) of the floor, the crates' rows, the directional zone's arrow and the spherical zone's circle, with each crate's path drawn as a short arrow; or, with a patched build, a pair of stills before play and after a few seconds of play.
- `both-zones`: needs the patched editor's arrow gizmo and the wind zone's sphere gizmo. Proposed instead: an SVG of the Scene view's two gizmos (a sphere of the zone's radius around one zone, an arrow of 2 m along the other's -Z), both in the collider color, beside crates; the step's "You should see" already says what it shows.
- `radius-reason`: needs the patched editor, and the tooltip is a hover tooltip, which commands cannot show even with that build. Nearest honest picture at the pin, of the pattern the section copies: the Inspector (panel `Inspector`) of an entity whose UI Canvas is in screen space, with its dimmed `WorldUnitsPerUnit` row (`Strata/src/Strata/GameUI/GameUIComponents.cpp`, reason `WorldSpaceOnly`), or of an Animator with a Controller set and its dimmed `Clip` row (needs a controller asset). Its caption would say the row is dimmed and not name the tooltip; or a text figure of `component.get` on that entity, whose `inactive` member carries the reason as text. Either would need the page's words beside the figure to say that the picture shows another component's reason.

Photographer, 2026-11-23, at the pin 319075e3 (v0.8.0), round 0 for all three: still nothing taken, all three blocked.
The pin has `editor.screenshot` and the `waitsFor` lines are gone (09c20ead), but it still has no wind zone: no
`WindZone` or `Wind` in `Strata/src`, none in `reference/_dumps/319075e3…/components.json`, and no `WindZone` string in
the Release build's `StrataEditor.exe`, `StrataRuntime.exe` or `StrataCLI.exe`. The layout `layouts/capstone-build.ini`
is still missing. A take of the recipes as written would show an empty basic3d scene, either playing or with nothing
selected, so none of the three captions would hold. The figures need a kind that builds the editor from the capstone
chain's patches and opens the checkpoint project. Until that kind exists, the nearest honest pictures are the ones
proposed above (the two SVGs; for `radius-reason`, the dimmed `WorldUnitsPerUnit` row of a screen-space UI Canvas,
with the page's words saying that it shows another component's reason). The recipes are left as they are. A
`waitsFor` naming the patched engine would keep `figures.py list` from showing them as ready to take.

Finisher, 2026-11-24, at the final pin 319075e3 (v0.8.0, rulings-12 R55): the three figures are `blocked` (the pin has
no wind zone; the reasons stay in the manifest as the request for a later edition) and each names a stand-in that the
page places in its place:

- `result` → `wind-pushes`, a drawing: a top view with one zone in each panel, the directional zone (turned 90 degrees
  around Y) giving every crate (-20, 0, 0) N and the spherical zone of 5 m pushing the crates inside it away from its
  center, with the introduction's crate at (3, 0, 4) and its (12, 0, 16) N. The lead-in says the drawing shows the
  first promise from above.
- `both-zones` → `wind-gizmos`, a drawing of the two gizmo shapes in the collider color: the wire sphere of Radius as
  typed, and the arrow of `c_WindArrowLength` (2 m) along -Z. Lead-in: "the two shapes that the renderer receives".
- `radius-reason` → `robot-clip`, a picture taken at the pin: the Inspector of the ThirdPerson sample's Robot
  (Course.stscene, its Animator's Controller set), whose Clip row is dimmed by `WithoutController`, the reason the
  section's step 1 quotes. The lead-in says the reader's Radius row will look like it. No tooltip (needs the pointer).
- The page was at 6,487 prose words before (size L ends at 6,500); captions and lead-ins of the stand-ins added about
  100, so the old figures' captions were shortened and six repeats of the page were cut (step 3's guard list, the
  IBodyControl Why's last sentence, the Lines 9-13 note, the MarkTransformsChanged repeat, the ColliderEntities repeat
  of the gizmo step, the reason function's You should see).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Settled with the editor (2026-11-18)

- `radius-reason`: the Inspector shows an inactive reason only as a tooltip under the pointer (`StrataEditor/src/UI/PropertyWidgets.cpp`, `PropertyLabel`), which a take cannot show. The step's You should see now says how to make the tooltip appear; caption, alt and shows name only the dimmed row.
- `result`: the caption no longer tells motion (drift, scatter); it says where the crates stand after the wind pushed them.

## Tutorial run

- 2026-11-24, pin 319075e3: the patch and exercise-3 apply on the chain from capstone/plan and pass as written (`Physics.WindZone`, `Scripting.Wind`, `Editor.Journal`, `Architecture.Layering` and the feature test). The first round's build of the tutorial failed to link (`GetWindForceAt` unresolved): the patch adds `WindForce.cpp`, and the glob check reconfigured inside that build, after MSBuild had loaded the old projects; the second round, unchanged, passed.
