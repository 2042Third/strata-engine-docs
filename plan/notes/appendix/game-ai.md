# Notes: appendix/game-ai

## New terms

- behaviour tree (aliases: tick (behaviour tree), `Sequence`, `Selector`): a tree of condition and action nodes that an update evaluates from the root downward, one pass per tick; home appendix/game-ai. The page says in one sentence that this tick is not the simulation's fixed step and links core/time.
- steering behaviour (aliases: seek, flee, arrive, wander, separation): a rule that turns an agent's situation into a desired velocity; home appendix/game-ai.
- A* search (aliases: A*, heuristic, admissible heuristic): a shortest-path search that orders its open set by cost so far plus an estimate of the cost left; home appendix/game-ai.
- navigation mesh (aliases: navmesh, nav mesh): convex polygons that cover the walkable floor, searched as a graph; home appendix/game-ai.
- utility AI: a decision model that scores every action and runs the best; home appendix/game-ai.
- goal-oriented action planning (alias: GOAP): a decision model that searches a chain of actions from the current facts to a goal; home appendix/game-ai.
- line of sight: a ray from an agent to a target that reaches the target before anything else; home appendix/game-ai.
- local avoidance: rules that let agents on their own routes step around each other without a new search; home appendix/game-ai.
- agent: a character that no person controls and that decides and acts by code; home appendix/game-ai.

## Requests

- Names for tools/data/names.txt: Dijkstra, Manhattan (the distance), Reynolds, Isla, Orkin (authors cited in the table and Further reading), GOAP (alias of the proposed term).
- Extra words for tools/data/extra-words.txt: polygon, polygons (school mathematics); heuristic, admissible (alias words of the proposed A* search term); navmesh (alias of navigation mesh).
- External hosts for Further reading (cited without links until added): redblobgames.com (Red Blob Games, A* pages), red3d.com (Reynolds's steering paper), gdcvault.com (Isla's and Orkin's talks and papers), github.com is already allowed (Recast and Detour: github.com/recastnavigation/recastnavigation).
- Figures: none; every picture is a Mermaid diagram.

## Not verified

- The table's "used by" cells (Halo 2 and behaviour trees, F.E.A.R. and goal-oriented planning, utility AI in life simulations, large engines' behaviour tree tools) and the Further reading entries rest on general knowledge; no source was fetched.
- Reynolds 1999 as the origin of the named steering behaviours, and Mononen's Recast and Detour as the navigation mesh libraries, are general knowledge.
- Whether a fox that walks out of its loaded cell finds ground under the spot: not tested; the page states only that the code tests no cell and that a missing ground ray makes the fox wait.
- The 27 of 30 count comes from the translations of the Wander foxes in the Wildlife scenes against the 64 m cell size (checked by script at the pin).

## Findings not applied

- critic-appendix-9: the sources for steering, behaviour trees, utility AI, GOAP and navigation meshes are named in Further reading without links and marked unfetched above; the table's rows cite them by author.
- critic-appendix-13 concerns appendix/not-in-strata, not this page.
- critic-appendix-14: applied with the OnCreate excerpt (lines 25-34); the Assumes row make/prefabs is not linked because the page does not teach prefab overrides, it states the fact in one sentence.
- critic-appendix-7, -8, -10: applied (reason and search evidence; state in fields, `script.get`, the regression script, `Log::Info`; one sentence on the behaviour tree's tick).

## Clerk

- Admitted terms: behaviour tree, steering behaviour, navigation mesh (aliases navmesh, nav mesh), utility AI, goal-oriented action planning (alias GOAP), line of sight, local avoidance, Agent (appendix) ("AI agent" is homed on automation/agents). Refused: A* search (the glossary cannot match a name holding an asterisk: the lint strips it; the planner may name it A-star search). Refused aliases: tick (behaviour tree), `Sequence`, `Selector` (code names and a qualified word), seek, flee, arrive, wander, separation (everyday words: as aliases they would be marked everywhere); heuristic and admissible heuristic are not A* (extra-words instead). Names: Dijkstra, Manhattan, Reynolds, Isla, Orkin. Extra words: polygon, polygons, heuristic, admissible. Hosts: redblobgames.com, red3d.com admitted; gdcvault.com was listed.
