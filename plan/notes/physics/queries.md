# Notes: physics/queries

## New terms

- query category: the bit 63 that every shape's mask holds and only queries carry, so a query finds a shape whatever it collides with; home: this page; no aliases. The page also defines `raycast` and `shape cast`, homed by the glossary.

## Requests

- No figures; the one diagram is Mermaid.
- No external hosts requested; Further reading entries are cited without links.

## Since

0.3.0: the query host functions are "pre-0.3.0 append" (inventory scripting:73), so queries exist since the first physics module.

## Not verified

- Claims that Unity, Unreal and Godot offer sphere and box sweeps, and that Unity has a setting that updates transforms before queries, are from general knowledge; no source was opened.
- That a callback per hit would cost a guarded call into module code is the page's inference from the crash guard rule, not a statement of the engine.
- Which box3d function a `SphereCast` would use: not checked (the exercise answer leaves it open).
- That a ray starting inside a triangle mesh collider reports a hit: only the code's rule for convex shapes is stated.
- The Playground's `GrabDistance` value: not read; the page quotes only the code.

## Findings not applied

- The brief lists no open findings. The `SphereCast` and `OverlapCapsule` exercises of item `physics:465-466` appear as one paper exercise (`SphereCast`) with a worked outline, no patch file and no `OverlapCapsule`, to keep the page within size M. Item `new:17` (trace it) is exercise 3.

## Clerk

- Refused the term query category: the glossary homes it on physics/collision-layers (only its home words it).
