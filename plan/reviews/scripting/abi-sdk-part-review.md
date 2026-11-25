# Part review of `scripting/abi-sdk`

- wrong: the toy was said to hold its three ideas "in 60 lines"; the sketch has 85 lines, and the sentence now says so.
- contradiction: the contract said "Only `Log` may be called from any thread"; `ScriptABI.h`'s "Diagnostics (callable from any thread)" block holds `Log` and `ReportException`, and `scripting/shared-libraries` spoke of logging functions: both pages now name the two diagnostic functions.

Checked and holding: 165 host functions, the 19 pointers and 184 bytes of `StrataScriptClassDesc` with `OnUISubmit` at 176, the callback flag bits (`Coin` 291; `OnDestroy` and `OnCollisionExit` 144), `Coin`'s fields and defaults, `NewerSDK`'s 112-byte description, the layout asserts, `GetScrollDelta` as the baseline, `s_ConstructingEntity` set by `CreateThunk`, the duplicate-class refusal, `Gameplay.h`'s helpers (only `KeyRepeat` calls `Input`), `Strata::Random` and `Timer` in the engine, the 30 checks of the entity script, the guard bytes of `Scripting.Module`, `Architecture.ScriptSDK`'s two cases, the `ST_SCRIPT_HOST_FUNCTIONS` assert, every callout line against the pin.
