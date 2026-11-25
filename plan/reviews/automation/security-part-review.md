# Part review: automation/security

- contradiction: the first rule aside counted three rules of `AGENTS.md`, the second four, for the same list; the first now says four (loopback only, a token for every server, a token that never travels, a pointer without secrets).
- wrong: "How it is tested" put `Clients may name themselves in the handshake; the server lists them and tells handlers` in `Network.RpcServer`; it is in `Network.RpcPresence` (RpcServerTests.cpp:1766), as `automation/rpc-server` says.
- wrong: 2^128 was "about 3.4 followed by 38 zeros"; 3.4 times 10^38 is 34 followed by 37 zeros.
