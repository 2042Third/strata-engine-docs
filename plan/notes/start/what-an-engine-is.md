# Notes: start/what-an-engine-is

## New terms

- **millisecond** (ms): a second divided into 1,000 equal parts. Home: `start/what-an-engine-is`. Aliases: milliseconds,
  ms. The lint has it on no word list (`word-list` is clean now only because the page writes "ms" after the definition).
- **hitch**: one frame that takes far longer than the frames around it, so that the motion visibly jumps. Home:
  `start/what-an-engine-is`. Aliases: hitches. Add it if the glossary lacks it (the reading report lists it as no new
  term of this page, so it may be homed elsewhere already).

## Requests

- `tools/data/names.txt`: Bevy, GDScript (the survey table) and the authors of Further reading: Robert, Nystrom, Glenn,
  Fiedler, Jason, Gregory. These are the page's 8 remaining `word-list` failures.
- Glossary homes: the brief homes "frame" (`foundation:569`, `gamedev:614`), "frame rate" and "delta time"
  (`gamedev:614`) on this page, and the page defines each in bold at its first use; the reading report lists none of
  them as a new term of this page, so the glossary homes them elsewhere (markterms linked "frames per second" to
  `core/frame-loop`). The planner settles which page is their home.
- `tools/external-hosts.txt`: gameprogrammingpatterns.com (Nystrom's "Game Loop" chapter) and unrealengine.com (the
  Unreal Engine EULA) would let Further reading link those two sources; they are cited without links now.
- Figure `cube-fall` (`src/content/figures/start/what-an-engine-is.json`): a tier 3 strip of six captures of one play
  after 0, 10, 20, 30, 40 and 50 fixed steps, side by side, each labelled with its frame number and time. It keeps its
  `waitsFor` as the request for a later edition; its stand-in `cube-frames` is placed now (see `## Figures`).
- The two-lane diagram is a Mermaid `gantt` chart (`dateFormat X`); the site build should confirm it renders.

## Not verified

- The scene of `start/first-game` (not written yet): the page says a cube fell onto "the ramp" and slid down it, and
  that another cube carries `Spinner`; the ramp, which cube carries the script and its `DegreesPerSecond` value come
  from the brief, not from that page.
- The worked solution `tutorials/start/what-an-engine-is/exercise-2.tutorial.json` passes `tutorials.py check`; it was
  not run against an editor.
- "10 while its window is behind another one": the code's condition is the window not having the focus
  (`UnfocusedIdleFrameRate`, `EditorLayer::UpdateFrameRate`); "behind another one" is the reader's usual case of it.
- The survey's rows for Unreal Engine, Unity, Godot, Bevy and in-house engines (languages, editors, platforms, licence
  terms, Electronic Arts building its own engines) are general knowledge, not checked against the cited sources in this
  session.

Checked at the pin: the application's frame (`Docs/Architecture.md` lines 788-831, `Application::Run`), the scene
systems' order (UI, Scripting, Animation, World in `OnUpdate`; Physics in `OnFixedUpdate`; Audio in `OnLateUpdate`),
the fixed step 1/60 s (`Scene.h`), `MaxTimestep` 0.25 s, `MaxFramesInFlight = 2` (`GraphicsDevice.h:28`), the frame
pill's text, tooltip and work time (`EditorLayer::DrawFramePill`, `EditorLayer.cpp:930-945`), the idle rates 30 and
10 after 0.5 s and never idle while playing (`EditorFrameRate.h`, `EditorLayer::IsBusy`), `VSync = true`
(`Window.h`), the `Spinner` template (`ScriptProject.cpp:241-257`), export copying `StrataRuntime` under the game's
file name (`GameExport.cpp:193-201`, `:690-706`), a script crash stopping play mode but not the editor
(`EditorContext.cpp:1342-1354`), the menu items (**File ▸ Open Sample**, **Export Game...**, **Project Settings...**,
**Preferences...**), the Play tooltip and **Ctrl+P**, no licence file at the root (`git ls-tree`), and
`ThirdPartyNotices.md` (`Docs/Releases/PackageReadme.md:23`).

## Findings not applied

- critic-start-2: it asks `start/first-game` to save the scene and show how a project is opened again; the change
  belongs to that page, not this one. This page's exercise opens the `Tetris` copy through **File ▸ Open Sample ▸
  Tetris** when the reader has none, so it does not depend on the fix.
- critic-start-11 is applied (the Strata row's licence cell). critic-start-17 is applied (one sentence in exercise 2).

## Clerk

- Admitted: "hitch", homed here.
- Refused: "millisecond": a unit, on `tools/data/extra-words.txt` already (R54).
- `tools/data/names.txt`: Bevy, GDScript, Robert Nystrom, Glenn Fiedler, Jason Gregory added.
- `tools/external-hosts.txt`: `gameprogrammingpatterns.com` added; `unrealengine.com` answered 403 to the fetch, so it
  is left for the planner, as are the homes of frame, frame rate and delta time.

## Tutorial run

- 2026-11-18, exercise 2 passes at the pin (Release build): during play the editor drew 59 frames a second with a
  median frame work of 0.04 ms, so the file now also expects the work's median under 16.7 ms, the answer's "a small
  part of the frame".
- The answer's steps 3 and 4 (**idle** after Stop, 30 or 10 frames a second) are not checked by the file: the pin never
  throttles a headless run (`EditorLayer::IsThrottlingEnabled`), and every automation request keeps the editor busy for
  a second (`c_AutomationActivitySeconds`). That is the engine as designed, not a fault.

## Figures

- `cube-fall` (2026-11-24, at v0.8.0 `319075e3`): the strip in one picture cannot be made: a capture returns one picture
  of one frame. Its stand-in is `cube-frames`, six real captures of one recipe (variants `frame-0` to `frame-50`): the
  scene before play, then after 10, 20, 30, 40 and 50 fixed steps (`play.step`, paused). The page places them one under
  the other, each with its frame and time as the figure's own line.
- Round 1: `material.create` refused the second variant, since the variants share one copy of the project and the
  materials were already there: each variant now makes its own (`Ramp<n>`, `Cube<n>`). Round 2: the camera's target
  went up from 1.9 to 2.1 m, since the cube's top nearly touched the picture's edge.
- The old recipe would not have shown a slide: a cube dropped from 4 m onto a 20 degree ramp lands only after about 43
  steps, and with the default friction of 0.5 (`RigidBody`) a 20 degree slope holds it (tan 20 degrees is 0.36). The
  recipe now tilts the ramp 30 degrees, its right end on the ground, tilts the cube the same way so that it lands flat,
  drops it 1.5 m above its place on the ramp and gives it `Friction` 0.02. Judged by eye: frames 0 and 10 high, 20
  lower, 30 just above the ramp, 40 on it, 50 further down it. `cube-fall` now carries the same setup, so a later strip
  shows the same play.
- Words: the six figure lines added words; the lead-in, the paragraph after the figures, the caption and the alt were
  cut so that the page stays within size L (6,498 prose words).
- Mend after the viewer's report: the renderer reads one caption and alt per recipe, so the six variants of
  `cube-frames` printed the same caption and alt six times. They are now six recipes, `cube-frame-0` to
  `cube-frame-50`, each with its own caption (the frame label, explained in `numbers`) and its own alt, placed as leaf
  figures; `cube-fall`'s stand-in is `cube-frame-0`. The camera aims at the cube and the upper ramp (target
  -0.13, 2.58, 0; fov 26.5; 1024 x 768), so the cube is about 1.4 times larger and frames 0 and 10 differ visibly; the
  ramp's lower end leaves the picture. The cube's shadow on the ramp (sun from the right) is named in frame 10's
  caption. Captions and alts were kept short to hold size L (6,500 prose words).
