---
id: automation/rpc-server
title: "The editor's RPC server"
description: "How the editor lets other programs run its commands without stalling a frame: the network thread, the bounded queue, responders and the command binding."
kind: internals
size: XL
tracks: [E]
needs: [automation/json-rpc, editor/deferred-commands, core/jobs]
time: 130
learn:
  - id: trace-request
    text: trace one request through the network thread and the main thread, from the socket read to the answer
  - id: one-answer
    text: explain why every request gets exactly one answer and which code guarantees it
  - id: name-limit
    text: name the limit that answers a client that floods, stalls, hoards or reads slowly, and say how
  - id: commands-methods
    text: explain how a registered command becomes a method and how its errors become wire codes
  - id: extend-safely
    text: add behaviour to the server without breaking the one-answer rule or the main-thread rule
since: 0.3.0
status: final
---

An editor that an agent drives must answer requests from other programs through remote :term[function calls]{id=function-call} (:term[RPC]{id=rpc}), yet it may never stall a frame to do so. The server of this page reads sockets on a thread of its own and hands each request to the :term[main thread]{id=main-thread}, which runs it at a fixed point of the frame. It also keeps every peer within bounds, so a slow or hostile client cannot grow its memory or hold its threads. A second piece, `EditorAutomation`, turns each editor command into a method, so no feature needs an endpoint of its own. The proof exchange that opens a connection belongs to [the security page](../automation/security.md), and the session file to [the sessions page](../automation/sessions.md).

## The problem and how engines solve it

A request such as "create an entity" changes the scene. The scene belongs to the main thread, which also draws the frame. A handler that touches the scene must therefore run on the main thread. A network connection is the opposite: a client may send a request at any moment, and the server must read it at once or the client's buffer fills. The two sides cannot wait for each other, and four designs resolve this at a price.

The first design handles requests on the network thread and protects the scene with locks. Every system that touches the scene must then take the same locks, including the :term[renderer]{id=renderer} and the scripts. One missed lock is a :term[data race]{id=data-race} that shows once in a thousand runs. The second design starts a thread for each connection. It has the same race, and it adds a thread per client: a hostile client that opens a thousand connections costs a thousand stacks.

The third design runs an event loop on the main thread. The loop polls the sockets between frames and handles each request in place. It has no races, but the frame now waits for the network. A client that sends half a request holds the loop only if the code blocks, so the code must never block, and every read must be written as a small step of a state machine. Reading a large message on the main thread also takes :term[frame time]{id=frame-time} that the player sees as a pause.

The fourth design splits the work. A network thread owns every socket, parses the messages and puts the requests into a queue. The main thread takes the queue once per frame and runs the handlers, and answers travel back through a second queue. Strata chooses this design, and its price is latency: a request waits up to one frame, 16.7 ms at 60 :term[frames per second]{id=frame-rate}, before its handler runs. An agent that sends a hundred requests one after another pays that wait a hundred times, unless it sends them together.

The second problem is a peer that breaks the rules. A client may be slow, faulty or hostile, and on a :term[loopback]{id=loopback} port any program of the machine can connect. A server that is open to such peers stays bounded by five tools:

- **Fixed buffers.** Every message, id and queue has a maximum size, so no peer can make the server allocate without end.
- **Flow control.** The server stops reading from a peer that has too much work in progress. The :term[operating system's]{id=operating-system} transmission control protocol (:term[TCP]{id=tcp}) then fills its window, the space it offers the sender for data not yet read, and the pressure reaches the peer. The idea, backpressure, is taught in [the page on asset loading](../assets/loading.md): refuse new work while too much is pending. Here it takes a network form, which the real code below shows.
- **Rate limits.** A repeated warning is logged once in a while with a count, so a flood of bad input cannot flood the log.
- **Timeouts.** A peer that does not finish the opening exchange, or does not read its answers, loses its connection.
- **Load shedding.** When a limit is reached, the server answers with an error such as `ServerBusy` instead of accepting the work.

Each tool bounds something different, and the sections below name which limit answers which behaviour. The next section shows the parts and their owners.

## The map: threads, queue and responders

Three kinds of code take part. Each owns different data, and the rest of the page explains why the boundaries lie where they do.

The **network thread** is the thread of `RpcServer` that owns every socket: it accepts connections, reads and parses messages, writes answers and enforces the deadlines.

The network thread also answers the **built-in methods** itself. These are the four methods whose names start with `rpc.`: `rpc.handshake`, `rpc.authenticate`, `rpc.ping` and `rpc.listMethods`. The prefix is reserved, so no registered method can take such a name.

Every other request goes into a bounded queue. The main thread calls `ProcessRequests` once per frame, swaps the queue empty and runs the handlers. A handler receives a **responder**: the object that completes one request, from any thread, exactly once. A handler may answer at once, or keep the responder and answer frames later. When it answers, the responder places the answer in an outgoing list and wakes the network thread through a notifier, a small socket pair that exists only for this wake-up.

```mermaid caption="Two threads and two hand-offs: requests cross to the main thread through a bounded queue, and answers cross back through a list that wakes the network thread." alt="The network thread owns the sockets, answers the built-in methods and writes answers. The main thread runs the handlers of queued requests once per frame. A bounded queue leads from the first to the second, and an outgoing list with a wake-up leads back."
flowchart LR
	subgraph net["Network thread: owns all sockets"]
		accept["accept, read, parse"]
		builtin["answer the built-in methods"]
		write["write answers, check deadlines"]
	end
	subgraph main["Main thread: owns the scene"]
		process["ProcessRequests once per frame"]
		handler["handlers run commands"]
	end
	accept --> builtin
	accept -- "queue: 1024 requests, 256 MiB" --> process
	process --> handler
	handler -- "responder: Respond from any thread" --> outgoing["outgoing list"]
	outgoing -- "notifier wakes the thread" --> write
```

The split decides who may touch what. Only the network thread touches a connection, so connections need no lock. Only the main thread touches the scene, so handlers need no lock either. Three small pieces of state are shared: the request queue with its :term[byte]{id=byte} count, the outgoing list, and the table of registered methods. Each has a :term[mutex]{id=mutex} of its own, and the code holds none of them while it does real work.

A connection also has a life of its own. It starts when the server accepts the socket, and it ends when both sides have said goodbye. The picture shows its states and what moves it from one to the next.

```mermaid caption="The life of a connection: most edges lead to a close that sends the owed answers first, and only a stalled client is dropped without a goodbye." alt="A connection is accepted, starts the opening exchange and is trusted. Losing its place, a timeout, a wrong proof, a half-close, an error or a server busy answer lead to closing, where the server sends its answers, shuts its sending side and waits for the peer. A stalled client goes straight to closed."
stateDiagram-v2
	[*] --> Accepted
	Accepted --> HandshakeStarted: first request
	HandshakeStarted --> Authenticated: right proof
	Accepted --> Closing: eviction or timeout
	HandshakeStarted --> Closing: wrong proof or timeout
	Authenticated --> Closing: peer half-close, error, ServerBusy
	Closing --> SendSideShut: answers sent, send side shut
	SendSideShut --> Closed: peer's end of stream or deadline
	Authenticated --> Closed: stalled client
	Closed --> [*]
```

## The contract

Each rule below states what a caller may assume, what a change must keep, and why. The reason matters more than the rule: a rule without its reason is the first thing a hurried change breaks.

1. **Handlers run on the main thread, and the network thread never touches engine state.** A handler may read and write the scene directly. The reason is the threading model of [the page on the job system](../core/jobs.md): one owner of the scene removes the need for locks. The network thread holds only sockets and the data that it shares through the three small structures.

2. **Every request gets exactly one answer.** A request with no answer leaves a client waiting for ever, and a request with two confuses a client that matches answers to ids. The guarantee has three parts. A responder answers at most once, and a responder that dies with no answer sent answers with an error. A server that stops with a grace period also cancels what is queued.

3. **Everything a peer controls is bounded.** Message size, nesting depth and the length of an echoed id have a limit. So do the queue, the output waiting for a client, the number of connections and the number of warnings in the log. A value with no limit is a lever that a hostile peer can pull.

4. **Slow readers are throttled; only stalled ones are dropped.** A client that reads late is honest and gets its answers eventually. A client that accepts no byte for the **stall timeout** is not. The server drops it, because it holds memory and slots for nothing.

5. **A connection closes in order.** The server sends the owed answers, shuts down its sending side, waits for the peer's end of the stream, and then closes. A close that skips the wait can reset the connection, and a reset can destroy the last answer :term[in flight]{id=in-flight}.

6. **A feature never gets an RPC endpoint of its own.** A feature reaches agents by registering an editor command, and the command becomes a method with no further code. Two paths into the editor would need two sets of checks, two undo behaviours and two descriptions for agents.

:::rule[Commands are the API]
The engine's `AGENTS.md` makes registering a command the one way to offer a feature to agents: each command becomes a method and a tool of the Model Context Protocol (MCP) server, with no RPC code. The reason is the single path: commands are how the scene and the project change, so undo, the journal and validation apply to agents without extra code. What a command's description and schema must hold is the rule "Write commands for agents" of [the page on commands](../editor/commands.md).
:::

:::rule[Commands never block a frame]
The engine's `AGENTS.md` asks a command that has to wait to hand back a deferred result with a poll. The poll keeps its own data and allocates nothing per frame. The server relies on it: a handler runs inside the frame, so a handler that waited would stop the frame for every client. [The page on deferred commands](../editor/deferred-commands.md) teaches the mechanism; the server only answers later, from the poll's completion.
:::

The rules also name a counter that the later sections use. The **requests in flight** of a client are its requests and notifications that are queued, being handled, or answered but not yet written into its send buffer. A notification is a request with no id, which gets no answer, but its handling still costs the main thread, so it counts too. The limit for one client is 64.

## A toy version

The toy keeps the idea and drops the sockets. A scripted "wire" holds five requests.

The `Read` function plays the network thread: it moves requests from the wire into a queue, but only while the queue has room and the client has fewer than two requests in flight. The `ProcessRequests` function plays the main thread: it swaps the queue empty once per frame and runs a handler for each request. A request named `wait` keeps its responder for two frames. A request named `drop` forgets its responder, and the :term[destructor]{id=destructor} must answer.

The toy has one thread, so it cannot show the races that the real design avoids. It shows what the contract asks for: bounded reading, a queue drained once per frame, a responder that answers once, and a late answer.

```cpp sketch="automation-rpc-server-toy.cpp"
#include <cstdio>
#include <deque>
#include <memory>
#include <string>
#include <vector>

constexpr size_t c_MaxQueued = 3;
constexpr int c_MaxInFlight = 2;

struct Request
{
	int Id = 0;
	std::string Method;
};

// Answers exactly once: a responder destroyed without an answer answers "dropped".
class Responder
{
public:
	Responder(int id, int& inFlight)
		: m_Id(id), m_InFlight(inFlight)
	{
	}

	~Responder()
	{
		if (!m_Answered)
			Respond("error: dropped");
	}

	void Respond(const char* text)
	{
		if (m_Answered)
			return;
		m_Answered = true;
		m_InFlight--;
		std::printf("  answer #%d: %s\n", m_Id, text);
	}
private:
	int m_Id;
	int& m_InFlight;
	bool m_Answered = false;
};

struct Waiting
{
	int DueFrame = 0;
	std::shared_ptr<Responder> Handle;
};

class ToyServer
{
public:
	// The "network thread": reads from the wire only while there is room.
	void Read(std::deque<Request>& wire)
	{
		while (!wire.empty() && m_Queue.size() < c_MaxQueued && m_InFlight < c_MaxInFlight)
		{
			m_Queue.push_back(wire.front());
			wire.pop_front();
			m_InFlight++;
		}
	}

	// The "main thread": once per frame, handles what the queue holds.
	void ProcessRequests(int frame)
	{
		std::deque<Request> requests;
		requests.swap(m_Queue);
		for (const Request& request : requests)
		{
			auto responder = std::make_shared<Responder>(request.Id, m_InFlight);
			if (request.Method == "wait")
				m_Waiting.push_back({ frame + 2, responder });
			else if (request.Method != "drop")
				responder->Respond("ok");
		}
		std::erase_if(m_Waiting, [frame](Waiting& waiting)
		{
			if (waiting.DueFrame > frame)
				return false;
			waiting.Handle->Respond("ok, after two frames");
			return true;
		});
	}
private:
	std::deque<Request> m_Queue;
	std::vector<Waiting> m_Waiting;
	int m_InFlight = 0;
};

int main()
{
	std::deque<Request> wire = { { 1, "wait" }, { 2, "ping" }, { 3, "drop" }, { 4, "ping" }, { 5, "ping" } };
	ToyServer server;
	for (int frame = 1; frame <= 4; frame++)
	{
		server.Read(wire);
		std::printf("frame %d: %zu requests still on the wire\n", frame, wire.size());
		server.ProcessRequests(frame);
	}
	return 0;
}
```

```text output-of="automation-rpc-server-toy.cpp"
frame 1: 3 requests still on the wire
  answer #2: ok
frame 2: 2 requests still on the wire
  answer #3: error: dropped
frame 3: 1 requests still on the wire
  answer #4: ok
  answer #1: ok, after two frames
frame 4: 0 requests still on the wire
  answer #5: ok
```

1. **Lines 25-29:** the destructor answers "dropped" when no answer went out, so a handler that forgets its responder cannot leave a client waiting.
2. **Lines 33-36:** the flag makes a second answer do nothing, and an answer frees one place of the client's budget.
3. **Lines 57-62:** the read loop stops when the queue is full or two requests are in flight; what it does not read stays on the wire.
4. **Lines 68-69:** the swap empties the queue in one step, so the frame handles a fixed batch.
5. **Lines 73-76:** `wait` keeps its responder, `drop` forgets it, and any other method answers at once.

The first frame reads requests 1 and 2 and stops, because two requests are in flight. Request 3 stays on the wire until request 2 answers and frees a place. Request 3 is `drop`: its responder dies at the end of the loop body and answers the error, so the client does not hang. Request 1 answers in frame 3, two frames after its handler ran. Frame 3 therefore prints two answers, and the other requests continue meanwhile, as they do in the editor.

The real server differs in five ways. It has a second thread and a notifier, and it limits bytes as well as counts. It looks the handler up again at the moment of the call. It holds a weak reference, a pointer that does not keep its target alive, so a responder can live longer than the server. It adds deadlines that close a connection, and an orderly close.

## The real code

The code below follows a request in the order it flows. The code files are `Strata/src/Strata/Network/RpcServer.cpp` for the server and `StrataEditor/src/Editor/EditorAutomation.cpp` for the editor's side. The first stop is the network thread, which spends its life in one function.

### The network thread's loop

`RunNetworkThread` calls `RunIteration` in a loop. One pass has three phases: move the answers that other threads produced into the connections, service what is ready, and wait for the next event. The first excerpt covers the first phase and the work that follows it.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L645-L677"
for (OutgoingResponse& response : outgoing)
{
	Connection* connection = FindConnection(response.ConnectionId);
	if (!connection)
		continue;
	Guard(*connection, [&]()
	{
		if (response.IsNotification)
		{
			if (connection->RequestsInFlight > 0)
				connection->RequestsInFlight--;
			return;
		}
		connection->PendingResponses.push_back(std::move(response));
	});
}

// Move answers into send buffers that have room and write eagerly (waiting for writability is only needed
// once a socket's buffer is full), resume clients whose backpressure has cleared, and enforce deadlines.
const auto now = std::chrono::steady_clock::now();
for (const Scope<Connection>& connection : Connections)
{
	Guard(*connection, [&]()
	{
		TransferResponses(*connection);
		if (!connection->Closed && connection->GetPendingOutput() > 0)
			Flush(*connection);
		TransferResponses(*connection);
		ProcessBufferedLines(*connection);
		CheckDeadlines(*connection, now);
	});
}
RemoveClosedConnections();
```

1. **Line 645:** the loop starts from the answers that `RunNetworkThread` took out of the shared outgoing list; the thread swaps the list empty under the mutex, so it never holds the mutex while it works.
2. **Line 650:** `Guard` runs the work of one connection and, when an allocation fails, closes that connection only; the thread survives.
3. **Lines 652-656:** a notification's "answer" only lowers the in-flight count, because nothing is sent.
4. **Lines 669-674:** each connection moves answers into its send buffer, writes at once, reads the lines it already holds, and checks its deadlines.

The next excerpt builds the poll set. The thread asks the operating system to wake it when anything it listens to is ready.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L683-L718"
const bool hasNotifier = Shared->Notifier.IsValid();
std::chrono::milliseconds timeout = hasNotifier ? c_IdlePollInterval : c_FallbackPollInterval;
if (DrainStarted)
{
	const auto untilDrainDeadline = std::chrono::duration_cast<std::chrono::milliseconds>(DrainDeadline - now);
	timeout = std::clamp(untilDrainDeadline + std::chrono::milliseconds(1), std::chrono::milliseconds(0), timeout);
}
pollEntries.clear();
pollEntries.push_back(SocketPollEntry { hasNotifier ? Shared->Notifier.GetHandle() : c_InvalidSocketHandle, true, false });
pollEntries.push_back(SocketPollEntry { Listener.GetHandle(), true, false });
for (const Scope<Connection>& connection : Connections)
{
	pollEntries.push_back(SocketPollEntry { connection->Socket.GetHandle(), WantsInput(*connection), connection->GetPendingOutput() > 0 });

	std::optional<std::chrono::steady_clock::time_point> deadline;
	if (connection->Closing)
		deadline = connection->CloseDeadline;
	else if (!connection->Authenticated)
		deadline = connection->AuthenticationDeadline;
	if (connection->GetPendingOutput() > 0)
	{
		const auto stallDeadline = connection->LastSendProgress + Specification.StalledClientTimeout;
		deadline = deadline ? std::min(*deadline, stallDeadline) : stallDeadline;
	}
	if (deadline)
	{
		const auto untilDeadline = std::chrono::duration_cast<std::chrono::milliseconds>(*deadline - now);
		timeout = std::clamp(untilDeadline + std::chrono::milliseconds(1), std::chrono::milliseconds(0), timeout);
	}
}

if (!SocketPoller::Poll(pollEntries, timeout))
	return false;

if (pollEntries[0].Readable)
	Shared->Notifier.Drain();
```

1. **Line 684:** with a notifier the thread sleeps for up to a second, which is only a safety net; without one it wakes every 5 ms to search for answers.
2. **Line 695:** a connection is polled for reading only when `WantsInput` agrees, and for writing only when it has output waiting.
3. **Lines 697-706:** each connection contributes its nearest deadline: the close, the authentication, or the stall check.
4. **Lines 707-711:** the wait ends at the earliest deadline of all, plus one millisecond, so no deadline passes unseen.
5. **Lines 717-718:** the notifier's bytes are drained, so the next wake-up is a new event.

The excerpt omits the rest of the pass, which reads from each ready socket, writes to each socket that can take data and accepts new connections. The exchange of proofs that a new connection starts is on [the security page](../automation/security.md).

### Waking the network thread

A thread asleep in `Poll` must wake when the main thread has an answer, and the sockets give it no reason. The solution is the **self-pipe trick**: the server owns a pair of connected sockets, the **notifier**, and puts the receiving end in the poll set. A thread that wants to wake the network thread writes one byte into the sending end. The byte makes the receiving end ready to read, so `Poll` returns, and the thread drains the byte. The name comes from the first use of the trick, which wrote to a pipe that the same process read.

On Linux and macOS the pair is one call, `socketpair`, and no other process can reach it. Windows has no such call for sockets that `Poll` accepts. Strata builds the pair from a loopback connection: it listens on an :term[ephemeral port]{id=ephemeral-port}, connects to it and accepts. That leaves a gap, because another local process could connect to the temporary listener before the real sender does. The code closes the gap with a random cookie.

```cpp src="Strata/src/Platform/Windows/WindowsSocket.cpp#L548-L576"
// Another local process could connect to the temporary listener first. The sender proves its identity with
// a random cookie; connections that do not present it promptly are discarded, so an intruder can delay the
// setup by at most a short wait per connection it makes.
std::array<uint8_t, c_NotifierCookieSize> cookie = {};
if (!Platform::GenerateSecureRandom(cookie) || !sender->SendAll(std::span<const uint8_t>(cookie), c_NotifierSetupTimeout))
{
	ST_CORE_WARN("SocketNotifier: failed to send the pairing cookie");
	return false;
}

const auto deadline = std::chrono::steady_clock::now() + c_NotifierSetupTimeout;
while (std::chrono::steady_clock::now() < deadline)
{
	std::optional<TcpSocket> candidate = listener.Accept(Remaining(deadline));
	if (!candidate)
		continue;

	const auto candidateDeadline = std::min(deadline, std::chrono::steady_clock::now() + c_NotifierCandidateTimeout);
	std::vector<uint8_t> received;
	SocketReceiveStatus status = SocketReceiveStatus::Data;
	while (received.size() < cookie.size() && status == SocketReceiveStatus::Data)
		status = candidate->Receive(received, Remaining(candidateDeadline));

	if (received.size() == cookie.size() && std::equal(received.begin(), received.end(), cookie.begin()))
	{
		std::scoped_lock<std::mutex> lock(m_SenderMutex);
		m_Sender = std::move(*sender);
		m_Receiver = std::move(*candidate);
		return true;
```

1. **Lines 551-556:** the sender writes 16 random bytes, the cookie, from the system's secure generator; a failure to send them fails the whole setup.
2. **Lines 561-563:** the loop accepts every candidate that connects before the deadline of 2 s.
3. **Lines 565-569:** a candidate gets 250 ms to send the cookie, so an intruder can delay the setup by that much for each connection it makes.
4. **Lines 571-576:** only a candidate whose bytes equal the cookie becomes the receiving end.

:::why[A verified pair on Windows, a plain pair elsewhere]
A wake-up socket that an intruder holds would let it read or forge the wake-ups of the server, and a forged wake-up wastes a loop at worst. The cost of the check is a few lines and a few milliseconds at start. The alternative on Windows is an event object, but `Poll` waits on sockets only, so the notifier would need a second wait mechanism. Strata keeps one wait, and pays for the check.
:::

### Backpressure in three predicates

The network thread decides whether to read from a client in three small functions. The result of `WantsInput` goes into the poll set, so a client that fails the test is not listened to. Its data stays in the operating system's buffer. When that buffer fills, the TCP window of the connection closes, and the sending program blocks or sees a full buffer. No code of the server tells the client to slow; the protocol does it.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1362-L1388"
bool RpcServer::Impl::CanProcessRequests(const Connection& connection)
{
	if (!connection.Authenticated)
		return true; // Only the first message is ever handled, and it is size-limited
	return connection.GetPendingOutput() < c_OutputBackpressureThreshold && connection.RequestsInFlight < Specification.MaxRequestsInFlightPerClient && HasQueueRoom();
}

bool RpcServer::Impl::HasQueueRoom()
{
	if (QueuedBytes.load() < Specification.MaxQueuedBytes)
		return true;

	// ProcessRequests wakes this thread after draining the queue, but only if it sees the flag. Checking again
	// after raising it means a drain that happened in between is not missed (the atomics are sequentially
	// consistent: either ProcessRequests sees the flag, or this load sees the drained size).
	QueueBackpressured = true;
	return QueuedBytes.load() < Specification.MaxQueuedBytes;
}

bool RpcServer::Impl::WantsInput(const Connection& connection)
{
	if (connection.Closed || connection.PeerFinished)
		return false; // A finished peer stays readable (end of stream) forever
	if (connection.Closing)
		return true; // Drained and discarded so the final close is orderly
	return CanProcessRequests(connection);
}
```

1. **Lines 1364-1365:** a connection that has not proved the token is always read, because its messages are at most 4 KiB and only the opening exchange is accepted.
2. **Line 1366:** a client that has proved the token is read only while it has under 1 MiB of output waiting and fewer than 64 requests in flight, and while the global queue has room.
3. **Lines 1371-1378:** the queue has room while its bytes stay under 256 MiB; otherwise the thread raises a flag and checks the size again.
4. **Lines 1383-1387:** a finished peer is never read, and a closing connection is read only to throw the data away, so the close is orderly.

The comment of lines 1374 to 1376 is a lesson in :term[memory order]{id=memory-order}. The main thread drains the queue and wakes the network thread, but only if it sees the flag. Suppose the network thread tested the size, found the queue full, and only then raised the flag. A drain between the two steps would find no flag and send no wake-up, and the thread would sleep with an empty queue.

The code raises the flag first and tests again. The atomics use their default, sequentially consistent order, so either the main thread sees the flag or the network thread sees the drained size. Both cannot miss.

The same flow has a picture, with the three tests in order.

```mermaid caption="Where reading stops: three tests decide whether the thread reads a client, and when one fails the data waits in the system and the sender's window closes." alt="Three tests in a row check output waiting, requests in flight and room in the queue. If all pass, the thread reads the socket. If one fails, the bytes wait, the transmission window closes and the sender blocks until a drain or a written answer wakes the thread."
flowchart TD
	start["poll set is built"] --> a{"output waiting under 1 MiB?"}
	a -- yes --> b{"requests in flight under 64?"}
	a -- no --> stop
	b -- yes --> c{"queue under 256 MiB?"}
	b -- no --> stop
	c -- yes --> read["read the socket"]
	c -- no --> flag["raise the flag"] --> stop
	stop["do not read: bytes wait in the system buffer"] --> window["window closes: the sender blocks"]
	window --> wake["a drain or a written answer wakes the thread"]
	wake --> start
```

### The main thread's turn

Once per frame the editor calls `ProcessRequests`. The function does three things: it takes the queue, runs the handlers, and contains what they do wrong. The first part takes the queue and wakes the network thread.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1608-L1621"
std::vector<QueuedRequest> requests;
{
	std::scoped_lock<std::mutex> lock(m_Impl->QueueMutex);
	requests.swap(m_Impl->Queue);
	size_t dequeuedBytes = 0;
	for (const QueuedRequest& request : requests)
		dequeuedBytes += request.Size;
	m_Impl->QueuedBytes -= dequeuedBytes;
}
// The network thread stopped reading because the queue was full; now that it is drained, let it resume.
if (m_Impl->QueueBackpressured.exchange(false) && m_Impl->Shared)
	m_Impl->Shared->Wake();
if (requests.empty() || !m_Impl->Shared)
	return 0;
```

1. **Line 1611:** the queue is swapped into a local vector, so the mutex is held for a pointer swap and never during a handler.
2. **Line 1615:** the byte count falls by the size of what left, which lets the network thread read again.
3. **Lines 1618-1619:** the flag from the previous section is cleared, and the network thread is woken only if it raised it.

The second part walks the requests. It looks the handler up again, builds the responder and calls the handler inside a `try` block.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1623-L1672"
const WeakRef<RpcServerShared> weakShared = m_Impl->Shared;
for (QueuedRequest& request : requests)
{
	RpcHandler handler;
	{
		std::scoped_lock<std::mutex> lock(m_Impl->MethodsMutex);
		// Looked up again here: the method may have been unregistered since the request was queued, and its
		// handler's captures may no longer be valid.
		if (auto it = m_Impl->Methods.find(request.Method); it != m_Impl->Methods.end())
		{
			handler = it->second.Handler;
			m_Impl->RunningMethod = request.Method;
			m_Impl->ProcessingThread = std::this_thread::get_id();
		}
	}

	// A notification's "response" is never sent; delivering it only tells the network thread that the
	// notification no longer counts toward its client's in-flight budget.
	RpcResponder::DeliveryFunction deliver = [weakShared, connectionId = request.ConnectionId, id = request.Id, isNotification = request.IsNotification](RpcResult result)
	{
		if (Ref<RpcServerShared> shared = weakShared.lock())
			shared->Deliver(connectionId, id, isNotification ? RpcResult::Success(nullptr) : std::move(result), isNotification);
	};
	Ref<RpcResponder> responder = CreateRef<RpcResponder>(request.Method, std::move(deliver), RpcClientInfo { request.ConnectionId, request.ClientName, 0 });

	if (!handler)
	{
		responder->Respond(RpcResult::Failure(JsonRpc::ErrorCode::MethodNotFound, fmt::format("Method {} not found", QuoteMethod(request.Method))));
		continue;
	}

	// Handlers commonly read params with nlohmann::json accessors that throw on malformed input; contain
	// that here so one bad request cannot take down the main loop.
	try
	{
		handler(request.Params, responder);
	}
	catch (const std::exception& exception)
	{
		if (!responder->TryRespond(RpcResult::Failure(JsonRpc::ErrorCode::InternalError, fmt::format("Method {} failed: {}", QuoteMethod(request.Method), exception.what()))))
			ST_CORE_ERROR("RpcServer: method {} threw after responding: {}", QuoteMethod(request.Method), exception.what());
	}
	catch (...)
	{
		if (!responder->TryRespond(RpcResult::Failure(JsonRpc::ErrorCode::InternalError, fmt::format("Method {} failed with an unknown exception", QuoteMethod(request.Method)))))
			ST_CORE_ERROR("RpcServer: method {} threw after responding", QuoteMethod(request.Method));
	}

	// Release the handler copy before signalling, so UnregisterMethod callers may destroy its captures.
	handler = nullptr;
```

1. **Lines 1628-1636:** the method table is read again, because the method may have been removed since the request was queued and its captures may be gone; the handler is copied and its name noted.
2. **Lines 1641-1645:** the delivery function holds a weak reference to the shared state, so a responder that lives longer than the server finds nothing and does nothing.
3. **Lines 1648-1652:** a method that vanished is answered `MethodNotFound`, not skipped; the one-answer rule has no exception.
4. **Lines 1656-1669:** an exception from a handler becomes an `InternalError` answer, or only a log line when the handler had already answered.
5. **Line 1672:** the handler copy is released before the waiters of `UnregisterMethod` are signalled, so they may destroy whatever it captured.

The last point has a cost worth knowing. `UnregisterMethod` and `ReplaceMethod` wait for a handler that is running. They must not be called from a thread that is blocked by the main thread, or both wait for ever. The editor calls them from the main thread, so the case cannot arise.

### The responder

The responder is what makes the one-answer rule hold even when a handler forgets its duty. Two lines carry the rule: an atomic flag exchanged once, and a destructor that checks it.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L241-L273"
RpcResponder::~RpcResponder()
{
	if (m_Responded.exchange(true))
		return;

	// A destructor must not throw; delivery only allocates and enqueues, so a failure here can only be an
	// allocation failure, and the client then sees its connection close instead.
	try
	{
		if (m_Deliver)
			m_Deliver(RpcResult::Failure(JsonRpc::ErrorCode::InternalError, fmt::format("request dropped: {} finished without responding", QuoteMethod(m_Method))));
	}
	catch (...)
	{
	}
}

bool RpcResponder::TryRespond(RpcResult result)
{
	if (m_Responded.exchange(true))
		return false;
	if (!m_Deliver)
		return true;

	try
	{
		m_Deliver(std::move(result));
	}
	catch (const std::exception& exception)
	{
		ST_CORE_ERROR("RpcResponder: failed to deliver the response to {}: {}", QuoteMethod(m_Method), exception.what());
	}
	return true;
```

1. **Line 243:** `exchange(true)` sets the flag and returns the old value in one step, so of two threads that answer together exactly one sees `false`.
2. **Lines 248-255:** a destructor that finds no answer sent builds the "request dropped" error and delivers it; it catches everything, because a destructor must not throw.
3. **Lines 260-261:** `TryRespond` returns `false` for a second answer, and `Respond` logs that case as a warning.
4. **Lines 262-263:** a responder with no delivery function, such as one made for a test, counts as answered.

:::why[A destructor answers, not a rule for handlers]
Strata could write "every handler must answer" in a style guide. A handler that returns early, throws, or stores the responder in a list that is later cleared would break the guide silently, and the client would wait until its own timeout. The destructor turns the rule into a property of the type: the last owner of the responder is gone, so no one can answer any more, and the error goes out. The price is that the error says only "request dropped", with the method's name. The test `A dropped responder answers with an InternalError` pins this.
:::

### Deadlines and orderly close

`CheckDeadlines` runs for each connection in every pass. It has three duties in one function: it drops a stalled client, it ends an opening exchange that took too long, and it walks a closing connection through its last steps.

```cpp src="Strata/src/Strata/Network/RpcServer.cpp#L1250-L1296"
void RpcServer::Impl::CheckDeadlines(Connection& connection, std::chrono::steady_clock::time_point now)
{
	if (connection.Closed)
		return;

	// A client that keeps its connection open but stops reading would otherwise hold its output and its
	// in-flight slots forever. Nothing more can be sent to it, so it is dropped without a goodbye.
	if (connection.GetPendingOutput() > 0 && now - connection.LastSendProgress >= Specification.StalledClientTimeout)
	{
		uint64_t suppressed = 0;
		if (ProtocolWarnings.Allow(suppressed))
			ST_CORE_WARN("RpcServer: client {} has not accepted any output for {} ms; disconnecting{}", connection.Id, Specification.StalledClientTimeout.count(), DescribeSuppressed(suppressed));
		connection.Closed = true;
		return;
	}

	if (!connection.Authenticated && !connection.Closing && now >= connection.AuthenticationDeadline)
	{
		uint64_t suppressed = 0;
		if (AuthenticationWarnings.Allow(suppressed))
			ST_CORE_WARN("RpcServer: client {} did not authenticate in time{}", connection.Id, DescribeSuppressed(suppressed));
		Send(connection, JsonRpc::MakeError(nullptr, JsonRpc::ErrorCode::Unauthorized, "Authentication timed out"));
		BeginClose(connection, c_ErrorCloseLinger);
	}

	if (!connection.Closing)
		return;
	if (now >= connection.CloseDeadline)
	{
		connection.Closed = true;
		return;
	}
	if (connection.GetPendingOutput() > 0 || connection.RequestsInFlight > 0)
		return;

	// Everything is sent: end our stream once, then wait for the client's end so the close is orderly.
	if (!connection.SentShutdown)
	{
		connection.Socket.ShutdownSend();
		connection.SentShutdown = true;
		connection.CloseDeadline = std::min(connection.CloseDeadline, now + c_DrainTimeout);
	}
	// A stopping server does not wait for that: an idle client (e.g. an MCP server between tool calls) may only
	// notice the end of the stream when it next uses the connection. Its answers are sent, and a client that waits
	// for each answer before sending more has read them; anything it sends later finds the connection closed.
	if (connection.PeerFinished || DrainStarted)
		connection.Closed = true;
```

1. **Lines 1257-1263:** with output waiting and no progress for the stall timeout, 30 s, the connection is marked closed at once; the client gets no goodbye, because nothing can be sent to it.
2. **Lines 1266-1272:** a connection that has not proved the token by its deadline gets an error answer and starts to close.
3. **Lines 1277-1282:** a closing connection closes by force after its own deadline; before that, with output waiting or requests in flight, it waits, so its answers are not lost.
4. **Lines 1286-1291:** when everything is sent, the server ends its sending side once and gives the peer at most 2 s to do the same.
5. **Lines 1295-1296:** the connection closes when the peer's end arrives, or at once when the server itself is stopping.

The **stall timeout** is the time a client may leave its output waiting without accepting a byte of it. The test is "output waiting, and no progress for 30 s", so a client that reads 1 KiB every ten seconds never trips it. The slow client is throttled by the three predicates, and only the stalled one is dropped. The sketch of this page models the test with a stopped client and a slow one.

The lingers that start a close differ by reason. A close after an error lasts 2 s, so the error answer arrives. A close after a client :term[half-closes]{id=half-close} lasts 30 s, because such a client has sent everything and now reads the answers, which may take a while. A client that half-closes is not an error. It is how a program that sends its requests and waits for the replies says it is done.

### The editor's side: commands become methods

Everything so far is generic: the server knows methods, not commands. The editor's class `EditorAutomation` binds the two. It calls `SyncMethods` in every frame, and the function compares the registry's revision with the one it last saw. When the numbers match, the function returns at once. A command registered at run time bumps the revision, and the next frame offers it to clients.

```cpp src="StrataEditor/src/Editor/EditorAutomation.cpp#L240-L280"
void EditorAutomation::SyncMethods()
{
	const uint64_t revision = m_Commands.GetRevision();
	if (m_SyncedRevision == revision)
		return;

	std::map<std::string, Ref<const CommandMethod>> synced;
	for (const EditorCommand* command : m_Commands.GetAll())
	{
		const auto existing = m_Methods.find(command->Name);
		if (existing != m_Methods.end() && existing->second->Description == command->Description && existing->second->Parameters == command->Parameters)
		{
			synced.emplace(command->Name, existing->second);
			continue;
		}
		// New, or registered again with another description or schema: replaced in one step, so listings show the new
		// one and no request in between finds the method missing.
		Ref<const CommandMethod> method = CreateRef<CommandMethod>(CommandMethod { command->Name, command->Description, command->Parameters });
		RpcMethodInfo info;
		info.Name = command->Name;
		info.Description = command->Description;
		info.ParamsSchema = command->Parameters;
		const bool registered = m_Server.ReplaceMethod(std::move(info), RpcHandler([this, method](const nlohmann::json& params, const Ref<RpcResponder>& responder)
		{
			HandleRequest(method, params, responder);
		}));
		if (!registered)
		{
			ST_WARN("Automation: the command '{}' cannot be offered to clients (its name is reserved or invalid)", command->Name);
			continue;
		}
		synced.emplace(command->Name, std::move(method));
	}

	for (const auto& [name, method] : m_Methods)
	{
		if (!synced.contains(name))
			m_Server.UnregisterMethod(name);
	}
	m_Methods = std::move(synced);
	m_SyncedRevision = revision;
```

1. **Lines 242-244:** the revision check makes the common frame free of work.
2. **Lines 249-254:** a command whose description and schema have not changed keeps its method.
3. **Lines 257-265:** a new or changed command is registered through `ReplaceMethod`, which swaps the description, schema and handler in one step, so no request between two steps finds the method missing.
4. **Lines 266-270:** a command whose name is reserved or invalid is skipped with a warning.
5. **Lines 274-280:** methods whose command is gone are removed, and the table is replaced.

The handler of every method is the same function, `HandleRequest`, with the method's data captured. It refuses parameters given as an array, starts the command through the runner, and answers when the runner reports a result.

```cpp src="StrataEditor/src/Editor/EditorAutomation.cpp#L291-L329"
void EditorAutomation::HandleRequest(const Ref<const CommandMethod>& method, const nlohmann::json& params, const Ref<RpcResponder>& responder)
{
	Ref<RequestTrace> trace = CreateRef<RequestTrace>();
	trace->Id = m_State->NextRequestId++;
	trace->StartFrame = m_State->Frame;
	trace->StartTime = std::chrono::steady_clock::now();
	trace->Parameters = DescribeParameters(params);

	// JSON-RPC also allows positional (array) parameters; commands only take named ones.
	if (!params.is_object())
	{
		const EditorCommandResult invalid = EditorCommandResult::InvalidParameters(fmt::format("{} takes named parameters (a JSON object)", method->Name));
		RpcResult result = ToRpcResult(invalid, method->Name, method->Parameters);
		m_State->CompletedRequests++;
		LogCompletion(*trace, method->Name, result, m_State->Frame);
		responder->Respond(std::move(result));
		return;
	}

	// The completion may run after this object is gone (the runner cancels what is still pending when it is destroyed):
	// it only uses what it holds. A responder whose client disconnected discards the answer.
	const bool pending = m_Runner.Run(m_Context, m_Commands, method->Name, params, [state = m_State, method, responder, trace](const EditorCommandResult& result)
	{
		if (trace->Pending)
			state->PendingRequests--;
		state->CompletedRequests++;
		// The command may have opened or created a project: publish it before the client hears of it.
		if (state->RefreshSession)
			state->RefreshSession();
		RpcResult rpcResult = ToRpcResult(result, method->Name, method->Parameters);
		LogCompletion(*trace, method->Name, rpcResult, state->Frame);
		responder->Respond(std::move(rpcResult));
	}, CommandOrigin { CommandSource::Automation, responder->GetClient().Name });
	if (pending)
	{
		trace->Pending = true;
		m_State->PendingRequests++;
		ST_TRACE("Automation: #{} {} {} is pending", trace->Id, method->Name, trace->Parameters);
	}
```

1. **Lines 293-297:** a trace record is made first, with a number, the frame and the time, so the log can tell later how long the request took.
2. **Lines 300-307:** JSON-RPC allows parameters in an array; commands take named ones, so an array is answered `InvalidParams` with the schema in the error.
3. **Lines 312-323:** the runner starts the command, and the :term[lambda]{id=lambda} holds only shared state, because the runner may call it after the :term[automation]{id=automation} object is gone. Lines 318-319 refresh the session before the answer, so a client that opened a project finds the session file already moved.
4. **Line 323:** the command's origin is `Automation` plus the client's name, which the journal records.
5. **Lines 324-329:** a command that deferred is counted as pending and logged as such.

The last piece turns a command's result into a wire answer. The command's error kinds, taught on [the page on commands](../editor/commands.md), each have a code.

```cpp src="StrataEditor/src/Editor/EditorAutomation.cpp#L216-L237"
RpcResult EditorAutomation::ToRpcResult(const EditorCommandResult& result, const std::string& command, const nlohmann::json& parameterSchema)
{
	if (result.Success)
		return RpcResult::Success(result.Value);

	switch (result.ErrorKind)
	{
		case EditorCommandError::UnknownCommand:
			return RpcResult::Failure(JsonRpc::ErrorCode::MethodNotFound, result.Error);
		case EditorCommandError::InvalidParameters:
			// The schema lets a client correct its request without another round trip.
			return RpcResult::Failure(JsonRpc::ErrorCode::InvalidParams, result.Error, { { "command", command }, { "parameters", parameterSchema } });
		case EditorCommandError::Cancelled:
			return RpcResult::Failure(JsonRpc::ErrorCode::Cancelled, result.Error);
		case EditorCommandError::Internal:
			return RpcResult::Failure(JsonRpc::ErrorCode::InternalError, result.Error);
		case EditorCommandError::None:
		case EditorCommandError::Failed:
			break;
	}
	// Details the command gives with its failure (e.g. asset.delete's referencedBy).
	return RpcResult::Failure(JsonRpc::ErrorCode::OperationFailed, result.Error, result.ErrorData);
```

1. **Lines 223-224:** an unknown command is `MethodNotFound`, code -32601.
2. **Lines 225-227:** invalid parameters are -32602, and the schema goes into `data`, so the client corrects its request without another round trip.
3. **Lines 228-231:** a cancelled command is -32006, and an internal error is -32603.
4. **Lines 236-237:** every other failure, the ordinary "this cannot be done", is -32005, with the details the command gave, such as the list of what still uses an asset.

:::example[One `entity.create` from the socket to the journal]
A client sends one line of text with the method `entity.create` and a name. The network thread's loop reads the line from the socket and checks the limits: the message size, the id length, and a known method. It adds a queue entry and raises the client's requests in flight from 0 to 1. The line is at most a few hundred bytes, so the byte count of the queue barely moves.

The frame ends, and the next frame starts. The editor's layer runs the :term[command runner's]{id=command-runner} update, and then `EditorAutomation::Update`, which counts the frame, :term[syncs]{id=synchronization} the methods, updates the session and calls `ProcessRequests`. The queue holds one request. The handler `HandleRequest` makes a trace record and calls the runner with the origin `Automation` and the client's name. The command runs on the main thread, creates the entity inside a scene edit, and the journal writes one entry that says who did it.

The completion runs in the same call. It refreshes the session, converts the result, and writes one log line at trace level: the shape is `Automation: #<n> entity.create <parameters> -> ok (<time> ms)`. The responder delivers the answer to the outgoing list and wakes the network thread. The thread's next pass moves the answer into the connection, and `TransferResponses` writes it as text into the send buffer, which lowers the requests in flight to 0 and writes the bytes to the socket. Two threads, two hand-offs, one frame of waiting, one answer.
:::

## The limits that need no excerpt

The code above holds the main limits. The rest share a table, and the values that are set in code also appear in [the reference page on automation](../reference/automation.md).

| Limit | Value at the pin | What answers a client that reaches it |
| --- | --- | --- |
| Built-in methods | four, the prefix `rpc.` is reserved | The network thread answers them without the main thread; registering a method with that prefix fails |
| Method registry | one table with its own mutex; `RegisterMethod` refuses a duplicate | `ReplaceMethod` swaps in one step; `UnregisterMethod` waits for a running handler |
| Clients that proved the token | 8 | The ninth gets `ServerBusy` and a close, with a rate-limited warning |
| Requests in flight for one client | 64 | Reading stops until answers are written |
| Output waiting for one client | 1 MiB | Reading stops, and answers wait as values in the connection |
| Queued requests, all clients | 1024 | Reading continues, and each request beyond the limit is answered `ServerBusy` |
| Queued bytes, all clients | 256 MiB | Reading stops, and the main thread's drain wakes the thread |
| Reply size | 64 MiB, the message limit | An error replaces a reply that is too large |
| Request id | 256 characters | The request is refused, not echoed |
| Method name in an error | 64 characters, then dots | The message stays short |
| Closing connections beyond the limits | 16 | The oldest closing connection is dropped, so a flood cannot exhaust handles |
| Repeated warnings | one line per 5 s for each kind | The line carries the count of the lines it skipped |
| Stalled client | 30 s without accepted output | The connection closes without a goodbye |

The **graceful stop** is the last row of the story. `Stop` with a grace period first stops accepting connections and stops reading requests. It answers the queued requests with `Cancelled`, code -32006, since no `ProcessRequests` call will run them. It then keeps delivering answers, including ones that responders produce meanwhile on other threads, until every client has them or the **grace period** ends. The editor gives its server 2 s, so that the answer to `editor.quit` reaches its client before the process ends.

```mermaid caption="The order of a graceful stop: nothing new is accepted, the queue is cancelled, owed answers are delivered and each connection half-closes before the thread ends." alt="The editor cancels commands and removes its session file. The server stops accepting and reading, cancels queued requests, delivers owed answers and shuts each sending side. The thread ends when all connections are closed or the grace period of two seconds is over."
flowchart LR
	a["commands cancelled, session file removed"] --> b["listener closed, reading stops"]
	b --> c["queued requests answered: cancelled"]
	c --> d["owed answers delivered, also from other threads"]
	d --> e["each connection: send side shut"]
	e --> f["ends when all closed or the grace period is over"]
```

Three more details complete the table. Client presence: the server keeps the list of clients that proved the token, each with an id, a name and the time it connected, plus a counter that changes whenever the list changes. A caller reads the counter and copies the list only when the counter moved. A name is cut to 64 characters, stripped of control characters and repaired where it is not valid text, and it is used only to say who did something, never to decide trust. The notifier has an option, off for diagnosis only, that makes the thread poll every 5 ms instead.

The editor's own view shows in the command `editor.status` with the section `automation`. It reports whether the server runs, its address and port, and the number of clients with their names. It also reports the number of methods, the completed and pending requests, the pending commands, and whether the session file is published. Where it all runs in the editor's frame: the layer updates the context, then the command runner, then `EditorAutomation`, then the :term[command script]{id=command-script}. Because the runner comes first, a deferred command's poll runs before the next request is handled.

:::example[A deferred wait, and a client that leaves]
A client sends `editor.wait` with `frames` set to 10. The network thread queues it in a frame we call F. In frame F+1 the runner's update comes first, then `ProcessRequests` runs the handler. `HandleRequest` calls the runner, and the command returns `Defer`, so the request is pending, and the count of pending requests becomes 1. The responder stays with the runner's completion; no answer exists yet.

From frame F+2 the runner polls the command once per frame, and the command counts down from 10. Meanwhile the network thread reads other requests from the same client, up to 64 in flight, and the main thread runs them in the frames between. The wait does not block them, because it is a poll, not a loop. On the tenth poll, in frame F+11, the command completes and the completion calls `Respond`. The answer travels to the outgoing list, the notifier wakes the thread, and the client hears of it about 10 frames after the handler ran, which is about 167 ms at 60 frames per second.

Suppose the client closes its connection in frame F+5. The network thread removes the connection and its id leaves the table of open connections. The command is not cancelled: it still counts down and completes in frame F+11. Its `Respond` calls `Deliver`, which finds no open connection with that id and returns. The command had its effect, and only the answer was lost; the test `A client that disconnects while its command is pending loses only the answer` pins exactly this.
:::

```mermaid caption="A deferred request over frames: the answer comes ten frames after the handler, other requests continue meanwhile, and a disconnect loses only the answer." alt="The client sends a wait request, which the main thread defers and polls once per frame. A status request sent meanwhile is answered in the next frame. After the client disconnects, the command still completes, but its answer finds no connection and is dropped."
sequenceDiagram
	participant C as client
	participant N as network thread
	participant M as main thread
	C->>N: wait, frames 10
	N->>M: queue entry
	M->>M: handler runs, command defers
	C->>N: editor.status
	N->>M: queue entry
	M-->>C: status answered in the next frame
	M->>M: poll 1 to 9, one per frame
	C--xN: disconnects
	M->>M: poll 10, command completes
	M--xN: Respond finds no connection, answer dropped
```

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Handle requests on the network thread, with locks | Many general-purpose servers and web frameworks | No wait of up to one frame; handlers run at once | Every system that touches the scene needs the locks; one missed lock is a race |
| A thread per connection | Simple blocking servers | Simple code for each client | A stack per client, which a hostile client multiplies; the same races |
| An event loop on the main thread | Single-threaded servers and some games | No second thread, no hand-off | Frame time spent on the network; every read must be a small step |
| A queue to the main thread (chosen) | Editors and tools with one owner of their data | Handlers need no locks; the frame never waits for a socket | Up to one frame of latency per request; a bounded queue to tune |
| A pipe or a named handle instead of TCP | Local tools on one operating system | No port for other programs to find | A different code for each system; no common protocol for the :term[command line]{id=terminal-command} client, the MCP server and the tests |
| Drop the slow reader at once | Servers that favour their own memory | Smaller state; no throttling code | Honest clients that read late lose their answers |
| Buffers with no limit | Prototypes | No limits to tune | A hostile client can grow memory without end |

The sources for these designs are listed in Further reading. Strata keeps TCP on the loopback address because the same server then serves the :term[command line]{id=terminal-command} client, the Model Context Protocol (MCP) server and the tests, with one protocol on every system.

## How it is tested

Two suites test the server, and one tests the editor's side. A test is run by name, for example `StrataTests --test-suite=Network.RpcServer`. [The page on the feature test](../engineering/feature-test.md) explains why automation is not part of it: no case of the feature test project exercises the server, and the kinds that it counts do not include commands. The suites below are the tests.

`Network.RpcServer` holds the cases of the server. The groups that matter for this page are these:

- Round trips and registration: requests round-trip, `rpc.listMethods` describes built-in and registered methods, and unknown or removed methods report `MethodNotFound`.
- Threading: requests wait for `ProcessRequests` on the owning thread, deferred responders answer from another thread, and responses from other threads arrive without the notifier.
- One answer: `A dropped responder answers with an InternalError`, and destroying the server while another thread holds a responder is safe.
- Bounds: the requests in flight, the queue's count and its bytes are limited, replies stay bounded whatever the request contains, and oversized messages close the connection cleanly.
- Backpressure: `A client that stops reading is throttled, not dropped`, `Pipelined large responses reach a client that reads them late`, and `A client that stops accepting output is disconnected after the stall timeout`.
- Registry: removing and replacing a method wait for the running handler.
- Closing: a client that half-closes still receives its answers, and the graceful stop cases deliver what is owed, do not wait for idle clients, and end with the grace period.

The cases of the opening exchange in the same suite are read on [the security page](../automation/security.md). `Network.RpcPresence` holds two cases for client names: a client may name itself and the server lists it, and names are bounded and stripped of control characters.

`Editor.Automation` checks the editor's side. Every command is a method with its description and schema, and requests run commands and answer with their results. Failures become errors by kind, and a deferred command answers when its poll finishes. A client that disconnects loses only the answer. Pending requests get answers when the editor closes, and `editor.quit` gets its answer first.

The helpers live in `StrataTests/src/Network/NetworkTestHelpers.h`. `PumpedRpcServer` runs a server whose `ProcessRequests` a second thread calls every millisecond, so tests need no :term[frame loop]{id=game-loop}. `RawRpcConnection` sends hand-made lines, including broken ones. `LiveProcess` starts a built program, and a fake editor process stands in for the editor in the tests of the command line client. Tests wait by the clock or by a condition, never by counting frames, because a loaded machine runs frames at an unknown pace.

## Changing it safely

The server has three extension points, and each has a way to go wrong.

A new built-in method belongs in the network thread's list of built-ins. It must answer without the main thread, so it may read only what the network thread owns or what is shared under a mutex. If it needs the scene, it is not a built-in: register a command.

New behaviour in an existing command needs no server code. The command registers with a description and a complete schema, and `SyncMethods` offers it in the next frame. The checks that matter are the ones of [the page on commands](../editor/commands.md): it rejects invalid input without side effects, and a command that waits returns a deferred result.

A new limit needs a place in `RpcServerSpecification`, a test that pushes a client over it, and an answer that fits the contract. Throttle when the peer may be honest, drop when it holds resources for nothing, and use `ServerBusy` when the server cannot take more work. Whatever the limit is, it must keep the one-answer rule.

The rules that apply, with their reasons:

- **Never touch engine state from the network thread.** Add the work to a handler. The reason is the :term[lock-free]{id=lock-free} scene.
- **Never answer a request in two ways.** Keep the responder in one place. A second `Respond` is ignored with a warning, which is a sign of a bug.
- **Never let a handler wait.** Return `Defer`. A waiting handler stops every client.
- **Never add an RPC endpoint for a feature.** Register a command.
- **Never hold a mutex across handler code.** `ProcessRequests` copies what it needs and releases the lock first; `UnregisterMethod` depends on it.

Before a commit, run `Network.RpcServer`, `Network.RpcPresence` and `Editor.Automation`, and read the :term[diff]{id=diff} for any shared state that the network thread now reads. A new field of `Connection` is safe, because the network thread owns connections. A new field of the shared state needs the mutex.

## Summary

- A request crosses two threads. The network thread reads and validates it and queues it, the main thread runs the handler once per frame, and the responder carries the answer back and wakes the network thread through the notifier.
- Every request gets exactly one answer. A responder answers at most once, answers an error when it dies with no answer sent, and a server that stops with a grace period cancels queued requests.
- Each kind of bad behaviour meets a limit. A flood meets the queue and `ServerBusy`; a slow reader meets throttling; a stalled client meets the 30 s timeout; a client that takes many slots meets the client limit.
- Commands become methods when the registry's revision changes, they run through the runner with the origin `Automation`, and their error kinds map to the codes -32601, -32602, -32005, -32006 and -32603.
- New behaviour comes through a command or a limit with a test, never through an endpoint, a lock in the network thread or a handler that waits.

## Check yourself

1. A client sends 70 requests at once, and the main thread is busy for 200 ms. Which statement is right? (a) The server answers 6 requests with `ServerBusy`. (b) The server reads 64 requests and leaves the other 6 in the operating system until answers are written. (c) The server queues all 70 and grows its memory.

   :::answer{tests="name-limit"}
   Option (b) is right. The limit is 64 requests in flight for one client, so the poll set stops listening to its socket at 64, and the rest wait in the system buffer. Option (a) confuses the in-flight limit with the global queue, which answers `ServerBusy` only when its 1024 requests are used. Option (c) ignores the bound.
   :::

2. A handler stores its responder in a list and then the list is cleared by mistake. What does the client see, and why does it not wait for ever?

   :::answer{tests="one-answer"}
   The client gets an `InternalError` with the text "request dropped" and the method's name. Clearing the list destroys the last owner of the responder, and the destructor finds that no answer went out, so it delivers one. The guarantee belongs to the type, not to the handler.
   :::

3. A client accepts 1 KiB of output every 10 s for ten minutes, and another accepts nothing after its first read. Which one does the server drop, and when?

   :::answer{tests="name-limit"}
   The server drops the second client, 30 s after the last byte it accepted. The slow client makes progress every 10 s, which is less than 30 s, so the test "no progress for 30 s" never fires. The server only throttles it: it reads no new request while 1 MiB of output waits.
   :::

4. A client sends a request with its parameters as an array, `[1, 2]`. Which code and data does it get back, and which function made the answer?

   :::answer{tests="commands-methods"}
   The client gets code -32602, `InvalidParams`, with `data` holding the command name and the parameter schema. `HandleRequest` refuses the array, and `ToRpcResult` builds the answer from an `InvalidParameters` result, so the client can correct its request without asking again.
   :::

5. Why does `HasQueueRoom` raise the flag first and test the size again?

   :::answer{tests="trace-request"}
   The main thread wakes the network thread after a drain only when it sees the flag. If the thread tested the size and then raised the flag, a drain between the two steps would send no wake-up, and the thread would sleep with an empty queue. With the flag raised first, either the main thread sees it, or the second test sees the drained size.
   :::

6. A teammate wants a new method that counts the entities of the scene and proposes to read the scene on the network thread, so that the answer skips the wait for the frame. What do you answer?

   :::answer{tests="extend-safely"}
   Refuse the plan and register a command instead. The network thread must never touch engine state, because the scene belongs to the main thread, and a read during a frame is a data race. The cost of the command is up to one frame of latency. `SyncMethods` offers it in the next frame, and `Editor.Automation` shows the pattern in its tests.
   :::

## Exercises

1. **Basic.** The stall sketch of this page has a client that stops reading and a client that reads slowly. Predict the time at which the server drops the first one and the bytes it still holds, before you read the answer. Then say what changes if the first client stops at 10.5 s instead of 3.5 s.

   :::answer[Worked solution]{tests="name-limit"}
   The sketch below models the stall test of `CheckDeadlines`: output waiting and no progress for 30 s. The client `stopped` takes 20,000 bytes at each full second until 3.5 s, so its last progress is at 3 s with 40,000 bytes left. The test fires when the time minus 3000 ms reaches 30,000 ms, at 33,000 ms. The client `slow` makes progress every 10 s, so it stays.

   ```cpp sketch="automation-rpc-server-stall.cpp"
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>

   constexpr int64_t c_StallTimeoutMs = 30000;

   // What the server remembers about one client's output.
   struct Client
   {
   	const char* Name = "";
   	int64_t PendingBytes = 0;
   	int64_t LastProgressMs = 0;
   	int64_t ReadEveryMs = 0;     // The client takes some bytes this often
   	int64_t BytesPerRead = 0;
   	int64_t StopsReadingMs = -1; // -1: the client never stops
   	bool Closed = false;
   };

   // The client's side: the socket takes bytes only while the client reads.
   void Flush(Client& client, int64_t nowMs)
   {
   	if (client.Closed || client.PendingBytes == 0 || nowMs % client.ReadEveryMs != 0)
   		return;
   	if (client.StopsReadingMs >= 0 && nowMs >= client.StopsReadingMs)
   		return;
   	client.PendingBytes -= std::min(client.PendingBytes, client.BytesPerRead);
   	client.LastProgressMs = nowMs;
   }

   // The server's side: output waiting and no progress for the timeout means a stalled client.
   void CheckDeadline(Client& client, int64_t nowMs)
   {
   	if (client.Closed || client.PendingBytes == 0)
   		return;
   	if (nowMs - client.LastProgressMs >= c_StallTimeoutMs)
   	{
   		client.Closed = true;
   		std::printf("%s dropped at %lld ms with %lld bytes waiting\n", client.Name, static_cast<long long>(nowMs), static_cast<long long>(client.PendingBytes));
   	}
   }

   int main()
   {
   	Client clients[2];
   	clients[0] = { "stopped", 100000, 0, 1000, 20000, 3500, false };
   	clients[1] = { "slow", 100000, 0, 10000, 1000, -1, false };
   	for (int64_t nowMs = 1000; nowMs <= 100000; nowMs += 1000)
   	{
   		for (Client& client : clients)
   		{
   			Flush(client, nowMs);
   			CheckDeadline(client, nowMs);
   		}
   	}
   	for (const Client& client : clients)
   		std::printf("%s: %s, %lld bytes waiting\n", client.Name, client.Closed ? "closed" : "connected", static_cast<long long>(client.PendingBytes));
   	return 0;
   }
   ```

   ```text output-of="automation-rpc-server-stall.cpp"
   stopped dropped at 33000 ms with 40000 bytes waiting
   stopped: closed, 40000 bytes waiting
   slow: connected, 90000 bytes waiting
   ```

   1. **Lines 22-27:** the socket takes bytes only while the client reads, and the time of the last progress moves only when bytes moved.
   2. **Lines 35-38:** the stall test needs both output waiting and 30 s without progress.
   3. **Lines 45-46:** `stopped` reads 20,000 bytes each second until 3.5 s; `slow` reads 1,000 bytes every 10 s and never stops.

   With a stop at 10.5 s the client reads five times, at 1 to 5 s, and 5 times 20,000 bytes empties the 100,000 waiting. No output waits after that, so the test never fires and the server does not drop it.
   :::

2. **Medium.** Trace it yourself. Follow one `entity.create` from `RunIteration` to `HandleRequest` and to its journal entry. Name the function that queues the request, the function that runs it and the place where the journal records the origin.

   :::answer[Worked solution]{tests="trace-request"}
   In `Strata/src/Strata/Network/RpcServer.cpp`, `ReadFrom` leads to `ProcessBufferedLines`, which validates the line and pushes the queue entry. `ProcessRequests` runs the handler that `SyncMethods` registered, which is `EditorAutomation::HandleRequest` in `StrataEditor/src/Editor/EditorAutomation.cpp`. It calls `EditorCommandRunner::Run` with the origin `CommandSource::Automation` and the client's name, and the runner's journal entry carries it. Set a breakpoint in each function and send the command with `StrataCLI`.
   :::

3. **Hard.** Send `editor.wait` with `frames` set to N, together with `rpc.ping` and one `entity.create`. Then read the trace lines with the command `log.read` and `minLevel` set to `Trace`. Say in which order the three answers arrive and why the wait does not delay the others.

   :::answer[Worked solution]{tests="trace-request,one-answer"}
   `editor.wait` is registered with `MayDefer` and returns a deferred result. The ping is a built-in, so the network thread answers it first, without the main thread. The `entity.create` runs in the first frame that handles the queue and answers at once. The wait answers about N frames later, because its poll runs once per frame and holds no thread.

   Only the trace line of the wait carries a frame count: `entity.create` never pended, and the ping, a built-in, writes no trace line at all. It shows N - 1, not N: the completion runs in the runner's update, before `EditorAutomation::Update` counts the new frame.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Network/RpcServer.h` and `RpcServer.cpp`: the server, the responder and the method registry.
- `Strata/src/Strata/Network/JsonRpc.h`: the wire format and the error codes.
- `Strata/src/Platform/Windows/WindowsSocket.cpp` and `Strata/src/Platform/Posix/PosixSocket.cpp`: `SocketNotifier`, the notifier of each system.
- `StrataEditor/src/Editor/EditorAutomation.cpp`: `SyncMethods`, `HandleRequest`, `ToRpcResult`, the trace log and the status section.
- `StrataEditor/src/EditorLayer.cpp`: `EditorLayer::OnUpdate`, where `EditorAutomation::Update` runs after the command runner.
- Tests: `StrataTests/src/Network/RpcServerTests.cpp`, `StrataTests/src/Editor/EditorAutomationTests.cpp` and `StrataTests/src/Network/NetworkTestHelpers.h`.
- Command: `editor.status` with the section `automation`; `editor.wait` as a deferred command to watch.

## Further reading

- The Linux manual page of `socketpair`, the call that gives POSIX its notifier: intermediate.
- The manual page of `poll` on POSIX systems, for the readiness set that the network thread waits on: intermediate.
- The JSON-RPC 2.0 specification: what a request, a notification and an error code are: beginner.
- Gaffer On Games, on networking and flow control with a fixed bound per peer: intermediate.
- Brian Hall, "Beej's Guide to Network Programming", on sockets, blocking and the TCP window: beginner.
