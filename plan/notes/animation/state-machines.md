# Notes: animation/state-machines

## New terms

- simple mode: the animator without a controller, which plays the component's clip and runs no state machine; home: this page; aliases: none.

## Since

0.3.0: the controller asset and its validation are listed for 0.3.0 (inventory animation:53-55).

## Requests

- Names for names.txt: Mecanim, Esoterica, Morpheme (engine and tool names, cited in Further reading).
- Layouts: settled by the photographer (see ## Figures): `layouts/asset-tab-controller.ini` was made; the fade uses `layouts/materials.ini`.
- External hosts: the Unity manual, Unreal Engine documentation and Game Engine Architecture are cited without links.
- The robot's state diagram is a Mermaid diagram on this page, not a shared figure file; `make/animation` may link or repeat it.

## Figures

- robot-asset-tab, round 1 (provisional build): the Asset tab of `Animations/Robot.stanimator` selected with
  `selection.set`, in a new layout `layouts/asset-tab-controller.ini` (1280 × 1280, the Asset tab 700 × 1202 px) so that
  all five parameters, six states and fourteen transitions show without scrolling. Passed; the caption holds.
- robot-inspector-fade, round 1 (provisional build): the written recipe started play and showed the Inspector with no
  input and no selection, so no fade could show. It now plays the course 47 steps with Move held from step 0 and Run from
  step 40, and selects Robot. The picture shows State "Walk → Run", Time 0.09 and Speed 6.500. The Inspector shows no
  fade progress, so the caption no longer claims one; it uses the existing layout `layouts/materials.ini`, and
  `layouts/inspector-animator-fade.ini` is not needed.
- Both, round 2 (pin v0.8.0, 319075e3): `waitsFor` removed (the pin has `editor.screenshot`), taken without
  `--provisional` and published. robot-asset-tab shows 5 parameters, 6 states and 14 transitions, nothing cut;
  robot-inspector-fade shows State "Walk → Run", Time 0.09 and Speed 6.500. Captions and alt hold; recipes unchanged.

## Not verified

- That the loader logs the reason when `Create` refuses a controller (the page says only that the controller never reaches an animator).
- That previews set `AnimatorSettings::Transitions` to false (taken from the inventory and the header comment).
- The upper-body layering claim about Strata has no counterpart checked in `animation/limits`.
- Behaviour of Mecanim, Unreal animation blueprints, Esoterica and Morpheme is stated generally and cited in Further reading only.

## Findings not applied

The brief lists no open findings.

## Clerk

- Admitted the term simple mode, homed here.
- Admitted to names.txt: Mecanim, Esoterica, Morpheme.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
