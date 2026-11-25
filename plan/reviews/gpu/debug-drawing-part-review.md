# Part review of `gpu/debug-drawing`

- gap: the light gizmos named directional, point and spot lights only; `DrawSceneGizmos` at the pin also draws rectangle lights (the face's outline, a stroke along the way it shines, the reach where ranges show, a diamond with a small rectangle far away), and one sentence now says so (time raised from 70 to 75 for the reading floor).
- unclear: the grid was said to "write the depth of the intersection" two paragraphs after the grid's pipeline was said never to write depth; the shader outputs `SV_Depth` for the test only, and the sentence now says it outputs the depth for the depth test.
