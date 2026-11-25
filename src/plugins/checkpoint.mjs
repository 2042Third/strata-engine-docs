// checkpoint: "::checkpoint{stage=4}" ends a section of a tutorial (plan/style.md §7.4): the project as it is at that
// point, to download, the editor commands that lead there (plan/pipelines.md §6.3, written by tools/tutorials.py into
// public/downloads/tutorials/<part>/<chapter>/stage-<stage>.zip and .commands.json), and a picture headed "You should
// now have": the ::figure on the line after the checkpoint, which the box takes in. The stage is one of the page's
// tutorial file (`stages[].step`) that ends in a state the reader can download (`endState`). A download the tools have
// not made yet shows as a draft note; a release build refuses it, and refuses a tutorial whose file does not exist.
// A how-to has no checkpoints: when it has a tutorial file, the end of its "## Result" offers the last stage's downloads
// in a box of the same kind, the how-to's end state (plan/site.md, "Directives"; style.md §7.5); no other stage's.

import { formatBytes, readTutorial, stageDownloads, tutorialPaths } from '../lib/tutorials.mjs';
import { element, pageOf, report, text, withoutTerms } from './shared.mjs';

export const c_CheckpointPictureHeading = 'You should now have';

/**
 * The checkpoint's box: its title, its downloads (`pending` when a download is not made yet) and its picture (the
 * figure the figures plugin drew), headed "You should now have".
 */
export function checkpointBox(step, downloads, { fromSample, pending, picture = null }) {
	const items = [];
	if (downloads.zip) {
		items.push(element('li', {}, [
			element('a', { href: downloads.zip.url, download: '' }, [text('Download the project as it is at this checkpoint')]),
			text(` (ZIP, ${formatBytes(downloads.zip.bytes)})`),
		]));
	}
	if (downloads.commands) {
		items.push(element('li', {}, [
			element('a', { href: downloads.commands.url, download: '' }, [text('Download the editor commands that lead here')]),
			text(` (JSON, ${formatBytes(downloads.commands.bytes)}), to run them on your own project`),
		]));
	}
	const children = [element('p', { className: ['book-checkpoint__title'] }, [text(`Checkpoint ${step}`)])];
	if (fromSample) children.push(element('p', {}, [text('This tutorial starts from a sample project, which you already have: the commands below bring it to this checkpoint.')]));
	if (items.length) children.push(element('ul', {}, items));
	if (pending) children.push(element('p', { className: ['book-checkpoint__pending'] }, [element('span', { className: ['book-draft-label'] }, [text('Draft')]), text(' The downloads of this checkpoint are made when the tutorial runs against the engine.')]));
	// The book's own words stay out of the search index and hold no :term mark; the picture's caption is the writer's
	// text, which may hold terms and links and is indexed like every caption.
	const box = [withoutTerms(element('div', { className: ['book-checkpoint__downloads'], dataPagefindIgnore: '' }, children))];
	if (picture) box.push(element('div', { className: ['book-checkpoint__picture'] }, [withoutTerms(element('p', { className: ['book-checkpoint__have'] }, [text(c_CheckpointPictureHeading)])), picture]));
	return element('div', { className: ['book-checkpoint'], role: 'group', ariaLabel: `Checkpoint ${step}` }, box);
}

/** The box at the end of a how-to's Result: the downloads of its tutorial file's last stage (`pending` when not made yet). */
export function resultBox(downloads, { fromSample, pending }) {
	const items = [];
	if (downloads.zip) {
		items.push(element('li', {}, [
			element('a', { href: downloads.zip.url, download: '' }, [text('Download the project as it is at the end')]),
			text(` (ZIP, ${formatBytes(downloads.zip.bytes)})`),
		]));
	}
	if (downloads.commands) {
		items.push(element('li', {}, [
			element('a', { href: downloads.commands.url, download: '' }, [text('Download the editor commands of the last step')]),
			text(` (JSON, ${formatBytes(downloads.commands.bytes)}), to run them on your own project`),
		]));
	}
	const children = [element('p', { className: ['book-checkpoint__title'] }, [text('The result')])];
	if (fromSample) children.push(element('p', {}, [text('This how-to starts from a sample project, which you already have: the commands below bring it to this result.')]));
	if (items.length) children.push(element('ul', {}, items));
	if (pending) children.push(element('p', { className: ['book-checkpoint__pending'] }, [element('span', { className: ['book-draft-label'] }, [text('Draft')]), text(' The downloads of the result are made when the how-to runs against the engine.')]));
	return element('div', { className: ['book-checkpoint', 'book-result'], role: 'group', ariaLabel: 'The result' }, [withoutTerms(element('div', { className: ['book-checkpoint__downloads'], dataPagefindIgnore: '' }, children))]);
}

function headingText(node) {
	return (node.children ?? []).map((child) => (child.type === 'text' || child.type === 'inlineCode' ? child.value : headingText(child))).join('');
}

/** Puts the how-to's end state at the end of its "## Result" (before the next section of its level or higher). */
function addResultBox(tree, file, settings, page) {
	const tutorial = readTutorial(settings, page.id);
	if (tutorial.missing || tutorial.patch || tutorial.error || tutorial.stages.size === 0) return;
	const children = tree.children;
	const result = children.findIndex((node) => node.type === 'heading' && node.depth === 2 && headingText(node).trim() === 'Result');
	if (result < 0) return; // the strips plugin reports a how-to without its Result
	let end = children.findIndex((node, position) => position > result && node.type === 'heading' && node.depth <= 2);
	if (end < 0) end = children.length;
	const step = Math.max(...tutorial.stages.keys());
	const fromSample = Boolean(tutorial.startsFrom && typeof tutorial.startsFrom === 'object' && 'sample' in tutorial.startsFrom);
	const downloads = stageDownloads(settings, page.id, step);
	const wanted = fromSample ? ['commands'] : ['zip', 'commands'];
	const missing = wanted.filter((name) => !downloads[name]);
	if (missing.length && settings.release) {
		const { relative } = tutorialPaths(settings, page.id);
		report(file, children[result], `a release has the download of a how-to's end state, the last stage of ${relative.tutorial}, and ${missing.map((name) => downloads.names[name]).join(' and ')} ${missing.length === 1 ? 'does' : 'do'} not exist: run the tutorial with python -I tools/tutorials.py run`);
	}
	children.splice(end, 0, resultBox(fromSample ? { zip: null, commands: downloads.commands } : downloads, { fromSample, pending: missing.length > 0 }));
}

/** Whether a node is a figure the figures plugin drew (one picture, not a slider). */
function isDrawnFigure(node) {
	const classes = node?.data?.hProperties?.className ?? [];
	return node?.type === 'bookElement' && node.data.hName === 'figure' && classes.includes('book-figure') && !classes.includes('book-compare');
}

/**
 * The checkpoint's picture at `next`, the node after it: `{ picture }`, `{ reported: true }` when the figures plugin
 * reported the figure already (it stays a directive), or `{ problem }`.
 */
function checkpointPicture(next, step) {
	if (isDrawnFigure(next)) return { picture: next };
	if ((next?.type === 'leafDirective' || next?.type === 'containerDirective') && next.name === 'figure') return { reported: true };
	const slider = next?.type === 'bookElement' && (next.data?.hProperties?.className ?? []).includes('book-compare');
	if (slider || ((next?.type === 'leafDirective' || next?.type === 'containerDirective') && next.name === 'compare')) {
		return { problem: `::checkpoint{stage=${step}} is followed by one picture of the project at this point, headed "${c_CheckpointPictureHeading}": a ::figure{id=…}, not a ::compare slider` };
	}
	return { problem: `::checkpoint{stage=${step}} is followed by its picture, headed "${c_CheckpointPictureHeading}": write ::figure{id=…} on the line after it, with a recipe of the page's figure manifest that shows the project at this point (style.md §7.4)` };
}

export function remarkBookCheckpoints(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const { settings } = context;
			const { relative } = tutorialPaths(settings, page.id);
			let tutorial = null;
			let previous = 0;
			const visit = (parent) => {
				const children = parent.children ?? [];
				for (let position = 0; position < children.length; position++) {
					const node = children[position];
					if (node.type !== 'leafDirective' || node.name !== 'checkpoint') {
						visit(node);
						continue;
					}
					if (page.data.kind !== 'tutorial') {
						report(file, node, `::checkpoint ends a section of a tutorial (style.md §7.4); this page's kind is ${page.data.kind ?? 'not given'}`);
						continue;
					}
					const value = node.attributes?.stage;
					if (value === undefined || !/^[1-9][0-9]*$/.test(String(value))) {
						report(file, node, '::checkpoint needs the number of the step it ends: ::checkpoint{stage=4}');
						continue;
					}
					const step = Number(value);
					if (step <= previous) report(file, node, `::checkpoint{stage=${step}} comes after the checkpoint of step ${previous}: the steps of a page's checkpoints go up`);
					previous = Math.max(previous, step);
					tutorial ??= readTutorial(settings, page.id);
					let fromSample = false;
					if (tutorial.error) report(file, node, tutorial.error);
					else if (tutorial.missing) {
						if (settings.release) report(file, node, `::checkpoint{stage=${step}}: the page's tutorial file ${relative.tutorial} does not exist, and a release has every tutorial's downloads`);
					} else if (tutorial.patch) {
						report(file, node, `::checkpoint{stage=${step}}: ${relative.tutorial} changes the engine with a patch, which has no project to download`);
					} else {
						fromSample = Boolean(tutorial.startsFrom && typeof tutorial.startsFrom === 'object' && 'sample' in tutorial.startsFrom);
						const stage = tutorial.stages.get(step);
						if (!stage) report(file, node, `::checkpoint{stage=${step}}: ${relative.tutorial} has no stage with "step": ${step} (its steps: ${[...tutorial.stages.keys()].join(', ') || 'none'})`);
						else if (stage.endState !== true && !fromSample) report(file, node, `::checkpoint{stage=${step}}: the stage is no end state in ${relative.tutorial} ("endState": true), so the tools publish no project to download after it`);
					}
					const downloads = stageDownloads(settings, page.id, step);
					const wanted = fromSample ? ['commands'] : ['zip', 'commands'];
					const missing = wanted.filter((name) => !downloads[name]);
					if (missing.length && settings.release) report(file, node, `::checkpoint{stage=${step}}: a release has the downloads of every checkpoint, and ${missing.map((name) => downloads.names[name]).join(' and ')} ${missing.length === 1 ? 'does' : 'do'} not exist: run the tutorial with python -I tools/tutorials.py run`);
					// The figures plugin ran before this one: the picture is a drawn figure now, which the box takes in.
					const found = checkpointPicture(children[position + 1], step);
					if (found.problem) report(file, node, found.problem);
					if (found.picture) children.splice(position + 1, 1);
					children[position] = checkpointBox(step, fromSample ? { zip: null, commands: downloads.commands } : downloads, { fromSample, pending: missing.length > 0, picture: found.picture ?? null });
				}
			};
			visit(tree);
			if (page.data.kind === 'how-to') addResultBox(tree, file, settings, page);
		};
	};
}
