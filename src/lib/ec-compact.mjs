// An Expressive Code plugin (ec.config.mjs) that leaves out the token spans which only repeat the code's own colors.
// Expressive Code wraps every token in a span that names its color in each theme ("--0:#D6DEEB;--1:#403F53"); about
// half of the book's tokens are the plain text of their line, whose colors are the themes' code foreground, the color
// the code element itself has. Such a span inside no other colored span draws nothing its parent does not: its text is
// kept, the span goes. The page draws the same, in both themes and in print (src/styles/print.css prints the code
// foreground in the light theme's color, as the tokens print), and its code blocks are about a third lighter: they are
// on every chapter page and again in its part's print view (plan/site.md, budget row 9; rulings-13, R59).

/** The custom properties of an inline style ("--0:#abc;--1:#def") as a map, or null when it holds anything else. */
export function tokenStyle(style) {
	const result = new Map();
	for (const declaration of String(style).split(';')) {
		if (!declaration.trim()) continue;
		const colon = declaration.indexOf(':');
		const name = declaration.slice(0, colon).trim();
		if (colon < 0 || !name.startsWith('--')) return null;
		result.set(name, declaration.slice(colon + 1).trim().toLowerCase());
	}
	return result;
}

/** Whether a token's style is exactly the code foreground of every theme (`foregrounds[i]` for "--i"). */
export function isPlainToken(style, foregrounds) {
	const declarations = tokenStyle(style);
	if (!declarations || declarations.size !== foregrounds.length) return false;
	return foregrounds.every((color, index) => declarations.get(`--${index}`) === String(color).toLowerCase());
}

const isElement = (node) => node?.type === 'element';
const classesOf = (node) => (Array.isArray(node.properties?.className) ? node.properties.className : String(node.properties?.className ?? '').split(/\s+/).filter(Boolean));
// Expressive Code's own test for a span of token colors: no class, and a style that declares custom properties.
const isTokenSpan = (node) => isElement(node) && node.tagName === 'span' && classesOf(node).length === 0 && String(node.properties?.style ?? '').startsWith('--');

/**
 * Replaces, below `node`, every plain token span (isPlainToken) that stands inside no other token span by its
 * children; returns how many it replaced.
 */
export function unwrapPlainTokens(node, foregrounds, colored = false) {
	let unwrapped = 0;
	const children = node.children ?? [];
	for (let index = 0; index < children.length; index++) {
		const child = children[index];
		if (!isElement(child)) continue;
		if (!colored && isTokenSpan(child) && isPlainToken(child.properties.style, foregrounds)) {
			children.splice(index, 1, ...(child.children ?? []));
			unwrapped++;
			index--;
			continue;
		}
		unwrapped += unwrapPlainTokens(child, foregrounds, colored || isTokenSpan(child));
	}
	return unwrapped;
}

/** Finds the code of each line (`div.code`) below `node`. */
function codeElements(node, found = []) {
	if (isElement(node) && node.tagName === 'div' && classesOf(node).includes('code')) {
		found.push(node);
		return found;
	}
	for (const child of node.children ?? []) codeElements(child, found);
	return found;
}

export function pluginPlainTokens() {
	return {
		name: 'Plain tokens',
		hooks: {
			postprocessRenderedBlock: ({ renderData, styleVariants }) => {
				const foregrounds = styleVariants.map((variant) => variant.resolvedStyleSettings.get('codeForeground'));
				if (foregrounds.some((color) => typeof color !== 'string' || !color)) return;
				for (const code of codeElements(renderData.blockAst)) unwrapPlainTokens(code, foregrounds);
			},
		},
	};
}
