# Notes: `automation/security`

## New terms

None proposed. The page defines the glossary's fifteen entries it homes (threat model, session token, challenge-response, HMAC, session file, project pointer, nonce, replay attack, mutual authentication, reflection attack, domain separation label, constant-time comparison, CSPRNG, process start time, stale session).

## Since

`v0.3.0` (2026-10-13): since 0.3.0. The handshake, session files and private files exist from the first automation server.

## Requests

- `tools/data/extra-words.txt`: "handshake" (26 uses; the name of the two-step exchange, also in the brief), "cryptographically" and "pseudorandom" (the expansion of CSPRNG, which the acronym rule requires beside its first plain use). The three `word-list` findings stay until the words are added.
- Hosts for `tools/external-hosts.txt`: `rfc-editor.org` (RFC 2104 and RFC 4231) and `cheatsheetseries.owasp.org`. The four Further reading entries cite without links until then.
- Figures: none requested; the three diagrams are Mermaid. The page has no figures file.

## Not verified

- That a local process cannot read the loopback traffic of another account: the page says the handshake does not hide the connection, and makes no claim about who can capture it.
- The hexadecimal proofs of the worked example come from an independent HMAC-SHA256 over the test's token and a client nonce, with a server nonce of the page's choosing; the engine was not run on them.
- The Python script of exercise 2 was not run against an editor (no engine program is started); its framing (one JSON line per message) and labels are read from `RpcServer.cpp`, `RpcClient.cpp` and the tests' `RawRpcConnection`.
- The general statements of the alternatives table (who uses sockets protected by the system, certificates, bearer tokens) and of the HMAC and timing sections are not claims about Strata.
- What the four Further reading entries say: not fetched.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted to extra-words.txt: handshake, cryptographically, pseudorandom.
- Admitted to external-hosts.txt: www.rfc-editor.org and cheatsheetseries.owasp.org (each front page is what it claims).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
