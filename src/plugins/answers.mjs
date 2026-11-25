// answers: ":::answer" (or ":::answer[Worked solution]") hides an answer until the reader opens it. It is an HTML
// <details> element, so it works without scripts; the book's script opens every answer before the page prints. `tests`
// names the page's objectives (learn ids) the answer tests; the strips plugin checks it against the page's objectives.
// `solution` names the file of a worked solution that the book's checks run (plan/style.md §8), and the reader gets that
// file from the page: a sketch is shown in full in the answer, with its output; an editor exercise
// (tutorials/<page>/exercise-<n>.tutorial.json) and an engine exercise (tutorials/<page>/exercise-<n>.patch) are linked
// as their downloads, which tools/tutorials.py compile writes under public/downloads/solutions/ (plan/pipelines.md
// §6.3). A download not made yet is a draft note, and a release refuses it. An answer never sends the reader to the
// book's repository.

import { statSync } from 'node:fs';
import path from 'node:path';
import { c_Directives } from '../lib/directives.mjs';
import { formatBytes, publishedDownload } from '../lib/tutorials.mjs';
import { bookCodeOf, bookDownloadPath, sketchNameProblem } from './excerpts.mjs';
import { element, pageOf, report, takeDirectiveLabel, text, withoutTerms } from './shared.mjs';

export const c_AnswerAttributes = c_Directives.answer.attributes;

/** The learn ids an answer directive names in `tests` (separated by spaces or commas), or null without `tests`. */
export function answerTests(node) {
	const value = node.attributes?.tests;
	if (value === undefined || value === null) return null;
	return String(value).split(/[\s,]+/).filter(Boolean);
}

/**
 * What an answer's `solution` names, for a page (plan/style.md §8; plan/pipelines.md §4 and §6.2):
 * - `{ kind: 'sketch', name }`: solution="sketches/<page>-<name>.<ext>", a sketch the answer shows in full with its output;
 * - `{ kind: 'exercise', file, format }`: solution="tutorials/<page>/exercise-<n>.tutorial.json" (an editor exercise,
 *   downloaded as a ZIP) or "tutorials/<page>/exercise-<n>.patch" (an engine exercise, downloaded as the patch);
 * - `{ error }` for anything else.
 */
export function parseSolution(value, pageId) {
	const prefix = pageId.replace(/\//g, '-');
	if (value.startsWith('sketches/')) {
		const name = value.slice('sketches/'.length);
		const problem = sketchNameProblem(name, pageId, 'solution', value);
		return problem ? { error: problem } : { kind: 'sketch', name };
	}
	const exercise = /^tutorials\/(.+)\/exercise-([1-9][0-9]*)\.(tutorial\.json|patch)$/.exec(value);
	if (exercise) {
		if (exercise[1] !== pageId) return { error: `solution="${value}": the solution of an exercise is a file of its own page, tutorials/${pageId}/exercise-<n>.${exercise[3]}` };
		return { kind: 'exercise', file: value, format: exercise[3] === 'patch' ? 'patch' : 'zip' };
	}
	return { error: `solution="${value}" names the file of a worked solution: a sketch the answer shows with its output (solution="sketches/${prefix}-<name>.cpp"), an editor exercise (solution="tutorials/${pageId}/exercise-<n>.tutorial.json") or an engine exercise (solution="tutorials/${pageId}/exercise-<n>.patch") (style.md §8)` };
}

function fileExists(file) {
	try {
		return statSync(file).isFile();
	} catch (error) {
		if (error.code === 'ENOENT') return false;
		throw error;
	}
}

/** Whether `nodes` (or their children) hold the fence of the book's own code of this kind and file. */
function holdsCode(nodes, kind, name) {
	return nodes.some((node) => {
		const code = bookCodeOf(node);
		if (code?.kind === kind && code.file === name) return true;
		return holdsCode(node.children ?? [], kind, name);
	});
}

/** The words that link an exercise's download (`format` zip or patch), or say that it is not made yet. */
export function solutionDownloadNode(format, download) {
	if (!download) {
		return withoutTerms(element('p', { className: ['book-answer__pending'] }, [
			element('span', { className: ['book-draft-label'] }, [text('Draft')]),
			text(' The download of this solution is made when the book\'s checks run it against the engine.'),
		]));
	}
	const what = format === 'zip'
		? ` (ZIP, ${formatBytes(download.bytes)}): the editor commands of the solution and the files they copy, to run on your own project`
		: ` (patch, ${formatBytes(download.bytes)}): the solution's change to the engine's source, to apply with git apply`;
	return withoutTerms(element('p', { className: ['book-answer__download'] }, [
		element('a', { href: download.url, download: '' }, [text('Download the worked solution')]),
		text(what),
	]));
}

/**
 * Checks an answer's solution against the page and returns what the answer adds to its body (the download of an
 * exercise's solution, or a draft note), or null.
 */
function solutionPart(context, file, node, owner) {
	const value = String(node.attributes.solution);
	const solution = parseSolution(value, owner);
	if (solution.error) {
		report(file, node, solution.error);
		return null;
	}
	if (solution.kind === 'sketch') {
		// The fences are drawn already (the excerpts plugin runs first), and the excerpts plugin compares the sketch with
		// its file and fails when the file does not exist.
		if (!holdsCode(node.children, 'sketch', solution.name) || !holdsCode(node.children, 'output', solution.name)) {
			report(file, node, `solution="${value}": the answer shows the sketch in full, with its output: a fence with sketch="${solution.name}", then its \`\`\`text output-of="${solution.name}" fence (style.md §8)`);
		}
		return null;
	}
	const { settings } = context;
	if (!fileExists(path.join(settings.root, ...solution.file.split('/')))) {
		report(file, node, `solution="${value}": ${solution.file} does not exist`);
		return null;
	}
	const relative = bookDownloadPath(solution.file);
	const download = publishedDownload(settings, relative);
	if (!download && settings.release) report(file, node, `solution="${value}": a release has the download of every worked solution, and public/${relative} does not exist: write it with python -I tools/tutorials.py compile`);
	return solutionDownloadNode(solution.format, download);
}

export function remarkBookAnswers(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					visit(node);
					if (node.name !== 'answer') return;
					if (node.type !== 'containerDirective') {
						report(file, node, 'an answer is a block: write :::answer, the answer, then ::: on a line of its own');
						return;
					}
					// Attributes other than tests and solution are refused by the directives plugin (src/lib/directives.mjs).
					const attributes = node.attributes ?? {};
					if (attributes.tests !== undefined && answerTests(node).length === 0) report(file, node, ':::answer{tests=""} names no objective: write the learn ids it tests, such as tests="fixed-step"');
					const label = takeDirectiveLabel(node);
					if (node.children.length === 0) report(file, node, 'the answer is empty');
					let addition = null;
					if (attributes.solution !== undefined && !String(attributes.solution).trim()) report(file, node, ':::answer{solution=""} names no file');
					// A question copied onto a part's review page keeps the page it was written on (src/lib/partpages.mjs).
					else if (attributes.solution !== undefined && page) addition = solutionPart(context, file, node, node.data?.bookPageId ?? page.id);
					// A link inside <summary> would compete with opening the answer, so no :term mark stands in it.
					parent.children[position] = element('details', { className: ['book-answer'] }, [
						withoutTerms(element('summary', {}, label?.nodes ?? [text('Answer')])),
						element('div', { className: ['book-answer__body'] }, addition ? [...node.children, addition] : node.children),
					]);
				});
			};
			visit(tree);
		};
	};
}
