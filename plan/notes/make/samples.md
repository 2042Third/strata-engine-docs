## New terms

None.

## Requests

- Layout `layouts/samples.ini` for the three editor figures (pit, tour, outpost); a Play view layout is enough.
- Figures waited for tier 2: editor screenshot; met by the pin v0.8.0 (2026-11-23).

## Since

Samples: Physics Playground and Open World 0.5.0 (inventory gamedev:256-257); Showcase is wave 8. since set 0.5.0.

## Not verified

- The Hierarchy search field and the Inspector check box for a bool field exist as described.
- The button names of the Playground tool panel were not read from the scene.
- The size of the copies (about 33, 92 and 132 MB) is from the folders of the pin, not from a copy.

## Findings not applied

- Brief figure for the Playground's grab and slow motion, the Open World's night with camp fires and teleport fade: no existing pictures at the pin; only three figures requested.
- The second `until` of critic-make-b2-15 is applied: the regression is quoted and said to live in the repository, not the archive.

## Clerk

- No term or word asked.
- Left for the planner: `layouts/samples.ini` and the three figures.

## Figures

- Taken with the provisional build only (2026-11-18); all three wait for tier 2: editor screenshot and are not published.
  They picture the Game panel of `layouts/first-game.ini` (1280 × 720, panel 797 × 499), so `layouts/samples.ini` was not made.
- pit: play 180 steps, click Pour, 300 steps, key 5 (Station5 looks at the pit), 90 steps. Round 1 good: the glass pit
  full of red, blue and dark balls, the tool panel, 815 bodies. Caption now names the colors it shows, not "four materials".
- tour: round 1 (300 steps) and round 2 (660 steps) both show the forest from the air with the sea fading into haze; the
  tour looks outward, so the central peaks are not in view. Caption rewritten to the forest and the haze.
- outpost: wait for physics to load, 240 steps, Tab, P. Round 1 good: the photo panel's sliders (time of day 17:45,
  exposure, field of view, focus, aperture) over the valley with the bus small in the middle.
- Mended after a viewer's report (2026-11-18, provisional build again):
  - pit: at the 797 px Game panel the canvas (ScaleWithScreen, 1920 × 1080 reference) drew the pixel font at about 8 px,
    and "Pour 100 Balls" read as "POLA 130 BALLS". New layout `layouts/make-samples-wide.ini` (1920 × 1080 window,
    Game panel 1316 × 850): the labels read at 1:1 and still at the 768 px column. The alt no longer quotes the body
    count.
  - pit, words for the page: the counter reads 815 after one pour of 100, so the arena holds about 715 bodies before it
    (500 balls, 64 dominoes, crates, pins, ghost boxes); "about 600 bodies" in "The Physics Playground" should read
    "about 700 bodies".
  - outpost: Tab left the camera over the valley, the yard in the ridge's shadow and the shelter cut. The recipe now
    presses **2** (bookmark 2, the tour's bus shot at golden hour) instead of Tab: the rusty bus and the oil tank, lit
    warm, with the panel over the bus's rear. Alt and shows name the bus and the tank; the hut is not in this view.
- Settled 2026-11-18: "about 600 bodies" stands. The scene holds 615 tagged bodies (500 Ball, 64 Domino, 33 Crate, 10 Pin, 8 Ghost); the take's 815 is two pours, the click's and the one `Playground`'s `AutoDemo` (on by default) makes 6 s after the start. Step 3's "You should see" now tells the reader about the game playing by itself and the counter growing by 100 per pour.
- Published at the pin v0.8.0 (319075e3, 2026-11-23): the three `waitsFor` lines removed as `check` asked; one take
  without `--provisional`, one round each. pit: the glass pit full of red, blue and dark balls, the tool panel's
  labels readable, Bodies 815 at the top right. tour: the forest from the air, palms on the shore at the left, pale
  haze at the horizon, "Tour (any key: take over)" at the top left. outpost: the rusty bus and the oil tank in warm
  low light, the photo panel on the right (time of day 17:45, exposure, field of view, focus). Captions unchanged.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package (`docs-work/walkfix-G10`, `results-all.json`): the `Playground` script sits on the
  entity `Game` (`entity.find {"name": "Playground"}` is empty); after `script.setField` in edit mode,
  `project.openSample` refuses ("has unsaved changes") until `scene.save`. Sizes as files (the walker's figures and the
  old page's were disk use on an exFAT drive with large clusters): Playground 28 MB opened, 41.5 MB built and played;
  Open World 19.4 MB, 42.5 MB; Outpost 347 MB opened (its import cache 283 MB), 362 MB played; the three about 446 MB.
  The samples as shipped: 7.6, 16.8 and 79.5 MB.
- Page mended: steps 4 and 6 name `Game` and `Player` with `entity.find` and save; the sizes.
