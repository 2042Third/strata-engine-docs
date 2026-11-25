// strips: the top strip of a page is drawn from its front matter (src/components/PageTitle.astro, src/lib/strip.mjs);
// this plugin checks that front matter against the book's rules and the outline (src/lib/frontmatter.mjs), that the
// Needs of the written pages form no cycle (O6), and that the end of the page is the one of its kind (rule P1,
// style.md §6.3): the section the body ends with, then the bottom strip's sections in order as the page's last ones,
// one Summary item per objective, three to six questions, one to four exercises or three to eight practice items, each
// followed by a hidden answer whose `tests` name the objectives it tests (rule P2), and on primers at least three pages
// under "Where the book uses it" that have the primer in their Needs closure. It also checks the rest of what style.md
// §14 gives the strips: the exact headings of the body of each kind (§7), the Test out box of a primer (rule P3), a
// worked example before the bottom strip (§8), a checkpoint at the end of each step section of a tutorial (§7.4), the
// share of an internals page's general section (§7.3), and the page that teaches running a command in the Needs
// closure of a page with a step that has no menu or button (§10). tools/pages.py check applies the rules of §6.3, §7
// and P3 to the Markdown source in the same words.

import path from 'node:path';
import { checkFrontmatter, findNeedCycles, pageRole } from '../lib/frontmatter.mjs';
import { headingText } from '../lib/markdown.mjs';
import { needsClosure } from '../lib/outline.mjs';
import { readTutorial, stampProblems } from '../lib/tutorials.mjs';
import { answerTests } from './answers.mjs';
import { pageOf, report } from './shared.mjs';

const c_ConceptStrip = ['Summary', 'Check yourself', 'Exercises', 'Where it lives in Strata', 'Further reading'];

/** The bottom strip of each kind (style.md §6.3), in order: the page's last level-2 sections. */
export const c_BottomStrips = {
	primer: ['Summary', 'Check yourself', 'Practice', 'Where the book uses it', 'Further reading'],
	concept: c_ConceptStrip,
	internals: c_ConceptStrip,
	tutorial: c_ConceptStrip,
	'how-to': c_ConceptStrip,
	reference: ['Where it lives in Strata'],
};

// The section the body ends with, before the bottom strip (style.md §6.3). Internals pages and tutorials are checked
// in bodyEndProblem; a reference page's body is its generated tables.
export const c_BodyEnds = { primer: 'Common mistakes', concept: 'Common mistakes', 'how-to': 'Variations' };
export const c_InternalsEnd = 'Changing it safely';
export const c_InternalsHistory = 'What went wrong before';
// The sections a tutorial opens with (style.md §7.4): its step sections come after them, so neither ends its body.
export const c_TutorialOpening = ['What you will make', 'What you need'];

// How many numbered questions, exercises or practice items each section holds (style.md §6.3 and §8).
export const c_ItemCounts = { 'Check yourself': [3, 6], Exercises: [1, 4], Practice: [3, 8] };
// The sections whose every answer names the objectives it tests (style.md §8).
export const c_TestedSections = ['Check yourself', 'Exercises', 'Practice'];
// "Where the book uses it" links at least this many pages (style.md §6.3).
export const c_MinBookUses = 3;
// style.md §7: the exact headings of the body of each kind (those written in backticks there), in their order, and the
// heading a kind's body starts with. tools/pages.py holds the same lists.
export const c_BodyHeadings = {
	primer: ['Why you will need this', 'Common mistakes'],
	concept: ['Common mistakes'],
	internals: ['The problem and how engines solve it', 'Alternatives Strata did not choose', 'How it is tested', 'Changing it safely'],
	tutorial: ['What you will make', 'What you need'],
	'how-to': ['Result', 'Variations'],
};
export const c_FirstHeadings = { primer: 'Why you will need this', tutorial: 'What you will make' };
// style.md §7.1: the Test out box holds exactly this many questions.
export const c_TestOutQuestions = 5;
// style.md §8: the kinds whose body holds at least one :::example before the bottom strip.
export const c_ExampleKinds = ['primer', 'concept', 'internals'];
// style.md §10: a step without a menu or button says so in these words, and its page has in its Needs closure the page
// that teaches running a command on each of its tracks.
export const c_CommandOnlyStep = 'This step has no menu or button';
export const c_CommandPages = { G: 'make/commands', B: 'make/commands', E: 'editor/commands' };
// style.md §7.3: an internals page's general section holds at most this share of the page's prose words.
export const c_GeneralSection = 'The problem and how engines solve it';
export const c_GeneralShare = 1 / 5;

const s_Cycles = new WeakMap();

function cyclesOf(index) {
	if (!s_Cycles.has(index)) s_Cycles.set(index, findNeedCycles(index.pages));
	return s_Cycles.get(index);
}

function collectAnswers(node, found) {
	if (node.type === 'containerDirective' && node.name === 'answer') found.push(node);
	for (const child of node.children ?? []) collectAnswers(child, found);
	return found;
}

/**
 * The questions of a section: every item of its numbered lists (those at the top of the page, not inside an aside or
 * another block), each with the answers that follow it up to the next item, whether they are indented into the item
 * or not. `before` holds the answers that come before the first item.
 */
export function questionsOf(section) {
	const questions = [];
	const before = [];
	for (const node of section.nodes) {
		if (node.type === 'list' && node.ordered) {
			for (const item of node.children) questions.push({ node: item, answers: collectAnswers(item, []) });
		} else {
			collectAnswers(node, questions.length ? questions.at(-1).answers : before);
		}
	}
	return { questions, before };
}

/** How many bulleted items a section holds in its lists at the top of the page. */
export function bulletCount(section) {
	return section.nodes.filter((node) => node.type === 'list' && !node.ordered).reduce((count, list) => count + list.children.length, 0);
}

/** The level-2 sections of a page in order, `[{ title, node, nodes }]`: `nodes` are the top-level nodes under it. */
export function sections(tree) {
	const result = [];
	let current = null;
	for (const node of tree.children) {
		if (node.type === 'heading' && node.depth === 2) {
			current = { title: headingText(node).trim(), node, nodes: [] };
			result.push(current);
		} else if (current) {
			current.nodes.push(node);
		}
	}
	return result;
}

function headingList(titles) {
	return titles.map((title) => `"## ${title}"`).join(', ');
}

function withArticle(kind) {
	return `${/^[aeiou]/.test(kind) ? 'an' : 'a'} ${kind}`;
}

/** The problem of the section before the bottom strip (`body`: the titles of the sections before it), or null. */
function bodyEndProblem(kind, body) {
	const last = body.at(-1) ?? null;
	if (kind === 'internals') {
		if (last === c_InternalsEnd || (last === c_InternalsHistory && body.at(-2) === c_InternalsEnd)) return null;
		return `P1: the body of an internals page ends with "## ${c_InternalsEnd}", followed by "## ${c_InternalsHistory}" when the history has one, before the bottom strip (style.md §6.3)`;
	}
	if (kind === 'tutorial') {
		if (last !== null && !c_TutorialOpening.includes(last)) return null;
		return `P1: a tutorial ends its body with its last step section: its step sections come after ${headingList(c_TutorialOpening)} and before the bottom strip (style.md §6.3, §7.4)`;
	}
	if (c_BodyEnds[kind] && last !== c_BodyEnds[kind]) return `P1: the body of ${withArticle(kind)} page ends with "## ${c_BodyEnds[kind]}" before the bottom strip (style.md §6.3)`;
	return null;
}

/**
 * Rule P1 (site.md, "Page shape"; style.md §6.3) for a page of `kind` with `learnCount` objectives: the section its
 * body ends with, the bottom strip as its last sections in order, and the counts of the Summary, the questions, the
 * exercises and the practice items, each of which is followed by an answer.
 */
export function bottomStripProblems(tree, kind, learnCount) {
	const strip = c_BottomStrips[kind];
	if (!strip) return [];
	const problems = [];
	const found = sections(tree);
	const titles = found.map((section) => section.title);
	const last = titles.slice(-strip.length);
	if (last.length !== strip.length || last.some((title, position) => title !== strip[position])) {
		const missing = strip.filter((title) => !titles.includes(title));
		problems.push({
			node: found.at(-1)?.node ?? tree,
			message: `P1: ${withArticle(kind)} page ends with the sections ${headingList(strip)}, in this order (style.md §6.3); its last sections are ${headingList(last) || 'none'}${missing.length ? ` (missing: ${headingList(missing)})` : ''}`,
		});
	} else {
		const body = titles.slice(0, titles.length - strip.length);
		const problem = bodyEndProblem(kind, body);
		if (problem) problems.push({ node: found[body.length - 1]?.node ?? found[0].node, message: problem });
	}
	const summary = found.find((section) => section.title === 'Summary');
	if (summary && kind !== 'reference') {
		const items = bulletCount(summary);
		if (items !== learnCount) problems.push({ node: summary.node, message: `P1: "## Summary" holds ${items} bulleted items; it holds one per objective of "learn" (${learnCount}), in their order (style.md §6.3)` });
	}
	for (const [title, [low, high]] of Object.entries(c_ItemCounts)) {
		const section = found.find((candidate) => candidate.title === title);
		if (!section) continue;
		const { questions } = questionsOf(section);
		if (questions.length < low || questions.length > high) {
			problems.push({ node: section.node, message: `P1: "## ${title}" holds ${questions.length} numbered items; it holds ${low} to ${high} (style.md §6.3 and §8)` });
		}
		for (const question of questions) {
			if (question.answers.length === 0) problems.push({ node: question.node, message: `every question and exercise under "## ${title}" is followed by an :::answer (style.md §8): add one` });
		}
	}
	return problems;
}

/**
 * Rule P2 and the answers' `tests` (style.md §8): every answer under Check yourself, Exercises and Practice names
 * objectives of the page, every `tests` id is an objective of the page, and every objective is tested by at least one
 * Check-yourself answer.
 */
export function testsProblems(tree, learnIds) {
	const problems = [];
	const checked = new Set();
	const known = new Set(learnIds);
	// The answers of each level-2 section; those before the first heading (a primer's Test out box) name objectives too.
	let current = { title: null, answers: [] };
	const groups = [current];
	for (const node of tree.children) {
		if (node.type === 'heading' && node.depth === 2) {
			current = { title: headingText(node).trim(), answers: [] };
			groups.push(current);
		} else {
			collectAnswers(node, current.answers);
		}
	}
	for (const group of groups) {
		for (const answer of group.answers) {
			const tests = answerTests(answer);
			if (tests === null) {
				if (c_TestedSections.includes(group.title)) problems.push({ node: answer, message: `P2: an answer under "## ${group.title}" names the objectives it tests: :::answer{tests="<learn ids>"}` });
				continue;
			}
			for (const id of tests) {
				if (!known.has(id)) problems.push({ node: answer, message: `P2: tests="${id}" is not an objective of the page (its learn ids: ${[...known].join(', ') || 'none'})` });
				else if (group.title === 'Check yourself') checked.add(id);
			}
		}
	}
	for (const id of learnIds) {
		if (!checked.has(id)) problems.push({ node: tree, message: `P2: the objective "${id}" is in the tests of no answer under "## Check yourself"` });
	}
	return problems;
}

/** The book id a relative link to a page's .md file names (`from` is the linking page's id), or null. */
export function linkedPageId(from, url) {
	const target = String(url).split('#')[0];
	if (!target.endsWith('.md') || target.startsWith('/') || /^[a-z][a-z0-9+.-]*:/i.test(target)) return null;
	let decoded;
	try {
		decoded = decodeURIComponent(target);
	} catch {
		return null; // The links plugin reports the link.
	}
	const joined = path.posix.normalize(path.posix.join(path.posix.dirname(from), decoded));
	if (joined.startsWith('..') || joined.startsWith('/')) return null;
	return joined.slice(0, -'.md'.length);
}

/**
 * style.md §6.3 on a primer: "Where the book uses it" links at least three pages, each of which has the primer in its
 * Needs closure (it uses what the primer teaches). A linked page that does not exist is the links plugin's to report.
 */
export function bookUsesProblems(tree, pageId, outline) {
	const section = sections(tree).find((candidate) => candidate.title === 'Where the book uses it');
	if (!section) return [];
	const problems = [];
	const targets = new Map();
	const visit = (node) => {
		if (node.type === 'link') {
			const id = linkedPageId(pageId, node.url);
			if (id !== null && id !== pageId && !targets.has(id)) targets.set(id, node);
		}
		for (const child of node.children ?? []) visit(child);
	};
	section.nodes.forEach(visit);
	if (targets.size < c_MinBookUses) problems.push({ node: section.node, message: `"## Where the book uses it" links ${targets.size} page${targets.size === 1 ? '' : 's'}; it links at least ${c_MinBookUses}, each with one sentence on what it uses (style.md §6.3)` });
	for (const [id, node] of targets) {
		if (!outline.rows.has(id)) problems.push({ node, message: `"## Where the book uses it" links ${id}, which is no row of the outline: link a page of the book` });
		else if (!needsClosure(outline, id).has(pageId)) problems.push({ node, message: `${id} does not have ${pageId} in its Needs closure, so it does not use what the primer teaches (style.md §6.3): link a page that does` });
	}
	return problems;
}

/** P1 (style.md §7): the exact headings of the body of a kind are there, in their order, and the first one first. */
export function bodyHeadingsProblems(tree, kind) {
	const found = sections(tree);
	const titles = found.map((section) => section.title);
	const at = found[0]?.node ?? tree;
	const problems = [];
	const wanted = c_BodyHeadings[kind] ?? [];
	const positions = wanted.map((title) => titles.indexOf(title));
	wanted.forEach((title, index) => {
		if (positions[index] < 0) problems.push({ node: at, message: `P1: ${withArticle(kind)} page has the section "## ${title}" (style.md §7): add it` });
	});
	const present = positions.filter((position) => position >= 0);
	if (present.some((position, index) => index > 0 && position < present[index - 1])) problems.push({ node: at, message: `P1: the sections ${headingList(wanted)} stand in this order on ${withArticle(kind)} page (style.md §7)` });
	const first = c_FirstHeadings[kind];
	if (first && titles.length && titles[0] !== first) problems.push({ node: at, message: `P1: the first section of ${withArticle(kind)} page is "## ${first}" (style.md §7)` });
	return problems;
}

/** Comments in HTML stand anywhere: they are not the page's first thing. */
function isComment(node) {
	return node.type === 'html' && /^\s*<!--[\s\S]*-->\s*$/.test(node.value);
}

function findDirectives(node, name, found = []) {
	if (node.type === 'containerDirective' && node.name === name) found.push(node);
	for (const child of node.children ?? []) findDirectives(child, name, found);
	return found;
}

/**
 * P3 (site.md, "Page shape"; style.md §7.1): a primer opens with one Test out box, before any heading and any text, and
 * the box holds exactly five numbered questions, each followed by an answer whose `tests` name objectives; together
 * they test every objective of the page.
 */
export function testOutProblems(tree, learnIds) {
	const boxes = findDirectives(tree, 'test-out');
	const firstNode = tree.children.find((node) => !isComment(node));
	if (boxes.length === 0) return [{ node: firstNode ?? tree, message: 'P3: a primer opens with its Test out box (::::test-out holding five questions, each with an :::answer{tests="…"}) before any heading' }];
	const problems = [];
	const [box] = boxes;
	for (const extra of boxes.slice(1)) problems.push({ node: extra, message: 'P3: a primer has one Test out box: remove this one' });
	if (firstNode !== box) problems.push({ node: box, message: 'P3: the Test out box is the first thing of the page, before any heading and any text' });
	const { questions } = questionsOf({ nodes: box.children });
	if (questions.length !== c_TestOutQuestions) problems.push({ node: box, message: `P3: the Test out box holds ${questions.length} numbered questions; it holds exactly ${c_TestOutQuestions}` });
	const covered = new Set();
	for (const question of questions) {
		const [answer] = question.answers;
		if (!answer) {
			problems.push({ node: question.node, message: 'P3: each Test out question is followed by an :::answer{tests="…"}: add one' });
			continue;
		}
		const tests = answerTests(answer);
		if (tests === null) problems.push({ node: answer, message: 'P3: the answer carries tests="<learn ids>", the objectives the question tests' });
		for (const id of tests ?? []) covered.add(id);
	}
	for (const id of learnIds) {
		if (!covered.has(id)) problems.push({ node: box, message: `P3: the Test out answers' tests do not cover the learn id "${id}": a reader who passes the box must know everything the page teaches` });
	}
	return problems;
}

/** style.md §8: on primers, concept pages and internals pages, a :::example stands before the bottom strip. */
export function exampleProblems(tree, kind) {
	if (!c_ExampleKinds.includes(kind)) return [];
	const strip = tree.children.findIndex((node) => node.type === 'heading' && node.depth === 2 && headingText(node).trim() === c_BottomStrips[kind][0]);
	const body = strip < 0 ? tree.children : tree.children.slice(0, strip);
	if (body.some((node) => findDirectives(node, 'example').length > 0)) return [];
	return [{ node: tree.children[strip] ?? tree, message: `a :::example stands before the bottom strip of ${withArticle(kind)} page: a worked example comes before the first exercise (style.md §8)` }];
}

/**
 * style.md §7.4: each step section of a tutorial (the sections after "## What you need", before the bottom strip) ends
 * with its ::checkpoint and the checkpoint's "You should now have" picture (::figure); that the picture is there is the
 * checkpoint plugin's to say (src/plugins/checkpoint.mjs), so a section that ends with a checkpoint alone passes here.
 * A tutorial that changes the engine (its tutorial file holds a patch) has no project to download and no checkpoints.
 */
export function checkpointProblems(tree, patchTutorial) {
	if (patchTutorial) return [];
	const found = sections(tree);
	const opening = found.findIndex((section) => section.title === c_TutorialOpening[1]);
	const strip = found.findIndex((section) => section.title === c_BottomStrips.tutorial[0]);
	if (opening < 0) return [];
	const problems = [];
	for (const section of found.slice(opening + 1, strip < 0 ? undefined : strip)) {
		const blocks = section.nodes.filter((node) => !isComment(node));
		const last = blocks.at(-1);
		const isCheckpoint = (node) => node?.type === 'leafDirective' && node.name === 'checkpoint';
		const isFigure = (node) => (node?.type === 'leafDirective' || node?.type === 'containerDirective') && node.name === 'figure';
		if (isCheckpoint(last) || (isFigure(last) && isCheckpoint(blocks.at(-2)))) continue;
		problems.push({ node: section.node, message: `the step section "## ${section.title}" of a tutorial ends with ::checkpoint{stage=…}, the project as it is after its last step, and then the checkpoint's "You should now have" picture, ::figure{id=…} (style.md §7.4)` });
	}
	return problems;
}

// What is not prose (style.md §2.2): code, display math, raw HTML and the front matter. Inline code and an inline formula
// count as one word each; a word runs between spaces, so a formula and the stop after it are one word.
const c_NotProse = new Set(['code', 'math', 'html', 'yaml']);
const c_Inline = new Set(['text', 'emphasis', 'strong', 'delete', 'link', 'linkReference', 'textDirective', 'footnoteReference']);

/** The prose words of nodes, as style.md §2.2 counts them: runs of characters between spaces, outside code and math. */
export function proseWords(nodes) {
	let prose = '';
	const visit = (node) => {
		if (c_NotProse.has(node.type)) return;
		if (node.type === 'inlineCode' || node.type === 'inlineMath') {
			prose += 'x';
			return;
		}
		if (node.type === 'text') prose += node.value;
		const block = !c_Inline.has(node.type);
		if (block) prose += ' ';
		for (const child of node.children ?? []) visit(child);
		if (block) prose += ' ';
	};
	nodes.forEach(visit);
	return prose.split(/\s+/).filter(Boolean).length;
}

/**
 * style.md §7.3: the section "## The problem and how engines solve it" of an internals page holds at most a fifth of
 * the page's prose words (its heading and the figure manifests' captions are not counted on either side).
 */
export function generalSectionProblems(tree, kind) {
	if (kind !== 'internals') return [];
	const section = sections(tree).find((candidate) => candidate.title === c_GeneralSection);
	if (!section) return [];
	const own = proseWords(section.nodes);
	const total = proseWords(tree.children.filter((node) => node.type !== 'heading'));
	if (own <= total * c_GeneralShare) return [];
	return [{ node: section.node, message: `the section "## ${c_GeneralSection}" holds ${own} of the page's ${total} prose words; it holds at most a fifth (style.md §7.3): keep it to the approaches and their costs, or link the concept page of the part that holds them` }];
}

/** The items of numbered lists anywhere in the tree whose first words say the step has no menu or button. */
function commandOnlySteps(tree) {
	const steps = [];
	const visit = (node) => {
		if (node.type === 'list' && node.ordered) {
			for (const item of node.children) {
				const first = item.children?.[0];
				const words = first?.type === 'paragraph' ? first.children.map((child) => child.value ?? (child.children ?? []).map((inner) => inner.value ?? '').join('')).join('') : '';
				if (words.trim().startsWith(c_CommandOnlyStep)) steps.push(item);
			}
		}
		for (const child of node.children ?? []) visit(child);
	};
	visit(tree);
	return steps;
}

/**
 * style.md §10: a page with a step that only a command can do has, in its Needs closure, the page that teaches running
 * a command on each of its tracks (make/commands on tracks G and B, editor/commands on track E).
 */
export function commandStepProblems(tree, pageId, tracks, outline) {
	const steps = commandOnlySteps(tree);
	if (!steps.length || !outline.rows.has(pageId)) return [];
	const closure = needsClosure(outline, pageId);
	const missing = [...new Set((tracks ?? []).map((letter) => c_CommandPages[letter]).filter((id) => id && id !== pageId && !closure.has(id)))];
	return missing.map((id) => {
		const letters = Object.entries(c_CommandPages).filter(([letter, page]) => page === id && tracks.includes(letter)).map(([letter]) => letter);
		return { node: steps[0], message: `a step that has no menu or button runs a command, and ${id}, which teaches running one, is not in the page's Needs closure (track${letters.length > 1 ? 's' : ''} ${letters.join(' and ')}; style.md §10): move the step to a later page, or start the tutorial where its result is done` };
	});
}

export function remarkBookStrips(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const book = { outline: context.outline, sidebar: context.sidebar, pages: index.pages, pin: context.settings.engine, release: context.settings.release };
			for (const problem of checkFrontmatter(page, book)) report(file, tree, `front matter: ${problem}`);
			for (const cycle of cyclesOf(index)) {
				if (cycle.includes(page.id)) report(file, tree, `front matter: O6: the Needs form a cycle: ${cycle.join(' → ')}`);
			}
			if (context.settings.release && page.data.status === 'draft') report(file, tree, 'front matter: a release build has no draft pages (status: draft)');
			if (page.error || pageRole(page.id, page.data) !== 'chapter') return;
			const learn = Array.isArray(page.data.learn) ? page.data.learn : [];
			const learnIds = learn.map((item) => item?.id).filter((id) => typeof id === 'string');
			const kind = page.data.kind;
			const problems = [...bottomStripProblems(tree, kind, learn.length), ...bodyHeadingsProblems(tree, kind), ...exampleProblems(tree, kind), ...generalSectionProblems(tree, kind)];
			if (kind !== 'reference') problems.push(...testsProblems(tree, learnIds));
			if (kind === 'primer') problems.push(...testOutProblems(tree, learnIds), ...bookUsesProblems(tree, page.id, context.outline));
			if (kind === 'tutorial') {
				const tutorial = readTutorial(context.settings, page.id);
				problems.push(...checkpointProblems(tree, Boolean(tutorial.patch)));
				if (context.settings.release) for (const message of stampProblems(context.settings, page.id)) problems.push({ node: tree, message });
			}
			problems.push(...commandStepProblems(tree, page.id, page.data.tracks, context.outline));
			for (const problem of problems) report(file, problem.node, problem.message);
		};
	};
}
