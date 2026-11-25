// The build's settings: where the site is served (site.json at the repository's root, which DOCS_BASE and DOCS_SITE
// override for one build), whether this is a release build (DOCS_RELEASE), where the content lives and which engine
// commit the book is checked against (engine.pin). Every other module of the build reads them from here, so that
// building for another place changes only site.json or the environment, never the content. The tools read site.json
// through tools/booklib/settings.py; both apply the rules of tools/tests/fixtures/settings-cases.json (rulings 6, R24).

import { readFileSync } from 'node:fs';
import path from 'node:path';

export const c_SiteFile = 'site.json';

/**
 * Normalizes a base path to "/a/b" (no trailing slash), or "" for the root of the host, which is written "/". An empty
 * or blank value is refused rather than read as the root: an empty CI variable or "--build-arg DOCS_BASE=" would
 * otherwise move every URL out of the prefix without a word. `source` names where the value came from.
 */
export function normalizeBase(value, source = 'DOCS_BASE') {
	const trimmed = String(value ?? '').trim();
	if (trimmed === '') throw new Error(`${source} is empty: write / for the root of the host`);
	if (trimmed === '/') return '';
	if (!trimmed.startsWith('/')) throw new Error(`${source} must start with "/": ${JSON.stringify(value)}`);
	if (trimmed.startsWith('//')) throw new Error(`${source} must be a path, not a host: ${JSON.stringify(value)}`);
	if (!/^[A-Za-z0-9/._~-]+$/.test(trimmed)) throw new Error(`${source} may hold only letters, digits and / . _ ~ -: ${JSON.stringify(value)}`);
	const base = trimmed.replace(/\/$/, '');
	const segments = base.split('/').slice(1);
	if (segments.some((segment) => segment === '')) throw new Error(`${source} has an empty segment ("//"): ${JSON.stringify(value)}`);
	if (segments.some((segment) => segment === '.' || segment === '..')) throw new Error(`${source} must not contain . or .. segments: ${JSON.stringify(value)}`);
	return base;
}

/** Normalizes the site's origin to "https://host[:port]": http or https, no path, query, fragment, user or password. */
export function normalizeSite(value, source = 'DOCS_SITE') {
	let url;
	try {
		url = new URL(String(value ?? ''));
	} catch {
		throw new Error(`${source} must be an absolute URL such as https://books.example.org: ${JSON.stringify(value)}`);
	}
	if (url.protocol !== 'https:' && url.protocol !== 'http:') throw new Error(`${source} must use http or https: ${JSON.stringify(value)}`);
	if (url.pathname !== '/' || url.search || url.hash || /[?#]/.test(String(value))) throw new Error(`${source} is the origin only; put the path in the base: ${JSON.stringify(value)}`);
	if (url.username || url.password) throw new Error(`${source} holds no user name or password: ${JSON.stringify(value)}`);
	return url.origin;
}

/**
 * site.json's values: `{ base, origin, copyright: { holder, year } }`, the base and the origin normalized. The file is
 * the one place that names where the book is served (rulings 6, R24); its absence is an error, never a default.
 */
export function readSite(root) {
	const file = path.join(root, c_SiteFile);
	let data;
	try {
		data = JSON.parse(readFileSync(file, 'utf8'));
	} catch (error) {
		if (error.code === 'ENOENT') throw new Error(`${c_SiteFile} does not exist: it holds the base, the origin and the copyright line (rulings 6, R24)`);
		throw new Error(`${c_SiteFile} cannot be read: ${error.message}`);
	}
	if (data === null || typeof data !== 'object' || Array.isArray(data)) throw new Error(`${c_SiteFile} holds an object with base, origin and copyright`);
	const unknown = Object.keys(data).filter((key) => !['base', 'origin', 'copyright'].includes(key)).sort();
	if (unknown.length) throw new Error(`${c_SiteFile}: unknown keys ${unknown.join(', ')}: the keys are base, origin and copyright`);
	const copyright = data.copyright;
	if (copyright === null || typeof copyright !== 'object' || typeof copyright.holder !== 'string' || !copyright.holder.trim() || !Number.isInteger(copyright.year)) {
		throw new Error(`${c_SiteFile}: copyright is {"holder": "<name>", "year": <year>}`);
	}
	return {
		base: normalizeBase(data.base, `${c_SiteFile}'s base`),
		origin: normalizeSite(data.origin, `${c_SiteFile}'s origin`),
		copyright: { holder: copyright.holder, year: copyright.year },
	};
}

/**
 * The copyright line built from site.json's copyright: the first line of LICENSE and the line of every page's footer
 * (rulings 6, R20). tools/crawl.py builds the same line.
 */
export function copyrightLine(copyright) {
	return `Copyright © ${copyright.year} ${copyright.holder}. All rights reserved.`;
}

/** The files every page's footer links, at the base: LICENSE as the build writes it, and the notices (rulings 6, R22). */
export const c_FooterFiles = [
	{ label: 'License', file: 'license.txt' },
	{ label: 'Third-party notices', file: 'third-party-notices.txt' },
];

/** The problem of LICENSE's text, or null: it exists and its first line is the copyright line of site.json. */
export function licenseProblem(text, copyright) {
	if (text === null) return 'LICENSE does not exist: the build serves it as <base>/license.txt (rulings 6, R20)';
	const first = text.split(/\r?\n/, 1)[0];
	const line = copyrightLine(copyright);
	return first === line ? null : `LICENSE's first line is "${first}", not "${line}", which site.json's copyright makes`;
}

/** Reads engine.pin: "key value" lines, "#" comments. */
export function parsePin(text) {
	const values = {};
	for (const raw of text.split(/\r?\n/)) {
		const line = raw.trim();
		if (!line || line.startsWith('#')) continue;
		const space = line.search(/\s/);
		if (space < 0) throw new Error(`engine.pin: "${line}" has no value`);
		values[line.slice(0, space)] = line.slice(space).trim();
	}
	if (!/^[0-9a-f]{40}$/.test(values.commit ?? '')) throw new Error('engine.pin: "commit" must be a full 40-digit commit id');
	if (!/^\d+\.\d+\.\d+$/.test(values.release ?? '')) throw new Error('engine.pin: "release" must look like 0.8.0');
	if (!/^https:\/\/github\.com\/[^/]+\/[^/]+$/.test(values.repository ?? '')) throw new Error('engine.pin: "repository" must be https://github.com/<owner>/<name>');
	if (values.prerelease !== undefined && values.prerelease !== 'yes' && values.prerelease !== 'no') throw new Error('engine.pin: "prerelease" is yes or no');
	return { commit: values.commit, release: values.release, prerelease: values.prerelease === 'yes', repository: values.repository };
}

/**
 * A URL in the engine's repository at the pin (site.md, "Code fences"; rulings-6, R25): every link into the engine, the
 * pin on the top strip and every quote's header, is built here from engine.pin's `repository` and `commit` lines. With
 * no file it is the tree at the commit; with a file, that file at the commit, and its lines from `start` to `end`.
 */
export function engineUrl(engine, file = null, start = null, end = start) {
	if (!file) return `${engine.repository}/tree/${engine.commit}`;
	const lines = start === null ? '' : start === end ? `#L${start}` : `#L${start}-L${end}`;
	return `${engine.repository}/blob/${engine.commit}/${file}${lines}`;
}

/**
 * Why a release build cannot use this origin, or null (rulings 6, R24): a release is served over https from the real
 * place of the book, so plain http, this machine's names and the placeholder that tests pass are refused (an origin with
 * a path never gets here: normalizeSite refuses it). A tagged build is a release for site.json's origin.
 */
export function releaseSiteProblem(site) {
	const url = new URL(site);
	if (url.protocol !== 'https:') return `the origin is ${site}: a release is served over https`;
	if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') return `the origin is ${site}: a release is not served from this machine`;
	if (url.hostname === 'example.com') return `the origin is ${site}, the placeholder that tests use: a release names the real origin (site.json)`;
	if (url.pathname !== '/') return `the origin ${site} carries a path: put it in the base`;
	return null;
}

/** All settings of one build. `root` is the project folder (the one holding astro.config.mjs). */
/**
 * The pages a preview leaves out (DOCS_PREVIEW_OMIT: page ids separated by commas), for a page that breaks a rule of
 * the build which the preview cannot soften (PREVIEW.md). Only a preview (DOCS_PREVIEW=1) may leave pages out.
 */
export function previewOmitted(env = process.env) {
	const ids = (env.DOCS_PREVIEW_OMIT ?? '').split(',').map((id) => id.trim()).filter(Boolean);
	if (ids.length && env.DOCS_PREVIEW !== '1') throw new Error('DOCS_PREVIEW_OMIT leaves pages out of a preview: set DOCS_PREVIEW=1 with it');
	return new Set(ids);
}

export function readSettings({ root, env = process.env, command = 'build' }) {
	for (const name of ['DOCS_ROOT', 'DOCS_ARCHIVED']) {
		if (env[name] !== undefined) throw new Error(`${name} is reserved for archived versions of the book and is not implemented before the second release: leave it unset`);
	}
	const site = readSite(root);
	const base = env.DOCS_BASE === undefined ? site.base : normalizeBase(env.DOCS_BASE);
	const origin = env.DOCS_SITE === undefined ? site.origin : normalizeSite(env.DOCS_SITE);
	const release = env.DOCS_RELEASE === '1';
	// A preview of a partly written book (PREVIEW.md): a link to a row of the outline not written yet is drawn as
	// plain text instead of failing the build. Only a draft build may be a preview.
	const preview = env.DOCS_PREVIEW === '1';
	if (preview && release) throw new Error('DOCS_PREVIEW draws links to unwritten pages as text: a release build leaves it unset');
	if (release) {
		const problem = releaseSiteProblem(origin);
		if (problem) throw new Error(problem);
		if (env.DOCS_EXTRA_REDIRECTS !== undefined) throw new Error('DOCS_EXTRA_REDIRECTS adds test entries to the moved pages: a release build leaves it unset');
	}
	const content = path.join(root, 'src', 'content');
	return {
		root,
		command,
		base,
		site: origin,
		// site.json's own values: the deploy files are written for its base, and the copyright line names its holder.
		siteFile: site,
		release,
		preview,
		previewOmit: previewOmitted(env),
		redirectsFile: path.join(root, 'src', 'redirects.json'),
		// A file of test entries added to the moved pages for one build (the CI build at /x/y, while src/redirects.json
		// has no entry of its own: plan/site.md, "Moved pages"), relative to the project folder.
		extraRedirectsFile: env.DOCS_EXTRA_REDIRECTS ? path.resolve(root, env.DOCS_EXTRA_REDIRECTS) : null,
		docsDir: path.join(content, 'docs'),
		figuresDir: path.join(content, 'figures'),
		glossaryFile: path.join(content, 'glossary.json'),
		sidebarFile: path.join(root, 'src', 'sidebar.json'),
		outlineFile: path.join(root, 'src', 'generated', 'outline.json'),
		picturesDir: path.join(root, 'src', 'assets', 'figures'),
		diagramsDir: path.join(root, 'src', 'generated', 'diagrams'),
		sketchesDir: path.join(root, 'sketches'),
		referenceDir: path.join(root, 'src', 'generated', 'reference'),
		valuesFile: path.join(root, 'src', 'generated', 'reference', 'values.json'),
		vendorFile: path.join(root, 'src', 'generated', 'vendor.json'),
		cacheDir: path.join(root, '.cache'),
		engine: parsePin(readFileSync(path.join(root, 'engine.pin'), 'utf8')),
	};
}

/** The URL of a page from its route id: "<base>/<id>/", "<base>/" for the landing page (id "index"). */
export function pageUrl(base, id) {
	return id === 'index' ? `${base}/` : `${base}/${id}/`;
}

/**
 * The URL of a page of the site relative to the page `from` is on: both are paths of the site that end with "/"
 * ("/b/core/time/", "/b/core/map/" gives "../map/"; "/b/" from "/b/" gives "./"). The sidebar links its 395 pages so,
 * on every page (rulings-13, R59); a URL that is not such a path (a fragment, a query, a file) is returned as it is.
 */
export function relativeUrl(from, to) {
	if (!/^\/([^?#]*\/)?$/.test(from) || !/^\/([^?#]*\/)?$/.test(to)) return to;
	const source = from.split('/').filter(Boolean);
	const target = to.split('/').filter(Boolean);
	let common = 0;
	while (common < source.length && common < target.length && source[common] === target[common]) common++;
	return '../'.repeat(source.length - common) + target.slice(common).map((segment) => `${segment}/`).join('') || './';
}

/** The URL of a file or folder of the site: `path` starts with "/" ("/print/core/", "/favicon.svg"). */
export function withBase(base, filePath) {
	if (!filePath.startsWith('/')) throw new Error(`withBase: "${filePath}" must start with "/"`);
	return `${base}${filePath}`;
}
