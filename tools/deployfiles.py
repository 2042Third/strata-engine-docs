#!/usr/bin/env python3
"""Writes the files of deploy/ for another base path than site.json's:

    python tools/deployfiles.py --base=/docs/strata --out deploy-docs-strata
    python tools/deployfiles.py --base=/ --out deploy-root          the book at the root of its host

Every "/strata-engine-docs" that is the prefix in the nginx files, the Dockerfiles and the copy script becomes the
base, and deploy/Dockerfile copies the site from the release's top folder for that base ("docs/strata/", or "site/"
for the root of a host). For the root of a host, the blocks marked "(redirect: begin)" to "(redirect: end)" (the
redirect of the prefix without its slash) and "(outside: begin)" to "(outside: end)" (the answer for everything outside
the prefix) are dropped. README.md is not written: it describes the committed files. The two files the release step
generates from a built site (nginx-csp.conf, nginx-redirects.conf) are tools/release.py's: assemble --base writes
the whole deploy folder of a release for its base, these two included. Build the site with the same DOCS_BASE. In Git
Bash or MSYS2 on Windows write the base with "=" (--base=/docs/strata), so that the shell leaves it alone
(.tools/env.sh).

Only the standard library is used. Exit codes: 0 written, 2 usage errors.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import crawl  # noqa: E402
from booklib import deploy  # noqa: E402

c_Deploy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'deploy')


def written_files(folder=c_Deploy):
    """The files of deploy/ this tool writes for another base: every committed file but README.md."""
    return [name for name in deploy.deploy_files(folder) if name != 'README.md']


def main(argv=None):
    parser = argparse.ArgumentParser(description='Writes deploy/\'s files for another base path.')
    parser.add_argument('--base', required=True, help='the base path the site was built for; "/" for the root of the host')
    parser.add_argument('--out', required=True, help='the folder to write (created; existing files are replaced)')
    options = parser.parse_args(argv)
    try:
        base = crawl.normalize_base(options.base)
        if os.path.abspath(options.out) == os.path.abspath(c_Deploy):
            raise ValueError('--out must not be deploy/ itself: its files are written for site.json\'s base')
        os.makedirs(options.out, exist_ok=True)
        names = written_files()
        for name in names:
            with open(os.path.join(c_Deploy, name), encoding='utf-8') as file:
                text = deploy.for_base(file.read(), base, name)
            with open(os.path.join(options.out, name), 'w', encoding='utf-8', newline='\n') as file:
                file.write(text)
            if name == 'deploy-files.sh':
                os.chmod(os.path.join(options.out, name), 0o755)
    except (OSError, ValueError) as error:
        print('deployfiles: %s' % error, file=sys.stderr)
        return 2
    print('deployfiles: wrote %s for the base %s into %s' % (', '.join(names), base or '/', options.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
