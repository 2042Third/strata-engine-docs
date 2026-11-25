// Test helpers: a small book in a temporary folder, and the book's Markdown pipeline run on one of its pages the way
// the build runs it (without Starlight and Expressive Code, which the tests do not need).
//
// A test book has the book's 25 parts, an outline's data (src/generated/outline.json) and a sidebar. By default both
// are made from the pages the test writes: every page is a row of the outline whose title, kind, size, tracks and
// Needs are its front matter's, and every track lists the pages that name it, in the order the test gives them. A test
// changes them with `outline` (a function that edits the data) and `sidebar` (one that edits the sidebar).

import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkSmartypants from 'remark-smartypants';
import remarkDirective from 'remark-directive';
import remarkRehype from 'remark-rehype';
import { toHtml } from 'hast-util-to-html';
import { VFile } from 'vfile';
import { c_ThemeNames, diagramHash, drawingFile, idPrefix } from '../../lib/diagrams.mjs';
import { splitFrontmatter } from '../../lib/markdown.mjs';
import { copyrightLine, readSettings } from '../../lib/settings.mjs';
import { bookMarkdown, createBookContext } from '../index.mjs';

export const c_Pin = 'commit 822a7a46dbcdd86e8e2eafde7e41d003e27260c8\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n';

// The book's parts (plan/book.md, "Parts"), as the outline's headings name them.
export const c_Parts = [['start', 'Start here'], ['make', 'Making games'], ['basics', 'Foundations'], ['core', 'Engine architecture'],
	['world', 'Scenes and the ECS'], ['gpu', "The GPU and the renderer's core"], ['assets', 'Assets'], ['draw', 'Drawing a scene'],
	['light', 'Light and materials'], ['image', 'The image'], ['indirect', 'Indirect light'], ['physics', 'Physics'],
	['animation', 'Animation'], ['audio', 'Audio'], ['input', 'Input'], ['scripting', 'Scripting'], ['ui', 'Game UI'],
	['worlds', 'Large worlds and shipping'], ['editor', "The editor's core"], ['editor-ui', "The editor's interface"],
	['automation', 'Automation and AI agents'], ['engineering', 'Building, testing and releasing the engine'],
	['capstone', 'Capstone: one feature through every layer'], ['reference', 'Reference'], ['appendix', 'Appendices']];

// A release build names a real origin (src/lib/settings.mjs); tests of release builds use this one.
export const c_ReleaseSite = 'https://book.example.org';

// The site.json of a test book: the repository's base, and the placeholder origin tests use (rulings 6, R24), which a
// release build refuses.
export const c_SiteJson = { base: '/strata-engine-docs', origin: 'https://example.com', copyright: { holder: 'Test Holder', year: 2026 } };
// A test book's LICENSE: its first line is the one c_SiteJson's copyright makes, as the build asks.
export const c_License = `${copyrightLine(c_SiteJson.copyright)}\n\nA book written for a test.\n`;

const c_DefaultLearn = '\n  - id: one-thing\n    text: explain one thing\n  - id: another-thing\n    text: explain another thing';

/**
 * A page's front matter with every key a concept page of parts 3 to 21 carries (`id` is added by makeBook). A key
 * given as undefined is left out; `kind: 'reference'` leaves out `time`, `learn` and `since` unless they are given.
 */
export function frontmatter(overrides = {}) {
	const reference = overrides.kind === 'reference';
	const data = {
		title: '"A page"',
		description: '"A page of the test book."',
		kind: 'concept',
		size: 'M',
		tracks: '[E]',
		needs: '[]',
		time: reference ? undefined : 20,
		learn: reference ? undefined : c_DefaultLearn,
		since: reference ? undefined : '0.3.0',
		status: 'draft',
		...overrides,
	};
	return `---\n${Object.entries(data).filter(([, value]) => value !== undefined).map(([key, value]) => `${key}: ${value}`).join('\n')}\n---\n`;
}

// The bottom strip of the concept, internals, tutorial and how-to pages of the tests, for the default objectives.
const c_StripSections = `
## Summary

- One line.
- Another line.

## Check yourself

1. One?

   :::answer{tests="one-thing"}
   Yes.
   :::

2. Two?

   :::answer{tests="another-thing"}
   Yes.
   :::

3. Three?

   :::answer{tests="one-thing another-thing"}
   Yes.
   :::

## Exercises

1. Do it.

   :::answer{tests="one-thing"}
   Done.
   :::

## Where it lives in Strata

- \`Strata/src/Strata/Scene/Scene.cpp\`

## Further reading

- A book.
`;

// A worked example (style.md §8: primers, concept and internals pages hold one before the bottom strip).
export const c_Example = '\n:::example\nA worked example: the problem, every step, the result.\n:::\n';

// The sections each kind's body ends with (style.md §6.3), with the exact headings style.md §7 gives the kind: an
// internals page's general section, alternatives and tests before "Changing it safely", a how-to's result before its
// variations. A tutorial's body ends with its last step section, which ends with its checkpoint and the checkpoint's
// picture (style.md §7.4; checkpointPictureFiles gives the page its recipe); its first sections are c_TutorialOpening,
// which a test page puts at its top.
const c_BodyEnds = {
	concept: `\n## Common mistakes\n\n- One thing to know.\n${c_Example}`,
	internals: `\n## The problem and how engines solve it\n\nTwo approaches.\n${c_Example}\n## Alternatives Strata did not choose\n\n- One.\n\n## How it is tested\n\n- A test.\n\n## Changing it safely\n\n- One thing to know.\n`,
	tutorial: '\n## Make the cube spin\n\n- One thing to know.\n\n::checkpoint{stage=1}\n\n::figure{id=now}\n',
	'how-to': '\n## Result\n\nIt works.\n\n## Variations\n\n- One thing to know.\n',
};

/**
 * The files that give a test tutorial `pageId` the recipe of its checkpoints' picture, ::figure{id=now}: a drawing (an
 * SVG file), which a release build accepts without the engine.
 */
export function checkpointPictureFiles(pageId) {
	const recipe = { id: 'now', kind: 'diagram', shows: 'The project at the checkpoint', size: [40, 20], caption: 'The project as it is now.', alt: 'A cube on the ground.' };
	return {
		[`src/content/figures/${pageId}.json`]: JSON.stringify({ figures: [recipe] }),
		[`src/assets/figures/${pageId}/now.svg`]: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20"><rect width="40" height="20"/></svg>',
	};
}

/**
 * The committed drawings of a diagram, as `npm run diagrams` writes them into src/generated/diagrams/ (stamped), for a
 * test book's `files`: `{ hash, files }`. `svgs` may give each theme's SVG; by default a small one whose ids carry the
 * diagram's prefix, as the renderer's do.
 */
export function committedDiagram(source, svgs = {}) {
	const hash = diagramHash(source);
	const files = {};
	for (const theme of c_ThemeNames) {
		const prefix = idPrefix(hash, theme);
		const svg = svgs[theme] ?? `<svg id="${prefix}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20" aria-roledescription="flowchart-v2" role="graphics-document document"><style>#${prefix} text{fill:#333;}</style><marker id="${prefix}_arrow"></marker><text x="4" y="14">${theme}</text><line marker-end="url(#${prefix}_arrow)"></line></svg>`;
		files[`src/generated/diagrams/${hash}-${theme}.svg`] = drawingFile({ hash, theme, svg });
	}
	return { hash, files };
}

/** The first sections of a test tutorial (style.md §7.4). */
export const c_TutorialOpening = '## What you will make\n\nA cube that spins.\n\n## What you need\n\n- The editor.\n';

/**
 * The end of a test page of `kind` (concept, internals, tutorial or how-to) that satisfies the strips plugin for the
 * default objectives: the sections its body ends with, then its bottom strip.
 */
export function bottomStrip(kind = 'concept') {
	if (!c_BodyEnds[kind]) throw new Error(`bottomStrip: no test strip for the kind "${kind}"`);
	return `${c_BodyEnds[kind]}${c_StripSections}`;
}

/** A Test out box (style.md §7.1) whose five answers test the default objectives. */
export const c_TestOut = `::::test-out\n${[1, 2, 3, 4, 5].map((n) => `${n}. Question ${n}?\n\n   :::answer{tests="${n % 2 ? 'one-thing' : 'another-thing'}"}\n   Yes.\n   :::\n`).join('\n')}::::\n`;

/**
 * The body of a test primer for the default objectives: its Test out box, "Why you will need this", a worked example,
 * "Common mistakes" and its bottom strip, whose "Where the book uses it" holds `uses` (the list of pages that use it).
 */
export function primerBody(uses) {
	const strip = c_StripSections.replace('## Exercises', '## Practice').replace('## Where it lives in Strata', '## Where the book uses it')
		.replace('1. Do it.\n\n   :::answer{tests="one-thing"}\n   Done.\n   :::', [1, 2, 3].map((n) => `${n}. Do ${n}.\n\n   :::answer{tests="one-thing"}\n   Done.\n   :::`).join('\n\n'))
		.replace('- `Strata/src/Strata/Scene/Scene.cpp`\n', uses);
	return `${c_TestOut}\n## Why you will need this\n\nThree pages use it.\n${c_Example}\n## Common mistakes\n\n- One mistake.\n${strip}`;
}

/** The end of a concept page: "## Common mistakes" and the bottom strip. */
export const c_BottomStrip = bottomStrip('concept');

/** Adds `id: <page id>` to a page's front matter unless it names an id (the landing and 404 pages carry none). */
function withId(id, text) {
	const newline = text.startsWith('---\r\n') ? '\r\n' : '\n';
	if (id === 'index' || id === '404' || !text.startsWith(`---${newline}`)) return text;
	const start = 3 + newline.length;
	const block = text.slice(start, text.indexOf(`${newline}---`, start - newline.length));
	if (/^id:/m.test(block)) return text;
	return `---${newline}id: ${id}${newline}${text.slice(start)}`;
}

/** The bottom strip of a reference page. */
export const c_ReferenceStrip = '\n## Where it lives in Strata\n\n- `src/content/glossary.json`\n';

function readData(text) {
	try {
		return splitFrontmatter(text).data ?? {};
	} catch {
		return {};
	}
}

/** The outline's data of a test book whose pages (id → Markdown) are rows. */
export function testOutline(pages) {
	return testOutlineOf(Object.fromEntries(Object.entries(pages).map(([id, text]) => [id, readData(text)])));
}

/**
 * The outline's data of a test book from its pages' front matter (id → data): its parts, a row for every page that is
 * not a part page, and the tracks.
 */
export function testOutlineOf(pages) {
	const rows = [];
	for (const [id, data] of Object.entries(pages)) {
		if (id === 'index' || id === '404') continue;
		if (data.generated !== undefined) continue;
		rows.push({
			id,
			title: typeof data.title === 'string' ? data.title : id,
			kind: data.kind ?? 'concept',
			size: data.size ?? 'M',
			tracks: Array.isArray(data.tracks) ? data.tracks.filter((letter) => ['G', 'B', 'E'].includes(letter)) : [],
			needs: Array.isArray(data.needs) ? data.needs : [],
			part: id.split('/')[0],
			level: 1,
			row: `plan/outline-test.md:${rows.length + 1}`,
		});
	}
	const parts = c_Parts.map(([slug, title], number) => {
		const own = rows.filter((row) => row.part === slug);
		return {
			number,
			slug,
			title,
			tracks: ['G', 'B', 'E'].filter((letter) => own.some((row) => row.tracks.includes(letter))),
			needs: [],
			pages: own.map((row) => row.id),
			partPages: false,
		};
	});
	const tracks = {};
	for (const letter of ['G', 'B', 'E']) tracks[letter] = rows.filter((row) => row.tracks.includes(letter)).map((row) => ({ id: row.id }));
	return { generated: 'test', parts, pages: rows, tracks };
}

/** The sidebar of a test book from its outline's data: the written pages of each part, the tracks' full lists. */
export function testSidebar(outline, written) {
	const sideSteps = (letter) => {
		const entries = outline.tracks[letter];
		return entries.flatMap((entry, index) => (entry.sideStep ? [{ id: entry.id, before: entries.slice(index + 1).find((other) => !other.sideStep).id }] : []));
	};
	const track = (letter, label) => ({
		label,
		description: `the ${label} track.`,
		sequence: outline.tracks[letter].filter((entry) => !entry.sideStep).map((entry) => entry.id),
		sideSteps: sideSteps(letter),
	});
	return {
		parts: outline.parts.map((part) => ({
			slug: part.slug,
			label: part.title,
			pages: [`${part.slug}/index`, ...part.pages, `${part.slug}/review`].filter((id) => written.has(id)),
		})),
		tracks: { game: track('G', 'Games'), beginner: track('B', 'Beginners'), engine: track('E', 'Engine') },
	};
}

/**
 * Writes a book into a temporary folder. `pages` maps page ids to Markdown; `files` maps other paths (relative to the
 * book) to their contents; `outline(data)` and `sidebar(data)` may change the generated outline and sidebar in place.
 * Returns `{ root, remove }`.
 */
export function makeBook({ pages = {}, files = {}, glossary = { terms: [] }, outline, sidebar } = {}) {
	const root = mkdtempSync(path.join(process.env.TMP ?? tmpdir(), 'book-test-'));
	const write = (relative, content) => {
		const file = path.join(root, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	};
	const texts = Object.fromEntries(Object.entries(pages).map(([id, text]) => [id, withId(id, text)]));
	const outlineData = testOutline(texts);
	outline?.(outlineData);
	const sidebarData = testSidebar(outlineData, new Set(Object.keys(texts)));
	sidebar?.(sidebarData);
	write('engine.pin', c_Pin);
	write('site.json', JSON.stringify(c_SiteJson));
	write('LICENSE', c_License);
	write('src/content/glossary.json', JSON.stringify(glossary));
	write('src/generated/outline.json', JSON.stringify(outlineData));
	write('src/sidebar.json', JSON.stringify(sidebarData));
	for (const [id, text] of Object.entries(texts)) write(`src/content/docs/${id}.md`, text);
	for (const [relative, content] of Object.entries(files)) write(relative, content);
	return { root, remove: () => rmSync(root, { recursive: true, force: true }) };
}

/**
 * Runs the book's remark and rehype plugins on one page; resolves to its HTML (or its HTML tree with `tree: true`), or
 * rejects with the build's error. A release build (`env.DOCS_RELEASE`) gets c_ReleaseSite unless `env` names a site.
 * `after` holds remark plugins that run after the book's, as Starlight's do in the build (`[plugin, options]`).
 */
export async function render(root, pageId, { env = {}, rehype = true, tree: returnTree = false, after = [] } = {}) {
	const site = env.DOCS_RELEASE === '1' ? c_ReleaseSite : 'https://example.com';
	const settings = readSettings({ root, env: { DOCS_BASE: '/book', DOCS_SITE: site, ...env } });
	const context = createBookContext(settings);
	const markdown = bookMarkdown(context, { digest: 'test' });
	const file = path.join(settings.docsDir, ...`${pageId}.md`.split('/'));
	const { readFileSync } = await import('node:fs');
	const text = readFileSync(file, 'utf8');
	// As Astro's content layer does (its "empty-with-spaces" front matter): the front matter becomes blank lines, so the
	// lines the plugins report are the lines of the file.
	const body = text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, (block) => block.replace(/[^\r\n]/g, ' '));
	let processor = unified().use(remarkParse).use(remarkGfm).use(remarkSmartypants).use(remarkDirective);
	for (const plugin of [...markdown.remarkPlugins, ...after]) processor = Array.isArray(plugin) ? processor.use(plugin[0], plugin[1]) : processor.use(plugin);
	processor = processor.use(remarkRehype, { allowDangerousHtml: true });
	if (rehype) for (const plugin of markdown.rehypePlugins) processor = Array.isArray(plugin) ? processor.use(plugin[0], plugin[1]) : processor.use(plugin);
	const vfile = new VFile({ path: file, value: body });
	const tree = await processor.run(processor.parse(vfile), vfile);
	return returnTree ? tree : toHtml(tree, { allowDangerousHtml: true });
}

/** Asserts that the promise rejects with a message matching every pattern. */
export async function rejectsWith(promise, ...patterns) {
	try {
		await promise;
	} catch (error) {
		for (const pattern of patterns) {
			if (!pattern.test(error.message)) throw new Error(`the error does not match ${pattern}:\n${error.message}`);
		}
		return error;
	}
	throw new Error('expected the build to fail');
}
