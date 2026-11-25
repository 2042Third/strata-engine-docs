# Notes: make/commands

## Since

0.3.0: StrataCLI `launch`, `list` and `call cmd @file` (inventory gamedev:247, "0.3.0").

## New terms

None proposed. The page defines "command" and "command-line client" in bold inline; the glossary homes none here.

## Requests

- Downloads of the book: `tutorials/make/commands/scatter.json` (200 coin instances, 20 by 10, 2 m apart), `controller.json`, `layers.json`, `shot.json`, `batch.json` shapes are shown inline; the end states of make/animation, make/large-worlds, make/reflections (courtyard with probe) and make/gi (room with GI on) are named as downloads.
- The page uses a hand-run command list: `exercise-1.tutorial.json` assumes `Prefabs/Coin.stprefab` carries the tag `Coin` and the Coin Run end state holds no coin entity in the edited scene.

## Not verified

- The exact text of a status pill and the chip: read from code (`EditorLayer.cpp`, `ViewportPanel.cpp`), not seen on screen.
- Answer shapes of `animation.createController`, `lighting.bakeProbes` and `viewport.capture` are described from their descriptions, not run.
- That `Idle` and `Walking` are the clip names of the robot (from make/animation).
- `list --json` output shape (schemas per command): taken from the usage text.

## Findings not applied

- critic-make-b2-2: the starting projects are named per step as downloads, but make/reflections and make/gi were not yet written at the pin of this page; their end states are only named.

## Clerk

- No term or word asked.
- Left for the planner: the downloads the page names (scatter.json and the others), the exercise's assumptions on Prefabs/Coin.stprefab.

## Tutorial run

- 2026-11-23, pin 822a7a46: exercise-1 (start from make/project-coin-run) passes. The run showed the Coin Run end state
  holds no tagged coin before the scatter and the prefab's root carries the tag `Coin`; the undo step is named
  `Instantiate 200 entities`.
- `prefab.instantiate` with `instances` numbers every coin whose name a sibling has when it is made, so the first coin
  is `Coin (1)`, the second `Coin (2)` and the last keeps `Coin` (as its description says). Step 1's "You should see"
  said `Coin`, `Coin (1)` and on: mended, and the file checks the first, second and last coin's name and Translation.
- 2026-11-24, pin 319075e3: the final run. The pin-build run was already current; exercise-1 passes as written with
  the official v0.8.0 package (Strata-0.8.0-windows-x64.zip), and `tutorials.py check --release` finds nothing.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package (`docs-work/walkfix-G10`): `world.setLayers` with `Worlds/Meadow` fails ("no asset
  'Worlds/Meadow'"), with `Worlds/Meadow.stworld` it adds `Decals` (32 m cells, 128 m) and one undo removes it;
  `StrataCLI list` prints 160 lines, the commands and `rpc.handshake`, `rpc.authenticate`, `rpc.ping`,
  `rpc.listMethods`; `animation.createController` and `animation.preview` as the page says; `lighting.bakeProbes {}`
  on the download of `make/reflections` fails ("The scene has no active reflection probe"), and with the page's step 6
  probe it writes `Lighting/Main/<probe id>.hdr`; the `gi` capture on the result of `make/gi` completes.
- Page and file mended (WK11 to WK14): exercise 1 copies `scatter.json`, so its solution download holds it; the projects
  are linked; the world's path has its extension; the list's `rpc.` lines; the probe is added before the bake.
- Run 2026-11-24, pin build and package: exercise 1 failed both times in its chain, `make/project-coin-run` stage 3
  (`log.read` finds no "script 'BallControl' has no field 'Speed'" among the newest 50 messages), before its own stage;
  that is the chain's (`make/input` is being changed in the worktree). The solution zip was written with
  `scatter.json`. To run again once the chain passes.
