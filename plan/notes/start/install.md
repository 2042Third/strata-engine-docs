# Notes: start/install

## New terms

No new glossary terms. The page defines in bold: operating system (OS), graphics processing unit (GPU), driver, build tools (alias toolchain), log, submodule, CMake preset. Plain-sentence definitions (not bold): archive, terminal (linked to `basics/tools`), argument, CMake, code editor, Vulkan (linked to `gpu/vulkan-nvrhi`), the mark of downloaded files (`com.apple.quarantine`).

## Requests

- `tools/external-hosts.txt`: `visualstudio.microsoft.com`, `code.visualstudio.com`, `vulkan.lunarg.com` (written as code, not linked, in steps 6, 9 and 10).
- No figures file: the launcher and the no-GPU dialog cannot be pictured at the pin; the dialog's first sentence stands as inline code.
- Links to pages not written yet: `../gpu/vulkan-nvrhi.md`, `../core/first-change.md`, `../basics/tools.md` (exists).
- `tutorials/start/install/exercise-2.tutorial.json`: run 2026-11-18 at the pin, passes (see "Tutorial run").

## Not verified

- The behaviour of File Explorer, Finder, Ubuntu's Files, the Visual Studio and Visual Studio Code menus and installers (labels "Properties", "Unblock", "Go to Folder...", "Continue without code", "Open Folder...") comes from general knowledge, not the pin.
- Ubuntu's `Ctrl+Alt+T`, `Expand-Archive` and `tar -xzf` unpacking, and the `.deb` install line of Visual Studio Code are general knowledge.
- That a double-click starts the editor on Windows only: macOS and Linux use `./StrataEditor` as the README says; what a double-click does there was not settled.
- The label **Apply** of the External Editor page is taken from `Docs/Manual/Scripting.md`, not from the editor's code.
- Releases page assets (names of the files) follow `CMake/StrataPackaging.cmake`; no release was fetched.

## Findings not applied

- critic-start-8: applied in short (step 10, last paragraph: **Scripts ▸ External Editor...**, a click, **Apply**, once a project is open); the step before `Spinner.cpp` on `start/first-game` belongs to that page.
- critic-start-10: applied (the log folder in OS tabs, opened in the code editor).
- critic-start-11: applied (the table row `ThirdPartyNotices.md`, and the sentence that the folder holds no license file for Strata itself; checked: the pin's root has no license file).
- critic-start-15: applied (Windows by a double-click, macOS and Linux by `./StrataEditor`).
- Erratum new:12: applied (five samples, ten guides; the README row says its lists are shorter).

## Clerk

- `external-hosts.txt`: `visualstudio.microsoft.com`, `code.visualstudio.com`, `vulkan.lunarg.com` (front pages fetched: Visual Studio, Visual Studio Code, LunarG's LunarXchange).
- Left for the planner: the tutorial's `log.read` assumption (settled by the tutorial run below).

## Tutorial run

- 2026-11-18, pin Release build: exercise 2 passes as written; the stamp and reader copy are unchanged. `log.read`
  oldest first answers `Strata Editor 0.7.0 (Windows)` as message 1 (logger `App`), and `editor.status` answers
  `engineVersion` `0.7.0`, as the answer says.
- Not checked by the file: the `Graphics device: ...` line and the About dialog's GPU rows. The runner starts the editor
  with `--no-gpu` (headless, `editor.gpu` null, `graphicsDevice` false), so no such line is logged in a run.
