# Part review: automation/rpc-server

- wrong: the limits table said reading stops at 1024 queued requests; only the byte limit stops reading (`HasQueueRoom`), and a request beyond the count is answered `ServerBusy` (`RpcServer.cpp`, the queue push): "Reading continues, and each request beyond the limit is answered `ServerBusy`".
- contradiction: the deferred-wait sequence diagram queued a ping to the main thread, while the page (and Exercise 3) has `rpc.ping` answered by the network thread as a built-in; the diagram's meanwhile request is now `editor.status`, answered in the next frame (alt changed to match).
- wrong: Exercise 3's answer said the two other requests' trace lines carry no frame count because they never pended; `rpc.ping` writes no `Automation:` trace line at all (built-ins skip `HandleRequest`): now says so.
