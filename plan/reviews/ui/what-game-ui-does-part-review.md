# Part review: ui/what-game-ui-does (group 1 of 1)

- contradiction: the frame's step 2 said the system "rebuilds the hit grids" and ends by queuing the widget events; `ui/input` (and `GameUISystem::OnUpdate`) rebuild only grids whose layout or hit stamp changed and end with `DispatchEvents`; the step now says "the hit grids that changed" and "delivers the queued widget events".

Checked and held at the pin: eleven `ComponentRegistry::Register` calls, the menu's ten component types (`MainMenu.stscene`), `ReferenceResolution` 1920 x 1080 and `MatchWidthOrHeight` 0.5, `c_RepeatDelay` 0.4 and `c_RepeatInterval` 0.1 (`Input/UIActions.h`), the GameUI layer's `MayInclude` (Core, Input, Asset, Reflection, Scene, Renderer), the overlay order (world text, `DrawWorld`, then screen text and screen canvases), `MainMenu`'s `Focus()` on Play in `OnCreate`, the selectable's three navigation modes, the exercise's tutorial file.
