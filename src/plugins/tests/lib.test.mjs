// The build library: settings, engine.pin, the web manifest, the page index and the front matter reader. The outline,
// the sidebar, the tracks and the top strip are tested in src/plugins/tests/sidebar.test.mjs.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { webManifest } from '../../lib/manifest.mjs';
import { collectAnchors, pageIdOf } from '../../lib/pages.mjs';
import { parseMarkdown } from '../../lib/markdown.mjs';
import { c_FooterFiles, copyrightLine, engineUrl, licenseProblem, normalizeBase, normalizeSite, pageUrl, parsePin, readSettings, readSite, relativeUrl, releaseSiteProblem, withBase } from '../../lib/settings.mjs';
import { c_Pin, makeBook } from './helpers.mjs';

const c_Root = fileURLToPath(new URL('../../../', import.meta.url));

test('the site links nowhere in the book\'s repository: no edit link, no social links', () => {
	// The book's repository is not public. Starlight draws an edit link on every page when its editLink is set, and
	// header links when social is: astro.config.mjs sets neither, and the interface words name no edit link.
	const config = readFileSync(path.join(c_Root, 'astro.config.mjs'), 'utf8').replace(/^\s*\/\/.*$/gm, '');
	assert.doesNotMatch(config, /\beditLink\b|\bsocial\b/);
	const words = JSON.parse(readFileSync(path.join(c_Root, 'src', 'content', 'i18n', 'en.json'), 'utf8'));
	assert.equal(Object.keys(words).some((key) => key.startsWith('page.editLink')), false);
});

test('the base path is one setting with a strict form', () => {
	assert.equal(normalizeBase('/strata-engine-docs'), '/strata-engine-docs');
	assert.equal(normalizeBase('/strata-engine-docs/'), '/strata-engine-docs');
	assert.equal(normalizeBase('/'), '');
	// An empty value is a mistake (an empty CI variable), never the root: the root is written "/".
	assert.throws(() => normalizeBase(''), /DOCS_BASE is empty/);
	assert.throws(() => normalizeBase('  '), /DOCS_BASE is empty/);
	assert.throws(() => normalizeBase('/a//b'), /empty segment/);
	assert.throws(() => normalizeBase('/a/b//'), /empty segment/);
	assert.equal(readSettings({ root: c_Root, env: {} }).base, '/strata-engine-docs');
	assert.throws(() => readSettings({ root: c_Root, env: { DOCS_BASE: '' } }), /DOCS_BASE is empty/);
	assert.equal(readSettings({ root: c_Root, env: { DOCS_BASE: '/' } }).base, '');
	assert.equal(normalizeBase('/docs/v0.8'), '/docs/v0.8');
	assert.throws(() => normalizeBase('docs'), /must start with/);
	assert.throws(() => normalizeBase('//host/x'), /path, not a host/);
	assert.throws(() => normalizeBase('/a/../b'), /\.\. segments/);
	assert.throws(() => normalizeBase('/a b'), /may hold only/);
	assert.equal(normalizeSite('https://example.com/'), 'https://example.com');
	assert.throws(() => normalizeSite('https://example.com/docs'), /origin only/);
	assert.equal(pageUrl('/b', 'core/time'), '/b/core/time/');
	assert.equal(pageUrl('/b', 'index'), '/b/');
	assert.equal(pageUrl('', 'index'), '/');
	assert.equal(withBase('/b', '/print/core/'), '/b/print/core/');
	assert.equal(withBase('', '/print/core/'), '/print/core/');
	assert.throws(() => withBase('/b', 'print/core/'), /must start with/);
	// The sidebar's links, relative to the page they are on, at the three bases of budget row 17.
	assert.equal(relativeUrl('/b/core/time/', '/b/core/map/'), '../map/');
	assert.equal(relativeUrl('/b/core/time/', '/b/physics/bodies/'), '../../physics/bodies/');
	assert.equal(relativeUrl('/b/core/time/', '/b/core/time/'), './');
	assert.equal(relativeUrl('/b/core/', '/b/core/time/'), 'time/');
	assert.equal(relativeUrl('/b/', '/b/core/'), 'core/');
	assert.equal(relativeUrl('/', '/core/'), 'core/');
	assert.equal(relativeUrl('/x/y/print/core/', '/x/y/core/time/'), '../../core/time/');
	assert.equal(relativeUrl('/b/core/time/', '/b/core/map/#x'), '/b/core/map/#x');
	assert.equal(relativeUrl('/b/core/time/', 'https://example.com/'), 'https://example.com/');
});

test('a release build names a real https origin, and the archive settings are refused', () => {
	assert.match(releaseSiteProblem('https://example.com'), /placeholder/);
	assert.match(releaseSiteProblem('http://docs.example.org'), /https/);
	assert.match(releaseSiteProblem('https://localhost:8080'), /this machine/);
	assert.match(releaseSiteProblem('https://127.0.0.1'), /this machine/);
	assert.equal(releaseSiteProblem('https://docs.example.org'), null);
	// A tagged build is a release for the committed address: site.json's origin, with no DOCS_SITE.
	const site = JSON.parse(readFileSync(path.join(c_Root, 'site.json'), 'utf8'));
	const release = readSettings({ root: c_Root, env: { DOCS_RELEASE: '1' } });
	assert.equal(release.release, true);
	assert.equal(release.site, normalizeSite(site.origin));
	assert.throws(() => readSettings({ root: c_Root, env: { DOCS_RELEASE: '1', DOCS_SITE: 'https://example.com' } }), /placeholder/);
	assert.equal(readSettings({ root: c_Root, env: { DOCS_RELEASE: '1', DOCS_SITE: 'https://docs.example.org' } }).site, 'https://docs.example.org');
	// A draft build may name any origin for one build: a test server, a preview.
	assert.equal(readSettings({ root: c_Root, env: { DOCS_SITE: 'http://127.0.0.1:8080' } }).site, 'http://127.0.0.1:8080');
	for (const name of ['DOCS_ROOT', 'DOCS_ARCHIVED']) {
		assert.throws(() => readSettings({ root: c_Root, env: { [name]: '/docs' } }), new RegExp(`${name} is reserved for archived versions`));
		assert.throws(() => readSettings({ root: c_Root, env: { [name]: '' } }), /not implemented before the second release/);
	}
});

test('the build reads site.json with the same rules as the tools, on their shared cases', () => {
	// tools/tests/fixtures/settings-cases.json: what tools/booklib/settings.py passes, the build passes (rulings 6, R24).
	const cases = JSON.parse(readFileSync(path.join(c_Root, 'tools', 'tests', 'fixtures', 'settings-cases.json'), 'utf8'));
	for (const entry of cases.base) {
		if (entry.error) assert.throws(() => normalizeBase(entry.value), Error, JSON.stringify(entry.value));
		else assert.equal(normalizeBase(entry.value), entry.base, JSON.stringify(entry.value));
	}
	for (const entry of cases.origin) {
		if (entry.error) assert.throws(() => normalizeSite(entry.value), Error, JSON.stringify(entry.value));
		else assert.equal(normalizeSite(entry.value), entry.origin, JSON.stringify(entry.value));
	}
	for (const entry of cases.release) assert.equal(releaseSiteProblem(normalizeSite(entry.origin)) !== null, entry.refused, entry.origin);
});

test('site.json holds the base, the origin and the copyright, and nothing else', () => {
	const site = readSite(c_Root);
	assert.equal(site.base, '/strata-engine-docs');
	assert.equal(typeof site.copyright.holder, 'string');
	assert.ok(Number.isInteger(site.copyright.year));
	const folder = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'site-json-'));
	try {
		const write = (data) => writeFileSync(path.join(folder, 'site.json'), typeof data === 'string' ? data : JSON.stringify(data));
		assert.throws(() => readSite(folder), /site\.json does not exist/);
		const good = { base: '/b/', origin: 'https://Books.Example.org/', copyright: { holder: 'Someone', year: 2026 } };
		write(good);
		assert.deepEqual(readSite(folder), { base: '/b', origin: 'https://books.example.org', copyright: { holder: 'Someone', year: 2026 } });
		write('{');
		assert.throws(() => readSite(folder), /cannot be read/);
		write({ ...good, extra: 1 });
		assert.throws(() => readSite(folder), /unknown keys extra/);
		write({ ...good, base: '' });
		assert.throws(() => readSite(folder), /site\.json's base is empty/);
		write({ ...good, origin: 'https://books.example.org/docs' });
		assert.throws(() => readSite(folder), /site\.json's origin is the origin only/);
		write({ ...good, copyright: { holder: '', year: 2026 } });
		assert.throws(() => readSite(folder), /copyright is/);
		write({ ...good, copyright: { holder: 'Someone', year: '2026' } });
		assert.throws(() => readSite(folder), /copyright is/);
	} finally {
		rmSync(folder, { recursive: true, force: true });
	}
	// A build without DOCS_BASE and DOCS_SITE is for site.json's place, whatever it names.
	const book = makeBook({});
	try {
		writeFileSync(path.join(book.root, 'site.json'), JSON.stringify({ base: '/other/place', origin: 'https://books.example.org', copyright: { holder: 'Someone', year: 2026 } }));
		const settings = readSettings({ root: book.root, env: {} });
		assert.equal(settings.base, '/other/place');
		assert.equal(settings.site, 'https://books.example.org');
		assert.deepEqual(settings.siteFile.copyright, { holder: 'Someone', year: 2026 });
		assert.equal(readSettings({ root: book.root, env: { DOCS_BASE: '/x/y', DOCS_SITE: 'https://example.com' } }).base, '/x/y');
	} finally {
		book.remove();
	}
});

test('the book is closed source: LICENSE starts with site.json\'s copyright line, and package.json is private and UNLICENSED', () => {
	const { copyright } = readSite(c_Root);
	assert.equal(copyrightLine({ holder: '2042Third', year: 2026 }), 'Copyright © 2026 2042Third. All rights reserved.');
	assert.equal(licenseProblem(readFileSync(path.join(c_Root, 'LICENSE'), 'utf8'), copyright), null);
	assert.match(licenseProblem(null, copyright), /LICENSE does not exist/);
	assert.match(licenseProblem('Copyright © 2025 Someone. All rights reserved.\r\n', copyright), /first line is "Copyright © 2025 Someone\. All rights reserved\.", not "Copyright © 2026/);
	assert.equal(licenseProblem(`${copyrightLine(copyright)}\r\nMore.\r\n`, copyright), null);
	const pkg = JSON.parse(readFileSync(path.join(c_Root, 'package.json'), 'utf8'));
	assert.equal(pkg.private, true);
	assert.equal(pkg.license, 'UNLICENSED');
	assert.deepEqual(c_FooterFiles.map((entry) => entry.file), ['license.txt', 'third-party-notices.txt']);
});

test('the web manifest\'s start URL, scope and icon are under the base', () => {
	for (const [base, prefix] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
		const manifest = webManifest(normalizeBase(base));
		assert.equal(manifest.start_url, `${prefix}/`);
		assert.equal(manifest.scope, `${prefix}/`);
		assert.deepEqual(manifest.icons.map((icon) => icon.src), [`${prefix}/favicon.svg`]);
		if (prefix !== '/strata-engine-docs') assert.doesNotMatch(JSON.stringify(manifest), /strata-engine-docs/);
	}
});

test('engine.pin is read with its checks', () => {
	assert.deepEqual(parsePin(`# comment\n${c_Pin}`), { commit: '822a7a46dbcdd86e8e2eafde7e41d003e27260c8', release: '0.8.0', prerelease: true, repository: 'https://github.com/2042Third/GameEngine' });
	assert.throws(() => parsePin('commit 822a7a46\nrelease 0.8.0\nrepository https://github.com/a/b'), /full 40-digit/);
});

test('every link into the engine is built by one helper from engine.pin\'s repository and commit', () => {
	const pin = parsePin(c_Pin.replace('2042Third/GameEngine', 'someone/elsewhere'));
	const commit = '822a7a46dbcdd86e8e2eafde7e41d003e27260c8';
	assert.equal(engineUrl(pin), `https://github.com/someone/elsewhere/tree/${commit}`);
	assert.equal(engineUrl(pin, 'Strata/src/Strata/Scene/Scene.cpp', 2267, 2295), `https://github.com/someone/elsewhere/blob/${commit}/Strata/src/Strata/Scene/Scene.cpp#L2267-L2295`);
	assert.equal(engineUrl(pin, 'Strata/src/Strata/Scene/Scene.h', 439), `https://github.com/someone/elsewhere/blob/${commit}/Strata/src/Strata/Scene/Scene.h#L439`);
	assert.equal(engineUrl(pin, 'AGENTS.md'), `https://github.com/someone/elsewhere/blob/${commit}/AGENTS.md`);
	// No other module of the build spells a path into a repository: a vendored library's quote links its own
	// repository (src/generated/vendor.json), which is not the engine's.
	const spelled = [];
	const visit = (folder) => {
		for (const entry of readdirSync(folder, { withFileTypes: true })) {
			const file = path.join(folder, entry.name);
			if (entry.isDirectory()) {
				if (entry.name !== 'tests' && entry.name !== 'generated') visit(file);
				continue;
			}
			if (!/\.(mjs|js|ts|astro)$/.test(entry.name) || file === path.join(c_Root, 'src', 'lib', 'settings.mjs')) continue;
			readFileSync(file, 'utf8').split('\n').forEach((line, index) => {
				if (/\/(blob|tree)\//.test(line) && !line.includes('library.repository')) spelled.push(`${path.relative(c_Root, file)}:${index + 1}`);
			});
		}
	};
	visit(path.join(c_Root, 'src'));
	assert.deepEqual(spelled, []);
});

test('page ids are the files\' paths, and anchors are the slugs Astro gives headings', () => {
	assert.equal(pageIdOf('core/time.md'), 'core/time');
	// The part's index page is known by its file (rule O1); Starlight serves it at <base>/make/.
	assert.equal(pageIdOf('make/index.md'), 'make/index');
	assert.equal(pageIdOf('index.md'), 'index');
	const anchors = collectAnchors(parseMarkdown("## Strata's choice\n\n## The `Scene` class\n\n## Summary\n\n## Summary\n\n::figure{id=taa-off-on}\n"));
	assert.deepEqual([...anchors].sort(), ['_top', 'fig-taa-off-on', 'stratas-choice', 'summary', 'summary-1', 'the-scene-class']);
});

test('the inputs digest changes with the code-block settings, the configuration, the schema and the packages', async () => {
	// Astro keeps rendered pages while its configuration digest stays; ec.config.mjs is not part of that configuration.
	const { inputsDigest, createBookContext } = await import('../index.mjs');
	const { makeBook } = await import('./helpers.mjs');
	const { readFileSync, writeFileSync } = await import('node:fs');
	const path = (await import('node:path')).default;
	const book = makeBook({ pages: {} });
	try {
		const settings = readSettings({ root: book.root, env: {} });
		const digest = async () => inputsDigest(settings, await createBookContext(settings).index());
		const digests = [await digest()];
		for (const name of ['ec.config.mjs', 'astro.config.mjs', 'src/content.config.ts', 'package-lock.json']) {
			writeFileSync(path.join(book.root, ...name.split('/')), `// ${name}\n`);
			digests.push(await digest());
		}
		// Every page reads the outline's data (titles of Needs, levels): a change of it renders every page again.
		const outlineFile = path.join(book.root, 'src', 'generated', 'outline.json');
		const outline = JSON.parse(readFileSync(outlineFile, 'utf8'));
		outline.parts[3].title = 'Another title';
		writeFileSync(outlineFile, JSON.stringify(outline));
		digests.push(await digest());
		assert.equal(new Set(digests).size, digests.length, digests.join(' '));
		assert.equal(await digest(), digests[digests.length - 1]);
	} finally {
		book.remove();
	}
});

test('the inputs digest changes with the included tables, the tutorials\' files, patches and downloads, the vendored libraries and the pages\' questions, not with their places', async () => {
	// A reference page shows a generated table, a checkpoint the downloads that exist, a part's review page the other
	// pages' questions: a change of any of them renders every page again, and moving a question down a page does not.
	const { inputsDigest, createBookContext } = await import('../index.mjs');
	const { c_BottomStrip, frontmatter, makeBook } = await import('./helpers.mjs');
	const { mkdirSync, writeFileSync } = await import('node:fs');
	const path = (await import('node:path')).default;
	// The page as makeBook writes it, with its id first.
	const page = (before) => `${frontmatter()}\n${before}\n${c_BottomStrip}`.replace('---\n', '---\nid: core/time\n');
	const book = makeBook({ pages: { 'core/time': page('Text.') } });
	try {
		const settings = readSettings({ root: book.root, env: {}, command: 'dev' });
		const digest = async () => inputsDigest(settings, await createBookContext(settings).index());
		const write = (relative, text) => {
			const file = path.join(book.root, ...relative.split('/'));
			mkdirSync(path.dirname(file), { recursive: true });
			writeFileSync(file, text);
		};
		const first = await digest();
		write('src/content/docs/core/time.md', page('Text.\n\nMore text above the questions.'));
		assert.equal(await digest(), first);
		write('src/content/docs/core/time.md', page('Text.').replace('1. One?', '1. Another question?'));
		const asked = await digest();
		assert.notEqual(asked, first);
		write('src/generated/reference/commands.md', '## Commands\n');
		const included = await digest();
		assert.notEqual(included, asked);
		write('public/downloads/tutorials/make/spin/stage-1.zip', 'zip');
		const downloaded = await digest();
		assert.notEqual(downloaded, included);
		write('tutorials/make/spin.tutorial.json', '{}');
		const tutorial = await digest();
		assert.notEqual(tutorial, downloaded);
		// A hunk quote and a worked solution read a patch of tutorials/; a vendor quote reads the vendored libraries' record.
		write('tutorials/make/spin/exercise-1.patch', 'diff');
		const patched = await digest();
		assert.notEqual(patched, tutorial);
		write('src/generated/vendor.json', '{}');
		assert.notEqual(await digest(), patched);
	} finally {
		book.remove();
	}
});

test('the front matter reader agrees with tools/booklib/frontmatter.py on the shared cases', async () => {
	const { readFileSync } = await import('node:fs');
	const { splitFrontmatter } = await import('../../lib/markdown.mjs');
	const { cases } = JSON.parse(readFileSync(new URL('../../../tools/tests/fixtures/frontmatter.json', import.meta.url), 'utf8'));
	for (const { name, text, data, error } of cases) {
		if (error) {
			assert.throws(() => splitFrontmatter(text), undefined, name);
		} else {
			assert.deepEqual(splitFrontmatter(text).data, data, name);
		}
	}
});
