# Part review: image/encoding

- contradiction, wrong: the contract said no file of `StrataEditor/src` names `DitherOutput`, so the editor cannot switch it, while the opening says `viewport.capture` switches it; at the pin `viewport.capture` has the renderer switch `DitherOutput` (`StrataEditor/src/Editor/ViewportRenderer.cpp`); the contract now says so.
- wrong: the bands program's output was read as "each code holds 266 to 325 columns, so the eye sees six flat bands"; the last code holds 146 and seven codes make seven bands; now "each code but the last" and "seven flat bands".
