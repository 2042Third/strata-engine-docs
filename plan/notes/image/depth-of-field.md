# Notes: image/depth-of-field

## Since

0.7.0: the inventory entry for depth of field and motion blur (render-image, "Post-processing", "Motion blur") is dated 0.7.0.

## New terms

None. The five terms the brief homes are defined in bold on the page. The page writes "widening of tiles" and `Dilate` for tile dilation, because "dilate" is on no word list.

## Requests

- Figures `dof-pair`, `aperture-sweep` and `focus-entity` (kind scene, sample ThirdPerson): the entity names `Camera` (verified in the sample's `Course.stscene`), `Robot` and "the nearer entity" (not verified) in the setup steps are placeholders for the planner. A `FocusEntity` value must be an entity's id, and the variants carry their own `setup` (the recipe schema for that is not verified).
- Figure `coc-curve` (diagram): drawn by the illustrator from its `numbers`.
- Sources in Further reading without a link: Jimenez 2014 and Abadie 2018 (SIGGRAPH talks); ask for their hosts if links are wanted.

## Not verified

- The entity named `Robot` in the Third-Person sample and the picture's look at f/2.
- Who uses scatter and layered blur (the table's second and third rows rest on the cited talks and on the literature, not on a check).
- That the premultiplied near image stays correct under bilinear reads (stated from the composite's use of a linear sampler).
- The 0.20 ms cost in the developer guide: left out.

## Findings not applied

None: the brief lists no open findings. The brief's item for the racing camera's shutter angle (180 against 90) is not on the page: shutter angle belongs to `image/motion-blur`; the exercise covers the lens, the focus entity, f/2.8 and the players' rows.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- Photographed 2026-11-17 (three rounds): `dof-pair`, `aperture-sweep` and `focus-entity` are published. The recipes now
  open `Scenes/Course.stscene` (the sample starts in the main menu), name the focus entity by its ID (Robot
  `A94EC4E371BEB484`, Barrel `3E91A1A4E85F13E5`), and hide the game's HUD canvas (`entity.setActive`).
- `dof-pair` keeps the sample's 60 degree camera: the far islands soften only slightly, as the page says.
- `aperture-sweep` and `focus-entity` move the camera to 7.5 m behind the robot with a 25 degree view (about 54 mm),
  because at 60 degrees f/1.4 against f/8 differ by a few pixels only. `focus-entity` focuses a farther entity (the
  barrel on the next island, right of center) instead of a nearer one: no entity stands between the camera and the
  robot, and the soft robot in the center shows that the focus follows the entity, not the screen's center.
- Mended 2026-11-17 after a viewer's look. `dof-pair`: at page width the far course is a patch of about 130 by 150
  pixels, where the slight softening barely shows. The recipe now has a crop `far` (pixels 776 to 1152 by 40 to 340 of
  the 1920 by 1080 shot, scale 2), published for both variants (`dof-pair-off-far.webp`, `dof-pair-on-far.webp`):
  enlarged, the far trees, coins and cliff soften plainly while the top of the robot's head stays sharp. The page shows
  a crop only where it names it: the page needs `::figure{id=dof-pair variant=off crop=far}` and
  `::figure{id=dof-pair variant=on crop=far}` after the two pictures (a writer's change; the photographer does not edit
  the page). `aperture-sweep` and `focus-entity`: the chest (entity `Chest`, turned 180 degrees) is seen from behind and
  reads as a drum or log with grey ends; the captions and alt texts now call it the drum-shaped chest seen from behind,
  left of the robot's head.
- Retaken 2026-11-23 at the pin v0.8.0 (319075e3), one round, recipes unchanged. `figures.py compare` against the
  originals of 822a7a46: all five pictures differ by at most 11 levels (mean under 0.01 level), the crops likewise;
  `publish` found every file below the threshold, so the published files stay and their stamps record the check at
  319075e3. Looked at: the far course softens in the `dof-pair` crops, f/1.4 blurs the far island plainly against f/8,
  and with the focus on the barrel the robot is soft while the barrel and the chest are sharp.
- Mended 2026-11-23 after a second viewer's look; words only, no retake (the pictures at 319075e3 stand: the `Chest`
  entity is at (-3.2, 0, -14.8), turned 180 degrees, the barrel at (3.3, 0, -14.6), so the cylinder with blue ends at
  the island's left is the chest seen from behind). `aperture-sweep`: the caption names f/1.4 (first) and f/8 (second)
  instead of "nearly closed", and points to the chest (left of the island, seen from behind) and the barrel (right);
  `numbers` added. `focus-entity`: caption and alt say where the barrel (right of the robot's head) and the chest (the
  island's left edge) are. `dof-pair`: the caption now says f/2, focused on the robot about 6 m away (camera at
  (0, 2, 6), 6.33 m along its forward axis), 1.54 pixels at infinity by the page's formula, and that the crops enlarge
  twice, so the crop's blur is not read against the 0.7 pixels of f/2.8 at 10 m; `numbers` added. Captions and alts
  were shortened to keep the page within size L (6,486 prose words).
