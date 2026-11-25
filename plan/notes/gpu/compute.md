# Notes: gpu/compute

## New terms

- thread: a single copy of a shader program that the GPU runs on one item of data; home gpu/compute; aliases: invocation.
- dispatch: one command that starts a compute shader as many thread groups; home gpu/compute.
- thread group: a fixed number of threads that run together and share fast memory; home gpu/compute; aliases: workgroup.
- shared memory: small fast memory shared by the threads of one thread group (groupshared); home gpu/compute.
- group barrier: a point where all threads of a group wait for each other; home gpu/compute.
- atomic operation: a read-change-write of a memory cell that no other thread can split (used here; home basics/threads).

## Requests

- Word "unordered" for extra-words.txt (the expansion of UAV, "unordered access view").
- Hosts for Further reading are cited without links (Microsoft, NVIDIA, Khronos documents).

## Since

- 0.3.0: SceneRenderer::CreateComputePipeline listed since 0.3.0 in inventory render-core:96.

## Not verified

- That NVRHI inserts a UAV barrier for a repeated UnorderedAccess state (page says only what the source comment says).
- The table's "Used by" column and Further reading sources are general knowledge, not engine facts.
- Exercise 2 breakpoint check on a source build was not included.

## Findings not applied

- The brief lists no open findings.
- new:7 evidence (no CommandQueue::Compute in Strata/src; no Wave calls in shaders) verified at the pin: grep found none; compute queue fetched at VulkanGraphicsDevice.cpp:939-940.
- Page claims culling's prefix allocation uses an atomic running offset (CullBuild.comp.slang); it does not teach a deterministic scan as Strata's own.

## Clerk

- Admitted terms homed here: Thread (gpu) (alias invocation; the glossary's thread stays basics/threads'), dispatch, thread group (alias workgroup), shared memory, group barrier.
- Refused: atomic operation, already the glossary's, homed on basics/threads.
- Admitted to extra-words.txt: unordered (G0 has 6).
