# Notes: appendix/networking

## New terms

Each is defined once in bold on the page, general knowledge, home `appendix/networking`.

- latency (network): the time a message needs to travel from one machine to another; its round trip is the round-trip time. Aliases: round-trip time. One sentence of the page tells that audio latency is another sense (not written; the page links no audio page).
- packet loss: the share of messages that never arrive.
- jitter (network): the change of the latency from one message to the next; the sub-pixel offset of temporal anti-aliasing is another term.
- head-of-line blocking: later messages of a stream wait for an earlier lost one (bold on the page).
- tick (simulation), tick rate: one fixed step of the simulation counted as a number, and the number of ticks a second.
- authority: the one simulation that decides what is true for a piece of state. Alias: authoritative server.
- datagram, user datagram protocol (UDP): a separate message that carries its own boundaries and may be lost, copied or reordered.
- deterministic lockstep: machines send only inputs and run the same deterministic steps.
- rollback: guess the remote input, run on, and restore and replay when the real input differs. Alias: rollback network code.
- snapshot (networking): the state of the game at one tick, sent by a server.
- entity interpolation: draw a remote object between the two snapshots that surround a time in the past.
- client-side prediction: apply the local player's inputs at once, with the server's movement code.
- server reconciliation: take the server's state as the truth and replay the inputs it has not applied.
- lag compensation: the server moves targets back to the time the shooter saw before it tests a hit.
- quantization, delta compression, interest management (relevancy): bandwidth tools, bold in their own paragraphs.
- NAT traversal, relay server: bold in two paragraphs.

## Requests

- Extra words: rewind (rewinds, rewinding), StarCraft, QuakeWorld, Overwatch, lockstep (if not admitted as a term), NAT, UDP, datagram.
- External hosts for Further reading, cited without a link: gabrielgambetta.com (Gambetta), developer.valvesoftware.com (Valve), ggpo.net (GGPO), gdcvault.com is listed already (the two talks have no verified address, so no link).
- No figures file: all five pictures are Mermaid diagrams (idea, lockstep beside rollback, snapshot interpolation, prediction, layers).

## Not verified

- The "Used by" cells of the table (Age of Empires, StarCraft, Quake 3, Source engine games, QuakeWorld, Overwatch, fighting games with rollback libraries) and the typical figures (RTT of 30 to 150 ms, a loss of one in fifty on a wireless link, 1,200 bytes per datagram, a maximum rewind of about 200 ms) are general knowledge, not fetched from the sources of Further reading.
- That Strata's physics has no save and load of its state: not searched at the pin; the page says the book has not verified one.
- A game script module's rule that callbacks must return quickly is read from the ABI comment (the engine calls the module on its main thread); not run.

## Findings not applied

- critic-appendix-7: applied (Strata's choice states that the documents name no plan, with the search). 
- critic-appendix-9: partly. The rollback row cites GGPO and the lockstep row the Age of Empires talk, both in Further reading and marked unfetched here; a game-ai counterpart is not this page.
- critic-appendix-10: the terms are qualified as "jitter (in networking)" in text; the sentence on audio latency and the link to the tick of behaviour trees are not written, because those pages are not in this page's closure; the planner may add them.
- critic-appendix-13: not this page (appendix/not-in-strata).
- critic-appendix-15: applied in Strata's choice (script module, polling, own threads), marked read, not run.

## Clerk

- Admitted terms: Latency (networking), packet loss, Jitter (networking), head-of-line blocking, Tick (networking) (alias tick rate), authority, datagram, deterministic lockstep (alias lockstep), Rollback (networking), Snapshot (networking), entity interpolation, client-side prediction, server reconciliation, lag compensation, delta compression, interest management (alias relevancy), NAT traversal (alias NAT), relay server; qualified where another home holds the word. Refused: UDP as a term (the page defines it with datagram in one paragraph; UDP is a protocol's name, now in names.txt). Refused: quantization (homed on basics/color). Names: StarCraft, QuakeWorld, Overwatch. Extra words: rewind, rewinds, rewinding. Hosts: gabrielgambetta.com, ggpo.net admitted; developer.valvesoftware.com left for the planner (bot check).
