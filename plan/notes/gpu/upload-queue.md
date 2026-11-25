# Notes: gpu/upload-queue

## New terms

- batch: the group of upload steps recorded between BeginBatch and SubmitBatch and sent to the GPU in one submission, closed with a fence; home gpu/upload-queue; aliases: upload batch. (Defined in bold on the page; proposed, not required by the brief.)

## Requests

- None. No names or extra words proposed.

## Since

- 0.3.0: the upload path and staging pool exist from wave 3 (inventory render-core:84-88 list wave 3 for the queue); PrepareBackBuffer 0.4.0 (render-core:65).

## Not verified

- NVRHI's own writeBuffer internals (page says only that it takes staging outside the pool and budget).
- The "Who uses it" cells of the alternatives table are generic and cite no other engine.
- The 2 ms frame upload budget in the worked example is an assumed number, not a default.
- The measurements (0.4 to 1.2 ms, 595 to 622 MB) are quoted from code comments, not re-measured.
- The tests' exact list is from test names at the pin; none was run.

## Findings not applied

- The brief lists no open findings. Omitted by choice: "What went wrong before" (no regression history verified); the optional black-frame figure render-core:543 (covered in prose and the PrepareBackBuffer quote); the "design note" box (the pool's design note is taught in prose); assets:200/202/203 details "c_MaxPendingBytes 256 MiB" is applied, the tenth in reserve is applied; "AwaitingGPU" applied.

## Clerk

- Admitted the term Batch (gpu), homed here (alias upload batch); the glossary's other batches keep their homes.
