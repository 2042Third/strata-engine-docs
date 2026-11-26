#!/usr/bin/env python3
"""The book's own programs (plan/pipelines.md §4): code that is not the engine's. A fence with sketch="<file>" is a copy
of sketches/<file>, a fence with output-of="<file>" is what that program prints, and a fence with the flag pseudocode is
neither compiled nor run.

    python -I tools/sketches.py fill  [pages...]
    python -I tools/sketches.py check [--no-compile] [--engine <clone>] [--slangc <path>] [pages...]

Names. A page's sketch files are sketches/<part>-<chapter>-<name>.<ext> (core/time's are core-time-<name>.cpp), so two
pages never collide; check fails on a sketch fence whose file does not carry its page's prefix.

C++ (.cpp, .cc, .cxx) is compiled by $CXX, else the first of g++, clang++ and c++ on the PATH, with -std=c++20 -Wall
-Wextra -Werror, and with --engine also -isystem <clone>/Strata/vendor/glm: the clone's checkout of glm, which must be
at the commit the pin records for it. A sketch whose output a page shows is run, at most 10 seconds, and its output is
compared with the output-of fence. A sketch whose output differs by platform by design (the size of long, of wchar_t)
shows one output fence per platform, each naming it: output-of="<file>" platform="windows|linux|macos". A run compares
the fence of the platform it runs on (fill writes only that one) and leaves the others to the runs on theirs.

Slang (<name>.<vert|frag|comp>.slang) is compiled by the slangc of the release that CMake/StrataSlang.cmake pins at the
pin (STRATA_SLANG_VERSION): slangc <file> -target spirv -entry main -stage <vertex|fragment|compute>
-I <clone>/Strata/shaders -o <scratch file>. check first runs slangc -version and requires that version in its output.
--slangc names the program (default: slangc on the PATH); Slang sketches need --engine.

fill writes the copies and the outputs into the fences. check fails (exit 1) when a fence differs from its file or
output, a sketch does not compile or compiles with a warning, a program exits with a code other than 0, or runs longer
than 10 seconds; it also compiles the files of sketches/ that no fence shows (with pages named, only those that carry
one of their prefixes). With --no-compile only the copies are compared. Exit 2: no C++ compiler (or no slangc) when a sketch
needs one, a slangc of another version, glm not at the pinned commit, or a clone without the pin (§1.4, check 1).

Every message names the page (or the sketch) and the line. Only the standard library is used. Exit codes: 0 all is
well, 1 problems were found, 2 usage or environment errors.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import markdown, repo  # noqa: E402

c_CppExtensions = ('.cpp', '.cc', '.cxx')
c_SlangStages = {'vert': 'vertex', 'frag': 'fragment', 'comp': 'compute'}
c_RunSeconds = 10
c_Glm = 'Strata/vendor/glm'
# The platforms an output fence may name (platform="..."), in the order a page shows them (its sync=os tabs).
c_Platforms = ('windows', 'linux', 'macos')


class SketchError(Exception):
    """A problem of one sketch: exit code 1."""


class UsageError(Exception):
    """A missing or wrong tool, or an engine without the pin: exit code 2."""


def find_compiler(otherwise='run check --no-compile'):
    """$CXX, else the first of g++, clang++ and c++ on the PATH. otherwise is the caller's way to go on without one."""
    configured = os.environ.get('CXX')
    if configured:
        found = shutil.which(configured)
        if not found:
            raise UsageError('CXX names %s, which is not a program on the PATH: set CXX to the full path of a C++ compiler' % configured)
        return found
    for name in ('g++', 'clang++', 'c++'):
        found = shutil.which(name)
        if found:
            return found
    raise UsageError('no C++ compiler found: set CXX or put g++ on the PATH, or %s' % otherwise)


def sketch_fences(text):
    """(fence, kind, file) for every fence of a page that copies a sketch or shows its output."""
    result = []
    for fence in markdown.fences(text):
        if 'sketch' in fence.attributes:
            result.append((fence, 'sketch', fence.attributes['sketch']))
        elif 'output-of' in fence.attributes:
            result.append((fence, 'output', fence.attributes['output-of']))
    return result


def current_platform():
    """The platform="..." name of the machine this check runs on (None on another system)."""
    if sys.platform == 'win32':
        return 'windows'
    if sys.platform.startswith('linux'):
        return 'linux'
    if sys.platform == 'darwin':
        return 'macos'
    return None


def platform_problems(path, fences):
    """(path, line, message) for the output fences of a page that name platforms wrongly: a sketch whose output differs
    by platform shows exactly one fence per platform, every one of them naming its platform."""
    problems = []
    by_name = {}
    for fence, kind, name in fences:
        if kind == 'output':
            by_name.setdefault(name, []).append(fence)
    for name, group in by_name.items():
        named = [fence for fence in group if 'platform' in fence.attributes]
        if not named:
            continue
        seen = set()
        for fence in group:
            platform = fence.attributes.get('platform')
            if platform is None:
                problems.append((path, fence.open_line, 'the output of sketches/%s is shown per platform: this fence names '
                                 'its platform too (platform="windows", "linux" or "macos")' % name))
            elif platform not in c_Platforms:
                problems.append((path, fence.open_line, 'platform="%s" is not one of %s' % (platform, ', '.join(c_Platforms))))
            elif platform in seen:
                problems.append((path, fence.open_line, 'the output of sketches/%s on %s is shown twice: keep one fence per '
                                 'platform' % (name, platform)))
            else:
                seen.add(platform)
        missing = [platform for platform in c_Platforms if platform not in seen]
        if missing:
            problems.append((path, named[0].open_line, 'the output of sketches/%s is shown per platform, so every platform has '
                             'its fence: add platform="%s"' % (name, '", "'.join(missing))))
    return problems


def page_prefix(page_id):
    return page_id.replace('/', '-') + '-'


def read_sketch(layout, name):
    if os.path.basename(name) != name or name.startswith('.'):
        raise SketchError('"%s" must be a file name in sketches/: name the file without a folder' % name)
    path = os.path.join(layout.sketches, name)
    if not os.path.isfile(path):
        raise SketchError('sketches/%s does not exist: write it, or correct the name' % name)
    return repo.read_text(path).rstrip('\n').split('\n')


def slang_stage(name):
    match = re.match(r'^.+\.(vert|frag|comp)\.slang$', name)
    return c_SlangStages[match.group(1)] if match else None


def environment_for(program):
    # A compiler outside the system folders (MSYS2's g++ on Windows) needs its own folder on the PATH to run what it built.
    env = dict(os.environ)
    env['PATH'] = os.path.dirname(program) + os.pathsep + env.get('PATH', '')
    return env


class Toolchain:
    """The compilers a check uses, found once, and the engine's pinned glm and Slang."""

    def __init__(self, layout, engine_path, slangc, compile_code):
        self.layout = layout
        self.compile_code = compile_code
        self.engine_path = engine_path
        self.slangc_option = slangc
        self.compiler = None
        self.glm = None
        self.slangc = None
        self.slang_version = None
        self.engine = None
        self.pin = None
        if engine_path:
            try:
                self.engine = repo.Engine(engine_path)
                self.pin = self.engine.resolve(repo.read_pin(layout.pin_file)['commit'])
            except repo.EngineError as error:
                raise UsageError('%s (pipelines.md §1.4, check 1)' % error)

    def close(self):
        if self.engine is not None:
            self.engine.close()

    def cpp(self):
        if self.compiler is None:
            self.compiler = find_compiler()
            if self.engine is not None:
                self.glm = glm_include(self.engine, self.pin)
        return self.compiler

    def slang(self):
        """(slangc, the shaders folder) for Slang sketches; checks slangc's version once."""
        if self.slangc is None:
            if self.engine is None:
                raise UsageError('Slang sketches compile against the engine\'s shaders: pass --engine <clone>')
            self.slang_version = slang_version(self.engine, self.pin)
            program = self.slangc_option or shutil.which('slangc')
            if not program or not shutil.which(program):
                raise UsageError('no slangc found: pass --slangc <path> to the slangc of Slang %s (CMake/StrataSlang.cmake at the pin)' % self.slang_version)
            program = shutil.which(program)
            result = subprocess.run([program, '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = result.stdout.decode('utf-8', 'replace')
            if self.slang_version not in output:
                raise UsageError('%s -version prints "%s", but the pin builds with Slang %s (CMake/StrataSlang.cmake): use that '
                                 'release' % (program, output.strip().splitlines()[0] if output.strip() else '', self.slang_version))
            self.slangc = program
        return self.slangc, os.path.join(self.engine.path, 'Strata', 'shaders')


def glm_include(engine, pin):
    """The clone's checkout of glm, after checking that it is at the commit the pin records."""
    recorded = engine.gitlink(pin, c_Glm)
    if not recorded:
        raise UsageError('%s is not a submodule of the engine at %s: give --engine the pin clone' % (c_Glm, pin[:12]))
    folder = os.path.join(engine.path, *c_Glm.split('/'))
    result = subprocess.run(['git', '-C', folder, 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    head = result.stdout.decode('ascii', 'replace').strip()
    if result.returncode != 0 or head != recorded:
        raise UsageError('the clone\'s %s is at %s, not at %s, the commit the pin records: run git submodule update --init '
                         '--recursive --depth 1 in the clone (pipelines.md §1.3)' % (c_Glm, head[:12] or 'no commit', recorded[:12]))
    return folder


def slang_version(engine, pin):
    for line in engine.read(pin, 'CMake/StrataSlang.cmake') or []:
        match = re.match(r'^\s*set\(STRATA_SLANG_VERSION\s+"([^"]+)"\)', line)
        if match:
            return match.group(1)
    raise UsageError('CMake/StrataSlang.cmake at %s sets no STRATA_SLANG_VERSION' % pin[:12])


def compile_cpp(compiler, path, output, link, glm=None):
    """Compiles a C++ sketch (to output when link, else only checks it); raises SketchError with the compiler's words."""
    arguments = [compiler, '-std=c++20', '-Wall', '-Wextra', '-Werror']
    if glm:
        arguments += ['-isystem', glm]
    arguments.append(path)
    arguments += ['-o', output] if link else ['-fsyntax-only']
    result = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment_for(compiler))
    if result.returncode != 0:
        text = result.stdout.decode('utf-8', 'replace').strip()
        hint = ''
        if not glm and re.search(r'#\s*include\s*[<"]glm/', repo.read_text(path)):
            hint = '\n(the sketch includes glm: pass --engine <clone>, which adds the pinned glm)'
        raise SketchError('sketches/%s does not compile:\n%s%s' % (os.path.basename(path), text, hint))


def compile_slang(slangc, shaders, path, scratch):
    name = os.path.basename(path)
    stage = slang_stage(name)
    if stage is None:
        raise SketchError('sketches/%s: a Slang sketch is named <name>.<vert|frag|comp>.slang, so that its stage is known' % name)
    output = os.path.join(scratch, name + '.spv')
    result = subprocess.run([slangc, path, '-target', 'spirv', '-entry', 'main', '-stage', stage, '-I', shaders, '-o', output],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = result.stdout.decode('utf-8', 'replace').strip()
    if result.returncode != 0:
        raise SketchError('sketches/%s does not compile:\n%s' % (name, text))
    if re.search(r'\bwarning\b', text, re.IGNORECASE):
        raise SketchError('sketches/%s compiles with a warning (warnings fail the check):\n%s' % (name, text))


def run_program(program, name, timeout, env):
    """The lines a compiled sketch prints; raises SketchError on a failure."""
    try:
        result = subprocess.run([program], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        raise SketchError('sketches/%s ran longer than %d seconds: make it do less, so that it ends sooner' % (name, timeout))
    if result.returncode != 0:
        raise SketchError('sketches/%s exited with %d (%s): make it end with exit code 0' % (
            name, result.returncode, result.stderr.decode('utf-8', 'replace').strip() or 'no message'))
    return result.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').rstrip('\n').split('\n')


def run_sketch(tools, name, scratch):
    """The lines a C++ sketch prints (compiled into the scratch folder)."""
    path = os.path.join(tools.layout.sketches, name)
    program = os.path.join(scratch, os.path.splitext(name)[0] + ('.exe' if os.name == 'nt' else ''))
    compiler = tools.cpp()
    compile_cpp(compiler, path, program, True, tools.glm)
    return run_program(program, name, c_RunSeconds, environment_for(compiler))


def compile_one(tools, name, scratch):
    path = os.path.join(tools.layout.sketches, name)
    if name.endswith(c_CppExtensions):
        compiler = tools.cpp()
        compile_cpp(compiler, path, None, False, tools.glm)
    elif name.endswith('.slang'):
        slangc, shaders = tools.slang()
        compile_slang(slangc, shaders, path, scratch)


def process(layout, pages, mode, tools, named=False):
    """Fills or checks every sketch fence; returns problems as (path, line, message). check also compiles the files of
    sketches/ that no fence shows: all of them, or with named pages only those that carry one of their prefixes."""
    problems = []
    outputs = {}
    compiled = set()
    with tempfile.TemporaryDirectory(prefix='sketches-') as scratch:
        for page, path in pages:
            text = repo.read_text(path)
            new_text = text
            fences = sketch_fences(text)
            problems.extend(platform_problems(path, fences))
            for fence, kind, name in reversed(fences):
                platform = fence.attributes.get('platform') if kind == 'output' else None
                if platform is not None and platform != current_platform():
                    continue  # the run on that platform compares it
                try:
                    if not name.startswith(page_prefix(page)):
                        raise SketchError('the sketch "%s" of %s is named %s<name>.<ext> (pipelines.md §4): rename the file and the '
                                          'fence' % (name, page, page_prefix(page)))
                    if kind == 'sketch':
                        expected = read_sketch(layout, name)
                        if mode == 'check' and tools.compile_code and name not in compiled:
                            compile_one(tools, name, scratch)
                            compiled.add(name)
                    else:
                        read_sketch(layout, name)
                        if not tools.compile_code:
                            continue
                        if not name.endswith(c_CppExtensions):
                            raise SketchError('output-of="%s": only C++ sketches are run: show the output of a C++ sketch' % name)
                        if name not in outputs:
                            outputs[name] = run_sketch(tools, name, scratch)
                        expected = outputs[name]
                except SketchError as error:
                    problems.append((path, fence.open_line, str(error)))
                    continue
                if fence.body == expected:
                    continue
                if mode == 'fill':
                    new_text = markdown.replace_fence_body(new_text, fence, expected)
                else:
                    what = 'sketches/%s' % name if kind == 'sketch' else 'what sketches/%s prints' % name
                    problems.append((path, fence.open_line, 'the fence differs from %s: run python -I tools/sketches.py fill' % what))
            if mode == 'fill' and new_text != text:
                repo.write_text(path, new_text)
                print('%s: filled' % layout.relative(path))
        if tools.compile_code and mode == 'check':
            for name in sorted(os.listdir(layout.sketches)) if os.path.isdir(layout.sketches) else []:
                if name in compiled or not name.endswith(c_CppExtensions + ('.slang',)):
                    continue
                if named and not any(name.startswith(page_prefix(page)) for page, _ in pages):
                    continue  # another page's file: the check of that page or of the whole book compiles it
                try:
                    compile_one(tools, name, scratch)
                except SketchError as error:
                    problems.append((os.path.join(layout.sketches, name), 1, str(error)))
    return problems


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Copies, compiles and runs the book\'s sketches (plan/pipelines.md §4).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['fill', 'check'])
    parser.add_argument('pages', nargs='*', help='page ids (default: every page)')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--no-compile', action='store_true', help='check: compare the copies only')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone, for glm and Slang (default: $STRATA_ENGINE)')
    parser.add_argument('--slangc', help='the slangc of the pinned Slang release (default: slangc on the PATH)')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    tools = None
    try:
        known = dict(layout.pages())
        options.pages = [repo.named_page(name) for name in options.pages]
        unknown = [name for name in options.pages if name not in known]
        if unknown:
            raise UsageError('not pages of the book: %s (give page ids such as core/time)' % ', '.join(unknown))
        pages = [(page, path) for page, path in sorted(known.items()) if not options.pages or page in options.pages]
        tools = Toolchain(layout, options.engine, options.slangc, not options.no_compile)
        problems = process(layout, pages, options.command, tools, named=bool(options.pages))
    except (UsageError, OSError, ValueError) as error:
        print('sketches: %s' % error, file=sys.stderr)
        return 2
    finally:
        if tools is not None:
            tools.close()
    for path, line, message in problems:
        print('%s:%d: %s' % (layout.relative(path), line, message))
    if options.command == 'check':
        print('sketches: %d problem%s%s' % (len(problems), '' if len(problems) == 1 else 's', '' if not options.no_compile else ' (not compiled)'))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
