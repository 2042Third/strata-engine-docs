# Notes: engineering/building

## New terms

- Preset: a named set of build settings that CMake reads from `CMakePresets.json`; home engineering/building. Glossary id preset.
- Generator (CMake): the part of CMake that writes the build files of one build tool. Id generator-cmake.
- Multi-config generator: one that writes build files holding every configuration. Id multi-config-generator.
- Cache variable (alias `CMakeCache.txt`): defined in prose in one paragraph without bold ("the cache variable: a named setting ... stored in `CMakeCache.txt`"); the planner should check the bold definition for id cache-variable.
- Validation layer: bolded once on this page (a layer that checks Vulkan calls); the glossary may home it in gpu/debugging or gpu/vulkan-nvrhi.

## Requests

- No figures file. Two pictures asked by the brief are not drawn: a text capture of a configure log (the card bars CMake output as a capture; the log lines stand in prose) and Visual Studio's Solution Explorer folders (described in prose). A Mermaid tree of the build folder stands in.
- Further reading hosts: CMake documentation (cmake.org) and Khronos (khronos.org, vulkan.lunarg.com) entries cite without links.
- Tutorial patch: tutorials/engineering/building/exercise-3.patch (adds the preset `linux-cached`; applies to the pin).

## Since

0.3.0: the presets, configurations and options existed at the first release (inventory build-test, Root project and Build configurations rows: first release 0.3.0).

## Not verified

- The log line `Graphics device: ..., validation enabled` is verified in VulkanGraphicsDevice.cpp, but `StrataEditor --headless --frames 3` printing it to a terminal was not run.
- The macOS `sed` command that copies the layer manifest was not run; the engine's skill uses Python for the same edit.
- Per-configuration subfolders under `lib/` and `tools/` follow CMake's documented rule for multi-config generators; no build was inspected.
- The file name and place of `compile_commands.json` under Ninja Multi-Config was not checked.
- The Linux layer setup (SDK or distribution package) is not described in the engine's guide beyond "install the Vulkan SDK".
- `cmake --list-presets` hiding presets whose condition is false is CMake behavior, not checked here.

## Findings not applied

- build-test:759 (the Developer Guide's option list omits `STRATA_WITH_GLFW`): applied; the page names it with the optional modules.
- Brief item build-test:458 (text capture of a configure log) and build-test:461 (Solution Explorer figure): not drawn, see Requests.
- The brief's second exercise (read the log with the CLI off): done as exercise 2; the "add a source file" hands-on is a step, not an exercise.

## Clerk

- Preset, Generator (CMake) and Multi-config generator are in the glossary already, homed here.
- Refused validation layer: the glossary homes it on gpu/vulkan-nvrhi (only its home words it). Cache variable is homed here; its bold definition is the page's (the planner's if the lint asks for it).
- Hosts: cmake.org and vulkan.lunarg.com are on the list; www.khronos.org entered it (its front page is the Khronos Group's).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
