# Part review: image/grading

- contradiction: the grading's rows, offset and power were said to go into push constants; `TonemapConstants` is a volatile constant buffer, as `image/tone-mapping` says and `SceneRendererPost.cpp` writes it; now "its constant buffer, `TonemapConstants`".
- gap: the figure `lookup-sweep` was taken with sky and robot crops that its caption names, but the page placed none, so pagecheck failed; the six crops are now placed after the three variants.
