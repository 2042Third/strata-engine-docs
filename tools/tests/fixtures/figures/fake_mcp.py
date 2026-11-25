"""A stand-in for StrataCLI mcp (tests of booklib.editor.McpClient): JSON-RPC 2.0 over standard input and output, one
message per line. It lists only its own tools until the second tools/list (the editor is reached then), answers
strata_call with what it was asked, the client's name and whether a token reached its environment, fails the method
"broken", and sends a notification before each answer, which the client skips."""

import json
import os
import sys

client = None
lists = 0
for line in sys.stdin:
    message = json.loads(line)
    if 'id' not in message:
        continue
    method, params = message['method'], message.get('params') or {}
    sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/tools/list_changed'}) + '\n')
    if method == 'initialize':
        client = params['clientInfo']['name']
        result = {'protocolVersion': params['protocolVersion'], 'serverInfo': {'name': 'strata'}}
    elif method == 'tools/list':
        lists += 1
        result = {'tools': [{'name': 'strata_call'}] + ([{'name': 'editor_status'}] if lists >= 2 else [])}
    elif method == 'tools/call' and params['arguments']['method'] == 'broken':
        result = {'content': [{'type': 'text', 'text': 'Error -32000: the command failed'}], 'isError': True}
    elif method == 'tools/call':
        answer = {'method': params['arguments']['method'], 'params': params['arguments']['params'], 'client': client, 'arguments': sys.argv[1:],
                  'token': 'STRATA_EDITOR_TOKEN' in os.environ or 'STRATA_EDITOR_PORT' in os.environ}
        result = {'content': [{'type': 'text', 'text': json.dumps(answer)}], 'structuredContent': answer, 'isError': False}
    else:
        sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32601, 'message': 'no such method'}}) + '\n')
        sys.stdout.flush()
        continue
    sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': message['id'], 'result': result}) + '\n')
    sys.stdout.flush()
