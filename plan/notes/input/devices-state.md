# Notes: `input/devices-state`

## New terms

None: the four terms of the brief (input frame, suspended input frames, surrogate, pointer capture with keyboard capture) are defined in bold on the page.

## Requests

- Hosts: the Further reading names www.glfw.org, gameprogrammingpatterns.com and learn.microsoft.com, all on the list. The pages were not opened and no URL is written.
- No figures file: the only picture is a Mermaid diagram.

## Since

`since: 0.3.0`. Not checked against the tag `v0.3.0`; the subject (polled keyboard and mouse state) is the engine's oldest input code. The suspension, captures and typed text may be newer.

## Not verified

- Alternatives table, "Who uses it" column: that some libraries offer an event queue beside a key state array and that Windows has a raw input API for high-precision mice come from general knowledge. No engine or library source was read.
- The three Further reading entries were not opened.
- The claim that the Third-Person Jump action binds `Key/Space` is read from `Samples/ThirdPerson/ThirdPerson.stproj`; the script that reads the action was not traced.
- `Window::ProcessEvents` runs `glfwPollEvents` (GLFWWindow.cpp line 412); who else calls `Input::Reset` (the application calls it at start) was not traced beyond `Application.cpp` line 105.
- The "pause of about three loop turns" in the worked example is an invented example, as the page says.
- `InputActions::Update` and the SDK's action functions were not read; the page only names them.

## Findings not applied

- The brief lists no open findings.
- The brief asks for a table of who sees what with the input actions as a row; the page's table omits the actions row because `InputActions` was not read at the pin for this page (its page is `input/actions`).
- The brief's "Fit" mentions three figures; the page has one Mermaid diagram, one table for the frame sequence (in the worked example) and the capture table. The suspension timeline is the worked example's table and the exercise's sketch output.
- The exercise "a doctest case ... a patch: done" is a predict exercise without a patch (`solution=` patches belong to tutorials after `core/first-change`); the second exercise is the done one, a sketch.
- `:::elsewhere` is not used: no claim about another engine is cited.

## Clerk

- Nothing to admit: the hosts named are on the list.
