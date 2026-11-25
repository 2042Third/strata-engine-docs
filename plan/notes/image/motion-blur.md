# Notes: image/motion-blur

## Since

0.7.0: the gather shader was added on 2026-11-02 (commit 3735800b of the engine); no release tag found that contains it, so the value is an estimate.

## New terms

None proposed. The page defines the glossary's three terms: shutter angle, sample-and-hold blur, tile max (neighbor max).

## Requests

- Name for the prose: McGuire (the published reconstruction filter is cited in Further reading only; prose says "a published gather filter").
- Figures: three scene figures from the look-dev shots tp.live.turn, tp.live.turn.mb90 and tp.live.turn.mb180 of the ThirdPerson sample, to be taken. The brief's crop of the far course and the robot is the shots' own crops.

## Not verified

- The "Who uses it" column of the alternatives table (film renderers, papers, older engines, temporal renderers, cheap passes) is general knowledge, not checked.
- The toy's claim that the real pass sits after depth of field and before bloom comes from the source order in SceneRenderer.cpp, not from a run.
- The interface and overlays never blur: taken from the rule in the inventory; the code shows only that the pass works on the scene color.
- Further reading entries (McGuire and others 2012; Jimenez 2014) are cited from memory.

## Findings not applied

The brief lists no open findings.

## Figures

All three (turn-off, turn-mb90, turn-mb180) are taken at the pin 319075e3 as live figures and published (2026-11-24).

- Round 1 (2026-11-17): the recipes were kind `scene`, so the game never ran and every still was the same sharp frame:
  the capture renderer never blurs (`ViewportRenderer.cpp:225`); only a live capture of the Game view does. The recipes
  became kind `live` and waited until `take` took them.
- Round 2 (2026-11-24, live): the copy started at the project's start scene, the main menu ("SKY ISLANDS", buttons),
  where the Look action does nothing; the three pictures were the same menu frame. Cure: `scene: Scenes/Course.stscene`.
- Round 3: on the course the turn of the shots (`Gameplay/Look` at 0.1875 from step 1) moved the far course about 8
  pixels per frame, a blur of 2 and 4 pixels: under TAA's softness, the variants differed no more than two takes of one
  variant (1.1 % of pixels against 0.9 %). Not visible at the page's width.
- Round 4 (published): Look at 0.75 from step 24 (a fast turn of about 12 degrees by step 30, so the far course stays in
  the frame). The far course moves about 30 pixels per frame, so by the page's formula the blur is about 7.5 pixels at
  90 degrees and 15 at 180, both under the clamp (21.6 at 1080 rows). Differences from turn-off: 1.7 % of pixels at 90,
  3.7 % at 180 (takes of one variant: 1.0 %). By eye: turn-off sharp; the far course, the coins and the trees smear
  sideways at 90, about twice as far at 180; the robot stays sharp in all three, since the camera orbits it.
- The page's lead-in now says the turn is fast and around the robot, and why the robot stays sharp; the captions name
  the trees beside the far course. The exercise that runs the shots `tp.live.turn.mb180` and `.mb90` still names the
  slower look-dev shots: their streaks are short (2 and 4 pixels at that motion), which the exercise asks the reader to
  measure.
- Round 5 (2026-11-24, viewer's report): the near trees (the round tree at the left edge, the pine at the right) stay
  as sharp as with blur off; only the far course and the mid pine at the left streak. The captions, alts and the
  lead-in now name the far course and the pine at the left, and say the near trees stay sharp. The `edge` crop framed
  the round tree, alike in all three; it became `course` ([0.15, 0.08, 0.47, 0.5], the left pine and the far course,
  shown near full size so the 7.5 pixel streak reads), and the mb90 caption points the reader at the far islands there.

## Clerk

- Nothing asked.
