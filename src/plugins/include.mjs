// include: "::include{file="commands.md"}" on a page of `reference` puts a generated table there (plan/site.md,
// "Generated reference"): src/generated/reference/<file>, which tools/reference.py render writes from the engine at the
// pin. The file is parsed with the book's own Markdown at the place of the directive, before the other plugins run, so
// its headings get anchors (the page index sees them too), its code blocks and links are drawn as the page's, and the
// print view holds it. Its content is wrapped in an element that search weighs less than written prose. A problem in
// the included text is reported at the directive's line, with the file and line it comes from. The file's stamp must
// name engine.pin's commit and the hash of its content, and it holds no raw HTML but the closed block around a schema
// (src/lib/reference.mjs).

import { directiveProblems } from '../lib/directives.mjs';
import { readIncluded } from '../lib/pages.mjs';
import { allowedHtml, readStamp, stampProblems } from '../lib/reference.mjs';
import { element, markOrigin, pageOf, report } from './shared.mjs';

export const c_IncludePart = 'reference';
export const c_ReferenceWeight = '0.3';

export function remarkBookInclude(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const { referenceDir } = context.settings;
			const visit = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type !== 'leafDirective' || node.name !== 'include') {
						visit(node);
						return;
					}
					// This plugin runs before the directives plugin (the included text is checked as the page's own), so it
					// checks its own directive's form here.
					const problems = directiveProblems(node);
					node.data ??= {};
					node.data.bookChecked = true;
					for (const problem of problems) report(file, node, problem);
					if (problems.length) return;
					if (page.part !== c_IncludePart) {
						report(file, node, `::include stands only on pages of the part "${c_IncludePart}", which hold the generated tables`);
						return;
					}
					const name = node.attributes?.file;
					if (!name) {
						report(file, node, '::include needs the file it reads: ::include{file="<table>.md"}, a file of src/generated/reference/');
						return;
					}
					if (!/^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)*\.md$/.test(name)) {
						report(file, node, `::include{file="${name}"}: name a file of src/generated/reference/ by its path there, in lowercase with "-" and "/", ending in .md`);
						return;
					}
					const included = readIncluded(referenceDir, name);
					if (!included) {
						report(file, node, `::include{file="${name}"}: src/generated/reference/${name} does not exist (tools/reference.py render writes the generated tables)`);
						return;
					}
					const where = `src/generated/reference/${name}`;
					// The stamp names the engine commit and the hash of the rest (src/lib/reference.mjs); it is not shown.
					const nodes = included.tree.children;
					const stamped = readStamp(included.text) !== null;
					if (stamped && nodes[0]?.type === 'html') nodes.shift();
					const nested = [];
					const html = [];
					const find = (current) => {
						if (current.type === 'leafDirective' && current.name === 'include') nested.push(current);
						if (current.type === 'html' && !allowedHtml(current.value)) html.push(current);
						for (const child of current.children ?? []) find(child);
					};
					nodes.forEach(find);
					markOrigin(nodes, where, node.position?.start);
					for (const problem of stampProblems(included.text, context.settings.engine.commit)) report(file, node, `${where}: ${problem}`);
					for (const inner of nested) report(file, inner, 'a generated table includes no other file');
					for (const raw of html) report(file, raw, 'a generated table holds no raw HTML but the closed <details> and <summary> around a schema: tools/reference.py escapes the engine\'s text, which never reaches a page as HTML');
					parent.children[position] = element('div', { className: ['book-reference'], dataPagefindWeight: c_ReferenceWeight }, nodes);
				});
			};
			visit(tree);
		};
	};
}
