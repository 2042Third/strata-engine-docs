// Moved pages (plan/site.md, "Moved pages"). After the first release a page whose id disappears gets an entry in
// src/redirects.json, `{ "redirects": [{ "from": "<old id>", "to": "<new id>" }] }`. The build writes a fallback page
// at <base>/<old id>/index.html, which sends the reader on to the new page (for a server without the rules), and
// tools/release.py writes the server's rules, nginx-redirects.conf, from those fallback pages: an exact location for
// the old address, with and without its slash, that answers 301 with the new page's path. Astro's own redirects are
// never used: whether Astro adds the base to their targets is not documented.
//
// Ids are page ids as the outline writes them ("core/time"); a part's index page is "core/index", served as "core/".

import { existsSync, readFileSync } from 'node:fs';
import { c_FooterFiles, copyrightLine, pageUrl, withBase } from './settings.mjs';
import { reservedSegmentProblem, routeIdOf } from './sidebar.mjs';

// The meta element the fallback pages carry, which tools/release.py and tools/crawl.py read (tools/booklib/deploy.py).
export const c_MovedMeta = 'strata-book-moved';

function escapeHtml(value) {
	return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * The entries of a redirects file: `{ entries, problems }`. A missing file has no entries; a file of another shape is
 * a problem, named with the file.
 */
export function loadRedirects(file, label = file) {
	if (!existsSync(file)) return { entries: [], problems: [] };
	let data;
	try {
		data = JSON.parse(readFileSync(file, 'utf8'));
	} catch (error) {
		return { entries: [], problems: [`${label}: not valid JSON (${error.message})`] };
	}
	const shape = `${label} holds { "redirects": [{ "from": "<old id>", "to": "<new id>" }] } (and an optional "description")`;
	if (data === null || typeof data !== 'object' || Array.isArray(data) || !Array.isArray(data.redirects) || Object.keys(data).some((key) => key !== 'redirects' && key !== 'description')) {
		return { entries: [], problems: [shape] };
	}
	const entries = [];
	const problems = [];
	data.redirects.forEach((entry, index) => {
		const keys = entry !== null && typeof entry === 'object' && !Array.isArray(entry) ? Object.keys(entry).sort() : [];
		if (keys.join(',') !== 'from,to' || typeof entry.from !== 'string' || typeof entry.to !== 'string') problems.push(`${label}: entry ${index + 1} is not { "from": "<old id>", "to": "<new id>" }`);
		else entries.push({ from: entry.from, to: entry.to, label: `${label}, entry ${index + 1}` });
	});
	return { entries, problems };
}

/**
 * Problems of the redirect entries against the book's pages (a Map of page ids): a `from` that is a current page (its
 * fallback page would replace it) or not a page id, a `to` that is not a current page, an entry whose target is
 * another `from` (a chain: point it at the final page), and an old id named twice.
 */
export function redirectProblems(entries, pages) {
	const problems = [];
	const oldIds = new Map();
	for (const entry of entries) {
		const where = `${entry.label} ("${entry.from}" to "${entry.to}")`;
		if (!/^[a-z0-9-]+(\/[a-z0-9-]+)*$/.test(entry.from)) problems.push(`${where}: the old id is not a page id (segments of a-z, 0-9 and -)`);
		else {
			const reserved = reservedSegmentProblem(entry.from);
			if (reserved) problems.push(`${where}: ${reserved}`);
		}
		if (entry.from === 'index' || entry.from === '404') problems.push(`${where}: the landing page and the 404 page never move`);
		if (pages.has(entry.from)) problems.push(`${where}: "${entry.from}" is a page of the book, so it has not moved`);
		if (!pages.has(entry.to)) problems.push(`${where}: "${entry.to}" is not a page of the book`);
		if (oldIds.has(entry.from)) problems.push(`${where}: "${entry.from}" is moved twice (${oldIds.get(entry.from)})`);
		oldIds.set(entry.from, entry.label);
	}
	for (const entry of entries) {
		if (oldIds.has(entry.to)) problems.push(`${entry.label} ("${entry.from}" to "${entry.to}"): "${entry.to}" has moved itself: point the entry at the page it moved to`);
	}
	return problems;
}

/** Where a fallback page is written, relative to the built site: "<old route>/index.html". */
export function fallbackFile(entry) {
	return `${routeIdOf(entry.from)}/index.html`;
}

/**
 * The fallback page of one moved page: a refresh to the new page, the new page as its canonical address, noindex, and
 * a plain link for a reader whose browser does not follow the refresh, and the footer's copyright line with its links
 * (rulings 6, R20). It runs no script, so the Content Security Policy has nothing to allow for it.
 */
export function fallbackPage({ base, site, entry, title, copyright }) {
	const path = pageUrl(base, routeIdOf(entry.to));
	const name = escapeHtml(title);
	return [
		'<!doctype html>',
		'<html lang="en">',
		'<head>',
		'<meta charset="utf-8">',
		'<meta name="viewport" content="width=device-width, initial-scale=1">',
		`<title>Moved: ${name}</title>`,
		'<meta name="robots" content="noindex">',
		`<meta name="${c_MovedMeta}" content="${escapeHtml(path)}">`,
		`<link rel="canonical" href="${escapeHtml(site + path)}">`,
		`<meta http-equiv="refresh" content="0; url=${escapeHtml(path)}">`,
		'</head>',
		'<body>',
		`<p>This page has moved: <a href="${escapeHtml(path)}">${name}</a>.</p>`,
		`<footer><p>${escapeHtml(copyrightLine(copyright))} ${c_FooterFiles.map(({ label, file }) => `<a href="${escapeHtml(withBase(base, `/${file}`))}">${label}</a>`).join(' ')}</p></footer>`,
		'</body>',
		'</html>',
		'',
	].join('\n');
}
