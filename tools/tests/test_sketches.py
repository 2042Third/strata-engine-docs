"""sketches.py (plan/pipelines.md §4): copies, names, glm at the pinned commit, Slang with the pinned slangc."""

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import sketches


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


def has_compiler():
    return bool(shutil.which(os.environ.get('CXX') or 'g++') or shutil.which('clang++') or shutil.which('c++'))


class SketchTests(unittest.TestCase):
    def setUp(self):
        self.engine = helpers.TempEngine()
        self.glm = self.engine.add_submodule('Strata/vendor/glm', {'glm/glm.hpp': '#pragma once\nnamespace glm { struct vec2 { float x, y; }; }\n'}, 'https://github.com/g-truc/glm.git')
        self.pin = self.engine.commit({'CMake/StrataSlang.cmake': 'set(STRATA_SLANG_VERSION "2026.20")\n', 'Strata/shaders/Include/Common.slang': '// common\n'})
        self.book = helpers.TempBook(self.pin)
        self.book.write('sketches/core-time-hello.cpp', '#include <cstdio>\nint main() { std::puts("hello"); return 0; }\n')

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def run_tool(self, *arguments):
        return quiet(sketches.main, *(list(arguments) + ['--root', self.book.root]))

    def test_fill_and_check_the_copies(self):
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp sketch="core-time-hello.cpp"\nold\n```\n')
        self.assertEqual(self.run_tool('check', '--no-compile')[0], 1)
        self.assertIn('the fence differs from sketches/core-time-hello.cpp: run python -I tools/sketches.py fill', self.run_tool('check', '--no-compile')[1])
        self.assertEqual(self.run_tool('fill')[0], 0)
        self.assertIn('int main() { std::puts("hello"); return 0; }\n```', self.book.read('src/content/docs/core/time.md'))
        self.assertEqual(self.run_tool('check', '--no-compile')[0], 0)

    def test_a_sketch_carries_its_page_s_prefix(self):
        self.book.write('sketches/hello.cpp', 'int main() { return 0; }\n')
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp sketch="hello.cpp"\nint main() { return 0; }\n```\n\n```cpp sketch="gone-file.cpp"\n```\n')
        code, output = self.run_tool('check', '--no-compile')
        self.assertEqual(code, 1)
        self.assertIn('time.md:19: the sketch "hello.cpp" of core/time is named core-time-<name>.<ext> (pipelines.md §4)', output)
        self.assertIn('the sketch "gone-file.cpp" of core/time is named core-time-<name>.<ext>', output)

    def test_no_compiler_and_a_wrong_slangc_stop_with_exit_code_2(self):
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp sketch="core-time-hello.cpp"\n```\n')
        previous = os.environ.get('CXX')
        os.environ['CXX'] = 'no-such-compiler-for-the-book'
        try:
            code, output = self.run_tool('check')
        finally:
            if previous is None:
                del os.environ['CXX']
            else:
                os.environ['CXX'] = previous
        self.assertEqual(code, 2)
        self.assertIn('CXX names no-such-compiler-for-the-book, which is not a program on the PATH: set CXX to the full path of a C++ compiler', output)
        # A Slang sketch needs the engine, and a slangc of the pinned release.
        self.book.write('sketches/core-time-tint.frag.slang', 'float4 main() : SV_Target { return 1; }\n')
        self.book.page('core/time', helpers.frontmatter() + '\n```slang sketch="core-time-tint.frag.slang"\nfloat4 main() : SV_Target { return 1; }\n```\n')
        code, output = self.run_tool('check', '--engine', '')
        self.assertEqual(code, 2)
        self.assertIn('Slang sketches compile against the engine\'s shaders: pass --engine <clone>', output)
        folder = tempfile.mkdtemp(prefix='slangc-')
        try:
            fake = os.path.join(folder, 'slangc.cmd' if os.name == 'nt' else 'slangc')
            with open(fake, 'w', encoding='utf-8', newline='\r\n' if os.name == 'nt' else '\n') as file:
                file.write('@echo slang 2025.1\n' if os.name == 'nt' else '#!/bin/sh\necho slang 2025.1\n')
            os.chmod(fake, 0o755)
            code, output = self.run_tool('check', '--engine', self.engine.root, '--slangc', fake)
            self.assertEqual(code, 2, output)
            self.assertIn('but the pin builds with Slang 2026.20 (CMake/StrataSlang.cmake): use that release', output)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_glm_must_be_at_the_commit_the_pin_records(self):
        engine = sketches.repo.Engine(self.engine.root)
        try:
            self.assertEqual(sketches.glm_include(engine, self.pin), os.path.join(self.engine.root, 'Strata', 'vendor', 'glm'))
        finally:
            engine.close()
        later = self.engine.add_submodule('Strata/vendor/glm', {'glm/later.hpp': '\n'}, 'https://github.com/g-truc/glm.git')
        self.assertNotEqual(later, self.glm)
        engine = sketches.repo.Engine(self.engine.root)
        try:
            with self.assertRaises(sketches.UsageError) as caught:
                sketches.glm_include(engine, self.pin)
            self.assertIn('not at %s, the commit the pin records' % self.glm[:12], str(caught.exception))
        finally:
            engine.close()

    def test_a_program_that_fails_or_runs_too_long_says_what_to_do(self):
        folder = tempfile.mkdtemp(dir=self.book.root)
        try:
            program = os.path.join(folder, 'broken.cmd' if os.name == 'nt' else 'broken')
            with open(program, 'w', encoding='utf-8', newline='\r\n' if os.name == 'nt' else '\n') as file:
                file.write('@echo off\necho the sketch broke 1>&2\nexit /b 3\n' if os.name == 'nt' else '#!/bin/sh\necho the sketch broke >&2\nexit 3\n')
            os.chmod(program, 0o755)
            with self.assertRaises(sketches.SketchError) as caught:
                sketches.run_program(program, 'core-time-hello.cpp', 10, None)
            self.assertEqual(str(caught.exception), 'sketches/core-time-hello.cpp exited with 3 (the sketch broke): make it end with exit code 0')
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        # The limit is the run's: a stand-in for subprocess.run says that it passed, so that no process is left running.
        expired = sketches.subprocess.TimeoutExpired(['core-time-hello'], 10)
        with mock.patch.object(sketches.subprocess, 'run', side_effect=expired):
            with self.assertRaises(sketches.SketchError) as caught:
                sketches.run_program('core-time-hello', 'core-time-hello.cpp', 10, None)
        self.assertEqual(str(caught.exception), 'sketches/core-time-hello.cpp ran longer than 10 seconds: make it do less, so that it ends sooner')

    def test_slang_stages_come_from_the_name(self):
        self.assertEqual(sketches.slang_stage('core-gpu-tint.frag.slang'), 'fragment')
        self.assertEqual(sketches.slang_stage('core-gpu-blur.comp.slang'), 'compute')
        self.assertIsNone(sketches.slang_stage('core-gpu-tint.slang'))

    @unittest.skipUnless(has_compiler(), 'no C++ compiler on the PATH')
    def test_compile_and_run_compares_the_output(self):
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp sketch="core-time-hello.cpp"\n```\n\n```text output-of="core-time-hello.cpp"\nwrong\n```\n')
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        self.assertIn('```text output-of="core-time-hello.cpp"\nhello\n```', self.book.read('src/content/docs/core/time.md'))
        self.book.write('sketches/core-time-hello.cpp', 'int main() { return undefined_name; }\n')
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('does not compile', output)

    @unittest.skipUnless(has_compiler(), 'no C++ compiler on the PATH')
    def test_a_check_of_pages_compiles_only_their_own_sketch_files(self):
        # Another page's broken sketch file fails the whole book's check, not a check of this page (and compiling
        # every file of sketches/ for one page took minutes).
        self.book.page('core/time', helpers.frontmatter() + '\n```cpp sketch="core-time-hello.cpp"\n```\n')
        self.book.page('core/jobs', helpers.frontmatter(id='core/jobs') + '\nText.\n')
        self.book.write('sketches/core-jobs-broken.cpp', 'int main() { return undefined_name; }\n')
        self.book.write('sketches/core-time-spare.cpp', 'int main() { return undefined_name; }\n')
        self.assertEqual(self.run_tool('fill')[0], 0)
        code, output = self.run_tool('check', 'core/time')
        self.assertEqual(code, 1, output)
        self.assertIn('core-time-spare.cpp', output)
        self.assertNotIn('core-jobs-broken.cpp', output)
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('core-jobs-broken.cpp', output)


if __name__ == '__main__':
    unittest.main()
