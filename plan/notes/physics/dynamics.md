# Notes: physics/dynamics

## New terms

None proposed. Effective mass is explained in a sentence, not bold (the brief names it with the inertia tensor); the planner may give it a glossary entry.

## Requests

- Extra word: "solver" is on no word list (22 uses avoided on this page); the book's physics pages would use it.
- External hosts for Further reading (cited without links now): box2d.org (Catto, Solver2D and soft step), matthias-research.github.io (Position Based Dynamics).
- Figures: pit-pouring and pit-resting (Physics Playground, `play.steps` 60 and 1500). The brief asks for the crate tower and the domino run at exact fixed steps; a recipe for the dominoes (the tool panel starts them) is not known to this page, so they are not requested.

## Since

since 0.3.0: physics module of the first releases; continuous collision "Fast bodies" in Release 0.5.0; the `Physics.Simulation` section 0.7.0.

## Not verified

- box3d wakes an island when an awake body touches it (stated from general knowledge of the library).
- The relax pass description (solves again after moving) read from stage order in `solver.c`; whether contacts drop their push-out bias there was not read.
- Sequential impulses in Box2D before version 3 and Bullet; position-based methods in cloth (outside the pin).
- That writing a sleeping body's transform without `MarkModified` leaves physics with the old pose (stated as "may").
- Effective mass formula in words only, no formula.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Effective mass is left for the planner (no bold sentence on the page). box2d.org entered the hosts; matthias-research.github.io's front page is GitHub's "Site not found": left for the planner.

## Figures

- `pit-pouring`, `pit-resting`: published after two rounds. The recipes' `camera: "scene"` (the Main Camera at 0, 22, 30) looked at the arena, not the pit; both now look from (17.5, 11, 4) at the pit's centre (10, 0.4, -10.5), fov 40 (round 1 at (16, 9, 1) cut the near glass corner). The sample's game HUD and tool panel draw over the corners; the pit stays clear of them.
- In the pin the pit holds 500 balls lying on its floor when Play starts; the demo (`Playground`, `DemoStart` 2 s + 4 s) pours 100 more as one sheet at y 3 at 6 s. So `pit-pouring` plays 385 steps (6.4 s, the sheet 0.4 s into its fall, above the pile), not 60 (at 1 s nothing falls). `pit-resting` keeps 1,500 steps (25 s); a launched ball lies outside the pit at the lower left.
- Page words the pin contradicts: paragraph 25 says the pit "takes 500 balls" that "pour in"; the 500 are placed before Play and the pour is 100. A picture cannot show sleep; the caption says what sleep needs instead.
- Viewer's review (round 3, captions only, pictures kept): `pit-pouring` now says the 500 lie in rows and where the sheet's shadows fall (the balls just below its near edge); `pit-resting` says the poured balls form the red layer over the middle and back while the near rows are the original floor balls, and names the lone ball outside at the lower left. Probe takes at 450, 594 and 900 steps (not published) show no ball outside the pit at 7.5, 9.9 or 15 s and the pit unchanged from 9.9 to 15 s, so that ball is no poured ball: it arrives after the demo feeds the goal and launches balls at 10 s (Goal 4 of 5 fed at 25 s).
- Pin v0.8.0 (319075e3): both taken again in one round and compared with the published originals (`figures.py compare`): one pixel off by one level each; publish kept both files and stamped the commit they were checked at. Looked at: pour sheet above the floor rows, then the settled red layer and the lone ball at the lower left, as the captions say.
- The page's words still need (planner, page line 25): "a pit holds 500 balls in rows on its floor; at 6 s the demo pours 100 more, which fall, bounce a little, settle in a layer and lie still" in place of "a pit takes 500 balls ... The balls pour in, bounce a little, pile up and lie still". No picture can mend this: the sample places the 500 before Play, and 100 balls over a 9 m pit make a layer, not a pile.
- Viewer's review (round 4, words only, picture kept): `pit-resting`'s "red layer" could not be told from the floor's red balls, and poured reds also lie over the front-middle and front-left rows (enlarged, they sit on top of the rows of red, wood, dark metal and blue). The pour spawns the same `Ball` prefab that makes 125 of the 500 floor balls (125 each of Ball, BallMetal, BallPlastic, BallWood in the scene), so no recipe can colour it apart. Caption, alt and shows now say the poured balls are the same red as one floor ball in four, lie on top of the floor rows, mostly over the middle and back; the "near rows are the original floor balls" claim is gone. No retake: the recipe is unchanged.
