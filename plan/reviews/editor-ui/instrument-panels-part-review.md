# Part review: `editor-ui/instrument-panels`

- contradiction: the map said the registry draws "the panels whose windows are open" and calls `OnHidden` for the others; `editor-ui/shell` and the pin (`EditorPanelRegistry`) draw only windows that show, so an open panel behind another tab also gets `OnHidden`: the sentence, the diagram's caption, alt and decision node now say "shown".
- wrong: the summary forms "Build 4 succeeded" and "Build 4 succeeded with 1 warning" lacked the period that `ProblemsPanel::Rebuild` writes after every form: corrected.

Checked at the pin without finding: the Problems idle check, stack filtering and summary forms, the clipped table and file texts, the Console's collecting, filters and unread errors, the Streaming panel's sections, `c_TableRefreshSeconds` 0.25, the job and `OnDetach`, the Activity filters, buttons and row key, the Performance spike threshold (the larger of 1/60 s and twice the median work time), its bound line and `c_SummaryRefreshSeconds`, the Problems request counter in `play.start`, and the test suites.
