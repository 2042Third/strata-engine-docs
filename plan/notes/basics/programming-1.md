# Notes: `basics/programming-1`

## New terms

None proposed. The page defines in bold the 16 terms the brief lists (statement, value, type, variable, assignment,
expression, operator, boolean, comparison operator, logical operator, condition, if statement, scope, namespace, scoped
enumeration, switch statement) and also **field** (a variable of a script class that the editor shows), whose home is
not this page.

## Requests

- `tools/external-hosts.txt`: `learncpp.com`. The brief links a learncpp lesson per section; the page cites "Learn C++"
  in Further reading without a link until the host is allowed.
- Figures: none requested. The page has one Mermaid diagram (the start function once, the update function every frame)
  and no figure manifest.
- Sketches: seven files `sketches/basics-programming-1-*.cpp` (types, arithmetic, decisions, switch; division,
  fallthrough, goldspin for the Practice). All compile with the sketch check and their output is filled in.

## Not verified

- That the Inspector draws a `bool` script field as a box to tick: `PropertyWidgets.cpp` has a checkbox for `bool`
  properties, but I did not trace a script field to it. The brief's Coin Run item says "ticked".
- That New Script always writes a `float` field `Speed`: `ScriptProject.cpp:327-328` adds it when no fields are
  declared; the dialog may pass fields of its own.
- Coin Run's `Coin` script and its `DegreesPerSecond` field: `make/first-script` at this commit teaches a `Spinner` on a
  cube, not `Coin`. The page says "`Coin` on tracks G and B, `Spinner` on track E" as the brief does.
- The Console lines of a script's `Log::Info` as the Console draws them: the form `[time] [Script] text` comes from
  `ConsolePanel.cpp:139` and `Log.cpp:266`, not from a run.
- That a line logged every frame fills the Console's 4,096 lines "in a minute or two": 4,096 lines at 50 frames per
  second take about 80 seconds, which assumes one line per frame.
- Links to pages not written yet: `basics/programming-2`, `basics/programming-3`, `basics/cpp-classes`,
  `basics/cpp-generic`, `basics/numbers`, `basics/debugging`, `reference/script-api`.

## Findings not applied

- critic-basics-a-1, -2, -8, -11: applied. The playground is a script `Playground` on one new empty entity; the two
  lines that add a field and the rule stop, build, Play; truncation toward zero and the sign of `%`; the Trace box, the
  4,096 lines and the place named in the text. Not applied from -8: floor division and the round-up rule (they belong to
  `basics/numbers`). Not applied from -11: that the log file keeps every line (not verified at the pin).
- critic-basics-a-12 and -17 name `basics/programming-3`. The page mentions the `double` field and its message
  `Unsupported script field type` only once, in the types section and Common mistakes; the compiler-specific text of the
  error and the table of SDK words stay with `basics/programming-3`.
- The brief's "learncpp lessons linked per section": not applied, because the host is not on the allowed list (see
  Requests).

## Clerk

- `tools/external-hosts.txt`: `learncpp.com` and `www.learncpp.com` added (front page fetched: the Learn C++ tutorial site).
- "field": no request; the glossary homes it on `make/first-script`.
