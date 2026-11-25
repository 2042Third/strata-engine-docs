# Notes: gpu/resources-lifetimes

## Since

since 0.3.0: render-core inventory lines 74-78 give "0.3.0 + later fixes" for barriers and event queries; the queue's own release is not stated.

## New terms

None. The page defines constant buffer, volatile constant buffer and deferred release (its glossary terms) in bold.

## Requests

None. Further reading cites O'Donnell's FrameGraph talk (GDC 2017), the Vulkan specification and the NVRHI readme without links.

## Not verified

- The experiment of exercise 2 (nullptr against ReleaseDeferred, validation errors) was not run; the page says "expect" and cites the engine's comment.
- Claims about other engines (render graphs in some commercial engines, frame-number deletion queues) rest on general knowledge and the cited talk, not on the clone.
- That a validation error appears for a dropped cleared target on every driver: the header calls it one; timing may hide it.

## Findings not applied

None: the brief listed no open findings.

## Clerk

- Nothing asked.
