# Part review: `physics/world-step`

- wrong: the example "A script writes the crate's height 3 m and calls `MarkModified`": a script cannot call it; the script host's `SetTransform` runs `MarkModified` for it (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp`). Now says so, and names engine code as the writer that can skip the signal.
- wrong: Check yourself 1 had a script set a sleeping crate's `Translation` with no effect; a script's write is signalled, so the crate moves. The question now names engine code, and the answer adds that scripts never meet the case.

Checked at the pin: `c_ParallelSyncThreshold` 1,024, `c_ParallelWriteThreshold` 512 and the chunk arithmetic, the 24-body pile (25 poses), the 643-body crowd with 640 written, the golden-hash test with four workers, `SettlingSums` in 1e-8 m units, `SetGravity` waking every body, the stats fields, `IBodyMotionQuery` and `IBodyControl`, the SDK's `Teleport` overloads and `Entity::SetProperty`.
