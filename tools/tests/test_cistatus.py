"""cistatus.py: CI's result through git (plan/site.md, "CI"; rulings 6, R25). A failed step writes its reason as an
::error annotation, the report job turns GitHub's answers into one record per run attempt and commits it to the branch
ci-results, and the reader fetches that branch and prints the newest attempt of a commit."""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import cistatus  # noqa: E402

c_Identity = {'name': 'Book test', 'email': 'book-test@example.invalid'}


def git(cwd, *arguments):
    return subprocess.run(['git', '-c', 'user.name=Book test', '-c', 'user.email=book-test@example.invalid'] + list(arguments), cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class StepTests(unittest.TestCase):
    def run_step(self, code, lines, title='Pages (check 1)'):
        script = 'import sys\n' + ''.join('print(%r)\n' % line for line in lines) + 'sys.exit(%d)\n' % code
        out = io.StringIO()
        result = cistatus.run_step(title, [sys.executable, '-c', script], out)
        return result, out.getvalue()

    def test_a_failed_step_writes_its_reason_as_an_error_annotation(self):
        code, output = self.run_step(3, ['checking 12 pages', 'core/time.md:4: O7: the title differs from the outline\'s row'])
        self.assertEqual(code, 3)
        lines = output.splitlines()
        # The output passes through as it is, and the annotation follows it.
        self.assertEqual(lines[:2], ['checking 12 pages', 'core/time.md:4: O7: the title differs from the outline\'s row'])
        self.assertTrue(lines[-1].startswith('::error title=Pages (check 1)::'), lines[-1])
        message = lines[-1].split('::', 2)[2]
        self.assertIn('exited 3:%0Achecking 12 pages%0Acore/time.md:4: O7', message)
        self.assertNotIn('\n', lines[-1])

    def test_a_step_that_passes_writes_no_annotation(self):
        code, output = self.run_step(0, ['ok'])
        self.assertEqual((code, output.splitlines()), (0, ['ok']))

    def test_the_annotation_escapes_what_github_reads_and_keeps_the_end_of_long_output(self):
        self.assertEqual(cistatus.escape_data('50% done\r\nnext'), '50%25 done%0D%0Anext')
        self.assertEqual(cistatus.escape_property('a: b, c'), 'a%3A b%2C c')
        code, output = self.run_step(1, ['line %d %s' % (number, 'x' * 200) for number in range(100)], title='Crawl: /x/y, lychee')
        self.assertEqual(code, 1)
        annotation = output.splitlines()[-1]
        self.assertTrue(annotation.startswith('::error title=Crawl%3A /x/y%2C lychee::'))
        message = annotation.split('::', 2)[2].replace('%0A', '\n').replace('%25', '%')
        self.assertLessEqual(len(message.encode('utf-8')), cistatus.c_MaxMessageBytes)
        self.assertTrue(message.rstrip().endswith('line 99 ' + 'x' * 200))
        self.assertNotIn('line 50 ', message)

    def test_a_command_that_does_not_start_is_a_failure_with_its_reason(self):
        out = io.StringIO()
        self.assertEqual(cistatus.run_step('Lint', ['a-program-that-does-not-exist-here'], out), 127)
        self.assertIn('::error title=Lint::a-program-that-does-not-exist-here exited 127:%0Athe command did not start', out.getvalue())

    def test_the_command_line_runs_a_step(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cistatus.main(['step', '--title', 'Exit', '--', sys.executable, '-c', 'import sys; print("no"); sys.exit(4)'])
        # run_step writes to sys.stdout as main finds it.
        self.assertEqual(code, 4)


c_Commit = 'a' * 40
c_Jobs = {'total_count': 4, 'jobs': [
    {'id': 11, 'name': 'lint', 'status': 'completed', 'conclusion': 'success', 'steps': [{'name': 'Pages', 'conclusion': 'success'}]},
    {'id': 12, 'name': 'build', 'status': 'completed', 'conclusion': 'failure',
     'steps': [{'name': 'Set up job', 'conclusion': 'success'}, {'name': 'Crawl at /x/y', 'conclusion': 'failure'}, {'name': 'Budgets', 'conclusion': 'skipped'}]},
    {'id': 13, 'name': 'release', 'status': 'completed', 'conclusion': 'skipped', 'steps': []},
    {'id': 14, 'name': 'report', 'status': 'in_progress', 'conclusion': None, 'steps': []},
]}
c_Annotations = {12: [
    {'path': '.github', 'start_line': 1, 'annotation_level': 'failure', 'title': 'Crawl at /x/y', 'message': 'crawl.py exited 1:\n/x/y/a/ answers 404'},
    {'path': '.github', 'start_line': 1, 'annotation_level': 'warning', 'title': 'Node.js 20', 'message': 'deprecated'},
]}


class RecordTests(unittest.TestCase):
    def test_the_record_holds_every_job_s_conclusion_failed_steps_and_errors(self):
        record = cistatus.build_record(c_Jobs, c_Annotations, c_Commit, 2, 'https://ci.example.invalid/runs/1', 'push', 'refs/heads/ci/site')
        self.assertEqual(record['conclusion'], 'failure')
        self.assertEqual([job['name'] for job in record['jobs']], ['build', 'lint', 'release'])
        build = record['jobs'][0]
        self.assertEqual(build['failedSteps'], ['Crawl at /x/y'])
        self.assertEqual(build['errors'], [{'title': 'Crawl at /x/y', 'message': 'crawl.py exited 1:\n/x/y/a/ answers 404', 'path': '.github', 'line': 1}])
        self.assertEqual(cistatus.record_name(c_Commit, 2), 'runs/%s-2.json' % c_Commit)
        passed = dict(c_Jobs, jobs=[dict(job, conclusion='success') if job['name'] == 'build' else job for job in c_Jobs['jobs']])
        self.assertEqual(cistatus.build_record(passed, {}, c_Commit, 1)['conclusion'], 'success')
        cancelled = dict(c_Jobs, jobs=[dict(job, conclusion='cancelled') if job['name'] == 'lint' else job for job in passed['jobs']])
        self.assertEqual(cistatus.build_record(cancelled, {}, c_Commit, 1)['conclusion'], 'failure')
        with self.assertRaises(cistatus.CIStatusError):
            cistatus.build_record(c_Jobs, {}, 'abc1234', 1)

    def test_the_record_command_reads_github_s_answers_from_files(self):
        folder = tempfile.mkdtemp(prefix='cistatus-record-')
        try:
            with open(os.path.join(folder, 'jobs.json'), 'w', encoding='utf-8') as file:
                json.dump(c_Jobs, file)
            os.makedirs(os.path.join(folder, 'annotations'))
            with open(os.path.join(folder, 'annotations', '12.json'), 'w', encoding='utf-8') as file:
                json.dump(c_Annotations[12], file)
            out = os.path.join(folder, 'runs', '%s-1.json' % c_Commit)
            with contextlib.redirect_stdout(io.StringIO()):
                code = cistatus.main(['record', '--jobs', os.path.join(folder, 'jobs.json'), '--annotations', os.path.join(folder, 'annotations'),
                                      '--commit', c_Commit, '--attempt', '1', '--out', out])
            self.assertEqual(code, 0)
            with open(out, encoding='utf-8') as file:
                self.assertEqual(json.load(file)['jobs'][0]['errors'][0]['title'], 'Crawl at /x/y')
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_a_record_is_printed_in_utf_8_whatever_the_console_s_code_page(self):
        # node --test marks passing tests with "✔", which Windows' cp1252 cannot write: the program, its output piped
        # as a reader's terminal or a script pipes it, prints the record without failing.
        folder = tempfile.mkdtemp(prefix='cistatus-utf8-')
        try:
            with open(os.path.join(folder, 'jobs.json'), 'w', encoding='utf-8') as file:
                json.dump(c_Jobs, file)
            os.makedirs(os.path.join(folder, 'annotations'))
            with open(os.path.join(folder, 'annotations', '12.json'), 'w', encoding='utf-8') as file:
                json.dump([dict(c_Annotations[12][0], message='npm test exited 124:\n✔ a test that passed')], file)
            script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cistatus.py')
            result = subprocess.run([sys.executable, '-I', script, 'record', '--jobs', os.path.join(folder, 'jobs.json'),
                                     '--annotations', os.path.join(folder, 'annotations'), '--commit', c_Commit, '--attempt', '1',
                                     '--out', os.path.join(folder, 'out.json')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
            self.assertIn('✔ a test that passed', result.stdout.decode('utf-8'))
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class PublishAndReadTests(unittest.TestCase):
    """A bare repository stands for GitHub; two clones stand for two runs, and a third for the authoring machine."""

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='cistatus-git-')
        self.remote = os.path.join(self.folder, 'remote.git')
        subprocess.run(['git', 'init', '-q', '--bare', self.remote], check=True)
        self.clones = []
        for name in ('run-a', 'run-b', 'author'):
            clone = os.path.join(self.folder, name)
            subprocess.run(['git', 'init', '-q', clone], check=True)
            git(clone, 'remote', 'add', 'origin', self.remote)
            self.clones.append(clone)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def record(self, clone, commit, attempt, conclusion):
        path = os.path.join(clone, 'record-%d.json' % attempt)
        jobs = {'jobs': [{'id': 1, 'name': 'lint', 'conclusion': conclusion, 'steps': []}]}
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(cistatus.build_record(jobs, {}, commit, attempt), file)
        return path

    def read(self, commit):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cistatus.main([commit, '--repository', self.clones[2]])
        return code, out.getvalue()

    def test_records_are_published_beside_each_other_and_the_newest_attempt_is_read(self):
        run_a, run_b, author = self.clones
        other = 'b' * 40
        self.assertEqual(self.read(c_Commit)[0], 3)  # no branch yet: no run is recorded
        cistatus.publish(self.record(run_a, c_Commit, 1, 'failure'), cwd=run_a, **c_Identity)
        cistatus.publish(self.record(run_b, other, 1, 'success'), cwd=run_b, **c_Identity)
        code, output = self.read(c_Commit)
        self.assertEqual(code, 1, output)
        self.assertIn('commit %s, attempt 1: failure' % c_Commit, output)
        # A second attempt of the run succeeds: the newest attempt is the commit's result.
        cistatus.publish(self.record(run_a, c_Commit, 2, 'success'), cwd=run_a, **c_Identity)
        code, output = self.read(c_Commit)
        self.assertEqual(code, 0, output)
        self.assertIn('attempt 2: success', output)
        self.assertEqual(self.read(other)[0], 0)
        self.assertEqual(self.read('c' * 40)[0], 3)
        files = git(author, 'ls-tree', '--name-only', 'refs/remotes/origin/ci-results', 'runs/').split()
        self.assertEqual(sorted(files), sorted(['runs/%s-1.json' % c_Commit, 'runs/%s-2.json' % c_Commit, 'runs/%s-1.json' % other]))
        # The working trees and the checked-out branches are untouched: the records live only on ci-results.
        self.assertEqual(git(run_a, 'status', '--porcelain', '--untracked-files=no'), '')

    def test_a_push_that_lost_the_race_is_made_again_on_the_new_tip(self):
        run_a, run_b, _ = self.clones
        cistatus.publish(self.record(run_a, c_Commit, 1, 'success'), cwd=run_a, **c_Identity)
        stale = cistatus.fetch_branch('origin', 'ci-results', run_b)
        git(run_b, 'update-ref', 'refs/stale', stale)
        cistatus.publish(self.record(run_a, 'b' * 40, 1, 'success'), cwd=run_a, **c_Identity)
        real = cistatus.fetch_branch
        calls = []

        def first_stale(remote, branch, cwd=None):
            calls.append(remote)
            return 'refs/stale' if len(calls) == 1 else real(remote, branch, cwd)
        cistatus.fetch_branch = first_stale
        try:
            cistatus.publish(self.record(run_b, 'd' * 40, 1, 'failure'), cwd=run_b, **c_Identity)
        finally:
            cistatus.fetch_branch = real
        self.assertEqual(len(calls), 2)
        files = git(run_b, 'ls-tree', '--name-only', 'refs/remotes/origin/ci-results', 'runs/').split()
        self.assertEqual(len(files), 3, files)

    def test_a_short_hash_is_resolved_in_the_clone(self):
        author = self.clones[2]
        tree = git(author, 'write-tree')
        commit = git(author, 'commit-tree', tree, '-m', 'first')
        self.assertEqual(cistatus.resolve_commit(commit[:8], author), commit)
        with self.assertRaisesRegex(cistatus.CIStatusError, 'does not name a commit'):
            cistatus.resolve_commit('0000000', author)


if __name__ == '__main__':
    unittest.main()
