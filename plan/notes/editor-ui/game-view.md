# Notes: editor-ui/game-view

## New terms

None proposed; the page defines letterboxing and shortcut routing, the two glossary terms of the brief, in bold.

## Since

since 0.3.0: Game view, play mode and shortcuts exist from the first tags; no per-feature evidence gathered beyond the brief.

## Requests

- Figures `letterboxed-16x9`, `fixed-1920x1080`, `no-camera` and `locked-cursor-hint` (kind editor): all need the layout `layouts/game-view-tall.ini` (Scene view and a tall Game view). `no-camera` needs a scene without a primary camera (no sample has one: tier 3); `locked-cursor-hint` needs a game that locks the cursor and a focused Game view within the hint's five seconds (tier 3).
- Further reading cites the Dear ImGui project's `imgui.h` without a link: ask for the host github.com if a link is wanted.
- Pages linked that may not exist yet: `editor-ui/widget-kit`, `editor-ui/ui-scale`, `editor-ui/scene-view`, `reference/editor`, `basics/programming-1` to `-3`.

## Not verified

- That the game's UI scale in play is the display's, without the person's factor (brief `new:28`); the page states it in one sentence.
- That the "No camera to show" text equals what an exported game's `GameRenderer` shows (the code comment says so; `GameRenderer` was not read).
- That the Inspector, Console and Content Browser do not call `HandleSelectionShortcuts`: only two callers (Hierarchy, Scene view) were found by search.
- That ImGui blocks nothing else for bare keys during text input beyond the panels' own `WantTextInput` tests.

## Findings not applied

- The brief's "Delete in the Content Browser deleting entities": at the pin the Content Browser's Delete opens a delete dialog for the selected asset or folder; the page says so and that it never deletes entities.
- The brief's `Ctrl+P always` leaves: the code returns first for a modal, so the page says Ctrl+P works whenever no modal is open.
- Pictures of "HUD" and the macOS shortcut test appear only as prose; the `EditorContext.h` comment "viewport focused" is stale (the Game view's focus decides) and was not copied.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken with the provisional build (the pin lacks `editor.screenshot`); nothing is published, and every recipe keeps `waitsFor: tier 2: editor screenshot` until the pin moves.

- Layout `layouts/game-view-tall.ini` (1280 x 720) made from `scene-view.ini`: Hierarchy 300 px, Inspector 460 px, bottom tabs 100 px, so the Game panel is 516 x 540 and taller than 16:9. Every recipe pictures the `Game` panel at its own pixels.
- `letterboxed-16x9`, `fixed-1920x1080` (Showcase): round 1 showed a black image under a "Scripts built" toast; the paused game sat before the sample's fade-in. Round 2 waited 600 frames: toast gone, still black. Round 3 adds `play.step` of 120 steps after `play.start` (the fade runs) and keeps the wait: the tour's view in a 516 x 290 image with dark bars above and below; the chip reads 16:9 or 1920 x 1080. Good.
- `no-camera`: no sample lacks a primary camera, but `scene.new` (an empty scene named Level) has none: the Game view shows "No camera to show" and names the scene 'Level'. The tier 3 `waitsFor` became tier 2. Good.
- `locked-cursor-hint` (ThirdPerson, `Scenes/Course.stscene`, which locks the cursor in `CourseState::OnCreate`): play focuses the Game view and the hint shows within its five seconds. Round 1 had the build toast over the image; round 2 builds the scripts first and waits 600 frames before play. The game's vsync notice also shows at the image's bottom; the caption does not speak of it. The tier 3 `waitsFor` became tier 2. Good.

Review of the provisional pictures, mended by words (the pictures stay as taken; no retake, as no step changed):

- `locked-cursor-hint`: a reader may take the bottom line ("The game asked for a window with vsync on; play mode keeps the editor's window.") for the hint. It cannot be left out: `EditorGameWindow::DescribeForPeople` shows it as long as the game's request stands, and ThirdPerson's settings ask for vsync at start. Caption, alt and shows now name it as play mode's notice that the game's window request is not applied (the page's "Game's request" paragraph explains why).
- `fixed-1920x1080`: same rectangle, bars and scene as `letterboxed-16x9`; only the chip differs (the game draws the same picture at any size). The caption now says so: the chip reads 1920 x 1080, the rectangle is the 16:9 one, the picture holds 1920 by 1080 pixels scaled down. `numbers` says where the numbers come from.

## Pin move to v0.8.0

- Options table of `reference/editor`: at 319075e3 it gained only `--window-size` (at least 640x360). The page takes no number from the table; its link there is to the shortcut table. The game's content scale sentence now names `--ui-scale`, which the scale the game sees follows (`ImGuiLayer::GetDisplayUIScale`: the override, else the content scale; set each frame in `EditorLayer.cpp`). The three preference sections (`EditorPreferences::RegisterSections`) and the roadmap's later rebinding of editor shortcuts still hold.
- Figures: the four `waitsFor` "tier 2: editor screenshot" entries are removed, since the pin has `editor.screenshot`; the pictures are not retaken.

## Photographed at v0.8.0

All four taken at the pin 319075e3 (Release build, no `--provisional`) in one hold, one round each, recipes unchanged, and published:

- `letterboxed-16x9`: the Showcase's dawn vista in a 516 x 290 image with dark bars above and below in the 516 x 540 panel; chip 16:9.
- `fixed-1920x1080`: the same rectangle, bars and picture; only the chip differs (1920 x 1080), as the caption says.
- `no-camera`: "No camera to show" and "The scene 'Level' has no active entity with a Camera component marked Primary." in grey, centered.
- `locked-cursor-hint`: ThirdPerson's course with the hint box "Shift+F1 frees the mouse · Ctrl+P stops the game" at the top and the vsync notice at the bottom; no toast.
