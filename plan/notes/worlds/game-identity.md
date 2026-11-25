# Notes: worlds/game-identity

## New terms

None. The four terms the brief homes (game manifest, game identity, PE resources, desktop entry) are defined in bold on the page.

## Since

since 0.6.0: Docs/Releases/0.6.0.md (lines 105, 365, 369) lists the Dock icon, the Linux desktop entry and the game's identity as new in that release.

## Requests

- Figure `game-page` (editor, Showcase): needs the window layout `layouts/project-settings-game.ini` with the Project Settings window open on its Game page (the panel name in the recipe may need the planner's correction).
- The picture of the executable's Properties "Details" tab and of the exported folder in the system's file browser (brief items worlds-runtime:401) is an operating-system window, not an editor or runtime capture: no figure is requested; the page tells the reader to open the tab.
- Further reading names two sources without a link (the freedesktop.org Desktop Entry Specification; Microsoft's portable executable documentation): hosts may be requested for the build.

## Not verified

- The Windows user data folder's exact path (the code uses the local application data folder; the page names only macOS's path) and the Linux fallback when no data home variable is set.
- What `Editor.Export.GameIcon` and `Editor.Export.DesktopEntry` check beyond their suite names and the test case titles read (the page says only that they test the conversion and parse the text back).
- The `StrataRuntime.*` CTests read icon and version back "through Windows" only on Windows: not stated on the page beyond starting an exported game.
- Which message a person sees on a refused manifest beyond the code's text (the start-up dialog text is quoted from `ReportFatalError` use at `RuntimeApplication.cpp:463`).

## Findings not applied

- `new:22` (a script cannot read the game's title or version): the page has no not-done line; the page was already at the top of its size and the card's strip has no place for it. Evidence in the brief held at the pin (not rerun).
- Brief item worlds-runtime:401 picture of the Details tab: see Requests.
- The brief's wish to teach settings sections, quality settings and the Game page as a window: left to their pages, as its "Leaves out" says.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- game-page (editor, 2026-11-18): round 1 good, taken with the provisional build (`--provisional`); nothing published,
  `waitsFor` kept. The recipe's `layouts/project-settings-game.ini` did not exist and is not needed: the recipe now uses
  `layouts/first-game.ini` with `panel: ProjectSettings` (the panel at its own pixels, about 800 × 500, as
  make/export's game-page), and the panel opens on its first page, Game. The `setup` step moved into the window's steps
  (`project.setGameInfo` with the page's Moon Crab values and the Showcase's `Icon.png`, `expect` on the title), then
  `editor.showPanel ProjectSettings`. The picture shows Start Scene Outpost, Loading Scene Loading, Title Moon Crab,
  Version 1.2.0, Company and Copyright Tidepool Games, the Icon field with its preview, and the page's foot line that
  the project's name keeps naming the save and log folders (the caption's second sentence). Alt and shows now name
  those values; the alt names no company, since "Tidepool" is on no word list.
- game-page (editor, 2026-11-24): taken at the pin v0.8.0 (319075e3) without `--provisional`, round 1 good; `waitsFor`
  removed as `check` asked; published. The panel reads at 1:1 and shows every value the alt and shows name, the icon's
  preview, and the foot line on the project's name keeping the save and log folders.
