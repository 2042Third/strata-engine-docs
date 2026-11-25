# Part review: `indirect/seam`

- unclear: the frame diagram put each pass's slot on the arrow into that pass (SRV 11 into `GPU.AO`, the field's slots into `GPU.RadianceCascades`, 9, 10 and 18 into `GPU.Reflections`), against its caption; each slot now labels the arrow out of the pass that makes it.
- wrong: the link to `indirect/problem` carried a title no page has ("Why a scene needs indirect light"); it now names the page's title, "The indirect-light problem".
- gap: the worked example used a found reflection's occlusion of 0.9 (the toy's `c_ScreenOcclusion`) without stating it, beside a 0.9 that meant what the reflectance leaves; the example now states it.
- wrong: the frame-order callout said a failed GI frame sets "the field's weight in the constants" to 0; the pin writes the field's constants again with `FieldSize.w` 0, now said so.
