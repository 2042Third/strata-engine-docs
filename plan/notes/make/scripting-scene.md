# Notes: make/scripting-scene

## New terms

None proposed.

## Since

0.3.0: StrataScriptCore/Include/StrataScript/Scene.h exists at tag v0.3.0 (git ls-tree of the pin).

## Requests

- Names or words: none (the page passes word-list).
- Figure: none drawn. `## Result` has no picture and no download link of its end state; the page's tutorial files hold the finished `Coin.cpp` and `CoinPlacer.cpp` (tutorials/make/scripting-scene/).
- The end-state download of the tutorial is made by `tutorials.py compile`, not by me.

## Not verified

- The Coin prefab has the tag `Coin` and the Coin script on its root, the scene has an entity `Ball`, and `Materials/GoldGlow.stmat` exists: these come from the brief's starting state and earlier pages.
- The tutorial JSON starts from `make/first-script`, whose own tutorial file (a Spinner cube) differs from the brief's Coin Run state; its stages here are not run.
- The Hierarchy panel's **+** button (the preset **Empty** is in SceneHierarchyPanel.cpp); **Copy Values** copying name and values as JSON (finding evidence only).
- (Verified by the tutorial run of 2026-11-18: `Coins placed: 5` prints in the placing frame, and the glow finds the Mesh Renderer on a descendant of the prefab root.)
- That `IsLoaded` on a prefab means its meshes are drawn complete (the page uses `GetLoadProgress` for that).

## Findings not applied

- critic-make-a-2, -3, -4, -5, -6, -22, -25: applied (material swap in step 7, `GetEntity` before step 5, finds see inactive entities, registered names, value types, **Copy Path**, whole `Instantiate` call).
- critic-make-a-12: applied as far as this page goes (step 4 removes the five hand-placed coins); the other pages' changes are theirs.
- Brief: the typed accessors (`GetRigidBody` and others) are not named beside the pages that use them; the table of classes covers the namespaces only.

## Tutorial run

- 2026-11-18, against the pin's Release build. No page before this one makes `Materials/GoldGlow.stmat` (materials and
  lighting change `Gold` only), so step 7 now makes it with the page's values (Gold's, Emissive Intensity 1000) and the
  prerequisite line is gone.
- The file had four stages for nine steps and copied the final scripts early; it now has one stage per step, with
  `script.create` in step 2, `CoinPlacer.step3.cpp`, `Coin.step5.cpp` and `Coin.step7.cpp` for the steps between, and
  checks of the bob heights, `Coins placed: 5`, the five children of `Coins`, the glow material (1000 nits) and the
  collected coin. The final `Coin.cpp` keeps the warning about a missing `Ball` that step 5 adds (line callouts moved by 2).
- Step 8 said no command moves the ball: `component.set` moves it in the running copy, and the tab now says so. Steps 6
  and 9 read placed coins, which exist only while the game plays: their tabs say so.
- Exercise 2 now plays and checks that the coins are off after five seconds, hold their height while off, and are on
  after eight.
- 2026-11-24, final runs at pin 319075e3: the pin build's stamp was current; the official v0.8.0 package passes the
  tutorial (9 stages) and exercise 2 as written.
- 2026-11-24, track G walk segment 5 (WK4-WK6): the page quotes the files whole (step 1's `Coin.step1.cpp` in two
  parts, step 3's `CoinPlacer.step3.cpp`, step 4's `CoinPlacer.cpp` from line 7 on), gives `entity.delete` its
  `entities` list, and the ball's start (0, 0.5, 6). The package's first run failed in the reader's copy of stage 6:
  stepped paused from a fresh editor, the 47 steps ran before the coin prefab had loaded (`entity.find` empty,
  `Coins placed: 5` after it). Stages 6, 8 and 9, which read placed coins at a given step, now start with a play that
  waits (`until`, 60 s) for `Coins placed: 5` from the `Script` logger, so the prefab is loaded before the timed play;
  a reader's play does not step, so the page is unchanged there. Passed with the pin build and the 0.8.0 package.

## Clerk

- No term or word asked.
- Left for the planner: the Result picture and the end-state download (tutorials.py compile).
