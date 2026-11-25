# Notes: `editor/script-builds`

## New terms

- **stamp**: the note a script build tree keeps (`StrataScriptBuild.json`) of the toolchain and settings it was configured with and, after a successful configure step, the sorted list of the script folder's files. Home: `editor/script-builds`. Aliases: build stamp.
- **diagnostic**: one error or warning found in a build log, split into file, line, column, severity, code and message. Home: `editor/script-builds`. Aliases: diagnostics, build diagnostic.

The word "summaries" (messages that only say a step failed) is explained in plain text, not defined in bold.

## Requests

- No new hosts: Further reading names cmake.org, learn.microsoft.com, docs.godotengine.org and docs.unity3d.com by name only; the Unreal Live Coding documentation is cited without a link (host not on the list).
- No figures file: the only picture is a Mermaid flow chart.

## Since

`since: 0.3.0`. `ScriptBuild.cpp` came with `12cbd039` ("Build game scripts with the engine's toolchain", 2026-10-09), `ScriptToolchain.cpp` with `ff9f0589` and `ScriptSources.cpp` with `db3707c6`, all contained in `v0.3.0`.

## Not verified

- The worked example's command results (a failed build after a field name is changed, then a fixed one) are derived from the code and from the `Editor.ScriptWorkflow` test names; nobody ran them. The `project.create` call uses the schema of the pin; the path `C:/Games/Coin` is only an example.
- The claim that a new `basic3d` project already has its script `CMakeLists.txt` comes from the `script.init` command description.
- The alternatives table cites other engines from general knowledge (GDScript read at run time, Unity compiling scripts in the editor, Unreal Live Coding patching the running program); no source was fetched.
- The lengths 104 and 78 of the tracking logs are counted from the constants in `ScriptBuild.cpp`, not measured against MSBuild.
- The 1 MiB class-scan limit and the 4,096 / 65,536 listing limits were read from `ScriptSources.h`.
- Menu labels: the page names none; the editor's Scripts menu was not checked.

## Findings not applied

- The brief had no open findings at its end.
- The brief's second half (script files, `script.init`, `script.create`, the external editor) is covered in one short section; the brief's Fit note proposes a separate page `editor/script-sources` for it, which would hold the rest (the template contents, field type names, `script.setExternalEditor`, choices found on the machine).
- The brief's figure of the status bar's build pills (`scripting:434`) is not drawn: the pills belong to `editor-ui/instrument-panels`, which the brief leaves out.
- The brief's item `scripting:426` (a figure of the loop of edit, build, load, Play and Problems) is covered by the Mermaid flow chart of the map.

## Clerk

- Admitted the terms stamp (alias build stamp) and diagnostic (aliases diagnostics, build diagnostic), homed here.
- Hosts: none admitted; the sources are cited without links, so no host is needed (docs.unrealengine.com is not on the list and is the planner's).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
