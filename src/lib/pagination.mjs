// "Previous" and "next" of every track that holds a page, as data for src/components/Pagination.astro: the book's
// script shows the set of the reader's track in place of Starlight's links, which follow the sidebar. Every URL is
// built from the base by src/lib/settings.mjs.

import { c_ChooserPage } from './labels.mjs';
import { pageUrl } from './settings.mjs';
import { trackNeighbours } from './sidebar.mjs';

/** The written pages of the book from Astro's docs collection: book id (the front matter's `id`) → `{ title, route }`. */
export function writtenPages(entries) {
	const pages = new Map();
	for (const entry of entries) {
		if (typeof entry.data?.id === 'string') pages.set(entry.data.id, { title: entry.data.title, route: entry.id });
	}
	return pages;
}

/**
 * The track links of one page: `{ tracks: [{ key, letter, label, prev, next, sideStep }], chooser }`, where `prev` and
 * `next` are `{ href, title }` or null and `chooser` is the link to the page where readers choose a track (null while
 * that page is not written).
 */
export function trackLinks({ sidebar, pages, id, base }) {
	const link = (other) => (other ? { href: pageUrl(base, pages.get(other).route), title: pages.get(other).title } : null);
	const tracks = trackNeighbours(sidebar, pages, id).map((track) => ({ ...track, prev: link(track.prev), next: link(track.next) }));
	const chooserPage = pages.get(c_ChooserPage);
	return { tracks, chooser: chooserPage ? { href: pageUrl(base, chooserPage.route), title: chooserPage.title } : null };
}
