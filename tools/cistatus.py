#!/usr/bin/env python3
"""CI's result, read through git (plan/site.md, "CI"; plan/critique/rulings-5.md, R16, and rulings-6.md, R25).

    python tools/cistatus.py <commit> [--remote origin]     fetch the branch ci-results and print CI's result for the
                                                             commit (a hash, short or full, or a branch)

The last job of .github/workflows/book.yml, report, commits one file per run attempt to the branch ci-results:
runs/<commit>-<attempt>.json, with every job's conclusion, its failed steps and every ::error annotation. This tool
fetches that branch with git and prints the newest attempt of the commit. It needs no token and no API: the git
credential is used for git and for nothing else, and the same works for a private repository as for a public one.

The other commands are CI's own; they run on GitHub's runners:

    python tools/cistatus.py step --title <title> -- <command> ...
        runs a step's command, passes its output through, and when it fails writes the reason as an ::error
        annotation (the command, its exit code and the last lines it printed), which the report job collects: a job's
        log needs a token to read, its annotations reach ci-results
    python tools/cistatus.py record --jobs <jobs.json> --annotations <folder> --commit <sha> --attempt <n>
            [--run-url <url>] [--event <event>] [--ref <ref>] --out <file>
        writes the run's record from GitHub's answers (the jobs of the run attempt, and <folder>/<job id>.json with
        each job's annotations), leaving out the report job itself
    python tools/cistatus.py publish --file <record> [--remote origin] [--name <name> --email <address>]
        commits the record to ci-results (creating the branch when it does not exist) and pushes it, fetching again
        and retrying when another run pushed first; it never forces a push

Exit codes of reading: 0 when every job succeeded or was skipped, 1 when one failed or was cancelled, 3 while no run
of the commit is recorded yet (CI still runs, or did not start), 2 on errors. step exits with its command's code;
record and publish with 0, or 2 on errors. Only the standard library is used.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

c_Branch = 'ci-results'
c_Folder = 'runs'
# GitHub keeps 4,096 bytes of an annotation's message; the reason ends with the last lines the command printed.
c_MaxMessageBytes = 3900
c_TailLines = 40
c_MaxCommandCharacters = 300
c_Passed = ('success', 'skipped', 'neutral')
c_ReportJob = 'report'


class CIStatusError(Exception):
    pass


def git(arguments, cwd=None, input=None, env=None, check=True):
    result = subprocess.run(['git'] + arguments, cwd=cwd, input=input, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if check and result.returncode != 0:
        raise CIStatusError('git %s failed: %s' % (' '.join(arguments), (result.stderr or result.stdout).strip()))
    return result


# ---------------------------------------------------------------------------------------------------------------------
# Annotations (the step command)


def escape_data(text):
    """A workflow command's message: GitHub reads %, CR and LF as escapes."""
    return text.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')


def escape_property(text):
    return escape_data(text).replace(':', '%3A').replace(',', '%2C')


def error_annotation(title, command, code, tail):
    """The ::error line of a failed step: the command, its exit code and the last lines it printed, within GitHub's
    size of a message."""
    lines = list(tail)
    shown = ' '.join(command)
    if len(shown) > c_MaxCommandCharacters:
        shown = shown[:c_MaxCommandCharacters] + ' …'
    head = '%s exited %d' % (shown, code)
    while True:
        message = head + (':\n' + '\n'.join(lines) if lines else '')
        if len(message.encode('utf-8')) <= c_MaxMessageBytes or not lines:
            break
        lines.pop(0)
    if len(message.encode('utf-8')) > c_MaxMessageBytes:
        message = message.encode('utf-8')[:c_MaxMessageBytes].decode('utf-8', 'ignore')
    return '::error title=%s::%s' % (escape_property(title), escape_data(message))


def run_step(title, command, out=None):
    """Runs `command`, writing its output (standard error merged into it) through; returns its exit code, after
    writing an ::error annotation when it is not 0."""
    out = out or sys.stdout
    tail = collections.deque(maxlen=c_TailLines)
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', bufsize=1)
    except OSError as error:
        out.write(error_annotation(title, command, 127, ['the command did not start: %s' % error]) + '\n')
        out.flush()
        return 127
    with process.stdout:
        for line in process.stdout:
            out.write(line)
            out.flush()
            tail.append(line.rstrip('\r\n'))
    code = process.wait()
    if code != 0:
        out.write(error_annotation(title, command, code, tail) + '\n')
        out.flush()
    return code


# ---------------------------------------------------------------------------------------------------------------------
# The record (the record and publish commands)


def record_name(commit, attempt):
    return '%s/%s-%d.json' % (c_Folder, commit, attempt)


def build_record(jobs, annotations, commit, attempt, run_url=None, event=None, ref=None):
    """The record of one run attempt: `jobs` is GitHub's answer for the attempt's jobs ({"jobs": [...]}),
    `annotations` maps a job's id to its annotations (GitHub's answer for its check run). The report job, which writes
    the record while it runs, is left out."""
    if not re.match(r'^[0-9a-f]{40}$', commit or ''):
        raise CIStatusError('the commit must be its full 40-digit hash, not %r' % commit)
    entries = []
    for job in sorted(jobs.get('jobs', []), key=lambda item: item.get('name', '')):
        if job.get('name') == c_ReportJob:
            continue
        errors = []
        for annotation in annotations.get(job.get('id'), []):
            if annotation.get('annotation_level') != 'failure':
                continue
            errors.append({'title': annotation.get('title') or '', 'message': annotation.get('message') or '',
                           'path': annotation.get('path') or '', 'line': annotation.get('start_line')})
        failed = [step.get('name') for step in job.get('steps', []) if step.get('conclusion') not in (None,) + c_Passed]
        entries.append({'name': job.get('name'), 'conclusion': job.get('conclusion') or job.get('status'), 'failedSteps': failed, 'errors': errors})
    passed = all(entry['conclusion'] in c_Passed for entry in entries)
    return {'commit': commit, 'attempt': attempt, 'run': {'url': run_url, 'event': event, 'ref': ref},
            'conclusion': 'success' if passed else 'failure', 'jobs': entries}


def read_annotations(folder):
    """{job id: annotations} from <folder>/<job id>.json, as the report job saves GitHub's answers."""
    found = {}
    if not folder or not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        match = re.match(r'^(\d+)\.json$', name)
        if match:
            with open(os.path.join(folder, name), encoding='utf-8') as file:
                found[int(match.group(1))] = json.load(file)
    return found


def fetch_branch(remote, branch, cwd=None):
    """Fetches the branch into refs/remotes/<remote>/<branch>; returns that ref, or None when the remote has no such
    branch yet."""
    local = 'refs/remotes/%s/%s' % (remote, branch)
    result = git(['fetch', '--quiet', '--no-tags', remote, '+refs/heads/%s:%s' % (branch, local)], cwd=cwd, check=False)
    if result.returncode != 0:
        listed = git(['ls-remote', '--heads', remote, branch], cwd=cwd, check=False)
        if listed.returncode == 0 and not listed.stdout.strip():
            return None
        raise CIStatusError('git fetch %s %s failed: %s' % (remote, branch, (result.stderr or result.stdout).strip()))
    return local


def publish(path, remote='origin', branch=c_Branch, cwd=None, name=None, email=None, tries=5):
    """Commits the record at `path` to the branch, beside the records already there, and pushes it. The commit is
    made with git's plumbing on a private index, so the working tree and the checked-out branch are untouched. When
    another run pushed first, the branch is fetched again and the commit made again on its new tip."""
    with open(path, encoding='utf-8') as file:
        record = json.load(file)
    target = record_name(record['commit'], record['attempt'])
    identity = []
    if name:
        identity += ['-c', 'user.name=%s' % name]
    if email:
        identity += ['-c', 'user.email=%s' % email]
    blob = git(['hash-object', '-w', path], cwd=cwd).stdout.strip()
    handle, index = tempfile.mkstemp(prefix='cistatus-index-')
    os.close(handle)
    os.remove(index)
    try:
        env = dict(os.environ, GIT_INDEX_FILE=index)
        for attempt in range(1, tries + 1):
            parent = fetch_branch(remote, branch, cwd)
            if os.path.exists(index):
                os.remove(index)
            if parent:
                git(['read-tree', parent], cwd=cwd, env=env)
            git(['update-index', '--add', '--cacheinfo', '100644,%s,%s' % (blob, target)], cwd=cwd, env=env)
            tree = git(['write-tree'], cwd=cwd, env=env).stdout.strip()
            message = 'Record CI of %s, attempt %d: %s' % (record['commit'][:12], record['attempt'], record['conclusion'])
            commit = git(identity + ['commit-tree', tree] + (['-p', parent] if parent else []) + ['-m', message], cwd=cwd).stdout.strip()
            pushed = git(['push', '--quiet', remote, '%s:refs/heads/%s' % (commit, branch)], cwd=cwd, check=False)
            if pushed.returncode == 0:
                return commit
            if attempt == tries:
                raise CIStatusError('the record was not pushed after %d tries: %s' % (tries, (pushed.stderr or pushed.stdout).strip()))
    finally:
        if os.path.exists(index):
            os.remove(index)


# ---------------------------------------------------------------------------------------------------------------------
# Reading


def resolve_commit(revision, cwd=None):
    """The full hash of a revision of the local clone; a full hash is taken as it is (its commit may not be fetched)."""
    if re.match(r'^[0-9a-f]{40}$', revision):
        return revision
    # Brace-free (rulings 5, R17): MSYS2's git expands "{…}" in arguments native programs pass.
    result = git(['rev-parse', '--verify', '--quiet', revision + '~0'], cwd=cwd, check=False)
    sha = result.stdout.strip()
    if result.returncode != 0 or not re.match(r'^[0-9a-f]{40}$', sha):
        raise CIStatusError('%r does not name a commit of this clone (fetch it first, or give the full hash)' % revision)
    return sha


def latest_record(ref, commit, cwd=None):
    """The newest attempt's record of `commit` on the fetched branch, or None."""
    listed = git(['ls-tree', '--name-only', ref, c_Folder + '/'], cwd=cwd).stdout.split()
    attempts = []
    for path in listed:
        match = re.match(r'^%s/%s-(\d+)\.json$' % (c_Folder, commit), path)
        if match:
            attempts.append((int(match.group(1)), path))
    if not attempts:
        return None
    text = git(['show', '%s:%s' % (ref, max(attempts)[1])], cwd=cwd).stdout
    try:
        return json.loads(text)
    except ValueError as error:
        raise CIStatusError('%s on %s is not valid JSON: %s' % (max(attempts)[1], ref, error))


def describe(record):
    """The lines that print a record."""
    run = record.get('run') or {}
    lines = ['commit %s, attempt %d%s: %s' % (record['commit'], record['attempt'], ' (%s)' % run['url'] if run.get('url') else '', record['conclusion'])]
    for job in record['jobs']:
        lines.append('  %s: %s' % (job['name'], job['conclusion']))
        for step in job.get('failedSteps', []):
            lines.append('    step "%s" failed' % step)
        for error in job.get('errors', []):
            where = '%s:%s ' % (error['path'], error['line']) if error.get('path') and error['path'] != '.github' else ''
            lines.append('    error: %s%s' % (where, error['title'] or ''))
            lines.extend('      ' + line for line in (error.get('message') or '').splitlines())
    return lines


def read_main(argv):
    parser = argparse.ArgumentParser(prog='cistatus.py', description='Prints CI\'s result for a commit from the branch ci-results.')
    parser.add_argument('commit', help='the commit: a hash, short or full, or a branch')
    parser.add_argument('--remote', default='origin', help='the remote that holds ci-results (default origin)')
    parser.add_argument('--branch', default=c_Branch, help=argparse.SUPPRESS)
    parser.add_argument('--repository', help='the clone to run git in (default this repository)')
    options = parser.parse_args(argv)
    cwd = options.repository or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        commit = resolve_commit(options.commit, cwd)
        ref = fetch_branch(options.remote, options.branch, cwd)
        record = latest_record(ref, commit, cwd) if ref else None
    except CIStatusError as error:
        print('cistatus: %s' % error, file=sys.stderr)
        return 2
    if record is None:
        print('cistatus: no run of %s is recorded on %s yet: CI still runs, did not start, or was not pushed' % (commit, options.branch))
        return 3
    for line in describe(record):
        print(line)
    return 0 if record['conclusion'] == 'success' else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ('step', 'record', 'publish'):
        return read_main(argv)
    parser = argparse.ArgumentParser(prog='cistatus.py', description='CI\'s side: annotate failed steps, write and publish the record.')
    commands = parser.add_subparsers(dest='command', required=True)
    step = commands.add_parser('step', help='run a step\'s command and annotate its failure')
    step.add_argument('--title', required=True, help='the annotation\'s title: what the step checks')
    step.add_argument('arguments', nargs=argparse.REMAINDER, help='-- <command> ...')
    record = commands.add_parser('record', help='write the run\'s record from GitHub\'s answers')
    record.add_argument('--jobs', required=True)
    record.add_argument('--annotations', required=True)
    record.add_argument('--commit', required=True)
    record.add_argument('--attempt', type=int, required=True)
    record.add_argument('--run-url')
    record.add_argument('--event')
    record.add_argument('--ref')
    record.add_argument('--out', required=True)
    published = commands.add_parser('publish', help='commit the record to ci-results and push it')
    published.add_argument('--file', required=True)
    published.add_argument('--remote', default='origin')
    published.add_argument('--branch', default=c_Branch, help=argparse.SUPPRESS)
    published.add_argument('--name', help='the committer\'s name (default git\'s)')
    published.add_argument('--email', help='the committer\'s address (default git\'s)')
    published.add_argument('--tries', type=int, default=5)
    options = parser.parse_args(argv)
    try:
        if options.command == 'step':
            command = options.arguments[1:] if options.arguments[:1] == ['--'] else options.arguments
            if not command:
                parser.error('step needs a command after --')
            return run_step(options.title, command)
        if options.command == 'record':
            with open(options.jobs, encoding='utf-8') as file:
                jobs = json.load(file)
            result = build_record(jobs, read_annotations(options.annotations), options.commit, options.attempt, options.run_url, options.event, options.ref)
            os.makedirs(os.path.dirname(os.path.abspath(options.out)), exist_ok=True)
            with open(options.out, 'w', encoding='utf-8', newline='\n') as file:
                json.dump(result, file, indent=1, sort_keys=True)
                file.write('\n')
            print('\n'.join(describe(result)))
            return 0
        commit = publish(options.file, options.remote, options.branch, name=options.name, email=options.email, tries=options.tries)
        print('cistatus: recorded as %s on %s' % (commit, options.branch))
        return 0
    except (CIStatusError, OSError, ValueError, KeyError) as error:
        print('cistatus: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
