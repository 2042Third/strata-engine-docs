# Notes: editor-ui/launcher-dialogs

## New terms

None proposed. The page defines the glossary term launcher.

## Since

0.3.0: `WelcomePanel.cpp`, `ProjectDialogs.cpp` and `ExportDialog.cpp` first appear in the tag v0.3.0.

## Requests

- Figures `launcher-recent` and `about-strata` (editor, project Tetris, layout `layouts/first-game.ini`); both wait for `tier 2: editor screenshot`. The launcher figure needs a `project.close` step first (brief item new:42); the agent card sits below the scrolling region's edge at 1600x900 and the code sets no scroll position.
- Not drawn: the agent card in its four states (automation:574), the New Project and Open Sample pictures (shared with `start/first-game`), and the Export dialog set (shared with `assets/packs-export`).
- Words proposed for extra-words: none needed after rewording.

## Not verified

- The "Who uses it" column of the Alternatives table (Unity Hub, Godot project manager, Unreal project browser) comes from general knowledge, not from a source.
- The Further reading entries are cited without links.
- The tooltip text "Show the running export" is read from `EditorLayer.cpp`; the button's label while exporting is not.

## Findings not applied

- The brief says `EditorLayer` draws all dialogs; at the pin the Delete dialog is owned and drawn by `ContentBrowserPanel`, and the page says so.
- The brief says no file is read in a frame; at the pin the project dialogs test folder existence on the main thread when a name or location changes and when they open, and the page says so.
- Open findings of the brief: none beyond item new:42, which is applied as the figure's `project.close` step.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken with the provisional build (engine 5b975ad2831e, `--provisional`); nothing published; both keep `waitsFor`.

- `launcher-recent`, round 1 of 1: the step `project.close` does bring the launcher up (the card's "take always opens a project" does not hold here), at 960 x 540 with `layouts/dialogs.ini`. The picture shows the left column, the Tetris copy as the one recent card with its picture, folder and "Opened just now", the template cards, the top of the sample cards and the footer with version, commit, graphics card, graphics interface, start time and the About Strata link. The agent card cannot be shown: it sits below the scrolling list's edge at this size (and at 1600 x 900, as ## Requests says), and no command scrolls the launcher. Caption, alt and shows now name only what shows. The recent card's folder line shows the take's work folder (no user name); the final take shows its own. If the page wants the agent card, it needs a diagram or a command that scrolls the launcher.
- `launcher-recent`, round 2 (a viewer's fault: the Tetris card prints the take's work folder,
  `G:\GameEngineAI\.worktrees\docs-work\photo\editor-ui-launcher-dialogs\projects\01`): the fault stands, but no recipe
  can cure it, so the recipe is unchanged and nothing was retaken. `take` copies every figure's project into
  `<work>/projects/NN` (`tools/figures.py`, the line `directory = os.path.join(work, 'projects', '%02d' ...)`), the window's
  editor opens that copy with `--project`, and the launcher prints the full folder (no home abbreviation). The schema's
  `project` takes only a sample, template, lab or lookdev, and no step can name the work folder. The one way out from a
  recipe, a step `project.openSample` into an absolute folder such as `G:/StrataProjects/Tetris` followed by
  `editor.removeRecentProject` for the copy, would write outside the take's folders, name the take machine's drive in the
  book, and fail on every later take (the directory must be new or empty, and no take empties it). Proposed for the
  planner: `figures.py take` puts an editor figure's project copy in a folder named after the project under a short,
  neutral root (for example `<drive>:/StrataProjects/<Name>`, emptied by the take), so the final take's card reads like a
  reader's.
- `about-strata`, round 1 of 1: `editor.showDialog {dialog: "about"}` at 960 x 540 with `layouts/dialogs.ini`, project template basic3d (the dialog needs no sample). The table of eight rows, Copy Details and the top of the notices box are readable; the box runs past the window's foot, so the Close button of the old alt is not in the picture and the alt no longer names it.

Taken at the pin v0.8.0 (319075e3, Release build, without `--provisional`); `check` asked to drop both `waitsFor`
lines; both published, recipes, captions and alts unchanged.

- `launcher-recent`, round 1 at the pin: the left column with its three buttons and "Continue without a project", the
  Tetris copy as the one recent card with its picture, folder and "Opened just now", the Basic 3D and Empty cards, the
  top of the sample cards, and the footer (Strata 0.8.0, commit, graphics card, Vulkan 1.3.0, "started in 0.87 s",
  About Strata). The card's folder line still prints the take's work folder (no user name); the planner's proposal of
  round 2 above stands.
- `about-strata`, round 1 at the pin: the dialog over the dimmed editor with the mark and name, the eight rows (0.8.0,
  319075e3f92b, Windows, the graphics card, driver, Vulkan 1.3.0, startup, 100 %), Copy Details and the top of the
  notices box with its table of libraries; all readable at 960 x 540.

A viewer's faults on `launcher-recent`, mended at the pin (319075e3, Release):

- Folder line (fault stood, mended): the steps now run `project.info` (binding the copy's file), `project.openSample`
  Tetris into `<work>/StrataProjects/Tetris` (inside the take's folder, so each take empties it), `editor.removeRecentProject`
  for the copy, then `project.close`. The one recent card reads `...\editor-ui-launcher-dialogs\StrataProjects\Tetris`;
  the take's folder still prefixes it (`take` alone chooses the work folder), so round 2's proposal for the planner stands.
- Sample cards cut by the footer (fault stood, mended): 960 x 640 with `layouts/make-performance-result.ini` shows the
  High Desert Outpost and Third-Person Adventure cards whole above the footer, at 80 % in the column.
- Third-Person Adventure title over its description (fault stands; the pin cannot do better): the suggested 1280 x 720
  was taken and still wraps the title onto the description. `UI::Card` (`StrataEditor/src/UI/Widgets.cpp`) moves the
  description down by one title line whatever the title wraps to, while `GetCardHeight` counts the wrapped lines. The
  title needs about 215 px beside a 112 px picture; the grid's widest card (three columns just before a fourth fits, about
  314 px) leaves about 178, and only a two-column window about 1,000 to 1,060 px wide would fit it, for which no layout
  exists. Engine fix: advance by the wrapped title's height in `Card`.
- `publish` fails when a retake changes a picture's size (`encode-figures.mjs diff` refuses two sizes); the old
  `launcher-recent.webp` was removed before publishing so the new size could go in.
