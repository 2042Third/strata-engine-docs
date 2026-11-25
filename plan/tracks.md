# Tracks: the three reading orders

A track is one reader's way through the book. This file writes each track out as a numbered list of page ids in
reading order. The site's "next page" and "previous page" links of a track follow its list. A page's Tracks column in
`plan/outline-1.md` to `outline-4.md` names exactly the tracks whose list holds the page. The personas of the tracks
(G0 for track G, B0 for track B, E1 for track E) are described in `style.md`.

## Rules

**Track G, the game maker.** Track G reads the pages of `start` in order, `start/coming-from` included. That page is
optional: a reader who has used no other engine skips it. Then the track reads the pages of `make` in the order of
their rows: block A, block B and block C. After `make/first-script` it steps into `basics` for `basics/programming-1`,
`basics/programming-2`, `basics/programming-3` and `basics/debugging`, and comes back to `make/script-loop`. It has two
side steps: `basics/tools` before `make/first-script`, and `basics/math-vectors` before `make/gameplay-math`. Track G
ends with `make/project-platformer`.

**Track B, the beginner.** Track B reads the pages of `start` in order, without `start/coming-from`. Then it reads
block A of `make` from `make/editor-tour` to `make/lighting`. It steps into `basics` for `basics/computer` and
`basics/tools`, and comes back to `make/first-script`. It steps into `basics` again for `basics/programming-1`,
`basics/programming-2`, `basics/programming-3` and `basics/debugging`, and comes back to `make/script-loop`. It reads
the rest of block A, up to `make/project-coin-run`, whose reader owns the exported Coin Run. Then it reads the other
pages of `basics` in order, from `basics/git` to `basics/threads`. Track B ends there, and the reader chooses:
track G from `make/gameplay-math` (block B of `make`), or track E from `core/map`. At either page the reader has read
every page that the chosen track lists before it, except the optional `start/coming-from`. Track G is open to a track B
reader already after `make/project-coin-run`: that page's "what next" says so, for a reader who wants games first and
the rest of `basics` later. The primers after `basics/debugging` each end with an optional practice item on the
reader's Coin Run project.

**Track E, the engine builder.** Track E reads `start` in order, then `basics` in order, then `core`, `world` and
`gpu`. Then it reads the later parts in the order of `book.md`: `assets`, `draw`, `light`, `image`, `indirect`,
`physics`, `animation`, `audio`, `input`, `scripting`, `ui`, `worlds`, `editor`, `editor-ui`, `automation`,
`engineering` and `capstone`. Within a part it follows the order of the rows. It does not read `make`, `reference` or
`appendix`. Every primer of `basics` opens with a Test out box: a reader who answers its five questions skips the page.
The index page of `basics` names, for each primer, the first part whose pages need it, so that a reader knows which
Test out boxes can wait. A part after `gpu` can be read as soon as the Needs of its pages are read, so a reader may take
those parts in another order; the part's index page names its Needs, or the part's first page when the part has fewer
than eight pages and so no index page. The list gives the book's order, which always works.

**Side steps.** A side step is a page that a track offers but does not hold. Its entry is marked "(side step)" and
stands directly before the first page of the track whose Needs name it. In those Needs it is one alternative of a Need
(`` `basics/tools`\|`start/install` ``), never the only way to meet it. The track's "next page" link passes over a side
step, and the page after it offers the side step among its Needs. A side-step page's Tracks column does not name the
track. A side step must be readable where it is offered: each of its own Needs (or one alternative) comes earlier on the
track, or is an earlier side step (`basics/tools` needs `start/install`; `basics/math-vectors` needs
`basics/programming-2`).

**The check.** `plan/check_outline.py` reads this file. It fails when a listed id is no row of the outline, when a
track lists a page twice, or when a page's Tracks column and the lists disagree. It fails when a list is not the
sequence that the rules above give (each list is computed from the outline's rows and compared entry by entry), when a
track other than G has a side step, or when G's side steps are not exactly `basics/tools` and `basics/math-vectors`.
It fails when no alternative of a page's Need comes earlier on a track the page is on. It fails when a track takes the
pages of one part out of the order of their rows, when a side step does not stand directly before the first page that
names it, and when a side step's own Need comes later on the track. The entries of each list are numbered from 1,
without a gap.

## Track G: the game maker

**Part 0 — Start here (`start`)**:

1. `start/welcome`
2. `start/how-to-read`
3. `start/install`
4. `start/first-game`
5. `start/what-an-engine-is`
6. `start/coming-from` — optional

**Part 1 — Making games (`make`)**, block A, Your first game:

7. `make/editor-tour`
8. `make/project-files`
9. `make/scenes-entities`
10. `make/transforms-units`
11. `make/assets`
12. `make/materials`
13. `make/prefabs`
14. `make/lighting`
15. `basics/tools` (side step) — offered before `make/first-script`, whose Needs hold `basics/tools`\|`start/install`
16. `make/first-script`

Steps into **Part 2 — Foundations (`basics`)** after `make/first-script`:

17. `basics/programming-1`
18. `basics/programming-2`
19. `basics/programming-3`
20. `basics/debugging`

Back to `make`, block A, at `make/script-loop`:

21. `make/script-loop`
22. `make/scripting-scene`
23. `make/input`
24. `make/physics`
25. `make/sound`
26. `make/hud`
27. `make/play-test-debug`
28. `make/export`
29. `make/project-coin-run`

`make`, block B, The toolbox:

30. `basics/math-vectors` (side step) — offered before `make/gameplay-math`, whose Needs hold `make/transforms-units`\|`basics/math-vectors`
31. `make/gameplay-math`
32. `make/timers-events`
33. `make/script-fields`
34. `make/patterns`
35. `make/recipes`
36. `make/script-builds`
37. `make/characters-cameras`
38. `make/animation`
39. `make/menus`
40. `make/levels-saves`
41. `make/lamps`
42. `make/reflections`
43. `make/gi`
44. `make/look`
45. `make/quality`
46. `make/large-worlds`
47. `make/performance`
48. `make/automated-playtests`
49. `make/commands`
50. `make/with-an-agent`
51. `make/samples`

`make`, block C, Projects:

52. `make/designing-a-game`
53. `make/project-tetris`
54. `make/project-platformer`

Track G ends here.

## Track B: the beginner

**Part 0 — Start here (`start`)**, without `start/coming-from`:

1. `start/welcome`
2. `start/how-to-read`
3. `start/install`
4. `start/first-game`
5. `start/what-an-engine-is`

**Part 1 — Making games (`make`)**, block A, Your first game:

6. `make/editor-tour`
7. `make/project-files`
8. `make/scenes-entities`
9. `make/transforms-units`
10. `make/assets`
11. `make/materials`
12. `make/prefabs`
13. `make/lighting`

Steps into **Part 2 — Foundations (`basics`)** after `make/lighting`:

14. `basics/computer`
15. `basics/tools`

Back to `make`, block A, at `make/first-script`:

16. `make/first-script`

Steps into `basics` again after `make/first-script`:

17. `basics/programming-1`
18. `basics/programming-2`
19. `basics/programming-3`
20. `basics/debugging`

Back to `make`, block A, at `make/script-loop`, up to the exported Coin Run:

21. `make/script-loop`
22. `make/scripting-scene`
23. `make/input`
24. `make/physics`
25. `make/sound`
26. `make/hud`
27. `make/play-test-debug`
28. `make/export`
29. `make/project-coin-run`

Steps into `basics` for its other pages, in order:

30. `basics/git`
31. `basics/numbers`
32. `basics/data-structures`
33. `basics/trees-graphs`
34. `basics/cpp-memory`
35. `basics/cpp-classes`
36. `basics/cpp-generic`
37. `basics/cpp-modern`
38. `basics/build`
39. `basics/bytes`
40. `basics/data-formats`
41. `basics/math-vectors`
42. `basics/math-matrices`
43. `basics/math-bases`
44. `basics/math-projection`
45. `basics/math-rotations`
46. `basics/math-geometry`
47. `basics/math-change`
48. `basics/math-interpolation`
49. `basics/color`
50. `basics/signals`
51. `basics/math-probability`
52. `basics/math-sphere`
53. `basics/threads`

Track B ends here. The reader continues on track G from `make/gameplay-math`, or on track E from `core/map`.

## Track E: the engine builder

**Part 0 — Start here (`start`)**:

1. `start/welcome`
2. `start/how-to-read`
3. `start/install`
4. `start/first-game`
5. `start/what-an-engine-is`
6. `start/coming-from` — optional

**Part 2 — Foundations (`basics`)**:

7. `basics/computer`
8. `basics/tools`
9. `basics/programming-1`
10. `basics/programming-2`
11. `basics/programming-3`
12. `basics/debugging`
13. `basics/git`
14. `basics/numbers`
15. `basics/data-structures`
16. `basics/trees-graphs`
17. `basics/cpp-memory`
18. `basics/cpp-classes`
19. `basics/cpp-generic`
20. `basics/cpp-modern`
21. `basics/build`
22. `basics/bytes`
23. `basics/data-formats`
24. `basics/math-vectors`
25. `basics/math-matrices`
26. `basics/math-bases`
27. `basics/math-projection`
28. `basics/math-rotations`
29. `basics/math-geometry`
30. `basics/math-change`
31. `basics/math-interpolation`
32. `basics/color`
33. `basics/signals`
34. `basics/math-probability`
35. `basics/math-sphere`
36. `basics/threads`

**Part 3 — Engine architecture (`core`)**:

37. `core/map`
38. `core/first-change`
39. `core/conventions`
40. `core/reading-code`
41. `core/first-frame`
42. `core/frame-loop`
43. `core/time`
44. `core/windows-events`
45. `core/engine-modules`
46. `core/layers-registries`
47. `core/jobs`
48. `core/platform`
49. `core/files`
50. `core/profiling`
51. `core/debugging`
52. `core/math`

**Part 4 — Scenes and the ECS (`world`)**:

53. `world/what-a-world-is`
54. `world/ecs`
55. `world/scene-graph`
56. `world/systems`
57. `world/interpolation`
58. `world/reflection`
59. `world/serialization`
60. `world/prefabs`
61. `world/sub-scenes`
62. `world/projects-settings`
63. `world/tutorial-component`

**Part 5 — The GPU and the renderer's core (`gpu`)**:

64. `gpu/how-a-gpu-frame-works`
65. `gpu/vulkan-nvrhi`
66. `gpu/shaders`
67. `gpu/compute`
68. `gpu/coordinates`
69. `gpu/first-triangle`
70. `gpu/debugging`
71. `gpu/resources-lifetimes`
72. `gpu/upload-queue`
73. `gpu/binding`
74. `gpu/geometry-pool`
75. `gpu/frame-tour`
76. `gpu/readback-timing`
77. `gpu/debug-drawing`
78. `gpu/text`

**Part 6 — Assets (`assets`)**:

79. `assets/what-is-an-asset`
80. `assets/handles-meta`
81. `assets/importing`
82. `assets/textures`
83. `assets/texture-cooking`
84. `assets/models-gltf`
85. `assets/loading`
86. `assets/residency`
87. `assets/references`
88. `assets/uploads`
89. `assets/packs-export`
90. `assets/robustness`
91. `assets/extending`

**Part 7 — Drawing a scene (`draw`)**:

92. `draw/entities-to-draws`
93. `draw/render-scene`
94. `draw/bounds-culling`
95. `draw/asset-requests`
96. `draw/batching`
97. `draw/lod`
98. `draw/mirrors-camera-relative`
99. `draw/render-scene-gpu`
100. `draw/gpu-driven`
101. `draw/occlusion`
102. `draw/mip-streaming`
103. `draw/skinned`
104. `draw/motion-vectors`

**Part 8 — Light and materials (`light`)**:

105. `light/units-exposure`
106. `light/materials`
107. `light/reflectance`
108. `light/material-data`
109. `light/brdf`
110. `light/energy`
111. `light/measuring-light`
112. `light/lights`
113. `light/many-lights`
114. `light/area-lights`
115. `light/shadow-basics`
116. `light/sun-shadows-1`
117. `light/sun-shadows-2`
118. `light/local-shadows`
119. `light/sky`
120. `light/atmosphere`
121. `light/fog`
122. `light/clearcoat-transmission`

**Part 9 — The image (`image`)**:

123. `image/why-post`
124. `image/exposure`
125. `image/pre-exposure`
126. `image/tone-mapping`
127. `image/grading`
128. `image/encoding`
129. `image/lens-effects`
130. `image/spatial-aa`
131. `image/taa`
132. `image/motion-blur`
133. `image/depth-of-field`
134. `image/quality-settings`
135. `image/tutorial-post-effect`

**Part 10 — Indirect light (`indirect`)**:

136. `indirect/problem`
137. `indirect/ibl`
138. `indirect/seam`
139. `indirect/ao`
140. `indirect/probes`
141. `indirect/ssr`
142. `indirect/gi-voxels`
143. `indirect/gi-cascades`
144. `indirect/gi-limits`

**Part 11 — Physics (`physics`)**:

145. `physics/why`
146. `physics/bodies-colliders`
147. `physics/collision-detection`
148. `physics/dynamics`
149. `physics/building-bodies`
150. `physics/world-step`
151. `physics/collision-layers`
152. `physics/contacts-triggers`
153. `physics/queries`
154. `physics/character-controllers`
155. `physics/scale-streaming`
156. `physics/tuning`

**Part 12 — Animation (`animation`)**:

157. `animation/problem`
158. `animation/skeletons`
159. `animation/clips`
160. `animation/skinning`
161. `animation/importing`
162. `animation/state-machines`
163. `animation/blending`
164. `animation/time-events`
165. `animation/root-motion`
166. `animation/system`
167. `animation/culling`
168. `animation/editor`
169. `animation/limits`

**Part 13 — Audio (`audio`)**:

170. `audio/sound-in-a-computer`
171. `audio/engine`
172. `audio/clips-voices-sources`
173. `audio/spatial`
174. `audio/scene-system`
175. `audio/testing`

**Part 14 — Input (`input`)**:

176. `input/how-input-works`
177. `input/devices-state`
178. `input/mouse-cursor`
179. `input/gamepads`
180. `input/actions`
181. `input/rebinding`
182. `input/simulated`

**Part 15 — Scripting (`scripting`)**:

183. `scripting/why-scripts`
184. `scripting/shared-libraries`
185. `scripting/abi-sdk`
186. `scripting/loading`
187. `scripting/crash-containment`
188. `scripting/symbolization`
189. `scripting/script-system`
190. `scripting/hot-reload`
191. `scripting/host-api`
192. `scripting/tutorial-host-function`

**Part 16 — Game UI (`ui`)**:

193. `ui/what-game-ui-does`
194. `ui/layout`
195. `ui/contract`
196. `ui/input`
197. `ui/text`
198. `ui/drawing`

**Part 17 — Large worlds and shipping (`worlds`)**:

199. `worlds/why-streaming`
200. `worlds/grids`
201. `worlds/streamer`
202. `worlds/physics-scripts`
203. `worlds/export`
204. `worlds/game-identity`
205. `worlds/runtime`

**Part 18 — The editor's core (`editor`)**:

206. `editor/program`
207. `editor/commands`
208. `editor/deferred-commands`
209. `editor/undo`
210. `editor/saving`
211. `editor/recovery`
212. `editor/projects`
213. `editor/trash-references`
214. `editor/prefab-instances`
215. `editor/play-mode`
216. `editor/worlds`
217. `editor/script-builds`
218. `editor/stepping`
219. `editor/command-scripts`
220. `editor/journal`
221. `editor/placement`
222. `editor/thumbnails`
223. `editor/camera-viewport`
224. `editor/tutorial-command`

**Part 19 — The editor's interface (`editor-ui`)**:

225. `editor-ui/immediate-mode`
226. `editor-ui/imgui`
227. `editor-ui/imgui-backends`
228. `editor-ui/ui-scale`
229. `editor-ui/design-system`
230. `editor-ui/widget-kit`
231. `editor-ui/shell`
232. `editor-ui/lists`
233. `editor-ui/inspectors`
234. `editor-ui/scene-view`
235. `editor-ui/game-view`
236. `editor-ui/status`
237. `editor-ui/launcher-dialogs`
238. `editor-ui/settings-windows`
239. `editor-ui/instrument-panels`
240. `editor-ui/ui-testing`
241. `editor-ui/tutorial-panel`

**Part 20 — Automation and AI agents (`automation`)**:

242. `automation/agents`
243. `automation/json-rpc`
244. `automation/rpc-server`
245. `automation/security`
246. `automation/sessions`
247. `automation/mcp`

**Part 21 — Building, testing and releasing the engine (`engineering`)**:

248. `engineering/building`
249. `engineering/cmake`
250. `engineering/flags-portability`
251. `engineering/third-party`
252. `engineering/generated-code`
253. `engineering/testing`
254. `engineering/test-program`
255. `engineering/test-kinds`
256. `engineering/feature-test`
257. `engineering/perf-lab`
258. `engineering/look-dev`
259. `engineering/ci`
260. `engineering/releasing`
261. `engineering/contributing`

**Part 22 — Capstone: one feature through every layer (`capstone`)**:

262. `capstone/plan`
263. `capstone/build`
264. `capstone/land`

Track E ends here.
