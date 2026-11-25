// The generated parts of a part's index and review pages (plan/site.md, "Navigation"; plan/style.md §7.7), as Markdown
// trees built from the outline's data and the written pages. The page index uses them for the pages' anchors (so that
// a link to a generated heading is checked like any other) and src/plugins/partpages.mjs puts them into the page:
// - <part>/index, after the part editor's paragraph: the map of the part (its Needs graph as a diagram, and the same
//   graph as a list), the pages outside the part that its pages need, what the reader can do after the part (the learn
//   lines of its pages), and in `basics` the first part that needs each primer;
// - <part>/review, before the part editor's cumulative exercises: every "Check yourself" question of the part's pages,
//   page by page, with its answer.

import path from 'node:path';
import { closureNeeds, needAlternatives, needsClosure } from './outline.mjs';
import { parseMarkdown } from './markdown.mjs';

export const c_PrimerPart = 'basics';
export const c_IndexHeadings = {
	map: 'The map of this part',
	before: 'Before this part',
	after: 'After this part you can',
	primers: 'Where each primer is first needed',
};
export const c_ReviewHeading = 'Check yourself, page by page';

const text = (value) => ({ type: 'text', value });
const paragraph = (children) => ({ type: 'paragraph', children });
const heading = (depth, children) => ({ type: 'heading', depth, children });
const list = (items, ordered = false) => ({ type: 'list', ordered, spread: false, children: items.map((children) => ({ type: 'listItem', spread: false, children })) });

/** A title as inline Markdown (outline titles may hold code spans). */
export function inlineTitle(title) {
	const first = parseMarkdown(title).children[0];
	return first?.type === 'paragraph' ? first.children : [text(title)];
}

/** A relative link from the page `from` to the page `to`, both book ids: "time.md", "../core/time.md". */
export function relativeLink(from, to, anchor = null) {
	const target = `${path.posix.relative(path.posix.dirname(from), to)}.md`;
	return anchor ? `${target}#${anchor}` : target;
}

/** A page named in a generated part: a link when it is written, its title marked "not written yet" otherwise. */
function pageName(from, id, outline, pages) {
	const page = pages.get(id);
	if (page) return [{ type: 'link', url: relativeLink(from, id), children: inlineTitle(page.title) }];
	return [{ type: 'emphasis', children: [...inlineTitle(outline.rows.get(id)?.title ?? id), text(' (not written yet)')] }];
}

/** A Need with its alternatives: "X or Y". */
function needName(from, need, outline, pages) {
	return needAlternatives(need).flatMap((id, position) => [...(position > 0 ? [text(' or ')] : []), ...pageName(from, id, outline, pages)]);
}

// Mermaid reads labels in quotes; these characters would end or change them.
function mermaidLabel(title) {
	return title.replace(/`/g, '').replace(/[#"<>&]/g, (character) => ({ '#': '#35;', '"': '#quot;', '<': '#lt;', '>': '#gt;', '&': '#amp;' })[character]);
}

/**
 * The Needs graph of a part as Mermaid's text: a box per row, and an arrow from each Need inside the part to the row
 * that needs it (a dotted arrow for one of two alternatives). A row whose Needs are "-" needs the part's first row
 * (style.md §1.2). Needs outside the part are listed in "Before this part" instead.
 */
export function needsGraphSource(outline, part) {
	const ids = new Map(part.pages.map((id, position) => [id, `p${position}`]));
	const lines = ['flowchart TB'];
	for (const id of part.pages) lines.push(`    ${ids.get(id)}["${mermaidLabel(outline.rows.get(id)?.title ?? id)}"]`);
	for (const id of part.pages) {
		for (const need of closureNeeds(outline, id)) {
			const alternatives = needAlternatives(need);
			const arrow = alternatives.length > 1 ? '-.->' : '-->';
			for (const alternative of alternatives) if (ids.has(alternative)) lines.push(`    ${ids.get(alternative)} ${arrow} ${ids.get(id)}`);
		}
	}
	return lines.join('\n');
}

/** The caption and alternative text of a part's Needs graph. */
export function needsGraphText(part) {
	return {
		caption: 'Each page of this part with the pages of the part it needs: an arrow leads from a page to a page that needs it, and a dotted arrow from one of two pages either of which will do.',
		alt: `A graph of the ${part.pages.length} pages of the part “${part.title.replace(/`/g, '')}”. Each page is a box, and an arrow leads from each page to the pages of the part that need it. The list below the graph names the same pages and Needs.`,
	};
}

/** The pages of the part, in reading order, each with the pages of the part it needs: the graph as a list. */
function mapList(from, outline, part, pages) {
	return list(part.pages.map((id) => {
		const inside = closureNeeds(outline, id).filter((need) => needAlternatives(need).some((alternative) => part.pages.includes(alternative)));
		const children = [...pageName(from, id, outline, pages)];
		if (inside.length) {
			children.push(text(': needs '));
			inside.forEach((need, position) => {
				if (position > 0) children.push(text(position === inside.length - 1 ? ' and ' : ', '));
				children.push(...needName(from, need, outline, pages));
			});
		}
		return [paragraph(children)];
	}), true);
}

/** For each primer of `basics`, the first other part with a page that has the primer in its Needs closure. */
export function primerFirstParts(outline) {
	const primers = (outline.partBySlug.get(c_PrimerPart)?.pages ?? []).filter((id) => outline.rows.get(id)?.kind === 'primer');
	return primers.map((id) => {
		const part = outline.parts.find((candidate) => candidate.slug !== c_PrimerPart && candidate.pages.some((row) => needsClosure(outline, row).has(id)));
		return { id, part: part ?? null };
	});
}

/**
 * The generated part of `<part>/index` (`from` is its book id): Markdown nodes, and the diagram they draw, `{ source,
 * meta }` (npm run diagrams draws it with the book's other diagrams).
 */
export function indexContent(from, outline, part, pages) {
	const graph = needsGraphText(part);
	const source = needsGraphSource(outline, part);
	const meta = `caption="${graph.caption}" alt="${graph.alt.replace(/"/g, '“')}"`;
	const nodes = [
		heading(2, [text(c_IndexHeadings.map)]),
		paragraph([text(`The part has ${part.pages.length} pages. The graph shows which pages of the part each page needs; the list says the same in words, in reading order.`)]),
		{ type: 'code', lang: 'mermaid', meta, value: source },
		mapList(from, outline, part, pages),
	];
	// A part on no track (the reference) is read by links and search, not in order: each of its pages shows its own
	// Needs in its top strip, and its index shows no "Before this part" (plan/site.md, "Navigation"; rulings 7, D9).
	if (part.tracks.length) {
		nodes.push(heading(2, [text(c_IndexHeadings.before)]));
		if (part.needs.length) {
			nodes.push(paragraph([text('The pages of this part need these pages of other parts:')]));
			nodes.push(list(part.needs.map((need) => [paragraph(needName(from, need, outline, pages))])));
		} else {
			nodes.push(paragraph([text('The pages of this part need no page of another part.')]));
		}
	}
	nodes.push(heading(2, [text(c_IndexHeadings.after)]));
	const learned = part.pages.filter((id) => Array.isArray(pages.get(id)?.data?.learn) && pages.get(id).data.learn.length);
	if (learned.length) {
		nodes.push(paragraph([text('Each page of the part says what you can do after it:')]));
		nodes.push(list(learned.map((id) => [
			paragraph(pageName(from, id, outline, pages)),
			list(pages.get(id).data.learn.map((item) => [paragraph([text(String(item?.text ?? ''))])])),
		])));
	} else {
		nodes.push(paragraph([text('No page of this part with objectives is written yet.')]));
	}
	const unwritten = part.pages.filter((id) => !pages.has(id)).length;
	if (unwritten) nodes.push(paragraph([text(`${unwritten} of the part's ${part.pages.length} pages ${unwritten === 1 ? 'is' : 'are'} not written yet.`)]));
	if (part.slug === c_PrimerPart) {
		nodes.push(heading(2, [text(c_IndexHeadings.primers)]));
		nodes.push(paragraph([text('Each primer, with the first part of the book whose pages need what it teaches:')]));
		nodes.push(list(primerFirstParts(outline).map(({ id, part: first }) => [paragraph([
			...pageName(from, id, outline, pages),
			text(first ? `: first needed in part ${first.number}, ${first.title.replace(/`/g, '')}` : ': no page outside this part needs it'),
		])])));
	}
	return { nodes, diagrams: [{ source, meta }] };
}

/**
 * The generated part of `<part>/review` (`from` is its book id): for each written page of the part, in reading order, a
 * heading and a copy of its "Check yourself" section (`questions`: page id → the section's nodes). Links within the
 * page a question comes from are turned into links to that page, and every copied node remembers its page (for
 * pictures and for messages).
 */
export function reviewContent(from, outline, part, pages, questions) {
	const nodes = [heading(2, [text(c_ReviewHeading)])];
	const written = part.pages.filter((id) => questions.has(id));
	if (!written.length) {
		nodes.push(paragraph([text('No page of this part with questions is written yet.')]));
		return { nodes, diagrams: [] };
	}
	nodes.push(paragraph([text('The questions of every page of this part, in reading order, each with its hidden answer. Answer them before the exercises below.')]));
	for (const id of written) {
		const copy = structuredClone(questions.get(id));
		const visit = (node) => {
			node.data ??= {};
			node.data.bookPageId = id;
			if ((node.type === 'link' || node.type === 'definition') && typeof node.url === 'string' && node.url.startsWith('#')) node.url = relativeLink(from, id, node.url.slice(1));
			for (const child of node.children ?? []) visit(child);
		};
		copy.forEach(visit);
		// The copies stay out of the search index: each question is indexed on its own page, and a part's review would
		// otherwise match every query of its part and carry all of its questions in its search fragment (budget row 12).
		for (const node of copy) node.data.hProperties = { ...node.data.hProperties, dataPagefindIgnore: '' };
		nodes.push(heading(3, inlineTitle(pages.get(id).title)));
		nodes.push(paragraph([text('From '), ...pageName(from, id, outline, pages), text('.')]));
		nodes.push(...copy);
	}
	return { nodes, diagrams: [] };
}

/** The generated part of a part page, `{ nodes, diagrams, after }`: `after` is true when it follows the editor's text. */
export function partPageContent(page, outline, pages, questions) {
	const part = outline.partBySlug.get(page.id.split('/')[0]);
	if (!part) return null;
	if (page.data?.generated === 'index') return { ...indexContent(page.id, outline, part, pages), after: true };
	if (page.data?.generated === 'review') return { ...reviewContent(page.id, outline, part, pages, questions), after: false };
	return null;
}
