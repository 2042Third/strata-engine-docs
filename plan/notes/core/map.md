# Notes: `core/map`

## New terms

None proposed. The page defines in bold the two glossary terms it homes (engine module registration, and layer with its
architecture sense), and also, in one sentence each, the terms whose homes are other pages: script module, registry,
service, engine service and scene service. "Architecture layer" is used as the alias of the layer entry.

## Requests

- `tools/external-hosts.txt`: `docs.godotengine.org` (Godot, "Introduction to the buildsystem") and `dev.epicgames.com`
  (Unreal Engine, "Unreal Engine Modules"). Both sources stand in Further reading without a link until then.
- `tools/data/names.txt`: nothing needed (the authors named in Further reading are not read by the word list).

## Since

`since: 0.4.0`. The per-layer static libraries (`CMake/StrataLayers.cmake`, commit `dd83f1e0`, "Build one library per
layer from the layer table") first appear in `v0.4.0-rc1` and `v0.4.0`. The layer table itself (`Layers.json`, commit
`f0ea4dfe`) is older, in `v0.3.0`, and `StrataRuntime.NoTooling` came with `dd83f1e0`.

## Not verified

- Godot: that its editor build and its export templates come from one source tree, the templates without the tools
  (table, "Used by"). Written from general knowledge.
- Unreal Engine: that editor modules stay out of a packaged game. Written from general knowledge.
- Unity: that scripts compile into assemblies the editor and the player load; the URL
  `https://docs.unity3d.com/Manual/assembly-definition-files.html` was not fetched.
- Jason Gregory, Game Engine Architecture: that its chapters on tools and the runtime layers survey how engines divide
  their code (chapter numbers not checked).
- The option counts of the Medium exercise (16 and 12, five shared) come from the two `c_Arguments` tables at the pin;
  the installed programs were not run.
- "A crashing script stops the game and not the editor": taken from the engine's own documents (the script boundary is
  plain C data); the page does not quote the crash guard's code.

## Findings not applied

The brief lists no open findings. Differences between the brief and the pin:

- `foundation:173` says the layer table has 21 layers. `StrataTests/Architecture/Layers.json` at the pin has 19 rows
  (16 for games, three marked `Tooling`); the page says 19.
- The diagram of `foundation:385` is a Mermaid diagram on the page, so there is no figure manifest.
- The brief's evidence lines for `new:17` (`Layers.json:5-24`, `EditorApplication.cpp:64-80`, `RuntimeApplication.cpp:340-354`)
  are from another commit; the page uses the facts, verified at the pin in the same files.
- The Basic exercise lists six files as the brief asks; the done exercise is a 23-line sketch (the level-1 limit of 25
  lines per fence made the real glob matcher too long), so it matches folder prefixes, not globs.

## Clerk

- `tools/external-hosts.txt`: `docs.godotengine.org` added (front page fetched: Godot's documentation).
  `dev.epicgames.com` answered 403 to the fetch, so it is left for the planner.
