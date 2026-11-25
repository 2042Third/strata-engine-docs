# Notes: editor-ui/imgui-backends

## New terms

None proposed. The page bolds only the three glossary terms of its brief (clip rectangle, dynamic textures, ImGuiTextureDisplay). Draw data, draw list, draw command, the three buffer-set states and push constants are used plainly; the brief lists "draw list / draw command / draw data" (editor-ui:713) as homed here, but the glossary list of the brief does not, so the page explains them in one paragraph without bold. If the glossary homes them here, bold them in the paragraph "After `ImGui::Render`".

## Requests

- No figure file: all three diagrams are Mermaid (map, draw data layout, buffer set states). The pixel-to-NDC figure is a worked table in the text.
- Extra words that the lint accepted nothing for: none left (the page was rewritten to the common list).

## Since

0.3.0: the brief's source (R0.3 line 160 of the inventory) names keyboard layouts, cursor shapes and the clipboard in 0.3; not checked against the 0.3.0 tag.

## Not verified

- That Windows ImGui places the candidate list by the text cursor at runtime (read only from the header comment of `ImGuiPlatform.h` and `Init` setting `PlatformHandleRaw`).
- That GLFW 3.4 has no preedit callback (the brief's grep on the vendored header found nothing; the page states it as the reason).
- That optimized linkers fold the four display callbacks (the comment in `ImGuiRenderer.cpp` says the linker may merge identical functions; the Debug versus Release behavior in check question 5 is the general rule, not observed).
- The roadmap's 0.05 to 0.06 ms figure is quoted from `Docs/Roadmap.md`, not measured again.
- `EditorLayer::OnImGuiRender` is the editor's widget entry, as exercise 3 names it (found in `StrataEditor/src/EditorLayer.cpp`).

## Findings not applied

None: the brief lists no open findings. Differences between inventory and code that the page follows by the code: the fragment shader's `st_Main` is lines 26 to 46 (the brief said 26 to 46 for the whole display code, the inventory 26-46 as well); the Render function runs from line 407 to 518 and the push constants are written in lines 457 to 462.

## Clerk

- Nothing to admit.
- draw list is homed on draw/batching; the page's plain uses stay plain.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
