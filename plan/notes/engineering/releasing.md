# Notes: engineering/releasing

## Since

0.3.0: the release workflow and the install rules are listed as 0.3.0 in the build-test inventory (`Docs/Releases/0.3.0.md` exists at the pin).

## New terms

None beyond the seven glossary terms the brief homes (install tree, installation marker, CPack, pre-release suffix, release candidate, dry run, checksum file), each defined in bold.

## Requests

- Figure `archive-folder` (file browser view of the unpacked archive): owner takes it; waitsFor tier 3 (see ## Figures).
- Host `semver.org` is not in the external hosts list; "Semantic Versioning 2.0.0" is cited without a link.
- Words the lint refused and the page avoids: workflow, TGZ, notarized, typo, Chocolatey. "Workflow" would help every CI page.

## Not verified

- That the macOS runner archive keeps its symbols for the reason the packaging comment gives (strip would have to re-sign): stated from the comment only.
- The contents of `Docs/Releases/PackageReadme.md` beyond its first lines.
- That a downloaded archive triggers a system warning: not claimed as fact beyond "may".

## Findings not applied

The brief lists no open findings. The brief's quotes of `release.yml` lines 45-93 and 175-226 are quoted as the `run:` bodies (51-93, 178-226), because the lines before are YAML.

## Clerk

- Nothing to admit.
- Admitted to external-hosts.txt: semver.org. workflow is now a term (engineering/ci), so the page may use it.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `archive-folder` (kind tool, owner's file browser picture): not placed at the v0.8.0 pin. No take of the tool can
  show a folder of the operating system, and the paragraph teaches fully without it: the `:::files` tree just before it
  lists every top entry of the unpacked folder, checked against the layout comment at the top of
  `CMake/StrataPackaging.cmake` at the pin. The entry keeps its `waitsFor` as the request for a later edition and gives
  `noStandIn`; the paragraph before it needed no change, since it never introduced the picture.
