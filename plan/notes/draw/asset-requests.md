# Notes: draw/asset-requests

## New terms

None proposed. The page defines the four glossary terms (asset resolve cache, prefetch distance, replay, request priority) in bold, plus the local words "use bits" and "memo".

## Requests

- No new host. The two Further reading entries (Nystrom, Gregory) are cited without a link.
- Figures: `streaming-view-opening` and `request-priorities` (variants early, later) need the layout `layouts/scene-view.ini` and the OpenWorld sample; both wait for tier 2: editor screenshot.

## Since

0.3.0: the resolve cache, use bits, prefetch and the default-material fallback are listed 0.3.0 in the inventory; replay's first tag is not stated.

## Not verified

- The comment that a comparison sort of 10,000 material slots took a sixth of a frame is quoted from the code comment, not measured.
- That the streaming view is chosen by an entry of the Scene view's debug view chip: the label "Streaming" is in ViewportPanel.cpp, the chip's layout was not read.
- The editor's `viewport.setSettings` accepting `debugView: streaming` was taken from the inventory and the brief, not read in the command's code.
- EndFrame's body was not read; the page relies on the header comment and `m_Used`.
- The two Further reading entries are named from memory of their subject, not checked.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing to admit.

## Figures

Photographer, 2026-11-18, provisional build (engine 5b975ad2831e, `--provisional`): one round, nothing published; both
recipes keep their `waitsFor`.

- Both recipes now picture the Scene view alone (`editorWindow.panel` `Viewport`, 797 × 499 px in
  `layouts/scene-view.ini`) after a `camera.set`, since the editor's own camera framed no subject.
- `streaming-view-opening`: cannot show the opening. Round 1, camera at -112, 40, -12 toward Camp1 (-144, 22, -48),
  fov 40: the camp's tents among trees, nothing tinted, no boxes, the legend in the lower left reads Loading 0 and
  Failed 0. An editor figure is pictured only once the window is settled (`editor.screenshot` expects `settled`, after a
  wait of 120 frames), so every request is answered by then; `make/performance`'s streaming view found the same. The
  recipe now states that state: caption, alt and shows say that nothing is tinted and the legend counts 0 and 0. The
  page's "the view fills with tints that fade as the requests are answered" needs a picture taken while the world
  loads, which needs a screenshot that does not wait to settle (or a `live` capture during the load, not taken yet);
  until then the figure shows the end of that fade.
- `request-priorities` (early, later): cannot be shown. Round 1, camera at -60, 90, 60 toward -150, 20, -50, fov 45:
  both variants are the same picture (forest, the hill's rocks, the legend at Loading 0 and Failed 0), for the reason
  above; the early variant cannot catch a pending count above 0, and no picture shows which requests are High. Caption,
  alt and shows are left as the page writer wrote them and are not true of these takes. The page needs either a
  screenshot that does not wait to settle (the early variant), or instead a text figure or chart of the pending count by
  priority over the first frames of the load (one run's measurements), or a diagram; the later picture alone matches
  `streaming-view-opening`'s.

Photographer, 2026-11-23, pin v0.8.0 (319075e3), one round, all three pictures published; `waitsFor` removed from
both recipes (the pin has `editor.screenshot`), recipes otherwise unchanged.

- `streaming-view-opening`: the camp's two red tents among teal-green trees, nothing tinted, no boxes; the legend in the
  lower left reads Loading 0 and Failed 0. Caption, alt and shows are true of it, and so is the page's paragraph
  ("The picture below comes from after the opening, so nothing is tinted").
- `request-priorities` (early, later): the two pictures are identical (forest on the plain, rocks on the dark slope,
  legend Loading 0 and Failed 0), as the caption and the page now say. True but it teaches little: no picture shows a
  tint or which requests are High. A later page revision could replace the pair with a text figure or chart of the
  pending count by priority over the first frames of a load (one run's measurements), or a diagram.

Photographer, 2026-11-23, pin v0.8.0, mending a viewer's faults, one round, all three published again.

- Both recipes set `sceneGizmos` and `selectionOutline` false: the orange and red gizmo diamond between the tents (and
  at the centre of the pair) is gone.
- `request-priorities`: the later variant now waits its 600 frames after `camera.set` (each variant has its own
  `editorWindow.steps`); the earlier take waited before it, so both shots were 120 frames after the camera arrived.
  The pictures are still alike, as the page says; caption and alt now say they are two runs of the editor. An early
  picture with tints cannot be taken: `editor.screenshot` expects `settled` after the take's 120-frame wait, and the
  page's paragraph says both legends read zero. One picture in place of the pair needs the page's two `::figure`
  lines changed.
- `streaming-view-opening`: the caption now points at the highlighted layers chip (upper right) as the Streaming view
  and at the legend in the lower left. The legend stays small (text about 9 px in a 797 px capture at UI scale 1): an
  enlarged crop needs a `crops` entry in the recipe and `::figure{id=streaming-view-opening crop=legend}` in the page,
  which only the page writer may add. A wider window to show the chip's label would shrink the legend at page width.
