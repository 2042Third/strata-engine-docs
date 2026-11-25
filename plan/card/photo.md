# Card: photographer

You take one page's engine pictures (`scene` and `text` figures) from its recipes,
`src/content/figures/<part>/<chapter>.json`. You change only that manifest, its published files and `taken.json`, and
`plan/notes/<part>/<chapter>.md`.

## Places

- Book: `G:/GameEngineAI/.worktrees/docs-book` (Bash: `P=/c/msys64/mingw64/bin/python.exe`; node:
  `source G:/GameEngineAI/.worktrees/strata-engine-docs/.tools/env.sh`).
- Pin clone, run only: `G:/GameEngineAI/.worktrees/docs-pin`; build `<pin>/build/windows/bin/Release`.
- Work folder: `G:/GameEngineAI/.worktrees/docs-work/photo/<page-key>`; each take empties it.
- Dumps: `reference/_dumps/822a7a46dbcdd86e8e2eafde7e41d003e27260c8` (below: `<dumps>`).

## Steps for one page

1. Read every `::figure`/`::compare`/`capture=` line of the page and the paragraph before it: that is what the picture
   must show.
2. `$P -I tools/figures.py list | grep <part>/<chapter>`: no rows means no manifest, nothing to take. Rows with
   `waits for` or `blocked`, kind `tool`, `baseline` variants and `ctest` text figures: report, leave. Kind `editor`:
   plan/card/photo-editor.md. Kinds `live` and `runtime`: below.
3. Offline: `$P -I tools/figures.py check --engine ../docs-pin --dumps <dumps> | grep -v note:`. Fix your page's errors.
4. Take, in PowerShell only (the lock lives in PowerShell's TEMP), one page per hold:

   ```powershell
   Set-Location G:/GameEngineAI/.worktrees/docs-book
   python G:/GameEngineAI/.worktrees/docs-pin/Tools/PerfLock.py --label docs-figures --wait 30 --limit 10 -- C:/msys64/mingw64/bin/python.exe -I tools/figures.py take --engine G:/GameEngineAI/.worktrees/docs-pin --build G:/GameEngineAI/.worktrees/docs-pin/build/windows/bin/Release --work G:/GameEngineAI/.worktrees/docs-work/photo/<page-key> --kinds scene,text --figures "<part>/<chapter>/*"
   ```

   Long waits: run it in the background. Retake one figure with `--figures "<part>/<chapter>/<id>"`.
5. Output: `<work>/shots/<part>.<chapter>.<id>[.<variant>].png`; also `crops/`, `results/`, `text/`, `log/`.
6. Look: Read each PNG. Detail too small: cut and enlarge with sharp (book folder):
   `node -e "require('sharp')('<png>').extract({left:x,top:y,width:w,height:h}).resize(w*3,h*3,{kernel:'nearest'}).toFile('<work>/look.png')"`.
   Variants side by side: sharp `composite`.
7. Judge (below). Fails: change the recipe, take again; three rounds per figure at most. Caption, alt and shows follow
   plan/card/common.md's Language rules (the lint reads them as the page's prose; they count toward the page's size).
8. Publish (needs node: source env.sh first), then fill text fences and check:

   ```sh
   $P -I tools/figures.py publish --from ../docs-work/photo/<page-key> --figures "<part>/<chapter>/*" --accept
   $P -I tools/figures.py fill <part>/<chapter>     # text figures only: writes the fence bodies
   $P -I tools/figures.py check --engine ../docs-pin --dumps <dumps> | grep -E "<chapter>|^figures:"
   ```

   `publish` prints `restamped` for a picture whose take equals the published one (its stamp moves to the take's
   pin) and `skipped` for a picture or crop no page places, which it does not publish.
9. `$P -I tools/pagecheck.py <part>/<chapter>` must pass after publishing (it may rewrite the page: see its diff).
10. Commit by path: the manifest, `src/assets/figures/<part>/<chapter>/`, the notes, and the page only when `fill`
   changed it. `git add <paths>; git commit -F <file> -- <paths>`; never `-A`, never `originals/`. On `index.lock`
   wait and retry. The message ends with the two lines your task gives.

## Live and runtime figures

- `live` (`--kinds live`): three takes, each a fresh copy in an editor in a window that serves automation, about a
  minute each; the recipe needs `camera: "scene"`, `play` with at least `live.atFixedStep` steps, and `size` (the Game
  view's). The original is take 1's last frame; judge it beside `<work>/live/<picture>/take-<n>/`.
- `runtime` (`--kinds runtime`): the copy is exported (`project.export`) into `<work>/export/<picture>`, then the game
  runs `--windowed --resolution --seconds --quality --screenshot`; it must exit 0. The game draws what the project
  saved: changes go in `setup` steps that end with `scene.save`; `check` refuses capture fields on it.

## Judge each picture

`complete` means only that nothing was loading (a white picture passed). Look:

- The subject is in the frame, large enough at the page's width, not cut by the edge.
- Lit so the point shows: not black, not blown to white.
- The variants differ where the caption says and nowhere else; check the detail enlarged.
- Caption, alt and shows (yours to rewrite) state what you see (colors, which side is darker, which shadow blurs). The page's paragraph
  must still be true of the picture.

## Usual faults and cures

- `camera: "scene"` rarely frames the subject. Take positions from the scene document
  (`<pin>/Samples/<S>/Assets/Scenes/*.stscene`, `Name` and `Transform.Translation`), the look-dev script
  (`<pin>/Tools/LookDev/LookDevScene.json`), the Showcase generator's constants (`<pin>/Tools/GenerateShowcaseTerrain.py`:
  `FIRE_PIT`, `LANTERN_A`, `HUT`), or a shot in `Shots.json`. Start 3 to 10 m away, fov 22 to 40. A shot framing
  the feature too small: replace `shot` by `camera` (crops go with the shot).
- The Showcase is saved at Golden (sun toward -0.70, -0.10, -0.70: +X+Z faces lit, faces across raked); lanterns and
  fire burn only with `station: "Dusk"`.
- Look-dev `Furnace` has only a uniform sky: no highlight; tone mapper None clips whites. For reflections, add a
  figure-level `setup` step `entity.create` with a `DirectionalLight` (Intensity 1.5).
- `setup` asset paths are relative to `Assets/`, untested by `check`: find a file by its handle in `*.meta`.
- Manual exposure at an unknown `Exposure` blows out; leave exposure to the scene unless the page compares it.
- Facts in the caption: read the scene (the look-dev poles differ in thickness, not height).
- Names: entities from the scene document (`check` refuses one not found exactly once); properties, ranges and options
  from `<dumps>/components.json`; quality fields `settings.json`; debug views and presets `commands.json`
  (`viewport.capture`).
- Variants alike: compare `results/*.json`; a preset or auto exposure may override the property.
- A technique's switch (dither, FXAA's subpixel blend, specular energy): set the recipe's or the variant's `renderer`
  (`<dumps>/commands.json`, `viewport.capture`'s `renderer`); the stamp records it. A `setup` step `viewport.capture` is
  a capture of its own that the take throws away.
- The launcher: `editorWindow.launcher: true` and no `project`. A program's text figure that reads a file (a command
  script): `files` stage it in the folder the program runs in; its `arguments` name it relatively, never by an absolute
  path.
- Paths: editor windows see their copy as `S:\Projects\<name>` and programs with `files` their folder as `S:\`, so
  dialogs and logs show no path of this machine; a take that names the work folder or your home folder fails, and so
  must a picture you judge: never publish one that shows a path of the machine.
- `incomplete:` names the pointer: retake, set `antiAliasing`, or give an unlit scene a light; `relax` only with a reason.
- Pairs off by 1 level in at most 0.5 % of pixels pass (stamp: `pairDifference`). Larger: `nondeterministic`: retake
  that figure alone; differs again: report it with `<work>/nondeterministic/<picture>/`.
- Timings in a text figure: name them in `text.measured`; the caption says "one run's measurements".

## When the pin cannot show it

Add `## Figures` to the page's notes: per figure, each round, what the recipe now shows and why, what the page's
words would need. Never publish a picture that cannot show its caption: propose the nearest honest one there.
Mark the recipe `blocked` with that reason (or keep its `waitsFor`). The page's owner then names its `standIn` (a
drawing, or the nearest honest picture: a figure of the same manifest) and places that in its place, or writes
`noStandIn`; `check` refuses a figure no page places otherwise, and a release fails on any placeholder.

## The lock

A page's hold takes 10 to 45 s; waits for others' perf runs took 0 to 18 minutes. Queue with `--wait 30`; work
offline meanwhile. After a stopped run, list
`Get-CimInstance Win32_Process -Filter "Name='StrataEditor.exe'"` and end only processes whose command line names
your work folder.

## Never

Edit a page's words or an engine file; run an engine program outside the lock; commit `originals/` or other pages'
files; leave an editor or runtime running.
