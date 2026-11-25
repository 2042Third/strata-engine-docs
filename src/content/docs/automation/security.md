---
id: automation/security
title: "The security model"
description: "How the editor decides who may drive it: a secret token that never travels, a handshake in which both sides prove it, and files that keep the secret private."
kind: internals
size: XL
tracks: [E]
needs: [automation/rpc-server, core/files]
time: 130
learn:
  - id: threat-model
    text: explain why a loopback port is open to every local process and web page, and what the editor trusts instead
  - id: handshake
    text: trace the two steps of the handshake and name the attack each check stops
  - id: compare-and-random
    text: explain why proofs are compared in constant time and why nonces and tokens come from the system's secure random generator
  - id: session-files
    text: explain how a session file, the project pointer and a process's start time work together without trusting any one of them
  - id: race-safe-removal
    text: change how session files are removed without opening a race between checking a file and deleting it
since: 0.3.0
status: final
---

The editor can write files, build code and load it into itself, so whoever drives it can run programs as you. This page
covers how Strata decides who may do that. The editor creates a secret when it starts and keeps it in a file that only you can read. Then it accepts a connection
only from a client that proves it holds the secret. The client demands the same proof from the editor.

The page does not cover how clients find an editor
([sessions](../automation/sessions.md)), what the server does after a client is trusted ([the server](../automation/rpc-server.md)),
or how private files are made on each system ([files you can trust](../core/files.md)).

## The problem and how engines solve it

An :term[automation]{id=automation} server is a door into a powerful program. Opening a door is quick work; the problem is to open it for your own
tools and for nobody else.

### Loopback is not private

The editor listens on a port of the **loopback** address, which only programs on the same machine can reach. That sounds
private, but consider who is on your machine. Every program you run is there, and so is every page open in your web
browser. A page can ask the browser to connect to `127.0.0.1` and a port number, and the browser will try. The port
has no idea who is knocking.

Now count what a connection to the editor could do. It could create a script, build it and load it into the editor,
and a script is a program with your rights. One open door is enough to read your files, change your project or send
them away. A :term[game engine]{id=game-engine} editor is a bigger target than it looks.

So the first decision is the **threat model**: a statement of who the system defends against and what that enemy can do.
Strata's fits in one sentence: only holders of the token are trusted. The enemy is any other process or web page on the
machine, even one that runs as you. It can connect to any port, send any :term[bytes]{id=byte}, connect many times, and read every file
that the :term[operating system]{id=operating-system} lets your account read. It cannot read a file that only the editor's own account may read,
and it cannot guess a number of 128 random bits.

The words "even one that runs as you" matter. A program that runs under your account can read your files. The defence is
therefore not "files that only you can read" alone: the secret sits in such a file, but the connection also has to
prove that the other end knows what the file says. Both halves work together, and the rest of the page builds them.

### Four ways to prove who you are

Four approaches are common, and each costs something.

An endpoint that the operating system protects needs no secret on the wire. A local socket is a file, and the system
checks the file's owner and mode before a process may connect. A Windows named pipe has an access list in the same way.
The cost is a second kind of channel on three systems, which the editor, the command-line client and every agent tool
must all speak. A web page can never open such a channel, which is a gain, but many test tools could not use it either.

Strata chose a plain port because every tool and language can open one.

A **session token**, a random secret that the editor makes when it starts and that is valid until it stops, travels with
each request. This is the bearer token: whoever holds it is trusted. The cost is that it crosses the wire. A client that
connects to the wrong program hands the secret over, and a program that can read the traffic can use it.

A **challenge-response** exchange fixes the first cost. One side sends a random challenge; the other answers with a
value computed from the challenge and the secret. The secret stays at home and only the answer travels. When both sides
challenge each other, the exchange is mutual. The cost is a small protocol, and small
protocols have subtle failures: the rest of this page is about those.

Mutual authentication with certificates is the fourth: each side holds a key pair and a certificate that the other
checks, as web sites do. The cost is a key store: someone must create, hand out,
renew and withdraw certificates. For a program that starts on one person's machine and lives for hours, that is far
more machinery than the secret it protects.

Strata's choice is the third: a secret token, a challenge-response in both directions, and the token kept in a
file that only the user's account reads. The section "Alternatives Strata did not choose" returns to the table of costs
at the end of the page.

### A keyed hash as the answer

What should the answer be? The cryptographic hash from [data formats](../basics/data-formats.md) takes any bytes and
gives a fixed-size digest, and nobody can find the input from the digest. A first idea: the answer is the :term[hash]{id=hash} of the
challenge with the secret attached. That is close, but joining a secret to a message and hashing it has known
weaknesses for some hash designs. A standard construction avoids them: the hash-based message authentication code (HMAC).

The **HMAC** mixes the key into a hash twice, once in an inner pass and once in an outer pass. The result depends on
both key and message in a way that is safe to publish. A message authentication code is a short tag that only a holder of the key can make for a
given message, and that anyone with the key can check.

Strata uses HMAC with :term[SHA-256]{id=sha-256} and writes the 32 bytes of the tag as 64 lower-case :term[hexadecimal]{id=hexadecimal} digits. Its own
implementation of both lives in `Strata/src/Strata/Core/Crypto.h`, named here and not walked through: the tests of
`Core.Crypto` hold it to the published test vectors, and the handshake only calls it.

## The map

Follow the secret from birth to use. The editor starts and calls `EditorSession::GenerateSessionToken`, which asks the system
for 16 random bytes and writes them as 32 hexadecimal digits. If the system cannot supply them, the function returns an
empty string and the editor's automation stops with an error before the server starts, so there is no weak fallback. The editor starts the server
with the token. Once it knows the server's port, it writes the token and the port into its **session file**, a :term[JSON]{id=json}
file named after its process id, in a private folder.

A client starts with no secret. It reads session files, picks the editor it wants and connects to the port in the file.
The two sides then run the handshake: each proves it holds the token, and only proofs travel. A second kind
of file sits beside the project: the **project pointer**, which names a process but holds neither a port nor a token. A
shared project folder may be written by anyone who can write there, so the pointer only suggests which session file to read,
and the session file in the private folder has the last word.

```mermaid caption="The life of the token: the editor makes it and writes it to a private file, a client reads the file, and only proofs cross the connection." alt="A diagram with three boxes in a row. The editor makes the token and writes a private session file. The client reads the private file and then connects to the editor, and only two proofs cross between them. A dashed box for the project file holds a pointer to the editor's process, with an arrow to the private file marked as a hint only."
flowchart LR
    E["Editor: GenerateSessionToken"] -->|writes owner-only| S["Private session file: pid, port, token, start time"]
    S -->|read through one handle| C["Client"]
    C <-->|"two proofs, never the token"| E
    P["Project pointer: pid, project, no port, no token"] -.->|"hint: which file to read"| S
```

The rest of the page takes this picture apart. The contract comes first, rule by rule, with the reason for each. A toy
handshake follows that you can break in three ways. Then the real code in two halves, the handshake and the files that
keep the secret, a worked example, and the questions.

## The contract: the connection

Eleven rules hold the model together. Each one has a reason, and most have an attack that the reason names. They fall into three groups: the connection, the proofs and names, and the files.

### Loopback only

The server binds only a :term[loopback]{id=loopback} address, and clients follow only sessions that name one. `RpcServer::Start` checks the bind
address and refuses anything that is not a numeric loopback address, such as `127.0.0.1` (the whole range `127.0.0.0/8`)
or `::1`. The reason is that full control of the editor must not be offered to the network. The cost is that you cannot
drive an editor on another machine through this door, which is a loss that the design accepts.

Clients apply the same rule from their side: StrataCLI uses a session only when its address is loopback. An explicit
endpoint given by hand is not checked in the same way; how the clients treat it is the subject of
[the sessions page](../automation/sessions.md).

### No server without a token, and the token never leaves

`Start` also refuses an empty token. A server that needs a token and is given none must not start open; it
fails and says why. The token is never sent on the wire, never written to a log and never printed. A log line is a
copy that stays after the process ends, and the output of a command may be pasted into a bug report, so a token in either
place stops being secret.

The token's quality matters too. A predictable token, such as a counter or the time, would let a process try values until one
works. Sixteen bytes from the system's secure random generator give 2^128 possibilities, about 34 followed by 37 zeros. At a billion
guesses a second the average search would take more than 10^21 years.

The operating system has a part built for this, the cryptographically secure pseudorandom number generator (CSPRNG). An
ordinary generator such as the one behind dice rolls in a game is fast and predictable: its next value follows from
a few earlier ones. A **CSPRNG** is fed by the system's unpredictable events and is built so that even someone who sees
many of its outputs cannot predict the next. Strata asks it through `Platform::GenerateSecureRandom` for every token,
every nonce and every random file suffix, and treats a failure as an error, never as a reason to use something weaker.

### The server proves first

Before the client sends anything derived from the token, the server must show that it knows the token. Imagine that an
editor exits and leaves its session file behind, and another program takes its port. A client that reads the old file
connects to the stranger. If the client spoke first, it would hand a proof to a process that has shown nothing. So the
client waits for the server's proof, checks it, and stops if it is wrong.

The second half of the exchange is the reverse: the server will not accept any request before the client's proof. Each
side proves to the other, which is **mutual authentication**.

### Fresh numbers and the replay attack

A proof built only from the token would be the same every time. Someone who records one valid exchange could send it
again tomorrow. That is the **replay attack**: an attacker who cannot make a proof sends an old one.

The defence is a **nonce**, a "number used once": each side adds a fresh random number to what it proves, so a recorded proof matches only the
connection it was made for.

Strata's nonces are 16 random bytes, written as exactly 32 lower-case hexadecimal characters.  When two values are glued together to form a message, the border between them has to be
clear. Suppose nonces could have any length. Then the pair `ab` and `c` and the pair `a` and `bc` would glue into the
same text `abc`, and two different exchanges would share one proof. With fixed length the border is always in the same
place.

## The contract: proofs and names

### Reflection and the labels

The second attack is the **reflection attack**. The attacker opens a connection and sends back what the other side
sent. If the editor's proof and the client's proof were computed in the same way, the attacker could take a proof that
the editor made. It could return that proof as if the client had made it, and never need the token.

Two defences stop this. First,
each side refuses a peer nonce equal to its own: the server checks that its nonce differs from the client's, and the client does the
same. Second, the two directions use different **domain separation labels**: short fixed texts, here `strata-server` and
`strata-client`, put at the front of what is proved. A proof made with one label is useless where the other is expected,
even if every other input matched.

### Compared in constant time

When the server checks a proof, it compares two strings of 64 characters. The usual `==` stops at the first difference, which is fast and leaks.
An answer that differs at the first character is rejected a little sooner than one that
differs at the last. A program that measures the delays a million times can tell the two apart. This is a
timing side channel, an information leak through how long something takes instead of what it says.

Here is how it would work. The attacker wants to forge a proof. It tries all sixteen digits for the first position and
finds the one whose rejection takes longest, which is the one that matched. Then it moves to the second position.

The proof has 64 digits, so at most 64 positions times 16 digits, 1,024 tries, give the attacker a full valid proof
without knowing the token. Whether the noise of the link hides the delays decides if the attack works, and the safe design
does not depend on the answer.

The **constant-time comparison** examines every character whatever the outcome, and combines the results at the end,
so the time depends on the lengths only. `Crypto::ConstantTimeEquals` is this function, and both the server and the client use it for every proof. The
lengths are not secret, because the proofs always have 64 characters.

### Names are shown, never trusted

A client may send a name in its handshake, such as "Claude Code" or "StrataCLI". The server shows it in the list of clients
and the :term[activity journal]{id=activity-journal} so that a person can see who is connected. It proves nothing: any client may send any name,
including the name of another tool.

Since the name is shown to a person, it can be used to deceive. Control characters can rewrite a line in a terminal, and
the bidirectional format characters of :term[Unicode]{id=unicode} can make text read in a different order than it was written. The server
therefore cleans the name. It keeps at most 64 characters, replaces broken :term[UTF-8]{id=utf-8} with a replacement character, and
drops control characters and the format characters that change the order of text or hide it. The name is a label for people, never a
credential.

## The contract: the files

### The project pointer is untrusted and holds no secret

The file `.strata/EditorSession.json` in a project names the editor that has the project open: its process id, project
path, version, whether it is headless and a start timestamp. A project folder is a shared place. It may come from a
download, a copy from :term[version control]{id=version-control} or a colleague. Anything in it could have been written by someone else, so the
pointer holds neither the port nor the token. A planted pointer could otherwise send clients to a port of the planter's
choice, or leak the token to everyone who can read the folder.

The pointer's one job is to choose which per-user session file to read. That file, in the private folder, must exist, be
trusted, belong to the same process, name the same project and belong to a running process. When any check fails, the
pointer is ignored.

### Session files are private

The session file holds the token, so it is written for its owner alone: mode 0600 on Linux and macOS, an owner-only
access list on Windows. The folder is private, named `Sessions`, inside a `Strata` folder in the data folder of your
account. There is no fallback. If the system has no such folder, sessions are refused, and the code never uses a shared
place such as the temporary folder, where another account could read the secret.

On Linux and macOS the folder must belong to the current user, and nobody else may change it. A folder reached through
a symbolic link is refused too, because a link can point the folder somewhere else. How `EnsurePrivateDirectory`, `WritePrivateFile` and `ReadTrustedFile` do this on each system
is the subject of [files you can trust](../core/files.md).

:::rule[Automation stays on loopback, behind a token that never travels]
`AGENTS.md` gives the editor's automation four rules. The server accepts loopback addresses only and never runs
without a token. The token is not sent, logged or printed. A project's pointer file is not trusted and holds no port or
token. The reason is the threat model: the editor is a door to a program with your rights, so the door needs a lock whose
key never leaves the file.
:::

### A process id is not an identity

A session file names a process by its id, a small number that the system hands out and takes back. An editor that crashes leaves
its file behind. Later, a different program may get the same id. If a client tested only "does a process with this id
exist?", it would treat the old file as live and connect to whatever has the port, or refuse to clean it up.

The file therefore also records the **process start time**, the moment the system started it, and the client compares it with the start
time of the live process under that id. A different start time means a different process that took the id. When the
start time is unknown, the state is `Unverifiable`: the client does not use the session and does not delete it either,
because it may belong to a running editor.

A session whose process is gone, or whose id another process took, is a **stale session**.

### Never check, then delete

Several clients may clean the same folder at the same moment, and a new editor may write its own file at the same path
between a check and a delete. Suppose a client reads a file, sees that it is stale, and deletes it. If a new editor with
the same id wrote its file in the gap, the client deletes a live editor's secret. That gap between a check and its use is a
time-of-check to time-of-use race, which [files you can trust](../core/files.md) introduces.

The rule: take the file out of its place with one :term[atomic rename]{id=atomic-rename}, judge it again where nobody else can reach it, and put it
back unless it is still stale. A file that is shared is never checked and then deleted.

## A toy version

Here is the handshake in miniature, with three attacks on it. The toy replaces HMAC with a small non-cryptographic hash
so that the file stays short. That is fine for showing the protocol, and useless for protecting anything. The
nonces are fixed texts, where the real ones come from the CSPRNG, and the labels are shorter.

:::question
You need to know what a function, a loop and a `std::string` are; see [functions and loops](../basics/programming-2.md) and [classes and calls](../basics/programming-3.md).
:::

The program first runs an honest handshake: each side computes both proofs from the token and the nonces and accepts the
other's. The three breaks follow. Break 1 shows what a client that sends the token puts on the wire. Break 2 guesses a
proof character by character from comparison counts, once against an early-exit comparison and once against a
constant-time one; the counter `g_Examined` stands in for time. Break 3 plays a fake server that gets a client's proof and
guesses a four-digit token with no help from the editor.

```cpp sketch="automation-security-toy.cpp"
// A toy handshake and the three ways to break it. ToyMac is a 64-bit non-cryptographic hash: it only lets the
// protocol run and is never a real message authentication code.
#include <cstdint>
#include <cstdio>
#include <string>

std::string ToyMac(const std::string& key, const std::string& message)
{
	uint64_t hash = 14695981039346656037ull;
	for (const char character : key + "|" + message)
	{
		hash ^= static_cast<uint8_t>(character);
		hash *= 1099511628211ull;
	}
	char text[17];
	std::snprintf(text, sizeof(text), "%016llx", static_cast<unsigned long long>(hash));
	return text;
}

size_t g_Examined = 0; // Stands in for the time a comparison takes

bool EarlyExitEquals(const std::string& left, const std::string& right)
{
	for (size_t index = 0; index < left.size() && index < right.size(); index++)
	{
		g_Examined++;
		if (left[index] != right[index])
			return false;
	}
	return left.size() == right.size();
}

bool ConstantTimeEquals(const std::string& left, const std::string& right)
{
	bool same = left.size() == right.size();
	for (size_t index = 0; index < left.size() && index < right.size(); index++)
	{
		g_Examined++;
		same = same && left[index] == right[index];
	}
	return same;
}

// The attacker knows the proof has 16 hexadecimal digits, and sees only how long each comparison took.
std::string GuessProof(const std::string& expected, bool (*equals)(const std::string&, const std::string&))
{
	std::string guess(16, '0');
	for (size_t position = 0; position < guess.size(); position++)
	{
		size_t bestExamined = 0;
		char bestDigit = '0';
		for (const char digit : std::string("0123456789abcdef"))
		{
			guess[position] = digit;
			g_Examined = 0;
			if (equals(guess, expected))
				return guess; // Accepted: the attacker sees that too
			if (g_Examined > bestExamined)
			{
				bestExamined = g_Examined;
				bestDigit = digit;
			}
		}
		guess[position] = bestDigit;
	}
	return guess;
}

int main()
{
	const std::string token = "6c1f0a9e55d27b3a";
	const std::string clientNonce = "c0ffee00";
	const std::string serverNonce = "5eed1234";
	const std::string serverProof = ToyMac(token, "server" + clientNonce + serverNonce);
	const std::string clientProof = ToyMac(token, "client" + serverNonce + clientNonce);
	std::printf("handshake: client accepts server %d, server accepts client %d\n",
		ConstantTimeEquals(serverProof, ToyMac(token, "server" + clientNonce + serverNonce)),
		ConstantTimeEquals(clientProof, ToyMac(token, "client" + serverNonce + clientNonce)));

	// Break 1: the token travels. Anyone who reads the connection now holds the secret.
	std::printf("break 1: the wire carried token=%s\n", token.c_str());

	// Break 2: an early exit tells how many leading digits of a guess are right.
	const bool early = GuessProof(clientProof, EarlyExitEquals) == clientProof;
	const bool constant = GuessProof(clientProof, ConstantTimeEquals) == clientProof;
	std::printf("break 2: guessed the proof with ==: %d, in constant time: %d\n", early, constant);

	// Break 3: the client proves first, so an impostor that sends any nonce gets a proof to guess against.
	const std::string weakToken = "4821";
	const std::string sample = ToyMac(weakToken, "client" + serverNonce + clientNonce);
	for (int candidate = 0; candidate < 10000; candidate++)
	{
		char text[16];
		std::snprintf(text, sizeof(text), "%04d", candidate);
		if (ToyMac(text, "client" + serverNonce + clientNonce) == sample)
			std::printf("break 3: the impostor found the token %s in %d tries\n", text, candidate + 1);
	}
	return 0;
}
```

1. **Lines 7–18:** the stand-in for HMAC, a 64-bit hash of the key and the message; it is fast and is never safe.
2. **Lines 22–31:** the early exit counts how many characters it looked at before it stopped.
3. **Lines 33–42:** the constant-time loop looks at every character and decides at the end.
4. **Lines 52–63:** the attacker keeps the digit whose comparison looked at the most characters, and stops when a guess is accepted.
5. **Lines 89–96:** with a weak token the fake server tries all 10,000 values on its own.

```text output-of="automation-security-toy.cpp"
handshake: client accepts server 1, server accepts client 1
break 1: the wire carried token=6c1f0a9e55d27b3a
break 2: guessed the proof with ==: 1, in constant time: 0
break 3: the impostor found the token 4821 in 4822 tries
```

The output shows each break working. A token on the wire is read directly. The `==` comparison hands the whole proof to
an attacker who only measures. The client that proves first gives a fake server a sample to attack at leisure.

Be careful about what break 3 shows. The real editor also answers any client nonce with a proof, so a process can
collect a sample from it too. The real defence against guessing away from the editor is the size of the token: a 128-bit token cannot be
searched, while a four-digit one falls at once. The order "server first" removes one source of samples, the client's
own, and the length of the token removes the danger of the other. The toy uses a weak token to make the point visible.

## The real code

The real handshake has the same shape as the toy, with HMAC-SHA256, 128-bit nonces and a long list of ways that a
confused or hostile peer can go wrong. The two halves of the code follow the two halves of the secret's life: the handshake
that proves it, and the files that keep it.

### The handshake

The protocol is specified in a comment in the server's :term[header]{id=header}, in the order a reader needs it. Read the comment before the
code, since the code only does what the comment promises.

```cpp src="Strata/src/Strata/Network/RpcServer.h#L111-L133"
// Every connection starts with a challenge-response handshake in which both sides prove that they know the
// session token, and the token itself never crosses the wire:
//   1. rpc.handshake {"clientNonce", "clientName"?} -> {"serverNonce", "serverProof"}
//      clientName (optional) names the client for people and the activity journal (RpcClientInfo); it proves nothing.
//      serverProof = HMAC-SHA256(token, "strata-server" + clientNonce + serverNonce). The client verifies it
//      before it sends anything else, so it never talks to (or proves anything to) a process that merely took
//      over a dead editor's port.
//   2. rpc.authenticate {"clientProof"} -> {"authenticated": true}
//      clientProof = HMAC-SHA256(token, "strata-client" + serverNonce + clientNonce). The server verifies it
//      before it accepts any other request.
// Nonces are 128-bit values from the system's secure random generator, fresh for every connection and written
// as 32 lower-case hexadecimal characters; proofs are lower-case hexadecimal. Both sides compare proofs in
// constant time, and a connection performs the handshake only once.
class RpcAuthentication
{
public:
	// A fresh nonce (empty if the system's secure random generator fails).
	static std::string GenerateNonce();
	// Exactly 32 lower-case hexadecimal characters.
	static bool IsValidNonce(std::string_view nonce);
	static std::string ComputeServerProof(std::string_view token, std::string_view clientNonce, std::string_view serverNonce);
	static std::string ComputeClientProof(std::string_view token, std::string_view serverNonce, std::string_view clientNonce);
};
```

1. **Lines 113–117:** step 1 carries the client's nonce and an optional name in, and the server's nonce and proof out; the proof is checked by the client before anything else.
2. **Lines 118–120:** step 2 carries the client's proof, which the server checks before it accepts any other request.
3. **Lines 121–123:** the nonce format, the constant-time comparison and the single handshake are stated as rules.
4. **Lines 124–133:** the helper class has four functions and no state: a fresh nonce, a format check and the two proofs.

Now the computing of the proofs. The two functions differ in the label and in the order of the nonces: the server's proof puts
the client's nonce first, and the client's proof puts the server's nonce first. That second difference is a further
barrier to reflection, since swapping the nonces changes the message.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L330-L363"
std::string RpcAuthentication::GenerateNonce()
{
	std::array<uint8_t, c_NonceBytes> bytes = {};
	if (!Platform::GenerateSecureRandom(bytes))
		return {};
	return Crypto::ToHex(bytes);
}

bool RpcAuthentication::IsValidNonce(std::string_view nonce)
{
	// One canonical spelling: with fixed-length nonces, the concatenations in the proofs are unambiguous.
	if (nonce.size() != c_NonceBytes * 2)
		return false;
	return std::all_of(nonce.begin(), nonce.end(), [](char character)
	{
		return (character >= '0' && character <= '9') || (character >= 'a' && character <= 'f');
	});
}

std::string RpcAuthentication::ComputeServerProof(std::string_view token, std::string_view clientNonce, std::string_view serverNonce)
{
	std::string message(c_ServerProofLabel);
	message += clientNonce;
	message += serverNonce;
	return Crypto::ToHex(Crypto::HmacSha256(token, message));
}

std::string RpcAuthentication::ComputeClientProof(std::string_view token, std::string_view serverNonce, std::string_view clientNonce)
{
	std::string message(c_ClientProofLabel);
	message += serverNonce;
	message += clientNonce;
	return Crypto::ToHex(Crypto::HmacSha256(token, message));
}
```

1. **Lines 332–335:** 16 bytes from the system's secure random generator become 32 hexadecimal digits; a failure returns an empty string, which callers treat as an error.
2. **Lines 341–346:** the format check accepts exactly 32 characters from `0-9` and `a-f`, so there is one spelling per value.
3. **Lines 351–354:** the label, the client's nonce and the server's nonce are glued and passed to `Crypto::HmacSha256` with the token as key.
4. **Lines 359–362:** the client's proof uses the other label and the nonces in the other order.

The server's side of the first step is in `HandleHandshakeMessage`. A connection that has not yet proven itself may send
only the two handshake requests, in order. Anything else ends the connection through the local helper `reject`, which
logs a warning at a limited rate, sends an error when a reply is possible and closes. This is the answer to a hostile
local process, or a web page sending a web request to the port: it gets one error and a closed socket.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1069-L1113"
if (connection.ServerNonce.empty())
{
	// Step 1: the client's nonce in, the server's nonce and its proof of the token out.
	if (method != c_RpcHandshakeMethod)
	{
		reject(validation.Id, JsonRpc::ErrorCode::Unauthorized, "Authentication required: the first request must be rpc.handshake", true);
		return;
	}
	const std::string* clientNonce = FindString(params, "clientNonce");
	if (!clientNonce || !RpcAuthentication::IsValidNonce(*clientNonce))
	{
		reject(validation.Id, JsonRpc::ErrorCode::InvalidParams, "Expected params {\"clientNonce\": 32 lower-case hexadecimal characters}", true);
		return;
	}
	// The client's name is optional (clients from before it existed send none) and only shown, never trusted.
	if (params.is_object() && params.contains("clientName"))
	{
		const std::string* clientName = FindString(params, "clientName");
		if (!clientName)
		{
			reject(validation.Id, JsonRpc::ErrorCode::InvalidParams, "\"clientName\" must be a string", true);
			return;
		}
		connection.ClientName = SanitizeRpcClientName(*clientName);
	}
	std::string serverNonce = RpcAuthentication::GenerateNonce();
	if (serverNonce.empty())
	{
		reject(validation.Id, JsonRpc::ErrorCode::InternalError, "The server's random number generator failed", true);
		return;
	}
	// Each nonce is used once per connection; a client echoing the server's nonce back (or one that
	// happens to match) could make one side's proof stand in for a fresh one.
	if (serverNonce == *clientNonce)
	{
		reject(validation.Id, JsonRpc::ErrorCode::InvalidParams, "The nonces of a handshake must differ", true);
		return;
	}

	connection.ClientNonce = *clientNonce;
	connection.ServerNonce = std::move(serverNonce);
	const std::string serverProof = RpcAuthentication::ComputeServerProof(Specification.AuthToken, connection.ClientNonce, connection.ServerNonce);
	Send(connection, JsonRpc::MakeResult(validation.Id, nlohmann::json { { "serverNonce", connection.ServerNonce }, { "serverProof", serverProof } }));
	return;
}
```

1. **Lines 1072–1076:** the first request must be `rpc.handshake`, or the connection ends.
2. **Lines 1077–1082:** the client's nonce must have exactly the fixed format.
3. **Lines 1083–1093:** the optional name is cleaned, and a name that is not a string is an error.
4. **Lines 1100–1106:** a server nonce equal to the client's is refused, the check against reflection.
5. **Lines 1108–1112:** the nonces are stored on the connection, the proof is computed, and the reply goes out; the connection waits for step 2.

Step 2 checks the client's proof against the proof the server computes itself. The comparison is the constant-time one.
Only after it succeeds does the server look at the client limit, and only then does it trust the connection.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1131-L1152"
const std::string expectedProof = RpcAuthentication::ComputeClientProof(Specification.AuthToken, connection.ServerNonce, connection.ClientNonce);
if (!Crypto::ConstantTimeEquals(*clientProof, expectedProof))
{
	reject(validation.Id, JsonRpc::ErrorCode::Unauthorized, "Authentication failed: the proof does not match the session token", true);
	return;
}

if (CountConnections(true) >= Specification.MaxClients)
{
	uint64_t suppressed = 0;
	if (RejectionWarnings.Allow(suppressed))
		ST_CORE_WARN("RpcServer: rejecting client {}, the limit of {} clients is reached{}", connection.Id, Specification.MaxClients, DescribeSuppressed(suppressed));
	Send(connection, JsonRpc::MakeError(validation.Id, JsonRpc::ErrorCode::ServerBusy, fmt::format("The server accepts at most {} clients", Specification.MaxClients)));
	BeginClose(connection, c_ErrorCloseLinger);
	return;
}

connection.Authenticated = true;
connection.ConnectedAt = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
connection.ClientNonce.clear();
connection.ServerNonce.clear();
connection.Reader.SetMaxMessageSize(Specification.MaxMessageSize);
```

1. **Lines 1131–1136:** the expected proof is computed from the stored nonces, and a difference found in :term[constant time]{id=constant-time} ends the connection.
2. **Lines 1138–1146:** a server with every client slot taken refuses the client with a busy error, after the proof, so a peer that has not proven itself cannot learn the count.
3. **Lines 1148–1152:** the nonces are cleared, since they served their purpose, and the message size limit rises from the small pre-authentication limit to the server's normal one.

The last item is a hint at the limits. Before authentication, a connection may send messages of at most 4,096 bytes. The
server holds at most 16,384 bytes of output for it, and the whole handshake must finish within 5 seconds of the accept.
The limits after authentication and the :term[backpressure]{id=backpressure} are the topic of [the server](../automation/rpc-server.md). Here the point is why the
small limits come first: a peer that has not proven itself can be anyone, so it may take almost nothing.

The server also holds at most 8 pending connections, the ones that have not yet proven themselves. What happens when a ninth arrives?
The choice is made by a pure function that takes only the facts of each pending connection and gives the
index to drop, so it can be tested without sockets.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L550-L563"
std::optional<size_t> ChoosePendingConnectionToEvict(std::span<const PendingConnectionState> pending)
{
	std::optional<size_t> oldestStarted;
	for (size_t index = 0; index < pending.size(); index++)
	{
		if (!pending[index].Polled)
			continue; // Never evicted before it had a chance to send
		if (!pending[index].HandshakeStarted)
			return index;
		if (!oldestStarted)
			oldestStarted = index;
	}
	return oldestStarted;
}
```

1. **Lines 555–556:** a connection that has not been through a poll yet had no chance to send, so it is never chosen.
2. **Lines 557–558:** the oldest connection that never started the handshake goes first.
3. **Lines 559–562:** when every candidate has started, the oldest of them goes; with no candidate, the function returns nothing and the newcomer is turned away.

The rule has two aims. A program that opens eight silent connections must not lock out the editor's own client, and an
honest client in the middle of a handshake should not be dropped if a silent one can be. The test `Connections that hoard pending slots cannot lock out a client` checks the first aim.

The client's side is `AuthenticateLocked`. The excerpt starts after the client sent its nonce and received the
reply. It checks the server's proof before it does anything else.

```cpp src="Strata/src/Strata/Network/RpcClient.cpp#L91-L106"
// The server proves that it knows the token before the client proves anything in return: a process that
// took over the port of an editor that exited cannot, and gets nothing it could use. A server nonce equal to
// the client's would let a reflected proof pass, so it is refused as well.
const nlohmann::json& value = handshake.GetValue();
const auto serverNonce = value.is_object() ? value.find("serverNonce") : value.end();
const auto serverProof = value.is_object() ? value.find("serverProof") : value.end();
const bool proven = serverNonce != value.end() && serverNonce->is_string() && serverProof != value.end() && serverProof->is_string()
	&& RpcAuthentication::IsValidNonce(serverNonce->get_ref<const std::string&>()) && serverNonce->get_ref<const std::string&>() != clientNonce
	&& Crypto::ConstantTimeEquals(serverProof->get_ref<const std::string&>(), RpcAuthentication::ComputeServerProof(token, clientNonce, serverNonce->get_ref<const std::string&>()));
if (!proven)
{
	FailLocked(JsonRpc::ErrorCode::Unauthorized, "Authentication failed: the server could not prove that it knows the session token, so it may not be the editor", true);
	return false;
}

const std::string clientProof = RpcAuthentication::ComputeClientProof(token, serverNonce->get_ref<const std::string&>(), clientNonce);
```

1. **Lines 94–96:** the reply must be an object with a server nonce and a server proof.
2. **Lines 97–99:** the nonce must have the fixed format and differ from the client's, and the proof must equal the one the client computes, compared in constant time.
3. **Lines 100–104:** if anything is wrong, the client stops with a message that says the server may not be the editor.
4. **Line 106:** only now does the client compute its own proof, and `rpc.authenticate` goes out.

What does the order buy? A process that took over a dead editor's port sees the client's nonce and one name, and then the
client hangs up. It gets no client proof. The test `The client refuses a server that cannot prove it knows the token` pins this: the
client sends exactly one line, never the token, and closes.

What does it not buy? The editor itself answers a handshake from any client. And the exchange proves who the two ends are,
but it does not hide the connection afterwards: the proofs stop a fake server, and they do not keep the requests secret.
That is acceptable for a loopback link between two programs of one user. It is a cost to remember if a future
design lets the link leave the machine, which the loopback rule forbids today.

Finally, two checks in `Start` turn two of the rules into code. A bind address that is not loopback fails, and an empty
token fails. Each failure has an error that names the reason.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1434-L1438"
if (!IsLoopbackAddress(specification.BindAddress))
	return fail(fmt::format("refusing to listen on '{}': only loopback addresses (127.0.0.0/8 or ::1) are allowed", specification.BindAddress));
if (specification.AuthToken.empty())
	return fail("refusing to start without an authentication token");
if (!m_Impl->Listener.Listen(specification.BindAddress, specification.Port))
```

The code stops before it opens the socket. A refused start leaves nothing listening.

### Files that keep the secret

The session file's content is the :term[struct]{id=struct} `EditorSessionInfo`: the process id, the process start time, the address, the
port, the token, the project path, the editor's version, whether it is headless and a start timestamp. `FromJson`
accepts a file only with a valid process id and port and a non-empty token. A session without a token could not prove
anything, so it counts as no session.

The file is named `<pid>.json` and lives in the `Sessions` folder inside the `Strata` folder of your account's data. For tests, the :term[environment variable]{id=environment-variable} `STRATA_SESSION_DIR`
names another private folder. In both cases `GetSessionDirectory` calls `EnsurePrivateDirectory`, and when no folder is
available it fails with a message. It never falls back to a shared place.

The file is read with `Platform::ReadTrustedFile`. It opens the file once and, on the same handle that reads it, checks that
the file is a regular file, owned by the current user and not open to change by others. The read stops at 65,536 bytes.
A link, a pipe or a device is rejected without waiting. Nothing can swap the file between the check and the read, because there is no gap.

```mermaid caption="The session files: the private folder holds the full session, the project folder holds a pointer without port or token, and trust runs from the pointer to the file." alt="A diagram with two folders. The private folder in the user's data holds a session file with process id, port, token and start time. The project folder holds a pointer with process id, project name, version, headless flag and start timestamp, and no port or token. An arrow from the pointer to the session file says that it only chooses which file to read. A second arrow from the session file to the running process says that the start time must match."
flowchart TB
    subgraph Private["Private folder: owner only, no shared fallback"]
        F["pid.json: pid, port, token, start time"]
    end
    subgraph Project["Project folder: shared, untrusted"]
        Q["EditorSession.json: pid, project, version, headless, start"]
    end
    Q -->|"only chooses which file to read"| F
    F -->|"start time must match the live process"| R["Running editor process"]
```

The pointer is read by `ReadProjectSession`. It reads the pointer, takes the process id from it and nothing else, and
then asks the per-user file for everything. The file must hold the same process id and name the same project, and its
process must be running with the recorded start time.

```cpp src="Strata/src/Strata/Network/EditorSession.cpp#L375-L391"
std::optional<EditorSessionInfo> EditorSession::ReadProjectSession(const std::filesystem::path& projectDirectory, const std::filesystem::path& sessionDirectory)
{
	const std::optional<nlohmann::json> pointer = ReadJsonFile(GetProjectSessionFilePath(projectDirectory));
	if (!pointer)
		return std::nullopt;
	const std::optional<uint32_t> processId = GetProcessId(*pointer);
	if (!processId)
		return std::nullopt;

	// Everything the connection needs comes from the per-user file; the pointer only chose which one.
	std::optional<EditorSessionInfo> session = ReadSessionFile(GetSessionFilePath(sessionDirectory, *processId));
	if (!session || session->ProcessId != *processId || !IsSameProject(session->ProjectPath, projectDirectory))
		return std::nullopt;
	if (!IsSessionProcessRunning(*session))
		return std::nullopt;
	return session;
}
```

1. **Lines 377–382:** the pointer is read, and the only value taken from it is a process id.
2. **Lines 384–387:** the per-user file is read through the trusted read, and its process id and project must agree with what the pointer claims.
3. **Lines 388–390:** a file whose process is not running with the recorded start time is not used.

The question "is this process still the editor?" is answered by `GetSessionProcessState`, which compares the id and the
start time.

```cpp src="Strata/src/Strata/Network/EditorSession.cpp#L393-L404"
SessionProcessState EditorSession::GetSessionProcessState(const EditorSessionInfo& session)
{
	if (!Platform::IsProcessAlive(session.ProcessId))
		return SessionProcessState::Exited;

	// The start time tells the process that wrote the session apart from a later one that reuses its id. Only a
	// known start time that differs proves the id was reused; an unknown one proves nothing either way.
	const std::optional<uint64_t> startTime = Platform::GetProcessStartTime(session.ProcessId);
	if (!startTime || session.ProcessStartTime == 0)
		return SessionProcessState::Unverifiable;
	return *startTime == session.ProcessStartTime ? SessionProcessState::Running : SessionProcessState::Exited;
}
```

1. **Lines 395–396:** an id that is not alive means the process exited.
2. **Lines 398–402:** an unknown start time, on either side, proves nothing, so the state is `Unverifiable`.
3. **Line 403:** a known start time that matches means running; one that differs means another process took the id.

`Unverifiable` is not `Exited`. That one rule keeps a client from deleting the session of a live editor that only failed
to report its start time. The editor warns in its log when it cannot read its own start time, since clients will skip
such a session.

When `FindSessions` meets a file whose process has exited, it removes the file with `RemoveStaleSessionFile`. A plain
check followed by a delete would race with a new editor that has the same process id and writes its own file at the
same path. The function takes the file aside with one rename to a random name, judges it again and puts it back if it
is not stale.

```cpp src="Strata/src/Strata/Network/EditorSession.cpp#L315-L342"
bool EditorSession::RemoveStaleSessionFile(const std::filesystem::path& path)
{
	// The file was judged stale from contents read earlier, and a new editor that reuses the process id may have
	// written its own session at the same path since. So the file is taken out of place atomically and judged
	// again: only a file that is still stale is deleted; anything else goes back (unless an even newer session
	// has taken the path in the meantime, which then wins). The taken name does not end in ".json", so even if
	// this process dies in between, no client ever reads it as a session.
	std::array<uint8_t, 8> suffix = {};
	if (!Platform::GenerateSecureRandom(suffix))
		return false;
	std::filesystem::path takenFile = path;
	takenFile += FileSystem::FromUTF8(".stale-" + Crypto::ToHex(suffix));

	std::error_code error;
	std::filesystem::rename(path, takenFile, error);
	if (error)
		return false; // Already removed (e.g. by another client), or held open by a reader

	const std::optional<EditorSessionInfo> session = ReadSessionFile(takenFile);
	if (!session || GetSessionProcessState(*session) != SessionProcessState::Exited)
	{
		if (!Platform::RenameNoReplace(takenFile, path))
			std::filesystem::remove(takenFile, error);
		return false;
	}
	std::filesystem::remove(takenFile, error);
	return !error;
}
```

1. **Lines 322–326:** the aside name is the old one plus `.stale-` and a random suffix. It does not end in `.json`, so if this process dies here, no client reads the aside file as a session.
2. **Lines 328–331:** the rename is the atomic step; if it fails, another client took the file first, or a reader holds it open, and this call does nothing.
3. **Lines 333–339:** the file is read again from its new name. A file that is no longer stale returns with `RenameNoReplace`; when a newer file already took the path, the newer one wins and the aside file is dropped.
4. **Lines 340–341:** only a file that is still stale after the second judgement is deleted.

```mermaid caption="Two processes and one stale file: the cleaner takes the file aside and judges it again, and a new editor's file at the old path survives." alt="A sequence diagram with a cleaner process, the folder and a new editor. The cleaner reads a stale file. The new editor writes a fresh file at the same path. The cleaner renames the path to a random aside name and reads it again. The cleaner finds that the file is no longer stale, restores it with a rename that never replaces, and leaves the folder as the new editor wrote it."
sequenceDiagram
    participant Cleaner
    participant Folder
    participant NewEditor
    Cleaner->>Folder: read pid.json, judge: stale
    NewEditor->>Folder: write pid.json (the id was reused)
    Cleaner->>Folder: rename pid.json to pid.json.stale-random
    Cleaner->>Folder: read the aside file, judge again: running
    Cleaner->>Folder: RenameNoReplace back to pid.json
    Note over Folder: the new editor's session survives
```

The pointer has the same race and the same cure. `RemoveProjectPointer` takes the pointer aside and reads it. It deletes
the pointer only when the pointer still names the process that is shutting down. A pointer written by another editor
returns to its place, or is dropped when an even newer one has appeared.

One last place in the system holds the token: the :term[command line]{id=terminal-command}. StrataCLI accepts `--token`, and its help text says to
avoid it. Other processes can read the command line of a running program, so a token passed that way is no longer
private. The preferred way is the environment variable `STRATA_EDITOR_TOKEN`, and the normal way needs neither,
because a discovered session provides its own token.

## A worked example

Here is one handshake computed by hand, with the token and the client nonce of a test. The test `The handshake proves the token both ways without sending it` computes each proof again with `Crypto` and checks that the server sent it.

:::example[One handshake, with numbers]
The token is `0123456789abcdef0123456789abcdef`, the test's token. The client's nonce is `00112233445566778899aabbccddeeff`.
Suppose the server picks `ffeeddccbbaa99887766554433221100`. The nonces differ, and each has 32 digits from the
allowed set, so both pass the format check.

The server's message is the label `strata-server` (13 bytes), then the client's nonce (32), then the server's (32):
77 bytes in all. HMAC-SHA256 with the token as key gives, in hexadecimal,
`4fce8b83f0031c08a2eb33e41e27fbe8ead57895921a9e58675dc70972230a5c`. That is the server's proof, 64 digits for 32 bytes.

The client checks it. It computes the same HMAC from its own copy of the token. The two match, so the editor knows
the token.

The client then builds its message, with the label `strata-client` and the nonces in the other order: the
server's first, then its own. The proof is `ad9ee935cf4ae515fcfdd14765a006d2a3db0157d3fa016031db660bf389b157`. The server
computes the same and compares in constant time. They match: it answers `{"authenticated": true}`.

Two small checks show the design at work. Put the client's label with the server's nonce order and the digits are
`8ef3f609…`, which is neither proof. So a server proof returned as a client proof is refused. And nothing in either message
shows the token: an observer sees two nonces and two 64-digit proofs.
:::

Now the fake server. A program has taken the port of an editor that exited. The client connects and sends `rpc.handshake`
with its nonce. The fake server knows no token, so it can reply with a made-up server nonce and a proof of 64 zeros. It
can send no proof at all, or a proof recorded from the real editor for another client nonce.

The client computes its own expected proof, sees that the strings differ and stops with the message "the server could
not prove that it knows the session token, so it may not be the editor". The fake server saw one line, the handshake
request. It never received the token or a client proof. A fourth try fails too: the fake server sends the client's own
nonce back as the server nonce, with a proof that is valid for that pair, and the client refuses equal nonces.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Endpoint the operating system protects (local socket file, named pipe) | Many database servers and container tools | No secret on the wire and the system's own access check | One channel type per system; web pages and some tools could not connect at all |
| A bearer token in each request | Web programming interfaces | A very small protocol | The token crosses the wire; a wrong peer or a recorded request can use it |
| Certificates on both ends, as in secure web connections | Services between companies | Traffic that others cannot read, and a strong identity for both ends | A key store to create, hand out and renew, for a link that never leaves the machine |
| Prove only the client | Simple password schemes | Half the code | A client talks to any program on a dead editor's port |
| A shared password typed by a person | Remote desktops | Nothing stored in a file | A weak secret, typed again for every tool, and no way for agents to start |

Each row is a real trade. The choice of Strata rests on one fact: a local, short-lived program whose clients are scripts and
agents. A token in a private file costs a user nothing to manage, and the handshake costs two messages. The enemy, a hostile local
program or web page, is met without a key store. The price is the sum of the rules above: eleven rules to keep, and no secrecy
for the traffic beyond the machine's own boundary.

## How it is tested

Two suites hold the model. `Network.RpcServer` drives the real server with a raw socket and with the real client:

- `The handshake proves the token both ways without sending it` computes both proofs again, independently, and checks that every connection gets a fresh server nonce.
- `A recorded client proof is refused on another connection` replays a recorded proof with the same client nonce and expects an authentication error and a closed connection.
- `The client refuses a server that cannot prove it knows the token` runs a fake server in four forms: no proof, a wrong proof, a recorded proof and a reflected nonce.
- `Connections that do not authenticate in time are closed` checks the deadline, with and without the first step done.
- `Connections that hoard pending slots cannot lock out a client` and `The pending connection to evict is the oldest that had a chance to send` check the :term[eviction]{id=eviction}.
- Names are covered in the suite `Network.RpcPresence`, by `Clients may name themselves in the handshake; the server lists them and tells handlers`.

`Network.EditorSession` covers the files, with real helper processes:

- `A session whose process id now belongs to another process is stale` makes an id taken by another process and a session that cannot be verified.
- `A stale session file is deleted only while it is still stale` plays the race of the picture above.
- `Session files are written owner-only, found and removed` and `The project pointer is not trusted` check the private files and the pointer.
- `A session directory reached through a symbolic link is refused` and `Without a per-user directory, sessions are refused rather than shared` check the folder rules.

Run them with `StrataTests.exe --test-suite=Network*` from the build's binary folder, or `ctest --preset windows-debug -R Network`, in the chosen
configuration. The tests need no :term[graphics card]{id=gpu}.

## Changing it safely

The first extension point is the handshake. Any change to what is proved or in what order is a change of protocol:
a client of the old version meets a server of the new one. The labels and the order of the nonces are part of the protocol.
A change keeps both proofs distinct, the nonces fixed in length and the server first, and it extends the cases of `Network.RpcServer`
with an attack for each new field.

The second is the files. A change to how session files are written, found or removed keeps three properties. The file
stays owner-only in a private folder with no shared fallback. Every read goes through the trusted read, never through a
check followed by a normal read. And no code deletes a file that another process may have replaced since it looked: it
takes the file aside, judges it again, and puts it back with `RenameNoReplace` when it is not stale.

:::rule[Automation rules in `AGENTS.md`]
`AGENTS.md` keeps four rules for automation: loopback addresses only, a token for every server, a token that never
travels, and a pointer that holds no secret. A change that relaxes one needs a new threat model first, because the other
rules assume it. Commands reach agents by registration alone, so a new command changes none of this page.
:::

Before a change leaves your machine, check three things. Both suites, `Network.RpcServer` and `Network.EditorSession`,
pass. A new attack has a test that fails without its fix. No new log line holds a token or a proof.

## Summary

- A loopback port is open to every local process and every web page, so the editor trusts only holders of a secret token. The token is 128 random bits, made once per editor run.
- The handshake has two steps. The server proves it knows the token first, with HMAC-SHA256 over a label and both nonces, and the client proves it second. Fresh nonces stop replay, the labels and the check for equal nonces stop reflection, and the token never travels.
- Proofs are compared in constant time because an early exit leaks how many characters matched, and the nonces and the token come from the system's secure random generator because a predictable value could be guessed.
- A session file with the token lives in a private folder and the project pointer holds neither port nor token. The pointer only chooses a file, the file's process id and start time must match a running process, and a process whose identity cannot be checked is skipped and never deleted.
- A stale file is taken aside with one rename, judged again, and deleted only if it is still stale; otherwise `RenameNoReplace` puts it back. No code checks a shared file and then deletes it.

## Check yourself

1. A page in a web browser sends the bytes `GET / HTTP/1.1` to the editor's port. What happens, and why does the page gain nothing?

   :::answer{tests="threat-model"}
   The first message is not the JSON of `rpc.handshake`, so the server answers with an error, logs a warning at a limited
   rate and closes the connection. The page cannot continue to step 2, since it does not know the token and cannot compute a
   proof. Loopback let it connect; the handshake is what refuses it.
   :::

2. In the real protocol, which of these statements about the client's proof is right? (a) It is the HMAC of the token and the client's nonce alone. (b) It is the HMAC, keyed by the token, of `strata-client`, the server's nonce and the client's nonce. (c) It is the token, written in hexadecimal.

   :::answer{tests="handshake"}
   (b). The label separates the two directions and both nonces tie the proof to one connection. (a) lacks the label and the
   server's nonce, so a proof could serve on other connections or come back reflected. (c) would put the token on the wire, which the
   design forbids.
   :::

3. A recorded client proof is sent on a new connection with the same client nonce. Why does the server refuse it?

   :::answer{tests="handshake"}
   The server picks a new random nonce for every connection. The recorded proof was computed from the old server nonce, so
   it differs from the proof the server now expects, and the constant-time comparison fails. A nonce is a number used once:
   its freshness is what makes a recording worthless.
   :::

4. An attacker times how long the server takes to reject proofs. With `==` and 64 hexadecimal digits, how many tries find a full proof, and why does the constant-time comparison stop it?

   :::answer{tests="compare-and-random"}
   At most 16 digits times 64 positions is 1,024 tries, one position at a time, against up to 16^64 tries without the timing. The
   constant-time comparison examines every character whatever the outcome, so the time no longer shows how many
   leading digits matched, and the attacker is back to guessing the whole proof.
   :::

5. A session file for process 4120 holds the start time 1000. Another process now has the id 4120, with start time 2500. What state does the client assign, and what does it do with the file? What changes if the file's start time is 0?

   :::answer{tests="session-files"}
   The id is alive and the start times differ, so the state is exited: the session is stale, and the client removes the
   file by the safe path. With start time 0 the start time is unknown, so the state is `Unverifiable`: the client skips the
   session and keeps the file, because it may belong to a running editor.
   :::

6. Why does the code rename a stale file aside before it deletes it, instead of deleting it after the check?

   :::answer{tests="race-safe-removal"}
   Between the check and the delete a new editor with the same id may write its own file at the same path. Deleting would
   destroy a live secret. The rename takes the file out of the shared place in one atomic step. The second judgement then
   sees a file that nobody else can replace, and a file that is no longer stale returns with `RenameNoReplace`.
   :::

## Exercises

1. **Basic.** Trace it yourself: find which proof each call of `Crypto::HmacSha256` and `Crypto::ConstantTimeEquals` in `Strata/src/Strata/Network` computes or compares, and which side runs it. Then put a breakpoint in `RpcClient::AuthenticateLocked` while `StrataCLI status` runs and see that the server's proof is checked before the client sends its own.

   :::answer[Worked solution]{tests="handshake"}
   A search for `Crypto::HmacSha256` finds the two proof functions in `RpcServer.cpp`, `ComputeServerProof` near line 354 and
   `ComputeClientProof` near line 362. Both sides call them: the server computes the server proof to send and the
   client proof to expect, and the client does the reverse. A search for `Crypto::ConstantTimeEquals` finds the server's
   check of the client proof in `HandleHandshakeMessage` (near line 1132) and the client's check of the server proof
   in `RpcClient::AuthenticateLocked` (near line 99). In the debugger, the check at line 99 runs before the call that
   sends `rpc.authenticate` at line 107, and no other call sends a proof first.
   :::

2. **Medium.** Write a raw client in Python that performs the handshake by hand against a running headless editor, calls `rpc.listMethods`, and then sends a plain web request on a fresh connection. Predict what you see in each case first.

   :::answer[Worked solution]{tests="handshake"}
   Read the port and the token from the editor's session file, in the `Sessions` folder inside the `Strata` folder of your
   account's data. The script below sends one line of JSON per request and reads one line per answer. It stops with an
   assertion error if the server's proof is wrong.

   ```python
   import hashlib, hmac, json, os, socket

   def proof(token, label, first, second):
       message = (label + first + second).encode()
       return hmac.new(token.encode(), message, hashlib.sha256).hexdigest()

   def call(stream, number, method, params):
       stream.write(json.dumps({"jsonrpc": "2.0", "id": number, "method": method, "params": params}) + "\n")
       stream.flush()
       return json.loads(stream.readline())

   port, token = 12345, "the token from the session file"
   stream = socket.create_connection(("127.0.0.1", port)).makefile("rw", newline="\n")
   nonce = os.urandom(16).hex()
   reply = call(stream, 1, "rpc.handshake", {"clientNonce": nonce})["result"]
   assert reply["serverProof"] == proof(token, "strata-server", nonce, reply["serverNonce"])
   print(call(stream, 2, "rpc.authenticate", {"clientProof": proof(token, "strata-client", reply["serverNonce"], nonce)}))
   print(call(stream, 3, "rpc.listMethods", {})["result"])
   ```

   1. **Lines 3–5:** a proof is the HMAC, keyed by the token, of the label and the two nonces in the order the label names.
   2. **Lines 7–10:** one request is one JSON line out and one JSON line in.
   3. **Lines 14–16:** a fresh 16-byte nonce goes out as 32 hexadecimal digits, and the reply is checked before anything else is sent.
   4. **Lines 17–18:** the client proof comes second, then the table of methods.

   The first `print` shows the whole answer, whose result holds `'authenticated': True`, and the second shows the method table. On a fresh
   connection, send the line `GET / HTTP/1.1` instead. The server answers with the error `Parse error: the message is not valid JSON` and closes the connection, because
   only the two handshake requests are allowed first.
   :::

3. **Medium.** Build a fake server on a stale port, as the fake server of the example, that relays what it receives to a real editor and returns the real answers. Predict how far the client gets, and compare your result with the test `The client refuses a server that cannot prove it knows the token`.

   :::answer[Worked solution]{tests="handshake"}
   Listen on the port of an editor that has exited, and forward the client's `rpc.handshake` to a live editor. The live
   editor answers with a proof for the nonce you forwarded, so the client accepts it and sends its own proof, and you relay
   that too. The relay works only while a live editor answers and your program sits in the middle of the connection.

   The result shows what the handshake promises. It proves that the answering side knows the token, and it does not
   protect a connection from a process that relays every message. Once the live editor is gone, the same fake server fails
   at the first check, as in the test: one line received, no token, a closed connection.
   :::

4. **Hard.** Write a test in which a new process takes the process id's path between the read and the delete of a stale file. Which functions do you call, and what must the test assert?

   :::answer[Worked solution]{tests="race-safe-removal"}
   Copy the shape of `A stale session file is deleted only while it is still stale`. Create a temporary session
   folder and a live helper process. Write a stale session at the path of the helper's id, by giving it a start time one
   too high.

   Before calling `EditorSession::RemoveStaleSessionFile(path)`, write a second session at the same path with the
   helper's true start time, as the new editor would. Call the function and assert three things. It returns false, the file
   at the path still holds the new session (its port is the new one), and the folder holds exactly one entry, so no
   aside file is left. Then write the stale file again, call the function and assert it returns true and the path is gone.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Network/RpcServer.h` and `RpcServer.cpp`: `RpcAuthentication`, `HandleHandshakeMessage`, the pre-authentication limits, the eviction and the checks of `Start`.
- `Strata/src/Strata/Network/RpcConnectionLimits.h`: `ChoosePendingConnectionToEvict`.
- `Strata/src/Strata/Network/RpcClient.cpp`: `AuthenticateLocked`.
- `Strata/src/Strata/Network/EditorSession.h` and `EditorSession.cpp`: the session file, the project pointer, process state and the safe removal.
- `Strata/src/Strata/Core/Crypto.h` and `Strata/src/Strata/Core/Platform.h`: the hash, `HmacSha256`, `ConstantTimeEquals`, `GenerateSecureRandom`, the private-file functions and `RenameNoReplace`.
- `StrataEditor/src/Editor/EditorAutomation.cpp`: where the editor makes the token, starts the server and writes and removes the session files.
- `StrataCLI/src/CLI/CliApplication.cpp`: `--token` and `STRATA_EDITOR_TOKEN`.
- `StrataTests/src/Network/`: `RpcServerTests.cpp` and `EditorSessionTests.cpp`.

## Further reading

- RFC 2104, "HMAC: Keyed-Hashing for Message Authentication": the definition of the construction. Advanced.
- RFC 4231, "Identifiers and Test Vectors for HMAC-SHA-224, HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512": the values that implementations are tested against. Advanced.
- The OWASP "Cryptographic Storage" and "Authentication" cheat sheets: practical rules for secrets, random numbers and comparisons. Intermediate.
- Paul Kocher, "Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems" (1996): the paper that showed how time leaks a secret. Advanced.
