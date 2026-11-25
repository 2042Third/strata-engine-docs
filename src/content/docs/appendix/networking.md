---
id: appendix/networking
title: "Networking for games, in general"
description: "How online games keep two machines in one game: datagrams, lockstep, rollback, snapshots, prediction, lag compensation and what Strata lacks."
kind: concept
size: L
tracks: []
needs: [automation/json-rpc, core/time]
time: 60
learn:
  - id: transport
    text: explain why games send datagrams and add reliability only to the messages that need it
  - id: models
    text: choose the model a game needs, name what it costs and name what it hides
  - id: bandwidth
    text: compute the bytes a snapshot stream needs and how quantization and deltas cut them
  - id: interpolation
    text: predict where a client draws the ball when a snapshot is lost
  - id: strata
    text: name what Strata would have to add to run an online game
status: final
---

Two players stand on two machines, each in front of its own screen. A ball lies in the middle of a field. Player A pushes it to the right at tick 100, and player B pushes it back at the same moment. Both screens must show one game: the ball must rest in the same place for both of them.

The machines are far apart, so nothing arrives at once. The time a message needs to travel from one machine to the other is the **latency**. A message that goes there and a reply that comes back take the **round-trip time**, and on the internet that is commonly 30 to 150 ms. At 60 steps a second, a step lasts 16.7 ms, so a round trip of 100 ms is six steps. B's push reaches A six steps after B pressed the key.

The network also damages what it carries. **Packet loss** is the share of messages that never arrive; a wireless link may lose one in fifty. A message may also arrive twice, or after a message that was sent later.

The third trouble is **jitter** (in networking), the change of the latency from one message to the next. A message that took 40 ms is followed by one that takes 90 ms. This page uses jitter in that sense only; the sub-pixel offset that temporal anti-aliasing uses is another thing.

Everything below answers one question. How do two machines, which see each other's actions late, unevenly and incompletely, show one game that feels instant to each player? The answer is a set of models, and each one trades something that another one keeps.

## The naive answer sends every position over a stream

The first idea is the one you already know from the page on [JSON-RPC](../automation/json-rpc.md): open a connection of the transmission control protocol (TCP), and send every object's position in every frame. The other machine reads the positions and draws them. TCP delivers every :term[byte]{id=byte}, in order, so the data looks safe.

The idea breaks on four points, one after the other.

First, input feels late. Player B presses a key, and the ball moves only after the message travelled to the other machine and the answer came back. With a round trip of 100 ms, every action waits six steps before the player sees it.

Second, one lost message stops all the later ones. TCP hands data to the program in order, so when message 2 is lost, messages 3, 4 and 5 wait in the :term[operating system]{id=operating-system} until message 2 has been sent again. That wait is **head-of-line blocking**. Sending again takes at least one round trip, so a game that sends a position every 16.7 ms freezes for 100 ms or more. The late position of message 2 is useless anyway, because message 3 already holds a newer one.

Third, the bytes grow with the number of objects and with the :term[frame rate]{id=frame-rate}. One hundred objects with an identifier, a position and a velocity take 28 bytes each. At 60 frames a second, that is 100 × 28 × 60 = 168,000 bytes a second for each player, and the frame rate of a fast machine raises it further.

Fourth, the machine that sends the position can send any position it likes. A player who edits the program can place the ball in the goal, and the other machine believes it.

The simulation counts time in **ticks**. A tick is one :term[fixed step]{id=fixed-step} of the game, and the **tick rate** is the number of ticks a second, 60 in this page's example. A message that names the tick it belongs to has a meaning that does not depend on the frame rate or on when it arrived. The page on [time](../core/time.md) explains the fixed step; a networked game counts these steps and never frames.

## One machine decides and the others predict

Every model on this page rests on one rule: for each piece of the game state, exactly one simulation has the **authority**, the right to decide what is true. The other machines hold copies. When copy and authority disagree, the authority wins.

Authority removes the fourth failure of the naive answer, because a machine that has no authority cannot change what is true. It also gives a cost. A player who is not the authority must wait for the answer before seeing the truth, and the answer is late by the round trip. Every model below is a way to hide that wait, and each one hides it differently.

```mermaid caption="The authority simulates and sends state to the copies; each copy shows a guess that the next message corrects." alt="Three boxes in a row: the authority runs the true simulation, a network link with delay carries messages, and the copy shows its guess and corrects it."
flowchart LR
    A["Authority: true simulation"] -->|"state, late by the latency"| N["Network: delay, loss, jitter"]
    N --> C["Copy: shows a guess"]
    C -->|"inputs, late by the latency"| N
    N --> A
```

The diagram shows the loop. Inputs travel to the authority and state travels back, so everything a player sees has made a round trip. The models differ in what the copy shows while it waits, and in how much it must repair when the answer comes.

## Datagrams trade order for speed

The transport decides what the network does to your messages before any model runs. A TCP stream, as the page on [JSON-RPC](../automation/json-rpc.md) teaches, delivers every byte once and in order. A stream also has no message boundaries, so the editor's protocol frames its messages with line ends.

The **user datagram protocol** (UDP) sends **datagrams** instead: separate messages that carry their own boundaries. The network may lose them, copy them or change their order, and UDP does not repair any of it. A datagram that arrives is whole, and one that does not arrive costs nothing to the others.

Datagrams fit a game because most of its messages go out of date. A position from 50 ms ago has no value once a newer one has arrived, so sending it again wastes :term[bandwidth]{id=bandwidth} and time. A game takes the newest datagram and ignores the lost ones.

A few messages must arrive: the order to start the match, a purchase, a chat line. Games add a small **reliability layer** on top of UDP for these messages, and it needs a few numbers per datagram. Each side numbers its datagrams, and each datagram also carries the number of the newest datagram it received from the other side and a :term[bit mask]{id=bit-mask} of the 32 before it. A sender that sees a reliable message missing from the acknowledgements sends it again in a later datagram, and a message that is not reliable is never sent again.

The reliability costs no stall, because later datagrams are never held back. TCP applies its order to everything, while the game applies it only to the few messages that need it, and a game can choose per message. A game also decides how long to wait before sending again, which TCP decides for you.

Two limits remain. A datagram that is larger than the path allows is split, and one lost piece loses the whole datagram, so games keep each one below about 1,200 bytes. Players at home also need help to reach each other, which a later section describes.

## Lockstep sends only the inputs

If both machines run the same :term[deterministic]{id=determinism} simulation from the same start, they need no positions at all. Each machine sends only its player's input for each tick, and each machine applies the same inputs in the same order. This is **deterministic lockstep**. A strategy game with 1,000 units sends a few bytes a tick, because the units themselves never cross the network.

A machine may run tick $n$ only when it holds the inputs of every player for tick $n$. Player A therefore waits for B's input, and with a round trip of 100 ms that is six ticks. Lockstep hides this with an input delay: a key pressed at tick 100 takes effect at tick 106, and the input travels during the wait. Strategy games accept this, because a unit that starts walking 100 ms after the click does not feel wrong.

The price is exactness. The two machines must compute the same result bit for bit, because one different bit grows into two different games, which players call a loss of :term[sync]{id=synchronization}. The code must run the steps in one fixed order, read random numbers from a generator that both seed with the same value, and avoid floating-point operations that differ between :term[compilers]{id=compiler} and processors. Lockstep also waits for the slowest player: one stalled machine stops all of them.

## Rollback guesses the inputs and repairs the guess

Waiting is wrong for a fighting game, where 100 ms is six frames of a character's kick. **Rollback** (also called rollback network code) removes the wait: the machine does not wait for the remote input, but guesses it, usually as the same as the last one, and runs the tick at once. The inputs of the local player take effect at once.

When the real input arrives, the machine compares it with the guess. If the guess was right, nothing happens. If it was wrong, the machine loads the saved state of the tick where the guess was made, and runs every tick since then again with the true input, all inside one frame.

```mermaid caption="Lockstep waits for the remote input; rollback guesses it, then rewinds and replays when the guess was wrong." alt="Two time diagrams between player A and player B. In lockstep, A waits until the input of B arrives. In rollback, A runs ahead on a guess, receives the input late, rewinds and replays four ticks."
sequenceDiagram
    participant A as PlayerA
    participant B as PlayerB
    Note over A,B: Lockstep
    B->>A: input of tick 100
    Note over A: waits, then runs tick 100
    Note over A,B: Rollback
    Note over A: guesses B and runs ticks 100 to 103
    B->>A: input of tick 100 arrives
    Note over A: rewinds to 100, replays 100 to 104
```

The cost is computing time. If the input arrives four ticks late, one frame must run five steps, the replayed four and the new one, within 16.7 ms. Each step may then take at most about 3.3 ms, and the game must be able to save and load its whole state in each tick. Rollback also needs the deterministic simulation of lockstep, so that the replay gives the same result on both machines.

## Snapshots show the other player in the past

Lockstep and rollback need determinism and an exact copy of the state on every machine. A game with many players and a large world drops that goal. One server runs the true simulation instead. Each tick, or every few ticks, the server sends the state, and this message is a **snapshot**, the state of the game at one tick. Other pages of the book use the word in two other senses.

If a client draws every snapshot when it arrives, the ball moves in jumps, because snapshots come 20 times a second and jitter moves them in time. The remedy is **entity interpolation**: the client keeps the last snapshots and draws each remote object between the two that surround a time slightly in the past.

Take a ball that moves at 4 m/s, with snapshots every 50 ms (every third tick). The client draws at the newest snapshot time minus 50 ms. At one moment it holds the snapshots at 0.20 m and 0.40 m, taken 50 ms apart, and draws the ball halfway between them, at 0.30 m. The motion is smooth, and every remote object shows its past, one snapshot interval behind the server. One interval of delay hides jitter that is shorter than one interval, and a lost snapshot needs a second interval.

```mermaid caption="The client draws between the two newest snapshots, so every remote object shows the past by one snapshot interval." alt="A server sends snapshots every 50 milliseconds. The client holds two of them and draws the ball halfway between them, 50 milliseconds behind the newest."
sequenceDiagram
    participant S as Server
    participant C as Client
    S->>C: snapshot at 0.20 m
    S->>C: snapshot at 0.40 m
    Note over C: draws 0.30 m, one interval behind
```

Strata's own drawing of fixed steps uses the same idea on one machine; the page on [interpolation](../world/interpolation.md) shows it, one fixed step behind instead of one snapshot interval. The exercise at the end of this page runs it with a lost snapshot.

## Prediction runs the local player ahead

Interpolation is fine for other players, but it is wrong for yours: your own character would answer a key press 100 ms late. **Client-side prediction** fixes this. The client applies your inputs to your own character at once, with the same movement code as the server, and sends the inputs to the server, each with a number.

The server runs the inputs and sends back the state with the number of the last input it applied. The client then compares the server's position with its own prediction. If the two agree, nothing happens. If they differ, because a crate that the client did not know about blocked the way, the client must correct itself. This correction is **server reconciliation**: the client takes the server's state as the truth and replays the inputs that the server has not yet applied.

Suppose a player moves 1/12 m a tick, which is 5 m/s. After six inputs, the client shows 0.50 m. The server acknowledges input 3 and says the position is 0.20 m, because a crate stopped it, while the client had 0.25 m. The client sets 0.20 m and replays inputs 4 to 6, which gives 0.20 + 3/12 = 0.45 m. The character jumps back by 0.05 m, and many games spread such a correction over several frames so that it looks like a slide.

```mermaid caption="The client runs its inputs at once; the server answers late, and the client replays the inputs that the server has not seen." alt="The client sends inputs 1 to 6 and shows its own result at once. The server acknowledges input 3 with a different position. The client resets to it and replays inputs 4 to 6."
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: inputs 1 to 3
    Note over C: shows 0.25 m at once
    C->>S: inputs 4 to 6
    S->>C: after input 3 the position is 0.20 m
    Note over C: resets to 0.20 m, replays 4 to 6, shows 0.45 m
```

## Lag compensation rewinds the server for a shot

Prediction fixes your own movement, but interpolation puts the others in the past. You aim at a target that is 100 ms old: 50 ms for the trip of the snapshot and 50 ms of interpolation delay. A target that runs at 6 m/s has moved 0.6 m since. You hit it on your screen, but the server sees the target 0.6 m away and calls it a miss.

**Lag compensation** lets the server rewind. It stores the recent positions of every target, and when a shot arrives, it moves the targets back to the time the shooter saw, which is 6 ticks earlier here, and tests the hit there. The server needs the shooter's latency and the shooter's interpolation delay, and it limits how far it may rewind.

The cost falls on the target. A player who ran behind a wall 100 ms ago can be hit after reaching cover, because the shooter's screen still showed the player in the open. Games choose a maximum rewind of about 200 ms and accept this, because the other choice is a shooter that misses shots that looked perfect.

## The five models side by side

Each model hides the delay in another place, and the table shows what that costs. The sources in the section on further reading describe each row.

| Model | Bandwidth | Hides the latency of | Cheating | Difficulty | Used by |
| --- | --- | --- | --- | --- | --- |
| Deterministic lockstep | Lowest: inputs only | Everything, by an input delay | Weak: every machine holds all of the state | Hard: bit-exact simulation | Strategy games such as Age of Empires and StarCraft |
| Rollback | Low: inputs only | Everything, by guessing | Weak: the same | Hardest: determinism, saved state, fast replay | Fighting games, with rollback libraries |
| Snapshots with interpolation | Medium to high: state | Nothing: others are shown late | Strong with a server | Medium | Quake 3, Source engine games |
| Prediction with reconciliation | Medium: state and inputs | Your own actions | Strong with a server | Hard: shared movement code, replay | QuakeWorld, Overwatch |
| Lag compensation | Adds only history on the server | Aiming at late targets | Strong, but it favours the shooter | Medium on top of the others | Source engine games, Overwatch |

The first two models need all players to compute the same thing, so every machine can see all the state and a cheater can use it. The last three keep the truth on a server and only copy what each player may know. That is the first big choice of a game: where the truth lives.

## Bandwidth shrinks with fewer bits, fewer objects and fewer changes

Three tools keep a snapshot stream small, and each one answers the flaw that the one before leaves.

**Quantization** stores a number in fewer bits. A position inside a field of 100 m fits in 16 bits, which gives 65,536 steps of about 1.5 mm, instead of the 32 bits of a float. A player cannot see 1.5 mm, so nothing is lost that matters. The page on [numbers](../basics/numbers.md) explains how floats store values; here you only choose the range and the step.

**Delta compression** sends only what changed since a snapshot that the other side is known to have. The sender keeps the snapshots it sent, and the receiver acknowledges the newest one it has. The next snapshot lists only the objects that differ from that one. If an acknowledgement is lost, the sender still deltas against the older snapshot, so the receiver never lacks the base.

**Interest management** (also called relevancy) sends a client only the objects it can matter to, such as those inside a radius or in the same room. A server with 10,000 objects may send each player 200.

:::example[What 100 balls cost in each design]
Start from the naive answer: 100 objects × 28 bytes × 60 frames = 168,000 bytes a second. Send 20 snapshots a second instead of 60 frames, every third tick, and the count falls to 56,000. :term[Quantization]{id=quantization} without the velocity, which the client computes from two snapshots, keeps 3 × 2 bytes of position and 1 of identifier: 100 × 7 × 20 = 14,000 bytes a second. If only 10 balls move between snapshots, the delta lists 10 objects: 10 × 7 × 20 = 1,400 bytes a second. Each datagram also costs about 28 bytes of :term[headers]{id=header}, which is another 560 bytes a second at 20 datagrams, so 1,960 in all, or 1.2 % of the first number.
:::

## The layout of the network decides who runs the authority

The layout answers where the authority runs. A dedicated server is a machine that runs only the simulation, usually in a data centre; it is fair and hard to cheat on, and someone pays for it. A listen server is one player's machine, which is both a player and the authority; it costs nothing, but that player has no latency and an advantage, and the match ends when the player leaves. In peer to peer, every machine talks to every other one; lockstep and rollback use it, and with n players each machine keeps n - 1 connections.

Players at home sit behind a gateway that does network address translation (NAT). It rewrites addresses so that many devices share one public address, and it drops datagrams that nobody inside asked for.

Two players behind two gateways cannot start a connection to each other. **NAT traversal** is the set of tricks that fixes this. A public server tells each side the public address of the other, and both send a datagram at the same moment. Each gateway then sees the traffic as an answer and lets it pass.

The trick fails on some gateways. A **relay server** is the last resort: both players send their datagrams to a public server, which forwards them. This always works, costs bandwidth for the owner and adds a trip of latency.

## Never trust the peer

A server that accepts what a client says is as safe as the least honest client. Send the client's inputs ("I press forward"), never its results ("I am at x = 40"), and let the server check each input: movement speed, fire rate, ammunition. Hide from a client the state that it must not see, for example another team's position, because anything that reaches the machine can be read by a cheating program.

A peer can also overload you without cheating at all. Bound everything a peer controls: the size of a message, the nesting of its data, the number of connections, the length of every name and the queue of its work. The editor's server is a worked case, and the page on [the editor's server](../automation/rpc-server.md) describes it. Its limits are 256 levels of nesting in :term[JSON]{id=json}, 64 characters in a client name and 256 in an identifier. A full table of waiting connections removes the oldest one that had a chance to send.

A game server needs the same limits, plus a check of every action against the rules.

The threat model of the editor, a local program that must prove it may drive the editor, is on the page about [security](../automation/security.md). A game server adds the case of a player who has a valid ticket and wants to win.

## Strata has no gameplay networking

Strata has no networking for games, and the engine's documents name no plan and no decision about it. A search of its `Docs` folder, `AGENTS.md` and the overview file for the words `multiplayer`, `netcode`, `lockstep`, `replication` and `matchmaking` finds only local play with several players, and one word in a physics test plan. What exists is the layer `Network` in `Strata/src/Strata/Network/` and the two socket files of the platform folders: sockets, JSON-RPC and editor sessions. The :term[layer table]{id=layer-table} in `StrataTests/Architecture/Layers.json` marks it as a :term[tooling layer]{id=tooling-layer} that may include only `Core`. The scripts' C interface, their library and the :term[runtime]{id=runtime} contain no socket, and a game never links a tooling layer.

```mermaid caption="The Network layer is one of the tooling layers beside the stack: the editor and the tools use it, and a game links none of them." alt="A box for the game stack holds Core, Scene, Physics, Renderer and Scripting. Beside it a box for tooling layers holds Network, ImGui and the editor. An arrow shows that games link only the stack."
flowchart LR
    subgraph Game["Linked by a game"]
        Core --> Scene --> Physics
        Scene --> Renderer
        Scene --> Scripting
    end
    subgraph Tooling["Tooling, never linked by a game"]
        Network
        ImGui
        Editor
    end
    Editor --> Network
```

The reason cannot be read from the engine, and this page does not invent one. The pieces that a networked game would use are already there:

- **Ticks.** Game time runs in fixed steps, counted by `Scene::GetFixedStepCount`, and the project can fix the rate for every scene.
- **Determinism, in part.** Strata compiles its physics library, box3d, without contraction of floating-point operations, and the test `Physics.Box3D` checks one scenario against box3d's :term[golden hash]{id=golden-hash} with any number of threads. The engine's own code may contract them, unless its build enables the option `STRATA_CROSS_PLATFORM_DETERMINISTIC`, which is off by default. No test shows that a whole game gives the same bits on two machines, which is what lockstep needs; the page on [flags and portability](../engineering/flags-portability.md) shows how contraction changes results.
- **Inputs as data.** The editor's `input.key` command queues :term[simulated input]{id=simulated-input} for a number of fixed steps, and the scripts' library has a seeded random generator, `Random`, that gives one sequence on every platform. The pages on [simulated input](../input/simulated.md) and [input actions](../input/actions.md) describe both.
- **A step behind.** :term[Drawn transforms]{id=drawn-transform} between the last two fixed poses, read through `Scene::FindDrawnTransform`, use the idea of entity interpolation on one machine.
- **Scene documents.** A scene is a document that can be written and read, the starting point of a state that travels; the page on [scene documents](../world/serialization.md) teaches it.

:::why[Why does the editor's network code stay out of games?]
A game that links a socket layer also takes its listening port, its token handling and its attack surface, and a game that never needs them should not carry them. Strata's layer rule keeps tooling out of every shipped game, so the sockets that serve the editor cannot become a path into a player's machine. The cost is that a game that wants networking must bring its own transport.
:::

A game that wants to try would put the code in its script module, a :term[CMake]{id=cmake} project of the game's own. The rules of scripts bind it. :term[Callbacks]{id=callback} run on the :term[main thread]{id=main-thread} and must return quickly, so the code polls its socket without blocking. Threads that the module starts must never call the engine. The book has read these rules and has not built such a module.

## What Strata's choice cannot do

A game cannot play online with Strata today. To run any model of this page, it would have to add a transport, snapshots and their deltas, a way to rewind state for rollback or lag compensation, and devices assigned to players. The page on [gamepads](../input/gamepads.md) states that last absence. The page on [what Strata does not do](../appendix/not-in-strata.md) lists the other gaps.

The pieces above help, but they are not a network design. A snapshot needs the state of every entity in a form that can be diffed, and Strata has no such form. Rewinding needs the whole simulation, physics included, to load a saved tick, and Strata's physics has no save and load of its state that the book has verified.

## Common mistakes

- **TCP for fast-changing state.** Symptom: the game freezes for a round trip after each lost message. Fix: send state in datagrams, and make only the rare messages reliable.
- **Sending every frame.** Symptom: the bandwidth follows the frame rate, and a fast machine floods a slow one. Fix: send every tick, or every few ticks, and number the messages by tick.
- **Trusting a result that a client computed.** Symptom: a modified program wins every match. Fix: the client sends inputs, and the server computes and checks.
- **Counting frames instead of ticks.** Symptom: two machines with different frame rates disagree about when something happened. Fix: count fixed steps, as the page on [time](../core/time.md) shows.
- **Assuming that floating-point results agree.** Symptom: a lockstep game loses sync between two compilers or two processors. Fix: test the whole simulation on every target, or compute with :term[integers]{id=integer}.

## Summary

- A game sends datagrams, not a stream, because lost state is replaced by newer state; a reliability layer of numbers and acknowledgements covers the few messages that must arrive.
- The models differ in where they hide the delay: lockstep by waiting, rollback by guessing, snapshots by showing the past, prediction by running ahead, and lag compensation by rewinding the server. Each costs bandwidth, exactness or cheating resistance.
- :term[Quantization]{id=quantization}, deltas and interest management cut a stream of 168,000 bytes a second to about 2,000 in the page's example.
- With interpolation one snapshot interval behind, one lost snapshot makes the ball wait and then jump, and a second interval of delay hides it.
- Strata has no gameplay networking; a game would need a transport, snapshots with deltas, state that can be restored and devices assigned to players.

## Check yourself

1. A game sends each object's position over TCP every frame. A message is lost, and players report that everything freezes for about 100 ms. Which is the cause?

   - A. The server is overloaded.
   - B. TCP holds later messages until the lost one is sent again.
   - C. Interpolation needs two snapshots.
   - D. The frame rate is too low.

   :::answer{tests="transport"}
   Answer B. TCP delivers in order, so the messages after the lost one wait for a new copy, which takes at least one round trip. A server that is overloaded slows all messages, not only after a loss (A). Interpolation (C) belongs to datagram snapshots, and a low frame rate (D) does not depend on a loss.
   :::

2. A fighting game and a strategy game with 2,000 units both need exact copies on every machine. Which model suits each, and why?

   :::answer{tests="models"}
   The strategy game suits deterministic lockstep, because 2,000 units are too many to send and an input delay of 100 ms does not hurt a unit that walks. The fighting game suits rollback, because 6 frames of delay would hurt, and a replay of a few small steps is cheap. Both need the same bit-exact simulation.
   :::

3. A snapshot holds 200 objects. Each has a 1-byte identifier and a position of 3 values. Compute the bytes of one full snapshot with 32-bit floats and with 16-bit values, ignoring headers.

   :::answer{tests="bandwidth"}
   With floats, one object takes 1 + 12 = 13 bytes, so the snapshot takes 200 × 13 = 2,600 bytes. With 16 bits, one object takes 1 + 6 = 7 bytes and the snapshot 1,400 bytes. The quantization saves 1,200 bytes, which is 46 %.
   :::

4. With the sketch of the first exercise, the delay is 3 ticks and the snapshot of tick 30 is lost. What does the client draw at tick 32?

   :::answer{tests="interpolation"}
   The client draws the ball at tick 29, and the newest snapshot it has is from tick 27, with no newer one. The ball waits at 1.800 m, while the truth is 1.933 m, an error of 0.133 m. With a delay of 6 ticks, the client would draw tick 26, between the snapshots of ticks 24 and 27, and would not wait.
   :::

5. Name three things that Strata already has and three that a networked game would have to add.

   :::answer{tests="strata"}
   Strata has game time in fixed steps, drawn transforms between two fixed poses and inputs that arrive as data, with a seeded random generator and scene documents. A game would have to add a transport, snapshots and their deltas, a way to rewind state, and devices assigned to players.
   :::

## Exercises

1. **Basic.** Run the sketch below, then change the constant `c_DelayTicks` to 6. Predict first whether the ball still waits, and how large the error becomes.

   :::answer[Worked solution]{tests="interpolation,models" solution="sketches/appendix-networking-interpolation.cpp"}
   The program stores the snapshots that arrived and draws the ball at a tick that lies `c_DelayTicks` behind the newest one, between the two snapshots around it. The lost snapshot of tick 30 leaves a gap of six ticks. With a delay of 3, the client draws ticks 28 and 29 before snapshot 33 arrives, so the ball waits at 1.800 m and then jumps to 2.100 m. The error is first 0.133 m behind the truth, then 0.100 m ahead of it, and then it falls to 0.

   ```cpp sketch="appendix-networking-interpolation.cpp"
   // A server steps a ball 60 times a second and sends its position every third tick. One snapshot is lost.
   // The client draws the ball c_DelayTicks behind the newest tick, between the two snapshots around that time.
   #include <cstdio>
   #include <vector>

   namespace
   {
   	constexpr int c_SnapshotEvery = 3; // ticks between two snapshots: one snapshot interval
   	constexpr int c_LostTick = 30;     // the snapshot taken at this tick never arrives
   	constexpr int c_DelayTicks = 3;    // how far behind the newest tick the client draws

   	struct Snapshot
   	{
   		int Tick = 0;
   		double X = 0.0;
   	};

   	// The server's ball moves at 4 m/s and is pushed to 8 m/s at tick 30 (0.5 s).
   	double ServerPosition(int tick)
   	{
   		const double seconds = tick / 60.0;
   		return seconds <= 0.5 ? 4.0 * seconds : 2.0 + 8.0 * (seconds - 0.5);
   	}
   }

   int main()
   {
   	std::vector<Snapshot> received;
   	std::printf("now drawn  shown  true  error (m)\n");
   	for (int now = 0; now <= 45; now++)
   	{
   		if (now % c_SnapshotEvery == 0 && now != c_LostTick)
   			received.push_back({ now, ServerPosition(now) });
   		if (now < 24)
   			continue;

   		const int drawnTick = now - c_DelayTicks;
   		const Snapshot* before = nullptr;
   		const Snapshot* after = nullptr;
   		for (const Snapshot& snapshot : received)
   		{
   			if (snapshot.Tick <= drawnTick)
   				before = &snapshot;
   			if (snapshot.Tick >= drawnTick && !after)
   				after = &snapshot;
   		}

   		// With no newer snapshot, the ball waits where the last one put it.
   		double shown = before->X;
   		if (after && after->Tick != before->Tick)
   			shown += (after->X - before->X) * (drawnTick - before->Tick) / (after->Tick - before->Tick);
   		const double truth = ServerPosition(drawnTick);
   		std::printf("%3d %5d %7.3f %6.3f %6.3f\n", now, drawnTick, shown, truth, shown - truth);
   	}
   	return 0;
   }
   ```

   ```text output-of="appendix-networking-interpolation.cpp"
   now drawn  shown  true  error (m)
    24    21   1.400  1.400  0.000
    25    22   1.467  1.467  0.000
    26    23   1.533  1.533  0.000
    27    24   1.600  1.600  0.000
    28    25   1.667  1.667  0.000
    29    26   1.733  1.733  0.000
    30    27   1.800  1.800  0.000
    31    28   1.800  1.867 -0.067
    32    29   1.800  1.933 -0.133
    33    30   2.100  2.000  0.100
    34    31   2.200  2.133  0.067
    35    32   2.300  2.267  0.033
    36    33   2.400  2.400  0.000
    37    34   2.533  2.533  0.000
    38    35   2.667  2.667 -0.000
    39    36   2.800  2.800  0.000
    40    37   2.933  2.933 -0.000
    41    38   3.067  3.067  0.000
    42    39   3.200  3.200  0.000
    43    40   3.333  3.333  0.000
    44    41   3.467  3.467 -0.000
    45    42   3.600  3.600  0.000
   ```

   1. **Lines 32–33:** the snapshot of tick 30 is never stored, which is the loss.
   2. **Lines 40–45:** the loop finds the newest snapshot at or before the drawn tick and the first one at or after it.
   3. **Lines 49–51:** with no newer snapshot the ball waits; otherwise it moves in a straight line between the two.

   With a delay of 6, the client always holds a snapshot after the drawn time, so it never waits. It draws between snapshots 27 and 33 for the whole gap. The error is then only the smoothing of the push at tick 30, at most 0.1 m, and the ball is two intervals in the past.
   :::

2. **Hard.** For a strategy game, a fighting game and a shooter, name the model each needs, what it costs, and what Strata would have to add.

   :::answer[Worked solution]{tests="models,strata"}
   The strategy game needs deterministic lockstep. It costs a bit-exact simulation, an input delay and a wait for the slowest player. Strata would add a transport and a check of results between machines, such as a :term[hash]{id=hash} of the state every few ticks, and it would have to test its floating-point results on every target.

   The fighting game needs rollback. It costs the replay time of several steps in one frame. Strata would add a transport, a quick save and load of the whole state, and devices assigned to the two players.

   The shooter needs a server with prediction and lag compensation. It costs a server, a history of every target for rewinding hits and shared movement code. Strata would add a transport, snapshots and their deltas, a way to rewind state, and the server side of its scripts.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Network/Socket.h`, `Strata/src/Strata/Network/JsonRpc.h`, `Strata/src/Strata/Network/RpcServer.h` and `Strata/src/Strata/Network/RpcConnectionLimits.h`: the sockets, the framing and the limits of the editor's server, the only network code of the engine.
- `StrataTests/Architecture/Layers.json`: the `Network` layer, marked as tooling, which may include only `Core`.
- `Strata/src/Strata/Scene/Scene.h`: `GetFixedTimestep`, `GetFixedStepCount` and `FindDrawnTransform`, the tick and the drawn pose.
- `StrataScriptCore/Include/StrataScript/Gameplay.h`: the seeded `Random` of the scripts' library.
- `StrataTests/src/Physics/PhysicsBox3DTests.cpp`: the suite `Physics.Box3D`, the golden hash of the physics determinism scenario.
- `StrataEditor/src/Editor/EditorInputCommands.cpp`: the `input.key` command and its fixed-step durations.

## Further reading

- [Glenn Fiedler, "Networking for Game Programmers"](https://gafferongames.com/categories/game-networking/): UDP against TCP, reliability over UDP, snapshots and state synchronization, with code; intermediate.
- Gabriel Gambetta, "Fast-Paced Multiplayer": the client-server architecture, prediction, reconciliation, interpolation and lag compensation in four short parts with demos; beginner.
- Bettner and Terrano, "1500 Archers on a 28.8: Network Programming in Age of Empires and Beyond" (Game Developers Conference, 2001): deterministic lockstep in a shipped game; advanced.
- Valve, "Source Multiplayer Networking" (developer documentation): snapshots, interpolation, prediction and lag compensation of a shipped engine; intermediate.
- Tony Cannon, "GGPO" (ggpo.net): the rollback library and its description; intermediate.
- Timothy Ford, "Overwatch Gameplay Architecture and Netcode" (Game Developers Conference, 2017): prediction and the netcode of a modern shooter; advanced.
