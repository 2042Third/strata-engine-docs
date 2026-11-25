// The book's content collection. Starlight's schema is extended with the book's front matter (plan/style.md §6.1,
// plan/site.md "Front matter and the teaching checks"): this schema checks each key's shape. The keys are optional here
// because pages of different roles carry different keys: the landing and 404 pages only `title` and `description`, a
// part's index and review pages `id`, `title`, `description`, `tracks`, `status` and `generated`. The strips plugin
// (src/plugins/strips.mjs, src/lib/frontmatter.mjs) requires the keys of each role and checks what one file's shape
// cannot: the id against the file's path, the Needs and the page against the outline, the tracks against the sidebar.

import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';
import { previewOmitted } from './lib/settings.mjs';

const pageId = z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*$/, 'lowercase segments of a-z, 0-9 and single hyphens, joined by "/"');
const need = z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*(\|[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*)*$/, 'a page id, or alternatives "a|b"');
const release = z.string().regex(/^\d+\.\d+\.\d+$/, 'a release as a string, such as 0.3.0');
const objective = z.strictObject({
	id: z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, 'lowercase words joined by hyphens'),
	text: z.string().min(1),
});

const book = z.object({
	description: z.string().max(160).optional(),
	id: pageId.optional(),
	kind: z.enum(['primer', 'concept', 'internals', 'tutorial', 'how-to', 'reference']).optional(),
	size: z.enum(['S', 'M', 'L', 'XL']).optional(),
	tracks: z.array(z.enum(['G', 'B', 'E'])).max(3).optional(),
	needs: z.array(need).max(5).optional(),
	time: z.number().int().positive().optional(),
	learn: z.array(objective).min(2).max(5)
		.refine((items) => new Set(items.map((item) => item.id)).size === items.length, 'the learn ids of a page are unique')
		.optional(),
	since: release.optional(),
	status: z.enum(['draft', 'reviewed', 'final']).optional(),
	generated: z.enum(['index', 'review']).optional(),
});

// A preview may leave pages out (DOCS_PREVIEW_OMIT, PREVIEW.md): Starlight's own loader with those files excluded, so
// that they are never rendered.
function docsOrPreviewLoader() {
	const omitted = [...previewOmitted()];
	if (omitted.length === 0) return docsLoader();
	const pattern = ['**/[^_]*.md', ...omitted.map((id) => `!${id}.md`)];
	return { name: 'starlight-docs-loader', load: (context) => glob({ base: './src/content/docs', pattern }).load(context) };
}

export const collections = {
	docs: defineCollection({ loader: docsOrPreviewLoader(), schema: docsSchema({ extend: book }) }),
	// The interface's own words (Starlight's English strings, overridden in src/content/i18n/en.json).
	i18n: defineCollection({ loader: i18nLoader(), schema: i18nSchema() }),
};
