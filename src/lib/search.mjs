// What a page tells search about itself (plan/site.md, "Search"). Pagefind indexes the built site through Starlight's
// integration with no configuration, so everything is an attribute in the HTML, which src/components/PageTitle.astro
// writes from this: the result's title with the page's part and kind beside it (Starlight's search shows the title, so
// no Search override is needed), the kind and the part as metadata of their own, and the filters by part, kind and
// track.

import { c_KindLabels, trackByLetter } from './labels.mjs';
import { partOf } from './outline.mjs';

// A part's index and review pages have no kind (they carry `generated`): search names them so.
export const c_PartPageLabels = { index: 'Part overview', review: 'Part review' };

/**
 * How search ranks its results (Pagefind's ranking weights), given to Starlight's search (astro.config.mjs) and to the
 * search test (scripts/search-quality.mjs), so that the test ranks as the readers' search does. These are Starlight's
 * own defaults (its schemas/pagefind), written out so that the test can read them.
 */
export const c_SearchRanking = Object.freeze({ pageLength: 0.1, termFrequency: 0.1, termSaturation: 2, termSimilarity: 9, diacriticSimilarity: 0.8 });

/**
 * How many word positions a chunk of Pagefind's index holds (its PAGEFIND_UNSTABLE_INDEX_CHUNK_SIZE, which the book's
 * integration sets for the build; Pagefind's own is 20,000). A query downloads the chunk of each of its words: at
 * 20,000 the chunks of the released book are about 40 KB each, and two of them take most of the next query's budget
 * (budget row 12); at 2,000 they are about 5 KB, and the first query's chunk list (pf_meta) grows by about 10 KB.
 */
export const c_SearchIndexChunkSize = 2000;

/** The environment Pagefind's index is built with: the chunk size above. */
export function searchIndexEnvironment() {
	return { PAGEFIND_UNSTABLE_INDEX_CHUNK_SIZE: String(c_SearchIndexChunkSize) };
}

// The separator of the parts of a result's title.
const c_TitleSeparator = ' · ';

/**
 * The search facts of a page from its front matter and the outline's data: `{ title, part, kind, tracks }`, where
 * `title` is "<title> · <part> · <kind>" and `tracks` the names of the page's tracks (one filter value each). Null for
 * pages outside the book's parts (the landing page and the 404 page), which keep search's own title.
 */
export function searchFacts({ data, outline }) {
	if (typeof data?.id !== 'string' || typeof data.title !== 'string') return null;
	const part = partOf(outline, data.id);
	if (!part) return null;
	const kind = data.generated !== undefined ? c_PartPageLabels[data.generated] : c_KindLabels[data.kind];
	if (!kind) return null;
	const tracks = (Array.isArray(data.tracks) ? data.tracks : []).map(trackByLetter).filter(Boolean).map((track) => track.name);
	return { title: [data.title, part.title, kind].join(c_TitleSeparator), part: part.title, kind, tracks };
}

/**
 * The attribute of the element that gives a result its title. Pagefind reads "key:value" to the end of the attribute,
 * commas included, when it is the attribute's only (or last) entry, so a title with commas or colons stays whole.
 */
export function titleMeta(facts) {
	return `title:${facts.title}`;
}
