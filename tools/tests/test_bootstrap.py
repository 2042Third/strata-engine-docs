"""tools/bootstrap.py and tools/toolchain.json: the checkers (typos, lychee 0.24.2 for gate (a), actionlint for CI's
workflows) on the PATH, and with --servers nginx in the two versions the deploy files are tested with, 1.20.1 and
1.30.6; each archive pinned by its SHA-256, and no Caddy (plan/critique/rulings-6.md, R23)."""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
import bootstrap

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ToolchainTests(unittest.TestCase):
    def test_nginx_is_pinned_in_both_tested_versions_and_caddy_is_gone(self):
        with open(os.path.join(c_Root, 'tools', 'toolchain.json'), encoding='utf-8') as file:
            toolchain = json.load(file)
        self.assertNotIn('caddy', toolchain)
        self.assertEqual(sorted(toolchain['nginx']['versions']), ['1.20.1', '1.30.6'])
        for version, entry in toolchain['nginx']['versions'].items():
            archive = entry['archives']['windows-x64']
            self.assertEqual(archive['file'], 'nginx-%s.zip' % version)
            self.assertRegex(archive['sha256'], r'^[0-9a-f]{64}$')
        with open(os.path.join(c_Root, 'tools', 'bootstrap.py'), encoding='utf-8') as file:
            self.assertNotRegex(file.read(), r'(?i)caddy')


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tools = tempfile.mkdtemp(prefix='bootstrap-test-')

    def tearDown(self):
        shutil.rmtree(self.tools, ignore_errors=True)

    def test_the_checkers_are_pinned_for_both_platforms(self):
        with open(os.path.join(c_Root, 'tools', 'toolchain.json'), encoding='utf-8') as file:
            toolchain = json.load(file)
        self.assertEqual(bootstrap.c_Checkers, ('typos', 'lychee', 'actionlint'))
        # plan/site.md, "Framework and versions": lychee 0.24.2, with Windows and Linux archives.
        self.assertEqual(toolchain['lychee']['version'], '0.24.2')
        for name in bootstrap.c_Checkers:
            self.assertEqual(sorted(toolchain[name]['archives']), ['linux-x64', 'windows-x64'], name)
            self.assertIn(toolchain[name]['version'], toolchain[name]['base_url'], name)
            for archive in toolchain[name]['archives'].values():
                self.assertRegex(archive['sha256'], r'^[0-9a-f]{64}$')

    def archive(self, name, inner):
        """A zip in the downloads folder holding the program at `inner`; returns its SHA-256."""
        path = os.path.join(self.tools, 'downloads', '%s.zip' % name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with zipfile.ZipFile(path, 'w') as bundle:
            bundle.writestr(inner, 'program %s' % name)
        with open(path, 'rb') as file:
            return hashlib.sha256(file.read()).hexdigest()

    def test_each_checker_is_unpacked_and_its_program_s_folder_goes_on_the_path(self):
        # lychee's zip keeps the program in a folder of its own; typos' and actionlint's at the top.
        inner = {'typos': 'typos.exe', 'lychee': 'lychee-x86_64-pc-windows-msvc/lychee.exe', 'actionlint': 'actionlint.exe'}
        toolchain = {'node': {'archives': {'windows-x64': {'file': 'node-v1-win-x64.zip'}}}}
        for name in bootstrap.c_Checkers:
            toolchain[name] = {'version': '1.0', 'base_url': 'https://downloads.invalid/',
                               'archives': {'windows-x64': {'file': '%s.zip' % name, 'sha256': self.archive(name, inner[name])}}}
        programs = bootstrap.install_checkers(self.tools, toolchain, 'windows-x64')
        self.assertEqual(sorted(programs), sorted(bootstrap.c_Checkers))
        for name, program in programs.items():
            self.assertEqual(program, os.path.join(self.tools, '%s-1.0' % name, *inner[name].split('/')))
        paths = bootstrap.environment(self.tools, toolchain, 'windows-x64')['paths']
        self.assertEqual(paths[1:], [os.path.dirname(programs[name]) for name in bootstrap.c_Checkers])
        # A toolchain file that pins fewer checkers puts only those on the PATH.
        del toolchain['lychee']
        paths = bootstrap.environment(self.tools, toolchain, 'windows-x64')['paths']
        self.assertEqual(paths[1:], [os.path.dirname(programs[name]) for name in ('typos', 'actionlint')])


class InstallNginxTests(unittest.TestCase):
    def setUp(self):
        self.tools = tempfile.mkdtemp(prefix='bootstrap-test-')

    def tearDown(self):
        shutil.rmtree(self.tools, ignore_errors=True)

    def archive(self, version):
        """A zip shaped like nginx.org's (nginx-<version>/nginx.exe) in the downloads folder; returns its SHA-256."""
        path = os.path.join(self.tools, 'downloads', 'nginx-%s.zip' % version)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with zipfile.ZipFile(path, 'w') as bundle:
            bundle.writestr('nginx-%s/nginx.exe' % version, 'program %s' % version)
            bundle.writestr('nginx-%s/conf/mime.types' % version, 'types {}')
        with open(path, 'rb') as file:
            return hashlib.sha256(file.read()).hexdigest()

    def toolchain(self, sums):
        return {'nginx': {'base_url': 'https://downloads.invalid/', 'versions': {
            version: {'archives': {'windows-x64': {'file': 'nginx-%s.zip' % version, 'sha256': digest}}} for version, digest in sums.items()}}}

    def test_every_pinned_version_is_unpacked_from_its_checked_archive(self):
        toolchain = self.toolchain({'1.30.6': self.archive('1.30.6'), '1.20.1': self.archive('1.20.1')})
        programs = bootstrap.install_nginx(self.tools, toolchain, 'windows-x64')
        self.assertEqual(list(programs), ['1.20.1', '1.30.6'])
        for version, program in programs.items():
            self.assertEqual(program, os.path.join(self.tools, 'nginx-%s' % version, 'nginx-%s' % version, 'nginx.exe'))
            with open(program, encoding='utf-8') as file:
                self.assertEqual(file.read(), 'program %s' % version)
        # A machine without pinned archives (Linux) gets none: its nginx comes from its packages or CI's images.
        self.assertEqual(bootstrap.install_nginx(self.tools, toolchain, 'linux-x64'), {})

    def test_an_archive_whose_sum_differs_is_refused(self):
        self.archive('1.20.1')
        toolchain = self.toolchain({'1.20.1': '0' * 64})
        # The download would be tried again: an address that cannot answer makes it fail without the network.
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.install_nginx(self.tools, toolchain, 'windows-x64')
        self.assertFalse(os.path.exists(os.path.join(self.tools, 'nginx-1.20.1', 'nginx-1.20.1', 'nginx.exe')))
        with self.assertRaisesRegex(bootstrap.BootstrapError, 'pins no nginx 9.9.9'):
            bootstrap.install_tool(self.tools, toolchain, 'windows-x64', 'nginx', 'nginx', '9.9.9')


if __name__ == '__main__':
    unittest.main()
