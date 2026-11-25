# Notes: light/reflectance

## New terms

None proposed. Bold definitions on the page are all glossary terms of the brief, plus masking and shadowing (plain words, defined once in a sentence of the visibility section).

## Since

0.3.0: the GGX, Smith, Schlick and Lambert BRDF is listed at 0.3.0 in plan/inventory/render-direct.md line 56; F0 from the IOR is 0.8.0 (render-direct line 45), taught here as part of the same model.

## Requests

- Words for tools/data/extra-words.txt: bidirectional (the BRDF's expansion), refraction (the IOR's expansion).
- Names for tools/data/names.txt: Phong, Blinn, Cook, Torrance, Beckmann, Walter, Burley, Disney, Filament (the table of approaches and its sources).
- Figures not drawn (the page uses two Mermaid diagrams and tables; no figures file): the microfacet anatomy picture (D widening with roughness, G and F panels, Fresnel curves for 1.33, 1.5, 2.42 and a metal) and the IOR sweep (water, glass and diamond spheres, `lookdev.ior` of render-indirect:432; the Showcase water material has IOR 1.33 in Tools/GenerateShowcaseProps.py).
- External hosts for Further reading are not requested: the entries are cited without links.

## Not verified

- The claims about other models (Phong's peak and total, Blinn-Phong, Beckmann's falloff, Disney's parameters, Smith correlation giving more light than the product) come from the cited papers, not from the pin.
- Phong's lack of reciprocity (brief) is not stated: the page names the energy budget, Fresnel and the meaning of the exponent instead.
- The Showcase's puddles at 1.33: only the Showcase's Water material (IOR 1.33) was checked.

## Findings not applied

None open in the brief.

## Clerk

- Admitted to names.txt: Phong, Blinn, Blinn-Phong, Cook-Torrance, Torrance, Beckmann, Walter, Burley, Disney, Filament.
- Admitted to extra-words.txt: bidirectional, refraction.
