// The generated values (plan/pipelines.md §7.3): src/generated/reference/values.json, which tools/reference.py render
// writes from the engine at the pin, is a flat map of keys to numbers or strings ("commands.count": 151). A count the
// engine can change is never typed in prose (plan/style.md §13): a page writes :value{key="commands.count"}, and the
// values plugin (src/plugins/values.mjs) puts the number there.

import { readFileSync } from 'node:fs';

export const c_ValuesFile = 'src/generated/reference/values.json';

// The key that names the engine commit the values come from; values.json has no stamp (JSON has no comments), so this
// key is its stamp.
export const c_EngineKey = 'engine.commit';

/**
 * The record of values.json: `{ missing: true }`, `{ error }`, or `{ values: Map<key, number | string> }`. With `pin`
 * (engine.pin's commit), a file rendered from another commit, or naming none, is an error.
 */
export function loadValues(file, pin = null) {
	let text;
	try {
		text = readFileSync(file, 'utf8');
	} catch (error) {
		if (error.code === 'ENOENT') return { missing: true };
		throw error;
	}
	let data;
	try {
		data = JSON.parse(text);
	} catch (error) {
		return { error: `${c_ValuesFile} is not valid JSON: ${error.message}` };
	}
	if (!data || typeof data !== 'object' || Array.isArray(data)) return { error: `${c_ValuesFile} is not a JSON object of keys and values` };
	const values = new Map();
	for (const [key, value] of Object.entries(data)) {
		if (!key.trim()) return { error: `${c_ValuesFile} has an empty key` };
		const scalar = typeof value === 'string' || (typeof value === 'number' && Number.isFinite(value));
		if (!scalar) return { error: `${c_ValuesFile}: the value of "${key}" is ${JSON.stringify(value)}; every value is a number or a string` };
		values.set(key, value);
	}
	if (pin !== null && values.get(c_EngineKey) !== pin) {
		const named = values.has(c_EngineKey) ? `was rendered from engine ${values.get(c_EngineKey)}, but engine.pin names ${pin}` : `names no "${c_EngineKey}", the engine commit its values come from`;
		return { error: `${c_ValuesFile} ${named}` };
	}
	return { values };
}

/** How a value reads in a sentence: a number as JavaScript writes it (151, 0.6; 20000.0 reads 20000), a string as it is. */
export function valueText(value) {
	return String(value);
}

/** Up to `count` keys of the file that share the asked key's first segment ("commands." for "commands.cuont"). */
export function nearKeys(values, key, count = 5) {
	const head = key.split('.')[0];
	return [...values.keys()].filter((candidate) => candidate.split('.')[0] === head).sort().slice(0, count);
}
