# Notes: core/engine-modules

## New terms

None proposed. The six terms the brief homes here (engine module, hook, Kahn's algorithm, service, service locator,
topological sort) are defined in bold on the page. "In-degree" is named once in plain words ("the count of arrows that
point at the node") and is not a glossary entry.

## Requests

- Host: `dev.epicgames.com` (the Unreal Engine documentation on modules and `IModuleInterface`), cited in Further
  reading without a link until the host is allowed.
- Page links to pages of the outline that may not be written yet: `../gpu/vulkan-nvrhi.md`, `../audio/engine.md`,
  `../editor-ui/imgui-backends.md`, `../world/projects-settings.md`, `../world/systems.md`, `layers-registries.md`,
  `frame-loop.md`.

## Since

`since: 0.4.0`: `Docs/Roadmap.md` at the pin lists `engine-modules` in wave 4 ("Landed on 2026-10-19 with release
0.4.0"; the wave's entry at line 1186).

## Not verified

- What Unreal Engine's `IModuleInterface` and its loading phases do, and what the textbook *Game Engine Architecture*
  and *Game Programming Patterns* say of manager objects and service locators: written from the inventory and general
  knowledge, cited in Further reading, not checked against the sources.
- That the exercise patch `tutorials/core/engine-modules/exercise-1.patch` builds and passes: it applies to the pin
  (`git apply --check`), but no build was run (`tools/tutorials.py patch` does that).
- The claim that a module "between two cycles" stays in the cycle message: read from the removal loop in
  `EngineModuleRegistry::Create`, not run.
- The 32 ms of the exercise 4 answer is two waits of 16 ms (`c_SkippedFrameWait`); the frame pacer's own waiting is
  not measured.
- The last check of the page after the third pagecheck round was `tools/lint.py` alone (two sentence-length findings
  fixed after it).

## Findings not applied

The brief lists no open findings. Left out of the page on purpose: the profiler's discard of a skipped frame
(`foundation:517` mentions it; the frame-loop page teaches the profiler), the layers' scene-service counterpart (a
link to `world/systems`), and the audio, ImGui and graphics modules' insides (other pages). "What went wrong before"
is omitted: no regression of this part was found in the pin's history, which was not searched beyond the tests.

## Clerk

- Left for the planner: `dev.epicgames.com` (the fetch of its front page returned 403, nothing to confirm).
- Links to pages not written yet are the writers' of those pages; nothing to admit.

## Track walk E-final-6

Checks in `docs-work/walkfix-E6`, 2026-11-24, with the official 0.8.0 package and the pin clone's `build/docs-patch`, under the perf lock; no editor left running, the clone clean afterwards.

- WK7: the new `tutorials/core/engine-modules.tutorial.json` starts from `core/first-change` and names
  `Core.EngineModules` for exercise 1's patch (before it, `tutorials.py patch` ran only `Architecture.Layering` and
  the feature test). `tutorials.py patch core/engine-modules` passed: with the first change and the exercise patch,
  `Core.EngineModules` ran 10 test cases, 10 passed, as the worked solution says; `Architecture.Layering` 18 and the
  feature test passed. The "Not verified" line on the patch above no longer holds.
- WK1, WK6: a paragraph after the introduction says that the page needs no project and no download and that its test
  commands, traces and exercise 2's patch need the source build; How it is tested says where to run them.
