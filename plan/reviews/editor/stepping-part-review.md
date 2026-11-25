# Part review: editor/stepping (group 3 of 3)

- wrong: the example said `play.start {paused: true}` answers with `fixedSteps` 0; `play.start` answers `DescribePlayState`, which holds only `state` and `paused` (`StrataEditor/src/Editor/CommandUtils.cpp`), so the page now says it answers with the state `Play` and `paused` true, no fixed step run yet.
