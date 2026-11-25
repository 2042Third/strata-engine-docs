# Notes: physics/world-step

## New terms

None proposed. The page defines the four glossary terms homed here (collision step, synchronization, write-back, golden hash).

## Requests

- Extra word: `bitmap` (used 8 times: "a bitmap with one bit for each body slot"; the brief itself names "the write-back bitmap"). The word-list check fails on it.
- Figures: none requested; all four diagrams (frame timeline with the physics overlay, inside a fixed step, two copies of the truth, parallel write-back) are Mermaid. The timeline's overlay is a flow chart here, not the captured figure of `world/systems`.
- Sidebar entry for `physics/world-step` if not present.

## Since

`since: 0.5.0`: inventory rows for `PhysicsTaskSystem` and determinism name 0.5.0 (`physics.md` lines 74 and 149). The sync and write-back may be older.

## Not verified

- Tracy zone names are inferred from `ST_PROFILE_FUNCTION` in `PhysicsSystem::OnFixedUpdate`, `SyncEntitiesToBodies` and `WriteBackDynamicBodies`; no trace was taken.
- The Alternatives table's "Who uses it" column states general practice of engines and is not cited.
- That a property edit through `Entity::SetProperty` reaches the world as a component change that rebuilds the body: taken from the test `Property edits rebuild the body and keep its motion` and `PhysicsSystem.h`'s comment on `on_update`; the rebuild code itself was not read.
- `ScopedJobSystem` described from its use in the tests, not from its definition.
- The further-reading entries are named from memory, with no link.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to extra-words.txt: bitmap.
