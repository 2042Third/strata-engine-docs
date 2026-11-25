# Part review: `animation/skeletons`

- unclear: "Select the skeleton sub-asset of a model in the Asset Inspector and its Joints section lists the tree": the reader selects the sub-asset (in the asset browser) and the Asset Inspector shows it (`AssetInspectorPanel.cpp` draws the `Joints` section for a selected skeleton); now "Select the skeleton sub-asset of a model, and the Joints section of the Asset Inspector lists the tree".
- wrong: "the editor shows the same result on animators in scenes that are not playing": the preview's edit pose is the rest pose only by default (`AnimationPreview.h:41`, `AnimationEditPose::Rest`; `ClipStart` is the other mode, taught on `animation/editor`); now "by default the editor shows the same result".
- contradiction: the page defined **animator** in bold, a term homed on `animation/importing` (outside the Needs closure); the bold is removed and the defining clause kept, as the brief asks.
