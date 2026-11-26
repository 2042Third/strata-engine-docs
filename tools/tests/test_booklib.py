"""The shared library: front matter, fences, the JSON Schema subset, and bootstrap's helpers."""

import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
import zipfile

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import bootstrap
from booklib import frontmatter, jsonschema, markdown, repo


class FrontmatterTests(unittest.TestCase):
    def test_reads_the_book_s_fields(self):
        data, body, line, error = frontmatter.read(helpers.frontmatter(title='"Time: delta time"', needs='[core/frame-loop, basics/tools|start/install]') + '\nBody.\n')
        self.assertIsNone(error)
        self.assertEqual(data['title'], 'Time: delta time')
        self.assertEqual(data['tracks'], ['E'])
        self.assertEqual(data['needs'], ['core/frame-loop', 'basics/tools|start/install'])
        self.assertEqual(data['time'], 30)
        self.assertEqual(data['learn'], [{'id': 'one', 'text': 'explain one thing'}, {'id': 'two', 'text': 'compute another thing'}])
        self.assertEqual(data['since'], '0.3.0')
        self.assertEqual(body.strip(), 'Body.')
        self.assertEqual(line, 18)

    def test_refuses_what_yaml_would_read_otherwise(self):
        self.assertIn('must be quoted', frontmatter.read('---\ntitle: Time: delta time\n---\n')[3])
        self.assertIn('appears twice', frontmatter.read('---\na: 1\na: 2\n---\n')[3])
        self.assertIn('no front matter', frontmatter.read('Just text.\n')[3])
        self.assertIn('no closing', frontmatter.read('---\na: 1\n')[3])

    def test_reads_numbers_and_comments_as_yaml_does(self):
        # The build reads "0.8" as a number and "C # notes" as "C" with a comment; the twin agrees (the checks then say
        # that a release is written as a string such as 0.8.0).
        self.assertEqual(frontmatter.read('---\nengine: 0.8\n---\n')[0], {'engine': 0.8})
        self.assertEqual(frontmatter.read('---\ntitle: C # notes\n---\n')[0], {'title': 'C'})

    def test_quoted_values_lists_and_nested_mappings(self):
        data = frontmatter.parse("a: 'it''s'\nb: \"x \\\"y\\\"\"\nc: [one, 'two, three']\nhero:\n  title: Hi\n  tagline: There\nd: true\n")
        self.assertEqual(data, {'a': "it's", 'b': 'x "y"', 'c': ['one', 'two, three'], 'hero': {'title': 'Hi', 'tagline': 'There'}, 'd': True})


class SharedFrontmatterTests(unittest.TestCase):
    """The cases the build's reader (src/lib/markdown.mjs) runs too: the twins must read pages alike."""

    def test_the_reader_agrees_with_the_build_on_the_shared_cases(self):
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'frontmatter.json'), encoding='utf-8') as file:
            cases = json.load(file)['cases']
        for case in cases:
            with self.subTest(case['name']):
                data, _, _, error = frontmatter.read(case['text'])
                if case.get('error'):
                    self.assertIsNotNone(error)
                elif case['data'] is None:
                    self.assertIsNone(data)
                    self.assertEqual(error, 'the page has no front matter')
                else:
                    self.assertIsNone(error)
                    self.assertEqual(data, case['data'])

    def test_errors_name_the_file_s_line_after_a_byte_order_mark_and_blank_lines(self):
        _, _, _, error = frontmatter.read('\ufeff\n\n---\ntitle: A\nbad: |\n  x\n---\n')
        self.assertTrue(error.startswith('line 5:'), error)


class MarkdownTests(unittest.TestCase):
    def test_fences_with_attributes_indentation_and_longer_markers(self):
        text = '---\ntitle: x\n---\n\n1. Step\n\n   ```cpp src="a/b.cpp#L1-L2" mark="L2"\n   int a;\n     int b;\n   ```\n\n````md\n```\ninner\n```\n````\n'
        found = markdown.fences(text)
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].lang, 'cpp')
        self.assertEqual(found[0].attributes, {'src': 'a/b.cpp#L1-L2', 'mark': 'L2'})
        self.assertEqual(found[0].body, ['int a;', '  int b;'])
        self.assertEqual((found[0].open_line, found[0].close_line), (7, 10))
        self.assertEqual(found[1].body, ['```', 'inner', '```'])

    def test_replace_fence_body_keeps_the_indentation(self):
        text = '- item\n\n  ```cpp\n  old\n  ```\n'
        fence = markdown.fences(text)[0]
        self.assertEqual(markdown.replace_fence_body(text, fence, ['new', '', 'line']), '- item\n\n  ```cpp\n  new\n\n  line\n  ```\n')

    def test_prose_lines_leave_out_front_matter_and_code(self):
        text = '---\ntitle: x\n---\nOne `code`.\n```text\nnot prose\n```\nTwo.\n'
        self.assertEqual([line for _, line in markdown.prose_lines(text)], ['One `code`.', 'Two.', ''])
        self.assertEqual(markdown.strip_inline_code('a `b::c` d'), 'a        d')


class SchemaTests(unittest.TestCase):
    def test_reports_each_problem_with_its_place(self):
        schema = {'type': 'object', 'required': ['id'], 'additionalProperties': False, '$defs': {'n': {'type': 'integer', 'minimum': 1}},
                  'properties': {'id': {'type': 'string', 'pattern': '^[a-z]+$'}, 'size': {'type': 'array', 'items': {'$ref': '#/$defs/n'}, 'maxItems': 2}}}
        errors = jsonschema.Validator(schema).errors({'id': 'A', 'size': [0, 2, 3], 'extra': 1})
        messages = ['%s %s' % error for error in errors]
        self.assertIn("/id 'A' does not match ^[a-z]+$", messages)
        self.assertIn('/size holds at most 2 items', messages)
        self.assertIn('/size/0 must be at least 1', messages)
        self.assertIn('/extra is not a known field', messages)
        self.assertEqual(jsonschema.Validator(schema).errors({}), [('(the document)', 'needs "id"')])

    def test_unknown_keywords_are_refused(self):
        with self.assertRaises(jsonschema.SchemaError):
            jsonschema.Validator({'allOf': []}).errors(1)
        with self.assertRaises(jsonschema.SchemaError):
            jsonschema.Validator({'oneOf': []}).errors(1)

    def test_forms_report_the_closest_form_and_raw_pointers(self):
        schema = {'oneOf': [{'title': 'a word', 'type': 'string'},
                            {'title': 'a camera', 'type': 'object', 'required': ['position'], 'additionalProperties': False,
                             'properties': {'position': {'type': 'array'}, 'fov': {'type': 'number'}}}]}
        validator = jsonschema.Validator({'type': 'object', 'properties': {'camera': schema}})
        self.assertEqual(validator.errors({'camera': 'scene'}), [])
        self.assertEqual(validator.errors({'camera': {'position': []}}), [])
        problems = validator.problems({'camera': {'position': [], 'fov': 'wide'}})
        self.assertEqual(problems[0][0], '/camera')
        self.assertIn('is none of its 2 forms (a word; a camera); the closest form says: /camera/fov must be of type number', problems[0][1])
        self.assertEqual(jsonschema.Validator({'type': 'string'}).problems(1), [('', 'must be of type string')])
        both = jsonschema.Validator({'oneOf': [{'type': 'number'}, {'type': 'integer'}]})
        self.assertIn('matches 2 of its forms', both.errors(3)[0][1])
        self.assertEqual(both.errors(2.5), [])
        anything = jsonschema.Validator({'anyOf': [{'type': 'number'}, {'type': 'integer'}], 'maxProperties': 1})
        self.assertEqual(anything.errors(3), [])
        self.assertIn('holds at most 1 entries', jsonschema.Validator({'type': 'object', 'maxProperties': 1}).errors({'a': 1, 'b': 2})[0][1])

    def test_the_keywords_of_the_editor_s_parameter_schemas(self):
        # tools/tutorials.py validates command parameters against the schemas of the commands dump, which use these.
        schema = {'type': 'object', 'properties': {'sections': {'type': 'array', 'uniqueItems': True, 'deprecated': True},
                                                   'name': {'type': 'string', 'maxLength': 3}}}
        validator = jsonschema.Validator(schema)
        self.assertEqual(validator.errors({'sections': [1, 'a', True], 'name': 'abc'}), [])
        self.assertEqual(validator.errors({'sections': [1, 1.0]}), [('/sections', 'holds the same item twice')])
        self.assertEqual(validator.errors({'name': 'abcd'}), [('/name', 'must hold at most 3 characters')])
        # A value the predicate accepts (a command step's $ref) meets every schema.
        accepting = jsonschema.Validator(schema, accept=lambda value: isinstance(value, dict) and '$ref' in value)
        self.assertEqual(accepting.errors({'name': {'$ref': 'bound'}}), [])
        self.assertEqual(validator.errors({'name': {'$ref': 'bound'}}), [('/name', 'must be of type string')])


class JsonPositionTests(unittest.TestCase):
    def test_every_value_knows_its_line(self):
        from booklib import jsonpos
        text = '{\n\t"figures": [\n\t\t{\n\t\t\t"id": "a",\n\t\t\t"size":\n\t\t\t\t[1, 2],\n\t\t\t"a/b": {"c~d": "x \\" y"}\n\t\t}\n\t]\n}\n'
        data, lines = jsonpos.load(text)
        self.assertEqual(data['figures'][0]['id'], 'a')
        self.assertEqual(lines['/figures/0/id'], 4)
        self.assertEqual(lines['/figures/0/size'], 5)  # the key's line
        self.assertEqual(lines['/figures/0/size/1'], 6)
        self.assertEqual(lines['/figures/0/a~1b/c~0d'], 7)
        self.assertEqual(jsonpos.line_of(lines, '/figures/0/missing'), 3)
        self.assertEqual(jsonpos.line_of(lines, ''), 1)
        with self.assertRaises(jsonpos.JsonError) as caught:
            jsonpos.load('{\n\t"a": 1,\n\t"b": \n}\n')
        self.assertEqual(caught.exception.line, 4)


class TreeTests(unittest.TestCase):
    def test_trees_gitlinks_submodules_and_the_pin_file(self):
        engine_repo = helpers.TempEngine()
        try:
            glm = engine_repo.add_submodule('Strata/vendor/glm', {'glm/vec3.hpp': 'struct vec3;\n'}, 'https://github.com/g-truc/glm.git')
            commit = engine_repo.commit({'Strata/src/a.cpp': 'int a;\n'})
            engine = repo.Engine(engine_repo.root)
            try:
                self.assertEqual(set(engine.tree(commit)), {'.gitmodules', 'Strata'})
                self.assertEqual(engine.gitlink(commit, 'Strata/vendor/glm'), glm)
                self.assertIsNone(engine.gitlink(commit, 'Strata/src'))
                self.assertEqual(engine.submodule_of(commit, 'Strata/vendor/glm/glm/vec3.hpp'), ('Strata/vendor/glm', 'glm/vec3.hpp'))
                self.assertIsNone(engine.submodule_of(commit, 'Strata/src/a.cpp'))
                self.assertEqual(engine.submodule('Strata/vendor/glm').read(glm, 'glm/vec3.hpp'), ['struct vec3;'])
                self.assertEqual(engine.submodule_urls(commit), {'Strata/vendor/glm': 'https://github.com/g-truc/glm.git'})
            finally:
                engine.close()
        finally:
            engine_repo.cleanup()
        folder = tempfile.mkdtemp(prefix='pin-')
        try:
            path = os.path.join(folder, 'engine.pin')
            with open(path, 'w', encoding='utf-8', newline='\n') as file:
                file.write('# old comment\ncommit %s\nrelease 0.8.0\nprerelease yes\nrepository https://example.com/engine\n' % ('a' * 40))
            repo.write_pin(path, 'b' * 40, '0.8.1', False)
            with open(path, encoding='utf-8') as file:
                text = file.read()
            self.assertTrue(text.startswith(repo.c_PinHeader))
            self.assertIn('the working tree must be at\n# the pin and clean for pictures, tutorials and the reference dump (plan/pipelines.md §1)', text)
            self.assertTrue(text.endswith('commit %s\nrelease 0.8.1\nprerelease no\nrepository https://example.com/engine\n' % ('b' * 40)))
            self.assertEqual(repo.read_pin(path)['commit'], 'b' * 40)
            with open(path, 'w', encoding='utf-8') as file:
                file.write('commit abc\n')
            with self.assertRaises(ValueError):
                repo.read_pin(path)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class PreflightTests(unittest.TestCase):
    def test_the_four_checks_of_section_1_4(self):
        from booklib import editor
        engine_repo = helpers.TempEngine()
        folder = tempfile.mkdtemp(prefix='build-')
        try:
            first = engine_repo.commit({'a.txt': 'one\n'})
            second = engine_repo.commit({'a.txt': 'two\n'})
            engine = repo.Engine(engine_repo.root)
            try:
                with self.assertRaises(editor.PreflightError) as caught:
                    editor.preflight_clone(engine, '1' * 40)
                self.assertIn('check 1', str(caught.exception))
                with self.assertRaises(editor.PreflightError) as caught:
                    editor.preflight_clone(engine, first)
                self.assertIn('not at the pin', str(caught.exception))
                self.assertEqual(editor.preflight_clone(engine, second), second)
                with open(os.path.join(engine_repo.root, 'a.txt'), 'w', encoding='utf-8') as file:
                    file.write('dirty\n')
                with self.assertRaises(editor.PreflightError) as caught:
                    editor.preflight_clone(engine, second)
                self.assertIn('is not clean', str(caught.exception))
            finally:
                engine.close()
            with self.assertRaises(editor.PreflightError) as caught:
                editor.preflight_build(folder, ('StrataEditor', 'StrataCLI'))
            self.assertIn('check 3', str(caught.exception))
            for name in ('StrataEditor', 'StrataCLI'):
                with open(editor.program_path(folder, name), 'wb') as file:
                    file.write(b'program')
            editor.preflight_build(folder, ('StrataEditor', 'StrataCLI'))
            record = editor.build_record(folder, engine_repo.root)
            self.assertEqual(record['kind'], 'package')
            self.assertEqual(len(record['editorSha256']), 64)
        finally:
            engine_repo.cleanup()
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_environment_of_every_engine_program(self):
        from booklib import editor
        os.environ['STRATA_EDITOR_TOKEN'] = 'never passed on'
        try:
            session = editor.new_session_dir()
            self.assertFalse(os.path.exists(session))
            self.assertTrue(os.path.basename(session).startswith('StrataDocs-%d-' % os.getpid()))
            self.assertEqual(os.path.dirname(session), editor.system_temp())
            env = editor.environment('B', 'W', session)
        finally:
            del os.environ['STRATA_EDITOR_TOKEN']
        self.assertNotIn('STRATA_EDITOR_TOKEN', env)
        self.assertEqual(env['STRATA_SESSION_DIR'], session)
        self.assertEqual(env['STRATA_RECENT_PROJECTS'], os.path.join('W', 'recent-projects.json'))
        self.assertEqual(env['STRATA_SCRIPT_BUILDS_DIR'], os.path.join('W', 'script-builds'))
        self.assertEqual(env['STRATA_EDITOR_PATH'], editor.program_path('B', 'StrataEditor'))
        # A script build's MSBuild nodes end with the build, so a run leaves nothing running.
        self.assertEqual(env['MSBUILDDISABLENODEREUSE'], '1')
        self.assertEqual(editor.parse_json_object('progress\n{"ProcessId": 7, "Port": 1}\n'), {'ProcessId': 7, 'Port': 1})
        self.assertIsNone(editor.parse_json_object('error: no editor'))


class ProgramTests(unittest.TestCase):
    def test_a_program_past_its_time_limit_is_ended_with_what_it_started(self):
        from booklib import editor
        folder = tempfile.mkdtemp(prefix='programs-')
        child = ('import subprocess, sys, time\n'
                 'grandchild = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])\n'
                 'print(grandchild.pid, flush=True)\n'
                 'time.sleep(120)\n')
        try:
            log = editor.Log(folder)
            with self.assertRaisesRegex(editor.EditorError, r'did not end within 3 seconds and was ended with what it started'):
                editor.run_program([sys.executable, '-c', child], os.environ.copy(), log, 'sleeper', 3)
            with open(os.path.join(folder, os.listdir(folder)[0]), encoding='utf-8') as file:
                logged = file.read()
            self.assertIn('(ended after 3 seconds)', logged)
            grandchild = int(logged.split('exit code: timeout', 1)[1].split()[0])
            for _ in range(50):
                if not editor.process_alive(grandchild):
                    break
                time.sleep(0.1)
            self.assertFalse(editor.process_alive(grandchild), 'the program\'s own child still runs')
        finally:
            shutil.rmtree(folder, ignore_errors=True)


    @unittest.skipIf(os.name == 'nt', 'process groups are POSIX\'s')
    def test_ending_a_program_of_the_caller_s_group_leaves_the_caller_running(self):
        # A program that shares its caller's process group is ended alone: ending its group would end the caller, as it
        # ended CI's unit-test step. The caller runs in a session of its own here, so that a failure ends only it.
        tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caller = ('import subprocess, sys\n'
                  'sys.path.insert(0, sys.argv[1])\n'
                  'from booklib import editor\n'
                  'program = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])\n'
                  'editor.end_process_tree(program.pid)\n'
                  'print("the caller still runs; the program ended with", program.wait(timeout=30), flush=True)\n')
        result = subprocess.run([sys.executable, '-I', '-c', caller, tools], capture_output=True, text=True, timeout=60, start_new_session=True)
        self.assertEqual(result.returncode, 0, 'the caller ended with %s: %s' % (result.returncode, result.stderr))
        self.assertIn('the caller still runs; the program ended with -9', result.stdout)

    @unittest.skipIf(os.name == 'nt', 'process groups are POSIX\'s')
    def test_programs_lead_a_process_group_of_their_own(self):
        from booklib import editor
        folder = tempfile.mkdtemp(prefix='programs-')
        try:
            program = editor.Program([sys.executable, '-c', 'import time; time.sleep(120)'], os.environ.copy(), editor.Log(folder), 'leader')
            try:
                self.assertEqual(os.getpgid(program.pid), program.pid)
                self.assertNotEqual(os.getpgid(program.pid), os.getpgrp())
            finally:
                editor.end_process_tree(program.pid)
                program.finish(30)
            self.assertFalse(program.alive())
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class EngineTests(unittest.TestCase):
    def test_reads_through_one_process_and_closes_its_pipes(self):
        engine_repo = helpers.TempEngine()
        try:
            commit = engine_repo.commit({'a/b.txt': 'one\ntwo\n'})
            engine = repo.Engine(engine_repo.root)
            self.assertEqual(engine.resolve(commit[:12]), commit)
            self.assertEqual(engine.read(commit, 'a/b.txt'), ['one', 'two'])
            self.assertTrue(engine.exists(commit, 'a'))
            self.assertIsNone(engine.read(commit, 'a/missing.txt'))
            batch = engine.batch
            engine.close()
            # Both pipes are closed, so no ResourceWarning comes when the process object goes.
            self.assertTrue(batch.stdin.closed and batch.stdout.closed)
            self.assertIsNone(engine.batch)
            with self.assertRaises(repo.EngineError):
                engine.resolve('0' * 40)
        finally:
            engine_repo.cleanup()


class BootstrapTests(unittest.TestCase):
    def test_platform_keys(self):
        self.assertEqual(bootstrap.platform_key('Windows', 'AMD64'), 'windows-x64')
        self.assertEqual(bootstrap.platform_key('MINGW64_NT-10.0', 'x86_64'), 'windows-x64')
        self.assertEqual(bootstrap.platform_key('Linux', 'x86_64'), 'linux-x64')
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.platform_key('Linux', 'aarch64')

    def test_parse_shasums(self):
        sums = bootstrap.parse_shasums('%s  node-v1-win-x64.zip\n%s *other.tar.xz\nnot a line\n' % ('a' * 64, 'B' * 64))
        self.assertEqual(sums, {'node-v1-win-x64.zip': 'a' * 64, 'other.tar.xz': 'b' * 64})

    def test_extract_refuses_members_outside_the_destination(self):
        folder = tempfile.mkdtemp()
        try:
            archive = os.path.join(folder, 'bad.zip')
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('../escape.txt', 'x')
            with self.assertRaises(bootstrap.BootstrapError):
                bootstrap.extract(archive, os.path.join(folder, 'out'))
            good = os.path.join(folder, 'good.tar.gz')
            with tarfile.open(good, 'w:gz') as bundle:
                info = tarfile.TarInfo('dir/file.txt')
                info.size = 2
                bundle.addfile(info, io.BytesIO(b'ok'))
            bootstrap.extract(good, os.path.join(folder, 'out'))
            with open(os.path.join(folder, 'out', 'dir', 'file.txt'), encoding='utf-8') as file:
                self.assertEqual(file.read(), 'ok')
        finally:
            import shutil
            shutil.rmtree(folder, ignore_errors=True)

    def test_fetch_checked_refuses_a_pin_the_official_sums_disagree_with(self):
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.fetch_checked('https://invalid.example/x', os.path.join(tempfile.gettempdir(), 'never'), 'a' * 64, 'b' * 64)

    def test_environment_scripts_keep_the_system_temp_for_the_perf_lock(self):
        env = bootstrap.environment('C:\\book\\.tools', {'node': {'archives': {'windows-x64': {'file': 'node-v26.13.0-win-x64.zip'}}}, 'typos': {'version': '1.52.1'}}, 'windows-x64')
        self.assertEqual(env['paths'][0], 'C:\\book\\.tools\\node-v26.13.0-win-x64')
        shell = bootstrap.shell_script(env, True)
        self.assertIn('STRATA_DOCS_SYSTEM_TEMP', shell)
        self.assertIn('export PATH="/c/book/.tools/node-v26.13.0-win-x64:', shell)
        self.assertIn('ASTRO_TELEMETRY_DISABLED', bootstrap.powershell_script(env))

    def test_the_windows_shell_script_keeps_the_base_path_from_msys_path_conversion(self):
        env = bootstrap.environment('C:\\book\\.tools', {'node': {'archives': {'windows-x64': {'file': 'node-v26.13.0-win-x64.zip'}}}, 'typos': {'version': '1.52.1'}}, 'windows-x64')
        shell = bootstrap.shell_script(env, True)
        self.assertIn('export MSYS2_ENV_CONV_EXCL="DOCS_BASE', shell)
        self.assertIn('export MSYS2_ARG_CONV_EXCL="--base=', shell)
        # Linux shells convert nothing.
        self.assertNotIn('MSYS2', bootstrap.shell_script(env, False))
        if os.name == 'nt' and shutil.which('bash'):
            # The real shell: DOCS_BASE and --base=/x reach a native program unchanged.
            folder = tempfile.mkdtemp(prefix='envsh-')
            try:
                script = os.path.join(folder, 'env.sh')
                with open(script, 'w', encoding='utf-8', newline='\n') as file:
                    file.write(shell)
                probe = 'import os, sys; print(os.environ["DOCS_BASE"], sys.argv[1])'
                command = '. "%s" && DOCS_BASE=/other/deep/path "%s" -c \'%s\' --base=/x/y' % (bootstrap.to_posix(script), bootstrap.to_posix(sys.executable), probe)
                result = subprocess.run(['bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertEqual(result.stdout.decode('utf-8').split(), ['/other/deep/path', '--base=/x/y'], result.stderr.decode('utf-8', 'replace'))
            finally:
                shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
