# Part review: appendix/history (group 1 of 1)

- wrong: the page said release 0.8.0 is not out, the programs report 0.7.0 and the 0.8.0 rows come from draft notes; at the pin `CMakeLists.txt` sets 0.8.0 (commit "Bump the version to 0.8.0"), `Docs/Releases/0.8.0.md` exists and `Docs/Roadmap.md` says "Wave 8 landed (2026-11-23); release 0.8.0 holds it", so the introduction, the 0.8.0 section's opening and "Where it lives" (now `Docs/Releases/0.8.0.md` instead of the draft) say so.
- gap: the 0.8.0 table lacked what its notes list among the news: rect lights, many shadowed point and spot lights, and the new agent commands (`asset.place`, `scene.raycast`, `lighting.makeAreaLight`, `editor.screenshot`, `asset.types`); rows and links to the area-light, local-shadow and radiance-cascade pages were added.
- gap: the 0.8.0 upgrade notes lacked the script ABI line every other release has; added (three host functions appended, 0.7.0 modules load unchanged).
