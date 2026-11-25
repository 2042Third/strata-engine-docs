# Notes: `assets/loading`

## New terms

None proposed. The twelve glossary terms homed here are defined in bold on the page.

## Requests

- No new words, names or hosts. Further reading cites Unity, Unreal Engine and Godot documentation without links.
- No figures file: the four figures (load in time, parts of a load, dispatch decision, asset states) are Mermaid diagrams.

## Since

`since: 0.3.0`. The asset manager, its streaming queue and generations are not dated against a tag in these notes; the earliest release the field allows is used.

## Not verified

- The reasons the page gives for the byte bound ("a count of 8 loads is harmless for small meshes") and for not retrying a failed load are explanation, not statements of the code.
- The remark that a short fault such as a busy drive also leaves a load failed follows from the code (no retry) but is not tested.
- The alternatives table names Unity's blocking resource loading, Unreal Engine's asynchronous asset loading with a delegate, and Godot's threaded `ResourceLoader` with a polled status from general knowledge; no source was read.
- Timings of the worked example (200 MB per second, 30 ms decoding, a first frame near 14) are invented numbers, presented as an example.
- That `RuntimeAssetManager` never waits for an import: it does not override `IsAwaitingImport`, whose base returns false (checked by search, not by running).
- That a game never calls `ReloadAsset` is the brief's statement; not searched for in the runtime.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing asked.
