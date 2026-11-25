// values: ":value{key="commands.count"}" in a sentence puts a value the engine's code decides there (plan/pipelines.md
// §7.3; plan/style.md §13): a count of commands, components or host functions, a quality preset's setting, an
// importer's version. The value comes from src/generated/reference/values.json, which tools/reference.py render writes
// at the pin, so the sentence follows the engine when the pin moves instead of keeping a number typed by hand. An
// unknown key fails the build at its line, as a missing or broken file does.

import { c_ValuesFile, loadValues, nearKeys, valueText } from '../lib/values.mjs';
import { element, pageOf, report, text, withoutTerms } from './shared.mjs';

/** Why a :value mark cannot stand inside this node, or null. */
function placeProblem(ancestor) {
	// A heading's anchor is made from its words: one that held a value would change its URL when the engine changes.
	if (ancestor.type === 'heading') return 'a heading holds no :value: its anchor would change with the engine; put the value in the text below it';
	return null;
}

export function remarkBookValues(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			if (!pageOf(file, index)) return;
			let record = null;
			const visit = (parent, ancestors) => {
				(parent.children ?? []).forEach((node, position) => {
					if (node.type !== 'textDirective' || node.name !== 'value') {
						visit(node, [...ancestors, node]);
						return;
					}
					// A bare ":value" is prose, as "a:b" is; its text in brackets and its attributes are checked by the
					// directives plugin, which reported them already.
					if (!node.children.length && Object.keys(node.attributes ?? {}).length === 0) return;
					if (node.data?.bookReported) return;
					const key = node.attributes?.key;
					if (key === undefined || !String(key).trim()) {
						report(file, node, ':value needs the key of the value it shows: :value{key="commands.count"}, a key of src/generated/reference/values.json');
						return;
					}
					for (const ancestor of ancestors) {
						const problem = placeProblem(ancestor);
						if (problem) {
							report(file, node, problem);
							return;
						}
					}
					record ??= loadValues(context.settings.valuesFile, context.settings.engine.commit);
					if (record.missing) {
						report(file, node, `:value{key="${key}"}: ${c_ValuesFile} does not exist; tools/reference.py render writes it from the engine at the pin`);
						return;
					}
					if (record.error) {
						report(file, node, `:value{key="${key}"}: ${record.error}; write it again with python -I tools/reference.py render`);
						return;
					}
					if (!record.values.has(key)) {
						const near = nearKeys(record.values, key);
						const hint = near.length ? `: did you mean ${near.map((candidate) => `"${candidate}"`).join(', ')}?` : '; tools/reference.py render lists the keys it writes';
						report(file, node, `:value{key="${key}"}: ${c_ValuesFile} has no key "${key}"${hint}`);
						return;
					}
					parent.children[position] = withoutTerms(element('span', { className: ['book-value'] }, [text(valueText(record.values.get(key)))]));
				});
			};
			visit(tree, []);
		};
	};
}
