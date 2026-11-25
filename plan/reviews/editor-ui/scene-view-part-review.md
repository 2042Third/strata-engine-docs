# Part review: `editor-ui/scene-view`

- wrong: "**Q**, **W**, **E** and **R**, work while the Scene view has the keyboard": `ViewportPanel::HandleShortcuts` runs them while the view is hovered or focused (`ViewportPanel.cpp:882`), as `editor-ui/game-view` says; now "while the pointer is over the Scene view or it has the keyboard focus" (sentence split for length).
