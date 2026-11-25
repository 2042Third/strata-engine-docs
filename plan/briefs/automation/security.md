# Brief: `automation/security`

| Field | Value |
| --- | --- |
| Title | The security model |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `automation/rpc-server`, `core/files` |
| From | automation ch. 7 (the threat model of loopback, tokens, HMAC challenge and response, the server's proof first, limits before authentication, private session files, the untrusted pointer, pid reuse and TOCTOU-safe file handling) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `automation/security` — The security model

**Covers.** The job: deciding who may drive the editor, and keeping the secret that decides it. The problem and how
programs solve it (this page carries the full section): loopback is not private, because every local process and every
web page in a local browser can open a connection to the port, and the editor can write files, build code and load it;
the threat model in one sentence, "only holders of the token are trusted"; the approaches (endpoints that the operating
system protects, bearer tokens, mutual challenge and response, TLS client certificates) and their costs. From zero, on
top of the cryptographic hash of `basics/data-formats`: a message authentication code and HMAC, nonces and the replay
attack, the reflection attack, timing side channels and comparison in constant time, and the system's secure random
generator. The map: the token's life, from `GenerateSessionToken` to the private session file and the client that reads
it, and the two proofs that travel in its place. The contract, rule by rule with its reason: loopback only (the server
binds only loopback; clients follow only loopback sessions); no server without a token, and the token never on the
wire, in a log or in printed output; the server proves first; secrets are compared in constant time; client names are
shown, never trusted, and cleaned; the project's pointer is untrusted and holds no port or token; session files are
private; a pid is not an identity; shared files are never checked and then deleted. A toy handshake of about 50 lines
that the reader breaks in three ways (send the token, compare with `==`, let the client prove first). The real code, in
two halves. The handshake: the protocol as the header's comment states it; the proofs (labels, nonces of a fixed
format, HMAC-SHA256 in hexadecimal); the server's `HandleHandshakeMessage` (two steps, the reject helper, equal nonces
refused, the client limit, the message limit raised after authentication); the client's `AuthenticateLocked`, which
checks the server's proof before it proves anything; the limits before authentication (4 KiB messages, 16 KiB of
output, 5 seconds) and the eviction of pending connections made a pure function; the checks of `Start`. The files that
keep the secret: what a session file holds and where it lives, the private directory with no shared fallback and no
symbolic link, reads that check and read through one handle, the project pointer that only chooses which file to read,
process identity by pid and start time (an unverifiable process is skipped, never deleted), stale files taken aside,
judged again and put back with `RenameNoReplace`, the pointer removed the same way, and why a token on the command line
is discouraged. The example: the handshake computed by hand as the test recomputes it with `Crypto`, then an impostor
on a dead editor's port that fails at the client's first check. Alternatives Strata did not choose; how it is tested
(the handshake cases of `Network.RpcServer`, `Network.EditorSession`); changing it safely. Afterwards the reader can
explain each step of the handshake and the attack it stops, and change how session files are written or removed without
opening a race.

**Leaves out.**

- How clients find an editor, pin it and launch one → `automation/sessions`
- How private files are created and read on each system → `core/files`
- SHA-256 as a hash → `basics/data-formats`
- The server's limits after authentication and its backpressure → `automation/rpc-server`
- Every limit's value in one table → `reference/automation`

**Fit.** `fits`: about 8,250 words against XL (8,000). Eight excerpts in two halves with their own anchors, "The
handshake" and "Files that keep the secret", take the most, then nine rules and HMAC, nonces and two attacks taught
from zero; four exercises close the page.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:363` | concept | home | The security model: the threat model of loopback, four approaches, Strata's token, handshake and private files; hashes, MACs, nonces, replay and reflection, timing |
| `automation:74-75` | feature | home | The limits before authentication and the eviction of pending connections |
| `automation:86` | feature | home | `Start` refuses a bind address that is not loopback and an empty token |
| `automation:92-99` | feature | home | The mutual challenge and response, the server first, labels, nonces of a fixed format, constant-time comparison, one handshake per connection, the session token, the engine's own SHA-256 and HMAC |
| `automation:108` | feature | home | The client's optional name, sent in the handshake and proving nothing |
| `automation:114-119` | feature | home | `EditorSessionInfo`, the per-user session file, the untrusted project pointer, process identity, race-safe pruning of stale files and of the pointer |
| `automation:122` | feature | home | Trusted reads: checked and read through one handle, 64 KiB at most |
| `automation:201` | feature | home | `--token` is allowed but discouraged: other processes can read a command line |
| `automation:235` | feature | home | The suite `Network.EditorSession`: pid reuse, the stale-file race, owner-only files, the untrusted pointer, a session directory reached through a symbolic link |
| `automation:474` | code | home | `Strata/src/Strata/Network/RpcServer.h:107-133`: the whole handshake specified in a comment |
| `automation:476` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:1027-1156`: `HandleHandshakeMessage`, the server's two steps |
| `automation:479` | code | home | `Strata/src/Strata/Network/RpcClient.cpp:66-114`: `AuthenticateLocked`, the server's proof checked first |
| `automation:480` | code | home | `Strata/src/Strata/Network/RpcServer.cpp:330-363`: nonces and the two proofs, labels and `Crypto::HmacSha256` |
| `automation:484` | code | home | `Strata/src/Strata/Network/RpcConnectionLimits.h:10-21`: the eviction policy as a pure function; its body is `RpcServer.cpp:550-563` |
| `automation:494` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:393-404`: `GetSessionProcessState`, pid and start time; unverifiable is not exited |
| `automation:496` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:315-342`: `RemoveStaleSessionFile`, take aside, judge again, restore with `RenameNoReplace` |
| `automation:498` | code | home | `Strata/src/Strata/Network/EditorSession.cpp:375-391`: `ReadProjectSession`, the pointer only chooses, the per-user file must agree |
| `automation:538` | figure | home | The handshake as a sequence, with the inputs of each HMAC and its label, and a second lane where an impostor on a dead editor's port fails at the first check |
| `automation:553` | figure | home | Session files: the private per-user directory with `<pid>.json` (port, token, start time) beside the project's pointer (process id, project, version, headless, start timestamp; no port, no token), with the arrows of trust; `automation/sessions` adds the order of discovery |
| `automation:556` | figure | home | Stale-file removal with two processes: take aside, judge again, restore, and the race it prevents |
| `automation:597-611` | rule | home | Loopback only, worded as "the server binds only loopback; clients follow only loopback sessions" (an explicit endpoint is not checked, `automation/sessions`); no server without a token and the token never on the wire, logged or printed; the server proves first; constant-time comparison; the pointer untrusted; session files private; a pid is not an identity; never check and then delete |
| `automation:640` | rule | home | Client names are shown, never trusted, and cleaned of control and bidirectional characters |
| `automation:678` | hands-on | home | Exercise: a raw client in Python or C++ that performs the handshake by hand, calls `rpc.listMethods`, then sends an HTTP request and sees the connection close |
| `automation:689` | hands-on | home | Exercise: a fake server on a stale port that relays proofs, against the test "The client refuses a server that cannot prove it knows the token" |
| `automation:696` | hands-on | home | Exercise: a test in which a new process takes the pid's path between the read and the delete |
| `new:10` | hands-on | home | The "trace it yourself" exercise (D27), the first and easiest of the page's four (with `automation:678`, `:689` and `:696`; about 150 words): a search for `Crypto::HmacSha256` and `Crypto::ConstantTimeEquals` in `Strata/src/Strata/Network` names, for each call, the proof it computes or compares and the side that runs it; a breakpoint in `RpcClient::AuthenticateLocked` during `StrataCLI status` then shows the server's proof checked before the client sends its own. Evidence: `Strata/src/Strata/Network/RpcClient.cpp:66`, `:99`; `Strata/src/Strata/Network/RpcServer.cpp:354`, `:362`, `:1132` |
| `automation:715` | term | home | Process start time |
| `automation:743-744` | term | home | Token (session token), qualified against the tokens of a language model; nonce |
| `automation:746-756` | term | home | HMAC, challenge and response, mutual authentication, replay attack, reflection attack, constant-time comparison, domain separation label, CSPRNG, threat model, session file, project pointer |
| `automation:761` | term | home | Stale session |
| `automation:234` | feature | use | The handshake cases of `Network.RpcServer`: both ways, a replayed proof, an impostor server, the authentication timeout, slot hoarding and eviction |
| `automation:520` | code | use | The other half of the item: the handshake recomputed independently in `StrataTests/src/Network/RpcServerTests.cpp`, as the page's example |
| `automation:590` | figure | use | The two handshake lines of the raw capture |
| `foundation:156` | feature | home | `Crypto` (passed by `core`): the engine's own SHA-256, HMAC-SHA256, constant-time comparison and hexadecimal, as the handshake calls them; the implementation is named, not walked |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The RPC server: connections, the network thread, built-in methods, limits | `automation/rpc-server` | must |
| Loopback, ports and sockets; JSON-RPC requests and error codes | `automation/json-rpc` | must |
| Private files and directories, trusted reads, `RenameNoReplace`, TOCTOU | `core/files` | must |
| Cryptographic hashes such as SHA-256 | `basics/data-formats` | must |
| Hexadecimal digits | `basics/numbers` | must |
| Processes and process ids | `basics/computer` | must |
| Command-line arguments and environment variables | `basics/tools` | must |
| Unicode text and UTF-8 | `basics/bytes` | helps |
| Random numbers and seeds | `basics/math-probability` | helps |
| The operating system's seams (`Platform::*`) | `core/platform` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `challenge-response` | Challenge-response | - |
| `constant-time-comparison` | Constant-time comparison | - |
| `csprng` | CSPRNG | - |
| `domain-separation-label` | Domain separation label | - |
| `hmac-automation` | HMAC (automation) | - |
| `mutual-authentication` | Mutual authentication | - |
| `nonce` | Nonce | - |
| `process-start-time` | Process start time | - |
| `project-pointer` | Project pointer | - |
| `reflection-attack` | Reflection attack | - |
| `replay-attack` | Replay attack | - |
| `session-file` | Session file | - |
| `session-token` | session token | - |
| `stale-session` | Stale session | - |
| `threat-model` | Threat model | - |
