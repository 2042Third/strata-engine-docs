# Brief: `appendix/networking`

| Field | Value |
| --- | --- |
| Title | Networking for games, in general |
| Kind | C |
| Size | L |
| Tracks | - |
| Needs | `automation/json-rpc`, `core/time` |
| From | curricula; Strata has no gameplay networking: its network code serves editor automation only, in a Tooling layer games never link |
| Unit | `plan/allocation/appendix.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `appendix/networking` — Networking for games, in general

**Covers.** The page runs on one small example: two players on two machines push one ball across a field, on a
simulation of 60 steps a second. The problem as the reader meets it: the second player's push arrives tens to
hundreds of milliseconds late, some packets arrive twice, out of order or never, and both screens must still show one
game. The naive answer is to send every object's position over TCP every frame; it breaks on four things in turn: input
feels late, one lost packet holds back every later one (head-of-line blocking), the bytes grow with the objects and the
frame rate, and a player's machine can send any position it likes. The idea: one simulation has the authority, the
others predict and correct, and time, more than bytes, is the hard part.

Transport first: datagrams (UDP) against streams (TCP), a reliability layer of sequence numbers and acknowledgements
for the few messages that need it, and why games build their own; the stream, the framing and the bounds on a peer
come from `automation/json-rpc` and are not taught again. The approaches, each introduced by the flaw of the one
before: deterministic lockstep (send only inputs; every machine must compute the same steps bit for bit; strategy
games), rollback (predict the remote inputs, and rewind and replay the steps when the real ones arrive; fighting
games), client-server with snapshots and entity interpolation (remote objects drawn one or two snapshots in the past),
client-side prediction with server reconciliation (the local player runs ahead and is corrected), and lag compensation
(the server rewinds its hit tests to what the shooter saw). A table compares them: bandwidth, the latency they hide,
resistance to cheating, how hard they are, and who uses them, with sources (Gaffer on Games [S17] and Gambetta [S24]
of `research/curricula.md`). Then bandwidth: quantization of floats, deltas against the last snapshot the other side
acknowledged, and interest management. Then topologies: dedicated server, listen server, peer to peer, relays and NAT
traversal. Security: never trust the client, and bound everything a peer controls (the editor's server is the book's
worked case).

Strata's choice: no gameplay networking. Its sockets, framing and JSON-RPC are the Tooling layer `Network`, which
serves the editor's automation only and which games never link; the SDK and the runtime hold no socket. What a game or
an engine change would build on is already there: game time in fixed steps (the tick), parallel physics that gives the
same result with any number of threads (bit-identical results across machines are box3d's claim for its own scenario,
which Strata checks with a golden hash, not a promise of the engine), inputs as data (input actions; simulated input
queued per fixed step), drawn transforms between the last two fixed poses (the same idea as entity interpolation, one
step behind), and scene documents. What it would have to add: a transport, snapshots and their deltas, a way to rewind
state for rollback or lag compensation, and devices assigned to players. Common mistakes: TCP for fast-changing state;
sending every frame instead of every tick; trusting results that a client computed; counting frames instead of ticks;
assuming floating-point results agree across compilers and processors. The exercises: a sketch that draws the ball
one snapshot interval behind, with one snapshot lost, and prints the error; and a design exercise that names the model
for three games and what Strata would have to add for each. At the end the reader can name the model a given game
needs, say what it costs, and say what Strata would have to gain to run it.

**Leaves out.**

- Sockets, ports, non-blocking reads, framing and JSON-RPC as Strata implements them → `automation/json-rpc`
- The editor's RPC server: its network thread, limits and backpressure → `automation/rpc-server`
- The handshake, the session token and HMAC → `automation/security`
- The fixed step, the accumulator and time dilation → `core/time`
- Drawing between two fixed steps → `world/interpolation`
- Floating-point determinism across compilers (FMA contraction) → `engineering/flags-portability`
- Devices per player for local multiplayer (an absence) → `input/gamepads`

**Fit.** `fits`: about 5,550 words against L (5,000). Five approaches with their table take 1,700 words, Strata's
choice with what a game would build on 750, the problem and the naive answer 600, bandwidth and topologies 600,
transport 500, mistakes 300, security 250, the two exercises 250, and the fixed parts 600; three timelines carry the
approaches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:77` | not-done | home | Gameplay networking: network code exists for editor automation only, in the Tooling layer `Network`, which games never link; how engines do it is the page itself. Evidence: `StrataTests/Architecture/Layers.json:99-102` (the layer `Network`, `"Tooling": true`, `Strata/Network/**` and the OS socket files); `git grep -nE "Socket\|Network" 822a7a46 -- StrataScriptCore StrataRuntime` finds nothing |
| `automation:47` | feature | use | The Network layer's place: Tooling, may include only Core, links `ws2_32` on Windows |
| `worlds-runtime:140` | feature | use | Games link no tooling: the runtime links no editor, asset pipeline or network layer |
| `automation:284` | concept | use | Processes, sockets and ports; TCP on loopback, the starting point for datagrams against streams |
| `automation:298` | concept | use | A stream has no message boundaries: framing, against the packets of a game protocol |
| `automation:310` | concept | link | Remote procedure calls and JSON-RPC 2.0, the opposite of state replication |
| `automation:350` | concept | use | Limits and backpressure: what one slow or hostile peer may cost |
| `automation:363` | concept | use | The editor's threat model, as the worked case of "never trust the peer"; a game adds cheating players |
| `automation:615` | rule | use | The network thread never touches engine state: a game's network thread would hand messages to the main thread the same way |
| `automation:622` | rule | use | Bound everything a peer controls |
| `automation:481` | code | link | The network thread's iteration, read on `automation/rpc-server` |
| `foundation:228` | concept | use | The fixed step and its accumulator, as the tick a networked simulation counts |
| `physics:279` | concept | use | Determinism: the same results with any number of threads; what box3d's cross-platform claim covers, which lockstep would rest on |
| `physics:149` | feature | link | The determinism tests of physics |
| `build-test:301` | concept | use | Instruction sets and floating-point determinism across machines |
| `scene-ecs:357` | concept | use | Drawing between two fixed poses, the same idea as entity interpolation |
| `audio-input:357` | concept | use | Simulated input queued per fixed step: inputs as data, the basis of lockstep and replays |
| `scripting:343` | concept | use | Seeded random numbers in game code, which lockstep needs on every machine |
| `new:60` | not-done | link | Devices assigned to players for local multiplayer, stated on `input/gamepads` and `make/input` |
| `new:84` | figure | home | A timeline of deterministic lockstep beside rollback: inputs sent, steps waited for, steps rewound and replayed. General knowledge. |
| `new:85` | figure | home | A timeline of client-server with client-side prediction and server reconciliation, the corrections drawn as jumps. General knowledge. |
| `new:86` | figure | home | Snapshot interpolation: the remote ball drawn between the two newest snapshots, one interval behind. General knowledge. |
| `new:87` | figure | home | Strata's layers as a diagram, `Network` among the Tooling layers beside the stack, games linking none of them. Evidence: `StrataTests/Architecture/Layers.json:99-102` |
| `new:88` | term | home | UDP and datagram. General knowledge. |
| `new:89` | term | home | Latency and round-trip time. General knowledge. |
| `new:90` | term | home | Packet loss and jitter. General knowledge. |
| `new:91` | term | home | Tick and tick rate. General knowledge. |
| `new:92` | term | home | Authority; authoritative server. General knowledge. |
| `new:93` | term | home | Deterministic lockstep. General knowledge. |
| `new:94` | term | home | Rollback (rollback netcode). General knowledge. |
| `new:95` | term | home | Snapshot (networking): the state a server sends each tick, a third meaning beside the two of `book.md`'s rule 6. General knowledge. |
| `new:96` | term | home | Entity interpolation. General knowledge. |
| `new:97` | term | home | Client-side prediction. General knowledge. |
| `new:98` | term | home | Server reconciliation. General knowledge. |
| `new:99` | term | home | Lag compensation. General knowledge. |
| `new:100` | term | home | Delta compression and quantization. General knowledge. |
| `new:101` | term | home | Interest management (relevancy). General knowledge. |
| `new:102` | term | home | NAT traversal and relay server. General knowledge. |
| `new:189` | hands-on | home | The page's exercises (D27). Done, a sketch with its output: a C++ sketch of about 40 lines in which a server steps the ball at 60 ticks a second and sends its position every third tick, one snapshot is lost, and the client draws the ball one snapshot interval behind by interpolating between the two newest snapshots; the output lists, frame by frame, the drawn position beside the true one, and the reader explains the error after the lost snapshot. Design: for a strategy game, a fighting game and a shooter, the reader names the model each needs (lockstep, rollback, client-server with prediction and lag compensation), what it costs, and what Strata would have to add for it (a transport, snapshots and their deltas, a way to rewind state, devices assigned to players) (about 250 words). General knowledge. |
| `automation:716-717` | term | link | Socket and TCP, defined on `automation/json-rpc` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Sockets, ports, TCP, non-blocking reads, framing and JSON-RPC | `automation/json-rpc` | must |
| The fixed step, the accumulator and game time counted in fixed steps | `core/time` | must |
| Vectors: positions and velocities, adding and scaling them | `basics/math-vectors` | must |
| Binary, integers, floating point and precision (quantizing a float into fewer bits) | `basics/numbers` | must |
| Threads and the main-thread rule | `basics/threads` | helps |
| Deterministic parallel work: ordered records, fixed chunks | `core/jobs` | helps |
| Drawing between fixed steps | `world/interpolation` | helps |
| Determinism of the physics step | `physics/world-step` | helps |
| FMA contraction and floating-point determinism across compilers | `engineering/flags-portability` | helps |
| Scene documents and their serialization | `world/serialization` | helps |
| Input actions | `input/actions` | helps |
| Hashes, MACs and the threat model of the editor's server | `automation/security` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-appendix-7 | should | shape | `appendix/networking`, `appendix/game-ai` | The concept shape asks for Strata's choice and its reason. Neither Covers gives a reason, and the pin has none: the engine's documents neither plan nor refuse gameplay networking or game AI. Without that sentence a writer may invent a reason or read a plan into the silence. | Each page states it: the engine's documents name no plan and no decision; network code serves automation only, and AI is left to scripts; with the search as evidence (book.md rule 4). About 50 words on each page. | `style.md:486-487`; `allocation/appendix.md:227-234`, `:333`; pin: `git grep -n -i -w -E` for the words multiplayer, netcode, lockstep, replication and matchmaking over `Docs`, `AGENTS.md` and `README.md` finds only local multiplayer (`Docs/Releases/0.6.0.md:415, 490`, `Docs/Releases/0.7.0.md:412`, `Docs/Roadmap.md:988`) and a test's "lockstep" (`Docs/Plans/Wave8/specs/physics-timing.md:836`); `git grep -n -i -E` for nav mesh, navigation mesh, pathfind, behaviour tree, steering and game AI there finds only the input axis "steering" of `Docs/Manual/Settings.md:71` |
| critic-appendix-9 | should | missing-item | `appendix/game-ai`, `appendix/networking` (Further reading) | Each approach's "who uses it" needs a source. The game-ai page names only Red Blob Games [S28] and *Game Programming Patterns* [S7], which do not cover behaviour trees, utility AI, goal-oriented planning, steering behaviours or navigation meshes. The networking page names Gaffer on Games [S17] and Gambetta [S24], which do not cover rollback. The research holds no other source for them. | The two Covers name the sources the writer must find for these rows (for example Reynolds 1999 on steering, Isla 2005 on behaviour trees in Halo 2, Orkin 2006 on goal-oriented planning in F.E.A.R., Mononen's Recast and Detour, GGPO and the GDC talks on rollback), marked as not yet fetched. `appendix/further-reading` takes them in its second part. About 100 words of further reading lines. | `style.md:484-485`; `allocation/appendix.md:221-222`, `:326-327`, `:572-576`; `research/curricula.md:613-640` |
| critic-appendix-10 | should | other | `new:89`, `new:90`, `new:91` on `appendix/networking`; `new:109` on `appendix/game-ai` | Three term homes of the networking page share a word with another home that has another meaning. "Jitter" is homed on `image/taa` as the sub-pixel offset of the projection. "Latency" is homed on `audio/sound-in-a-computer` with the mixing period. "Tick" is also a word of the behaviour tree's entry on `appendix/game-ai`, where a tick is one evaluation from the root. `new:95` says that "snapshot" is a third meaning; these three rows do not. | Make the entries qualified, as `new:95` is: "jitter (network)", "latency (network)" with one sentence on audio latency, "tick (simulation)" and "tick (behaviour tree)". Each page says in one sentence which meaning it uses and links the other. About 40 words. | `allocation/appendix.md:284-286`, `:290`, `:377`; `allocation/image.md:733`, `:736`; `allocation/audio-input.md:48` |
| critic-appendix-13 | could | duplicate | `appendix/not-in-strata` (the Gameplay group) | The page gives one technique paragraph per area. For the Gameplay area, the techniques of networking and game AI are the whole subject of `appendix/networking` and `appendix/game-ai`, from the same angle. | The Gameplay group gives the technique of cutscene timelines and links the two appendix pages in one sentence each. This saves about 120 words. | `allocation/appendix.md:15-25`, `:50-52`; `book.md:574-580`; `allocation/appendix.md:205-239`, `:320-350` |
| critic-appendix-15 | could | missing-item | `appendix/networking` | The page says what Strata would have to add, but not where a game's own networking code would run today, or which rules bind it. Game code is a script module, a CMake project of the game's own. Its callbacks must never block or do synchronous network I/O, and threads it starts must never call the engine. | One paragraph in Strata's choice: such code would live in the game's script module, poll without blocking in its callbacks, and keep its own threads away from the engine; the book has not built one (read, not run). About 100 words. | `allocation/appendix.md:227-234`; pin `.claude/skills/strata-scripting/SKILL.md:650`, `:653`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:25-26`; `Samples/OpenWorld/Scripts/CMakeLists.txt:7-12` |
