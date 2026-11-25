---
id: automation/json-rpc
title: "Sockets, framing and JSON-RPC"
description: "How the command line client and the editor, two programs with no shared memory, exchange requests as lines of JSON over a loopback socket."
kind: concept
size: L
tracks: [E]
needs: [basics/data-formats, basics/threads, core/platform, automation/agents]
time: 80
learn:
  - id: choose-channel
    text: choose a way for two processes to talk and explain why Strata uses TCP on the loopback address
  - id: socket-life
    text: explain how a listener, a connection, a timeout and a half-close behave in Strata's socket layer
  - id: framing
    text: explain why a line break is a safe message boundary in Strata and what the line reader does with chunks
  - id: json-rpc
    text: trace a request and its answer through JSON-RPC 2.0 and name the error codes Strata uses
  - id: error-kinds
    text: compare a transport error with a command's failure and say why request ids exist
since: 0.3.0
status: final
---

You type `StrataCLI call entity.create` in a terminal. A second later the editor, a different program, has a new entity in its scene, and your terminal prints the identifier of that entity. No shared variable was involved: the two programs run in two processes, and each process has its own memory that the other cannot read. Something carried your request from one to the other, and something carried the answer back.

This page follows that something from the bottom. It starts with the :term[bytes]{id=byte} that cross between the processes, then cuts them into messages, and ends with the rules that make a message a request or an answer. At the end you can read the traffic between the :term[command line]{id=terminal-command} and the editor and say whether a failure came from the road or from the command.

## Two processes share nothing, so something must carry the bytes

Suppose you must build the carrier yourself. The command line knows what it wants: an entity named `Crate`. The editor knows how to make one, because it owns the scene. The first needs a way to say "create an entity", and the second needs a way to say "done, here is its identifier".

The first idea of most beginners is a file. The command line writes `request.txt`, the editor reads it, does the work and writes `answer.txt`. This works on a quiet day and fails in three ways.

- The editor must look at the file again and again. Looking once a second makes every answer up to a second late; looking a thousand times a second wastes work while nothing happens.
- Two programs use one file at the same time. The editor may read half of a request that is still being written, and nothing tells it that half is not all.
- Nobody knows when a file may be deleted. A second client that writes `request.txt` while the editor answers the first one destroys the first request.

The second idea is a channel that the :term[operating system]{id=operating-system} provides: the sender writes bytes into one end, and the receiver reads them from the other end. This removes the polling and the half-written file. It leaves a trap. Many beginners assume that when the sender writes one message, the receiver reads that one message. For the channel Strata uses, that assumption is wrong, and a later section shows the numbers.

## Four ways for processes to talk

An operating system offers several carriers. They differ in who may use them, how fast they are and how much code each system needs.

A **pipe** is a one-way channel from one program to another, such as the `|` of a terminal. The standard streams of a program are pipes when a parent starts a child and connects them. Only the parent and the child can use them, because no other program has a name to find them by. The page on [tools](../basics/tools.md) introduces them.

Linux and macOS also offer a socket that is named by a path in the file system, and Windows offers named pipes with a name in a special space. Any program that knows the name can connect. The two systems use different calls and different permission rules, so one program needs two code paths.

The same protocol that carries web pages can also run inside one machine, over an address that never leaves it. All three systems that Strata supports offer this with the same ideas, so one code path serves all of them.

:term[Shared memory]{id=shared-memory} lets two processes ask the operating system to show the same pages of memory in both. It is the fastest way, because nothing is copied. It is also the hardest, because the programs must agree on locks and layouts, and a crash in the middle of a write leaves broken data for the other side.

| Carrier | Who can connect | Speed | Code for three systems | Fit for editor :term[automation]{id=automation} |
| --- | --- | --- | --- | --- |
| Standard streams | A parent and its child | High | One path | Only when a client starts the program |
| Local socket or named pipe | Any program that knows the name | High | Two paths | Possible, with two sets of rules |
| Network protocol on the loopback address | Any program on the machine that knows the port | Good | One path | Yes |
| Shared memory | Any program that knows the name | Highest | Several paths | No: locks, layouts and crash damage |

## Strata uses TCP on loopback, and standard streams for one client

Strata's editor listens on a port of the loopback address, and `StrataCLI`, the test programs and every other client connect to it. The protocol is the transmission control protocol (TCP), explained below. One code path works on Windows, Linux and macOS, and a client needs no parent relation with the editor, so it can connect a day after the editor started.

:::why[Why not standard streams for everything?]
A pipe needs a parent. The editor is started by a person or a script, and a client that comes later has no pipe to it. The one place where a client starts the program itself is the Model Context Protocol (MCP): an artificial intelligence (AI) tool launches `StrataCLI mcp` as its child and talks to it over the child's standard streams. Then `StrataCLI` is the server of the tool and a client of the editor at once. The page on [MCP](../automation/mcp.md) tells that story.
:::

The choice has a price. TCP adds copies and a design made for unreliable networks, so it is slower than shared memory. A port is also open to every program on the machine, not only to the ones you intend; the page on [security](../automation/security.md) says what Strata does about that.

```mermaid caption="The command line and the editor are two processes with separate memory; a TCP connection on the loopback address is the only road between them." alt="Two boxes, one for the command line process and one for the editor process, each with its own memory. Request lines travel from the first box to the second, and answer lines travel back."
flowchart LR
    A["StrataCLI process"] -- "request lines" --> B["StrataEditor process"]
    B -- "answer lines" --> A
```

## A socket is the operating system's door for bytes

A **socket** is an operating system handle for one end of a network connection: a program writes bytes into it and reads bytes out of it like a file. On Windows the handle is a `SOCKET` and elsewhere a file descriptor; Strata widens both to one :term[integer]{id=integer} type, `SocketHandle`, so that its :term[header]{id=header} needs no system header.

**TCP** is the protocol under the socket: a reliable, ordered stream of bytes between two sockets, with no message boundaries. Reliable means that the system sends lost pieces again, and ordered means that bytes arrive in the order they were sent. Remember the last part: TCP promises the bytes, never their grouping.

A machine runs many programs that want to be reached, and one address cannot tell them apart. A **port** is a 16-bit number that selects one waiting program on a machine. The web uses 80 and 443, and your program may use any free number from 1 to 65535.

Port 0 is not a real port: it means "choose for me". An **ephemeral port** is a port that the operating system picks from its free ones when a program asks for port 0. The editor asks for port 0 by default, because a fixed port might belong to another program, and then the editor would not start. The number is then unknown in advance, so clients must learn it; the page on [sessions](../automation/sessions.md) shows how.

## One side listens, the other connects

The two ends play different roles. The waiting program creates a socket, **binds** it to an address and a port (it claims them) and **listens** (it asks the system to queue incoming connections). The program that wants service **connects** to that address and port.

A **listener** is a socket that only waits for connections and carries no data itself.

To **accept** is to take the oldest queued connection of a listener and receive a new, connected socket for that client. The listener stays open for the next client, so a server with four clients holds one listener and four connected sockets.

Which address does the listener bind? **Loopback** is the machine talking to itself: traffic to a loopback address never leaves the machine. IPv4 reserves every address from 127.0.0.0 to 127.255.255.255 for it, and IPv6 has the single address `::1`. A listener bound there refuses clients from other machines.

```text
bind 127.0.0.1 port 0   ->  the system picks a free port, for example 53311
listen                  ->  incoming connections are queued
accept                  ->  a connected socket for one client
```

The first line is what Strata does by default; one call, `Listen`, binds and listens.

## Waiting without freezing

A call that reads from a socket has a problem: what if nothing has arrived? The simple answer is to wait until a byte comes. A program that waits like this is blocked and can do nothing else, and an editor that draws sixty frames a second cannot be blocked by a client that went silent.

**Non-blocking I/O** (input and output) means that a socket call returns at once, with the data if there is some and with "nothing now" if there is none. The program then decides what to do. Trying again in a tight loop wastes the processor, so something must say "now there is data".

That something is **poll**, a system call that takes a list of sockets and a timeout, waits until one socket is ready to read or write, or until the timeout ends. It then reports which ones are ready. One thread can serve many connections this way, with no busy loop and no thread per connection. The call is named `poll` on Linux and macOS and `WSAPoll` on Windows; Strata hides both.

One more detail costs time that a user can feel. TCP likes to hold a very small write for a moment, hoping that more bytes follow to fill a packet. **Nagle's algorithm** is this delay: small writes wait until earlier data is acknowledged or a packet is full. For a request of 76 bytes followed by silence, it only delays. Request and answer protocols disable it with the option `TCP_NODELAY`, and Strata's client and server both do.

## How a connection ends, and how it fails

A connection can end politely or rudely. A **half-close** ends one direction of the connection: a program calls `shutdown` on its sending side, which tells the peer "no more bytes will come from me", while the program keeps receiving. The peer reads what remains and then sees the end of the stream. A client can say "that was my last request" and still read all its answers.

A **connection reset** is an abrupt close: the system drops the connection at once, and data still :term[in flight]{id=in-flight} can be lost. It happens when a program crashes or closes while data waits that nobody has read. A read then reports an error instead of an end of stream.

Linux and macOS send the broken pipe signal (SIGPIPE) to a process that writes to a connection the peer already closed. **SIGPIPE** is a signal whose default action ends the process, so a server that does nothing special dies because one client left at a bad moment. The cure is to suppress the signal and read the error: Linux does this per call with the flag `MSG_NOSIGNAL`, macOS per socket with `SO_NOSIGPIPE`, and Windows has no such signal.

## Strata's socket layer is small, and every wait has a timeout

Strata calls none of these system functions from its other code. `TcpSocket` is the connected socket, `TcpListener` the listener and `SocketPoller::Poll` the wait for many sockets, all in the `Network` layer. The quote is the contract of `TcpSocket`. Read the comment above the class first, then the signatures.

```cpp src="Strata/src/Strata/Network/Socket.h#L44-L97"
// Connected TCP stream socket (move-only; the destructor closes it).
//
// Sockets are kept in non-blocking mode internally; every blocking operation is implemented by waiting
// for readiness with a timeout (clamped to c_MaxSocketTimeout), so no call can hang forever unless explicitly
// asked to. Writing to a connection the peer has closed never raises SIGPIPE. A socket may be used by one
// thread at a time.
class TcpSocket
{
public:
	TcpSocket() = default;
	~TcpSocket();

	TcpSocket(TcpSocket&& other) noexcept;
	TcpSocket& operator=(TcpSocket&& other) noexcept;
	TcpSocket(const TcpSocket&) = delete;
	TcpSocket& operator=(const TcpSocket&) = delete;

	// Resolves host (a name or numeric IPv4/IPv6 address) and connects to the first address that accepts
	// within timeout (shared by all addresses). On failure, error (if given) receives a description.
	static std::optional<TcpSocket> Connect(std::string_view host, uint16_t port, std::chrono::milliseconds timeout, std::string* error = nullptr);

	// Sends every byte, waiting for buffer space as needed. Returns false if the connection failed or the
	// timeout (no limit when nullopt) elapsed first; the amount of data sent is then unspecified.
	bool SendAll(std::span<const uint8_t> data, std::optional<std::chrono::milliseconds> timeout = std::nullopt);
	bool SendAll(std::string_view data, std::optional<std::chrono::milliseconds> timeout = std::nullopt);

	// Sends as much of data as the socket accepts without blocking. Returns the number of bytes sent
	// (0 when the send buffer is full), or nullopt if the connection failed.
	std::optional<size_t> SendSome(std::span<const uint8_t> data);

	// Waits up to timeout for incoming data and appends whatever is available (one read) to appendTo.
	SocketReceiveStatus Receive(std::vector<uint8_t>& appendTo, std::chrono::milliseconds timeout);

	// Half-closes the connection: the peer sees the end of the stream, while this side can still receive.
	bool ShutdownSend();
	void Close();
	bool IsValid() const { return m_Handle != c_InvalidSocketHandle; }
	// Disables (true) or enables (false) Nagle's algorithm. Request/response protocols want it disabled.
	bool SetNoDelay(bool enabled);

	// The local port this socket is bound to (0 if unknown).
	uint16_t GetLocalPort() const;
	SocketHandle GetHandle() const { return m_Handle; }
private:
	explicit TcpSocket(SocketHandle handle)
		: m_Handle(handle)
	{
	}
private:
	SocketHandle m_Handle = c_InvalidSocketHandle;

	friend class TcpListener;
	friend class SocketNotifier;
};
```

1. **Lines 46–49:** every socket is non-blocking inside, and every "blocking" function waits for readiness with a timeout, so no call hangs unless the caller asks for no limit; no write raises SIGPIPE.
2. **Lines 56–59:** the type is move-only, since a copy would give two owners one handle, and the first :term[destructor]{id=destructor} would close the second's connection.
3. **Lines 63–68:** `Connect` shares one timeout between all addresses it tries, and `SendAll` returns `false` on failure with the amount sent unknown, which is why a failed send ends the connection (see the client below).
4. **Lines 69–82:** `Receive` returns `Data`, `Timeout`, `Closed` for an orderly end or `Error` for a reset, `ShutdownSend` is the half-close and `SetNoDelay` turns the delay of the earlier section off.

`TcpListener::Listen` takes an address and a port whose defaults are `127.0.0.1` and 0: loopback and an ephemeral port. `GetPort` reads the chosen port back. On Windows the listener also sets `SO_EXCLUSIVEADDRUSE`, so no other program can take the same port while the editor listens. On POSIX systems it sets `SO_REUSEADDR`, which lets a restarted program bind a port whose old connections are closing.

`SocketPoller::Poll` takes an array of entries, each with a handle and two wishes (`WantRead`, `WantWrite`), and a timeout. It sets `Readable` and `Writable` on the ready entries. A failed or closed connection also counts as ready to read, so the next read reports the failure and nobody watches a second list of errors.

Two guards surround the timeouts. A timeout longer than 24 hours, or a negative one, is clamped into the range from 0 to `c_MaxSocketTimeout`, which is 24 hours. A wait is computed as "now plus the timeout", and a huge value would overflow that sum and put the deadline in the past. Second, sockets are not inherited by child processes (`WSA_FLAG_NO_HANDLE_INHERIT` on Windows, `FD_CLOEXEC` on POSIX systems). Otherwise a game that the editor starts would hold a copy of the editor's connection, and the connection would stay open until the game exits.

Which addresses may the editor bind? The next quote is the loopback check on POSIX systems; the Windows twin is in `Strata/src/Platform/Windows/WindowsSocket.cpp`. The check reads numbers and never asks a name service.

```cpp src="Strata/src/Platform/Posix/PosixSocket.cpp#L491-L504"
bool IsLoopbackAddress(std::string_view address)
{
	if (address.empty() || address.find('\0') != std::string_view::npos)
		return false;

	const std::string text(address);
	in_addr ipv4 = {};
	if (inet_pton(AF_INET, text.c_str(), &ipv4) == 1)
		return (ntohl(ipv4.s_addr) >> 24) == 127;
	in6_addr ipv6 = {};
	if (inet_pton(AF_INET6, text.c_str(), &ipv6) == 1)
		return IN6_IS_ADDR_LOOPBACK(&ipv6) != 0;
	return false;
}
```

1. **Lines 493–494:** an empty address, or one with a zero byte inside, is refused first.
2. **Lines 497–502:** a dotted number is loopback when its first byte is 127, so the whole block counts, and an IPv6 number only when it is `::1`.

Everything else returns `false`, including the name `localhost`. A name is resolved by a service that a network setting controls, and it may point at another machine. A check that accepts only numbers can be tested without asking anyone.

The `Network` layer holds `Strata/src/Strata/Network/` and the two socket files of the platform folders. Those files sit under `Platform/` because they use system headers, but they belong to `Network`, which may include only `Core`. It is a Tooling layer, and a game never links one ([layers](../core/layers-registries.md) lists them). Strata has no gameplay networking: this code serves editor automation only, and [networking](../appendix/networking.md) explains what an online game needs.

## A stream has no message boundaries

Now the trap promised at the start. TCP delivers bytes in order, but it may cut them anywhere. The cut depends on packet sizes, timing and the load of both machines, so a test on your machine may never show it and another user's machine shows it daily.

:::example[A request cut into three reads]
The client writes the line `{"id":1,"jsonrpc":"2.0","method":"entity.create","params":{"name":"Crate"}}` and a line break: 76 bytes, in one call. The editor's reads return 39, 22 and 15 bytes.

After the first read the editor holds 39 bytes and no line break, so it knows nothing yet. After the second it holds 61 bytes, still without one. After the third it holds 76 bytes and the last is the line break, so the message is complete.

A program that treats the first read as the message reads the text `{"id":1,"jsonrpc":"2.0","method":"entit` and fails. A program that waits for a fixed byte count breaks when a request is longer or shorter. The program needs a rule that finds the end of a message however the stream was cut.
:::

That rule is **framing**: the convention that marks where one message ends and the next begins in a stream. The next section compares the conventions.

## Four ways to frame messages

A length prefix writes the size first. The receiver reads four bytes, learns that 75 bytes follow and reads exactly 75, without scanning the data, which may be binary. The cost is that a wrong length, from a bug or a hostile sender, breaks the stream for good.

An end marker is a special byte or sequence: a line break, a zero byte or a blank line. The receiver scans for it. The cost is that the marker must never occur inside a message, so the format must escape it. The mail protocol `SMTP` works this way.

Some formats show their own end. :term[JSON]{id=json} is one, because a document ends where its braces match. The cost is a reader that can stop in the middle and continue, which is more code than a scan for one byte, and a damaged document breaks all that follows.

The web protocol `HTTP` combines two: headers that end with a blank line, and a body whose length a header gives. It is flexible and heavy, since every message pays for headers.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Length prefix | A few bytes per message | Exact, safe for binary data | Low; a wrong length breaks the stream | Binary game and database protocols |
| End marker | One byte | People can read it | Low; the marker must be escaped | `SMTP`, line-based tools |
| Format with its own end | None | Needs a reader that continues | High | Streams of JSON documents |
| Headers and length | Large per message | Flexible, widely supported | Medium | `HTTP` |

Strata chooses the line break.

:::why[Why a line break and not a length prefix?]
Every request and answer is JSON, and JSON escapes every control character inside a string: a line break in a string is written as a backslash and `n`. In the compact form, with no spaces or line breaks between its parts, a document holds no raw line break. So the marker is safe by the format's own rules and costs nothing to escape.

The price is a scan over every byte, and no raw binary data in a message: an image travels as a path or as text. For commands that take milliseconds, that price is small.
:::

The rule sits in a comment above the reader's constants.

```cpp src="Strata/src/Strata/Network/JsonRpc.h#L13-L20"
// JSON-RPC 2.0 over newline-delimited streams: every message is one compact JSON document followed by '\n'.
// Compact serialization escapes control characters inside strings, so a message never contains a raw newline.
// Batch requests are not supported.

namespace Strata
{

	constexpr size_t c_DefaultMaxRpcMessageSize = 64ull * 1024 * 1024;
```

The comment gives the rule: one compact document and a `\n` per message, no raw line break inside, no batch requests. The constant adds the limit: `c_DefaultMaxRpcMessageSize` is 64 MiB (`64ull * 1024 * 1024` bytes) in both directions.

`JsonRpc::Serialize` writes the compact form and never throws: invalid :term[UTF-8]{id=utf-8} in a string becomes the character `U+FFFD` instead of an error. An engine does not throw (see [conventions](../core/conventions.md)), and a damaged name in a scene must not stop the editor from answering.

## The line reader rebuilds lines from chunks

`JsonLineReader` is the receiving half. `Append` feeds it chunks of any size, and `NextLine` returns complete lines. It keeps a text buffer and two offsets: the read offset, where the first line not yet taken starts, and the scan offset, before which no line break exists. The scan offset saves work: a message that arrives in a thousand chunks is never searched from its start a thousand times.

The reader accepts `\n` and `\r\n` and skips blank lines.

:::example[The reader meets four chunks]
The first case of the suite `Network.JsonRpc` feeds the reader these chunks. Each row is one `Append` and the `NextLine` calls after it.

| Chunk appended | Bytes held after it | What `NextLine` returns |
| --- | --- | --- |
| `{"a":` (5 bytes) | 5 | nothing: no line break yet |
| `1}` (2 bytes) | 7 | nothing; the buffered size is 7 |
| a line break and `{"b"` (5 bytes) | 12 | `{"a":1}`, then nothing; 4 bytes stay |
| `:2}` and a line break (4 bytes) | 8 | `{"b":2}`, then nothing; 0 bytes stay |

:::

The code of both functions follows. Search it for the places where the reader stops early.

```cpp src="Strata/src/Strata/Network/JsonRpc.cpp#L65-L114"
void JsonLineReader::Append(std::string_view data)
{
	if (HasError() || data.empty())
		return;

	Compact();
	m_Buffer.append(data);

	// Fail early on a line that can no longer fit, instead of buffering an unbounded amount of data.
	const size_t terminator = m_Buffer.find('\n', m_ScanOffset);
	const size_t pendingEnd = terminator == std::string::npos ? m_Buffer.size() : terminator;
	if (pendingEnd - m_ReadOffset > m_MaxMessageSize + 1) // +1 tolerates the '\r' of a "\r\n" terminator
		SetOversizeError(pendingEnd - m_ReadOffset);
}

std::optional<std::string> JsonLineReader::NextLine()
{
	while (!HasError())
	{
		const size_t terminator = m_Buffer.find('\n', m_ScanOffset);
		if (terminator == std::string::npos)
		{
			m_ScanOffset = m_Buffer.size();
			if (m_Buffer.size() - m_ReadOffset > m_MaxMessageSize + 1)
				SetOversizeError(m_Buffer.size() - m_ReadOffset);
			return std::nullopt;
		}

		size_t lineEnd = terminator;
		if (lineEnd > m_ReadOffset && m_Buffer[lineEnd - 1] == '\r')
			lineEnd--;

		const size_t lineStart = m_ReadOffset;
		m_ReadOffset = terminator + 1;
		m_ScanOffset = m_ReadOffset;

		const size_t length = lineEnd - lineStart;
		if (length > m_MaxMessageSize)
		{
			SetOversizeError(length);
			return std::nullopt;
		}

		std::string line = m_Buffer.substr(lineStart, length);
		const bool blank = line.find_first_not_of(" \t\r") == std::string::npos;
		if (!blank)
			return line;
	}
	return std::nullopt;
}
```

1. **Lines 70–77:** `Append` compacts the buffer, adds the data and checks the pending line against the limit, so a line that cannot fit fails at once instead of filling memory until its end arrives. The extra byte tolerates the `\r`.
2. **Lines 84–90:** `NextLine` searches from the scan offset, and with no line break it moves the scan offset to the end so the next call skips that part.
3. **Lines 93–95:** a `\r` before the line break is dropped. When `\r` arrives in one chunk and `\n` in the next, the first call finds no line break, and the second sees the pair as one end.
4. **Lines 101–111:** a line over the limit sets the error, and a blank line, with only spaces, tabs or `\r`, is skipped by the loop.

### An oversized line is a permanent error

What if a line never ends? A hostile or broken client could send many GB with no line break. A line over 64 MiB sets the reader into an error state, with a message that names the limit, and the reader drops its buffer. The error lasts until `Reset`, because the reader cannot know where the next message begins: reading on would take the middle of a message for a start.

The suite pins this down: a reader with a limit of 8 bytes fails on `1234567890` even with no end yet, and afterwards the bytes `\n{}\n` give no line until `Reset`.

## A depth check runs on raw text before any value is built

A message under the size limit can still hurt. The text `[[[[[` followed by a million more brackets is only a million bytes, yet copying, comparing or writing the value it describes calls a function that calls itself once per level. That exhausts the stack, which is small and fixed, and ends the process.

So `JsonRpc::Parse` scans the raw text before it builds any value. The scan has to know what is text and what is structure.

```cpp src="Strata/src/Strata/Network/JsonRpc.cpp#L14-L47"
bool ExceedsNestingDepth(std::string_view text, size_t maxDepth)
{
	size_t depth = 0;
	bool inString = false;
	bool escaped = false;
	for (const char character : text)
	{
		if (inString)
		{
			if (escaped)
				escaped = false;
			else if (character == '\\')
				escaped = true;
			else if (character == '"')
				inString = false;
			continue;
		}

		if (character == '"')
		{
			inString = true;
		}
		else if (character == '[' || character == '{')
		{
			if (++depth > maxDepth)
				return true;
		}
		else if ((character == ']' || character == '}') && depth > 0)
		{
			depth--;
		}
	}
	return false;
}
```

1. **Lines 21–28:** inside a string a backslash makes the next character ignored and a plain quote ends the string, so brackets inside strings never count.
2. **Lines 32–44:** a quote outside a string starts one, an opening bracket or brace raises the depth and fails above the limit, and a closing one lowers it, never below zero.

The limit is `c_MaxJsonDepth`, 256. The scan does not check that the JSON is valid: text with brackets that do not match passes when it stays shallow, and the real reader rejects it a moment later. `Parse` then calls the JSON library's form that does not throw, which marks bad input as discarded, and returns an empty `std::optional`. Exceptions of third-party code stay at the :term[call site]{id=call-site}, as the conventions ask.

## JSON-RPC turns lines into calls

Lines of JSON carry data, but a line does not say what it wants. Both programs need an agreement about meaning: which line is a request, which is an answer, and which answer belongs to which request.

An **RPC** (remote :term[function call]{id=function-call}) runs a function in another process: the caller names the function and its arguments, waits, and receives a :term[return value]{id=return-value} as if the function were local.

Systems differ in how much they fix. `REST` maps operations to web addresses and `HTTP` verbs. `gRPC` describes calls in a schema and sends compact binary messages, which is fast and typed but needs generated code on both sides. `XML-RPC` does the same with marked-up text. JSON-RPC is the smallest: a method name, parameters and an id, all in JSON, with no schema tool and no `HTTP`, so it fits a line over a socket.

**JSON-RPC 2.0** is that small protocol: every message is a :term[JSON object]{id=json-object} that names its version, `"jsonrpc": "2.0"`, and is a request, a notification or a response. A request has `method` (a string such as `entity.create`), `params` (an object or an array, optional) and `id` (a string, a number or null). The server copies the id into the answer.

A notification is a request with no `id`, and the server sends no answer to it, not even an error. A response carries the same `id` and exactly one of `result` and `error`. An error is an object with an integer `code`, a `message` for people and an optional `data` for programs.

A **batch** is an array of requests in one message, answered by an array of responses. Strata's server refuses it with an error. The client pays one line per request; the server never has to match a list of answers to a list of requests.

## The worked example, from the client's bytes to the answer

Follow one call. You run the command line with the name `Crate`, and the client sends a request with the id 1.

:::example[One entity.create on the wire]
The client builds the object with `MakeRequest`, writes it with `Serialize` and adds a line break. The keys come out sorted by name, because the JSON library keeps them in a sorted map. This line travels, 76 bytes with its line break:

```text
{"id":1,"jsonrpc":"2.0","method":"entity.create","params":{"name":"Crate"}}
```

The server reads the line, checks it (next section) and hands the method name and the parameters to the editor's :term[command registry]{id=command-registry}. When the command succeeds, the answer repeats the id and puts the command's value into `result`. The identifier is 16 :term[hexadecimal]{id=hexadecimal} digits; the value here is invented:

```text
{"id":1,"jsonrpc":"2.0","result":{"id":"00A1B2C3D4E5F607"}}
```

The answer is 60 bytes with its line break. The client matches the id 1 and returns the result, and the command line prints that whole result object, spread over several lines.
:::

Now write a wrong name for a parameter: `nam` instead of `name`. The command registry compares the keys with the command's schema, which allows no other properties, and refuses the call before the command runs, so the scene does not change.

```text
{"id":2,"jsonrpc":"2.0","method":"entity.create","params":{"nam":"Crate"}}
{"error":{"code":-32602,"data":{"command":"entity.create","parameters":{"additionalProperties":false,"properties":{...},"type":"object"}},"message":"Unknown parameter 'nam' for entity.create (parameters: components, name, parent)"},"id":2,"jsonrpc":"2.0"}
```

The first line is the request and the second the answer, with the schema's `properties` shortened to three dots. The sorted keys put `error` before `id` here. Read the error from the inside out. The `code` is -32602, `InvalidParams`: the method exists and the request is well formed, but its parameters do not fit. The `message` names the wrong key and lists the three known ones.

The `data` carries the command's whole schema, so an agent can correct its request without asking again. The same connection stays open after this error.

## `ValidateRequest` checks the shape and recovers the id

Before the server dispatches a message, `JsonRpc::ValidateRequest` checks that it has the shape of a request. It returns a small record: valid or not, notification or not, the id when one could be recovered, and a sentence that names the problem. The order of the checks shapes what the sender learns.

```cpp src="Strata/src/Strata/Network/JsonRpc.cpp#L235-L279"
RequestValidation ValidateRequest(const nlohmann::json& message)
{
	RequestValidation validation;
	if (!message.is_object())
	{
		validation.Error = "A request must be a JSON object";
		return validation;
	}

	const auto id = message.find("id");
	if (id != message.end())
	{
		if (!IsValidId(*id))
		{
			validation.Error = "\"id\" must be a string, a number or null";
			return validation;
		}
		validation.Id = *id;
	}
	validation.IsNotification = id == message.end();

	const auto version = message.find("jsonrpc");
	if (version == message.end() || !version->is_string() || version->get_ref<const std::string&>() != c_Version)
	{
		validation.Error = "\"jsonrpc\" must be \"2.0\"";
		return validation;
	}

	const auto method = message.find("method");
	if (method == message.end() || !method->is_string() || method->get_ref<const std::string&>().empty())
	{
		validation.Error = "\"method\" must be a non-empty string";
		return validation;
	}

	const auto params = message.find("params");
	if (params != message.end() && !params->is_object() && !params->is_array())
	{
		validation.Error = "\"params\" must be an object or an array";
		return validation;
	}

	validation.Valid = true;
	return validation;
}
```

1. **Lines 238–241:** a message that is not an object is invalid at once, with no id to recover.
2. **Lines 245–254:** the id is read first: an object or array as id is invalid, and a missing id makes the message a notification.
3. **Lines 257–260:** `"jsonrpc"` must be the string `"2.0"`; a request with `1.0` fails, but its id is already stored.
4. **Lines 264–273:** `method` must be a non-empty string, and `params` an object or an array when present.

The id is recovered early for a reason. A sender that made a mistake in `method` still waits for an answer to its id. When the server answers `InvalidRequest` with that id, the client knows which call failed; with a null id it could only guess. The suite checks it: a request with the version `1.0` and the id 5 is invalid and still returns 5.

## The error codes: five standard and six of Strata's

JSON-RPC 2.0 reserves five codes and leaves -32000 to -32099 to each implementation. Strata fills six of them. The codes are names of a plain enum inside a :term[struct]{id=struct}.

```cpp src="Strata/src/Strata/Network/JsonRpc.h#L59-L76"
struct ErrorCode
{
	enum : int
	{
		ParseError = -32700,
		InvalidRequest = -32600,
		MethodNotFound = -32601,
		InvalidParams = -32602,
		InternalError = -32603,

		Unauthorized = -32001,     // The connection has not authenticated (or used a wrong token)
		ConnectionClosed = -32002, // Client side: not connected, or the connection was lost mid-call
		Timeout = -32003,          // Client side: no response arrived in time
		ServerBusy = -32004,       // The server rejected the request or connection due to load limits
		OperationFailed = -32005,  // The request was valid, but the method could not carry it out (the message says why)
		Cancelled = -32006         // The request was abandoned before it completed (e.g. the server is shutting down)
	};
};
```

1. **Lines 63–67:** the standard five are `ParseError` (not JSON, or nested too deeply), `InvalidRequest` (JSON, but not a request), `MethodNotFound`, `InvalidParams` and `InternalError`.
2. **Lines 69–74:** Strata's six are `Unauthorized`, `ConnectionClosed`, `Timeout`, `ServerBusy`, `OperationFailed` and `Cancelled`, each with a comment that says when it appears.

The plain enum inside `ErrorCode` keeps the qualified name, as in `JsonRpc::ErrorCode::Timeout`, and converts to `int` without a cast, which a scoped `enum class` would need. The reference page on [automation](../reference/automation.md) holds the table of all codes and limits.

Two codes are raised by the client for failures it detects itself: `ConnectionClosed` and `Timeout`. `OperationFailed` is the code of a command that ran and said no, for example when the scene is full. `InvalidParams` is for parameters that the command's schema rejects.

## The blocking client and why ids exist

`RpcClient` is a blocking client with one request in flight at a time, guarded by a :term[mutex]{id=mutex}, so threads that share a client take turns. `Call` sends a request with the next integer id and waits for the answer, 30 seconds by default. A loop reads chunks into the line reader and takes each complete line.

The client skips three kinds of line: notifications, lines it cannot read and answers whose id is not its own. The last rule is why ids exist.

:::example[A late answer]
The client sends request 7, a slow command, with a timeout of one second. After one second there is no answer, so `Call` returns the code `Timeout`, and the connection stays open. The user then sends request 8, a fast one.

The slow command finishes after three seconds, and its answer arrives while the client waits for request 8. The id is 7, not 8, so the client skips the line. The next line carries the id 8, and the client returns it.

Without ids the client would return the answer of the slow command as the answer of the fast one, and every later answer in the session would be shifted by one.
:::

An answer with a null id means that the server could not say which request it answers, for example because the line was not JSON. That error belongs to the current call, so the client returns it.

A failed send follows a stricter rule. If `SendAll` cannot write the whole line, the server may hold half a request, and the next line would be glued to it, so the client closes the connection and the next call reports `ConnectionClosed`. The same code comes when the server closes the connection, when a read fails and when the reader passes its limit. A timeout is the opposite: the road is fine and the answer is only late, so the connection stays.

That difference is the point to take away. A transport error (`ConnectionClosed`, `Timeout`) says that the road failed or the answer is late, and the command may or may not have run. A command's failure (`InvalidParams`, `OperationFailed`) is an answer that arrived: the command was understood and refused, and the road is fine. A program that tries again after a timeout must remember that the first try may have worked.

## What this design cannot do

The line protocol is simple on purpose, and it has limits.

- **No binary data.** A message is text, so a screenshot travels as a file path or as encoded text.
- **No concurrency in one client.** One request is in flight per connection, so two slow commands run one after the other.
- **No batches and no recovery from an oversized line.** The reader cannot find the next message after the size error, so the connection ends.
- **No protection by loopback alone.** A loopback port is open to every program on the machine; the proof of the session token that client and server exchange first is the protection, and the page on [security](../automation/security.md) describes it.
- **No gameplay networking.** Strata has no networking for games, such as sharing one world between players; [not in Strata](../appendix/not-in-strata.md) says what that means for a game maker.

The server's side, with its thread, queue and limits, is the page on the [editor's server](../automation/rpc-server.md).

## Common mistakes

- **Treating one read as one message.** The symptom is an error that appears only under load or on another machine. The fix is to append every read to a line reader and take lines from it.
- **Writing a request with a raw line break inside.** The symptom is a request that arrives as two broken lines. The fix is the compact form, which escapes the line break.
- **Binding to `localhost` or a public address.** The symptom is a connection from another machine to a private program. The fix is a numeric loopback address, which Strata's check enforces.
- **Reusing a reader after the size error.** The symptom is lines that start in the middle of a message. The fix is to close the connection, or to call `Reset` on a new one.
- **Treating a timeout as a failure of the command.** The symptom is an entity created twice. The fix is to look at the scene before you try again.

## Summary

- Two processes share no memory. Strata connects the editor and its clients with TCP on the loopback address, one code path on three systems, and uses standard streams only where an MCP client starts `StrataCLI` as its child.
- A listener on port 0 gets an ephemeral port. `TcpSocket` is move-only, waits with timeouts of at most 24 hours, never raises SIGPIPE and is not inherited by children; `SocketPoller::Poll` waits for many sockets and `ShutdownSend` half-closes.
- A TCP stream has no message boundaries. Strata writes one compact JSON document per line, which is safe because compact JSON escapes every line break; `JsonLineReader` rebuilds lines from chunks and fails for good at 64 MiB.
- A request has a version, a method, optional parameters and an id; a notification has no id and no answer; batches are refused. `ValidateRequest` checks the shape and recovers the id, and five standard codes plus Strata's six describe what went wrong.
- A transport error (`ConnectionClosed`, `Timeout`) differs from a command's failure (`InvalidParams`, `OperationFailed`). Ids let the client skip late answers after a timeout.

## Check yourself

1. A client reads once from the socket and reads the bytes as one request. It works on a laptop and fails on a busy server. Which statement explains it?
   1. The loopback address drops packets under load.
   2. TCP delivers bytes in order but may cut them anywhere, so one read can hold half a request or two.
   3. JSON cannot be read from a socket.
   4. Compact JSON has no line break at its end.

   :::answer{tests="framing"}
   Option 2 is right: a stream has no message boundaries, and the cut depends on timing. Option 1 is wrong because loopback keeps bytes in order. Option 3 is wrong because JSON text is read from any source. Option 4 is wrong because the writer adds the line break after the compact text.
   :::

2. Which carrier fits a client that connects to an editor started an hour ago by someone else: standard streams, TCP on loopback, or shared memory?
   :::answer{tests="choose-channel"}
   TCP on loopback. Standard streams exist only between a parent and the child it started, and shared memory needs locks, layouts and care after a crash. A later client has no pipe to the editor, but it can connect to the port.
   :::

3. Why is a line break a safe boundary in Strata, although messages may hold text from users?
   :::answer{tests="framing"}
   Compact JSON escapes control characters inside strings, so a user's line break becomes a backslash and `n`. Only the end marker writes a raw line break. The writer must use the compact form for this to hold.
   :::

4. A reader with a limit of 8 bytes receives `{}\n123456789\n{}\n`. What do the first three calls of `NextLine` return, and is the reader healthy?
   :::answer{tests="framing"}
   The first call returns `{}`. The second finds a line of 9 bytes, over the limit, sets the error and returns nothing. The third returns nothing too, because the error lasts until `Reset`, and the last `{}` is never delivered.
   :::

5. The client sends `{"id":4,"jsonrpc":"1.0","method":"entity.create"}`. Which code and id come back, and why does the id matter?
   :::answer{tests="json-rpc"}
   The code is -32600, `InvalidRequest`, and the id is 4, because `ValidateRequest` stores the id before it reports the version. The client can then attribute the error to its call; with a null id it would have to guess.
   :::

6. A call returns the code -32003 after its timeout, and a second call follows. What happens to the first command's answer, and what do you know about whether the command ran? Which of `ConnectionClosed`, `InvalidParams`, `Timeout` and `OperationFailed` are transport errors?
   :::answer{tests="error-kinds socket-life"}
   The connection stays open, and the late answer carries an old id, so the client skips it. The code -32003 is `Timeout`, a transport error, and says nothing about whether the command ran. `ConnectionClosed` and `Timeout` are transport errors; `InvalidParams` and `OperationFailed` arrive as answers from the server.
   :::

## Exercises

1. **Basic.** A program binds a listener to port 0 and reads back the port 53311. Give two reasons why the editor does not bind a fixed port such as 9000, and say what clients need afterwards.
   :::answer[Worked solution]{tests="choose-channel socket-life"}
   Another program may already hold port 9000, and then the editor fails to start; and two editors on one machine could not both listen. The cost of port 0 is that clients must learn the number, which the page on [sessions](../automation/sessions.md) describes.
   :::

2. **Hard.** Predict, then run. A reader with the default limit receives three chunks: `{"a":1}` and a carriage return; then a line feed, a carriage return and a line feed; then `{"b":2}` and a line feed. Say what `NextLine` returns after each chunk, write the chunks as a new case of `Network.JsonRpc` and run the suite.
   :::answer[Worked solution]{tests="framing" solution="tutorials/automation/json-rpc/exercise-2.patch"}
   After the first chunk the buffer holds `{"a":1}` and the carriage return with no line feed, so `NextLine` returns nothing. The second chunk brings the line feed, and the reader drops the carriage return before it and returns `{"a":1}`. A second call finds the next carriage return and line feed with nothing before them: a blank line, which it skips, and then it returns nothing. After the third chunk `NextLine` returns `{"b":2}`, the call after it returns nothing, and the reader has no error.

   The patch adds the case after the existing `\r\n` case in `StrataTests/src/Network/JsonRpcTests.cpp`. Build the test program as in [first change](../core/first-change.md) and run it with `--test-suite=Network.JsonRpc`. To see that the case checks something, expect the carriage return to stay in the line and watch the check fail.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Network/Socket.h` and `Socket.cpp`: `TcpSocket`, `TcpListener`, `SocketPoller`, `IsLoopbackAddress`, `ClampSocketTimeout` and `c_MaxSocketTimeout`.
- `Strata/src/Platform/Windows/WindowsSocket.cpp` and `Strata/src/Platform/Posix/PosixSocket.cpp`: the system code, in the `Network` layer of `StrataTests/Architecture/Layers.json`.
- `Strata/src/Strata/Network/JsonRpc.h` and `JsonRpc.cpp`: `JsonLineReader`, `c_DefaultMaxRpcMessageSize`, `JsonRpc::Serialize`, `JsonRpc::Parse`, `JsonRpc::ValidateRequest`, `JsonRpc::ErrorCode` and `c_MaxJsonDepth`.
- `Strata/src/Strata/Network/RpcClient.h` and `RpcClient.cpp`: the blocking client.
- `StrataEditor/src/Editor/EditorAutomation.cpp`: `EditorAutomation::ToRpcResult`, which turns a command's failure into a code and puts the schema into `data`.
- The suites `Network.Socket` and `Network.JsonRpc` in `StrataTests/src/Network/`: ephemeral ports, half-close, a write to a closed peer, clamped timeouts and loopback recognition; rebuilding lines, split `\r\n`, the size limit, builders, one-line output and request validation.

## Further reading

- The JSON-RPC 2.0 specification at jsonrpc.org: the whole protocol in a few pages (beginner).
- Beej's Guide to Network Programming: sockets, bind, listen, accept and poll from the start (beginner to intermediate).
- RFC 896, Congestion control in IP/TCP internetworks, on Nagle's algorithm (advanced).
- RFC 9112, HTTP/1.1, the section on message framing (advanced).
