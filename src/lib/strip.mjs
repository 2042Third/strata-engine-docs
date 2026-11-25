// The top strip of a page, as data: what src/components/PageTitle.astro draws above the text (plan/style.md §6.2,
// plan/site.md "Navigation"). Everything comes from the page's front matter, the outline's data (the level, the
// part's first page and its Needs) and engine.pin; every URL is built from the base by src/lib/settings.mjs, so the
// strip works under any base.

import { c_KindLabels, c_LevelTexts, trackByLetter } from './labels.mjs';
import { firstRowOf, needAlternatives, partOf } from './outline.mjs';
import { engineUrl, pageUrl, withBase } from './settings.mjs';

const c_BookTitle = 'The Strata Engine Book';

/** A page named in the strip: a link when it is written, its title from the outline otherwise. */
function pageRef(id, outline, pages, base) {
	const written = pages.get(id);
	if (written) return { id, title: written.title, href: pageUrl(base, written.route), written: true };
	return { id, title: outline.rows.get(id)?.title ?? id, href: null, written: false };
}

/** Needs as the strip lists them: each Need with its alternatives ("X or Y"). */
function needRefs(needs, outline, pages, base) {
	return needs.map((need) => ({ need, alternatives: needAlternatives(need).map((id) => pageRef(id, outline, pages, base)) }));
}

/** Where the part's name in the breadcrumbs leads: its index page, or else its first written page. */
function partHref(part, outline, pages, base) {
	const index = pages.get(`${part.slug}/index`);
	if (index) return pageUrl(base, index.route);
	const first = part.pages.find((id) => pages.has(id));
	return first ? pageUrl(base, pages.get(first).route) : null;
}

/**
 * The strip of one page. `data` is its front matter (with `id`); `pages` maps the book id of every written page to
 * `{ title, route }`; `pin` is engine.pin read by parsePin. Returns null for pages without a strip (the landing page and
 * the 404 page carry no `id`).
 */
export function topStrip({ data, outline, pages, base, pin }) {
	if (typeof data?.id !== 'string') return null;
	const part = partOf(outline, data.id);
	if (!part) return null;
	const row = outline.rows.get(data.id) ?? null;
	const partPage = data.generated !== undefined;
	const tracks = (Array.isArray(data.tracks) ? data.tracks : []).map(trackByLetter).filter(Boolean);
	const strip = {
		breadcrumbs: [
			{ label: c_BookTitle, href: pageUrl(base, 'index') },
			{ label: part.title, href: partHref(part, outline, pages, base) },
			{ label: data.title, href: null },
		],
		kind: !partPage && c_KindLabels[data.kind] ? { word: data.kind, label: c_KindLabels[data.kind] } : null,
		tracks: tracks.map((track) => ({ letter: track.letter, key: track.key, name: track.name })),
		level: !partPage && row ? { number: row.level, text: c_LevelTexts[row.level] } : null,
		minutes: !partPage && Number.isInteger(data.time) ? data.time : null,
		newIn: !partPage && data.since === pin.release ? pin.release : null,
		draft: data.status === 'draft',
		learn: !partPage && Array.isArray(data.learn) ? data.learn.map((item) => item.text) : [],
		needs: null,
		needsFirstPage: false,
		beforePart: null,
		engine: {
			release: pin.release,
			prerelease: pin.prerelease,
			commit: pin.commit,
			short: pin.commit.slice(0, 8),
			href: engineUrl(pin),
		},
		print: { href: withBase(base, `/print/${part.slug}/`), label: part.title },
	};
	if (partPage) return strip;
	const needs = Array.isArray(data.needs) ? data.needs : [];
	const first = firstRowOf(part);
	if (needs.length > 0) strip.needs = needRefs(needs, outline, pages, base);
	else if (first && first !== data.id) {
		// A page whose row has "-" needs the first page of its part (style.md §1.2 and §6.2).
		strip.needs = needRefs([first], outline, pages, base);
		strip.needsFirstPage = true;
	} else strip.needs = [];
	// The first page of a part without an index page shows what the index page would: the part's Needs (style.md §7.7).
	if (!part.partPages && first === data.id && part.needs.length > 0) strip.beforePart = needRefs(part.needs, outline, pages, base);
	return strip;
}
