# Notes: draw/render-scene

## Since

0.3.0: render proxies and instance data (inventory render-scene rows, release 0.3.0).

## New terms

None proposed; the page defines the eleven glossary terms of its brief.

## Requests

- No figure file: all diagrams are Mermaid. The before/after picture of placeholder bounds (a terrain whose origin is out of view) is not requested; the page uses a decision diagram.
- Links to pages not yet written: draw/entities-to-draws, draw/bounds-culling, draw/skinned, draw/mirrors-camera-relative, draw/render-scene-gpu, light/lights.

## Not verified

- The motion history's check of the entity ID (brief) is not stated; only the fade state's check (`LODSelection.cpp`) is.
- Which entity a given proxy index holds after the first sync (EnTT view order) is not stated.
- The 4 ms and 36 ms figures are from code comments, not measured here.

## Findings not applied

None: the brief lists no open findings. Not included: a "What went wrong before" section (no history found at the pin).

## Clerk

- Nothing asked.
