# Part review: `worlds/export`

- unclear: the toy section told the reader to "look at the last two runs" of `worlds-export-toy.cpp`, but the page showed no output; its output fence is added (filled by pagecheck), with the callouts after it.

Checked at the pin and found right: the seven states, the stage text "Packing {} assets ({} of {} MB)", the order of the failures in `GameExport::Start` and the folder created last, `BeginCooking` for every world, `FinishCooking` writing without an undo step, the job's script check, icon and stamp before the pack, the order of the writes, `IncludeScriptSymbols` off only in Dist, the window of 1280 by 720, `ToFileName`, the `project.exportStatus` reply, the suites `Editor.Export` (also in `WorldGameExportTests.cpp`) and `Editor.Export.GameIcon`, and every callout.
