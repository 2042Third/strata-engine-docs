# Notes: `core/windows-events`

## New terms

- **framebuffer**: the image that the graphics card draws a window into, whose size `GetFramebufferSize` gives in
  pixels. Home: `core/windows-events`. Aliases: framebuffers, framebuffer size. (The word is used 14 times on the page,
  so its word-list finding is left until the term exists.)

The page also defines the glossary's own entries homed here: event, dispatcher, Handled flag, overlay, window backend,
GLFW, content scale and DPI scale. "Category" (of an event) is explained in plain words, not as a term.

## Requests

- `tools/data/names.txt`: Retina, Wayland, Qt. Retina is Apple's name for a display of twice the usual density; Wayland
  is a window system of Linux; Qt is a library for programs with windows. The word-list findings are left until then.
- `tools/data/extra-words.txt`: clipboard (the system's store for copied text; the page uses it once, naming
  `GetClipboardText`). The word-list finding is left until then.
- Hosts for Further reading (`tools/external-hosts.txt`): `www.glfw.org`, whose input guide and window guide the last
  entry cites without a link.
- The glossary holds one entry for the pair "Content scale / DPI" and another "DPI scale"; the page defines both in bold
  in separate paragraphs, as the brief's terms table asks. The planner may merge the two entries.

## Since

`since: 0.3.0`, the earliest release the field allows. `Event.h`, `LayerStack.cpp` and `GLFWWindow.cpp` were added by
the first commit (`a0f2865f`, "Add build system, pinned dependencies and engine core"), which `v0.3.0` contains. The
window modes and the content scale event came later; the page teaches the pin's contract.

## Not verified

- The pixel densities in "Content scale" (a 24 inch monitor with 1920 by 1080 pixels against a 13 inch screen with
  2880 by 1800, "a factor of nearly three") come from general knowledge of those sizes, not from the engine.
- That Retina is Apple's name for a display of twice the usual density, and that a keyboard repeats a held key after
  a pause at its own rate, are general knowledge.
- That macOS and Wayland measure window sizes in points and Windows and X11 in pixels comes from the comment of
  `ImGuiLayer::ToUIScale` in `Strata/src/Strata/ImGui/ImGuiLayer.h`; no program was run on those systems.
- The table of alternatives (the message queues of Windows, the observer pattern and the signals of Qt, the staged
  delivery of Godot) and Further reading cite other software from general knowledge; the pages were not fetched.
- The page gives no example for `GetLayoutKey`: the comment in `Window.h` does not say clearly which key of a French
  keyboard its example means, and nothing at the pin runs it.
- `Tests::StubWindow` and the test cases of `Core.WindowBackend` were read, not run.

## Findings not applied

- `foundation:710` (the design's origin): applied by omission. The page does not say where `Layer`, `LayerStack`,
  `Event` or `ST_BIND_EVENT_FN` came from, and does not mention a lineage.
- The brief's line numbers differ at the pin (`Application::OnEvent` is lines 202 to 223, the size and close callbacks
  lines 230 to 249, the mode switch lines 482 to 508); the page quotes the pin's lines.
- `Window.h` has 136 lines at the pin, not the 213 of the inventory; the contract follows the pin's file.
- No `## What went wrong before` section: the history of the area holds no bug with a regression test that this page
  could teach (`git log` of the pin names none for events, layers or window modes).
- The Dock icon of the GLFW backend (`GLFWApplicationIcon`) is named nowhere: the page's `SetIcon` sentence follows the
  interface's comment, and the macOS detail is not taught.
- The warnings `passive` and `noun-stack` were read one by one. The passives left describe the state of data ("`Handled`
  is set", "sizes are measured in points") or a place where naming an actor would add nothing.

## Clerk

- Admitted: framebuffer.
- `names.txt`: Retina, Wayland, Qt. `extra-words.txt`: clipboard.
- `external-hosts.txt`: `www.glfw.org` (front page fetched: GLFW).
- Left for the planner: merging "Content scale" and "DPI scale".

## Track walk E-final-6

- WK1, WK6: a paragraph after the introduction says that the page needs no project and no download and that its test
  commands and traces need the source build of Your first engine change; How it is tested says where to run them.
