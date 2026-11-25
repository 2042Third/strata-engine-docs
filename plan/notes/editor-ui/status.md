# editor-ui/status

## New terms

None proposed. The page defines toast (alias notification), idle throttling and notification group, which the glossary homes here.

## Since

0.3.0: the inventory cites the 0.3 release notes for the status pills (line 103) and for the idle rates of 30 and 10 frames per second (line 172). The Editor.FrameRate preferences arrived later (wave 8); the page describes them as the policy's defaults.

## Requests

- Layout `layouts/status.ini`: the editor window with the Scene view, the Console and the status bar, 1,600 by 900 pixels; the compact variant of figure status-bar needs a window of about 1,000 points at 150 percent (waitsFor tier 1: window size).
- Figures status-bar, automation-pill and toasts wait for tier 2: editor screenshot; the named-agent variant of automation-pill needs tier 1: command details (an open tooltip).
- Not drawn: the text capture of the assets section of editor.status (assets:514), because the command's output shape was not verified at the pin.

## Not verified

- The exact pixel widths of the examples are invented for teaching (font 24 pixels at 150 percent, full text 1,540 pixels); the logic is the code's.
- The "Who uses it" column of the alternatives table names kinds of programs, not products.
- The pills' look (colors in a picture) was not checked by running the editor.

## Findings not applied

- The brief lists no open findings.
- The text figure of assets:514 (see Requests).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

2026-11-24, at the pin v0.8.0 (319075e3): automation-pill taken and published, its waitsFor removed. The figure tool now serves automation (`automation: true` on the no-agent variant, `automation: {client: "claude-code"}` on the named-agent variant, which runs StrataCLI mcp named so). Round 1 (crop bar, the whole bottom edge): no-agent grey "port 52090 · no agent", named-agent blue "Agent connected · claude-code"; the full-width crop shrank in the column. Round 2 cut the pill alone (rect 0.505 to 0.705): the shorter no-agent pill let the Scripts pill into it. Round 3 has two crops, "pill" (rect 0.509, 0.963 to 0.705, 1, scale 4: 188 by 20 pixels, the named pill) and "pill-short" (to 0.658, scale 5: 143 by 20, the no-agent pill); the page places named-agent crop=pill and no-agent crop=pill-short, the other two crops are published but not placed. The page places both crops, each after the sentence that names its text; caption, alt and shows no longer claim the tooltip, which only the pointer opens (the figure tool cannot), and the page says that no picture shows it. Still a request for a later edition: the tooltip open (each client, time since it connected, pending and answered requests), and the pill with several clients ("2 agents connected").

2026-11-23, at the pin v0.8.0 (319075e3): status-bar (full and compact) and toasts taken in one round without --provisional, their met waitsFor lines removed, and published. Full: Editing, 0.8 ms · 120 FPS · 0 jobs, the assets pill yellow at textures 56/56 MB, Automation off, Scripts crashed and 3 errors in red, the crash toast over the Scene view. Compact: the same pills in their compact texts, the assets pill (365 ready · 0 streaming) yellow. Toasts: as round 1 below (red build-failed card, two yellow command-script cards with their links). Captions and alts unchanged: each states what shows. automation-pill stays untaken: its waitsFor is now "tier 3" with the reason below (the figure tool runs the editor with --no-automation, so the pill reads Automation off, and no command connects a named client or opens the tooltip). Nearest honest picture: the published status-bar figure shows the pill's off state; the three texts and the tooltip's rows would need a diagram.

Earlier, taken with the provisional build (engine 5b975ad2831e) on 2026-11-18; nothing is published until the pin moves. Every recipe keeps its waitsFor.

- status-bar (full and compact): layouts status.ini (960 by 540, a copy of dialogs.ini) and status-640.ini (640 by 360, the smallest window). Round 1 (a failed build of the Showcase's scripts, texture budget 128 MB) showed no errors pill: the Console does not count the errors of a failed build, which the scripts pill already announces (ConsolePanel.cpp), and the textures stood at 49 of 128 MB, grey. Round 2 builds CoinCrash.cpp of make/first-script into the Showcase, plays until the Coin script crashes, and sets the texture budget to 56 MB with asset.setBudget: the full picture shows the assets pill yellow at 56 of 56 MB, Scripts crashed and 3 errors in red, and every full text fits at 960 pixels; the compact picture showed the compact texts, its assets pill grey: its 640 by 360 view kept only 45 of the 56 MB resident (77 percent, below the 85 percent that turns the pill yellow, StreamingPanel.h). Round 3 gives the compact variant a budget of 44 MB: its assets pill is yellow (Warning, not red), the rest as before; its alt now says so. The page shows only variant=full; the compact variant has its own caption and alt for a ::compare the writer may add. The crash's toast stands over the Scene view in both.
- automation-pill (no-agent, named-agent): cannot be taken, not taken. The figure tool starts the editor with --no-automation, so the pill always reads Automation off (seen in the status-bar picture), and no command connects a named client or opens a tooltip. What the page gets instead: the status-bar picture shows the pill in its off state; the pill's three texts (port and no agent, Agent connected with the client's name, the count of agents) and the tooltip's rows would need a diagram, or a take with automation on and a client that names itself, which the figure tool does not offer.
- toasts: basic3d with CoinNoSemicolon.cpp, layout status-toasts.ini (960 by 600, the Scene view 60 px taller). Round 1 passed: a failed script build (red bar, Show Problems and Show in Console), then entity.create and scene.new with force (yellow bar, A command script discarded unsaved changes, Show in Activity and Recover...), then asset.delete of Materials/Ground.stmat with force (yellow bar, A command script deleted an asset, Show in Activity). No title carries a count (each toast is one notification), and no Show Asset link appears; the caption names only what shows.

2026-11-23, mend after a viewer's report (pin v0.8.0, 319075e3). status-bar: the recipe gains the crop "bar" (rect 0, 0.944 to 1, 1, scale 2: the bottom 30 rows of the 960 by 540 full picture, the bottom 20 of the compact one, whole pills in both); retaken under the lock, published as status-bar-full-bar.webp and status-bar-compact-bar.webp with both pictures (the full picture's Scene view now looks at the sand; the bar, the toast and every claim are unchanged, 0.9 ms instead of 0.8). The page still shows only `::figure{id=status-bar variant=full}`: to show the bar enlarged the writer adds `::figure{id=status-bar variant=full crop=bar}` after it. A full-width crop of the 960-pixel picture is not enlarged in the 768-pixel column; the compact crop (640 wide) shows at its own pixels. Caption now begins "Along the bottom edge" and says the card over the Scene view is the crash's toast. toasts: caption now says where the bars are (a thin bar at each card's left edge, red on the top card, yellow on the two below); picture unchanged.
