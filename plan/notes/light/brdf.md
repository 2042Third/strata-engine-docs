# Notes: light/brdf

## New terms

None proposed. The page defines the three terms the glossary homes on it: specular aliasing, specular anti-aliasing (geometric) and `SanitizeHDR`.

## Since

0.3.0: the GGX, Smith, Schlick and Lambert shading is listed at 0.3.0 in plan/inventory/render-direct.md line 56. The widening itself was not dated at the pin; the page keeps the page's first-tag value.

## Requests

- Words for tools/data/extra-words.txt: bidirectional (the expansion of BRDF), refraction (index of refraction), compositing and anti-aliased (the expansions of CLEAN and LEAN).
- Names for tools/data/names.txt: Toksvig, Tokuyoshi, Kaplanyan (the aside on filtering methods; Further reading names Olano, Baker, Hill and Heitz, which are not read).
- No new external hosts: Further reading cites without links.

## Not verified

- The claims about other methods (Toksvig, LEAN, CLEAN, Tokuyoshi and Kaplanyan, Heitz) and their years come from the cited papers, not from the pin. The pin's source does not name the paper behind `c_SpecularAAVariance` (0.25) and `c_SpecularAAMaxKernel` (0.18); the page does not say the engine copies it.
- The comparison procedure of exercise 1 (two sun strengths, subtract, divide by the pre-exposure) was not run; the HDR target holds the color times `TemporalParams.y`, which is verified in `Strata/shaders/Scene/Forward.frag.slang`.
- The brief names the suite `GPU.SceneRenderer.Specular`; the pin has no such suite. The specular tests are in `GPU.SceneRenderer.Materials` (GPUSceneSpecularTests.cpp), which the page names.
- The stage list says the stages for global illumination and reflections are conditional; read from the indentation of `gpuTimer.Next` in `SceneRenderer::Render`, not traced through each condition.
- The six-variant picking: the glass without entity ids is chosen when the shaders load (`m_Specification.EntityIDs`), the velocity glass in `EnsureMotionResources`; the page's exercise names `SceneRenderer::CreateResources` for the first, which holds the line at 302.

## Findings not applied

None open in the brief. The brief's erratum (light culling and clusters timed in `GPU.Cull` only on GPU-driven frames, `GPU.Setup` otherwise) is applied in the map section.

## Clerk

- Admitted to names.txt: Toksvig, Tokuyoshi, Kaplanyan.
- Admitted to extra-words.txt: bidirectional, refraction, compositing, aliased (for anti-aliased: anti- is a known part).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `specular-aa-compare`, taken at the pin (v0.8.0) through `viewport.capture`'s `renderer` switch `SpecularAntiAliasing` (off, then on); its old `waitsFor` ("tier 3") is gone. The look-dev project holds no normal map, so the recipe uses the Showcase: each variant creates a metal material (roughness 0.03, the asphalt normal map `Textures/asphalt_02/asphalt_02_nor_gl_2k.jpg`) and a sphere at (4, 6, 2) in the yard, seen from the sun's side at 10 m, 768 by 768, the image's anti-aliasing off. Each variant makes its own material path, because a second `material.create` of one path fails in the same copy.
- Round 1 (sphere at 3.6 m): the bumps were several pixels wide, so the picture showed a bumpy mirror, not aliasing. Round 2 (10 m, roughness 0.1) and round 3 (roughness 0.03) look alike: off, the sun is one small spot in the mirrored sky and most pixels miss its lobe; on, the sun's light spreads into a wide patch of glints. The old caption ("single bright pixels" without, "one smooth patch of the same total light" with) is not what the pin shows in a still picture at golden hour: the widened picture is the brighter one, its patch flecked, not smooth. The caption now says what the picture shows, and a lead-in sentence before the figure introduces it.
