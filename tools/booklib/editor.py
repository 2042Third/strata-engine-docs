"""Running the engine's programs at the pin, as plan/pipelines.md §1.4 and §2 say: the preflight checks, the
environment every program gets, StrataCLI calls with parameter files, and ending what a run started.

- preflight_clone: checks 1 and 2 of §1.4 (the clone has the pin, its HEAD is the pin, it is clean).
- preflight_build: check 3 (the build holds the programs).
- Editor.check_commit: check 4 (editor.status reports an engineCommit that is a prefix of the pin); a provisional build
  (one that is not the pin's, for trying recipes before the pin has what they need) is reported instead of refused.
- window_arguments: an editor in a window of exactly window["size"] pixels at UI scale 1 that keeps its panels' layout in
  window["layout"] (editor figures, plan/pipelines.md §5.4). It runs a command script without automation: StrataCLI
  launch takes no --layout (an editor started without one reads and writes the person's own layout), and an editor that
  automation drives shows it in the picture (the status bar's "Agent connected", the Scene view's "Agent: <command>").
- Program: a program started in the background (an editor in a window), its output in a file of the log folder, so
  that a long-running editor never fills a pipe; finish() waits for it, ends its tree after the time limit and logs it.
- Editor with window: an editor in a window that serves automation (live figures: the Game view presents what a live
  capture reads), started directly with window_arguments, since StrataCLI launch takes no --layout, and driven through
  StrataCLI call like the others.
- McpClient: StrataCLI mcp in the run's session folder, an MCP client that names itself (initialize's clientInfo) and
  sends commands through the strata_call tool, so that the editor shows a named agent connected (automation figures).
  It finds the editor through the session file, which the tool never reads: no token passes through the tool, its
  output or its log.
- environment: STRATA_SESSION_DIR is a new folder StrataDocs-<pid>-<seconds> in the user's temporary folder, which the
  tool names but never creates (the editor and the CLI create it private; the authoring drive keeps no permissions, so it
  is never under the work folder); STRATA_RECENT_PROJECTS and STRATA_SCRIPT_BUILDS_DIR are in the work folder;
  STRATA_EDITOR_PATH names the build's editor. An explicit endpoint (STRATA_EDITOR_PORT, STRATA_EDITOR_TOKEN) is never
  passed on. The user's temporary folder is STRATA_DOCS_SYSTEM_TEMP when set (the book's env.sh keeps the original
  there, since it points TEMP at .tools/tmp), else Python's. MSBUILDDISABLENODEREUSE=1 keeps the MSBuild nodes of a
  script build from outliving the build (the pin build sets it for the same reason), so that a run leaves nothing
  running.

Every command and every program's output goes to the run's log folder. A program that passes its time limit is ended
with everything it started. Nothing here holds a machine path: the clone, the build and the work folder come from the
caller.
"""

import json
import os
import shutil
import subprocess
import tempfile
import time

from booklib import steps

c_CallSeconds = 300
c_OpenSeconds = 900
c_QuitSeconds = 30
c_IdleSeconds = 900
c_Programs = ('StrataEditor', 'StrataCLI', 'StrataRuntime')


class PreflightError(Exception):
    """A preflight check failed (§1.4): exit code 2, before anything starts."""


class EditorError(Exception):
    """A command or a program failed: exit code 1."""


class CommandError(EditorError, steps.CommandFailed):
    """The editor answered the command with an error (StrataCLI prints the JSON-RPC error object): until asks again."""


def system_temp():
    return os.environ.get('STRATA_DOCS_SYSTEM_TEMP') or tempfile.gettempdir()


def new_session_dir():
    """A session folder that does not exist yet, in the user's temporary folder (§2)."""
    base = os.path.join(system_temp(), 'StrataDocs-%d-%d' % (os.getpid(), int(time.time())))
    path = base
    number = 1
    while os.path.exists(path):
        number += 1
        path = '%s-%d' % (base, number)
    return path


def program_path(build, name):
    return os.path.join(build, name + ('.exe' if os.name == 'nt' else ''))


def environment(build, work, session):
    env = {key: value for key, value in os.environ.items() if key not in ('STRATA_EDITOR_PORT', 'STRATA_EDITOR_TOKEN')}
    env['STRATA_SESSION_DIR'] = session
    env['STRATA_RECENT_PROJECTS'] = os.path.join(work, 'recent-projects.json')
    env['STRATA_SCRIPT_BUILDS_DIR'] = os.path.join(work, 'script-builds')
    env['STRATA_EDITOR_PATH'] = program_path(build, 'StrataEditor')
    env['MSBUILDDISABLENODEREUSE'] = '1'
    return env


def git(engine_path, *arguments):
    result = subprocess.run(['git', '-C', engine_path] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace')


def preflight_clone(engine, pin):
    """§1.4 checks 1 and 2 for the pin clone (a booklib.repo.Engine): raises PreflightError with what to do."""
    try:
        commit = engine.resolve(pin)
    except Exception as error:  # repo.EngineError; kept general so this module does not import repo
        raise PreflightError('%s (pipelines.md §1.4, check 1)' % error)
    code, head, error = git(engine.path, 'rev-parse', 'HEAD')
    if code != 0 or head.strip() != commit:
        raise PreflightError('the clone %s is at %s, not at the pin %s: run git checkout --detach %s there '
                             '(pipelines.md §1.3; §1.4, check 2)' % (engine.path, head.strip()[:12] or error.strip(), commit[:12], commit))
    code, status, error = git(engine.path, 'status', '--porcelain')
    if code != 0 or status.strip():
        first = (status.strip().splitlines() or [error.strip()])[0]
        raise PreflightError('the clone %s is not clean (git status --porcelain prints "%s"): restore it before taking '
                             'pictures or running tutorials (pipelines.md §1.3; §1.4, check 2)' % (engine.path, first))
    code, submodules, error = git(engine.path, 'submodule', 'status')
    if code != 0:
        raise PreflightError('git submodule status in %s: %s (pipelines.md §1.4, check 2)' % (engine.path, error.strip()))
    for line in submodules.splitlines():
        if line and line[0] != ' ':
            raise PreflightError('the submodule "%s" of %s is not at the commit the pin records: run git submodule update '
                                 '--init --recursive --depth 1 there (pipelines.md §1.3; §1.4, check 2)' % (line[1:].split()[1] if len(line.split()) > 1 else line, engine.path))
    return commit


def preflight_build(build, programs):
    """§1.4 check 3: the build holds every program named."""
    if not build:
        raise PreflightError('name the pin build with --build <folder> (pipelines.md §1.2)')
    missing = [name for name in programs if not os.path.isfile(program_path(build, name))]
    if missing:
        raise PreflightError('the build %s lacks %s (pipelines.md §1.4, check 3): build the pin (§1.3)'
                             % (build, ', '.join(os.path.basename(program_path(build, name)) for name in missing)))


def file_sha256(path):
    import hashlib
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def build_record(build, engine_path):
    """The build as a stamp records it (pipelines.md §6.4): its kind, its configuration and the editor's SHA-256."""
    inside = os.path.normcase(os.path.abspath(build)).startswith(os.path.normcase(os.path.abspath(engine_path)) + os.sep)
    record = {'kind': 'pin-build' if inside else 'package', 'configuration': os.path.basename(os.path.normpath(build)),
              'editorSha256': file_sha256(program_path(build, 'StrataEditor'))}
    if not inside:
        record['package'] = os.path.basename(os.path.dirname(os.path.normpath(build))) or os.path.basename(os.path.normpath(build))
    return record


def process_alive(pid):
    if os.name == 'nt':
        import ctypes
        synchronize, query = 0x00100000, 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(synchronize | query, False, pid)
        if not handle:
            return False
        try:
            return ctypes.windll.kernel32.WaitForSingleObject(handle, 0) == 0x102  # WAIT_TIMEOUT: still running
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def own_group():
    """Popen's options that start a program as the leader of a process group of its own on POSIX (a new session), so
    that end_process_tree ends it with what it started and nothing else. Windows ends a tree by its parent links."""
    return {} if os.name == 'nt' else {'start_new_session': True}


def end_process_tree(pid):
    """Ends a process and everything it started. On POSIX the process's group is ended only when the process leads it
    (started with own_group()): a program that shares the caller's group is ended alone, because signalling that
    group would end the caller too (CI's unit-test step died so, without a word)."""
    if os.name == 'nt':
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        import signal
        try:
            group = os.getpgid(pid)
        except OSError:
            group = None
        if group == pid and group != os.getpgrp():
            try:
                os.killpg(group, signal.SIGKILL)
                return
            except OSError:
                pass
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


class Log:
    """The run's log folder: one numbered file per command or program, with its arguments and output."""

    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.number = 0

    def write(self, name, arguments, output, code):
        self.number += 1
        safe = ''.join(char if char.isalnum() or char in '.-' else '-' for char in name)[:60]
        path = os.path.join(self.folder, '%04d-%s.log' % (self.number, safe))
        with open(path, 'w', encoding='utf-8', newline='\n') as file:
            file.write('$ %s\nexit code: %s\n\n%s' % (' '.join(arguments), code, output))
        return path


def run_program(arguments, env, log, name, timeout, cwd=None, merge=True):
    """(exit code, output, errors) of a program. With merge, output holds stdout and stderr in the order the program wrote
    them and errors is empty; without it, output is stdout and errors stderr. A program still running after timeout
    seconds is ended with every process it started (a script build's compilers, an editor's children), and EditorError
    says so."""
    try:
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT if merge else subprocess.PIPE,
                                   env=env, cwd=cwd, **own_group())
    except OSError as error:
        raise EditorError('%s could not start: %s' % (arguments[0], error))
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        end_process_tree(process.pid)
        try:
            stdout, stderr = process.communicate(timeout=c_QuitSeconds)
        except subprocess.TimeoutExpired:
            # Something outside the tree still holds the program's output; the output so far is lost, the run is not.
            process.kill()
            stdout = b'(the output could not be read after the program was ended)'
        output = (stdout or b'').decode('utf-8', 'replace')
        log.write(name, arguments, output + '\n(ended after %d seconds)' % timeout, 'timeout')
        raise EditorError('%s did not end within %d seconds and was ended with what it started (log in %s)' % (name, timeout, log.folder))
    output = stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
    errors = '' if merge else stderr.decode('utf-8', 'replace').replace('\r\n', '\n')
    log.write(name, arguments, output + ('\n--- stderr ---\n' + errors if errors else ''), process.returncode)
    return process.returncode, output, errors


class Program:
    """A program running in the background: its output goes to a file of the log folder (an editor in a window writes
    its log for as long as it runs, more than a pipe holds unread)."""

    def __init__(self, arguments, env, log, name, cwd=None):
        self.arguments = [str(argument) for argument in arguments]
        self.log = log
        self.name = name
        log.number += 1
        safe = ''.join(char if char.isalnum() or char in '.-' else '-' for char in name)[:60]
        self.path = os.path.join(log.folder, '%04d-%s.out' % (log.number, safe))
        self.file = open(self.path, 'wb')
        try:
            self.process = subprocess.Popen(self.arguments, stdout=self.file, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, cwd=cwd,
                                            **own_group())
        except OSError as error:
            self.file.close()
            raise EditorError('%s could not start: %s' % (self.arguments[0], error))
        self.pid = self.process.pid

    def alive(self):
        return self.process.poll() is None

    def output(self):
        with open(self.path, 'rb') as file:
            return file.read().decode('utf-8', 'replace').replace('\r\n', '\n')

    def finish(self, timeout):
        """(exit code, output): waits up to timeout seconds, then ends the program with everything it started."""
        code = None
        try:
            code = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            end_process_tree(self.pid)
            try:
                self.process.wait(timeout=c_QuitSeconds)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.file.close()
        output = self.output()
        self.log.write(self.name, self.arguments, output + ('' if code is not None else '\n(ended after %d seconds)' % timeout),
                       code if code is not None else 'timeout')
        if code is None:
            raise EditorError('%s did not end within %d seconds and was ended with what it started (log in %s)' % (self.name, timeout, self.log.folder))
        return code, output


class Editor:
    """One editor started through StrataCLI launch, driven with StrataCLI call (as Tools/LookDev.py drives them). With
    window ({size, layout}) and a project, the editor runs in a window of that size with automation (live figures):
    started directly, as StrataCLI launch takes no --layout, and found by StrataCLI call through the run's session
    folder."""

    def __init__(self, build, work, log, project=None, gpu=False, window=None):
        self.build = build
        self.work = work
        self.log = log
        self.project = project
        self.gpu = gpu
        self.window = window
        self.session = new_session_dir()
        self.env = environment(build, work, self.session)
        self.cli = program_path(build, 'StrataCLI')
        self.pid = None
        self.program = None
        self.calls = 0

    def launch_window(self):
        arguments = window_arguments(self.build, self.window) + ['--project', self.project, '--idle-timeout', str(c_IdleSeconds)]
        self.program = Program(arguments, self.env, self.log, 'window-editor')
        self.pid = self.program.pid
        deadline = time.monotonic() + c_OpenSeconds
        while True:
            try:
                self.call('editor.status', {'sections': ['engine']}, timeout=60)
                break
            except EditorError as error:
                if not self.program.alive():
                    code, output = self.program.finish(c_QuitSeconds)
                    self.pid = None
                    raise EditorError('the editor in a window exited with %d before it served automation: %s' % (code, last_line(output)))
                if time.monotonic() > deadline:
                    raise EditorError('the editor in a window did not serve automation within %d seconds: %s' % (c_OpenSeconds, error))
                time.sleep(1)
        self.call('scene.loadStatus', {'wait': True}, timeout=c_OpenSeconds)
        return {'ProcessId': self.pid}

    def launch(self):
        if self.window:
            return self.launch_window()
        # With the GPU the editor still runs without a window (--headless): viewport.capture renders offscreen.
        arguments = [self.cli, 'launch'] + (['--headless'] if self.gpu else ['--no-gpu'])
        if self.project:
            arguments += ['--project', self.project]
        arguments += ['--idle-timeout', str(c_IdleSeconds)]
        code, output, errors = run_program(arguments, self.env, self.log, 'launch', c_OpenSeconds, merge=False)
        if code != 0:
            raise EditorError('StrataCLI launch exited with %d: %s' % (code, last_line(errors or output)))
        started = parse_json_object(output)
        if not isinstance(started, dict) or not isinstance(started.get('ProcessId'), int):
            raise EditorError('StrataCLI launch did not print the editor it started: %s' % last_line(output))
        self.pid = started['ProcessId']
        return started

    def call_arguments(self, command, parameters, timeout):
        self.calls += 1
        params = os.path.join(self.log.folder, 'params-%04d.json' % self.calls)
        with open(params, 'w', encoding='utf-8', newline='\n') as file:
            json.dump(parameters or {}, file, indent='\t')
        arguments = [self.cli, 'call', command, '@' + params]
        if self.project:
            arguments += ['--project', self.project]
        return arguments + ['--timeout', str(timeout * 1000)]

    def start_call(self, command, parameters=None, timeout=c_CallSeconds):
        """A call that answers later (a live capture, which answers once the frames it waits for were presented): the
        running StrataCLI call, for finish_call."""
        return Program(self.call_arguments(command, parameters, timeout), self.env, self.log, command + '-started')

    def finish_call(self, command, started, timeout=c_CallSeconds):
        code, output = started.finish(timeout + 60)
        found = parse_json_object(output)
        if code != 0:
            message = found.get('message') if isinstance(found, dict) and isinstance(found.get('message'), str) else last_line(output)
            raise CommandError('%s failed (StrataCLI exit code %d): %s' % (command, code, message))
        if found is None:
            raise EditorError('%s answered something that is not JSON: %s' % (command, last_line(output)))
        return found

    def call(self, command, parameters=None, timeout=c_CallSeconds):
        """The command's result (a JSON value); raises EditorError when the editor answers with an error."""
        arguments = self.call_arguments(command, parameters, timeout)
        code, output, errors = run_program(arguments, self.env, self.log, command, timeout + 60, merge=False)
        if code != 0:
            error = parse_json_object(errors)
            if isinstance(error, dict) and isinstance(error.get('message'), str):
                raise CommandError('%s failed (StrataCLI exit code %d): %s' % (command, code, error['message']))
            message = last_line(errors or output)
            raise EditorError('%s failed (StrataCLI exit code %d): %s' % (command, code, message))
        try:
            return json.loads(output)
        except ValueError:
            raise EditorError('%s answered something that is not JSON: %s' % (command, last_line(output)))

    def check_commit(self, pin, provisional=False):
        """§1.4 check 4: editor.status {sections: ["engine"]} reports an engineCommit (the first 12 hex digits of the
        build's commit) that is a prefix of the pin. Returns {engineCommit, platform, gpu, provisional}: the GPU from the
        "editor" section, which an editor without a window may not have (then None). With provisional the check is
        skipped: the caller says so and keeps what it takes from being published."""
        status = self.call('editor.status', {'sections': ['engine']})
        reported = status.get('engineCommit') if isinstance(status, dict) else None
        if not provisional and (not isinstance(reported, str) or reported == 'unknown' or not reported or not pin.startswith(reported)):
            raise PreflightError('the editor reports the engine commit %s, which is not the pin %s: build the pin (pipelines.md '
                                 '§1.3; §1.4, check 4)' % (reported, pin[:12]))
        gpu = None
        try:
            editor = self.call('editor.status', {'sections': ['editor']}).get('editor')
            if isinstance(editor, dict):
                gpu = editor.get('gpu') or editor.get('GPU')
            if isinstance(gpu, dict):
                # The editor reports {name, api, apiVersion, driver}; stamps hold one line of text (taken.schema.json).
                api = ('%s %s' % (gpu.get('api') or '', gpu.get('apiVersion') or '')).strip()
                driver = 'driver %s' % gpu['driver'] if gpu.get('driver') else ''
                details = ', '.join(part for part in (api, driver) if part)
                gpu = '%s (%s)' % (gpu.get('name') or 'unknown GPU', details) if details else (gpu.get('name') or None)
        except EditorError:
            pass  # a --no-gpu editor has no editor window, and so no "editor" section
        return {'engineCommit': reported, 'platform': status.get('platform'), 'gpu': gpu, 'provisional': provisional}

    def quit(self):
        """editor.quit {force: true}, then waits for the process; ends its tree when it does not end in time."""
        if self.pid is None:
            return
        try:
            self.call('editor.quit', {'force': True}, timeout=60)
        except EditorError:
            pass
        if self.program is not None:
            try:
                self.program.finish(c_QuitSeconds)
            except EditorError:
                pass  # ended with its tree, and logged
            self.program = None
            self.pid = None
            shutil.rmtree(self.session, ignore_errors=True)
            return
        deadline = time.monotonic() + c_QuitSeconds
        while process_alive(self.pid) and time.monotonic() < deadline:
            time.sleep(0.2)
        if process_alive(self.pid):
            end_process_tree(self.pid)
        self.pid = None
        shutil.rmtree(self.session, ignore_errors=True)


def window_arguments(build, window):
    """The start of the command line of an editor in a window for pictures: exactly window["size"] pixels
    (--window-size), the UI at scale 1 whatever the display's, the panels' layout kept in window["layout"]."""
    width, height = window['size']
    return [program_path(build, 'StrataEditor'), '--window-size', '%dx%d' % (width, height), '--ui-scale', '1', '--layout', window['layout']]


c_McpProtocol = '2025-06-18'
c_McpGenericPrefix = 'strata_'  # StrataCLI mcp's own tools (McpServer.cpp: strata_status, strata_call, ...)


class McpClient:
    """An agent as the book's automation pages show one: StrataCLI mcp, which names the agent to the editor with the
    clientInfo.name its initialize gives (StrataCLI/src/CLI/McpServer.cpp:410-415) and keeps its connection, so that the
    status bar shows the agent connected while it works. Commands go through the strata_call tool, whatever the toolsets.
    The server finds the editor through the session folder of env (STRATA_SESSION_DIR); this class never reads it, and
    environment() passes no STRATA_EDITOR_PORT or STRATA_EDITOR_TOKEN on, so no token reaches the tool or its log."""

    def __init__(self, build, env, log, client, project=None, timeout=c_CallSeconds, program=None):
        import queue
        import threading
        self.log = log
        self.client = client
        self.timeout = timeout
        # program: the command line that stands for StrataCLI (tests give a stand-in server).
        self.arguments = list(program or [program_path(build, 'StrataCLI')]) + ['mcp'] + (['--project', project] if project else []) + ['--timeout', str(timeout * 1000)]
        log.number += 1
        self.errors_path = os.path.join(log.folder, '%04d-mcp.err' % log.number)
        self.errors = open(self.errors_path, 'wb')
        try:
            self.process = subprocess.Popen(self.arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.errors, env=env,
                                            **own_group())
        except OSError as error:
            self.errors.close()
            raise EditorError('%s could not start: %s' % (self.arguments[0], error))
        self.lines = queue.Queue()
        self.queue_empty = queue.Empty
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()
        self.next_id = 0
        self.closed = False

    def read(self):
        for line in self.process.stdout:
            self.lines.put(line.decode('utf-8', 'replace'))
        self.lines.put(None)

    def request(self, method, params, timeout):
        """The result of one JSON-RPC request; notifications the server sends meanwhile are skipped."""
        self.next_id += 1
        message = {'jsonrpc': '2.0', 'id': self.next_id, 'method': method, 'params': params}
        try:
            self.process.stdin.write((json.dumps(message) + '\n').encode('utf-8'))
            self.process.stdin.flush()
        except OSError as error:
            raise EditorError('StrataCLI mcp stopped reading its requests: %s' % error)
        deadline = time.monotonic() + timeout
        while True:
            left = deadline - time.monotonic()
            try:
                line = self.lines.get(timeout=max(left, 0.01))
            except self.queue_empty:
                raise EditorError('StrataCLI mcp did not answer %s within %d seconds' % (method, timeout))
            if line is None:
                raise EditorError('StrataCLI mcp ended before it answered %s' % method)
            try:
                answer = json.loads(line)
            except ValueError:
                continue
            if not isinstance(answer, dict) or answer.get('id') != self.next_id:
                continue
            self.log.write('mcp-' + (params.get('arguments', {}).get('method') or params.get('name') or method if isinstance(params, dict) else method),
                           self.arguments + [method], json.dumps(message) + '\n' + line, 'error' if 'error' in answer else 0)
            if 'error' in answer:
                raise EditorError('StrataCLI mcp refused %s: %s' % (method, (answer['error'] or {}).get('message')))
            return answer.get('result')

    def initialize(self):
        self.request('initialize', {'protocolVersion': c_McpProtocol, 'capabilities': {}, 'clientInfo': {'name': self.client, 'version': '1'}}, c_CallSeconds)
        self.process.stdin.write((json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n').encode('utf-8'))
        self.process.stdin.flush()

    def wait_for_editor(self, seconds, alive=lambda: True):
        """Asks for the tools until the server lists the editor's (it reached the editor); TakeError-free: EditorError."""
        deadline = time.monotonic() + seconds
        while True:
            tools = (self.request('tools/list', {}, c_CallSeconds) or {}).get('tools') or []
            if any(not str(tool.get('name', '')).startswith(c_McpGenericPrefix) for tool in tools if isinstance(tool, dict)):
                return
            if not alive():
                raise EditorError('the editor ended before StrataCLI mcp reached it')
            if time.monotonic() > deadline:
                raise EditorError('StrataCLI mcp did not reach the editor within %d seconds' % seconds)
            time.sleep(1)

    def call(self, command, parameters=None, timeout=c_CallSeconds):
        """A command's result through the strata_call tool, as the editor answered it; CommandError when it failed."""
        result = self.request('tools/call', {'name': 'strata_call', 'arguments': {'method': command, 'params': parameters or {}}}, timeout + 60) or {}
        texts = [item.get('text', '') for item in result.get('content') or [] if isinstance(item, dict) and item.get('type') == 'text']
        if result.get('isError'):
            raise CommandError('%s failed (through StrataCLI mcp): %s' % (command, last_line('\n'.join(texts))))
        if 'structuredContent' in result:
            return result['structuredContent']
        try:
            return json.loads(texts[0]) if texts else None
        except ValueError:
            raise EditorError('%s answered something that is not JSON: %s' % (command, last_line(texts[0])))

    def close(self):
        """Ends the server (end of its input), and its tree when it does not end in time."""
        if self.closed:
            return
        self.closed = True
        try:
            self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=c_QuitSeconds)
        except subprocess.TimeoutExpired:
            end_process_tree(self.process.pid)
            try:
                self.process.wait(timeout=c_QuitSeconds)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.reader.join(timeout=c_QuitSeconds)
        self.process.stdout.close()
        self.errors.close()


def last_line(text):
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else '(no output)'


def parse_json_object(text):
    """The last JSON object a program printed (StrataCLI prints progress lines before it), or None."""
    for start in [index for index, char in enumerate(text) if char == '{']:
        try:
            value, end = json.JSONDecoder().raw_decode(text[start:])
        except ValueError:
            continue
        if not text[start + end:].strip():
            return value
    return None
