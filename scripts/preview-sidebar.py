"""Preview only (PREVIEW.md): lists the written pages in src/sidebar.json in the outline's order, writes the tracks as
plan/tracks.md gives them, and writes src/generated/outline.json from the outline, so that a build of the pages written
so far passes the sidebar and outline checks. Run from the book's folder: python -I scripts/preview-sidebar.py ."""
import json
import os
import sys

root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
sys.path.insert(0, os.path.join(root, 'tools'))
from booklib import outline as outline_rules  # noqa: E402
import pages as pages_tool  # noqa: E402

# documents=False: the outline's rows and tracks, without the count sentences of plan/book.md, which the planner keeps.
outline = outline_rules.read(os.path.join(root, 'plan'), outline_rules.c_Book, documents=False)
with open(os.path.join(root, 'src', 'generated', 'outline.json'), 'w', encoding='utf-8', newline='\n') as handle:
    handle.write(pages_tool.outline_text(outline))
path = os.path.join(root, 'src', 'sidebar.json')
with open(path, encoding='utf-8') as handle:
    data = json.load(handle)
docs = os.path.join(root, 'src', 'content', 'docs')
for part in data['parts']:
    slug = part['slug']
    folder = os.path.join(docs, slug)
    written = {slug + '/' + name[:-3] for name in os.listdir(folder) if name.endswith('.md')} if os.path.isdir(folder) else set()
    rows = [row.id for row in next(candidate for candidate in outline.parts if candidate.slug == slug).pages]
    part['pages'] = ([slug + '/index'] if slug + '/index' in written else []) + [row for row in rows if row in written] \
        + ([slug + '/review'] if slug + '/review' in written else [])
    for extra in sorted(written - set(part['pages'])):
        print('preview-sidebar: %s is no row of the outline; the build will name it' % extra)
for key, letter in {'game': 'G', 'beginner': 'B', 'engine': 'E'}.items():
    track = data['tracks'][key]
    track['sequence'] = outline_rules.track_order(outline, letter)
    entries = outline.tracks[letter]
    track['sideSteps'] = [{'id': page_id, 'before': next((entry[0] for entry in entries[number + 1:] if not entry[1]), None)}
                          for number, (page_id, side_step, _) in enumerate(entries) if side_step]
lines = ['{', '\t"parts": [', ',\n'.join('\t\t' + json.dumps(part, ensure_ascii=False) for part in data['parts']), '\t],',
         json.dumps({'tracks': data['tracks']}, indent='\t', ensure_ascii=False)[1:-1].strip('\n'), '}']
with open(path, 'w', encoding='utf-8', newline='\n') as handle:
    handle.write('\n'.join(lines) + '\n')
print('preview-sidebar: %d pages listed' % sum(len(part['pages']) for part in data['parts']))
