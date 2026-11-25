// lists: two directives that draw a Markdown list in another form (plan/site.md, "What MDX would have given").
// - ":::steps" holds one numbered list and draws it with Starlight's steps markup (the `sl-steps` class of its <Steps>
//   component, whose styles src/styles/book.css carries), so a sequence of steps reads as one numbered path.
// - ":::files" (":::files[The project after step 3]") holds one bulleted list of files and folders and draws it as a
//   file tree. An item starts with its name: a word, a name in backticks, or a bold name (highlighted); a name that ends
//   with "/" or holds a list is a folder, and "…" stands for files left out. The rest of the item's line is a comment.

import { element, plainText, rawHtml, report, takeDirectiveLabel, text, withoutTerms } from './shared.mjs';

export const c_FilesLabel = 'Files and folders';
// Icons drawn for the book (no third-party artwork): a folder and a page with a folded corner.
const c_FolderIcon = '<svg class="book-files__icon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false"><path d="M1.5 3.5h4.5l1.5 1.5h7v8.5h-13z"/></svg>';
const c_FileIcon = '<svg class="book-files__icon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false"><path d="M3.5 1.5h6l3 3v10h-9z M9.5 1.5v3h3"/></svg>';

function describe(node) {
	if (node.type === 'list') return node.ordered ? 'a numbered list' : 'a bulleted list';
	return { paragraph: 'a paragraph', code: 'a code block', heading: 'a heading', containerDirective: `a :::${node.name} block`, leafDirective: `::${node.name}` }[node.type] ?? `a ${node.type}`;
}

/** ":::steps": the container becomes its one numbered list, with Starlight's steps class. */
function drawSteps(file, node) {
	// A title in brackets is refused by the directives plugin; it is not counted again as content here.
	if (node.children[0]?.data?.directiveLabel) node.children.shift();
	const [list, ...others] = node.children;
	if (!list || list.type !== 'list' || !list.ordered || others.length) {
		const found = node.children.length ? node.children.map(describe).join(', ') : 'nothing';
		report(file, node, `:::steps holds one numbered list (1. 2. 3.) and nothing else; it holds ${found}`);
		return null;
	}
	const properties = { className: ['sl-steps'], role: 'list' };
	// Starlight counts the steps from the list's first number (its <Steps> component sets the same variable).
	if (typeof list.start === 'number' && list.start !== 1) properties.style = `--sl-steps-start: ${list.start - 1}`;
	list.data ??= {};
	list.data.hProperties = { ...(list.data.hProperties ?? {}), ...properties };
	return list;
}

/** The name, the highlight and the comment of a file tree's item from its first paragraph, or `{ error }`. */
export function fileEntry(paragraph) {
	const [first, ...rest] = paragraph?.type === 'paragraph' ? paragraph.children : [];
	let name = null;
	let highlighted = false;
	let comment = rest;
	if (first?.type === 'inlineCode') name = first.value;
	else if (first?.type === 'strong') {
		name = plainText(first);
		highlighted = true;
	} else if (first?.type === 'text') {
		const match = /^\s*(\S+)([\s\S]*)$/.exec(first.value);
		if (match) {
			// "Spinner.cpp: turns its entity": the colon ends the name, it is not part of it.
			name = match[1].replace(/:$/, '');
			comment = match[2] ? [text(match[2]), ...rest] : rest;
		}
	}
	if (!name || !name.trim()) return { error: 'an item of a file tree starts with the name of a file or folder (a word, a name in backticks, or a bold name)' };
	// The comment reads after the name: "Scripts/ — the game's scripts" and "Scripts/: the game's scripts" both show
	// "the game's scripts".
	if (comment[0]?.type === 'text') {
		const value = comment[0].value.replace(/^\s*(?:[:—–]|-(?=\s))?\s*/, '');
		comment = value ? [text(value), ...comment.slice(1)] : comment.slice(1);
	}
	return { name: name.trim(), highlighted, comment };
}

/** The <li> of one file tree item, or null after reporting why it cannot be drawn. */
function fileItem(file, item) {
	const [first, ...others] = item.children;
	const entry = fileEntry(first);
	if (entry.error) {
		report(file, item, entry.error);
		return null;
	}
	const inner = others.filter((child) => child.type === 'list');
	if (others.length !== inner.length || inner.length > 1 || inner.some((list) => list.ordered)) {
		report(file, item, `an item of a file tree holds its name, a comment and at most one bulleted list of what is inside it; "${entry.name}" also holds ${others.filter((child) => child.type !== 'list' || child.ordered).map(describe).join(', ') || 'a second list'}`);
		return null;
	}
	const more = /^(…|\.\.\.)$/.test(entry.name);
	if (more) {
		if (inner.length) report(file, item, `"${entry.name}" stands for files left out: it holds no list`);
		return element('li', { className: ['book-files__more'] }, [
			element('span', { ariaHidden: 'true' }, [text('…')]),
			element('span', { className: ['sr-only'] }, [text('More files')]),
		]);
	}
	const folder = entry.name.endsWith('/') || inner.length > 0;
	const nameNodes = [];
	if (folder) nameNodes.push(withoutTerms(element('span', { className: ['sr-only'] }, [text('Folder ')])));
	nameNodes.push(entry.highlighted ? element('strong', {}, [text(entry.name)]) : text(entry.name));
	const line = [
		rawHtml(folder ? c_FolderIcon : c_FileIcon),
		withoutTerms(element('span', { className: ['book-files__name', ...(entry.highlighted ? ['book-files__name--highlight'] : [])] }, nameNodes)),
	];
	if (entry.comment.length) line.push(text(' '), element('span', { className: ['book-files__comment'] }, entry.comment));
	const children = [element('span', { className: ['book-files__entry'] }, line)];
	if (inner.length) {
		const list = fileList(file, inner[0]);
		if (list) children.push(list);
	}
	return element('li', { className: [folder ? 'book-files__folder' : 'book-files__file'] }, children);
}

function fileList(file, list) {
	const items = list.children.map((item) => fileItem(file, item)).filter(Boolean);
	return items.length === list.children.length ? element('ul', {}, items) : null;
}

/** ":::files": the container becomes a figure holding the tree, named by its label or "Files and folders". */
function drawFiles(file, node) {
	const label = takeDirectiveLabel(node);
	const [list, ...others] = node.children;
	if (!list || list.type !== 'list' || list.ordered || others.length) {
		const found = node.children.length ? node.children.map(describe).join(', ') : 'nothing';
		report(file, node, `:::files holds one bulleted list of files and folders, nested for what a folder holds, and nothing else; it holds ${found}`);
		return null;
	}
	const tree = fileList(file, list);
	if (!tree) return null;
	tree.data.hProperties.className = ['book-files__tree'];
	if (label?.text.trim()) return element('figure', { className: ['book-files'] }, [element('figcaption', { className: ['book-files__caption'] }, label.nodes), tree]);
	return element('figure', { className: ['book-files'], ariaLabel: c_FilesLabel }, [tree]);
}

export function remarkBookLists() {
	return function attacher() {
		return function transformer(tree, file) {
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, index) => {
					visit(node);
					if (node.type !== 'containerDirective') return;
					let drawn = null;
					if (node.name === 'steps') drawn = drawSteps(file, node);
					else if (node.name === 'files') drawn = drawFiles(file, node);
					else return;
					if (drawn) parent.children[index] = drawn;
				});
			};
			visit(tree);
		};
	};
}
