# input/how-input-works

## New terms

None proposed. The page defines the eleven glossary terms of its brief in bold.

## Since

since 0.3.0: the polled input state, the GLFW callbacks and `Input::BeginFrame` exist from the first tag (the subject is older than the first tag; not checked against the tag's tree).

## Requests

- Extra word: modifier, modifiers (the name of an Unreal Enhanced Input feature, in the comparison table and in what Strata does not do).
- Hosts: dev.epicgames.com (Enhanced Input documentation) and a Unity manual page URL; the page cites Unity and Unreal in Further reading without a link.
- No figures file: the only picture is a Mermaid diagram.

## Not verified

- The claims about Unity's Input System, Unreal's Enhanced Input and Godot's InputMap in the comparison table come from memory of their manuals, not from a fetched page.
- That GLFW names keys by position on every platform; the page relies on the pin's `KeyCodes.h` comment.
- That a German keyboard's Z key reports `Key::Y` (follows from the position rule, not tested).
- The editor calls `Input::SetEnabled` with the Game view's focus: read at `GameViewPanel.cpp:257`, the focus condition itself not traced.

## Findings not applied

The brief lists no open findings. The brief's playground-script exercise (count Pressed in `OnUpdate` and `OnFixedUpdate`) became a standalone sketch, `sketches/input-how-input-works-edges.cpp`, because the card wants code exercises as sketches.

## Clerk

- Not admitted: dev.epicgames.com (no answer to one fetch in an earlier batch) and a Unity manual page; left for the planner. modifier, modifiers entered extra-words.txt (asked by input/actions).
