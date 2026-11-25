# Notes: audio/testing

## New terms

None proposed. RMS is defined in bold on the page.

## Requests

- Figure `audio-state-answer` (text capture of `audio.state`) needs a recording from the Tetris sample after `play.start` and a wait; the recipe's `keep` pointers are `/voices`, `/oneShots`, `/listener`, `/masterVolume`.

## Figures

- `audio-state-answer` (published, round 2). Round 1 (play.start, 120 frames) answered `voices: []` and all one-shot
  counts 0: the headless frames ran in about 0.07 ms each, so no piece locked and nothing played. Round 2 adds a tap of
  Space (hard drop, which plays `Sounds/Lock.wav` as a one-shot) and `play.pause` right after it, because the lock
  clip is a fraction of a second long: the answer shows one voice (playing and paused, not spatial, not waiting) and
  `oneShots` with 1 playing, 1 played, 0 dropped. Caption, alt and shows rewritten to say so.
- Page: the terminal block before the capture lists only `play.start` and `audio.state`; those two alone answer with an
  empty voice list. The page could add the Space tap (`StrataCLI call input.key` with key Space) and `play.pause` to
  match the captured answer.
- `audio-state-answer` (round 3, caption only, no retake). A viewer saw the block above list only two commands and the
  voice read playing and paused together. The caption now names the Space tap (`input.key`) and `play.pause` and says
  a paused voice still counts as playing (pin `AudioSystem.cpp` 423-424: a one-shot reads `Playing = true` until it is
  reclaimed, `Paused` while the scene's pause holds it). The page's words still need the two commands in the sh block
  and its lead-in, and a sentence under the answer explaining playing with paused.
- `audio-state-answer` (retaken at v0.8.0, pin 319075e3, one round). I took it again with the same recipe and diffed
  it against the answer published at 822a7a46. Only the voice's `seconds` changed (0.116 to 0.070): that is how far
  the playback had got when the pause came, so it depends on timing. Everything else is the same: one Lock.wav voice
  that is playing and paused, one-shots 1/1/0, the listener at (5.5, 9.5, 30) and master volume 1. I published it and
  `fill` rewrote the page's fence. The page's sh block now lists the Space tap and `play.pause`, so the page problem
  above is resolved.
- `audio-state-answer` (caption only, no retake). A viewer saw the sh block before the capture (page line 332) run
  `StrataCLI call play.pause` with no arguments; at the pin play.pause requires `paused` (PlayCommands.cpp 176-181:
  "Missing parameter 'paused'"), so that line fails. The recipe sends `{"paused": true}` and the answer is right; the
  caption now says play.pause with paused true. The page's line 332 still needs
  `StrataCLI call play.pause '{"paused": true}'` (page text, not the photographer's to change).

## Not verified

- That the Tetris sample plays sound within 120 frames of `play.start` (the capture may show empty voices).
- That the mix runs on a separate mixing thread (taken from the test name "through the mixing thread"; not read in the engine code); the page no longer states it.
- Sketch numbers (0.002 smoothing step) are the toy's own, not Strata's smoothing.
- Further reading entries name sources without links.

## Findings not applied

None: the brief listed no open findings except item 759, applied (release notes line 177 of Docs/Releases/0.3.0.md checked).

## Clerk

- Nothing asked.
