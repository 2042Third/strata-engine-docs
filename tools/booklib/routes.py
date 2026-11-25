"""The parsed routes of the generated reference (plan/pipelines.md §7.1): each reads the engine's source at the pin and
returns the data of one file of reference/_dumps/<pin>/parsed/. A route that finds nothing where the pin has something
raises RouteError, whose message names the file (and line) and says what to do.

parse_all(engine, pin, release, limits_path) runs every route and returns ({route: data}, problems).
"""

import json
import os
import re
import subprocess
import tempfile

from booklib import cpp

c_Keywords = {'alignas', 'alignof', 'asm', 'auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'const', 'consteval',
              'constexpr', 'constinit', 'const_cast', 'continue', 'decltype', 'default', 'delete', 'do', 'double',
              'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if',
              'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'nullptr', 'operator', 'private', 'protected',
              'public', 'register', 'reinterpret_cast', 'requires', 'return', 'short', 'signed', 'sizeof', 'static',
              'static_assert', 'static_cast', 'struct', 'switch', 'template', 'this', 'throw', 'true', 'try', 'typedef',
              'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'while'}
c_Tag = re.compile(r'^v(\d+)\.(\d+)\.(\d+)$')
c_Editor = 'StrataEditor/src'
c_Mcp = 'StrataCLI/src/CLI/McpToolsets.cpp'
c_AssetTypes = 'Strata/src/Strata/Asset/AssetTypes.h'
c_Quality = 'Strata/src/Strata/Renderer/RendererQuality.cpp'
c_RenderStats = 'StrataEditor/src/Editor/EditorStateCommands.cpp'
c_SceneRenderer = 'Strata/src/Strata/Renderer/SceneRenderer.h'
c_PerfLogHeader = 'Strata/src/Strata/Runtime/FramePerfLog.h'
c_PerfLogSource = 'Strata/src/Strata/Runtime/FramePerfLog.cpp'
c_PerfLogGroups = (('GameRuntime', 'Strata/src/Strata/Runtime/GameRuntime.cpp'), ('GameRenderer', 'Strata/src/Strata/Runtime/GameRenderer.cpp'))
c_EditorOptions = 'StrataEditor/src/EditorApplication.cpp'
c_RuntimeOptions = 'StrataRuntime/src/RuntimeApplication.cpp'
c_CliUsage = 'StrataCLI/src/CLI/CliApplication.cpp'
c_ScriptABI = 'StrataScriptCore/Include/StrataScript/ScriptABI.h'
c_SDKFolder = 'StrataScriptCore/Include/StrataScript/'
c_Budgets = 'StrataTests/Perf/Budgets.json'
c_TestsCMake = 'StrataTests/CMakeLists.txt'
c_Shards = 'StrataTests/CoreShards.json'
c_Presets = 'CMakePresets.json'
c_UIFolders = ('StrataEditor/src/UI/', 'StrataEditor/src/Panels/')
c_UIFiles = ('StrataEditor/src/EditorLayer.cpp',)
c_FrameProfiler = 'Strata/src/Strata/Core/FrameProfiler.h'
c_StageCalls = ('RegisterStage', 'RegisterGPUStage', 'ST_PROFILE_STAGE')


class RouteError(Exception):
    """A route found nothing where the pin has something: the message names the file and says what to do."""


def change_route(route):
    return 'the engine changed how it writes this: change the %s route of tools/booklib/routes.py (plan/pipelines.md §7.1)' % route


class Reader:
    """The pin clone at the pin: files, their tokens, git grep and the tree, each read once."""

    def __init__(self, engine, pin):
        self.engine = engine
        self.pin = pin
        self.sources = {}
        self.texts = {}
        self._tree = None

    def text(self, path):
        if path not in self.texts:
            lines = self.engine.read(self.pin, path)
            self.texts[path] = None if lines is None else '\n'.join(lines)
        return self.texts[path]

    def need(self, path, route):
        text = self.text(path)
        if text is None:
            raise RouteError('%s: missing at the pin: %s' % (path, change_route(route)))
        return text

    def source(self, path, route):
        if path not in self.sources:
            self.sources[path] = cpp.tokenize(self.need(path, route))
        return self.sources[path]

    def git(self, *arguments):
        result = subprocess.run(['git', '-C', self.engine.path] + list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode, result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace')

    def grep_output(self, pattern, options, paths):
        """What git grep prints for an extended regular expression at the pin. The pattern goes through a file (-f): MSYS2's
        git reads its command line as a shell would, so backslashes, quotes and brackets in an argument would change."""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.txt', delete=False) as file:
            file.write(pattern + '\n')
            name = file.name
        try:
            code, output, error = self.git('grep', '-I', '-E', *options, '-f', name, self.pin, '--', *paths)
        finally:
            os.remove(name)
        if code not in (0, 1):
            raise RouteError('git grep in %s: %s' % (self.engine.path, error.strip()))
        return output

    def grep(self, pattern, paths):
        """The files at the pin under paths that hold a match of the pattern (extended regular expression)."""
        prefix = self.pin + ':'
        output = self.grep_output(pattern, ['-l'], paths)
        return sorted(line[len(prefix):] if line.startswith(prefix) else line for line in output.splitlines() if line)

    def tree(self):
        """[(mode, type, id, path)] of git ls-tree -r at the pin."""
        if self._tree is None:
            code, output, error = self.git('ls-tree', '-r', '-z', '--full-tree', self.pin)
            if code != 0:
                raise RouteError('git ls-tree in %s: %s' % (self.engine.path, error.strip()))
            entries = []
            for record in output.split('\0'):
                if not record:
                    continue
                meta, _, path = record.partition('\t')
                mode, kind, object_id = meta.split()
                entries.append((mode, kind, object_id, path))
            self._tree = entries
        return self._tree


def tokens_at(tokens, index, *texts):
    """True when the tokens from index spell the given texts."""
    if index + len(texts) > len(tokens):
        return False
    return all(tokens[index + offset].text == text for offset, text in enumerate(texts))


def literal(tokens, start, end):
    """The string of tokens[start:end] when it is only adjacent string literals, else None."""
    joined = cpp.string_at(tokens, start)
    if joined is None or joined[1] != end:
        return None
    return joined[0]


def brace_strings(tokens, open_index):
    """The string literals of the brace list that starts at open_index (each element one run of literals)."""
    close = cpp.match(tokens, open_index)
    if close is None:
        return None, None
    values = []
    for start, end in cpp.split_top(tokens, open_index + 1, close):
        if start == end:
            continue
        value = literal(tokens, start, end)
        if value is None:
            return None, close
        values.append(value)
    return values, close


def find_initializer(source, name):
    """The index of the "{" of `name[] = {` or `name = {` (the first one), or None."""
    tokens = source.tokens
    for index, token in enumerate(tokens):
        if token.text != name or token.kind != 'id':
            continue
        position = index + 1
        if tokens_at(tokens, position, '[', ']'):
            position += 2
        if tokens_at(tokens, position, '=', '{'):
            return position + 1
    return None


# ---------------------------------------------------------------------------------------------------------------------
# commands.

def parse_registration(source, path, index):
    """The registration at tokens[index] ("Register"), or None when the call is no command's."""
    tokens = source.tokens
    if not tokens_at(tokens, index + 1, '('):
        return None
    position = index + 2
    wrapped = False
    if tokens_at(tokens, position, 'MayDefer', '('):
        wrapped = True
        position += 2
    if not tokens_at(tokens, position, '{') or position + 1 >= len(tokens) or tokens[position + 1].kind != 'str':
        return None
    close = cpp.match(tokens, position)
    if close is None:
        raise RouteError('%s:%d: a command registration whose braces do not close: %s' % (path, tokens[index].line, change_route('commands')))
    parts = cpp.split_top(tokens, position + 1, close)
    name = literal(tokens, *parts[0])
    if name is None or len(parts) < 4:
        raise RouteError('%s:%d: a command registration without a literal name, description, schema and handler: %s'
                         % (path, tokens[index].line, change_route('commands')))
    record = {'name': name, 'file': path, 'line': tokens[index].line, 'kind': 'Edit', 'results': 'Content', 'waitsForAssets': False,
              'mayDefer': wrapped}
    for number, (start, end) in enumerate(parts[4:], 4):
        text = ''.join(token.text for token in tokens[start:end])
        if number == 4 and text.startswith('EditorCommandKind::'):
            record['kind'] = text.split('::', 1)[1]
        elif number == 5 and text.startswith('EditorCommandResults::'):
            record['results'] = text.split('::', 1)[1]
        elif number == 6 and text in ('true', 'false'):
            record['waitsForAssets'] = text == 'true'
        elif number == 7 and text in ('true', 'false'):
            record['mayDefer'] = record['mayDefer'] or text == 'true'
        elif text:
            raise RouteError('%s:%d: the registration of %s has "%s" where EditorCommand\'s field %d (Kind, Results, WaitsForAssets, '
                             'MayDefer) stands: %s' % (path, tokens[start].line, name, text, number + 1, change_route('commands')))
    return record


def pairs(tokens, open_index, route, path):
    """[(a, b)] of a brace list of { "a", "b" } pairs."""
    close = cpp.match(tokens, open_index)
    found = []
    for start, end in cpp.split_top(tokens, open_index + 1, close):
        if start == end:
            continue
        if tokens[start].text != '{':
            raise RouteError('%s:%d: a list of pairs holds "%s": %s' % (path, tokens[start].line, tokens[start].text, change_route(route)))
        inner = cpp.split_top(tokens, start + 1, end - 1)
        values = [literal(tokens, *part) for part in inner]
        if len(values) != 2 or None in values:
            raise RouteError('%s:%d: a pair that is not two literals: %s' % (path, tokens[start].line, change_route(route)))
        found.append(tuple(values))
    return found


def route_commands(reader):
    registrations = []
    for path in reader.grep(r'Register\((MayDefer\()?\{ *"', [c_Editor]):
        if not path.endswith('.cpp'):
            continue
        source = reader.source(path, 'commands')
        for index, token in enumerate(source.tokens):
            if token.text == 'Register' and token.kind == 'id':
                record = parse_registration(source, path, index)
                if record:
                    registrations.append(record)
    if not registrations:
        raise RouteError('%s: no command registration (Register({ "<group>.<action>", …})) found: %s' % (c_Editor, change_route('commands')))
    names = [record['name'] for record in registrations]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise RouteError('%s: commands registered twice: %s: %s' % (c_Editor, ', '.join(duplicates), change_route('commands')))
    source = reader.source(c_Mcp, 'commands')
    found = {}
    for name in ('c_CoreCommands', 'c_ExactToolsets', 'c_PrefixToolsets', 'c_Toolsets'):
        open_index = find_initializer(source, name)
        if open_index is None:
            raise RouteError('%s: no initializer of %s: %s' % (c_Mcp, name, change_route('commands')))
        found[name] = open_index
    core, _ = brace_strings(source.tokens, found['c_CoreCommands'])
    if not core:
        raise RouteError('%s: c_CoreCommands holds no command: %s' % (c_Mcp, change_route('commands')))
    toolsets = {
        'core': core,
        'exact': [list(pair) for pair in pairs(source.tokens, found['c_ExactToolsets'], 'commands', c_Mcp)],
        'prefixes': [list(pair) for pair in pairs(source.tokens, found['c_PrefixToolsets'], 'commands', c_Mcp)],
        'known': [{'name': name, 'description': description} for name, description in pairs(source.tokens, found['c_Toolsets'], 'commands', c_Mcp)],
    }
    return {'registrations': sorted(registrations, key=lambda record: record['name']), 'toolsets': toolsets}


# ---------------------------------------------------------------------------------------------------------------------
# components.

def chain_calls(tokens, position):
    """[(method, args start, args end, line)] of a builder chain .A(...).B(...) from position, and the index after it."""
    calls = []
    while tokens_at(tokens, position, '.') and position + 2 < len(tokens) and tokens[position + 2].text == '(':
        method = tokens[position + 1].text
        close = cpp.match(tokens, position + 2)
        if close is None:
            break
        calls.append((method, position + 3, close, tokens[position + 1].line))
        position = close + 1
    return calls, position


def scoped_names(tokens, start, end, scope):
    """The names X of every "scope::X" in tokens[start:end]."""
    return [tokens[index + 2].text for index in range(start, end - 2) if tokens[index].text == scope and tokens[index + 1].text == '::']


def function_messages(source, name, visited=None):
    """The messages a function of this file can return: the string literals of its body that hold a space, and those of
    the functions of the same file it calls."""
    visited = visited if visited is not None else set()
    if name in visited:
        return []
    visited.add(name)
    tokens = source.tokens
    messages = []
    for index, token in enumerate(tokens):
        if token.text != name or token.kind != 'id' or index == 0:
            continue
        # A definition: "std::string Name(...) {" (or a template's "> Name(...) {").
        if tokens[index - 1].text not in ('string', '>') or not tokens_at(tokens, index + 1, '('):
            continue
        close = cpp.match(tokens, index + 1)
        if close is None:
            continue
        position = close + 1
        while position < len(tokens) and tokens[position].text in ('const', 'noexcept'):
            position += 1
        body_end = cpp.match(tokens, position) if tokens_at(tokens, position, '{') else None
        if body_end is None:
            continue
        for text, _ in cpp.strings(tokens, position, body_end):
            if ' ' in text and text not in messages:
                messages.append(text)
        for inner in range(position, body_end):
            item = tokens[inner]
            if item.kind == 'id' and tokens[inner + 1].text in ('(', '<'):  # a call, perhaps of another function of the file
                for text in function_messages(source, item.text, visited):
                    if text not in messages:
                        messages.append(text)
    return messages


def loop_strings(tokens, index, variable):
    """The strings of `for (... variable : { "a", "b" })` before index, or None."""
    for position in range(index - 1, max(0, index - 60), -1):
        if tokens[position].text == variable and tokens_at(tokens, position + 1, ':', '{'):
            values, _ = brace_strings(tokens, position + 2)
            return values
    return None


def route_components(reader):
    files = reader.grep(r'ComponentRegistry::(Register<|SetInactiveReason)', ['Strata/src', c_Editor])
    components = []
    types = {}
    for path in files:
        source = reader.source(path, 'components')
        tokens = source.tokens
        for index in range(len(tokens) - 4):
            if not tokens_at(tokens, index, 'ComponentRegistry', '::', 'Register', '<'):
                continue
            close = cpp.match_angle(tokens, index + 3)
            if close is None or not tokens_at(tokens, close + 1, '(') or tokens[close + 2].kind != 'str':
                continue
            type_name = ''.join(token.text for token in tokens[index + 4:close])
            name = tokens[close + 2].value
            arguments_close = cpp.match(tokens, close + 1)
            if arguments_close is None:
                raise RouteError('%s:%d: the registration of %s does not close its parentheses: %s' % (path, tokens[index].line, name,
                                                                                                    change_route('components')))
            calls, _ = chain_calls(tokens, arguments_close + 1)
            record = {'name': name, 'type': type_name, 'file': path, 'line': tokens[index].line, 'flags': [], 'properties': []}
            for method, start, end, line in calls:
                if method == 'Flags':
                    record['flags'] = scoped_names(tokens, start, end, 'ComponentFlags')
                elif method in ('DisplayName', 'Category', 'Description'):
                    value = literal(tokens, start, end)
                    if value is not None:
                        record[method[0].lower() + method[1:]] = value
                elif method.endswith('Property') and start < end and tokens[start].kind == 'str':
                    record['properties'].append({'name': tokens[start].value, 'method': method, 'line': line,
                                                 'flags': scoped_names(tokens, start, end, 'PropertyFlags')})
            components.append(record)
            types[type_name.split('::')[-1]] = name
    if not components:
        raise RouteError('Strata/src: no ComponentRegistry::Register<T>("Name") found: %s' % change_route('components'))
    inactive = []
    for path in files:
        source = reader.source(path, 'components')
        tokens = source.tokens
        for index in range(len(tokens) - 3):
            if tokens[index].text not in ('SetInactiveReason', 'SetInactiveReasons') or not tokens_at(tokens, index + 1, '<'):
                continue
            close = cpp.match_angle(tokens, index + 1)
            if close is None or not tokens_at(tokens, close + 1, '('):
                continue
            type_name = ''.join(token.text for token in tokens[index + 2:close]).split('::')[-1]
            if type_name not in types:
                continue  # a template helper's own call with its parameter T
            args_close = cpp.match(tokens, close + 1)
            arguments = cpp.split_top(tokens, close + 2, args_close)
            if len(arguments) < 2:
                raise RouteError('%s:%d: %s with %d argument: %s' % (path, tokens[index].line, tokens[index].text, len(arguments),
                                                                     change_route('components')))
            # The reason may be a template's address whose arguments hold commas (&F<int, &S::M>): all after the first.
            arguments = [arguments[0], (arguments[1][0], arguments[-1][1])]
            start, end = arguments[0]
            if tokens[start].text == '{':
                properties, _ = brace_strings(tokens, start)
            elif tokens[start].kind == 'str':
                properties = [literal(tokens, start, end)]
            elif tokens[start].kind == 'id' and end == start + 1:
                properties = loop_strings(tokens, index, tokens[start].text)
            else:
                properties = None
            if not properties or None in properties:
                raise RouteError('%s:%d: the properties of this %s are not literals or a loop over literals: %s'
                                 % (path, tokens[index].line, tokens[index].text, change_route('components')))
            function_start, function_end = arguments[1]
            names = [token.text for token in tokens[function_start:function_end] if token.kind == 'id']
            if not names:
                raise RouteError('%s:%d: the reason of this %s is no function of the file: %s' % (path, tokens[index].line, tokens[index].text,
                                                                                                change_route('components')))
            function = names[0]
            messages = function_messages(source, function)
            for name in properties:
                inactive.append({'component': types[type_name], 'property': name, 'function': function, 'messages': messages,
                                 'file': path, 'line': tokens[index].line})
    return {'components': sorted(components, key=lambda record: record['name']), 'inactive': inactive}


# ---------------------------------------------------------------------------------------------------------------------
# asset types and importers.

def enum_values(source, name, path, route):
    tokens = source.tokens
    for index in range(len(tokens) - 2):
        if tokens_at(tokens, index, 'enum', 'class', name):
            position = index + 3
            while position < len(tokens) and tokens[position].text not in ('{', ';'):
                position += 1
            if not tokens_at(tokens, position, '{'):
                continue
            close = cpp.match(tokens, position)
            values = []
            current = -1
            for start, end in cpp.split_top(tokens, position + 1, close):
                if start == end:
                    continue
                enumerator = tokens[start].text
                if end - start > 2 and tokens[start + 1].text == '=':
                    value = cpp.evaluate(cpp.spelled(source, start + 2, end - 1))
                    if value is None:
                        raise RouteError('%s:%d: the value of %s::%s is no constant: %s' % (path, tokens[start].line, name, enumerator,
                                                                                           change_route(route)))
                    current = int(value)
                else:
                    current += 1
                line = tokens[start].line
                values.append({'name': enumerator, 'value': current, 'line': line,
                               'comment': cpp.comment_on(source, line) or cpp.comment_before(source, line)})
            return values
    raise RouteError('%s: no enum class %s: %s' % (path, name, change_route(route)))


def class_ranges(source):
    """[(name, open, close)] of every class or struct definition of the file."""
    tokens = source.tokens
    ranges = []
    for index in range(len(tokens) - 1):
        if tokens[index].text in ('class', 'struct') and tokens[index + 1].kind == 'id' and (index == 0 or tokens[index - 1].text != 'enum'):
            position = index + 2
            while position < len(tokens) and tokens[position].text not in ('{', ';', '(', ')', ','):
                position += 1
            if tokens_at(tokens, position, '{'):
                close = cpp.match(tokens, position)
                if close is not None:
                    ranges.append((tokens[index + 1].text, position, close))
    return ranges


def inline_return(tokens, start, end, name):
    """The tokens (start, end) of `return …;` in the inline body of `name() const override { … }` within [start, end)."""
    for index in range(start, end - 3):
        if tokens[index].text == name and tokens_at(tokens, index + 1, '(', ')'):
            position = index + 3
            while position < end and tokens[position].text in ('const', 'override', 'final', 'noexcept'):
                position += 1
            if tokens_at(tokens, position, '{', 'return'):
                close = cpp.match(tokens, position)
                return position + 2, close - 1 if tokens[close - 1].text == ';' else close
    return None


def route_asset_types(reader):
    types = enum_values(reader.source(c_AssetTypes, 'asset-types'), 'AssetType', c_AssetTypes, 'asset-types')
    importers = []
    files = reader.grep(r'GetVersion\(\) const override \{ *return [0-9]+; *\}', ['Strata/src'])
    registrations = {}
    for path in reader.grep(r'CreateScope<[A-Za-z]+Importer>\(AssetType::', ['Strata/src']):
        tokens = reader.source(path, 'asset-types').tokens
        for index in range(len(tokens) - 8):
            if tokens_at(tokens, index, 'CreateScope', '<') and tokens_at(tokens, index + 3, '>', '(', 'AssetType', '::'):
                registrations.setdefault(tokens[index + 2].text, []).append((tokens[index + 7].text, path, tokens[index].line))
    for path in files:
        source = reader.source(path, 'asset-types')
        tokens = source.tokens
        for name, open_index, close in class_ranges(source):
            version_tokens = inline_return(tokens, open_index, close, 'GetVersion')
            if version_tokens is None:
                continue
            version = cpp.evaluate(cpp.spelled(source, version_tokens[0], version_tokens[1] - 1))
            type_tokens = inline_return(tokens, open_index, close, 'GetType')
            type_text = ''.join(token.text for token in tokens[type_tokens[0]:type_tokens[1]]) if type_tokens else ''
            extensions_tokens = inline_return(tokens, open_index, close, 'GetExtensions')
            extensions = []
            if extensions_tokens and tokens[extensions_tokens[0]].text == '{':
                extensions, _ = brace_strings(tokens, extensions_tokens[0])
            line = next(token.line for token in tokens[open_index:close] if token.text == 'GetVersion')
            if type_text.startswith('AssetType::'):
                importers.append({'class': name, 'type': type_text.split('::', 1)[1], 'version': version, 'extensions': extensions or [],
                                  'file': path, 'line': line})
            elif name in registrations:
                for asset_type, where, at in registrations[name]:
                    importers.append({'class': name, 'type': asset_type, 'version': version, 'extensions': extensions or [],
                                      'file': path, 'line': line, 'registered': '%s:%d' % (where, at)})
            else:
                raise RouteError('%s:%d: the importer %s returns "%s" from GetType and is never registered with an AssetType: %s'
                                 % (path, line, name, type_text, change_route('asset-types')))
    if not importers:
        raise RouteError('Strata/src: no importer with GetVersion() const override { return N; }: %s' % change_route('asset-types'))
    known = {item['name'] for item in types}
    for importer in importers:
        if importer['type'] not in known:
            raise RouteError('%s:%d: the importer %s imports %s, which the AssetType enum lacks: %s' % (
                importer['file'], importer['line'], importer['class'], importer['type'], change_route('asset-types')))
    return {'file': c_AssetTypes, 'types': types, 'importers': sorted(importers, key=lambda item: (item['type'], item['class']))}


# ---------------------------------------------------------------------------------------------------------------------
# quality rows.

def route_quality(reader):
    source = reader.source(c_Quality, 'quality')
    tokens = source.tokens
    rows = []
    for index in range(len(tokens) - 2):
        token = tokens[index]
        match = re.fullmatch(r'c_([A-Za-z0-9]+)Row', token.text) if token.kind == 'id' else None
        if not match or not tokens_at(tokens, index + 1, '=', '{'):
            continue
        close = cpp.match(tokens, index + 2)
        parts = cpp.split_top(tokens, index + 3, close)
        values = []
        for start, end in parts:
            text = cpp.spelled(source, start, end - 1)
            number = cpp.evaluate(text)
            values.append(number if number is not None else text)
        if len(values) != 4:
            raise RouteError('%s:%d: %s holds %d values, not one per preset (Low, Medium, High, Ultra): %s'
                             % (c_Quality, token.line, token.text, len(values), change_route('quality')))
        type_text = ''
        if index >= 4 and tokens[index - 1].text == '>':
            opening = next((position for position in range(index - 2, max(0, index - 12), -1) if tokens[position].text == '<'), None)
            if opening is not None:
                type_text = cpp.spelled(source, opening + 1, index - 2)
        rows.append({'row': match.group(1), 'type': type_text, 'values': values, 'line': token.line,
                     'comment': cpp.comment_before(source, token.line)})
    if not rows:
        raise RouteError('%s: no line c_<Row>Row = { Low, Medium, High, Ultra }: %s' % (c_Quality, change_route('quality')))
    fields = []
    for index in range(len(tokens) - 2):
        if tokens[index].text in ('EnumField', 'NumberField', 'BoolField') and tokens_at(tokens, index + 1, '(') and tokens[index + 2].kind == 'str':
            fields.append({'name': tokens[index + 2].value, 'line': tokens[index].line})
    names = {field['name'] for field in fields}
    for row in rows:
        if row['row'] not in names:
            raise RouteError('%s:%d: the row c_%sRow has no field "%s" of the Renderer.Quality section in the same file: %s'
                             % (c_Quality, row['line'], row['row'], row['row'], change_route('quality')))
    return {'file': c_Quality, 'rows': rows, 'fields': fields}


# ---------------------------------------------------------------------------------------------------------------------
# GPU stages.

def route_gpu_stages(reader):
    stages = []
    for path in reader.grep(r'RegisterGPUStage\("|FrameStageKind::GPU', ['Strata/src', c_Editor, 'StrataRuntime/src']):
        tokens = reader.source(path, 'gpu-stages').tokens
        for index in range(len(tokens) - 2):
            if tokens[index].text == 'RegisterGPUStage' and tokens_at(tokens, index + 1, '(') and tokens[index + 2].kind == 'str':
                stages.append({'name': tokens[index + 2].value, 'file': path, 'line': tokens[index].line, 'call': 'RegisterGPUStage'})
            elif tokens[index].text == 'RegisterStage' and tokens_at(tokens, index + 1, '(') and tokens[index + 2].kind == 'str':
                close = cpp.match(tokens, index + 1)
                if 'GPU' in scoped_names(tokens, index + 2, close, 'FrameStageKind'):
                    stages.append({'name': tokens[index + 2].value, 'file': path, 'line': tokens[index].line, 'call': 'RegisterStage'})
    if not stages:
        raise RouteError('Strata/src: no RegisterGPUStage("…") or RegisterStage("…", …, FrameStageKind::GPU): %s' % change_route('gpu-stages'))
    return {'stages': stages}


# ---------------------------------------------------------------------------------------------------------------------
# render statistics.

def function_body(tokens, name):
    """(open, close) of the body of the function `name` defined in the file, or None."""
    for index in range(1, len(tokens) - 1):
        if tokens[index].text == name and tokens[index].kind == 'id' and tokens_at(tokens, index + 1, '(') and tokens[index - 1].kind == 'id':
            close = cpp.match(tokens, index + 1)
            position = close + 1 if close is not None else len(tokens)
            while position < len(tokens) and tokens[position].text in ('const', 'noexcept', 'override'):
                position += 1
            if tokens_at(tokens, position, '{'):
                return position, cpp.match(tokens, position)
    return None


def json_entries(source, open_index, body):
    """The keys of a nlohmann::json brace list of { "key", value } pairs, with their comments and children."""
    tokens = source.tokens
    close = cpp.match(tokens, open_index)
    entries = []
    for start, end in cpp.split_top(tokens, open_index + 1, close):
        if start == end:
            continue
        if tokens[start].text != '{' or tokens[start + 1].kind != 'str':
            return None
        parts = cpp.split_top(tokens, start + 1, end - 1)
        if len(parts) != 2:
            return None
        key = literal(tokens, *parts[0])
        value_start, value_end = parts[1]
        line = tokens[start].line
        entry = {'key': key, 'line': line, 'comment': cpp.comment_before(source, line)}
        words = [token.text for token in tokens[value_start:value_end]]
        if len(words) >= 3 and words[0] == 'stats' and words[1] == '.':
            entry['source'] = 'SceneRendererStats::' + words[2]
        children = value_children(source, value_start, value_end, body)
        if children:
            entry['children'] = children
        entries.append(entry)
    return entries


def value_children(source, start, end, body):
    """The keys of an object a value builds: an inline nlohmann::json { … }, a variable filled with push_back({ … }), or a
    function of the file that returns { … }."""
    tokens = source.tokens
    for index in range(start, end - 3):
        if tokens_at(tokens, index, 'nlohmann', '::', 'json', '{'):
            entries = json_entries(source, index + 3, body)
            if entries:
                return entries
    words = [token.text for token in tokens[start:end]]
    if len(words) == 6 and words[:4] == ['std', '::', 'move', '(']:
        variable = words[4]
        for index in range(body[0], body[1] - 4):
            if tokens[index].text == variable and tokens_at(tokens, index + 1, '.', 'push_back', '(', '{'):
                entries = json_entries(source, index + 4, body)
                if entries:
                    return entries
    if len(words) >= 3 and tokens[start].kind == 'id' and words[1] == '(' and words[-1] == ')':
        inner = function_body(tokens, words[0])
        if inner:
            for index in range(inner[0], inner[1] - 1):
                if tokens_at(tokens, index, 'return', '{'):
                    entries = json_entries(source, index + 1, inner)
                    if entries:
                        return entries
    return None


def route_render_stats(reader):
    source = reader.source(c_RenderStats, 'render-stats')
    body = function_body(source.tokens, 'DescribeRenderStats')
    if body is None:
        raise RouteError('%s: no function DescribeRenderStats: %s' % (c_RenderStats, change_route('render-stats')))
    tokens = source.tokens
    returns = [index for index in range(body[0], body[1]) if tokens_at(tokens, index, 'return', '{')]
    entries = None
    for index in returns:
        entries = json_entries(source, index + 1, body)
        if entries:
            break
    if not entries:
        raise RouteError('%s:%d: DescribeRenderStats returns no list of { "key", value } pairs: %s' % (
            c_RenderStats, tokens[body[0]].line, change_route('render-stats')))
    return {'file': c_RenderStats, 'line': tokens[body[0]].line, 'keys': entries}


# ---------------------------------------------------------------------------------------------------------------------
# renderer specification and statistics.

def route_renderer(reader):
    source = reader.source(c_SceneRenderer, 'renderer')
    data = {'file': c_SceneRenderer}
    for key, name in (('specification', 'SceneRendererSpecification'), ('stats', 'SceneRendererStats')):
        members = cpp.struct_members(source, name)
        if not members:
            raise RouteError('%s: no struct %s with fields: %s' % (c_SceneRenderer, name, change_route('renderer')))
        found = cpp.find_struct(source, name)
        data[key] = {'name': name, 'line': source.tokens[found[0]].line, 'fields': members}
    return data


# ---------------------------------------------------------------------------------------------------------------------
# runtime perf log.

def perf_log_descriptions(text):
    """{column: description} and the order of the entries, from FramePerfLog.h's comment "The header names the columns:"."""
    lines = text.split('\n')
    start = next((index for index, line in enumerate(lines) if 'The header names the columns:' in line), None)
    if start is None:
        return None
    entries = []
    for line in lines[start + 1:]:
        stripped = line.strip()
        if not stripped.startswith('//'):
            break
        body = stripped[2:]
        names_line = re.match(r'^ {3}(\S.*?)(?: {2,}(\S.*))?$', body)
        deep = re.match(r'^ {10,}(\S.*)$', body)
        if names_line and not deep:
            names = names_line.group(1).strip()
            if entries and entries[-1]['names'].endswith(','):
                entries[-1]['names'] += ' ' + names
            else:
                entries.append({'names': names, 'description': ''})
            if names_line.group(2):
                entries[-1]['description'] = (entries[-1]['description'] + ' ' + names_line.group(2)).strip()
        elif deep and entries:
            entries[-1]['description'] = (entries[-1]['description'] + ' ' + deep.group(1)).strip()
        else:
            break
    descriptions = {}
    for entry in entries:
        for name in entry['names'].split(','):
            name = name.strip()
            if name:
                descriptions[name] = entry['description']
    return descriptions


def route_perf_log(reader):
    descriptions = perf_log_descriptions(reader.need(c_PerfLogHeader, 'perf-log'))
    if not descriptions:
        raise RouteError('%s: no comment "The header names the columns:" with the columns\' descriptions: %s'
                         % (c_PerfLogHeader, change_route('perf-log')))
    source = reader.source(c_PerfLogSource, 'perf-log')
    tokens = source.tokens
    first = None
    fixed = None
    for index in range(len(tokens) - 3):
        if first is None and tokens[index].text == 'm_Columns' and tokens_at(tokens, index + 1, '=', '{'):
            first, _ = brace_strings(tokens, index + 2)
            first_line = tokens[index].line
        if fixed is None and tokens[index].text == 'column' and tokens_at(tokens, index + 1, ':', '{'):
            fixed, _ = brace_strings(tokens, index + 2)
            fixed_line = tokens[index].line
    if not first or not fixed:
        raise RouteError('%s: no m_Columns = { … } and for (… column : { … }) lists of columns: %s' % (c_PerfLogSource, change_route('perf-log')))
    columns = [{'name': name, 'part': 'frame', 'line': first_line} for name in first]
    columns.append({'name': '<stage>', 'part': 'stages', 'line': first_line})
    columns += [{'name': name, 'part': 'built-in', 'line': fixed_line} for name in fixed]
    for column in columns:
        key = '<stage>...' if column['name'] == '<stage>' else column['name']
        column['description'] = descriptions.get(key, '')
        if not column['description']:
            raise RouteError('%s: the column %s has no description in the comment "The header names the columns:" of %s: %s'
                             % (c_PerfLogSource, column['name'], c_PerfLogHeader, change_route('perf-log')))
    groups = []
    for owner, path in c_PerfLogGroups:
        group_tokens = reader.source(path, 'perf-log').tokens
        names = None
        for index in range(len(group_tokens) - 4):
            if tokens_at(group_tokens, index, 'group', '.', 'Names', '=', '{'):
                names, _ = brace_strings(group_tokens, index + 4)
                line = group_tokens[index].line
                break
        if not names:
            raise RouteError('%s: no group.Names = { … } in %s::MakePerfLogColumns: %s' % (path, owner, change_route('perf-log')))
        groups.append({'owner': owner, 'file': path, 'line': line, 'names': names})
    return {'file': c_PerfLogSource, 'columns': columns, 'groups': groups}


# ---------------------------------------------------------------------------------------------------------------------
# program options.

def arguments_array(reader, path):
    source = reader.source(path, 'options')
    tokens = source.tokens
    open_index = find_initializer(source, 'c_Arguments')
    if open_index is None:
        raise RouteError('%s: no c_Arguments[] = { … }: %s' % (path, change_route('options')))
    close = cpp.match(tokens, open_index)
    options = []
    for start, end in cpp.split_top(tokens, open_index + 1, close):
        if start == end:
            continue
        parts = cpp.split_top(tokens, start + 1, end - 1)
        if len(parts) != 3:
            raise RouteError('%s:%d: an option that is not { name, value, description }: %s' % (path, tokens[start].line, change_route('options')))
        name = literal(tokens, *parts[0])
        value = None if tokens[parts[1][0]].text == 'nullptr' else literal(tokens, *parts[1])
        description = literal(tokens, *parts[2])
        if name is None or description is None:
            raise RouteError('%s:%d: an option whose name or description is no literal: %s' % (path, tokens[start].line, change_route('options')))
        options.append({'option': name, 'value': value, 'description': description, 'line': tokens[start].line})
    if not options:
        raise RouteError('%s: c_Arguments is empty: %s' % (path, change_route('options')))
    return options


def cli_usage(reader):
    source = reader.source(c_CliUsage, 'options')
    tokens = source.tokens
    body = function_body(tokens, 'GetUsageText')
    if body is None:
        raise RouteError('%s: no function GetUsageText: %s' % (c_CliUsage, change_route('options')))
    text = None
    for index in range(body[0], body[1]):
        if tokens_at(tokens, index, 'format', '(') and tokens[index + 2].kind == 'str':
            text = cpp.string_at(tokens, index + 2)[0]
            line = tokens[index + 2].line
            break
    if text is None:
        raise RouteError('%s: GetUsageText formats no usage text: %s' % (c_CliUsage, change_route('options')))
    text = text.replace('{}', '<version>').replace('{{', '{').replace('}}', '}')
    sections = {}
    current = None
    for raw in text.split('\n'):
        if raw and not raw.startswith(' '):
            head, _, rest = raw.partition(':')
            current = head.split(',')[0].strip()
            sections[current] = [rest.strip()] if rest.strip() else []
            continue
        if current is not None:
            sections[current].append(raw)
    required = ('Usage', 'Commands', 'Connection options', 'Other options', 'Environment', 'Exit codes')
    missing = [name for name in required if name not in sections]
    if missing:
        raise RouteError('%s:%d: the usage text has no section %s: %s' % (c_CliUsage, line, ', '.join(missing), change_route('options')))

    def entries(lines, pattern):
        found = []
        for raw in lines:
            match = re.match(pattern, raw)
            if match:
                found.append({'name': match.group(1).strip(), 'description': (match.group(2) or '').strip()})
            elif raw.strip() and found:
                found[-1]['description'] = (found[-1]['description'] + ' ' + raw.strip()).strip()
        return found

    usage = []
    for raw in sections['Usage']:
        if raw.startswith('  StrataCLI'):
            usage.append(raw.strip())
        elif raw.strip() and usage:
            usage[-1] += ' ' + raw.strip()
    commands = entries(sections['Commands'], r'^  ([a-z]+) {2,}(.*)$')
    connection = entries(sections['Connection options'], r'^  (--[a-z-]+(?: <[^>]+>)?|\(none\)) {2,}(.*)$')
    connection_notes = [raw.strip() for raw in sections['Connection options'] if raw.strip() and not raw.startswith('  ')]
    other = entries(sections['Other options'], r'^  (--[a-z-]+(?: <[^>]+>)?) {2,}(.*)$')
    environment = entries(sections['Environment'], r'^  ([A-Z][A-Z0-9_, ]*?) {2,}(.*)$')
    exit_codes = ' '.join(part.strip() for part in sections['Exit codes'] if part.strip())
    if not usage or not commands or not connection:
        raise RouteError('%s:%d: the usage text\'s Usage, Commands or Connection options list is empty: %s'
                         % (c_CliUsage, line, change_route('options')))
    connection_options = []
    for entry in connection:
        connection_options += re.findall(r'--[a-z][a-z0-9-]*', entry['name'] + ' ' + entry['description'])
    other_options = [re.match(r'--[a-z][a-z0-9-]*', entry['name']).group(0) for entry in other]
    programs = {'': []}
    for line_text in usage:
        words = line_text.split()
        command = words[1] if len(words) > 1 and not words[1].startswith('-') else ''
        found = re.findall(r'--[a-z][a-z0-9-]*', line_text)
        if '[connection options]' in line_text:
            found += connection_options
        listed = programs.setdefault(command, [])
        for option in found + other_options:
            if option not in listed:
                listed.append(option)
    for options in programs.values():
        options.sort()
    return {'line': line, 'usage': usage, 'commands': commands, 'connection': connection, 'connectionNotes': connection_notes,
            'other': other, 'environment': environment, 'exitCodes': exit_codes}, programs


def route_options(reader):
    editor_options = arguments_array(reader, c_EditorOptions)
    runtime_options = arguments_array(reader, c_RuntimeOptions)
    cli, cli_programs = cli_usage(reader)
    return {
        'programs': {
            'StrataEditor': {'': sorted(option['option'] for option in editor_options)},
            'StrataRuntime': {'': sorted(option['option'] for option in runtime_options)},
            'StrataCLI': cli_programs,
        },
        'details': {
            'StrataEditor': {'file': c_EditorOptions, 'options': editor_options},
            'StrataRuntime': {'file': c_RuntimeOptions, 'options': runtime_options},
            'StrataCLI': dict(cli, file=c_CliUsage),
        },
    }


# ---------------------------------------------------------------------------------------------------------------------
# script API.

def release_of(reader, commit, release, cache):
    """The first release tag (vX.Y.Z) that contains the commit, as "X.Y.Z"; the pin's release when none does yet."""
    if commit in cache:
        return cache[commit]
    code, output, error = reader.git('tag', '--contains', commit, '--list', 'v*')
    if code != 0:
        raise RouteError('git tag --contains %s in %s: %s' % (commit, reader.engine.path, error.strip()))
    versions = sorted(tuple(int(part) for part in match.groups()) for match in (c_Tag.match(name.strip()) for name in output.split()) if match)
    cache[commit] = '.'.join(str(part) for part in versions[0]) if versions else release
    return cache[commit]


def added_in(reader, name, release, cache):
    """(release, commit) of the commit that added "(*<name>)" to ScriptABI.h (git log -S, the earliest)."""
    code, output, error = reader.git('log', reader.pin, '--format=%H', '--reverse', '-S(*%s)' % name, '--', c_ScriptABI)
    if code != 0:
        raise RouteError('git log -S in %s: %s' % (reader.engine.path, error.strip()))
    commits = output.split()
    if not commits:
        raise RouteError('%s: git log -S"(*%s)" finds no commit that added %s: %s' % (c_ScriptABI, name, name, change_route('script-api')))
    return release_of(reader, commits[0], release, cache), commits[0][:12]


def abi_members(reader, name, release, cache):
    source = reader.source(c_ScriptABI, 'script-api')
    members = cpp.struct_members(source, name)
    if not members:
        raise RouteError('%s: no struct %s with members: %s' % (c_ScriptABI, name, change_route('script-api')))
    found = cpp.find_struct(source, name)
    out = []
    for member in members:
        # struct_members gives a function pointer's whole declaration as its type.
        declaration = member['type']
        kind = 'function' if '(*' in declaration.replace(' ', '') else 'data'
        record = {'name': member['name'], 'kind': kind, 'declaration': declaration, 'line': member['line'], 'comment': member['comment']}
        if kind == 'function':
            record['addedIn'], record['commit'] = added_in(reader, member['name'], release, cache)
        out.append(record)
    return {'name': name, 'line': source.tokens[found[0]].line, 'members': out}


class _Scope:
    def __init__(self, kind, name='', public=False):
        self.kind, self.name, self.public = kind, name, public


def skip_attribute(tokens, index, end):
    if index + 1 < end and tokens[index].text == '[' and tokens[index + 1].text == '[':
        close = cpp.match(tokens, index)
        if close is not None:
            return close + 1
    return index


def classify_scope(tokens, begin, end):
    angle = 0
    for index in range(begin, end):
        text = tokens[index].text
        if text == '(':
            return _Scope('other')
        if text == '<':
            angle += 1
        elif text == '>':
            angle -= 1
        elif text == 'namespace':
            return _Scope('namespace', ''.join(token.text for token in tokens[index + 1:end]))
        elif text == 'enum':
            return _Scope('other')
        elif angle == 0 and text in ('class', 'struct', 'union') and index + 1 < end and tokens[index + 1].kind == 'id':
            return _Scope('class', tokens[index + 1].text, text != 'class')
    return _Scope('other')


def public_namespace(scopes):
    components = []
    for scope in scopes:
        if scope.kind != 'namespace':
            continue
        if not scope.name:
            return None
        components += scope.name.split('::')
    if not components or components[0] != 'Strata' or 'Detail' in components:
        return None
    return '::'.join(components[1:])


def parse_function(tokens, begin, end, class_name):
    """SDKReader's ParseFunctionDeclaration: the function a declaration statement [begin, end) declares, or None."""
    function = {'class': class_name, 'static': False, 'virtual': False, 'templateParameters': []}
    while begin < end and skip_attribute(tokens, begin, end) != begin:
        begin = skip_attribute(tokens, begin, end)
    if begin + 1 < end and tokens[begin].text == 'template' and tokens[begin + 1].text == '<':
        close = cpp.match_angle(tokens, begin + 1, end)
        if close is None:
            return None
        for index in range(begin + 2, close):
            if tokens[index].text in ('typename', 'class'):
                name = index + 1
                while name < close and tokens[name].text == '...':
                    name += 1
                if name < close and tokens[name].kind == 'id':
                    function['templateParameters'].append(tokens[name].text)
        begin = close + 1
    paren = 0
    angle = 0
    index = begin
    while index < end:
        after = skip_attribute(tokens, index, end)
        if after != index:
            index = after
            continue
        token = tokens[index]
        if token.text == '(':
            paren += 1
        elif token.text == ')':
            paren -= 1
        elif paren == 0 and token.text == '<':
            angle += 1
        elif paren == 0 and token.text == '>':
            angle -= 1
        elif paren == 0 and angle == 0 and token.text in ('=', 'operator'):
            return None
        elif paren == 0 and angle == 0 and token.text == 'static':
            function['static'] = True
        elif paren == 0 and angle == 0 and token.text == 'virtual':
            function['virtual'] = True
        if token.kind != 'id' or paren != 0 or angle != 0 or index + 1 >= end or tokens[index + 1].text != '(':
            index += 1
            continue
        if token.text in c_Keywords or token.text.startswith('__'):
            index += 1
            continue
        previous = tokens[index - 1].text if index > begin else ''
        if previous in ('~', '::') or token.text == class_name:
            return None
        function['name'] = token.text
        function['nameIndex'] = index
        function['begin'] = begin
        return function
    return None


def sdk_functions(source, path):
    """SDKReader's CollectFunctions: the public functions of one SDK header, with their declarations and // comments."""
    tokens = [token for token in source.tokens if token.kind != 'pp']
    functions = []
    scopes = []
    statement = 0
    index = 0
    while index < len(tokens):
        text = tokens[index].text
        after = skip_attribute(tokens, index, len(tokens))
        if after != index:
            index = after
            continue
        scope = scopes[-1] if scopes else None
        if scope and scope.kind == 'class' and index + 1 < len(tokens) and tokens[index + 1].text == ':' and text in ('public', 'private', 'protected'):
            scope.public = text == 'public'
            index += 2
            statement = index
            continue
        if text not in ('{', '}', ';') or tokens[index].kind != 'punct':
            index += 1
            continue
        path_name = public_namespace(scopes)
        in_class = scope is not None and scope.kind == 'class' and scope.public
        in_namespace = scope is not None and scope.kind == 'namespace'
        if path_name is not None and (in_class or in_namespace):
            function = parse_function(tokens, statement, index, scope.name if in_class else '')
            if function and not any(outer.kind == 'class' and not outer.public for outer in scopes):
                if not in_class:
                    function['namespace'] = path_name
                first = tokens[function['begin']]
                last = index - 1
                while last > function['nameIndex'] and tokens[last].text in ('{',):
                    last -= 1
                declaration = cpp.spelled(source, source.tokens.index(first), source.tokens.index(tokens[last]))
                comment = cpp.comment_before(source, first.line)
                functions.append({'class': function['class'], 'namespace': function.get('namespace', ''), 'name': function['name'],
                                  'static': function['static'], 'virtual': function['virtual'],
                                  'templateParameters': function['templateParameters'], 'declaration': declaration,
                                  'comment': comment, 'file': path, 'line': first.line})
        if text == '{':
            scopes.append(classify_scope(tokens, statement, index))
        elif text == '}' and scopes:
            scopes.pop()
        statement = index + 1
        index += 1
    return functions


def sdk_macros(source, path):
    macros = []
    for token in source.tokens:
        if token.kind != 'pp':
            continue
        match = re.match(r'#\s*define\s+(ST_SCRIPT_[A-Z0-9_]+)(\([^)]*\))?', token.text)
        if not match or match.group(1).startswith('ST_SCRIPT_DETAIL_'):
            continue
        macros.append({'name': match.group(1), 'parameters': (match.group(2) or '').strip('()'), 'file': path, 'line': token.line,
                       'comment': cpp.comment_before(source, token.line)})
    return macros


def route_script_api(reader, release):
    cache = {}
    host = abi_members(reader, 'StrataScriptHostAPI', release, cache)
    classes = abi_members(reader, 'StrataScriptClassDesc', release, cache)
    headers = sorted(path for _, kind, _, path in reader.tree() if kind == 'blob' and path.startswith(c_SDKFolder)
                     and path.rsplit('.', 1)[-1] in ('h', 'hpp', 'cpp') and path != c_ScriptABI)
    functions = []
    macros = []
    for path in headers:
        source = reader.source(path, 'script-api')
        functions += sdk_functions(source, path)
        macros += sdk_macros(source, path)
    for name in ('ST_SCRIPT_CLASS', 'ST_SCRIPT_FIELD'):
        if name not in {macro['name'] for macro in macros}:
            raise RouteError('%s: no #define %s: %s' % (c_SDKFolder, name, change_route('script-api')))
    if not functions:
        raise RouteError('%s: no public SDK function (SDKReader\'s rules): %s' % (c_SDKFolder, change_route('script-api')))
    return {'file': c_ScriptABI, 'hostAPI': host, 'classDesc': classes, 'sdk': {'headers': headers, 'functions': functions,
                                                                                'macros': macros}}


# ---------------------------------------------------------------------------------------------------------------------
# perf budgets, limits.

def route_performance(reader):
    text = reader.need(c_Budgets, 'performance')
    try:
        data = json.loads(text)
    except ValueError as error:
        raise RouteError('%s: not valid JSON (%s): %s' % (c_Budgets, error, change_route('performance')))
    comment = data.get('_comment') if isinstance(data, dict) else None
    entries = []
    for name, value in (data.items() if isinstance(data, dict) else []):
        if name.startswith('_'):
            continue
        if not isinstance(value, dict) or 'Unit' not in value or not ('Budget' in value or value.get('Provisional')):
            raise RouteError('%s: the entry %s has neither a Budget nor Provisional: true: %s' % (c_Budgets, name, change_route('performance')))
        line = next((number for number, raw in enumerate(text.split('\n'), 1) if raw.strip().startswith('"%s"' % name)), 0)
        entries.append(dict({'name': name, 'line': line}, **value))
    if not entries:
        raise RouteError('%s: no budget: %s' % (c_Budgets, change_route('performance')))
    return {'file': c_Budgets, 'comment': comment if isinstance(comment, list) else [comment] if comment else [], 'budgets': entries}


def declared_constants(source):
    """{name: [(expression text, line)]} of every `name = expression;` or `name{expression};` the file declares with constexpr
    or const (a name declared twice, in two scopes, has two entries)."""
    tokens = source.tokens
    found = {}
    for index in range(1, len(tokens) - 1):
        token = tokens[index]
        if token.kind != 'id' or tokens[index + 1].text not in ('=', '{'):
            continue
        # The declaration's words before the name, back to the end of the previous statement or an access label ("::" is
        # one token, so ":" alone ends a label).
        back = index - 1
        qualifiers = set()
        while back >= 0 and tokens[back].text not in (';', '{', '}', ')', ':', ','):
            qualifiers.add(tokens[back].text)
            back -= 1
        if not qualifiers & {'constexpr', 'const'}:
            continue
        position = index + 2
        depth = 0
        while position < len(tokens):
            text = tokens[position].text
            if text in ('(', '[', '{'):
                depth += 1
            elif text in (')', ']', '}'):
                if depth == 0:
                    break
                depth -= 1
            elif text == ';' and depth == 0:
                break
            position += 1
        end = position
        found.setdefault(token.text, []).append((cpp.spelled(source, index + 2, end - 1) if end > index + 2 else '', token.line))
    return found


def route_limits(reader, limits_path):
    try:
        with open(limits_path, encoding='utf-8') as file:
            listed = json.load(file)
    except (OSError, ValueError) as error:
        raise RouteError('%s: %s: write it as {"limits": [{"file", "name"}]} (plan/pipelines.md §7.1)' % (limits_path, error))
    entries = listed.get('limits') if isinstance(listed, dict) else None
    if not isinstance(entries, list) or not entries:
        raise RouteError('tools/reference-limits.json: no "limits" list: write it as {"limits": [{"file", "name"}]} (plan/pipelines.md §7.1)')
    out = []
    problems = []
    for number, entry in enumerate(entries):
        where = 'tools/reference-limits.json: limits[%d]' % number
        if not isinstance(entry, dict) or not isinstance(entry.get('file'), str) or not isinstance(entry.get('name'), str):
            problems.append('%s: give "file" (an engine path) and "name" (the constant, with its class: Scene::c_MaxEntities)' % where)
            continue
        path = entry['file']
        name = entry['name']
        short = name.split('::')[-1]
        text = reader.text(path)
        if text is None:
            problems.append('%s: %s does not exist at the pin: fix the entry or remove it' % (where, path))
            continue
        source = cpp.tokenize(text)
        constants = declared_constants(source)
        if short not in constants:
            problems.append('%s: %s declares no constant %s at the pin: fix the entry or remove it' % (where, path, short))
            continue
        if len(constants[short]) > 1:
            problems.append('%s: %s declares %s %d times: the entry cannot tell which; name another constant' % (where, path, short,
                                                                                                         len(constants[short])))
            continue
        expression, line = constants[short][0]
        names = {}
        for other, values in constants.items():
            if len(values) == 1 and other != short:
                value = cpp.evaluate(values[0][0])
                if value is not None:
                    names[other] = value
        substituted = expression
        for text_part, target in sorted((entry.get('substitute') or {}).items()):
            value = substitute_value(reader, target)
            if value is None:
                problems.append('%s: the substitute for "%s" (%s) does not resolve at the pin: fix the entry' % (where, text_part, json.dumps(target)))
                break
            substituted = substituted.replace(text_part, repr(value))
        else:
            value = cpp.evaluate(substituted, names)
            if value is None:
                problems.append('%s: %s:%d: %s = %s is no constant the tool can evaluate: give "substitute" for the names it uses'
                                % (where, path, line, short, expression))
                continue
            out.append({'name': name, 'key': 'limits.' + name.replace('::', '.'), 'file': path, 'line': line, 'expression': expression,
                        'value': value, 'comment': cpp.comment_on(source, line) or cpp.comment_before(source, line)})
    if problems:
        raise RouteError('; '.join(problems))
    return {'limits': out}


def substitute_value(reader, target):
    """The value of the constant a substitute names: {"file", "line", "name"} (a vendor file is read at its submodule's
    commit)."""
    if not isinstance(target, dict) or not all(isinstance(target.get(key), str) for key in ('file', 'name')) or not isinstance(target.get('line'), int):
        return None
    path = target['file']
    inside = reader.engine.submodule_of(reader.pin, path)
    if inside:
        folder, relative = inside
        commit = reader.engine.gitlink(reader.pin, folder)
        try:
            lines = reader.engine.submodule(folder).read(commit, relative)
        except Exception:  # repo.EngineError: the submodule is not checked out
            return None
    else:
        lines = reader.engine.read(reader.pin, path)
    if lines is None or not 1 <= target['line'] <= len(lines):
        return None
    match = re.search(r'\b%s\s*=\s*([^;]+);' % re.escape(target['name']), lines[target['line'] - 1])
    return cpp.evaluate(match.group(1)) if match else None


# ---------------------------------------------------------------------------------------------------------------------
# build.

def cmake_commands(text):
    """[(command, [arguments], line)] of a CMake file (quoted arguments unquoted; comments dropped)."""
    commands = []
    index = 0
    line = 1
    length = len(text)
    while index < length:
        char = text[index]
        if char == '\n':
            line += 1
            index += 1
            continue
        if char == '#':
            if text.startswith('#[[', index) or re.match(r'#\[=*\[', text[index:index + 8]):
                close = text.find(']]', index)
                line += text[index:close].count('\n')
                index = close + 2 if close >= 0 else length
                continue
            end = text.find('\n', index)
            index = length if end < 0 else end
            continue
        match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', text[index:])
        if not match:
            index += 1
            continue
        name = match.group(0)
        position = index + len(name)
        while position < length and text[position] in ' \t':
            position += 1
        if position >= length or text[position] != '(':
            index = position
            continue
        start_line = line
        arguments = []
        depth = 0
        position += 1
        current = None
        while position < length:
            char = text[position]
            if char == '"':
                end = position + 1
                value = ''
                while end < length and text[end] != '"':
                    if text[end] == '\\' and end + 1 < length:
                        value += {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(text[end + 1], '\\' + text[end + 1])
                        end += 2
                        continue
                    if text[end] == '\n':
                        line += 1
                    value += text[end]
                    end += 1
                arguments.append(value)
                position = end + 1
                current = None
                continue
            if char == '#':
                end = text.find('\n', position)
                position = length if end < 0 else end
                continue
            if char == '\n':
                line += 1
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    position += 1
                    break
                depth -= 1
            if char in ' \t\n\r()':
                current = None
                position += 1
                continue
            if current is None:
                arguments.append('')
                current = len(arguments) - 1
            arguments[current] += char
            position += 1
        commands.append((name.lower(), arguments, start_line))
        index = position
    return commands


def route_build(reader):
    options = []
    paths = ['CMakeLists.txt'] + sorted(path for _, kind, _, path in reader.tree() if kind == 'blob' and re.match(r'^CMake/[^/]+\.cmake$', path))
    for path in paths:
        text = reader.text(path)
        if text is None:
            continue
        for command, arguments, line in cmake_commands(text):
            if command == 'option' and len(arguments) >= 2:
                options.append({'name': arguments[0], 'description': arguments[1], 'default': arguments[2] if len(arguments) > 2 else 'OFF',
                                'file': path, 'line': line})
    if not options:
        raise RouteError('CMakeLists.txt, CMake/*.cmake: no option(…): %s' % change_route('build'))
    presets_text = reader.need(c_Presets, 'build')
    shards_text = reader.need(c_Shards, 'build')
    try:
        presets = json.loads(presets_text)
        shards = json.loads(shards_text)
    except ValueError as error:
        raise RouteError('%s or %s: not valid JSON (%s): %s' % (c_Presets, c_Shards, error, change_route('build')))
    keep = ('name', 'displayName', 'description', 'hidden', 'inherits', 'generator', 'binaryDir', 'configurePreset', 'configuration',
            'cacheVariables', 'filter', 'output')
    preset_lists = {}
    for kind in ('configurePresets', 'buildPresets', 'testPresets'):
        preset_lists[kind] = [{key: preset[key] for key in keep if key in preset} for preset in presets.get(kind, [])]
    if not preset_lists['configurePresets']:
        raise RouteError('%s: no configurePresets: %s' % (c_Presets, change_route('build')))
    shard_names = [shard.get('Name') for shard in shards.get('Shards', [])]
    if not shard_names:
        raise RouteError('%s: no Shards: %s' % (c_Shards, change_route('build')))
    tests, problems = ctest_names(reader.need(c_TestsCMake, 'build'), {'shardName': shard_names})
    if problems:
        raise RouteError('; '.join(problems))
    if not tests:
        raise RouteError('%s: no add_test(NAME …): %s' % (c_TestsCMake, change_route('build')))
    return {'options': options, 'presets': preset_lists, 'tests': tests, 'shards': shards}


def ctest_names(text, lists):
    """[{name, labels, line}] of the add_test(NAME …) of a CMake file, with foreach loops over literal items and the lists
    given (variable: items) expanded; and problems for names that hold another variable."""
    commands = cmake_commands(text)
    tests = {}
    order = []
    problems = []
    loops = []

    def expand(value):
        values = [value]
        for variable, items in [(loop[0], loop[1]) for loop in loops] + list(lists.items()):
            token = '${%s}' % variable
            # A loop without literal items (RANGE, IN LISTS) leaves its variable, which is reported below.
            values = [item_value.replace(token, item) for item_value in values for item in ((items or [token]) if token in item_value else [''])]
        return values

    for command, arguments, line in commands:
        if command == 'foreach' and arguments:
            items = arguments[1:]
            if items[:1] in (['RANGE'], ['IN']):
                items = []
            loops.append((arguments[0], items))
        elif command == 'endforeach' and loops:
            loops.pop()
        elif command == 'add_test' and len(arguments) >= 2 and arguments[0] == 'NAME':
            for name in expand(arguments[1]):
                if '${' in name:
                    problems.append('%s:%d: the CTest name %s holds a variable the parse cannot expand: %s' % (c_TestsCMake, line, name,
                                                                                                           change_route('build')))
                    continue
                if name not in tests:
                    tests[name] = {'name': name, 'labels': [], 'line': line}
                    order.append(name)
        elif command == 'set_tests_properties' and 'PROPERTIES' in arguments:
            names = arguments[:arguments.index('PROPERTIES')]
            properties = arguments[arguments.index('PROPERTIES') + 1:]
            labels = []
            for index in range(0, len(properties) - 1, 2):
                if properties[index] == 'LABELS':
                    labels = [label for label in properties[index + 1].split(';') if label]
            for raw in names:
                for name in expand(raw):
                    if name in tests:
                        for label in labels:
                            if label not in tests[name]['labels']:
                                tests[name]['labels'].append(label)
    return [tests[name] for name in order], problems


def route_tests(reader):
    output = reader.grep_output('TEST_SUITE(_BEGIN)?[(][^)]*', ['-h', '-o'], ['StrataTests'])
    suites = sorted({line.split('"')[1] for line in output.splitlines() if line.count('"') >= 2})
    if not suites:
        raise RouteError('StrataTests: no TEST_SUITE("…"): %s' % change_route('tests'))
    shards = json.loads(reader.need(c_Shards, 'tests'))
    tests, problems = ctest_names(reader.need(c_TestsCMake, 'tests'), {'shardName': [shard.get('Name') for shard in shards.get('Shards', [])]})
    if problems:
        raise RouteError('; '.join(problems))
    return {'suites': suites, 'ctest': [test['name'] for test in tests]}


c_DefinitionCall = re.compile(r'\b(?:target|add)_compile_definitions\s*\(')
# A definition's name: an argument's first word ("ST_DIST", "ST_WITH_GLFW=...") or what a generator expression yields
# ("$<$<CONFIG:Dist>:ST_DIST>"); never a variable (${ST_X}) or a value (=ST_X).
c_DefinitionName = re.compile(r'(?<![A-Za-z0-9_{=])ST_[A-Z0-9_]+(?![A-Za-z0-9_])')


def cmake_definitions(text):
    """The ST_ names that the target_compile_definitions and add_compile_definitions calls of a CMake file define: the
    engine's configuration and module switches (ST_DIST, ST_WITH_PHYSICS) are definitions, not #defines."""
    code = []
    quoted = False
    index = 0
    while index < len(text):  # comments dropped: "#" outside a string runs to the end of the line
        character = text[index]
        if character == '\\' and quoted:
            code.append(text[index:index + 2])
            index += 2
            continue
        if character == '"':
            quoted = not quoted
        elif character == '#' and not quoted:
            end = text.find('\n', index)
            index = len(text) if end < 0 else end
            continue
        code.append(character)
        index += 1
    code = ''.join(code)
    names = set()
    for call in c_DefinitionCall.finditer(code):
        depth, quoted, index = 1, False, call.end()
        while index < len(code) and depth:
            character = code[index]
            if character == '\\' and quoted:
                index += 1
            elif character == '"':
                quoted = not quoted
            elif not quoted and character == '(':
                depth += 1
            elif not quoted and character == ')':
                depth -= 1
            index += 1
        names.update(c_DefinitionName.findall(code[call.end():index - 1]))
    return sorted(names)


def route_macros(reader):
    output = reader.grep_output('#[[:space:]]*define[[:space:]]+ST_[A-Z0-9_]+', ['-h', '-o'], ['.'])
    macros = {line.split()[-1] for line in output.splitlines() if line.strip()}
    for path in reader.grep('(target|add)_compile_definitions', ['.']):
        if path.endswith('.cmake') or os.path.basename(path) == 'CMakeLists.txt':
            macros.update(cmake_definitions(reader.text(path) or ''))
    macros = sorted(macros)
    if not macros:
        raise RouteError('the engine: no #define ST_…: %s' % change_route('macros'))
    return {'macros': macros}


def route_frame_stages(reader):
    """The names of the frame profiler's stages (tools/names.py): the strings of c_BuiltinFrameStages, the first string
    argument of every RegisterStage, RegisterGPUStage and ST_PROFILE_STAGE call, and each scene system's
    ProfileStage = "…"."""
    source = reader.source(c_FrameProfiler, 'frame-stages')
    open_index = find_initializer(source, 'c_BuiltinFrameStages')
    close = cpp.match(source.tokens, open_index) if open_index is not None else None
    if close is None:
        raise RouteError('%s: no c_BuiltinFrameStages = { … }: %s' % (c_FrameProfiler, change_route('frame-stages')))
    stages = {text for text, _ in cpp.strings(source.tokens, open_index, close)}
    # The CPU stages' table (pipelines.md §7.1, "CPU stages"; rulings-10.md, R48): where each is declared, where it is
    # timed, and whether it lies in the frame's work time.
    cpu = {}
    gpu = set()

    def stage(name):
        return cpu.setdefault(name, {'name': name, 'declared': [], 'timed': [], 'inWorkTime': True})

    tokens = source.tokens
    for index in range(open_index, close - 2):
        if tokens[index].kind == 'str' and tokens_at(tokens, index + 1, ',') and tokens[index + 2].text in ('true', 'false'):
            found = stage(tokens[index].value)
            found['declared'].append({'by': 'c_BuiltinFrameStages', 'file': c_FrameProfiler, 'line': tokens[index].line})
            found['inWorkTime'] = tokens[index + 2].text == 'true'
    for path in reader.grep(r'(RegisterStage|RegisterGPUStage|ST_PROFILE_STAGE)\("|ProfileStage = "', ['Strata/src', c_Editor, 'StrataRuntime/src']):
        tokens = reader.source(path, 'frame-stages').tokens
        for index in range(len(tokens) - 2):
            text = tokens[index].text
            if text in c_StageCalls and tokens_at(tokens, index + 1, '(') and tokens[index + 2].kind == 'str':
                name = tokens[index + 2].value
                stages.add(name)
                end = cpp.match(tokens, index + 1) or index + 3
                arguments = [token.text for token in tokens[index + 3:end]]
                if text == 'RegisterGPUStage' or 'GPU' in arguments:
                    gpu.add(name)
                elif text == 'ST_PROFILE_STAGE':
                    stage(name)['timed'].append({'file': path, 'line': tokens[index].line})
                else:
                    stage(name)['declared'].append({'by': text, 'file': path, 'line': tokens[index].line})
                    if arguments[:2] == [',', 'false']:
                        stage(name)['inWorkTime'] = False
            elif text == 'ProfileStage' and tokens_at(tokens, index + 1, '=') and tokens[index + 2].kind == 'str':
                stages.add(tokens[index + 2].value)
                stage(tokens[index + 2].value)['declared'].append({'by': 'ProfileStage', 'file': path, 'line': tokens[index].line})
    def order(name):
        """The built-in stages in the profiler's order, then the others by name."""
        builtin = [item['line'] for item in cpu[name]['declared'] if item['by'] == 'c_BuiltinFrameStages']
        return (0, builtin[0], '') if builtin else (1, 0, name)

    return {'stages': sorted(stages), 'cpu': [cpu[name] for name in sorted(cpu, key=order) if name not in gpu]}


def route_paths(reader):
    entries = reader.tree()
    paths = sorted(path for mode, kind, _, path in entries if kind == 'blob')
    submodules = {path: object_id for mode, kind, object_id, path in entries if kind == 'commit'}
    if not paths:
        raise RouteError('the engine: git ls-tree -r lists no file at the pin: %s' % change_route('paths'))
    return {'paths': paths, 'submodules': dict(sorted(submodules.items()))}


def route_ui_literals(reader):
    files = sorted(path for _, kind, _, path in reader.tree() if kind == 'blob' and (path.startswith(c_UIFolders) or path in c_UIFiles)
                   and path.rsplit('.', 1)[-1] in ('h', 'cpp'))
    literals = set()
    for path in files:
        source = reader.source(path, 'ui-literals')
        for text, _ in cpp.strings(source.tokens, 0, len(source.tokens)):
            text = text.split('##', 1)[0].strip()
            if text:
                literals.add(text)
    if not literals:
        raise RouteError('StrataEditor/src/UI, Panels, EditorLayer.cpp: no string literal: %s' % change_route('ui-literals'))
    return {'literals': sorted(literals)}


def parse_all(engine, pin, release, limits_path):
    reader = Reader(engine, pin)
    routes = [
        ('commands', lambda: route_commands(reader)),
        ('components', lambda: route_components(reader)),
        ('asset-types', lambda: route_asset_types(reader)),
        ('quality', lambda: route_quality(reader)),
        ('gpu-stages', lambda: route_gpu_stages(reader)),
        ('render-stats', lambda: route_render_stats(reader)),
        ('renderer', lambda: route_renderer(reader)),
        ('perf-log', lambda: route_perf_log(reader)),
        ('options', lambda: route_options(reader)),
        ('script-api', lambda: route_script_api(reader, release)),
        ('performance', lambda: route_performance(reader)),
        ('limits', lambda: route_limits(reader, limits_path)),
        ('build', lambda: route_build(reader)),
        ('tests', lambda: route_tests(reader)),
        ('macros', lambda: route_macros(reader)),
        ('frame-stages', lambda: route_frame_stages(reader)),
        ('paths', lambda: route_paths(reader)),
        ('ui-literals', lambda: route_ui_literals(reader)),
    ]
    data = {}
    problems = []
    for name, route in routes:
        try:
            data[name] = dict({'pin': pin}, **route())
        except RouteError as error:
            problems.append(str(error))
    return data, problems
