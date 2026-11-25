# Part review: `editor-ui/widget-kit`

- wrong: "`BeginDisabled` scales that alpha by `DisabledAlpha`, 0.6 by default" and $0.18 \times 0.6$: the editor's theme sets `DisabledAlpha` to 0.5 (`StrataEditor/src/UI/Theme.cpp:268`); now 0.5 and 0.09.
- contradiction: "A literal color breaks the light and dark themes and the contrast checks": the editor has one theme (`editor-ui/design-system`, "One theme only") and no contrast check exists at the pin; now "does not follow a change of the theme, and the source scan ... fails it".
- wrong: the toy strip's callouts were one line late (destructor sum at 30-32, walk 34-38, decision 39, `NextIsIcon` 47-48 of the sketch); renumbered.
- unclear: "The function is the toy's steps 1 and 2" while `DrawButton` takes all seven; now "takes the toy's steps".
