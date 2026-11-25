# Part review of `make/gameplay-math` (group 3)

Checked against the engine at the pin and the part's other pages.

- wrong: the callout of the Playground quote said a negative cursor position means "a cursor that has not moved in yet"; `Input::GetMousePosition` counts pixels from the view's top left, so a negative value is a cursor left of or above the view.
