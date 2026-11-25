// The book's Markdown pipeline: which plugins run, in which order, with what they share (the build context).
// Order matters: the strips check the page as its writer wrote it, before anything becomes HTML; the included tables
// and the part pages' generated parts come in next, so that every later plugin treats them as written text; the
// directives are checked against the book's table before any plugin draws one; mermaid fences are taken before
// excerpts and Expressive Code see them; and the report runs last to fail on everything at once.

import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { loadGlossary } from '../lib/glossary.mjs';
import { loadOutline } from '../lib/outline.mjs';
import { loadPageIndex } from '../lib/pages.mjs';
import { loadSidebar } from '../lib/sidebar.mjs';
import { remarkBookAnswers } from './answers.mjs';
import { remarkBookAsides } from './asides.mjs';
import { remarkBookCheckpoints } from './checkpoint.mjs';
import { remarkBookDerivations } from './derivation.mjs';
import { remarkBookDirectives } from './directives.mjs';
import { remarkBookExcerpts } from './excerpts.mjs';
import { remarkBookFigures } from './figures.mjs';
import { remarkBookGlossary } from './glossary.mjs';
import { remarkBookInclude } from './include.mjs';
import { remarkBookLinks } from './links.mjs';
import { remarkBookLists } from './lists.mjs';
import { c_KatexOptions, remarkBookMathCheck } from './math.mjs';
import { remarkBookMermaid } from './mermaid.mjs';
import { remarkBookNavigation } from './navigation.mjs';
import { remarkBookPartPages } from './partpages.mjs';
import { remarkBookReport } from './report.mjs';
import { rehypeBookMath, rehypeBookStrip } from './rehype.mjs';
import { remarkBookSince } from './since.mjs';
import { remarkBookStrips } from './strips.mjs';
import { remarkBookTabs } from './tabs.mjs';
import { remarkBookTestOut } from './testout.mjs';
import { remarkBookValues } from './values.mjs';

/** What every plugin of one build shares: the settings, the glossary, the outline, the sidebar and the page index. */
export function createBookContext(settings) {
	const glossary = loadGlossary(settings.glossaryFile);
	const outline = loadOutline(settings.outlineFile);
	const sidebar = loadSidebar(settings.sidebarFile);
	// A preview leaves some pages out (settings.previewOmit): the sidebar does not list them.
	for (const part of sidebar.parts) part.pages = part.pages.filter((id) => !settings.previewOmit.has(id));
	const glossaryIds = glossary.terms.map((term) => term.id);
	return {
		settings,
		glossary,
		outline,
		sidebar,
		index: () => loadPageIndex(settings.docsDir, { glossaryIds, revalidate: settings.command === 'dev', referenceDir: settings.referenceDir, outline, omit: settings.previewOmit }),
	};
}

function hashTree(hash, folder, filter) {
	let entries;
	try {
		entries = readdirSync(folder, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
	} catch (error) {
		if (error.code === 'ENOENT') return;
		throw error;
	}
	for (const entry of entries) {
		const file = path.join(folder, entry.name);
		if (entry.isDirectory()) hashTree(hash, file, filter);
		else if (filter(entry.name)) {
			const info = statSync(file);
			hash.update(`${path.relative(folder, file)}\n${info.size}\n${info.mtimeMs}\n`);
		}
	}
}

/**
 * A digest of everything a page's HTML depends on besides the page itself: the other pages' titles and anchors (links,
 * Needs), the glossary, the outline's data, the sidebar, the vendored libraries' record, the figure manifests and
 * pictures, the committed drawings of the diagrams, the sketches, the generated reference a page includes, the
 * tutorials' files, patches and downloads that checkpoints, hunks of patches and worked solutions name, the pin and the
 * book's own plugin code. Astro keeps rendered pages between builds and renders a page again only when its file changed
 * or its configuration did; the digest is part of the configuration, so a change to any of these renders every page.
 */
export function inputsDigest(settings, index) {
	const hash = createHash('sha256');
	// Besides the book's own files: how code blocks are drawn (ec.config.mjs, which is not part of Astro's
	// configuration), the configuration and the content schema, and every package's version (package-lock.json): a
	// change of any of them would otherwise leave pages in Astro's cache rendered the old way, without a word.
	const configuration = ['ec.config.mjs', 'astro.config.mjs', path.join('src', 'content.config.ts'), 'package-lock.json'].map((name) => path.join(settings.root, name));
	for (const file of [settings.glossaryFile, settings.outlineFile, settings.sidebarFile, settings.vendorFile, path.join(settings.root, 'engine.pin'), path.join(settings.root, 'site.json'), ...configuration]) {
		hash.update(`${path.relative(settings.root, file)}\n`);
		try {
			hash.update(readFileSync(file));
		} catch (error) {
			if (error.code !== 'ENOENT') throw error;
		}
	}
	hashTree(hash, settings.figuresDir, (name) => name.endsWith('.json'));
	hashTree(hash, settings.picturesDir, () => true);
	hashTree(hash, settings.diagramsDir, () => true);
	hashTree(hash, settings.sketchesDir, () => true);
	hashTree(hash, settings.referenceDir, () => true);
	hashTree(hash, path.join(settings.root, 'tutorials'), (name) => name.endsWith('.tutorial.json') || name.endsWith('.stamp.json') || name.endsWith('.patch'));
	hashTree(hash, path.join(settings.root, 'public', 'downloads'), () => true);
	hashTree(hash, path.join(settings.root, 'src', 'lib'), (name) => name.endsWith('.mjs'));
	hashTree(hash, path.join(settings.root, 'src', 'plugins'), (name) => name.endsWith('.mjs'));
	// What a page reads of the other pages: their ids, front matter, anchors and questions (a part's review page holds
	// them, without their places in the file, which move when the text above them changes), never the rest of their
	// prose, so that editing the text of one page renders only that page again.
	const withoutPositions = (key, value) => (key === 'position' ? undefined : value);
	for (const page of [...index.pages.values()].sort((a, b) => a.id.localeCompare(b.id))) {
		hash.update(JSON.stringify([page.id, page.data, page.error, [...page.anchors].sort(), page.checkYourself ?? null], withoutPositions));
	}
	hash.update(JSON.stringify({ base: settings.base, site: settings.site, release: settings.release }));
	return hash.digest('hex').slice(0, 16);
}

/** The remark and rehype plugins of the book, for `unified({ remarkPlugins, rehypePlugins })`. */
export function bookMarkdown(context, { digest }) {
	return {
		remarkPlugins: [
			remarkMath,
			// The digest rides on the first plugin's options so that Astro's configuration digest changes with it.
			[remarkBookStrips(context), { inputsDigest: digest }],
			remarkBookInclude(context),
			remarkBookPartPages(context),
			remarkBookDirectives(context),
			remarkBookValues(context),
			remarkBookMermaid(context),
			remarkBookExcerpts(context),
			remarkBookLinks(context),
			remarkBookFigures(context),
			remarkBookTabs(),
			remarkBookAnswers(context),
			remarkBookTestOut(context),
			remarkBookDerivations(),
			remarkBookLists(),
			remarkBookAsides(),
			remarkBookCheckpoints(context),
			remarkBookNavigation(context),
			remarkBookSince(context),
			remarkBookGlossary(context),
			remarkBookMathCheck(),
			remarkBookReport(context),
		],
		rehypePlugins: [
			[rehypeKatex, c_KatexOptions],
			rehypeBookMath(context),
			rehypeBookStrip(),
		],
	};
}
