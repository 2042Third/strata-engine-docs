# Notes: audio/scene-system

## Since

0.3.0: Docs/Releases/0.3.0.md lists miniaudio playback with spatial sources, a listener (component or camera) and one-shot sounds.

## New terms

- source record: the Audio system's per-entity data: the voice, the component values last applied and the flags of what the game asked for. Home: audio/scene-system. Aliases: record.

## Requests

- Layouts: layouts/inspector-audio.ini (Inspector with Audio Source and Audio Listener entities of the Physics Playground), layouts/console-audio.ini (Console with the dropped one-shot warning).
- Figure console-dropped-warning needs a recipe that forces a drop (many one-shots of a clip not loaded); setup commands not written.
- Further reading cites a book and the miniaudio documentation without links.

## Not verified

- That the scene's runtime update is called from a layer before the modules' OnUpdate in every program (Application.cpp runs layers, then modules; the page states the order only for the frame diagram).
- Further reading entries (Game Audio Programming chapters) are from memory, not checked.
- The Third-Person's Footstep event raised by the walk and run states: taken from the sample's script header comment.
- Impact.cpp's TakeSoundBudget is not described (not read).

## Findings not applied

- None open in the brief beyond the five-places AssetManager::GetActive finding, which is applied (checked at AudioSystem.cpp:141, 554, 613, 750, 908; scene path at 443).
- Brief items on "Tetris" sample, and the engine-wide screenshot of Inspector, are covered only as a figure request; Tetris is not discussed.

## Clerk

- Admitted the term source record, homed here, from the page's sentence. Refused the alias record: a common word (tools/data/common-words.txt).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken with the provisional build (2026-11-18); nothing published, both keep `waitsFor`.

- inspector-audio, 1 round: the Physics Playground has no entity with an Audio Source (its impacts are one-shots), and
  the Inspector shows one entity, so the recipe makes an entity Speaker with an Audio Source (clip Metal) and an Audio
  Listener and pictures the Inspector panel (layouts/make-sound.ini). Pitch is a number field, not a slider: caption and
  alt now say a volume slider and a pitch; the caption says Speaker carries both only for the picture. Good.
- console-dropped-warning, 2 rounds. Round 1 set the Playground's GoalSound field to an image (Icon.png) to force a
  drop: no warning for it appeared, but the demo's pour (play 960 steps) dropped impact one-shots for the 64-voice limit
  by itself, so round 2 has no setup. The reason shown is "more than 64 one-shots played at once", not the page's
  "took longer than 0.25 s to load": commands cannot make a clip load slowly (it needs a large clip file and a script);
  caption, alt and shows now describe the voice-stealing drop. Lines were cut at 673 px: new layouts/console-audio.ini
  (Hierarchy 140 px, Inspector 260 px, Console 876 px) shows them whole. The clips and times vary between takes (the
  impact budget refills by real time); Soft warned twice, more than a second apart. Good.

Viewer's faults, mended 2026-11-18 (provisional build, both figures in one hold; nothing published):

- inspector-audio had no picture in the take folder (round 2 retook only the Console). Retaken with the same recipe:
  Speaker's Transform, Audio Source (clip Metal, Volume slider at 1, Pitch 1, Loop off, Play On Start and Spatial on,
  Min Distance 1, Max Distance 50, Rolloff 1) and Audio Listener (Active ticked), as caption and alt say. Good.
- console-dropped-warning, unreadable bottom rows: the take's own commands (play.step, editor.wait, editor.showPanel)
  log [App] rows after the warnings, and with Auto-scroll they always fill the bottom; no command in the pin filters
  the Console. The recipe's step editor.showPanel Console duplicated the one the take adds: removed (3 [App] rows, not
  4), and a crop `log` (rect 0, 0, 1, 0.7767) keeps the toolbar and every row down to the last warning; its cut fell
  between the last warning and play.step in the retake. **The page needs `::figure{id=console-dropped-warning
  crop=log}`** to show the crop (page text, not changed here), as make/sound's coin-console does.
- console-dropped-warning, unclear caption: now says that the Physics Playground pours bodies into goals ("demo" is on no word list). The
  viewer's "Soft at 15.06 and 16.75" misread the first take (16.75 was Wood: Wood at 14.93 and 16.75); the retake has
  Wood at 15.23 and 17.05, so clips and times change between takes. Caption and alt point to the repeat without names
  or times: the clip named twice warns the second time more than a second after the first.

Taken at the pin v0.8.0 (319075e3, Release build), 2026-11-23, both figures in one hold, without `--provisional`;
`waitsFor` removed as `check` asked; published.

- inspector-audio, 1 round: Speaker's Transform, Audio Source (clip Metal, Volume slider at 1, Pitch 1, Loop off, Play
  On Start and Spatial on, Min Distance 1, Max Distance 50, Rolloff 1) and Audio Listener (Active ticked), as caption
  and alt say. Good.
- console-dropped-warning, 1 round: goal lines, four yellow Audio warnings (Wood 15.29 s, Soft 15.41 s, Metal 16.06 s,
  Wood again 17.10 s), each giving "more than 64 one-shots played at once, so the oldest was cut off". The crop `log`
  cuts just below the last warning, above the take's [App] rows. Wood is named twice 1.8 s apart, as the caption says.
  Good.
