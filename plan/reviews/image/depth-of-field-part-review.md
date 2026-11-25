# Part review: image/depth-of-field

No correction.

Checked without change: the thin-lens example and table (26.7 pixels, the 2 % clamp), the camera's five fields and their defaults, `CameraLens::FromEntity`'s clamps and focal length (20.78 mm for the Third-Person camera's 60 degrees), the focus along the forward axis and the near plane, `GetFocusMillimeters`'s 1.1 focal lengths, the 0.7, 1.4 and 0.24 pixel disks, the parameters and tile sizes (8 and 11), the shared circle of confusion, the prepare, tiles, dilate, gather (48 Vogel samples, golden angle, `c_MaxNearShare` 16) and composite (12 by 12 table, `c_FocusReach` 2, the fade) passes, the `RenderFrame` condition, the lens of GameRenderer.cpp and ViewportRenderer.cpp, the tests of `Renderer.CameraLens` and `GPU.SceneRenderer.DepthOfField` (16 frames, 6 codes), and the exercises' numbers.
