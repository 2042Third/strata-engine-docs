#!/usr/bin/env python3
"""The book's figures (plan/pipelines.md §5): recipes in src/content/figures/<part>/<chapter>.json, published files and
their stamps in src/assets/figures/<part>/<chapter>/.

    python -I tools/figures.py check   [--release] --engine <clone> --dumps reference/_dumps/<pin> [--baselines <dir>]
    python <engine>/Tools/PerfLock.py --label docs-figures --wait 120 -- python -I tools/figures.py take
        --engine <clone> --build <bin> [--work <dir>] [--figures <glob>] [--kinds text,reference,tool] [--baselines <dir>]
        [--provisional]
    python <engine>/Tools/PerfLock.py --label docs-figures --wait 120 -- python -I tools/figures.py layout <name>
        --engine <clone> --build <bin> --window-size <width>x<height> [--work <dir>] [--provisional]
    python -I tools/figures.py compare --after <work dir> --output <dir> --engine <clone>
    python -I tools/figures.py publish --from <work dir> [--figures <glob>] [--accept]
    python -I tools/figures.py archive --tag <tag>
    python -I tools/figures.py fill    [pages...]
    python -I tools/figures.py list    [--waits]
    python -I tools/figures.py labs    [labs...]

The formats (the recipe of §5.2, taken.json, the published names, labs/CREDITS.md, text figures) are written out in
.tools/handover/figures-format.md and tools/schemas/; the published files follow plan/site.md "Pictures".

check     Offline (§5.8): every manifest against tools/schemas/figure-manifest.schema.json; duplicate ids; a manifest
          without its page; a ::figure or ::compare that names no recipe, a variant or a crop the recipe lacks, a
          ::compare of a recipe without two variants; a shot missing from Tools/LookDev/Shots.json at the pin or of
          another project, a shot or camera "editor", camera or crops beside a shot; a scene that does not exist at the
          pin (in the sample, among the scenes LookDevScene.json saves, Scenes/Main.stscene of basic3d, or the scenes a
          lab saves); an entityName that the scene document (or the script or template that makes the scene) does not
          hold exactly once; a debugView or quality preset outside the enums of viewport.capture, a custom quality field
          that Renderer.Quality lacks, a postProcess key that PostProcess lacks or a value outside its options or range
          (the dumps); renderer switches that viewport.capture's renderer parameter lacks (the commands dump) or values it
          refuses, renderer on a figure that is no scene figure, a setup step viewport.capture with renderer (a capture
          the take throws away); editorWindow.launcher beside project or what a project gives (scene, station, world,
          setup, play, files), an editor figure with neither; an absolute path among a program's arguments, or one that
          leaves the run folder of a program with files; a recipe that names the user's home folder; a live recipe
          without camera "scene", or with debugView, overlays, waitForAssets or renderer; sizes, crops
          and scales out of range; a variant that sets a field variants may not set, or fewer than two variants; a
          record pointer that the capture's result cannot hold; a caption number that is neither {stats.<name>} nor
          explained by numbers, a {stats.…} that record lacks; a render of parts image, indirect or light without
          publish; a relax pointer outside the complete set or without its reason; a waitsFor that names an addition the
          pin already has (§11); files on a figure that is no editor or scene figure, a file the book lacks or one
          outside tutorials/, larger than 10 MB, a target outside the project, a stage the page's tutorial lacks, an
          atStep past the figure's steps or (editor) beside play; a baseline without a shot, of another set, or (with --baselines) missing; a lab that is
          missing, holds keys other than the engine's, a command the dumps lack, an absolute path or a placeholder, or
          whose download differs from what labs writes; a published file that no recipe promises, of another format than
          its recipe's, or whose size or SHA-256 differs from taken.json; crops and pictures of the interface that are
          not lossless WebP; slider sides that differ in size or encoder settings; a text figure's fence that is not a
          ```text fence, carries src, sketch, output-of or pseudocode, names a variant its recipe lacks, or differs from
          its file; automation on a figure that is no editor figure, or an agent beside atStep; a runtime figure with a
          field the exported game cannot take (shot, camera, scene, station, quality, postProcess, play, ...) or seconds
          that are not whole; a live figure without play, or whose play ends before live.atFixedStep; blocked beside
          waitsFor; a figure its page does not place (::figure, :::figure, ::compare or a text fence), unless it waits
          or is blocked and its page places its standIn (a figure of the same manifest that a take or a writer makes)
          or noStandIn says why it shows none; a page that places a figure with a stand-in in the stand-in's place.
          Pictures not taken yet, placeholders and missing stamps are notes in a draft and errors with
          --release; so is a table the dumps lack. A figure no take makes at the pin (waitsFor, blocked) is a note in
          a release too: its page shows its stand-in (rulings-12, R55).
take      Takes the figures of the kinds asked for into the work folder (§5.4, §5.6): text (a command's result in a
          --no-gpu editor on a copy of the recipe's project, after §5.4's steps in its order: the scene opened again with
          force, world, a custom quality, the station's, shot's, recipe's and variant's steps, materials, anti-aliasing
          and postProcess, play; the project's settings are restored after each figure, and a figure whose scene cannot
          be opened again, or that bakes probes, gets a copy of its own; or a program of the build), reference (a
          sketch compiled as tools/sketches.py compiles it, run without a time limit, its PPM turned into a PNG) and tool
          figures taken by Playwright (node scripts/screenshot-page.mjs). scene figures run the same steps in a
          headless editor with the GPU (one per project copy; the look-dev project is made once per run by
          Tools/LookDev.py capture and copied), then two viewport.capture calls with every parameter explicit, whose
          results must be complete (§5.3) and the same picture: byte-identical, or no channel of a pixel off by more
          than 1 level with at most 0.5 per cent of the pixels differing (R57; the stamp records that difference); the
          first is the original, kept as the engine wrote it, and a pair that differs more is kept in
          nondeterministic/<picture>/. Every figure is taken twice and must give the same text or the same picture; a
          text's measured values (pointers of a command's answer, patterns of a program's output) are left out of the
          comparison and published as the first run gave them. editor figures run one editor each, in a window of
          editorWindow.windowSize pixels (default 1280 x 720) at UI scale 1 on a copy of the recipe's layout (whose first
          line names the window it was made for; another window fails the figure): the project copy is made in a --no-gpu
          editor, then StrataEditor --window-size --ui-scale 1 --layout --no-automation --project --commands
          --quit-after-commands runs a script of the scene opened, the station's, the recipe's and the variant's setup,
          play, editorWindow.steps (entityName becomes entity.find, whose first match the step gets: check sees that
          there is one), editor.wait of 120 frames, editor.showPanel of editorWindow.panel when the recipe pictures one
          panel, and editor.screenshot of that panel or the whole window, which must be settled (a whole window must have
          the window's size). No automation, so that the window shows none; taken once, since the Console's times and
          live statistics differ between takes. A recipe's files (book files under tutorials/, or {"stage": n}: what
          stages 1 to n of the page's tutorial copy) go into the project copy before the editor opens it (a scene
          figure's editor opens it again), or before the step atStep: a scene figure's setup step, or of editorWindow.steps,
          before which the window closes and a new one opens the copy for the rest. A
          recipe's renderer switches go to both captures of a scene figure (the result must echo them) and into its
          stamp. editorWindow.launcher starts the window without a project: the launcher. A program's text figure with
          files runs each run in a fresh run folder with the files staged in it, as its working directory. Neutral
          paths: an editor figure's folder (its copy in Projects/<name>, its layout, script and screenshot in Editor/)
          and a program's run folder are shown to the program as the root of a drive of its own (subst, removed after
          the run), the layout copy makes the New Project dialog suggest that drive's Projects folder, and a figure whose
          recipe, stamp, text or editor's log names the work folder or the user's home fails. An editor
          figure's automation (true) leaves --no-automation out: the window serves on the free loopback port it picks,
          its token only in a private session folder the tool never reads; automation {client} also starts StrataCLI mcp
          in that folder, which names itself client in initialize and sends the figure's steps (the frames waited for
          first) through strata_call, connected at the screenshot. live figures: three takes, each a fresh copy (made
          in a --no-gpu editor) in an editor in a window that serves automation, the recipe's quality preset set and
          the players' options reset, the Game view at the recipe's size, the figure's steps, play.start paused,
          viewport.capture {live, camera scene, atFixedStep, frames} started before play's steps, its answer; the three
          must give the same fixed steps and camera; the first take's last frame is the original, every take's frames
          stay in live/<picture>/. runtime figures: a copy in a headless editor, the setup steps (which save what they
          change), script.build when the copy has Scripts/CMakeLists.txt, project.export into export/<picture>, then the
          exported game --windowed --resolution --seconds --quality --save-directory <new folder> --screenshot, which
          must exit 0 with a screenshot of the resolution. Figures with blocked (no take makes them at the pin) are
          skipped like those with waitsFor.
          --provisional takes with a build that is not the pin's, to try recipes before the pin has what they need: the
          commit check is skipped and said so, figures that wait for an addition of §11 are taken (and say that their
          waitsFor stays), and taken-pending.json records it, so that publish refuses the take. Figures with waitsFor, variants with baseline (the
          "before" pictures), tool figures the owner takes and text figures of the look-dev project are skipped and
          reported. Reference figures need a C++ compiler and the clone's
          glm at the pinned commit; without them the run stops before it starts (exit 2). On Windows the C runtime's
          newline translation of a sketch's output is undone.
          It writes shots/, crops/ (cut at the picture's own pixels), results/, text/, log/ and taken-pending.json, and
          keeps the folder until the next run. Each line of its report starts with the recipe's file and line.
layout    Makes layouts/<name>.ini: an editor in a window of --window-size pixels at UI scale 1, on a new basic3d project,
          lays out its panels as it does on a first start, and the file it keeps them in is written with a first line
          that names the window and the engine commit. A layout is for that window only (take checks it); the editor
          lays out its panels again when its layout version changes, so layouts are made again when the pin moves.
compare   Lays out the originals the current stamps name as a LookDev capture set beside a new take and runs the
          engine's Tools/LookDev.py compare on the two; the output must be outside both repositories' tracked trees.
publish   Encodes each original of a take as its recipe says (node scripts/encode-figures.mjs: lossy AVIF quality 80,
          90 for both sides of a ::compare and for pictures of the editor and of tools that say lossy, chroma 4:4:4,
          effort 4; lossless WebP, effort 4; crops always, and pictures of the editor and of tools unless they say
          lossy, lossless), copies every PNG original into originals/<sha256>.png, and writes the files,
          <figure>[-<variant>].result.json and taken.json, for the pictures and crops a page places (it skips the
          others). A retake with the stamp's original keeps the file, and its stamp takes the retake's pin, build,
          machine and recorded values (restamped); a different one is compared with the committed file (encode-figures.mjs diff): at or below site.md's thresholds
          (mean 0.5, largest 16 x 16 block mean 4, of 255) the file stays and the stamp records the engine commit it was
          checked at; above them it is a candidate, left in <work>/candidates/ for the photographer, and --accept puts the
          candidates --figures names in place. It fails when an original is missing or differs from taken-pending.json,
          and stops (exit 2) when node or sharp is missing.
archive   Packs every original a stamp names into release/strata-engine-docs-originals-<tag>.tar and writes its SHA-256
          beside it (<archive>.sha256, as sha256sum writes it); fails when an original is missing or the archive would be
          larger than 1 GB. The integrator moves both files out of the clone (rulings-6, R26).
fill      Copies text figures into the fences that show them: ```text capture="<figure>" (variant="<name>"); a fence of
          another form is left as it is and reported.
list      Every figure and its state per published file: taken, placeholder, missing, waiting, blocked; --waits groups the
          waiting figures by the engine addition they wait for (the request list of §11).
labs      Writes public/downloads/labs/<name>.zip: <name>.json, the files of labs/<name>/ and, when labs/CREDITS.md
          credits one of them, a CREDITS.md with those entries.

Every message names the file and the line. Only the standard library is used (encoding calls node). Exit codes: 0 all
is well, 1 problems were found, 2 usage or environment errors (and every preflight check of §1.4).
"""

import argparse
import fnmatch
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import blocks, editor, images, jsonpos, jsonschema, markdown, repo  # noqa: E402
from booklib import steps as script_steps  # noqa: E402
from booklib import tutorials as tutorial_files  # noqa: E402

c_Tools = os.path.dirname(os.path.abspath(__file__))
c_Schema = os.path.join(c_Tools, 'schemas', 'figure-manifest.schema.json')
c_TakenSchema = os.path.join(c_Tools, 'schemas', 'taken.schema.json')
c_Encoder = os.path.join(os.path.dirname(c_Tools), 'scripts', 'encode-figures.mjs')
c_Screenshot = os.path.join(os.path.dirname(c_Tools), 'scripts', 'screenshot-page.mjs')

c_Kinds = ('scene', 'live', 'editor', 'runtime', 'text', 'reference', 'tool', 'diagram')
c_TakeKinds = ('scene', 'live', 'editor', 'runtime', 'text', 'reference', 'tool')
c_Renders = ('scene', 'live', 'runtime', 'reference')
c_Interface = ('editor', 'tool')
# Editor figures (plan/pipelines.md §5.4): the window when the recipe names none, the frames waited before the picture
# (thumbnails, the launcher's fade), and the first line of a layout file, which names the window it was made for.
c_EditorWindow = [1280, 720]
c_EditorMinimumWindow = (640, 360)  # EditorApplication.cpp's smallest --window-size
c_EditorSettleFrames = 120
c_LayoutHeader = re.compile(r'^; Strata editor layout for a window of (?P<width>[0-9]+)x(?P<height>[0-9]+) pixels')
c_LayoutName = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
# A recipe's files (plan/pipelines.md §5.2): what the tutorials give the reader, sources and small assets, copied into
# editor and scene figures' project copies; a stage may also copy a sample's asset at the pin (tools/tutorials.py).
c_ProjectFileLimit = 10 * 1000 * 1000
c_FilesKinds = ('editor', 'scene')
c_SampleAsset = re.compile(r'^Samples/[^/]+/Assets/[^/].*[^/]$')
c_PublishParts = ('image', 'indirect', 'light')
c_EditorKinds = ('scene', 'live', 'editor', 'runtime', 'text')
c_OtherFenceKinds = ('src', 'sketch', 'output-of')  # with the flag pseudocode: the book's other kinds of fence
c_VariantRefused = ('id', 'kind', 'project', 'shot', 'camera', 'size', 'crops', 'publish', 'variants')
c_LiveRefused = ('debugView', 'overlays', 'waitForAssets', 'renderer')
# Live figures (plan/pipelines.md §5.4): three takes in fresh editors on fresh copies, in a window this much larger than
# the Game view's size, so that the Game view's panel holds the size it presents.
c_LiveTakes = 3
c_LiveWindowMargin = (480, 360)
c_LiveWindowLargest = (3840, 2100)
# The quality presets of a recipe as the section Renderer.Quality names them (its Preset enum).
c_PresetNames = {'low': 'Low', 'medium': 'Medium', 'high': 'High', 'ultra': 'Ultra'}
# Runtime figures (§5.4): the exported game draws what the project saved, with the runtime's options, so a recipe sets
# nothing a capture or an edit-mode view sets; its setup steps change the copy and save what they change.
c_RuntimeRefused = ('shot', 'camera', 'scene', 'station', 'world', 'quality', 'antiAliasing', 'postProcess', 'materials', 'debugView', 'renderer',
                    'overlays', 'waitForAssets', 'play', 'live', 'editorWindow')
# What an editor figure's automation is (§5.5, "Automation figures"): served (true), or served with an agent that
# names itself, whose MCP client sends the figure's steps.
c_AutomationKinds = ('editor',)
# A figure of the launcher (editorWindow.launcher) opens no project, so it takes none of what a project gives.
c_LauncherRefused = ('scene', 'station', 'world', 'setup', 'play', 'files')
# What a take never shows (plan/pipelines.md §5.4, "Neutral paths"): editor windows and programs given files see their
# folder as the root of a drive of its own, mapped by subst for the run and removed after it; the first free letter of
# these is taken, so that pictures name the same drive from one take to the next.
c_DriveLetters = 'SPQRTUVWXYZ'
c_NeutralEditor = 'Editor'  # the tool's own files on the drive: layout, script, screenshot, recent projects, script builds
c_NeutralProjects = 'Projects'  # the project copy, and the folder the New Project and Open Sample dialogs suggest
c_LauncherSettings = re.compile(r'(?ms)^\[StrataLauncher\]\[Settings\]\n.*?(?=^\[|\Z)')
c_Baselines = ('v0.6.0', 'v0.7.0', 'v0.7.0-medium')
c_DefaultSize = (1920, 1080)
# Shots.json's crops carry no scale; LookDev.py enlarges them 4 times (CROP_SCALE), and a page enlarges a shot's crop as
# much (.tools/handover/figures-format.md).
c_ShotCropScale = 4
c_LossyQuality = 80
c_CompareQuality = 90
# A picture of the editor or of a tool that is mostly the engine's image may be published lossy, at this quality: its
# interface text stays as sharp as the lossless file's at 1:1 (plan/critique/rulings-13.md, R59).
c_InterfaceQuality = 90
c_Effort = 4
c_MeanThreshold = 0.5
c_BlockThreshold = 4.0
c_ArchiveLimit = 1000 ** 3
c_TakenFile = 'taken.json'
c_Republish = 'take and publish it again (figures.py take, then figures.py publish)'
c_LabKeys = script_steps.c_ScriptKeys
# No tool changes the person's preferences (plan/pipelines.md §2), so no step of a recipe or a lab may.
c_RefusedCommands = script_steps.c_RefusedCommands
c_Placeholder = re.compile(r'@[A-Z][A-Z0-9_]*@')
c_AbsolutePath = re.compile(r'^(?:[A-Za-z]:[\\/]|/|\\\\)')
c_Stats = re.compile(r'\{stats\.([A-Za-z0-9]+)(?:\.([A-Za-z0-9]+))?\}')
c_Number = re.compile(r'(?<![\w.{])\d+(?:[.,]\d+)?(?![\w}])')
# A leaf directive ::figure{…}, or a container's opening line :::figure{…}, whose body adds to the caption.
c_Directive = re.compile(r'^\s*:::?(figure|compare)(?:\{([^}]*)\})?\s*$')
c_Complete = {
    '/pendingAssets': {'equals': 0}, '/texturesBelowWanted': {'equals': 0}, '/stalePoses': {'equals': 0},
    '/pendingTextGlyphs': {'equals': 0}, '/ui/pendingGlyphs': {'equals': 0}, '/localShadowViewsPending': {'equals': 0},
    '/reflectionProbesPending': {'equals': 0}, '/renderStats/deferredInstanceBytes': {'equals': 0},
    '/preExposureSettled': {'equals': True}, '/globalIlluminationSettled': {'equals': True},
    '/previewLighting': {'equals': False}, '/temporalFrames': {'min': 8}, '/debugView/shadows/complete': {'equals': True},
}
# Two captures of one recipe are the same picture when no channel of any pixel differs by more than c_PairLevels and at
# most c_PairPercent per cent of the pixels differ at all (R57, plan/pipelines.md §5.6): output dither and the last bit
# of a filter are no fault of the recipe.
c_PairLevels = 1
c_PairPercent = 0.5
# The anti-aliasing modes as component values of PostProcess (Tools/LookDev.py:49-54, plan/pipelines.md §5.4 step 4).
c_AntiAliasing = {
    'taa': {'AntiAliasing': True, 'AntiAliasingMethod': 'TAA'}, 'fxaa': {'AntiAliasing': True, 'AntiAliasingMethod': 'FXAA'},
    'morph': {'AntiAliasing': True, 'AntiAliasingMethod': 'Morphological'}, 'off': {'AntiAliasing': False},
}
# world {"loadAll": true}: every cell within WorldData::c_SupportedExtent (Strata/src/Strata/World/WorldAsset.h:89).
c_WorldRegion = {'min': [-20000, -20000], 'max': [20000, 20000]}
c_DebugViewsTier2 = ('specular', 'diffuse', 'clusters', 'culled', 'wireframe')
c_Additions = {
    'tier 1: capture complete': 'the result of viewport.capture reports complete, incomplete and screenSpaceReflectionsPending',
    'tier 1: command details': 'editor.commands reports each command\'s mayDefer, waitsForAssets and results',
    'tier 1: asset types': 'the command asset.types',
    'tier 1: window size': 'the editor option --window-size <width>x<height>',
    'tier 2: editor screenshot': 'the command editor.screenshot {path, overwrite, panel}',
    'tier 2: renderer switches': 'viewport.capture {renderer: {…}}',
}
for _view in c_DebugViewsTier2:
    c_Additions['tier 2: debug view %s' % _view] = 'the debug view %s of viewport.capture' % _view
c_Tier3 = re.compile(r'^tier 3: (?P<what>[^;]{3,}); (?P<why>.{3,})$')


class UsageError(Exception):
    """A usage or environment problem: exit code 2."""


# A figure that could not be taken (exit code 1). The command steps of booklib.steps raise the same error, so that a
# failed step fails its figure.
TakeError = script_steps.StepError


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read_bytes(path):
    with open(path, 'rb') as file:
        return file.read()


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    repo.write_text(path, json.dumps(data, indent='\t', ensure_ascii=False) + '\n')


# ---------------------------------------------------------------------------------------------------------------------
# Recipes.

class Recipe:
    """One figure of a manifest: its page, its entry, and where its fields stand in the manifest."""

    def __init__(self, page, manifest, entry, index, lines):
        self.page = page
        self.manifest = manifest  # the manifest's path relative to the book
        self.entry = entry
        self.index = index
        self.lines = lines
        self.id = entry['id']
        self.kind = entry['kind']
        self.part = page.split('/')[0]

    def where(self, *path):
        pointer = '/figures/%d' % self.index + ''.join('/' + jsonpos.escape(part) for part in path)
        return '%s:%d' % (self.manifest, jsonpos.line_of(self.lines, pointer))

    def variant_names(self):
        variants = self.entry.get('variants')
        return list(variants) if isinstance(variants, dict) and variants else []

    def variants(self):
        """[(variant name or None, the recipe's fields with the variant's over them)]."""
        names = self.variant_names()
        if not names:
            return [(None, dict(self.entry))]
        result = []
        for name in names:
            fields = {key: value for key, value in self.entry.items() if key != 'variants'}
            fields.update(self.entry['variants'][name])
            result.append((name, fields))
        return result

    def stem(self, variant=None):
        return self.id + ('-' + variant if variant else '')

    def publish(self, fields=None):
        """'lossy', 'lossless', 'text' or 'svg': how the recipe's pictures are published."""
        if self.kind == 'text':
            return 'text'
        if self.kind == 'diagram':
            return 'svg'
        if self.kind in c_Interface:
            return 'lossy' if self.entry.get('publish') == 'lossy' else 'lossless'
        return (fields or self.entry).get('publish', 'lossy')

    def extension(self):
        return {'lossy': '.avif', 'lossless': '.webp', 'text': '.txt', 'svg': '.svg'}[self.publish()]


def recipe_crops(recipe, shot):
    """[{name, rect, scale}] of a recipe: its own, or its shot's (with LookDev's scale)."""
    if recipe.entry.get('crops'):
        return recipe.entry['crops']
    if shot:
        return [{'name': crop.get('Name'), 'rect': crop.get('Rect'), 'scale': c_ShotCropScale} for crop in shot.get('Crops', [])
                if isinstance(crop, dict) and crop.get('Name') and crop.get('Rect')]
    return []


def promised_files(recipe, shot, placed=None):
    """{file name: (variant, crop name or None)} of every file a recipe promises (pictures, crops, text). Given placed,
    what its page places (placed_pictures), a picture of a variant and a crop are promised only where the page places
    them: a reader never meets the others, so they are not published (plan/pipelines.md §5.7). Text figures (shown by
    fences) and drawings are promised whole."""
    files = {}
    for variant, _ in recipe.variants():
        whole = placed is None or recipe.kind in ('text', 'diagram')
        if whole or picture_placed(placed, recipe.id, variant, None):
            files[recipe.stem(variant) + recipe.extension()] = (variant, None)
        if recipe.kind not in ('text', 'diagram'):
            for crop in recipe_crops(recipe, shot):
                if whole or picture_placed(placed, recipe.id, variant, crop['name']):
                    files['%s-%s.webp' % (recipe.stem(variant), crop['name'])] = (variant, crop['name'])
    return files


def placed_pictures(layout, recipes):
    """{page: {(figure, variant or None, crop name, '' for a ::figure{… crop} that names none, or None for the whole
    picture)}}: the pictures each page places, a ::compare its two sides (before and after, else the recipe's first two
    variants)."""
    variants = {(recipe.page, recipe.id): recipe.variant_names() for recipe in recipes}
    placed = {}
    for page, path in layout.pages():
        for _, name, attributes in directives(repo.read_text(path)):
            figure = attributes.get('id')
            if not figure:
                continue
            found = placed.setdefault(page, set())
            if name == 'compare':
                names = variants.get((page, figure), [])
                for side, index in (('before', 0), ('after', 1)):
                    found.add((figure, attributes.get(side) or (names[index] if len(names) > index else None), None))
            else:
                found.add((figure, attributes.get('variant'), (attributes.get('crop') or '') if 'crop' in attributes else None))
    return placed


def picture_placed(placed, figure, variant, crop):
    """Whether a page's placements (placed_pictures) hold the picture (crop None) or the crop; a ::figure{… crop} without a
    name places a recipe's one crop (check refuses it on a recipe of several)."""
    if crop is None:
        return (figure, variant, None) in placed
    return (figure, variant, crop) in placed or (figure, variant, '') in placed


def unplaced_files(recipe, shot, placed):
    """{file name: (what it is, the directive that would place it)} of the pictures and crops of a recipe that its page
    does not place, with the capture results of those pictures."""
    files = promised_files(recipe, shot, placed)
    found = {}
    for name, (variant, crop) in promised_files(recipe, shot).items():
        if name in files:
            continue
        directive = '::figure{id=%s%s%s}' % (recipe.id, ' variant=%s' % variant if variant else '', ' crop=%s' % crop if crop else '')
        if crop:
            what = ('crop', 'the crop %s of %s' % (crop, recipe.id))
        else:
            what = ('picture', 'the variant %s of %s' % (variant, recipe.id) if variant else 'the picture of %s' % recipe.id)
            found[name.rsplit('.', 1)[0] + '.result.json'] = (what, directive)
        found[name] = (what, directive)
    return found


def manifest_files(layout):
    result = []
    for folder, directories, files in os.walk(layout.figures):
        directories.sort()
        for name in sorted(files):
            if name.endswith('.json'):
                path = os.path.join(folder, name)
                result.append((os.path.relpath(path, layout.figures).replace(os.sep, '/')[:-5], path))
    return result


def load_schema(path):
    with open(path, encoding='utf-8') as file:
        return jsonschema.Validator(json.load(file))


def load_recipes(layout, report=None, invalid=None):
    """[Recipe] of every manifest that is valid JSON and passes the schema; problems go to report, and the pages of the
    manifests that fail go to the set invalid."""
    validator = load_schema(c_Schema)
    recipes = []
    for page, path in manifest_files(layout):
        where = layout.relative(path)
        try:
            data, lines = jsonpos.load(repo.read_text(path))
        except jsonpos.JsonError as error:
            if report:
                report.error('%s:%d' % (where, error.line), 'not valid JSON (%s): correct the manifest' % error)
            if invalid is not None:
                invalid.add(page)
            continue
        problems = validator.problems(data)
        if problems:
            if report:
                for pointer, message in problems:
                    report.error('%s:%d' % (where, jsonpos.line_of(lines, pointer)), '%s %s: write the recipe as plan/pipelines.md §5.2 '
                                 'gives its fields and forms' % (pointer or 'the manifest', message))
            if invalid is not None:
                invalid.add(page)
            continue
        for index, entry in enumerate(data['figures']):
            recipes.append(Recipe(page, where, entry, index, lines))
    return recipes


# ---------------------------------------------------------------------------------------------------------------------
# Published files and their stamps.

class Taken:
    """A chapter's taken.json: {file name: record}, with the lines of its records."""

    def __init__(self, layout, page):
        self.folder = os.path.join(layout.pictures, *page.split('/'))
        self.path = os.path.join(self.folder, c_TakenFile)
        self.relative = layout.relative(self.path)
        self.files = {}
        self.lines = {}
        self.problem = None
        if os.path.isfile(self.path):
            try:
                data, self.lines = jsonpos.load(repo.read_text(self.path))
            except jsonpos.JsonError as error:
                self.problem = ('%s:%d' % (self.relative, error.line), 'not valid JSON (%s): taken.json is written by figures.py publish' % error)
                return
            problems = load_schema(c_TakenSchema).problems(data)
            if problems:
                pointer, message = problems[0]
                self.problem = ('%s:%d' % (self.relative, jsonpos.line_of(self.lines, pointer)), '%s %s (taken.json is written by figures.py '
                                'publish: publish the figure again)' % (pointer or 'the file', message))
                return
            self.files = data['files']

    def where(self, name):
        return '%s:%d' % (self.relative, jsonpos.line_of(self.lines, '/files/' + jsonpos.escape(name)))

    def save(self):
        write_json(self.path, {'files': {name: self.files[name] for name in sorted(self.files)}})


def compare_ids(layout):
    """{page: {recipe ids used by a ::compare}}: both sides of a slider are encoded at quality 90."""
    used = {}
    for page, path in layout.pages():
        for line, name, attributes in directives(repo.read_text(path)):
            if name == 'compare' and attributes.get('id'):
                used.setdefault(page, set()).add(attributes['id'])
    return used


def encoder_settings(recipe, fields, crop, in_compare):
    """The settings encode-figures.mjs is called with: (publish, quality or None)."""
    if crop or recipe.publish(fields) == 'lossless':
        return 'lossless', None
    if recipe.kind in c_Interface:
        return 'lossy', c_InterfaceQuality
    return 'lossy', c_CompareQuality if in_compare else c_LossyQuality


# ---------------------------------------------------------------------------------------------------------------------
# Pages.

def directives(text):
    """(line, name, attributes) of every ::figure and ::compare of a page, outside fences."""
    found = []
    inside = set()
    for fence in markdown.fences(text):
        inside.update(range(fence.open_line, (fence.close_line or fence.open_line) + 1))
    for number, line in enumerate(text.split('\n'), 1):
        if number in inside:
            continue
        match = c_Directive.match(line)
        if match:
            found.append((number, match.group(1), blocks.parse_attributes(match.group(2) or '')))
    return found


def capture_fences(text):
    """(fence, figure id, variant) of every ```text capture="…" fence of a page."""
    return [(fence, fence.attributes['capture'], fence.attributes.get('variant')) for fence in markdown.fences(text) if 'capture' in fence.attributes]


def capture_form_problem(fence, figure):
    """What is wrong with the form of a fence that shows a text figure, or None: it is a ```text fence, and capture is
    a kind of fence of its own, never with src, sketch, output-of or pseudocode (the build refuses the same)."""
    if fence.lang != 'text':
        return 'capture="%s" is on a ```%s fence: show a text figure in a ```text fence' % (figure, fence.lang)
    others = [name for name in c_OtherFenceKinds if name in fence.attributes] + (['pseudocode'] if 'pseudocode' in fence.flags else [])
    if others:
        return 'capture="%s" is a kind of fence of its own: remove %s' % (figure, ', '.join(others))
    return None


# ---------------------------------------------------------------------------------------------------------------------
# The engine at the pin, as check reads it.

def json_lines(engine, pin, path):
    lines = engine.read(pin, path)
    if lines is None:
        return None
    try:
        return json.loads('\n'.join(lines))
    except ValueError:
        raise UsageError('%s at %s is not valid JSON' % (path, pin[:12]))


def scene_entities(document):
    """[entity name] of a scene document."""
    names = []
    for entity in (document.get('Scene') or {}).get('Entities') or []:
        name = ((entity.get('Components') or {}).get('Name') or {}).get('Name') if isinstance(entity, dict) else None
        if isinstance(name, str):
            names.append(name)
    return names


def script_scenes(steps):
    """{scene path: [entity names]} a command script saves (scene.new ... entity.create ... scene.saveAs)."""
    scenes = {}
    current = []
    for step in steps if isinstance(steps, list) else []:
        if not isinstance(step, dict):
            continue
        parameters = step.get('parameters') or {}
        if step.get('command') == 'scene.new':
            current = []
        elif step.get('command') == 'entity.create' and isinstance(parameters.get('name'), str):
            current.append(parameters['name'])
        elif step.get('command') in ('scene.saveAs', 'scene.save') and isinstance(parameters.get('path'), str):
            scenes[parameters['path']] = list(current)
    return scenes


class Pin:
    """What check reads of the engine at the pin, each file once."""

    def __init__(self, engine, pin):
        self.engine = engine
        self.pin = pin
        self.cache = {}

    def once(self, key, function):
        if key not in self.cache:
            self.cache[key] = function()
        return self.cache[key]

    def shots(self):
        def read():
            data = json_lines(self.engine, self.pin, 'Tools/LookDev/Shots.json') or {}
            shots = {shot.get('Name'): shot for shot in data.get('Shots', []) if isinstance(shot, dict)}
            return data.get('Projects', {}), shots
        return self.once('shots', read)

    def lookdev_scenes(self):
        return self.once('lookdev', lambda: script_scenes(json_lines(self.engine, self.pin, 'Tools/LookDev/LookDevScene.json') or []))

    def basic3d(self):
        def read():
            lines = self.engine.read(self.pin, 'StrataEditor/src/Editor/ProjectTemplates.cpp') or []
            return re.findall(r'CreateEntity\("([^"]+)"\)', '\n'.join(lines))
        return self.once('basic3d', read)

    def sample_scene(self, sample, scene):
        key = ('sample', sample, scene)
        def read():
            return json_lines(self.engine, self.pin, 'Samples/%s/Assets/%s' % (sample, scene))
        return self.once(key, read)

    def sample_start(self, sample):
        def read():
            project = json_lines(self.engine, self.pin, 'Samples/%s/%s.stproj' % (sample, sample)) or {}
            handle = (project.get('Project') or {}).get('StartScene')
            listing = subprocess.run(['git', '-C', self.engine.path, 'ls-tree', '-r', '--name-only', self.pin, 'Samples/%s/Assets' % sample],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8', 'replace').splitlines()
            for path in listing:
                if path.endswith('.stscene.meta'):
                    meta = json_lines(self.engine, self.pin, path) or {}
                    if meta.get('Handle') == handle:
                        return path[len('Samples/%s/Assets/' % sample):-len('.meta')]
            return None
        return self.once(('start', sample), read)

    def result_keys(self):
        """{top-level keys of viewport.capture's result} and {keys of renderStats}, read from the source at the pin."""
        def read():
            capture = initializer_keys(self.engine.read(self.pin, 'StrataEditor/src/Editor/EditorViewportCommands.cpp') or [], r'nlohmann::json result = \{')
            stats = initializer_keys(self.engine.read(self.pin, 'StrataEditor/src/Editor/EditorStateCommands.cpp') or [], r'\{ "quality", RendererQuality::ToSectionValue', element=True)
            if capture:
                capture.update({'notice', 'path'})
            return capture, stats
        return self.once('keys', read)


def initializer_keys(lines, start_pattern, element=False):
    """The keys of the elements { "key", … } of a C++ initializer list of nlohmann::json: the list opens with the "{"
    the pattern ends with, or (element) the pattern matches its first element and the list opens just before it. Empty
    when the pattern matches nothing."""
    text = '\n'.join(lines)
    match = re.search(start_pattern, text)
    if not match:
        return set()
    index = text.rfind('{', 0, match.start()) if element else match.end() - 1
    depth = 0
    keys = set()
    expect_key = False
    while 0 <= index < len(text):
        char = text[index]
        if char == '"':
            end = index + 1
            while end < len(text) and text[end] != '"':
                end += 2 if text[end] == '\\' else 1
            key = text[index + 1:end]
            if depth == 2 and expect_key and re.match(r'^[A-Za-z][A-Za-z0-9]*$', key) and text[end + 1:end + 40].lstrip().startswith(','):
                keys.add(key)
            expect_key = False
            index = end + 1
            continue
        if text.startswith('//', index):
            index = text.find('\n', index)
            continue
        if char == '{':
            depth += 1
            expect_key = depth == 2
        elif char == '}':
            depth -= 1
            if depth == 0:
                break
        elif not char.isspace():
            expect_key = False
        index += 1
    return keys


class Dumps:
    """The dumps of reference.py (plan/pipelines.md §7.2) check reads: commands, settings and components."""

    def __init__(self, folder, pin):
        self.folder = folder
        self.missing = []
        self.commands = self.load('commands', pin)
        self.settings = self.load('settings', pin)
        self.components = self.load('components', pin)

    def load(self, name, pin):
        path = os.path.join(self.folder, name + '.json') if self.folder else None
        if not path or not os.path.isfile(path):
            self.missing.append(name + '.json')
            return None
        try:
            with open(path, encoding='utf-8') as file:
                data = json.load(file)
        except ValueError as error:
            raise UsageError('%s is not valid JSON: %s' % (path, error))
        if not isinstance(data, dict) or data.get('pin') != pin:
            raise UsageError('%s holds the dump of pin %s, but engine.pin names %s: run python -I tools/reference.py dump at the pin'
                             % (path, data.get('pin') if isinstance(data, dict) else None, pin))
        return data.get('result')

    def command(self, name):
        if self.commands is None:
            return None
        for entry in self.commands.get('commands', []):
            if entry.get('name') == name:
                return entry
        return False

    def capture_enum(self, parameter):
        entry = self.command('viewport.capture')
        if not entry:
            return None
        return (((entry.get('parameters') or {}).get('properties') or {}).get(parameter) or {}).get('enum')

    def quality_fields(self):
        if self.settings is None:
            return None
        for section in self.settings.get('sections', []):
            if section.get('id') == 'Renderer.Quality':
                return set(((section.get('schema') or {}).get('properties') or {}))
        return set()

    def component(self, name):
        if self.components is None:
            return None
        for component in self.components.get('components', []):
            if component.get('name') == name:
                return {item.get('Name'): item for item in component.get('properties', [])}
        return {}


# ---------------------------------------------------------------------------------------------------------------------
# check.

class Report:
    def __init__(self, release=False):
        self.release = release
        self.errors = []
        self.notes = []

    def error(self, where, message):
        self.errors.append((where, message))

    def note(self, where, message):
        """A note in a draft, an error with --release."""
        (self.errors if self.release else self.notes).append((where, message))

    def unmade(self, where, message):
        """A note in a release too: what no take makes at the final pin (it waits for an addition the release lacks, or
        is blocked) keeps its waitsFor or blocked, and its page shows its stand-in (plan/critique/rulings-12.md, R55)."""
        self.notes.append((where, message))


def addition_present(name, dumps, pin_data):
    """True or False when the pin has the engine addition, None when the dumps needed are missing."""
    if name == 'tier 1: capture complete':
        capture, _ = pin_data.result_keys()
        return 'complete' in capture if capture else None
    if name == 'tier 1: command details':
        if dumps.commands is None:
            return None
        return any('mayDefer' in entry for entry in dumps.commands.get('commands', []))
    if name == 'tier 1: asset types':
        found = dumps.command('asset.types')
        return None if found is None else bool(found)
    if name == 'tier 1: window size':
        lines = pin_data.engine.read(pin_data.pin, 'StrataEditor/src/EditorApplication.cpp') or []
        return any('"--window-size"' in line for line in lines)
    if name == 'tier 2: editor screenshot':
        found = dumps.command('editor.screenshot')
        return None if found is None else bool(found)
    if name == 'tier 2: renderer switches':
        entry = dumps.command('viewport.capture')
        if entry is None:
            return None
        return 'renderer' in (((entry or {}).get('parameters') or {}).get('properties') or {})
    if name.startswith('tier 2: debug view '):
        views = dumps.capture_enum('debugView')
        return None if views is None else name[len('tier 2: debug view '):] in views
    return None


def check_steps(recipe, steps, path, entities, dumps, report, created):
    """Command steps of a recipe: entityName held once by the scene (or made by an earlier step)."""
    for number, step in enumerate(steps):
        where = recipe.where(*(path + (number,)))
        if dumps.commands is not None and dumps.command(step['command']) is False:
            report.error(where, 'the command %s is not one the editor at the pin registers (commands dump): use a command of '
                         'editor.commands at the pin' % step['command'])
        # A value outside a parameter's enum fails only when the editor runs the step (a panel named "Asset", not "AssetInspector").
        entry = dumps.command(step['command']) if dumps.commands is not None else None
        properties = ((entry or {}).get('parameters') or {}).get('properties') or {}
        for name, value in (step.get('parameters') or {}).items():
            allowed = (properties.get(name) or {}).get('enum')
            if allowed and isinstance(value, str) and value not in allowed:
                report.error(where, 'the parameter %s of %s is "%s", which the editor at the pin refuses: use one of %s'
                             % (name, step['command'], value, ', '.join(str(option) for option in allowed)))
        if step['command'] in c_RefusedCommands:
            report.error(where, '%s changes the person\'s preferences, which no tool does (pipelines.md §2): use a project setting' % step['command'])
        if step['command'] == 'viewport.capture' and 'renderer' in (step.get('parameters') or {}):
            report.error(where, 'a setup step\'s viewport.capture takes a picture of its own, which the take throws away: set renderer on the recipe '
                         'or the variant, which the figure\'s own captures take')
        if step.get('command') == 'entity.create' and isinstance((step.get('parameters') or {}).get('name'), str):
            created.append(step['parameters']['name'])
        if 'entityName' in step and entities is not None:
            count = entities.count(step['entityName']) + created.count(step['entityName'])
            if count != 1:
                report.error(where, 'entityName "%s" names %d entities of the scene at the pin; it must name exactly one (name '
                             'the entity uniquely, or choose another)' % (step['entityName'], count))


def figure_scene(recipe, fields, shot, projects, pin_data, labs):
    """(scene path or None, [entity names] or None, problem or None) of a figure's variant."""
    project = fields.get('project') or {}
    scene = fields.get('scene') or (shot or {}).get('Scene')
    if shot and not scene:
        scene = (projects.get(shot.get('Project')) or {}).get('Scene')
    if 'sample' in project:
        sample = project['sample']
        if not scene:
            scene = pin_data.sample_start(sample)
            if not scene:
                return None, None, None
        document = pin_data.sample_scene(sample, scene)
        if document is None:
            return scene, None, 'the scene %s does not exist in Samples/%s/Assets at the pin' % (scene, sample)
        return scene, scene_entities(document), None
    if project.get('lookdev'):
        scenes = pin_data.lookdev_scenes()
        if not scene:
            scene = 'Scenes/LookDev.stscene'
        if scene not in scenes:
            return scene, None, 'the look-dev script (Tools/LookDev/LookDevScene.json) saves no scene %s; it saves %s' % (scene, ', '.join(sorted(scenes)))
        return scene, scenes[scene], None
    if 'lab' in project:
        scenes = labs.get(project['lab'], {}).get('scenes', {})
        template = project.get('template')
        if scene and scene in scenes:
            return scene, scenes[scene], None
        if template == 'basic3d' and scene in (None, 'Scenes/Main.stscene'):
            return 'Scenes/Main.stscene', pin_data.basic3d() + scenes.get('Scenes/Main.stscene', []), None
        if scene:
            return scene, None, 'the lab %s saves no scene %s%s' % (project['lab'], scene, ' (basic3d has Scenes/Main.stscene)' if template == 'basic3d' else '')
        return None, None, None
    if project.get('template') == 'basic3d':
        if scene and scene != 'Scenes/Main.stscene':
            return scene, None, 'a basic3d project has one scene, Scenes/Main.stscene, not %s' % scene
        return 'Scenes/Main.stscene', pin_data.basic3d(), None
    if project.get('template') == 'empty':
        if scene:
            return scene, None, 'an empty project has no scene %s; a lab makes scenes ({"lab": …, "template": "empty"})' % scene
        return None, None, None
    return scene, None, None


def check_recipe(recipe, layout, pin_data, dumps, labs, baselines, report):
    entry = recipe.entry
    projects, shots = pin_data.shots()
    shot = None
    if recipe.kind == 'diagram' and recipe.variant_names():
        report.error(recipe.where('variants'), 'a drawing has no variants: draw two figures')
    if 'shot' in entry:
        shot = shots.get(entry['shot'])
        if shot is None:
            report.error(recipe.where('shot'), 'Tools/LookDev/Shots.json at the pin has no shot "%s": choose one of its shots' % entry['shot'])
        else:
            if shot.get('Camera') == 'editor':
                report.error(recipe.where('shot'), 'the shot %s uses the editor camera, whose state copies leave out: choose a shot with '
                             'its own camera' % entry['shot'])
            project = (projects.get(shot.get('Project')) or {})
            want = entry.get('project') or {}
            matches = (('sample' in want and project.get('Sample') == want['sample']) or (want.get('template') and 'lab' not in want
                       and project.get('Template') == want['template']) or (want.get('lookdev') and project.get('Script') == 'LookDevScene.json'))
            if not matches:
                report.error(recipe.where('project'), 'the shot %s belongs to the project %s of Shots.json, not to %s: use the shot\'s project, or another shot' % (
                    entry['shot'], shot.get('Project'), json.dumps(want)))
        for field in ('camera', 'crops'):
            if field in entry:
                report.error(recipe.where(field), 'a recipe with a shot takes the shot\'s %s: remove %s' % ('camera' if field == 'camera' else 'crops', field))
    launcher = any((fields.get('editorWindow') or {}).get('launcher') for _, fields in recipe.variants())
    if launcher:
        if 'project' in entry:
            report.error(recipe.where('project'), 'the launcher shows while no project is open: remove project, or editorWindow.launcher')
        for field in c_LauncherRefused:
            for variant, fields in recipe.variants():
                if field in fields:
                    report.error(recipe.where(*field_place(recipe, variant, field)), 'a figure of the launcher opens no project, so it takes no %s: '
                                 'remove %s' % (field, field))
                    break
    elif recipe.kind in c_EditorKinds and recipe.kind != 'text' and 'project' not in entry:
        report.error(recipe.where(), 'a %s figure runs an editor on a project: add project%s' % (
            recipe.kind, ' (or editorWindow.launcher: true for the launcher)' if recipe.kind == 'editor' else ''))
    home = home_folders()
    for path, value in walk_strings(entry):
        found = named_folder(value, home)
        if found:
            report.error(recipe.where(*path), 'the recipe names the user\'s home folder (%s): a picture never shows a path of the machine; name a '
                         'folder of the project or the run folder' % found)
            break
    if recipe.kind == 'text':
        text = entry.get('text') or any('text' in fields for _, fields in recipe.variants())
        if not text:
            report.error(recipe.where(), 'a text figure needs text: a command (with keep) or a program')
    if recipe.kind == 'scene' and 'camera' not in entry and 'shot' not in entry:
        report.error(recipe.where(), 'a scene figure needs a camera or a shot: add one of them')
    if entry.get('camera') == 'editor':
        report.error(recipe.where('camera'), 'camera "editor" is refused: use "scene" or position, target and fov')
    if recipe.kind == 'live' and entry.get('camera') != 'scene':
        report.error(recipe.where(), 'a live figure captures what the Game view shows: set camera "scene"')
    if recipe.kind == 'live' and 'live' not in entry:
        report.error(recipe.where(), 'a live figure needs live {atFixedStep, frames}')
    if recipe.kind == 'runtime' and 'runtime' not in entry:
        report.error(recipe.where(), 'a runtime figure needs runtime {resolution, seconds, quality}')
    if recipe.kind == 'editor' and 'editorWindow' not in entry:
        report.error(recipe.where(), 'an editor figure needs editorWindow {layout, steps}')
    if recipe.kind == 'reference' and 'reference' not in entry:
        report.error(recipe.where(), 'a reference figure needs reference {sketch}')
    if recipe.kind == 'tool':
        if 'takenBy' not in entry:
            report.error(recipe.where(), 'a tool figure says who takes it: takenBy "playwright" or "owner"')
        elif entry['takenBy'] == 'playwright' and 'url' not in entry:
            report.error(recipe.where('takenBy'), 'a tool figure taken by Playwright names its page: add url')
    refused = set()
    for variant, fields in recipe.variants():
        automation = fields.get('automation')
        if automation is not None and recipe.kind not in c_AutomationKinds:
            report.error(recipe.where(*field_place(recipe, variant, 'automation')), 'automation is an editor figure\'s (the window\'s status bar, '
                         'Activity panel and Scene view show it): remove it, or make the figure an editor figure')
        elif isinstance(automation, dict) and any(isinstance(item, dict) and 'atStep' in item for item in fields.get('files') or []):
            report.error(recipe.where(*field_place(recipe, variant, 'files')), 'an agent (automation.client) drives one window, and atStep closes '
                         'it: copy the files before the editor opens the project')
        if fields.get('blocked') and fields.get('waitsFor'):
            report.error(recipe.where(*field_place(recipe, variant, 'blocked')), 'a figure either waits for an addition (waitsFor) or is blocked '
                         'at the pin with its reason (blocked): keep one')
        if recipe.kind == 'runtime':
            for field in c_RuntimeRefused:
                if field in fields and field not in refused:
                    refused.add(field)
                    report.error(recipe.where(*field_place(recipe, variant, field)), 'a runtime figure is the exported game, which draws what the '
                                 'project saved with the runtime\'s options: it takes no %s; change the copy in setup steps and save it (scene.save), '
                                 'and set runtime {resolution, seconds, quality}' % field)
            seconds = (fields.get('runtime') or {}).get('seconds')
            if isinstance(seconds, (int, float)) and not isinstance(seconds, bool) and seconds != int(seconds):
                report.error(recipe.where(*field_place(recipe, variant, 'runtime')), 'runtime.seconds is %s: the runtime at the pin counts whole '
                             'seconds of game time (--seconds <count>): give a whole number' % seconds)
        if recipe.kind == 'live' and 'live' in fields:
            play = fields.get('play')
            if not play:
                report.error(recipe.where(*field_place(recipe, variant, 'live')), 'a live figure plays its game to the fixed step it captures: add '
                             'play {steps} (and input)')
            elif play['steps'] < fields['live']['atFixedStep']:
                report.error(recipe.where(*field_place(recipe, variant, 'play')), 'play runs %d fixed steps, fewer than live.atFixedStep %d: the '
                             'capture would wait for a step that never runs; run at least that many' % (play['steps'], fields['live']['atFixedStep']))
    stand_in, without = entry.get('standIn'), entry.get('noStandIn')
    if (stand_in or without) and not recipe_unmade(recipe):
        report.error(recipe.where('standIn' if stand_in else 'noStandIn'), 'only a figure that waits for an addition (waitsFor) or that no take '
                     'can make at the pin (blocked) has a stand-in: remove %s' % ('standIn' if stand_in else 'noStandIn'))
    if stand_in and without:
        report.error(recipe.where('noStandIn'), 'a figure has a stand-in (standIn) or says why the page shows none (noStandIn), not both: keep one')
    if stand_in == recipe.id:
        report.error(recipe.where('standIn'), 'a figure cannot stand in for itself: name another figure of the manifest')
    if 'station' in entry and (entry.get('project') or {}).get('sample') != 'Showcase':
        report.error(recipe.where('station'), 'stations are the Showcase\'s times of day: use station with {"sample": "Showcase"}')
    if 'publish' not in entry and recipe.part in c_PublishParts and recipe.kind in c_Renders:
        report.error(recipe.where(), 'a render of the part %s says how it is published: add publish "lossy" or "lossless" (dither, '
                     'grain and noise are what lossy encoding smears)' % recipe.part)
    if recipe.kind in c_Interface and entry.get('publish') not in (None, 'lossy'):
        report.error(recipe.where('publish'), 'pictures of the editor and of tools are lossless unless they say publish "lossy": remove publish')
    for variant, fields in sorted((entry.get('variants') or {}).items()) if recipe.kind in c_Interface else []:
        if isinstance(fields, dict) and 'publish' in fields:
            report.error(recipe.where('variants', variant, 'publish'), 'a picture of the editor or of a tool says publish for the whole recipe: remove it from the variant')
    for crop_number, crop in enumerate(entry.get('crops') or []):
        x0, y0, x1, y1 = crop['rect']
        if not all(0 <= value <= 1 for value in crop['rect']) or x0 >= x1 or y0 >= y1:
            report.error(recipe.where('crops', crop_number, 'rect'), 'a crop is [x0, y0, x1, y1] of the picture, from 0 to 1, with x0 < x1 '
                         'and y0 < y1')
        if not 1 <= crop['scale'] <= 8:
            report.error(recipe.where('crops', crop_number, 'scale'), 'scale is the whole factor the page enlarges the crop by, 1 to 8')
    names = [crop['name'] for crop in entry.get('crops') or []]
    for duplicate in sorted({name for name in names if names.count(name) > 1}):
        report.error(recipe.where('crops'), 'the crop name "%s" is used twice: give each crop its own name' % duplicate)
    variants = entry.get('variants')
    if variants is not None and len(variants) < 2:
        report.error(recipe.where('variants'), 'a recipe with variants has at least two (a slider shows two of them)')
    for name, fields in (variants or {}).items():
        for field in c_VariantRefused:
            if field in fields:
                report.error(recipe.where('variants', name, field), 'a variant may not set %s: both sides of a slider share it (set it '
                             'on the recipe)' % field)
        if 'baseline' in fields and 'shot' not in entry:
            report.error(recipe.where('variants', name, 'baseline'), 'a "before" picture is the baseline set\'s file of a shot: the recipe needs shot')
        if 'baseline' in fields and baselines and 'shot' in entry:
            size = entry.get('size', c_DefaultSize)
            aa = fields.get('antiAliasing', entry.get('antiAliasing', 'taa'))
            path = os.path.join(baselines, fields['baseline'], 'shots', '%s-%dx%d-%s.png' % (entry['shot'], size[0], size[1], aa))
            if not os.path.isfile(path):
                report.error(recipe.where('variants', name, 'baseline'), 'the baseline set %s has no %s: choose a shot, size and '
                             'anti-aliasing the set was taken with' % (fields['baseline'], os.path.relpath(path, baselines)))
    # Per variant: the fields that combine.
    capture_keys, stats_keys = pin_data.result_keys() if recipe.kind == 'scene' else (set(), set())
    for variant, fields in recipe.variants():
        place = ('variants', variant) if variant else ()
        if recipe.kind == 'live':
            for field in c_LiveRefused:
                if field in fields:
                    report.error(recipe.where(*(place + (field,))) if variant and field in entry['variants'][variant] else recipe.where(field),
                                 'live captures refuse %s: they return what the Game view presented, so remove it' % field)
        if 'debugView' in fields:
            views = dumps.capture_enum('debugView')
            if views is not None and fields['debugView'] not in views:
                report.error(recipe.where(*field_place(recipe, variant, 'debugView')), 'debugView "%s" is not a debug view of viewport.capture at the '
                             'pin: use one of %s' % (fields['debugView'], ', '.join(views)))
        if fields.get('renderer'):
            check_renderer(recipe, variant, fields, dumps, report)
        quality = fields.get('quality')
        if isinstance(quality, str):
            presets = dumps.capture_enum('quality')
            if presets is not None and quality not in presets:
                report.error(recipe.where(*field_place(recipe, variant, 'quality')), 'quality "%s" is not a preset of viewport.capture: '
                             'use one of %s' % (quality, ', '.join(presets)))
        elif isinstance(quality, dict):
            known = dumps.quality_fields()
            for field in quality['custom']:
                if known is not None and field not in known:
                    report.error(recipe.where(*field_place(recipe, variant, 'quality')), 'Renderer.Quality has no field %s at the pin: use '
                                 'a field of its section in the settings dump' % field)
        post = fields.get('postProcess') or {}
        properties = dumps.component('PostProcess') if post else None
        for key, value in post.items():
            if properties is None:
                break
            prop = properties.get(key)
            where = recipe.where(*field_place(recipe, variant, 'postProcess'))
            if prop is None:
                report.error(where, 'PostProcess has no property %s at the pin: use a property of the components dump' % key)
                continue
            options = prop.get('Options')
            if options and value not in options:
                report.error(where, 'PostProcess.%s is one of %s, not %s: choose one of them' % (key, ', '.join(map(str, options)), json.dumps(value)))
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if prop.get('Min') is not None and value < prop['Min'] or prop.get('Max') is not None and value > prop['Max']:
                    report.error(where, 'PostProcess.%s runs from %s to %s, not %s: choose a value in that range' % (key, prop.get('Min'), prop.get('Max'), value))
        for name, pointer in (fields.get('record') or {}).items():
            first = pointer.split('/')[1] if pointer.count('/') >= 1 else ''
            if capture_keys and first not in capture_keys:
                report.error(recipe.where(*field_place(recipe, variant, 'record')), 'record %s: %s is no field of viewport.capture\'s result at the '
                             'pin: point record at one of %s' % (name, pointer, ', '.join(sorted(capture_keys))))
            elif capture_keys and first == 'renderStats' and stats_keys and pointer.count('/') >= 2 and pointer.split('/')[2] not in stats_keys:
                report.error(recipe.where(*field_place(recipe, variant, 'record')), 'record %s: renderStats has no field %s at the pin: '
                             'point record at a field it has' % (name, pointer.split('/')[2]))
        for pointer, reason in (fields.get('relax') or {}).items():
            if pointer not in c_Complete:
                report.error(recipe.where(*field_place(recipe, variant, 'relax')), 'relax %s: only the pointers of the complete set can be relaxed (%s)'
                             % (pointer, ', '.join(sorted(c_Complete))))
            if not reason.strip():
                report.error(recipe.where(*field_place(recipe, variant, 'relax')), 'relax %s needs its reason: say why the figure may be taken without it' % pointer)
        # Captions: numbers come from the recorded values or are explained.
        caption = fields.get('caption', '')
        for match in c_Stats.finditer(caption):
            first, second = match.group(1), match.group(2)
            if second:
                variant_fields = dict(recipe.variants()).get(first) if first in recipe.variant_names() else None
                if variant_fields is None:
                    report.error(recipe.where(*field_place(recipe, variant, 'caption')), '%s names the variant %s, which the recipe lacks: '
                                 'correct the caption' % (match.group(0), first))
                elif second not in (variant_fields.get('record') or {}):
                    report.error(recipe.where(*field_place(recipe, variant, 'caption')), '%s: the variant %s records no %s: add it to that '
                                 'variant\'s record' % (match.group(0), first, second))
            elif first not in (fields.get('record') or {}):
                report.error(recipe.where(*field_place(recipe, variant, 'caption')), '%s: the recipe records no %s (add it to record)' % (match.group(0), first))
        if c_Number.search(c_Stats.sub('', caption)) and not fields.get('numbers'):
            report.error(recipe.where(*field_place(recipe, variant, 'caption')), 'the caption writes a number that is not {stats.…}: say where it '
                         'comes from in numbers, or record it')
        # The scene and its entities.
        scene, entities, problem = figure_scene(recipe, fields, shot, projects, pin_data, labs)
        if problem:
            report.error(recipe.where(*field_place(recipe, variant, 'scene')), problem + ': name a scene the project has at the pin')
        created = []
        for steps_name in ('setup',):
            if steps_name in entry:
                check_steps(recipe, entry[steps_name], (steps_name,), entities, dumps, report, created)
            if variant and steps_name in entry['variants'][variant]:
                check_steps(recipe, entry['variants'][variant][steps_name], ('variants', variant, steps_name), entities, dumps, report, created)
        if 'editorWindow' in fields:
            check_steps(recipe, fields['editorWindow']['steps'], field_place(recipe, variant, 'editorWindow') + ('steps',), entities, dumps, report, created)
            window_place = recipe.where(*field_place(recipe, variant, 'editorWindow'))
            layout_name = fields['editorWindow']['layout']
            layout_file = os.path.join(layout.root, *layout_name.split('/'))
            size = window_size(fields)
            if size[0] < c_EditorMinimumWindow[0]:
                report.error(window_place, 'windowSize %dx%d: the editor\'s window is at least %dx%d' % (tuple(size) + c_EditorMinimumWindow))
            if not os.path.isfile(layout_file) and (fields.get('blocked') or fields.get('waitsFor')):
                # No take makes the figure at the pin, so none needs its layout: a note in a release too (plan/pipelines.md §5.8).
                report.notes.append((window_place, 'the layout %s does not exist yet: the figure %s, so no take needs it at the pin' % (
                    layout_name, 'is blocked' if fields.get('blocked') else 'waits for %s' % fields['waitsFor'])))
            elif not os.path.isfile(layout_file):
                report.note(window_place, 'the layout %s does not exist yet' % layout_name)
            else:
                made = layout_window(layout_file)
                if made and made != size:
                    report.error(window_place, 'the layout %s was made for a window of %dx%d, not %dx%d: make a layout for that window (figures.py '
                                 'layout), or set windowSize to %dx%d' % ((layout_name,) + tuple(made) + tuple(size) + tuple(made)))
            panel = fields['editorWindow'].get('panel')
            shown = dumps.command('editor.showPanel') if dumps.commands is not None else None
            panels = (((shown or {}).get('parameters') or {}).get('properties') or {}).get('panel', {}).get('enum') if shown else None
            if panel and panels and panel not in panels:
                report.error(window_place, 'the panel %s is not one editor.showPanel names at the pin (%s): picture one of those, or the whole window'
                             % (panel, ', '.join(panels)))
        if 'files' in fields:
            check_project_files(recipe, variant, fields, layout, pin_data, report)
        if 'reference' in fields:
            sketch = os.path.join(layout.sketches, fields['reference']['sketch'])
            if not os.path.isfile(sketch):
                report.error(recipe.where(*field_place(recipe, variant, 'reference')), 'sketches/%s does not exist: write the sketch, or '
                             'correct its name' % fields['reference']['sketch'])
            elif not fields['reference']['sketch'].startswith(recipe.page.replace('/', '-') + '-'):
                report.error(recipe.where(*field_place(recipe, variant, 'reference')), 'a sketch of %s is named %s-<name>.cpp: rename it'
                             % (recipe.page, recipe.page.replace('/', '-')))
        text = fields.get('text') or {}
        for argument in text.get('arguments', []) if 'program' in text else []:
            where = recipe.where(*field_place(recipe, variant, 'text'))
            if c_AbsolutePath.match(argument):
                report.error(where, 'the argument "%s" is an absolute path, which names a folder of the machine the take runs on: stage the file '
                             'with files and name it relative to the run folder' % argument)
            elif fields.get('files') and '..' in re.split(r'[\\/]', argument):
                report.error(where, 'the argument "%s" leaves the run folder the files are staged in: name a file the recipe stages' % argument)
        for expression in text.get('redact', []):
            try:
                re.compile(expression)
            except re.error as error:
                report.error(recipe.where(*field_place(recipe, variant, 'text')), 'redact "%s" is not a regular expression (%s): correct it' % (expression, error))
        for measure in text.get('measured', []):
            if 'command' in text:
                if not any(measure == pointer or measure.startswith(pointer + '/') for pointer in text.get('keep', [])):
                    report.error(recipe.where(*field_place(recipe, variant, 'text')), 'measured %s is no value keep shows: measure a value inside a '
                                 'kept pointer' % measure)
            else:
                try:
                    re.compile(measure)
                except re.error as error:
                    report.error(recipe.where(*field_place(recipe, variant, 'text')), 'measured "%s" is not a regular expression (%s): correct it' % (measure, error))
        if text.get('measured') and 'one run' not in fields.get('caption', '').lower():
            report.error(recipe.where(*field_place(recipe, variant, 'caption')), 'the text holds measurements (measured): say in the caption that '
                         'they are one run\'s measurements (R57)')
        if 'command' in text and dumps.commands is not None and dumps.command(text['command']['command']) is False:
            report.error(recipe.where(*field_place(recipe, variant, 'text')), 'the command %s is not one the editor at the pin registers: use '
                         'a command of editor.commands at the pin' % text['command']['command'])
        waits = fields.get('waitsFor')
        if waits:
            where = recipe.where(*field_place(recipe, variant, 'waitsFor'))
            if waits in c_Additions:
                present = addition_present(waits, dumps, pin_data)
                if present:
                    report.error(where, 'waitsFor "%s": the pin already has %s; take the figure without waitsFor' % (waits, c_Additions[waits]))
                elif present is None:
                    report.note(where, 'waitsFor "%s" is not checked: the dumps that tell whether the pin has it are missing' % waits)
            elif not c_Tier3.match(waits):
                report.error(where, 'waitsFor names an addition of pipelines.md §11: one of %s, or "tier 3: <capture>; <why no debug view '
                             'shows it>"' % ', '.join('"%s"' % name for name in c_Additions))
            report.unmade(where, 'waits for %s' % waits)
    # Labs the recipe uses.
    lab = (entry.get('project') or {}).get('lab')
    if lab and lab not in labs:
        report.error(recipe.where('project', 'lab'), '%s does not exist: write the lab, or name another' % lab)
    return shot


def recipe_unmade(recipe):
    """Whether no take makes the figure at the pin: every variant waits for an addition (waitsFor) or is blocked."""
    return all(fields.get('waitsFor') or fields.get('blocked') for _, fields in recipe.variants())


def check_renderer(recipe, variant, fields, dumps, report):
    """A recipe's renderer switches against viewport.capture's renderer parameter in the commands dump: names it has,
    values its schema allows, and only on still figures (live captures refuse them: c_LiveRefused)."""
    where = recipe.where(*field_place(recipe, variant, 'renderer'))
    if recipe.kind == 'live':
        return
    if recipe.kind != 'scene':
        report.error(where, 'renderer switches are viewport.capture\'s: only scene figures take them')
        return
    entry = dumps.command('viewport.capture') if dumps.commands is not None else None
    if entry is None:
        return
    schema = (((entry or {}).get('parameters') or {}).get('properties') or {}).get('renderer')
    if not isinstance(schema, dict):
        report.error(where, 'renderer: viewport.capture at the pin takes no renderer switches: take the figure once the pin has them (waitsFor '
                     '"tier 2: renderer switches")')
        return
    switches = schema.get('properties') or {}
    for name, value in fields['renderer'].items():
        if name not in switches:
            report.error(where, 'renderer: viewport.capture at the pin has no switch %s: use one of %s' % (name, ', '.join(sorted(switches))))
            continue
        problems = jsonschema.Validator(switches[name]).problems(value)
        if problems:
            report.error(where, 'renderer: the switch %s is %s, which viewport.capture at the pin refuses (%s): give a value its schema allows'
                         % (name, json.dumps(value), problems[0][1]))


def home_folders():
    """The user's home folder as the system names it (USERPROFILE on Windows, HOME elsewhere), in the forms text may
    give it: what no picture, text or stamp of a take may name (plan/pipelines.md §5.4, "Neutral paths")."""
    found = []
    for path in (os.environ.get('USERPROFILE'), os.environ.get('HOME'), os.path.expanduser('~')):
        if not path or len(os.path.abspath(path).rstrip('\\/')) <= 3:
            continue
        # Windows also names the folder by its short name (C:\Users\<NAME>~1 for a long name), as TEMP often does.
        for form in (os.path.abspath(path), short_path(path)):
            if form and form not in found:
                found.append(form)
    return found


def short_path(path):
    """The short (8.3) name Windows gives a folder that exists, or None."""
    if os.name != 'nt' or not os.path.isdir(path):
        return None
    import ctypes
    buffer = ctypes.create_unicode_buffer(1024)
    length = ctypes.windll.kernel32.GetShortPathNameW(os.path.abspath(path), buffer, len(buffer))
    return buffer.value if 0 < length < len(buffer) else None


def named_folder(text, folders):
    """The first of folders that text names (with either slash, in any case, not as part of a longer name), or None."""
    lowered = text.replace('\\', '/').lower()
    for folder in folders:
        form = folder.replace('\\', '/').rstrip('/').lower()
        start = lowered.find(form)
        while start >= 0:
            after = lowered[start + len(form):start + len(form) + 1]
            if not after or not (after.isalnum() or after in '_-.'):
                return folder
            start = lowered.find(form, start + 1)
    return None


def privacy_problem(text, work, what):
    """What a take's text names that it must not: the work folder's real path or the user's home (None when neither);
    what says whose text it is ("the editor's log", "the text", "the stamp")."""
    for line in text.splitlines() or [text]:
        found = named_folder(line, [work]) if work else None
        if found:
            return '%s names the work folder (%s)' % (what, found), line.strip()
        found = named_folder(line, home_folders())
        if found:
            return '%s names the user\'s home folder (%s)' % (what, found), line.strip()
    return None


def check_project_files(recipe, variant, fields, layout, pin_data, report):
    """A recipe's files: book files under tutorials/ (or a stage's sample assets at the pin) of at most
    c_ProjectFileLimit bytes, copied to a place inside the project, before a step the figure has; a program's text figure
    stages them in its run folder before it starts."""
    base = field_place(recipe, variant, 'files')
    program = recipe.kind == 'text' and 'program' in (fields.get('text') or {})
    if recipe.kind not in c_FilesKinds and not program:
        report.error(recipe.where(*base), 'only editor, scene and program text figures copy files: remove files')
        return
    items, problems = project_files(layout, recipe, variant, fields)
    for place, message in problems:
        report.error(recipe.where(*place), message)
    for item in items:
        problem = project_file_data(layout, pin_data.engine, pin_data.pin, item, read=False)[1]
        if problem:
            report.error(recipe.where(*item.place), problem)
    holder, count = step_holder(recipe, variant, fields)
    for index, entry in enumerate(fields['files']):
        at = entry.get('atStep')
        if at is None:
            continue
        if program:
            report.error(recipe.where(*(base + (index, 'atStep'))), 'atStep %d: a program\'s files are staged in its run folder before it starts: '
                         'leave atStep out' % at)
            continue
        if at > count:
            report.error(recipe.where(*(base + (index, 'atStep'))), 'atStep %d: %s holds %d step%s: copy before one of them, or leave atStep out '
                         'to copy before the editor opens the project' % (at, holder, count, '' if count == 1 else 's'))
        if recipe.kind == 'editor' and fields.get('play'):
            report.error(recipe.where(*(base + (index, 'atStep'))), 'atStep closes the window before that step and opens it again on the copy, '
                         'which ends play: leave play out, or copy before the editor opens the project')


def field_place(recipe, variant, field):
    """The path of a field in the manifest: the variant's when it sets it, else the recipe's."""
    if variant and field in recipe.entry['variants'][variant]:
        return ('variants', variant, field)
    return (field,) if field in recipe.entry else ()


def read_labs(layout, report=None):
    """{"labs/<name>.json": {steps, lines, scenes}} of every lab of the book; problems of a lab go to report."""
    labs = {}
    folder = os.path.join(layout.root, 'labs')
    for path in sorted(glob.glob(os.path.join(folder, '*.json'))):
        relative = layout.relative(path)
        try:
            steps, lines = jsonpos.load(repo.read_text(path))
        except jsonpos.JsonError as error:
            if report:
                report.error('%s:%d' % (relative, error.line), 'not valid JSON (%s): correct the lab' % error)
            continue
        labs[relative] = {'steps': steps, 'lines': lines, 'scenes': script_scenes(steps), 'path': path}
    return labs


def walk_strings(value, path=()):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, path + (index,))


def check_lab(layout, relative, lab, dumps, report):
    steps, lines = lab['steps'], lab['lines']
    if not isinstance(steps, list):
        report.error('%s:1' % relative, 'a lab is an engine command script: write it as a JSON list of steps')
        return
    for number, step in enumerate(steps):
        where = '%s:%d' % (relative, jsonpos.line_of(lines, '/%d' % number))
        if not isinstance(step, dict) or 'command' not in step:
            report.error(where, 'a step is an object with a command: write {"command": …, "parameters": {…}}')
            continue
        for key in step:
            if key not in c_LabKeys:
                report.error(where, 'a lab step holds only the engine\'s keys (%s), not %s%s' % (', '.join(c_LabKeys), key,
                             ' (entityName is the book\'s: bind the entity of entity.find instead)' if key == 'entityName' else ''))
        if step['command'] == 'project.create':
            report.error(where, 'a lab runs in an open project, so it never calls project.create: remove the step')
        if step['command'] in c_RefusedCommands:
            report.error(where, '%s changes the person\'s preferences, which no tool does (pipelines.md §2): use a project setting' % step['command'])
        if dumps.commands is not None and dumps.command(step['command']) is False:
            report.error(where, 'the command %s is not one the editor at the pin registers: use a command of editor.commands at the pin' % step['command'])
        for path, value in walk_strings(step.get('parameters')):
            if c_Placeholder.search(value):
                report.error('%s:%d' % (relative, jsonpos.line_of(lines, '/%d/parameters' % number + ''.join('/' + jsonpos.escape(part) for part in path))),
                             'a lab holds no placeholder (%s): name assets by their path in the project' % c_Placeholder.search(value).group(0))
            elif c_AbsolutePath.match(value):
                report.error('%s:%d' % (relative, jsonpos.line_of(lines, '/%d/parameters' % number + ''.join('/' + jsonpos.escape(part) for part in path))),
                             'a lab holds no absolute path (%s): name assets by their path in the project' % value)
    name = os.path.basename(relative)[:-5]
    download = os.path.join(layout.root, 'public', 'downloads', 'labs', name + '.zip')
    expected = lab_zip(layout, name)
    if not os.path.isfile(download):
        report.error('%s:1' % relative, 'its download public/downloads/labs/%s.zip is missing: run python -I tools/figures.py labs %s' % (name, name))
    elif read_bytes(download) != expected:
        report.error('%s:1' % relative, 'its download public/downloads/labs/%s.zip differs from what figures.py labs writes: run python -I '
                     'tools/figures.py labs %s' % (name, name))


def check_published(recipe, shot, layout, taken, report, in_compare, placed=None):
    """The published files of a recipe against the recipe and taken.json; placed: the crops its page places."""
    folder = os.path.join(layout.pictures, *recipe.page.split('/'))
    files = promised_files(recipe, shot, placed)
    crops = {crop['name']: crop for crop in recipe_crops(recipe, shot)}
    for name, (variant, crop) in sorted(files.items()):
        path = os.path.join(folder, name)
        relative = layout.relative(path)
        stem = name.rsplit('.', 1)[0]
        others = [candidate for candidate in glob.glob(os.path.join(folder, glob.escape(stem) + '.*'))
                  if not candidate.endswith(('.result.json',)) and os.path.basename(candidate) != name]
        for other in others:
            report.error(layout.relative(other), 'the recipe %s (%s) publishes this picture as %s (%s): remove %s' % (
                recipe.id, recipe.where(), name, 'a crop is lossless WebP' if crop else {'lossy': 'lossy: AVIF', 'lossless': 'lossless: WebP',
                                                                         'text': 'text', 'svg': 'a drawing: SVG'}[recipe.publish()], os.path.basename(other)))
        if not os.path.isfile(path):
            (report.unmade if recipe_unmade(recipe) else report.note)(recipe.where(), 'no %s yet (%s)' % (
                relative, 'not taken' if recipe.kind != 'diagram' else 'not drawn'))
            continue
        if recipe.kind == 'diagram':
            data = read_bytes(path)
            if images.format_of(data) != 'svg':
                report.error(relative, 'a drawing is published as an SVG file (recipe %s): draw it as SVG' % recipe.where())
            continue
        record = taken.files.get(name)
        data = read_bytes(path)
        if record is None:
            report.note(relative, 'a placeholder: taken.json has no stamp for it (recipe %s): %s' % (recipe.where(), c_Republish))
        elif sha256_bytes(data) != record['sha256']:
            report.error(relative, 'its SHA-256 differs from its stamp (%s): %s' % (taken.where(name), c_Republish))
        if recipe.kind == 'text':
            continue
        record = record or {}
        kind = images.format_of(data)
        if kind == 'webp' and not images.webp_is_lossless(data):
            report.error(relative, 'a lossy WebP file: %s pictures are lossless WebP (recipe %s): %s' % ('crop' if crop else 'these', recipe.where(), c_Republish))
        if kind != name.rsplit('.', 1)[1]:
            report.error(relative, 'the file is %s, not what its name says (recipe %s): %s' % (kind or 'no picture the tool knows', recipe.where(), c_Republish))
        try:
            width, height = images.size_of(data, relative)
        except images.ImageError as error:
            report.error(relative, '%s (recipe %s): %s' % (error, recipe.where(), c_Republish))
            continue
        if record.get('size') and [width, height] != record['size']:
            report.error(relative, 'it is %d x %d; its stamp says %d x %d (%s): %s' % (width, height, record['size'][0], record['size'][1], taken.where(name), c_Republish))
        capture = taken.files.get(recipe.stem(variant) + recipe.extension(), {}).get('size') if crop else None
        if crop and capture:
            x0, y0, x1, y1 = images.crop_rectangle(crops[crop]['rect'], capture[0], capture[1])
            if [width, height] != [x1 - x0, y1 - y0]:
                report.error(relative, 'a crop is its rectangle at the capture\'s pixels, %d x %d; this file is %d x %d (recipe %s): %s' % (
                    x1 - x0, y1 - y0, width, height, recipe.where(), c_Republish))
        if not crop and recipe.kind in ('scene', 'live'):
            size = list(recipe.entry.get('size', c_DefaultSize))
            if [width, height] != size:
                report.error(relative, 'a render has the capture\'s size, %d x %d; this file is %d x %d (recipe %s): %s' % (
                    size[0], size[1], width, height, recipe.where(*(('size',) if 'size' in recipe.entry else ())), c_Republish))
        expected, quality = encoder_settings(recipe, recipe.entry, crop, in_compare)
        encoder = record.get('encoder') or {}
        if record and expected == 'lossy' and encoder.get('quality') != quality:
            report.error(taken.where(name), 'a lossy picture %s is encoded at quality %d; its stamp says %s: publish it again with figures.py '
                         'publish' % ('on a slider' if in_compare else 'outside a slider', quality, encoder.get('quality')))
    return files


def check_compare_pairs(recipe, taken, report):
    """Both sides of a slider: the same size and the same encoder settings."""
    sides = []
    for variant in recipe.variant_names()[:2] if len(recipe.variant_names()) >= 2 else []:
        record = taken.files.get(recipe.stem(variant) + recipe.extension())
        if record:
            sides.append((variant, record))
    if len(sides) == 2:
        (first, one), (second, other) = sides
        if one.get('size') != other.get('size'):
            report.error(recipe.where('variants'), 'the slider\'s sides %s and %s differ in size (%s, %s): take and publish both again' % (
                first, second, one.get('size'), other.get('size')))
        settings = lambda record: {key: value for key, value in (record.get('encoder') or {}).items()}
        if settings(one) != settings(other):
            report.error(recipe.where('variants'), 'the slider\'s sides %s and %s were encoded with different settings: publish both again '
                         'with figures.py publish' % (first, second))


def check_pages(layout, recipes, shots, report, invalid):
    by_page = {}
    for recipe in recipes:
        by_page.setdefault(recipe.page, {})[recipe.id] = recipe
    pages = dict(layout.pages())
    for page, path in sorted(pages.items()):
        text = repo.read_text(path)
        placed = set()
        for line, name, attributes in directives(text):
            where = '%s:%d' % (layout.relative(path), line)
            figure = attributes.get('id')
            if not figure:
                report.error(where, '::%s needs an id: ::%s{id=<figure>}' % (name, name))
                continue
            placed.add(figure)
            recipe = by_page.get(page, {}).get(figure)
            if recipe is None and page in invalid:
                continue  # its manifest fails its schema, which is reported above
            if recipe is None:
                manifest = 'src/content/figures/%s.json' % page
                report.error(where, '::%s{id=%s}: %s has no figure "%s": add its recipe, or correct the id' % (name, figure, manifest, figure))
                continue
            variants = recipe.variant_names()
            if name == 'compare':
                if len(variants) < 2:
                    report.error(where, '::compare{id=%s} needs a recipe with two variants: add them, or show it with ::figure' % figure)
                for side in ('before', 'after'):
                    if side in attributes and attributes[side] not in variants:
                        report.error(where, '::compare %s="%s" is not a variant of %s: use one of %s' % (side, attributes[side], figure, ', '.join(variants)))
            elif recipe.kind == 'text':
                # The site's build (src/plugins/figures.mjs) draws a text figure only from its fence.
                report.error(where, 'figure "%s" is a text figure: show it in a fence, ```text capture="%s"' % (figure, figure))
            else:
                if variants and attributes.get('variant') not in variants:
                    report.error(where, '::figure{id=%s} names one of its variants: variant=%s' % (figure, ' or variant='.join(variants)))
                if not variants and 'variant' in attributes:
                    report.error(where, '::figure{id=%s} has no variants: remove variant=' % figure)
                if 'crop' in attributes:
                    crops = [crop['name'] for crop in recipe_crops(recipe, shots.get((recipe.page, recipe.id)))]
                    wanted = attributes['crop']
                    if not crops:
                        report.error(where, '::figure{id=%s crop} names a crop, but the recipe has none: add crops to the recipe, or remove crop' % figure)
                    elif wanted and wanted not in crops:
                        report.error(where, 'crop="%s" is not a crop of %s: use one of %s' % (wanted, figure, ', '.join(crops)))
                    elif not wanted and len(crops) > 1:
                        report.error(where, 'the recipe %s has several crops: name one, crop="%s"' % (figure, crops[0]))
        for fence, figure, variant in capture_fences(text):
            placed.add(figure)
            where = '%s:%d' % (layout.relative(path), fence.open_line)
            problem = capture_form_problem(fence, figure)
            if problem:
                report.error(where, problem)
                continue
            recipe = by_page.get(page, {}).get(figure)
            if recipe is None or recipe.kind != 'text':
                report.error(where, 'capture="%s": the page has no text figure of that id: add its recipe (kind text), or correct capture' % figure)
                continue
            if recipe.variant_names() and variant not in recipe.variant_names():
                report.error(where, 'capture="%s" names one of its variants: variant="%s"' % (figure, recipe.variant_names()[0]))
                continue
            if not recipe.variant_names() and variant is not None:
                report.error(where, 'capture="%s" has no variants: remove variant="%s"' % (figure, variant))
                continue
            file = os.path.join(layout.pictures, *page.split('/'), recipe.stem(variant) + '.txt')
            if not os.path.isfile(file):
                report.note(where, 'the text figure %s is not taken yet: take it with figures.py take --kinds text, then publish and fill it' % recipe.stem(variant))
            elif fence.body != text_lines(repo.read_text(file)):
                report.error(where, 'the fence differs from %s: run python -I tools/figures.py fill' % layout.relative(file))
        if page not in invalid:
            check_placement(layout.relative(path), by_page.get(page, {}), placed, report)
    for page in sorted(by_page):
        if page not in pages:
            report.error(by_page[page][next(iter(by_page[page]))].manifest + ':1', 'there is no page %s.md for this manifest: write the page, '
                         'or move the manifest to its page\'s name' % page)


def check_placement(page_file, recipes, placed, report):
    """Every figure of a page's manifest is placed by its page (::figure, ::compare or a text fence), but a figure no take
    makes at the pin (it waits, or is blocked): the page places its stand-in in its place (standIn, a figure of the same
    manifest: a drawing or the nearest honest picture), or the manifest says why the page shows none (noStandIn)
    (plan/pipelines.md §11)."""
    for figure, recipe in sorted(recipes.items()):
        stand_in, without = recipe.entry.get('standIn'), recipe.entry.get('noStandIn')
        if stand_in:
            other = recipes.get(stand_in)
            if other is None:
                report.error(recipe.where('standIn'), 'standIn "%s" is no figure of %s: name a figure of the same manifest (a drawing, or the nearest '
                             'honest picture)' % (stand_in, recipe.manifest))
            elif other.entry.get('standIn') or recipe_unmade(other):
                report.error(recipe.where('standIn'), 'the stand-in %s is itself not made at the pin: name a figure a take or a writer can make' % stand_in)
            elif stand_in not in placed:
                report.error(recipe.where('standIn'), '%s does not place the stand-in %s of %s: write ::figure{id=%s} where %s would stand' % (
                    page_file, stand_in, figure, stand_in, figure))
        if figure in placed:
            if stand_in and recipe_unmade(recipe):
                report.error(recipe.where('standIn'), '%s places %s, which no take makes at the pin, and its stand-in is %s: place %s in its place' % (
                    page_file, figure, stand_in, stand_in))
            continue
        if not recipe_unmade(recipe):
            if not any(other.entry.get('standIn') == figure for other in recipes.values()):
                report.error(recipe.where(), '%s does not place the figure %s: place it (::figure{id=%s}, or a text fence for a text figure), or remove '
                             'its recipe' % (page_file, figure, figure))
        elif not stand_in and not without:
            report.error(recipe.where(), 'the figure %s %s, and %s does not place it: name the figure that stands in for it (standIn) and place '
                         'that, or say why the page shows none (noStandIn)' % (figure, 'is blocked' if any(fields.get('blocked') for _, fields in recipe.variants())
                                                                              else 'waits', page_file))


def text_lines(text):
    return text.rstrip('\n').split('\n') if text else []


def check(layout, engine, pin, dumps_folder, baselines, release):
    report = Report(release)
    dumps = Dumps(dumps_folder if os.path.isdir(dumps_folder) else None, pin)
    for name in dumps.missing:
        report.note(os.path.join(dumps_folder, name).replace(os.sep, '/'), 'the dump %s is missing, so what it lists is not checked: run '
                    'python -I tools/reference.py dump at the pin' % name)
    pin_data = Pin(engine, pin)
    invalid = set()
    recipes = load_recipes(layout, report, invalid)
    labs = read_labs(layout, report)
    for relative, lab in sorted(labs.items()):
        check_lab(layout, relative, lab, dumps, report)
    ids = {}
    for recipe in recipes:
        ids.setdefault((recipe.manifest, recipe.id), []).append(recipe)
    for (manifest, figure), found in sorted(ids.items()):
        if len(found) > 1:
            report.error(found[1].where('id'), 'the id "%s" is used twice in the manifest: give each figure its own id' % figure)
    compared = compare_ids(layout)
    placements = placed_pictures(layout, recipes)
    shots = {}
    taken_by_page = {}
    promised = {}
    unplaced = {}
    for recipe in recipes:
        shot = check_recipe(recipe, layout, pin_data, dumps, labs, baselines, report)
        shots[(recipe.page, recipe.id)] = shot
        if recipe.page not in taken_by_page:
            taken_by_page[recipe.page] = Taken(layout, recipe.page)
            if taken_by_page[recipe.page].problem:
                report.error(*taken_by_page[recipe.page].problem)
        taken = taken_by_page[recipe.page]
        placed = placements.get(recipe.page, set())
        files = check_published(recipe, shot, layout, taken, report, recipe.id in compared.get(recipe.page, set()), placed)
        unplaced.setdefault(recipe.page, {}).update(unplaced_files(recipe, shot, placed))
        if recipe.id in compared.get(recipe.page, set()):
            check_compare_pairs(recipe, taken, report)
        for name in files:
            promised.setdefault(recipe.page, set()).add(name)
            promised[recipe.page].add(name.rsplit('.', 1)[0] + '.result.json')
    for page, taken in sorted(taken_by_page.items()):
        for name in sorted(taken.files):
            if name in unplaced.get(page, {}):
                (kind, what), _ = unplaced[page][name]
                report.error(taken.where(name), 'taken.json stamps %s, %s, which no page places: remove the stamp and the file, or place the %s' % (
                    name, what, kind))
            elif name not in promised.get(page, set()):
                report.error(taken.where(name), 'taken.json stamps %s, which no recipe promises: publish again, or remove the stamp' % name)
            elif not os.path.isfile(os.path.join(taken.folder, name)):
                report.error(taken.where(name), 'taken.json stamps %s, which is not published: publish it again with figures.py publish' % name)
    check_pages(layout, recipes, shots, report, invalid)
    if os.path.isdir(layout.pictures):
        for folder, _, files in os.walk(layout.pictures):
            page = os.path.relpath(folder, layout.pictures).replace(os.sep, '/')
            for name in sorted(files):
                if name == c_TakenFile and page in taken_by_page:
                    continue
                if name in unplaced.get(page, {}):
                    (kind, what), directive = unplaced[page][name]
                    report.error(layout.relative(os.path.join(folder, name)), 'no page places %s (%s): remove the file%s, or place the %s' % (
                        what, directive, '' if name.endswith('.result.json') else ' and its stamp', kind))
                elif name not in promised.get(page, set()) and page not in invalid:
                    report.error(layout.relative(os.path.join(folder, name)), 'no recipe promises this file: remove it, or add its recipe'
                                 + (' (.png is not a published format)' if name.endswith('.png') else ''))
    return report


# ---------------------------------------------------------------------------------------------------------------------
# fill.

def fill_text(text, layout, page):
    """(new text, number of fences changed, problems as (line, message))."""
    problems = []
    changed = 0
    for fence, figure, variant in reversed(capture_fences(text)):
        problem = capture_form_problem(fence, figure)
        if problem:
            problems.append((fence.open_line, problem))
            continue
        stem = figure + ('-' + variant if variant else '')
        file = os.path.join(layout.pictures, *page.split('/'), stem + '.txt')
        if not os.path.isfile(file):
            problems.append((fence.open_line, 'the text figure %s is not taken yet (%s)' % (stem, layout.relative(file))))
            continue
        body = text_lines(repo.read_text(file))
        if body != fence.body:
            text = markdown.replace_fence_body(text, fence, body)
            changed += 1
    return text, changed, problems


# ---------------------------------------------------------------------------------------------------------------------
# labs.

def credits_entries(layout):
    """{path under labs/: entry text} of labs/CREDITS.md: each entry starts with "## <path>"."""
    path = os.path.join(layout.root, 'labs', 'CREDITS.md')
    if not os.path.isfile(path):
        return {}
    entries = {}
    current = None
    for line in repo.read_text(path).split('\n'):
        heading = re.match(r'^## (\S+)\s*$', line)
        if heading:
            current = heading.group(1)
            entries[current] = [line]
        elif current:
            entries[current].append(line)
    return {key: '\n'.join(value).strip() + '\n' for key, value in entries.items()}


def zip_bytes(files):
    """A zip of (name, bytes) pairs, the same bytes for the same files: sorted, fixed times, no extra fields."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            archive.writestr(info, data)
    return buffer.getvalue()


def lab_zip(layout, name):
    labs = os.path.join(layout.root, 'labs')
    files = [(name + '.json', read_bytes(os.path.join(labs, name + '.json')))]
    folder = os.path.join(labs, name)
    credited = []
    entries = credits_entries(layout)
    for root, directories, names in os.walk(folder):
        directories.sort()
        for file in sorted(names):
            path = os.path.join(root, file)
            inside = os.path.relpath(path, folder).replace(os.sep, '/')
            files.append((inside, read_bytes(path)))
            key = name + '/' + inside
            if key in entries:
                credited.append(entries[key])
    if credited:
        files.append(('CREDITS.md', ('# Credits\n\nThe third-party files of this lab and their terms.\n\n' + '\n'.join(credited)).encode('utf-8')))
    return zip_bytes(files)


# ---------------------------------------------------------------------------------------------------------------------
# take.

def picture_stem(recipe, variant):
    """<part>.<chapter>.<figure>[.<variant>]: LookDev's capture-set name of a take's picture."""
    return '%s.%s%s' % (recipe.page.replace('/', '.'), recipe.id, '.' + variant if variant else '')


def matches_figures(recipe, pattern):
    return not pattern or fnmatch.fnmatchcase('%s/%s' % (recipe.page, recipe.id), pattern)


def prepare_work(work):
    """Empties the work folder of the previous run (only a folder this tool marked as its own)."""
    marker = os.path.join(work, '.figures-take')
    if os.path.isdir(work) and os.listdir(work):
        if not os.path.isfile(marker):
            raise UsageError('the work folder %s holds files that are not a take of figures.py: name an empty folder with --work' % work)
        for entry in os.listdir(work):
            path = os.path.join(work, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    os.makedirs(work, exist_ok=True)
    repo.write_text(marker, 'A take of tools/figures.py; the next take empties this folder.\n')
    for folder in ('shots', 'crops', 'results', 'text', 'log', 'projects'):
        os.makedirs(os.path.join(work, folder), exist_ok=True)


resolve_pointer = script_steps.resolve_pointer


def kept(result, pointers):
    """The values the pointers name, in an object shaped by the pointers' keys (/engineCommit gives {"engineCommit": …},
    /commands/0/name gives {"commands": {"0": {"name": …}}}): what a text figure shows of a command's result."""
    copy = {}
    for pointer in pointers:
        try:
            value = resolve_pointer(result, pointer)
        except KeyError:
            raise TakeError('keep %s: the result has no such value: keep a pointer into the command\'s result' % pointer)
        parts = [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]
        node = copy
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise TakeError('keep %s: an earlier pointer keeps the whole value it is inside: keep one of the two' % pointer)
        node[parts[-1]] = value
    return copy


def redact(text, expressions):
    for expression in expressions:
        text = re.sub(expression, '…', text)
    return text


def without_measured(value, pointers):
    """A copy of a kept value with the values the measured pointers name replaced by one mark: what two runs of a
    command must agree on (R57)."""
    copy = json.loads(json.dumps(value))
    for pointer in pointers:
        parts = [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]
        node = copy
        try:
            for part in parts[:-1]:
                node = node[int(part)] if isinstance(node, list) else node[part]
            if isinstance(node, list):
                node[int(parts[-1])] = '…'
            elif parts[-1] in node:
                node[parts[-1]] = '…'
            else:
                raise KeyError(pointer)
        except (KeyError, IndexError, ValueError, TypeError):
            raise TakeError('measured %s: the answer has no such value: measure a pointer inside what keep shows' % pointer)
    return copy


def pair_difference(first, second):
    """How the two captures' PNG files of a scene figure differ: None when their bytes are equal, else {pixels, percent,
    largest} of their decoded pixels (largest: the largest difference of one channel, in levels). Pictures of
    different sizes differ in every pixel."""
    if first == second:
        return None
    try:
        a = images.read_png(first, 'the first capture')
        b = images.read_png(second, 'the second capture')
    except images.ImageError as error:
        raise TakeError('the two captures differ and do not decode: %s' % error)
    if (a.width, a.height, a.channels) != (b.width, b.height, b.channels):
        return {'pixels': max(a.width * a.height, b.width * b.height), 'percent': 100.0, 'largest': 255}
    stride = a.width * a.channels
    pixels = 0
    largest = 0
    for y in range(a.height):
        row_a = a.data[y * stride:(y + 1) * stride]
        row_b = b.data[y * stride:(y + 1) * stride]
        if row_a == row_b:
            continue
        for x in range(0, stride, a.channels):
            difference = max(abs(row_a[x + channel] - row_b[x + channel]) for channel in range(a.channels))
            if difference:
                pixels += 1
                largest = max(largest, difference)
    return {'pixels': pixels, 'percent': round(100.0 * pixels / (a.width * a.height), 3), 'largest': largest}


def same_picture(difference):
    """R57: byte-identical, or no channel more than c_PairLevels off in at most c_PairPercent per cent of the pixels."""
    return difference is None or (difference['largest'] <= c_PairLevels and difference['percent'] <= c_PairPercent)


def resolve_steps(session, command_steps, bound):
    """Runs command steps in an editor as the engine's runner does (booklib.steps)."""
    script_steps.run_steps(session, command_steps, bound)


substitute = script_steps.substitute


class Take:
    def __init__(self, layout, engine, pin, build, work, log):
        self.layout = layout
        self.engine = engine
        self.pin = pin
        self.build = build
        self.work = work
        self.log = log
        self.pending = {}
        self.status = None
        self.toolchain = None
        self.failures = []
        self.skipped = []
        self.lookdev_folder = None
        self.provisional = False
        self.notes = []
        self.window = None  # an editor figure's window: {size, layout} (editor_window)
        self.project_directory = None  # the project copy of the figures being taken (None: an editor figure of the launcher)
        self.drive_folder = None  # an editor figure's folder, which its window sees as the root of a drive (map_drive)

    def lookdev(self):
        """The look-dev project, made once per run as plan/pipelines.md §5.4 says: Tools/LookDev.py capture of one small
        shot with --keep-work, which leaves the project it made in <work>/lookdev/projects/LookDev."""
        if self.lookdev_folder is None:
            folder = os.path.join(self.work, 'lookdev')
            arguments = [sys.executable, '-I', os.path.join(self.engine.path, 'Tools', 'LookDev.py'), 'capture', '--build', self.build,
                         '--projects', 'LookDev', '--shots', 'lookdev.overview', '--sizes', '320x180', '--aa', 'off', '--repeat', '1',
                         '--work', folder, '--output', os.path.join(folder, 'capture'), '--keep-work']
            code, output, _ = editor.run_program(arguments, editor.environment(self.build, self.work, editor.new_session_dir()), self.log,
                                                 'lookdev-project', editor.c_OpenSeconds)
            project = os.path.join(folder, 'projects', 'LookDev')
            if code != 0 or not glob.glob(os.path.join(project, '*.stproj')):
                raise TakeError('Tools/LookDev.py capture did not make the look-dev project (exit code %d): %s' % (code, editor.last_line(output)))
            self.lookdev_folder = project
        return self.lookdev_folder

    def record(self, recipe, variant, stem, original, kind, size=None, recorded=None, crop=None, pair=None, renderer=None):
        """Records a picture or text in taken-pending.json; TakeError when the stamp would name the work folder or the
        user's home (the editor's status gives its GPU and OS as text)."""
        stamp = {'pairDifference': pair,
            'page': recipe.page, 'figure': recipe.id, 'variant': variant, 'crop': crop, 'kind': kind, 'sha256': original,
            'pin': self.pin, 'build': editor.build_record(self.build, self.engine.path) if self.build else None,
            'reportedCommit': (self.status or {}).get('engineCommit'), 'os': (self.status or {}).get('platform'),
            'gpu': (self.status or {}).get('gpu'), 'size': size, 'recorded': recorded or {}, 'renderer': renderer or None,
        }
        for _, value in walk_strings(stamp):
            problem = privacy_problem(value, self.work, 'the stamp')
            if problem:
                raise TakeError('%s in "%s": a stamp is published beside the picture' % problem)
        self.pending[stem] = stamp

    def write_text(self, recipe, variant, text, result=None, record=None):
        stem = picture_stem(recipe, variant)
        repo.write_text(os.path.join(self.work, 'text', stem + '.txt'), text)
        if result is not None:
            write_json(os.path.join(self.work, 'results', stem + '.json'), result)
        recorded = {}
        for name, pointer in (record or {}).items():
            try:
                recorded[name] = resolve_pointer(result, pointer)
            except KeyError:
                raise TakeError('record %s: the result has no %s: record a pointer the result has' % (name, pointer))
        self.record(recipe, variant, stem, sha256_bytes(text.encode('utf-8')), 'text', recorded=recorded)

    def picture(self, recipe, variant, image, kind, shot=None, data=None, recorded=None, pair=None, renderer=None):
        """Writes a picture of the take and its crops; records them. data is the PNG file a program wrote (an engine
        capture), kept byte for byte as the original; without it the image is written as PNG. A capture is decoded only
        when the recipe cuts crops from it. pair is how the second capture differed (pair_difference); renderer the
        switches the capture drew with."""
        stem = picture_stem(recipe, variant)
        crops = recipe_crops(recipe, shot)
        if data is None:
            data = images.png_bytes(image)
        elif crops:
            image = images.read_png(data, 'the capture of %s' % stem)
        with open(os.path.join(self.work, 'shots', stem + '.png'), 'wb') as file:
            file.write(data)
        size = [image.width, image.height] if image is not None else list(images.size_of(data, 'the capture of %s' % stem))
        self.record(recipe, variant, stem, sha256_bytes(data), kind, size=size, recorded=recorded, pair=pair, renderer=renderer)
        for crop in crops:
            x0, y0, x1, y1 = images.crop_rectangle(crop['rect'], image.width, image.height)
            piece = image.crop(x0, y0, x1, y1)
            crop_data = images.png_bytes(piece)
            crop_stem = '%s-%s' % (stem, crop['name'])
            with open(os.path.join(self.work, 'crops', crop_stem + '.png'), 'wb') as file:
                file.write(crop_data)
            self.record(recipe, variant, crop_stem, sha256_bytes(crop_data), kind, size=[piece.width, piece.height], crop=crop['name'],
                        renderer=renderer)


class ProjectFile:
    """One file a recipe copies into its project copy: source is book:<path> or (from a stage) Samples/<S>/Assets/<path>
    at the pin, target a path in the project, at the step it is copied before (None: before the editor opens the
    project), place the recipe field that names it, stage the tutorial stage that copies it (None: the recipe names it)."""

    def __init__(self, source, target, at, place, stage=None):
        self.source = source
        self.target = target
        self.at = at
        self.place = place
        self.stage = stage


def project_files(layout, recipe, variant, fields):
    """([ProjectFile] in the order they are copied, [(field path, problem)]) of a recipe's files. {"stage": n} stands for
    the files that stages 1 to n of the page's tutorial copy, in their order, so that a later copy to the same place wins:
    the stages' files, not their commands (the figure's steps do what those did)."""
    found, problems = [], []
    base = field_place(recipe, variant, 'files')
    for index, entry in enumerate(fields.get('files') or []):
        place = base + (index,)
        if 'stage' not in entry:
            found.append(ProjectFile(entry['from'], entry['to'], entry.get('atStep'), place))
            continue
        number = entry['stage']
        path = tutorial_files.page_tutorial_path(layout, recipe.page)
        relative = layout.relative(path)
        tutorial = tutorial_files.Tutorial(layout, path) if os.path.isfile(path) else None
        if tutorial is None or tutorial.data is None:
            problems.append((place + ('stage',), 'stage %d: the page has no tutorial %s%s: name single files with from and to' % (
                number, relative, ' that reads (%s)' % tutorial.error if tutorial is not None else '')))
            continue
        steps = [stage.get('step') for stage in tutorial.stages]
        if number not in steps:
            problems.append((place + ('stage',), 'stage %d: %s has no stage %d (its stages: %s): name one of them' % (
                number, relative, number, ', '.join(str(step) for step in steps) or 'none')))
            continue
        for stage in tutorial.stages:
            if not isinstance(stage.get('step'), int) or stage['step'] > number:
                continue
            for copy in stage.get('files') or []:
                if isinstance(copy, dict) and isinstance(copy.get('from'), str) and isinstance(copy.get('to'), str):
                    found.append(ProjectFile(copy['from'], copy['to'], entry.get('atStep'), place + ('stage',), stage['step']))
    return found, problems


def outside_project(target):
    parts = target.replace('\\', '/').split('/')
    return bool(c_AbsolutePath.match(target)) or '..' in parts or '' in parts or '.' in parts or parts[0] == '.strata'


def project_file_data(layout, engine, pin, item, read=True):
    """(the bytes of a recipe's file, or None without read or with a problem; the problem or None): a file of the book
    under tutorials/, or a stage's sample asset at the pin, of at most c_ProjectFileLimit bytes, whose target is inside
    the project."""
    prefix = 'stage %d copies %s: ' % (item.stage, item.source) if item.stage else ''
    if outside_project(item.target):
        return None, prefix + ('"%s" is outside the project (or in its .strata/): give a path relative to the project, without "..", such as '
                               'Scripts/Coin.cpp' % item.target)
    too_large = '%s has %d bytes, more than the %d a recipe copies into a project: copy a smaller file'
    if item.source.startswith('book:'):
        relative = item.source[len('book:'):]
        inside = relative.split('/')
        if inside[0] != 'tutorials' or '..' in inside or '' in inside or '.' in inside or '\\' in relative:
            return None, prefix + '"%s" is not a file under tutorials/: copy a tutorial\'s files or assets (book:tutorials/…)' % item.source
        path = os.path.join(layout.root, *inside)
        if not os.path.isfile(path):
            return None, prefix + 'the book has no file %s: name a file of the book, or write it' % relative
        size = os.path.getsize(path)
        if size > c_ProjectFileLimit:
            return None, prefix + too_large % (relative, size, c_ProjectFileLimit)
        return (read_bytes(path) if read else None), None
    if not c_SampleAsset.match(item.source) or '..' in item.source.split('/'):
        return None, prefix + '"%s" is neither book:tutorials/… nor a file under Samples/<sample>/Assets/ at the pin' % item.source
    if engine is None:
        return None, prefix + '%s is a file of the engine: give --engine' % item.source
    found = engine.object(pin, item.source)
    if found is None or found[0] != 'blob':
        return None, prefix + 'the engine has no file %s at the pin: name a file of Samples/<sample>/Assets/ there' % item.source
    if len(found[1]) > c_ProjectFileLimit:
        return None, prefix + too_large % (item.source, len(found[1]), c_ProjectFileLimit)
    return found[1], None


def step_holder(recipe, variant, fields):
    """(the steps atStep counts, how many there are): editorWindow.steps of an editor figure, the setup steps (the
    recipe's, then the variant's) of a scene figure."""
    if recipe.kind == 'editor':
        return 'editorWindow.steps', len((fields.get('editorWindow') or {}).get('steps') or [])
    steps = list(recipe.entry.get('setup') or []) + (list(recipe.entry['variants'][variant].get('setup') or []) if variant else [])
    return 'setup', len(steps)


def recipe_files(take, recipe, variant, fields):
    """The ProjectFiles of a figure being taken; TakeError on the first problem (check names them all)."""
    items, problems = project_files(take.layout, recipe, variant, fields)
    if problems:
        raise TakeError('files: ' + problems[0][1])
    return items


def copy_project_files(take, items, folder=None):
    """Writes recipe files into the project copy being taken (or into folder: a program's run folder); TakeError names
    the first that cannot be copied."""
    for item in items:
        data, problem = project_file_data(take.layout, take.engine, take.pin, item)
        if problem:
            raise TakeError('files: ' + problem)
        target = os.path.join(folder or take.project_directory, *item.target.replace('\\', '/').split('/'))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as file:
            file.write(data)


def make_project(session, project, directory, labs_folder, lookdev=None):
    """Makes the project copy of a recipe in the editor session; False when the recipe names no project (a command that
    needs none, such as project.templates, runs in the editor without one). A lab's files go into the project's asset
    folder and its script runs step by step, as StrataEditor --project <dir> --commands labs/<name>.json would run it.
    The look-dev project is copied from the one lookdev() made (Tools/LookDev.py capture, once per run) and opened."""
    if not project:
        return False
    if project.get('lookdev') and lookdev is not None:
        shutil.copytree(lookdev(), directory, ignore=shutil.ignore_patterns('.strata'))
        session.call('project.open', {'path': directory, 'force': True}, timeout=editor.c_OpenSeconds)
    elif 'sample' in project:
        session.call('project.openSample', {'sample': project['sample'], 'directory': directory}, timeout=editor.c_OpenSeconds)
    elif 'lab' in project:
        session.call('project.create', {'directory': directory, 'name': 'Lab', 'template': project['template']}, timeout=editor.c_OpenSeconds)
        name = os.path.basename(project['lab'])[:-5]
        assets = os.path.join(directory, 'Assets')
        lab_files = os.path.join(labs_folder, name)
        if os.path.isdir(lab_files):
            shutil.copytree(lab_files, assets, dirs_exist_ok=True)
        with open(os.path.join(labs_folder, name + '.json'), encoding='utf-8') as file:
            resolve_steps(session, json.load(file), {})
    elif 'template' in project:
        session.call('project.create', {'directory': directory, 'name': 'Figures', 'template': project['template']}, timeout=editor.c_OpenSeconds)
    else:
        raise TakeError('the look-dev project is made by Tools/LookDev.py capture, which needs the GPU: take it as a scene figure')
    return True


def project_key(project):
    return json.dumps(project, sort_keys=True)


def settings_record(session):
    result = session.call('project.settings', {})
    return {section.get('id'): section for section in result.get('sections', []) if isinstance(section, dict)}


def restore_settings(session, recorded):
    now = settings_record(session)
    for section_id, before in recorded.items():
        current = now.get(section_id)
        if current is None or current.get('value') == before.get('value'):
            continue
        if before.get('isDefault'):
            session.call('project.setSettings', {'section': section_id, 'reset': True})
        else:
            session.call('project.setSettings', {'section': section_id, 'value': before.get('value')})


def shot_steps(take, shot):
    """A shot's Setup ({Command, Parameters} in Tools/LookDev/Shots.json) as command steps: an entityName inside the
    parameters becomes the step's entityName, and a repoFile (an engine file for asset.import) the file's path in the
    clone, as Tools/LookDev.py resolves them."""
    steps = []
    for number, step in enumerate((shot or {}).get('Setup') or []):
        if not isinstance(step, dict) or not isinstance(step.get('Command'), str):
            raise TakeError('the Setup step %d of the shot %s in Tools/LookDev/Shots.json is no {Command, Parameters}' % (number, shot.get('Name')))
        parameters = json.loads(json.dumps(step.get('Parameters') or {}))
        converted = {'command': step['Command']}
        if 'entityName' in parameters:
            converted['entityName'] = parameters.pop('entityName')
        if 'repoFile' in parameters:
            file = os.path.join(take.engine.path, *parameters.pop('repoFile').split('/'))
            if not os.path.isfile(file):
                raise TakeError('the shot %s imports %s, which the clone lacks' % (shot.get('Name'), os.path.relpath(file, take.engine.path)))
            parameters['file'] = file
        converted['parameters'] = parameters
        steps.append(converted)
    return steps


def post_process_values(fields):
    """The PostProcess values of a figure: its anti-aliasing mode, then its postProcess properties."""
    values = dict(c_AntiAliasing[fields['antiAliasing']]) if fields.get('antiAliasing') else {}
    values.update(fields.get('postProcess') or {})
    return values


def bakes_probes(recipe, variant):
    steps = list(recipe.entry.get('setup') or []) + (list(recipe.entry['variants'][variant].get('setup') or []) if variant else [])
    return any(isinstance(step, dict) and step.get('command') == 'lighting.bakeProbes' for step in steps)


def run_setup(take, session, recipe, variant, fields, bound):
    """The recipe's and the variant's setup steps, with the files of atStep copied before their step."""
    setup = list(recipe.entry.get('setup') or []) + (list(recipe.entry['variants'][variant].get('setup') or []) if variant else [])
    later = [item for item in recipe_files(take, recipe, variant, fields) if item.at]
    start = 0
    for at in sorted({item.at for item in later}):
        resolve_steps(session, setup[start:at - 1], bound)
        copy_project_files(take, [item for item in later if item.at == at])
        start = at - 1
    resolve_steps(session, setup[start:], bound)


def prepare_figure(take, session, recipe, variant, fields, scene, shot, play=True):
    """Steps 1 to 5 of a figure on its project copy (plan/pipelines.md §5.4): the scene opened again with force, which
    drops what an earlier figure of the copy changed; world; a custom quality; the station's, the shot's, the recipe's
    and the variant's steps, then materials; anti-aliasing and postProcess on the scene's one PostProcess entity; play
    (unless play is False: a live figure starts its capture first). Returns (whether the game plays, so that play.stop
    ends it; the values the steps bound)."""
    bound = {}
    if scene:
        session.call('scene.open', {'scene': scene, 'force': True}, timeout=editor.c_OpenSeconds)
        session.call('scene.loadStatus', {'wait': True}, timeout=editor.c_OpenSeconds)
    if fields.get('world'):
        session.call('world.loadCells', {'region': c_WorldRegion, 'wait': True}, timeout=editor.c_OpenSeconds)
    quality = fields.get('quality')
    if isinstance(quality, dict):
        session.call('project.setSettings', {'section': 'Renderer.Quality', 'value': dict({'Preset': 'Custom'}, **quality['custom'])})
    if fields.get('station'):
        resolve_steps(session, station_steps(take, fields['station']), bound)
    resolve_steps(session, shot_steps(take, shot), bound)
    run_setup(take, session, recipe, variant, fields, bound)
    for material, properties in sorted((fields.get('materials') or {}).items()):
        session.call('material.set', {'material': material, 'properties': properties, 'save': False})
    values = post_process_values(fields)
    if values:
        found = session.call('entity.find', {'component': 'PostProcess'})
        entities = found.get('entities', []) if isinstance(found, dict) else []
        if len(entities) != 1:
            raise TakeError('the scene holds %d PostProcess entities; antiAliasing and postProcess need exactly one' % len(entities))
        entity = entities[0].get('id', entities[0]) if isinstance(entities[0], dict) else entities[0]
        session.call('component.set', {'entity': entity, 'component': 'PostProcess', 'values': values})
    if not play:
        return False, bound
    play = fields.get('play')
    if not play:
        return False, bound
    session.call('play.start', {'paused': True})
    try:
        if play.get('input'):
            session.call('input.sequence', {'events': play['input'], 'steps': play['steps']})
        else:
            session.call('play.step', {'steps': play['steps']})
    except (TakeError, editor.EditorError):
        session.call('play.stop', {})  # so that the next figure of the copy opens its scene in edit mode
        raise
    return True, bound


def take_text_command(take, session, recipe, variant, fields, scene, shot):
    playing, bound = prepare_figure(take, session, recipe, variant, fields, scene, shot)
    try:
        command = fields['text']['command']
        texts = []
        results = []
        compared = []
        for _ in range(2):
            result = session.call(command['command'], substitute(command.get('parameters') or {}, bound))
            results.append(result)
            value = kept(result, fields['text']['keep'])
            texts.append(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
            compared.append(without_measured(value, fields['text'].get('measured', [])))
        problem = privacy_problem(texts[0], take.work, 'the text')
        if problem:
            raise TakeError('%s: keep values that hold no path of the machine' % problem[0])
        if compared[0] != compared[1]:
            raise TakeError('two runs of %s gave different text: the figure is nondeterministic, or name its measurements in measured '
                            '(both are in %s)' % (command['command'], take.log.folder))
        take.write_text(recipe, variant, texts[0], results[0], fields.get('record'))
    finally:
        if playing:
            session.call('play.stop', {})


def capture_parameters(fields, shot):
    """viewport.capture's parameters of a still figure, every one explicit (plan/pipelines.md §5.4 step 6): the size, the
    shot's or the recipe's camera, overlays, the quality (a preset, or "project" for a custom one), the debug view (the
    recipe's, else the shot's DebugView, else none) and waitForAssets."""
    width, height = fields.get('size') or c_DefaultSize
    parameters = {'width': width, 'height': height}
    camera = fields.get('camera')
    if shot:
        if shot.get('Camera') == 'scene':
            parameters['camera'] = 'scene'
        elif 'Position' in shot and 'Target' in shot:
            parameters.update({'position': shot['Position'], 'target': shot['Target']})
            if 'Fov' in shot:
                parameters['fov'] = shot['Fov']
        else:
            raise TakeError('the shot %s has neither Camera "scene" nor Position and Target: choose another shot' % shot.get('Name'))
    elif camera == 'scene':
        parameters['camera'] = 'scene'
    elif isinstance(camera, dict):
        parameters.update({'position': camera['position'], 'target': camera['target']})
        if 'fov' in camera:
            parameters['fov'] = camera['fov']
    else:
        raise TakeError('the recipe names no camera: give camera or shot')
    quality = fields.get('quality', 'high')
    parameters['overlays'] = bool(fields.get('overlays', False))
    parameters['quality'] = 'project' if isinstance(quality, dict) else quality
    parameters['debugView'] = fields.get('debugView') or (shot or {}).get('DebugView') or 'none'
    parameters['waitForAssets'] = fields.get('waitForAssets', True)
    if fields.get('renderer'):
        parameters['renderer'] = dict(fields['renderer'])
    return parameters


def incomplete(result, fields, debug_view):
    """What keeps a capture's result from being complete (plan/pipelines.md §5.3): the complete set, temporalFrames for
    TAA, the shadows view's own flag, expectAlso, less what relax removes, and no notice. A recipe that leaves the
    scene's anti-aliasing as it is cannot know whether TAA draws it: then a history of 1 to 7 frames is incomplete."""
    relaxed = fields.get('relax') or {}
    conditions = {pointer: condition for pointer, condition in c_Complete.items() if pointer not in ('/temporalFrames', '/debugView/shadows/complete')}
    if fields.get('antiAliasing') == 'taa':
        conditions['/temporalFrames'] = c_Complete['/temporalFrames']
    if debug_view == 'shadows':
        conditions['/debugView/shadows/complete'] = c_Complete['/debugView/shadows/complete']
    conditions.update(fields.get('expectAlso') or {})
    problems = []
    for pointer, condition in sorted(conditions.items()):
        if pointer in relaxed:
            continue
        try:
            value = resolve_pointer(result, pointer)
        except KeyError:
            problems.append('%s is missing from the result' % pointer)
            continue
        number = isinstance(value, (int, float)) and not isinstance(value, bool)
        if 'equals' in condition and value != condition['equals']:
            problems.append('%s is %s, %s wanted' % (pointer, json.dumps(value), json.dumps(condition['equals'])))
        if 'min' in condition and (not number or value < condition['min']):
            problems.append('%s is %s, at least %s wanted' % (pointer, json.dumps(value), condition['min']))
        if 'max' in condition and (not number or value > condition['max']):
            problems.append('%s is %s, at most %s wanted' % (pointer, json.dumps(value), condition['max']))
    frames = result.get('temporalFrames') if isinstance(result, dict) else None
    if not fields.get('antiAliasing') and '/temporalFrames' not in relaxed and isinstance(frames, int) and 0 < frames < 8:
        problems.append('/temporalFrames is %d: the scene draws with TAA, and its history holds fewer than 8 frames' % frames)
    if isinstance(result, dict) and result.get('notice'):
        problems.append('the result has a notice: %s' % result['notice'])
    return problems


def take_scene(take, session, recipe, variant, fields, scene, shot):
    """A still figure (plan/pipelines.md §5.4 steps 1 to 7, §5.6): two captures with the same parameters, which must be
    complete and byte-identical; the first capture's PNG file is the original."""
    stem = picture_stem(recipe, variant)
    playing, _ = prepare_figure(take, session, recipe, variant, fields, scene, shot)
    parameters = capture_parameters(fields, shot)
    pictures, results = [], []
    try:
        for number in range(2):
            path = os.path.join(take.work, 'log', '%s-%d.png' % (stem, number))
            result = session.call('viewport.capture', dict(parameters, path=path, overwrite=True))
            if isinstance(result, dict):
                result.pop('Image', None)
            results.append(result)
            if not os.path.isfile(path):
                raise TakeError('viewport.capture wrote no picture to %s' % path)
            pictures.append(read_bytes(path))
    finally:
        if playing:
            session.call('play.stop', {})
    write_json(os.path.join(take.work, 'results', stem + '.json'), results[0])
    problems = incomplete(results[0], fields, parameters['debugView'])
    if problems:
        raise TakeError('incomplete: %s (results/%s.json holds the result): correct the recipe so that the view loads and settles, or '
                        'relax a condition with its reason' % ('; '.join(problems), stem))
    pair = pair_difference(pictures[0], pictures[1])
    if not same_picture(pair):
        folder = os.path.join(take.work, 'nondeterministic', stem)
        os.makedirs(folder, exist_ok=True)
        for number in range(2):
            with open(os.path.join(folder, 'capture-%d.png' % number), 'wb') as file:
                file.write(pictures[number])
            write_json(os.path.join(folder, 'result-%d.json' % number), results[number])
        raise TakeError('the two captures differ in %d pixel%s (%s per cent), by up to %d level%s: nondeterministic (both and their results '
                        'are in %s); take it once more alone (--figures %s/%s: a fresh editor on a fresh copy), and report it to the planner '
                        'with the images if they differ again'
                        % (pair['pixels'], '' if pair['pixels'] == 1 else 's', ('%.3f' % pair['percent']).rstrip('0').rstrip('.'), pair['largest'],
                           '' if pair['largest'] == 1 else 's', folder, recipe.page, recipe.id))
    wanted = fields.get('renderer') or {}
    echoed = results[0].get('renderer') if isinstance(results[0], dict) else None
    if wanted and isinstance(echoed, dict) and any(name not in echoed or echoed[name] != value for name, value in wanted.items()):
        raise TakeError('the capture drew with the renderer switches %s, not %s (results/%s.json holds the result): name switches the pin\'s '
                        'viewport.capture takes (figures.py check)' % (json.dumps(echoed, sort_keys=True), json.dumps(wanted, sort_keys=True), stem))
    recorded = {}
    for name, pointer in (fields.get('record') or {}).items():
        try:
            recorded[name] = resolve_pointer(results[0], pointer)
        except KeyError:
            raise TakeError('record %s: the result has no %s: record a pointer the result has' % (name, pointer))
    take.picture(recipe, variant, None, 'scene', shot, data=pictures[0], recorded=recorded, pair=pair, renderer=wanted)


def live_window(fields):
    """The window of a live figure's editor: the Game view's size with room around it for the editor's other panels."""
    width, height = fields.get('size') or c_DefaultSize
    return [min(width + c_LiveWindowMargin[0], c_LiveWindowLargest[0]), min(height + c_LiveWindowMargin[1], c_LiveWindowLargest[1])]


def new_copy_folder(take, stem, number):
    """<work>/projects/<picture>-take-<n>: a live take's own copy, beside the numbered copies of the other kinds."""
    folder = os.path.join(take.work, 'projects')
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, '%s-take-%d' % (stem, number))


def make_copy(take, recipe, variant, fields, directory):
    """A fresh copy of a recipe's project, made in an editor without a window (--no-gpu), with the recipe's files that
    go in before the editor opens it."""
    session = editor.Editor(take.build, take.work, take.log)
    try:
        session.launch()
        take.status = session.check_commit(take.pin, take.provisional)
        make_project(session, fields.get('project') or {}, directory, os.path.join(take.layout.root, 'labs'), take.lookdev)
    finally:
        session.quit()
    take.project_directory = directory
    copy_project_files(take, [item for item in recipe_files(take, recipe, variant, fields) if not item.at])


def run_play(session, play):
    if play.get('input'):
        session.call('input.sequence', {'events': play['input'], 'steps': play['steps']}, timeout=editor.c_OpenSeconds)
    else:
        session.call('play.step', {'steps': play['steps']}, timeout=editor.c_OpenSeconds)


def live_capture(take, recipe, variant, fields, scene, shot, folder):
    """One take of a live figure (plan/pipelines.md §5.4): a fresh copy, an editor in a window that serves automation,
    the recipe's quality preset and the players' options reset, the Game view at the recipe's size, steps 1, 3 and 4,
    play.start paused, viewport.capture {live} started before the steps run, the steps, its answer, play.stop. Returns
    the capture's result ({live, camera, images: [{fixedSteps, temporalFrames, width, height, path}]})."""
    directory = new_copy_folder(take, picture_stem(recipe, variant), int(os.path.basename(folder).rsplit('-', 1)[1]))
    make_copy(take, recipe, variant, fields, directory)
    width, height = fields.get('size') or c_DefaultSize
    live = fields['live']
    quality = fields.get('quality', 'high')
    layouts = os.path.join(take.work, 'layouts')
    os.makedirs(layouts, exist_ok=True)
    # A layout file of the run's own: the editor lays its panels out as on a first start and writes them there.
    window = {'size': live_window(fields), 'layout': os.path.join(layouts, '%s.ini' % os.path.basename(folder))}
    session = editor.Editor(take.build, take.work, take.log, project=directory, gpu=True, window=window)
    started = None
    try:
        session.launch()
        take.status = session.check_commit(take.pin, take.provisional)
        if not isinstance(quality, dict):
            session.call('project.setSettings', {'section': 'Renderer.Quality', 'value': {'Preset': c_PresetNames[quality]}})
        session.call('graphics.resetPlayerOptions', {})
        session.call('editor.showPanel', {'panel': 'Game'})
        session.call('viewport.setSettings', {'gameView': {'mode': 'custom', 'width': width, 'height': height}})
        prepare_figure(take, session, recipe, variant, fields, scene, shot, play=False)
        session.call('play.start', {'paused': True}, timeout=editor.c_OpenSeconds)
        try:
            started = session.start_call('viewport.capture', {'live': True, 'camera': 'scene', 'atFixedStep': live['atFixedStep'],
                                                              'frames': live['frames'], 'path': os.path.join(folder, 'frame.png'), 'overwrite': True},
                                         timeout=editor.c_OpenSeconds)
            run_play(session, fields['play'])
            result = session.finish_call('viewport.capture', started, editor.c_OpenSeconds)
            started = None
        finally:
            session.call('play.stop', {})
    finally:
        session.quit()
        if started is not None:
            try:
                started.finish(editor.c_QuitSeconds)
            except editor.EditorError:
                pass
    images_found = result.get('images') if isinstance(result, dict) else None
    if not isinstance(images_found, list) or len(images_found) != live['frames']:
        raise TakeError('the live capture returned %s images, not the %d frames asked for: look at its answer in %s' % (
            len(images_found) if isinstance(images_found, list) else 'no', live['frames'], take.log.folder))
    for image in images_found:
        if not isinstance(image, dict) or not os.path.isfile(str(image.get('path'))):
            raise TakeError('the live capture names a frame it did not write: %s' % json.dumps(image))
        if [image.get('width'), image.get('height')] != [width, height]:
            raise TakeError('the live capture presented %sx%s pixels, not the Game view\'s %dx%d: the window (%dx%d) must hold the Game view; take a '
                            'smaller size' % (image.get('width'), image.get('height'), width, height, window['size'][0], window['size'][1]))
    write_json(os.path.join(folder, 'result.json'), result)
    return result


def take_live(take, recipe, variant, fields, scene, shot):
    """A live figure (plan/pipelines.md §5.4, §5.6): c_LiveTakes takes, each in a fresh editor on a fresh copy, whose
    frames must have the same fixedSteps and camera; the first take's last frame is the original, and every take's
    frames stay in live/<picture>/take-<n>/ for the photographer, who judges them by eye."""
    stem = picture_stem(recipe, variant)
    if not fields.get('play') or not fields.get('live'):
        raise TakeError('a live figure needs live {atFixedStep, frames} and play {steps}: run figures.py check')
    if (fields.get('project') or {}).get('lookdev'):
        take.lookdev()  # before this figure's editors start, so that LookDev.py's editor runs alone
    results = []
    for number in range(1, c_LiveTakes + 1):
        folder = os.path.join(take.work, 'live', stem, 'take-%d' % number)
        os.makedirs(folder, exist_ok=True)
        results.append(live_capture(take, recipe, variant, fields, scene, shot, folder))
    signature = lambda result: ([image.get('fixedSteps') for image in result['images']], result.get('camera'))
    if any(signature(result) != signature(results[0]) for result in results[1:]):
        raise TakeError('the %d live takes differ in their fixed steps or camera (%s): the figure is not repeatable; their frames are in %s' % (
            c_LiveTakes, '; '.join('take %d: %s' % (number + 1, json.dumps(signature(result))) for number, result in enumerate(results)),
            os.path.join(take.work, 'live', stem)))
    write_json(os.path.join(take.work, 'results', stem + '.json'), results[0])
    recorded = {}
    for name, pointer in (fields.get('record') or {}).items():
        try:
            recorded[name] = resolve_pointer(results[0], pointer)
        except KeyError:
            raise TakeError('record %s: the live capture\'s result has no %s: record a pointer it has' % (name, pointer))
    take.picture(recipe, variant, None, 'live', shot, data=read_bytes(results[0]['images'][-1]['path']), recorded=recorded)


def has_scripts(directory):
    return os.path.isfile(os.path.join(directory, 'Scripts', 'CMakeLists.txt'))


def take_runtime(take, session, recipe, variant, fields, scene, shot):
    """A runtime figure (plan/pipelines.md §5.4): on the copy the session made, the recipe's setup steps (which save what
    they change: the game draws what the project saved), script.build when the project has scripts, project.export into
    <work>/export/<picture>, then the exported game in a window of the recipe's resolution for its seconds of game time
    at its quality, its saves in a new folder, its last frame saved by --screenshot. Exit code 0 is required."""
    stem = picture_stem(recipe, variant)
    if not os.path.isfile(editor.program_path(take.build, 'StrataRuntime')):
        # project.export copies the runtime that stands next to the editor.
        raise TakeError('the build %s has no StrataRuntime, which project.export copies into the game: build the pin (pipelines.md §1.3)' % take.build)
    run_setup(take, session, recipe, variant, fields, {})
    if has_scripts(take.project_directory):
        session.call('script.build', {'wait': True}, timeout=editor.c_OpenSeconds)
    folder = os.path.join(take.work, 'export', stem)
    exported = session.call('project.export', {'directory': folder}, timeout=editor.c_OpenSeconds)
    executable = exported.get('executable') if isinstance(exported, dict) else None
    if not isinstance(executable, str) or not os.path.isfile(executable):
        raise TakeError('project.export made no game executable (its answer names %s): look at its answer in %s' % (json.dumps(executable), take.log.folder))
    runtime = fields['runtime']
    width, height = runtime['resolution']
    saves = os.path.join(take.work, 'saves', stem)
    os.makedirs(saves, exist_ok=True)
    picture = os.path.join(take.work, 'log', stem + '-runtime.png')
    seconds = int(runtime['seconds'])
    arguments = [executable, '--windowed', '--resolution', '%dx%d' % (width, height), '--seconds', str(seconds), '--quality', runtime['quality'],
                 '--save-directory', saves, '--screenshot', picture]
    code, output, _ = editor.run_program(arguments, editor.environment(take.build, take.work, editor.new_session_dir()), take.log, 'runtime-' + stem,
                                         seconds + editor.c_OpenSeconds, cwd=os.path.dirname(executable))
    if code != 0:
        raise TakeError('the exported game exited with %d: %s' % (code, editor.last_line(output)))
    if not os.path.isfile(picture):
        raise TakeError('the exported game saved no screenshot: look at its output in %s' % take.log.folder)
    data = read_bytes(picture)
    size = list(images.size_of(data, 'the screenshot of %s' % stem))
    if size != [width, height]:
        raise TakeError('the exported game\'s screenshot is %dx%d, not the window\'s %dx%d: take a resolution the display holds' % (size[0], size[1], width, height))
    take.picture(recipe, variant, None, 'runtime', shot, data=data)


def station_steps(take, station):
    script = os.path.join(take.engine.path, 'Tools', 'GenerateShowcaseTerrain.py')
    code, output, errors = editor.run_program([sys.executable, '-I', script, 'setup', '--station', station, '--format', 'script'], dict(os.environ),
                                              take.log, 'station-' + station, editor.c_CallSeconds, merge=False)
    if code != 0:
        raise TakeError('Tools/GenerateShowcaseTerrain.py setup --station %s failed: %s' % (station, editor.last_line(errors or output)))
    try:
        steps = json.loads(output)
    except ValueError:
        raise TakeError('Tools/GenerateShowcaseTerrain.py setup --station %s printed no command script (its output is in the take\'s log)' % station)
    return steps


def take_text_program(take, recipe, variant, fields):
    text = fields['text']
    program = text['program']
    if program == 'ctest':
        found = shutil.which('ctest')
        if not found:
            raise TakeError('ctest is not on the PATH: put the ctest of CMake 3.25 or later on the PATH')
        arguments = [found] + text['arguments']
    else:
        arguments = [editor.program_path(take.build, program)] + text['arguments']
    env = editor.environment(take.build, take.work, editor.new_session_dir())
    # A program given files runs in a fresh run folder per run, with the files staged in it, which it sees as the root
    # of a drive of its own; without files it runs in the build, as the reader runs it there.
    items = recipe_files(take, recipe, variant, fields) if fields.get('files') else []
    outputs = []
    for number in range(2):
        if items:
            folder = os.path.join(take.work, 'runs', '%s-%d' % (picture_stem(recipe, variant), number + 1))
            os.makedirs(os.path.join(folder, c_NeutralEditor))
            copy_project_files(take, items, folder)
            root, release = map_drive(folder, work=take.work)
            try:
                code, output, _ = editor.run_program(arguments, neutral_environment(env, root), take.log, program, editor.c_CallSeconds, cwd=root)
            finally:
                release()
        else:
            code, output, _ = editor.run_program(arguments, env, take.log, program, editor.c_CallSeconds, cwd=take.build)
        outputs.append(redact(output, text.get('redact', [])))
        problem = privacy_problem(outputs[-1], take.work, 'the text')
        if problem:
            raise TakeError('%s: give the program files and relative paths, or redact the path' % problem[0])
    if redact(outputs[0], text.get('measured', [])) != redact(outputs[1], text.get('measured', [])):
        raise TakeError('two runs of %s gave different text after redact: add a redact expression for what varies, or choose '
                        'another output' % ' '.join([program] + text['arguments']))
    take.write_text(recipe, variant, outputs[0].rstrip('\n') + '\n', None, None)


def reference_toolchain(engine, pin):
    """(the C++ compiler, the clone's glm) that reference figures are compiled with, as tools/sketches.py compiles
    sketches (pipelines.md §4, §5.4). Found before anything starts: a missing compiler or a glm at another commit than
    the pin records is an environment error, exit 2."""
    import sketches
    try:
        return sketches.find_compiler('leave reference out of --kinds'), sketches.glm_include(engine, pin)
    except sketches.UsageError as error:
        raise UsageError('reference figures: %s' % error)


def take_reference(take, recipe, variant, fields, shot):
    import sketches
    sketch = os.path.join(take.layout.sketches, fields['reference']['sketch'])
    if not os.path.isfile(sketch):
        raise TakeError('sketches/%s does not exist: write the sketch, or correct its name in the recipe' % fields['reference']['sketch'])
    compiler, glm = take.toolchain
    program = os.path.join(take.work, 'log', os.path.splitext(fields['reference']['sketch'])[0] + ('.exe' if os.name == 'nt' else ''))
    try:
        sketches.compile_cpp(compiler, sketch, program, True, glm)
    except sketches.SketchError as error:
        raise TakeError(str(error))
    images_out = []
    for _ in range(2):
        result = subprocess.run([program] + fields['reference'].get('arguments', []), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=sketches.environment_for(compiler))
        take.log.write(os.path.basename(program), [program], result.stderr.decode('utf-8', 'replace'), result.returncode)
        if result.returncode != 0:
            raise TakeError('sketches/%s exited with %d: make it end with exit code 0' % (fields['reference']['sketch'], result.returncode))
        images_out.append(result.stdout)
    if images_out[0] != images_out[1]:
        raise TakeError('two runs of sketches/%s gave different images: a reference sketch uses a fixed random seed' % fields['reference']['sketch'])
    try:
        image = images.read_sketch_ppm(images_out[0], 'the output of sketches/%s' % fields['reference']['sketch'], os.name == 'nt')
    except images.ImageError as error:
        raise TakeError(str(error))
    take.picture(recipe, variant, image, 'reference', shot)


def take_tool(take, recipe, variant, fields, shot):
    node = shutil.which('node')
    if not node:
        raise UsageError('node is not on the PATH: source .tools/env.sh first (tool pictures use the site\'s pinned Playwright)')
    shots = []
    for number in range(2):
        target = os.path.join(take.work, 'log', '%s-%d.png' % (picture_stem(recipe, variant), number))
        code, output, _ = editor.run_program([node, c_Screenshot, fields['url'], target], dict(os.environ), take.log, 'screenshot', editor.c_CallSeconds)
        if code != 0:
            raise TakeError('screenshot-page.mjs failed: %s' % editor.last_line(output))
        shots.append(read_bytes(target))
    first = images.read_png(shots[0], 'the screenshot')
    second = images.read_png(shots[1], 'the screenshot')
    if first.data != second.data:
        take.skipped.append('%s: skipped: %s: the two screenshots differ; judge it by eye (the first is kept)' % take_label(recipe, variant))
    take.picture(recipe, variant, first, 'tool', shot)


def take_label(recipe, variant):
    """(<manifest>:<line>, <page>/<figure>[.<variant>]) of a figure, for the lines of take's report."""
    return recipe.where(*(('variants', variant) if variant else ())), '%s/%s%s' % (recipe.page, recipe.id, '.' + variant if variant else '')


def take(layout, engine, pin, build, work, pattern, kinds, provisional=False):
    recipes = [recipe for recipe in load_recipes(layout) if recipe.kind in kinds and matches_figures(recipe, pattern)]
    references = any(recipe.kind == 'reference' and not fields.get('waitsFor') for recipe in recipes for _, fields in recipe.variants())
    toolchain = reference_toolchain(engine, pin) if references else None
    prepare_work(work)
    log = editor.Log(os.path.join(work, 'log'))
    runner = Take(layout, engine, pin, build, work, log)
    runner.toolchain = toolchain
    runner.provisional = provisional
    pin_data = Pin(engine, pin)
    projects, shots = pin_data.shots()
    labs = read_labs(layout)
    if build:
        status_editor = editor.Editor(build, work, log)
        try:
            status_editor.launch()
            runner.status = status_editor.check_commit(pin, provisional)
        finally:
            status_editor.quit()
    groups = {}
    for recipe in recipes:
        for variant, fields in recipe.variants():
            if fields.get('waitsFor') and provisional and fields['waitsFor'] in c_Additions:
                runner.notes.append('%s: provisional: %s waits for %s at the pin; taken with the provisional build (keep waitsFor)' % (
                    take_label(recipe, variant) + (fields['waitsFor'],)))
            elif fields.get('waitsFor'):
                runner.skipped.append('%s: skipped: %s waits for %s; take it once the pin has that addition' % (
                    take_label(recipe, variant) + (fields['waitsFor'],)))
                continue
            if fields.get('blocked'):
                runner.skipped.append('%s: skipped: %s: no take makes it at the pin (blocked: %s)' % (take_label(recipe, variant) + (fields['blocked'],)))
                continue
            if recipe.kind == 'tool' and fields.get('takenBy') == 'owner':
                runner.skipped.append('%s: skipped: %s: the owner takes it (takenBy "owner")' % take_label(recipe, variant))
                continue
            if recipe.kind == 'scene' and fields.get('baseline'):
                runner.skipped.append('%s: skipped: %s: a "before" picture (baseline %s) comes from the look-dev baseline sets, which take '
                                      'does not copy yet' % (take_label(recipe, variant) + (fields['baseline'],)))
                continue
            problem = next((found for found in (privacy_problem(value, work, 'the recipe') for _, value in walk_strings(fields)) if found), None)
            if problem:
                runner.failures.append('%s: failed: %s: %s in "%s": a picture never shows a path of the machine' % (take_label(recipe, variant) + problem))
                continue
            if recipe.kind not in ('scene', 'editor', 'live', 'runtime') and (recipe.kind != 'text' or 'command' not in (fields.get('text') or {})):
                groups.setdefault('', []).append((recipe, variant, fields, None))
                continue
            project = fields.get('project') or {}
            if project.get('lookdev') and recipe.kind == 'text':
                # The other text figures are still taken now (pipelines.md §13, phase A); these wait for the GPU.
                runner.skipped.append('%s: skipped: %s: the look-dev project is made by Tools/LookDev.py capture, which needs the GPU: '
                                      'take it in phase B, after engine release 0.8.0' % take_label(recipe, variant))
                continue
            scene, _, problem = figure_scene(recipe, fields, shots.get(recipe.entry.get('shot')), projects, pin_data, labs) if project else (None, None, None)
            if problem:
                runner.failures.append('%s: failed: %s: %s: run figures.py check' % (take_label(recipe, variant) + (problem,)))
                continue
            if recipe.kind == 'live':
                # Three takes, each with a copy and an editor of its own (take_live).
                groups.setdefault('live ' + take_label(recipe, variant)[1], []).append((recipe, variant, fields, scene))
                continue
            # Scene figures share editors with the GPU; text figures of commands editors without (--no-gpu); a runtime
            # figure gets a copy and an export of its own.
            key = ('gpu ' if recipe.kind == 'scene' else 'window ' if recipe.kind == 'editor' else 'runtime ' if recipe.kind == 'runtime' else '') + project_key(project)
            if recipe.kind == 'runtime':
                key += ' %s' % take_label(recipe, variant)[1]
            if fields.get('files'):
                # Copies with other files differ; files copied at a step change the copy for the figures after it.
                key += ' files ' + json.dumps(fields['files'], sort_keys=True)
            if recipe.kind == 'editor' or (project and (scene is None or bakes_probes(recipe, variant))) or any(
                    'atStep' in entry for entry in fields.get('files') or []):
                # An editor figure's window shows what earlier figures left (selection, panels, the Console): one editor each.
                # Nothing to open again would drop an earlier figure's changes, and a bake moves the previous capture to
                # the trash: such a figure gets a copy of its own (§5.4).
                key += ' %s' % take_label(recipe, variant)[1]
            groups.setdefault(key, []).append((recipe, variant, fields, scene))
    for key, items in sorted(groups.items()):
        if not key:
            for recipe, variant, fields, _ in items:
                try:
                    if recipe.kind == 'text':
                        take_text_program(runner, recipe, variant, fields)
                    elif recipe.kind == 'reference':
                        take_reference(runner, recipe, variant, fields, shots.get(recipe.entry.get('shot')))
                    elif recipe.kind == 'tool':
                        take_tool(runner, recipe, variant, fields, shots.get(recipe.entry.get('shot')))
                except (TakeError, editor.EditorError) as error:
                    runner.failures.append('%s: failed: %s: %s' % (take_label(recipe, variant) + (error,)))
            continue
        if key.startswith('live '):
            for recipe, variant, fields, scene in items:
                try:
                    take_live(runner, recipe, variant, fields, scene, shots.get(recipe.entry.get('shot')))
                except (TakeError, editor.EditorError) as error:
                    runner.failures.append('%s: failed: %s: %s' % (take_label(recipe, variant) + (error,)))
            continue
        project = items[0][2].get('project') or {}
        directory = os.path.join(work, 'projects', '%02d' % (len(os.listdir(os.path.join(work, 'projects'))) + 1))
        runner.window = None
        runner.drive_folder = None
        runner.project_directory = directory
        if key.startswith('window '):
            # The window sees this folder as the root of a drive (take_editor), its project copy as Projects/<its name>.
            runner.drive_folder = directory
            runner.project_directory = os.path.join(directory, c_NeutralProjects, project_folder(project)) if project else None
            os.makedirs(os.path.join(directory, c_NeutralProjects))
            try:
                runner.window = editor_window(runner, *items[0][:3])
            except TakeError as error:
                runner.failures.append('%s: failed: %s: %s' % (take_label(*items[0][:2]) + (error,)))
                continue
        session = editor.Editor(build, work, log, gpu=key.startswith(('gpu ', 'runtime ')))
        try:
            if project.get('lookdev'):
                runner.lookdev()  # before this group's editor starts, so that LookDev.py's editor runs alone
            session.launch()
            runner.status = session.check_commit(pin, provisional)
            made = make_project(session, project, runner.project_directory, os.path.join(layout.root, 'labs'), runner.lookdev)
            if made and key.startswith(('gpu ', 'runtime ')) and items[0][2].get('files'):
                # The files go in before the figures' steps; the editor opens the copy again, so that it sees them.
                copy_project_files(runner, [item for item in recipe_files(runner, *items[0][:3]) if not item.at])
                session.call('project.open', {'path': directory, 'force': True}, timeout=editor.c_OpenSeconds)
            recorded = settings_record(session) if made and not runner.window and not key.startswith('runtime ') else None
            for recipe, variant, fields, scene in items:
                try:
                    taker = {'scene': take_scene, 'editor': take_editor, 'runtime': take_runtime}.get(recipe.kind, take_text_command)
                    taker(runner, session, recipe, variant, fields, scene, shots.get(recipe.entry.get('shot')))
                except (TakeError, editor.EditorError) as error:
                    runner.failures.append('%s: failed: %s: %s' % (take_label(recipe, variant) + (error,)))
                finally:
                    if recorded is not None:
                        restore_settings(session, recorded)
        except (TakeError, editor.EditorError) as error:
            runner.failures.append('%s: failed: the project %s of %s: %s' % (items[0][0].where('project'), project_key(project),
                                                                           take_label(*items[0][:2])[1], error))
        finally:
            session.quit()
    pending = {'pin': pin, 'pictures': runner.pending}
    if provisional:
        pending['provisional'] = {'reportedCommit': (runner.status or {}).get('engineCommit')}
    write_json(os.path.join(work, 'taken-pending.json'), pending)
    return runner


def window_size(fields):
    return list((fields.get('editorWindow') or {}).get('windowSize') or c_EditorWindow)


def layout_window(path):
    """[width, height] of the window a layout file was made for (its first line), or None when it does not say."""
    with open(path, encoding='utf-8', errors='replace') as file:
        found = c_LayoutHeader.match(file.readline())
    return [int(found.group('width')), int(found.group('height'))] if found else None


def parse_window_size(text):
    found = re.match(r'^([0-9]{3,4})x([0-9]{3,4})$', text or '')
    size = [int(found.group(1)), int(found.group(2))] if found else None
    if not size or size[0] < c_EditorMinimumWindow[0] or size[1] < c_EditorMinimumWindow[1] or max(size) > 4096:
        raise UsageError('--window-size takes <width>x<height> in pixels, at least %dx%d and at most 4096 each, e.g. 1280x720' % c_EditorMinimumWindow)
    return size


def editor_window(take, recipe, variant, fields):
    """The window of an editor figure: its size and a copy of its layout in <work>/layouts (the editor writes the file it
    keeps the layout in); TakeError when the layout is missing or made for another window."""
    name = fields['editorWindow']['layout']
    source = os.path.join(take.layout.root, *name.split('/'))
    if not os.path.isfile(source):
        raise TakeError('the layout %s does not exist: make it with figures.py layout %s (plan/card/photo-editor.md)' % (name, os.path.basename(name)[:-4]))
    size = window_size(fields)
    made = layout_window(source)
    if made and made != size:
        raise TakeError('the layout %s was made for a window of %dx%d, not %dx%d: make a layout for that window, or take the figure at %dx%d'
                        % ((name,) + tuple(made) + tuple(size) + tuple(made)))
    folder = os.path.join(take.work, 'layouts')
    os.makedirs(folder, exist_ok=True)
    copy = os.path.join(folder, picture_stem(recipe, variant) + '.ini')
    shutil.copyfile(source, copy)
    return {'size': size, 'layout': copy}


def script_steps_of(steps, counter):
    """Command steps as the editor's command script takes them: entityName becomes entity.find {name} bound to a name of
    the tool's, which the step gets as its entity (the first match; check sees that the scene holds the name once)."""
    out = []
    for step in steps:
        if step.get('command') in script_steps.c_RefusedCommands:
            raise TakeError('%s changes the person\'s preferences, which no tool does (pipelines.md §2): use a project setting' % step['command'])
        step = {key: value for key, value in step.items() if key in script_steps.c_ScriptKeys or key == 'entityName'}
        if 'entityName' in step:
            counter[0] += 1
            name = 'figuresEntity%d' % counter[0]
            out.append({'command': 'entity.find', 'parameters': {'name': step.pop('entityName')}, 'bind': {name: '/entities/0'}})
            step['parameters'] = dict(step.get('parameters') or {}, entity={'$ref': name})
        out.append(step)
    return out


def editor_scripts(take, recipe, variant, fields, scene, shot, path, breaks=(), settle_first=False):
    """The command scripts of an editor figure's windows (plan/pipelines.md §5.4): one, and one more for each step of
    editorWindow.steps in breaks (1 for the first), before which the window closes so that files are copied; each later
    window opens the scene again and runs the rest. Values the steps bind do not cross from one window to the next.
    With settle_first (an agent sends the steps) the frames waited for come before editorWindow.steps, so that what the
    last step leaves for a moment (the Scene view's flash of an agent's edit, 0.6 s) is still drawn at the screenshot."""
    for field in ('quality', 'materials', 'antiAliasing', 'postProcess', 'world'):
        if fields.get(field):
            raise TakeError('%s: an editor figure takes no %s: put the commands that set it in editorWindow.steps' % (field, field))
    counter = [0]
    steps = []
    if scene:
        steps.append({'command': 'scene.open', 'parameters': {'scene': scene, 'force': True}})
        steps.append({'command': 'scene.loadStatus', 'parameters': {'wait': True}})
    if fields.get('station'):
        steps += script_steps_of(station_steps(take, fields['station']), counter)
    steps += script_steps_of(recipe.entry.get('setup') or [], counter)
    if variant:
        steps += script_steps_of(recipe.entry['variants'][variant].get('setup') or [], counter)
    play = fields.get('play')
    if play and breaks:
        raise TakeError('files: atStep closes the window, which ends play: leave play out, or copy before the editor opens the project')
    if play:
        steps.append({'command': 'play.start', 'parameters': {'paused': True}})
        if play.get('input'):
            steps.append({'command': 'input.sequence', 'parameters': {'events': play['input'], 'steps': play['steps']}})
        else:
            steps.append({'command': 'play.step', 'parameters': {'steps': play['steps']}})
    window = fields['editorWindow'].get('steps') or []
    scripts = []
    start = 0
    settle = {'command': 'editor.wait', 'parameters': {'frames': c_EditorSettleFrames}}
    if settle_first:
        if breaks:
            raise TakeError('files: atStep closes the window, and an agent drives one window: copy the files before the editor opens the project')
        steps.append(settle)
    for at in sorted(set(breaks)):
        steps += script_steps_of(window[start:at - 1], counter)
        scripts.append(steps)
        steps = [{'command': 'scene.open', 'parameters': {'scene': scene, 'force': True}},
                 {'command': 'scene.loadStatus', 'parameters': {'wait': True}}] if scene else []
        start = at - 1
    steps += script_steps_of(window[start:], counter)
    if not settle_first:
        steps.append(settle)
    panel = fields['editorWindow'].get('panel')
    parameters = {'path': path, 'overwrite': True}
    expect = {'/settled': {'equals': True}}
    if panel:
        steps.append({'command': 'editor.showPanel', 'parameters': {'panel': panel}})
        parameters = dict({'panel': panel}, **parameters)
    else:
        width, height = window_size(fields)
        expect.update({'/width': {'equals': width}, '/height': {'equals': height}})
    steps.append({'command': 'editor.screenshot', 'parameters': parameters, 'expect': expect})
    return scripts + [steps]


def run_window_client(take, window, steps, name, project, root, client):
    """Runs an editor figure's steps as an agent would (plan/pipelines.md §5.5, "Automation figures"): the editor in a
    window serves automation, with its session file in a new private session folder; StrataCLI mcp, given that folder,
    names itself client in initialize, reaches the editor and sends every step through strata_call, keeping its
    connection to the screenshot; then editor.quit. Returns the editor's output; TakeError when a step or the editor
    fails. The tool never reads the session folder, so the token passes through no output or log of its own."""
    session = editor.new_session_dir()
    env = neutral_environment(editor.environment(take.build, take.work, session), root)
    arguments = editor.window_arguments(take.build, window) + (['--project', project] if project else []) + ['--idle-timeout', str(editor.c_IdleSeconds)]
    program = editor.Program(arguments, env, take.log, 'window-' + name)
    agent = None
    failure = None
    try:
        agent = editor.McpClient(take.build, env, take.log, client, project)
        agent.initialize()
        agent.wait_for_editor(editor.c_OpenSeconds, program.alive)
        if project:
            agent.call('scene.loadStatus', {'wait': True}, timeout=editor.c_OpenSeconds)
        script_steps.run_steps(agent, steps, {})
        agent.call('editor.quit', {'force': True}, timeout=60)
    except (TakeError, editor.EditorError) as error:
        failure = error
    finally:
        if agent is not None:
            agent.close()
        if failure is not None and program.alive():
            editor.end_process_tree(program.pid)
        try:
            code, output = program.finish(editor.c_QuitSeconds)
        finally:
            shutil.rmtree(session, ignore_errors=True)
    if failure is not None:
        raise TakeError('the agent %s stopped: %s (the editor\'s output and every request are in %s)' % (client, failure, take.log.folder))
    if code != 0:
        raise TakeError('the editor driven by the agent %s exited with %d: %s' % (client, code, editor.last_line(output)))
    return output


def run_window(take, window, script, name, project, path=None, shown=None, root=None, automation=False):
    """Runs a command script in an editor in a window, on the project (none: the launcher), without automation unless
    automation (then it serves on the free loopback port it picks, its session file in a private session folder);
    returns the editor's output (its log); TakeError when it fails. path is where the script is written, shown the path
    the editor is given for it, root the drive the editor sees its folder as (map_drive), whose Editor folder holds its
    recent projects and script builds."""
    path = path or os.path.join(take.work, 'scripts', name + '.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_json(path, script)
    arguments = editor.window_arguments(take.build, window) + ([] if automation else ['--no-automation']) + (['--project', project] if project else []) + [
        '--commands', shown or path, '--quit-after-commands']
    session = editor.new_session_dir()
    env = editor.environment(take.build, take.work, session)
    try:
        code, output, _ = editor.run_program(arguments, neutral_environment(env, root) if root else env, take.log, 'window-' + name, editor.c_OpenSeconds)
    finally:
        shutil.rmtree(session, ignore_errors=True)
    if code != 0:
        problems = [line for line in output.splitlines() if 'error' in line.lower() or 'failed' in line.lower() or 'expected' in line.lower()]
        raise TakeError('the window\'s command script %s stopped (StrataEditor exit code %d): %s' % (
            take.layout.relative(path) if path.startswith(take.layout.root) else path, code, (problems or [editor.last_line(output)])[-1].strip()))
    return output


def map_drive(folder, work=None):
    """(the root a program is shown folder as, release()) for a take's neutral paths (plan/pipelines.md §5.4): on
    Windows the first free letter of c_DriveLetters, mapped to folder by subst and removed by release; mappings that a
    stopped take left on folders of work are removed first. Elsewhere a link /tmp/strata-figures-<pid> to folder."""
    folder = os.path.abspath(folder)
    if os.name != 'nt':
        link = '/tmp/strata-figures-%d' % os.getpid()
        if os.path.lexists(link):
            os.unlink(link)
        os.symlink(folder, link)
        return link + os.sep, lambda: os.path.lexists(link) and os.unlink(link)
    if work:
        for letter, target in subst_mappings().items():
            if os.path.normcase(target).startswith(os.path.normcase(os.path.abspath(work)) + os.sep):
                subprocess.run(['subst', letter + ':', '/D'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for letter in c_DriveLetters:
        root = letter + ':\\'
        if os.path.exists(root):
            continue
        subprocess.run(['subst', letter + ':', folder], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.normcase(subst_mappings().get(letter, '')) == os.path.normcase(folder) and os.path.isdir(root):
            return root, lambda letter=letter: subprocess.run(['subst', letter + ':', '/D'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raise TakeError('no drive letter of %s is free for subst, which shows the editor its folder as a drive of its own: free one (subst <letter>: /D)'
                    % ', '.join(c_DriveLetters))


def subst_mappings():
    """{letter: folder} of the drives subst maps (its listing, "S:\\: => G:\\folder")."""
    result = subprocess.run(['subst'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    found = {}
    for line in result.stdout.decode('mbcs' if os.name == 'nt' else 'utf-8', 'replace').splitlines():
        match = re.match(r'^([A-Za-z]):\\: => (.+?)\s*$', line)
        if match:
            found[match.group(1).upper()] = match.group(2)
    return found


def neutral_environment(env, root):
    """The environment of a program shown its folder as root: its recent projects and script builds on that drive too."""
    env = dict(env)
    env['STRATA_RECENT_PROJECTS'] = root + os.path.join(c_NeutralEditor, 'RecentProjects.json')
    env['STRATA_SCRIPT_BUILDS_DIR'] = root + os.path.join(c_NeutralEditor, 'ScriptBuilds')
    return env


def project_folder(project):
    """The name of an editor figure's project copy in the drive's Projects folder: what the Export dialog and the title
    show (the sample's id; the name project.create gives a template's or a lab's copy)."""
    if 'sample' in project:
        return project['sample']
    if project.get('lookdev'):
        return 'LookDev'
    return 'Lab' if 'lab' in project else 'Figures'


def write_neutral_layout(source, target, location):
    """A window's layout: the recipe's (source) with the location the New Project and Open Sample dialogs suggest
    (ProjectDialogs' [StrataLauncher][Settings] ProjectLocation, which the editor keeps in its layout file) set to
    location, the drive's Projects folder, in place of the user's home folder."""
    with open(source, encoding='utf-8', errors='replace') as file:
        text = file.read().replace('\r\n', '\n')
    text = c_LauncherSettings.sub('', text).rstrip('\n')
    repo.write_text(target, text + '\n\n[StrataLauncher][Settings]\nProjectLocation=%s\n' % location)


def take_editor(take, session, recipe, variant, fields, scene, shot):
    """An editor figure (plan/pipelines.md §5.4): the project copy the session made with the recipe's files (none for
    the launcher), then one editor in a window that runs the figure's command script (editor_scripts) and quits, and one
    more after each step its files are copied before (atStep). The window sees the figure's folder as a drive of its own
    (map_drive): the copy, the layout, the script and the screenshot, so that no path of the machine reaches its log or
    its picture; a log that names the work folder or the user's home fails the figure. The PNG the editor wrote is the
    original."""
    session.quit()  # the copy is made; the window's editor opens it
    stem = picture_stem(recipe, variant)
    folder = take.drive_folder
    tools = os.path.join(folder, c_NeutralEditor)
    os.makedirs(tools, exist_ok=True)
    screenshot = os.path.join(tools, 'Screenshot.png')
    items = recipe_files(take, recipe, variant, fields)
    copy_project_files(take, [item for item in items if not item.at])
    breaks = sorted({item.at for item in items if item.at})
    root, release = map_drive(folder, work=take.work)
    shown = lambda path: root + os.path.relpath(path, folder)
    try:
        layout_file = os.path.join(tools, 'Layout.ini')
        write_neutral_layout(take.window['layout'], layout_file, root + c_NeutralProjects)
        window = {'size': take.window['size'], 'layout': shown(layout_file)}
        automation = fields.get('automation')
        client = automation.get('client') if isinstance(automation, dict) else None
        scripts = editor_scripts(take, recipe, variant, fields, scene, shot, shown(screenshot), breaks, settle_first=bool(client))
        project = shown(take.project_directory) if take.project_directory else None
        for number, script in enumerate(scripts):
            if number:
                copy_project_files(take, [item for item in items if item.at == breaks[number - 1]])
            name = stem if len(scripts) == 1 else '%s-%d' % (stem, number + 1)
            path = os.path.join(tools, name + '.json')
            if client:
                write_json(path, script)  # what the agent sent, for the photographer
                output = run_window_client(take, window, script, name, project, root, client)
            else:
                output = run_window(take, window, script, name, project, path, shown(path), root, automation=bool(automation))
            problem = privacy_problem(output, take.work, 'the editor\'s log')
            if problem:
                raise TakeError('%s in "%s": the picture may show it; give the editor paths on its drive (plan/pipelines.md §5.4)' % problem)
    finally:
        release()
    if not os.path.isfile(screenshot):
        raise TakeError('the editor wrote no picture into %s: look at its output in %s' % (screenshot, take.log.folder))
    path = os.path.join(take.work, 'shots', stem + '.png')
    shutil.copyfile(screenshot, path)
    take.picture(recipe, variant, None, 'editor', data=read_bytes(path))


def provisional_line(status, pin):
    reported = (status or {}).get('engineCommit')
    if isinstance(reported, str) and reported and reported != 'unknown' and pin.startswith(reported):
        return 'figures: provisional: the build reports the pin\'s commit %s; publish still refuses this take' % reported
    return 'figures: provisional: the build reports the engine commit %s, not the pin %s: the commit check is skipped; publish refuses this take' % (
        reported, pin[:12])


def make_layout(layout, pin, build, work, name, size, provisional):
    """layouts/<name>.ini: the layout an editor in a window of size pixels makes on a new basic3d project, with the first
    line that names the window. Returns (the file, the commit check's status)."""
    prepare_work(work)
    log = editor.Log(os.path.join(work, 'log'))
    folder = os.path.join(work, 'layouts')
    os.makedirs(folder, exist_ok=True)
    kept = os.path.join(folder, name + '.ini')
    session = editor.Editor(build, work, log)
    runner = Take(layout, None, pin, build, work, log)
    runner.project_directory = os.path.join(work, 'projects', '01')
    try:
        session.launch()
        status = session.check_commit(pin, provisional)
        make_project(session, {'template': 'basic3d'}, runner.project_directory, os.path.join(layout.root, 'labs'))
    finally:
        session.quit()
    run_window(runner, {'size': size, 'layout': kept}, [{'command': 'editor.wait', 'parameters': {'frames': c_EditorSettleFrames}}], 'layout-' + name,
               runner.project_directory)
    if not os.path.isfile(kept):
        raise TakeError('the editor wrote no layout into %s: look at its output in %s' % (kept, log.folder))
    with open(kept, encoding='utf-8', errors='replace') as file:
        lines = [line for line in file.read().replace('\r\n', '\n').split('\n') if not line.startswith(';')]
    header = '; Strata editor layout for a window of %dx%d pixels at UI scale 1 (tools/figures.py layout, engine %s)' % (
        size[0], size[1], status.get('engineCommit'))
    target = os.path.join(layout.root, 'layouts', name + '.ini')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    repo.write_text(target, '\n'.join([header] + lines).rstrip('\n') + '\n')
    return target, status


# ---------------------------------------------------------------------------------------------------------------------
# publish.

def encoder_command():
    """The program publish encodes with: node scripts/encode-figures.mjs (the tests give a stand-in)."""
    node = shutil.which('node')
    if not node:
        raise UsageError('node is not on the PATH: source .tools/env.sh first (the encoder is the site\'s pinned sharp)')
    return [node, c_Encoder]


def run_encoder(arguments, folder):
    result = subprocess.run(encoder_command() + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder)
    errors = result.stderr.decode('utf-8', 'replace').strip()
    if result.returncode == 2 or 'Cannot find' in errors or 'ERR_MODULE_NOT_FOUND' in errors:
        raise UsageError('the encoder could not run: %s' % (errors.splitlines()[-1] if errors else 'exit code %d' % result.returncode))
    if result.returncode != 0:
        raise TakeError(errors or 'the encoder failed')
    return json.loads(result.stdout.decode('utf-8'))


def publish(layout, source, pattern, accept):
    """Publishes a take; returns {published, unchanged, restamped, checked, candidates, skipped, problems}."""
    pending_path = os.path.join(source, 'taken-pending.json')
    if not os.path.isfile(pending_path):
        raise UsageError('%s has no taken-pending.json: publish the work folder of a take' % source)
    with open(pending_path, encoding='utf-8') as file:
        pending = json.load(file)
    if pending.get('provisional'):
        raise UsageError('%s was taken with --provisional (a build that is not the pin\'s): publish refuses it; take the figures again at the pin'
                         % source)
    recipes = {(recipe.page, recipe.id): recipe for recipe in load_recipes(layout)}
    compared = compare_ids(layout)
    placements = placed_pictures(layout, recipes.values())
    outcome = {'published': [], 'unchanged': [], 'restamped': [], 'checked': [], 'candidates': [], 'skipped': [], 'problems': []}
    takens = {}
    originals = os.path.join(layout.root, 'originals')
    for stem, item in sorted(pending.get('pictures', {}).items()):
        recipe = recipes.get((item['page'], item['figure']))
        if recipe is None:
            outcome['problems'].append('%s: the take names %s/%s, which no manifest holds now' % (pending_path, item['page'], item['figure']))
            continue
        if not matches_figures(recipe, pattern):
            continue
        variant, crop = item.get('variant'), item.get('crop')
        if recipe.kind not in ('text', 'diagram') and not picture_placed(placements.get(recipe.page, set()), recipe.id, variant, crop):
            if crop:
                outcome['skipped'].append('%s-%s.webp: no page places the crop %s of %s' % (recipe.stem(variant), crop, crop, recipe.id))
            else:
                outcome['skipped'].append('%s%s: no page places %s' % (recipe.stem(variant), recipe.extension(), 'the variant %s of %s' % (variant, recipe.id)
                                                                         if variant else recipe.id))
            continue
        if item['kind'] == 'text':
            original = os.path.join(source, 'text', stem + '.txt')
        else:
            original = os.path.join(source, 'crops' if crop else 'shots', stem + '.png')
        if not os.path.isfile(original):
            outcome['problems'].append('%s: the original is missing (%s)' % (stem, original))
            continue
        digest = sha256_file(original)
        if digest != item['sha256']:
            outcome['problems'].append('%s: the original differs from taken-pending.json (%s): take it again' % (stem, original))
            continue
        folder = os.path.join(layout.pictures, *recipe.page.split('/'))
        taken = takens.setdefault(recipe.page, Taken(layout, recipe.page))
        if taken.problem:
            raise UsageError('%s: %s' % taken.problem)
        name = (recipe.stem(variant) + ('-' + crop if crop else '')) + ('.webp' if crop else recipe.extension())
        target = os.path.join(folder, name)
        record = taken.files.get(name)
        if record and record['original'] == digest:
            # The same original: the file and its hashes stay, and the stamp tells of this take, at which pin it was made
            # and what it measured (plan/pipelines.md §5.7, "Retakes").
            restamped = restamp(record, item, crop)
            if restamped == record:
                outcome['unchanged'].append(name)
                continue
            taken.files[name] = restamped
            outcome['restamped'].append('%s (the same original, taken at %s)' % (name, item['pin'][:12]))
            write_result(source, folder, recipe, variant, stem, crop)
            continue
        os.makedirs(folder, exist_ok=True)
        stamp = {key: item.get(key) for key in ('kind', 'pin', 'build', 'reportedCommit', 'os', 'gpu', 'size')}
        stamp.update({'figure': recipe.id, 'variant': variant, 'crop': crop, 'original': digest, 'recorded': item.get('recorded') or {}, 'checkedAt': []})
        if item.get('pairDifference') and not crop:
            stamp['pairDifference'] = item['pairDifference']
        if item.get('renderer'):
            stamp['renderer'] = item['renderer']
        if item['kind'] == 'text':
            shutil.copyfile(original, target)
            stamp.update({'sha256': sha256_file(target), 'encoder': None, 'size': None})
            taken.files[name] = stamp
            outcome['published'].append(name)
        else:
            mode, quality = encoder_settings(recipe, recipe.entry, crop, recipe.id in compared.get(recipe.page, set()))
            arguments = ['encode', '--publish', mode] + (['--quality', str(quality)] if quality else []) + ['--effort', str(c_Effort)]
            with tempfile.TemporaryDirectory(prefix='publish-') as scratch:
                encoded = os.path.join(scratch, name)
                settings = run_encoder(arguments + [original, encoded], layout.root)
                stamp['encoder'] = {key: settings[key] for key in ('format', 'lossless', 'quality', 'chromaSubsampling', 'effort', 'sharp', 'libvips') if key in settings}
                stamp['size'] = [settings['width'], settings['height']]
                if record and os.path.isfile(target):
                    difference = run_encoder(['diff', target, encoded], layout.root)
                    above = difference['mean'] > c_MeanThreshold or difference['largestBlockMean'] > c_BlockThreshold
                    if not above:
                        record['checkedAt'] = sorted(set(record.get('checkedAt', [])) | {item['pin']})
                        outcome['checked'].append('%s (mean %.3f, largest block %.2f)' % (name, difference['mean'], difference['largestBlockMean']))
                        continue
                    if not accept:
                        candidates = os.path.join(source, 'candidates', *recipe.page.split('/'))
                        os.makedirs(candidates, exist_ok=True)
                        shutil.copyfile(encoded, os.path.join(candidates, name))
                        outcome['candidates'].append('%s (mean %.3f, largest block %.2f): judge it, then publish with --accept --figures %s/%s' % (
                            name, difference['mean'], difference['largestBlockMean'], recipe.page, recipe.id))
                        continue
                shutil.copyfile(encoded, target)
            stamp['sha256'] = sha256_file(target)
            taken.files[name] = stamp
            os.makedirs(originals, exist_ok=True)
            kept_original = os.path.join(originals, digest + '.png')
            if not os.path.isfile(kept_original):
                shutil.copyfile(original, kept_original)
            outcome['published'].append(name)
        write_result(source, folder, recipe, variant, stem, crop)
    for taken in takens.values():
        taken.save()
    return outcome


c_TakeFields = ('kind', 'pin', 'build', 'reportedCommit', 'os', 'gpu')


def restamp(record, item, crop):
    """A stamp whose original is the take's: the take's pin, build, machine and recorded values, with the file's hashes,
    size and encoder kept; the take's pin leaves checkedAt."""
    stamp = dict(record)
    stamp.update({key: item.get(key) for key in c_TakeFields})
    stamp['recorded'] = item.get('recorded') or {}
    for key, value in (('pairDifference', None if crop else item.get('pairDifference')), ('renderer', item.get('renderer'))):
        if value:
            stamp[key] = value
        else:
            stamp.pop(key, None)
    stamp['checkedAt'] = [pin for pin in record.get('checkedAt', []) if pin != item.get('pin')]
    return stamp


def write_result(source, folder, recipe, variant, stem, crop):
    """<figure>[-<variant>].result.json: the capture's result of the take, without its image (not for a crop)."""
    result = os.path.join(source, 'results', stem + '.json')
    if not crop and os.path.isfile(result):
        with open(result, encoding='utf-8') as file:
            data = json.load(file)
        if isinstance(data, dict):
            data.pop('Image', None)
        write_json(os.path.join(folder, recipe.stem(variant) + '.result.json'), data)


# ---------------------------------------------------------------------------------------------------------------------
# archive, compare, list.

def stamped_originals(layout):
    """{sha256} of every original a stamp names (not text figures)."""
    found = set()
    if not os.path.isdir(layout.pictures):
        return found
    for path in glob.glob(os.path.join(layout.pictures, '**', c_TakenFile), recursive=True):
        page = os.path.relpath(os.path.dirname(path), layout.pictures).replace(os.sep, '/')
        taken = Taken(layout, page)
        if taken.problem:
            raise UsageError('%s: %s' % taken.problem)
        for record in taken.files.values():
            if record.get('kind') != 'text':
                found.add(record['original'])
    return found


def archive(layout, tag):
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9._-]*$', tag):
        raise UsageError('--tag %s: a tag of this repository, such as book-v0.8.1' % tag)
    wanted = sorted(stamped_originals(layout))
    originals = os.path.join(layout.root, 'originals')
    missing = [digest for digest in wanted if not os.path.isfile(os.path.join(originals, digest + '.png'))]
    if missing:
        return None, ['originals/%s.png is missing (a stamp names it): read it from the latest release\'s archive' % digest for digest in missing]
    total = sum(os.path.getsize(os.path.join(originals, digest + '.png')) + 1024 for digest in wanted) + 1024
    if total > c_ArchiveLimit:
        return None, ['the originals come to %d bytes, more than the archive\'s 1 GB' % total]
    target = os.path.join(layout.root, 'release', 'strata-engine-docs-originals-%s.tar' % tag)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    partial = target + '.partial'
    with tarfile.open(partial, 'w', format=tarfile.USTAR_FORMAT) as tar:
        for digest in wanted:
            path = os.path.join(originals, digest + '.png')
            info = tarfile.TarInfo('originals/%s.png' % digest)
            info.size = os.path.getsize(path)
            info.mtime = 0
            info.mode = 0o644
            with open(path, 'rb') as file:
                tar.addfile(info, file)
    if os.path.getsize(partial) > c_ArchiveLimit:
        os.remove(partial)
        return None, ['the archive would be larger than 1 GB']
    os.replace(partial, target)
    # Its SHA-256 beside it, in sha256sum's form, for the owner who attaches both to the release (rulings-6, R26).
    repo.write_text(target + '.sha256', '%s  %s\n' % (sha256_file(target), os.path.basename(target)))
    return target, []


def compare(layout, engine, after, output):
    if not os.path.isfile(os.path.join(after, 'taken-pending.json')) or not os.path.isdir(os.path.join(after, 'shots')):
        raise UsageError('--after %s is not the work folder of a take (taken-pending.json, shots/)' % after)
    for root, label in ((layout.root, 'the book\'s repository'), (engine.path, 'the engine clone')):
        if os.path.normcase(os.path.abspath(output)).startswith(os.path.normcase(os.path.abspath(root)) + os.sep):
            # Inside the folder is allowed only where the folder's own repository ignores the path (.tools/, originals/).
            top = subprocess.run(['git', '-C', root, 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            own = top.returncode == 0 and os.path.normcase(os.path.abspath(top.stdout.decode('utf-8', 'replace').strip())) == os.path.normcase(os.path.abspath(root))
            ignored = own and subprocess.run(['git', '-C', root, 'check-ignore', '-q', os.path.abspath(output)], stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL).returncode == 0
            if not ignored:
                raise UsageError('--output %s is inside %s\'s tracked tree: choose a folder outside it' % (output, label))
    with open(os.path.join(after, 'taken-pending.json'), encoding='utf-8') as file:
        pending = json.load(file).get('pictures', {})
    current = {}
    for path in glob.glob(os.path.join(layout.pictures, '**', c_TakenFile), recursive=True):
        page = os.path.relpath(os.path.dirname(path), layout.pictures).replace(os.sep, '/')
        for name, record in Taken(layout, page).files.items():
            current[(page, record['figure'], record.get('variant'), record.get('crop'))] = record
    before = tempfile.mkdtemp(prefix='figures-before-')
    try:
        for folder in ('shots', 'crops'):
            os.makedirs(os.path.join(before, folder))
        laid = 0
        for stem, item in pending.items():
            if item['kind'] == 'text':
                continue
            record = current.get((item['page'], item['figure'], item.get('variant'), item.get('crop')))
            if not record:
                continue
            original = os.path.join(layout.root, 'originals', record['original'] + '.png')
            if not os.path.isfile(original):
                raise UsageError('originals/%s.png (the stamp of %s) is missing: read it from the latest release\'s archive' % (record['original'], stem))
            shutil.copyfile(original, os.path.join(before, 'crops' if item.get('crop') else 'shots', stem + '.png'))
            laid += 1
        script = os.path.join(engine.path, 'Tools', 'LookDev.py')
        result = subprocess.run([sys.executable, '-I', script, 'compare', before, after, '--output', output], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.returncode, result.stdout.decode('utf-8', 'replace'), laid
    finally:
        shutil.rmtree(before, ignore_errors=True)


def figure_states(layout):
    """(recipe, [(file name, state)], waits) of every figure. list reads no engine, so the crops a shot supplies are
    listed once taken.json stamps them; a recipe's own crops are listed always."""
    rows = []
    recipes = load_recipes(layout)
    placements = placed_pictures(layout, recipes)
    for recipe in recipes:
        taken = Taken(layout, recipe.page)
        folder = os.path.join(layout.pictures, *recipe.page.split('/'))
        waits = sorted({fields['waitsFor'] for _, fields in recipe.variants() if fields.get('waitsFor')})
        blocked = any(fields.get('blocked') for _, fields in recipe.variants())
        states = []
        # A figure no take makes at the pin lists its pictures whole: what waits or is blocked, placed or not.
        files = promised_files(recipe, None, None if waits or blocked else placements.get(recipe.page, set()))
        for name, record in taken.files.items():
            if record.get('figure') == recipe.id and name not in files:
                files[name] = (record.get('variant'), record.get('crop'))
        for name, (variant, crop) in sorted(files.items()):
            if not os.path.isfile(os.path.join(folder, name)):
                state = 'waiting' if waits else 'blocked' if blocked else 'missing'
            elif recipe.kind == 'diagram' or name in taken.files:
                state = 'taken'
            else:
                state = 'placeholder'
            states.append((name, state))
        rows.append((recipe, states, waits))
    return rows


# ---------------------------------------------------------------------------------------------------------------------

def default_work(layout, tool):
    """The work folder beside the clone: <parent of the clone>/docs-work/<tool> (plan/pipelines.md §2)."""
    return os.path.join(os.path.dirname(layout.root), 'docs-work', tool)


def open_engine(path, layout):
    try:
        engine = repo.Engine(path)
        pin = engine.resolve(repo.read_pin(layout.pin_file)['commit'])
    except repo.EngineError as error:
        raise UsageError('%s (pipelines.md §1.4, check 1)' % error)
    return engine, pin


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='The book\'s figures: recipes, takes, published pictures and their stamps (plan/pipelines.md §5).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['check', 'take', 'layout', 'compare', 'publish', 'archive', 'fill', 'list', 'labs'])
    parser.add_argument('names', nargs='*', help='fill: page ids; labs: lab names (default: all); layout: the layout\'s name')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--build', help='take: the pin build\'s bin/Release folder')
    parser.add_argument('--dumps', help='check: reference/_dumps/<pin>')
    parser.add_argument('--baselines', help='check, take: the folder of the look-dev baseline sets')
    parser.add_argument('--release', action='store_true', help='check: pictures not taken, placeholders and missing stamps are errors')
    parser.add_argument('--work', help='take: the work folder (default: docs-work/figures beside the clone)')
    parser.add_argument('--figures', help='take, publish: only the figures whose <page>/<id> matches this glob')
    parser.add_argument('--kinds', help='take: the kinds to take, comma separated (default: all of them)')
    parser.add_argument('--provisional', action='store_true', help='take, layout: a build that is not the pin\'s: skip the commit check, take the '
                        'figures that wait for an addition of §11, and keep publish from publishing the take')
    parser.add_argument('--window-size', help='layout: the editor\'s window, <width>x<height> pixels')
    parser.add_argument('--after', help='compare: the work folder of the new take')
    parser.add_argument('--output', help='compare: where LookDev.py compare writes')
    parser.add_argument('--from', dest='source', help='publish: the work folder of a take')
    parser.add_argument('--accept', action='store_true', help='publish: put the candidates --figures names in place')
    parser.add_argument('--tag', help='archive: the book release\'s tag')
    parser.add_argument('--waits', action='store_true', help='list: group the waiting figures by the addition they wait for')
    parser.add_argument('--quiet', action='store_true', help='check: print errors only')
    options = parser.parse_args(argv)
    layout = repo.Layout(options.root)
    engine = None
    try:
        if options.command == 'check':
            if not options.dumps:
                parser.error('check needs --dumps reference/_dumps/<pin>')
            engine, pin = open_engine(options.engine, layout)
            report = check(layout, engine, pin, options.dumps, options.baselines, options.release)
            for where, message in report.errors:
                print('%s: %s' % (where, message))
            if not options.quiet:
                for where, message in report.notes:
                    print('%s: note: %s' % (where, message))
            print('figures: %d error%s, %d note%s%s' % (len(report.errors), '' if len(report.errors) == 1 else 's', len(report.notes),
                                                         '' if len(report.notes) == 1 else 's', ' (release)' if options.release else ''))
            return 1 if report.errors else 0
        if options.command == 'take':
            kinds = [kind.strip() for kind in (options.kinds or ','.join(c_TakeKinds)).split(',') if kind.strip()]
            unknown = [kind for kind in kinds if kind not in c_TakeKinds]
            if unknown:
                parser.error('--kinds: %s; the kinds are %s' % (', '.join(unknown), ', '.join(c_TakeKinds)))
            if options.baselines:
                raise UsageError('--baselines gives the "before" pictures of scene figures, which take does not copy yet (pipelines.md §5.5): '
                                 'take leaves out the variants with baseline and reports them')
            engine, pin = open_engine(options.engine, layout)
            editor.preflight_clone(engine, pin)
            if any(kind in kinds for kind in c_EditorKinds):
                editor.preflight_build(options.build, ('StrataEditor', 'StrataCLI'))
            work = os.path.abspath(options.work or default_work(layout, 'figures'))
            runner = take(layout, engine, pin, options.build, work, options.figures, kinds, options.provisional)
            if options.provisional and runner.status:
                print(provisional_line(runner.status, pin))
            for line in runner.notes + runner.skipped + runner.failures:
                print(line)
            print('figures: took %d file%s into %s; %d failed, %d skipped%s' % (len(runner.pending), '' if len(runner.pending) == 1 else 's', work,
                                                                                len(runner.failures), len(runner.skipped),
                                                                                '; every command and its answer are in %s' % os.path.join(work, 'log')
                                                                                if runner.failures else ''))
            return 1 if runner.failures else 0
        if options.command == 'layout':
            if len(options.names) != 1 or not c_LayoutName.match(options.names[0]):
                raise UsageError('layout takes one name of lowercase words joined by "-" (layouts/<name>.ini)')
            size = parse_window_size(options.window_size)
            engine, pin = open_engine(options.engine, layout)
            editor.preflight_clone(engine, pin)
            editor.preflight_build(options.build, ('StrataEditor', 'StrataCLI'))
            work = os.path.abspath(options.work or default_work(layout, 'layouts'))
            target, status = make_layout(layout, pin, options.build, work, options.names[0], size, options.provisional)
            if status.get('provisional'):
                print(provisional_line(status, pin))
            print('figures: wrote %s (the editor\'s default layout for a window of %dx%d; arrange it further by editing the file\'s '
                  '[Docking] sizes, then look at a take)' % ((layout.relative(target),) + tuple(size)))
            return 0
        if options.command == 'compare':
            if not options.after or not options.output:
                parser.error('compare needs --after <work dir> and --output <dir>')
            engine, pin = open_engine(options.engine, layout)
            editor.preflight_clone(engine, pin)
            code, output, laid = compare(layout, engine, os.path.abspath(options.after), os.path.abspath(options.output))
            print(output.rstrip())
            print('figures: compared %d original%s with the take; LookDev.py exited with %d' % (laid, '' if laid == 1 else 's', code))
            return 0 if code == 0 else 1
        if options.command == 'publish':
            if not options.source:
                parser.error('publish needs --from <work dir>')
            outcome = publish(layout, os.path.abspath(options.source), options.figures, options.accept)
            for key in ('published', 'unchanged', 'restamped', 'checked', 'candidates', 'skipped', 'problems'):
                for line in outcome[key]:
                    print('%s: %s' % (key if key != 'problems' else 'failed', line))
            print('figures: %d published, %d unchanged, %d restamped, %d checked, %d candidate%s, %d skipped, %d failed' % (
                len(outcome['published']), len(outcome['unchanged']), len(outcome['restamped']), len(outcome['checked']), len(outcome['candidates']),
                '' if len(outcome['candidates']) == 1 else 's', len(outcome['skipped']), len(outcome['problems'])))
            return 1 if outcome['problems'] else 0
        if options.command == 'archive':
            if not options.tag:
                parser.error('archive needs --tag <tag>')
            target, problems = archive(layout, options.tag)
            for line in problems:
                print('figures: %s' % line)
            if target:
                print('figures: wrote %s (%d bytes)' % (layout.relative(target), os.path.getsize(target)))
            return 1 if problems else 0
        if options.command == 'fill':
            pages = dict(layout.pages())
            unknown = [name for name in options.names if name not in pages]
            if unknown:
                raise UsageError('not pages of the book: %s' % ', '.join(unknown))
            failures = 0
            for page, path in sorted(pages.items()):
                if options.names and page not in options.names:
                    continue
                text = repo.read_text(path)
                new_text, changed, problems = fill_text(text, layout, page)
                if changed:
                    repo.write_text(path, new_text)
                    print('%s: filled %d text figure%s' % (layout.relative(path), changed, '' if changed == 1 else 's'))
                for line, message in problems:
                    print('%s:%d: %s' % (layout.relative(path), line, message))
                failures += len(problems)
            return 1 if failures else 0
        if options.command == 'list':
            rows = figure_states(layout)
            if options.waits:
                grouped = {}
                for recipe, _, waits in rows:
                    for name in waits:
                        grouped.setdefault(name, []).append('%s/%s' % (recipe.page, recipe.id))
                for name in sorted(grouped):
                    print('%s (%s):' % (name, c_Additions.get(name, 'a capture of tier 3')))
                    for figure in grouped[name]:
                        print('  %s' % figure)
                return 0
            for recipe, states, waits in rows:
                print('%s\t%s\t%s\t%s%s' % (recipe.page, recipe.id, recipe.kind, ', '.join('%s %s' % item for item in states),
                                            '\twaits for ' + '; '.join(waits) if waits else ''))
            return 0
        if options.command == 'labs':
            folder = os.path.join(layout.root, 'labs')
            names = options.names or sorted(os.path.basename(path)[:-5] for path in glob.glob(os.path.join(folder, '*.json')))
            for name in names:
                if not os.path.isfile(os.path.join(folder, name + '.json')):
                    raise UsageError('labs/%s.json does not exist' % name)
                target = os.path.join(layout.root, 'public', 'downloads', 'labs', name + '.zip')
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, 'wb') as file:
                    file.write(lab_zip(layout, name))
                print('figures: wrote %s' % layout.relative(target))
            return 0
    except (UsageError, editor.PreflightError, ValueError, OSError, jsonschema.SchemaError) as error:
        print('figures: %s' % error, file=sys.stderr)
        return 2
    except TakeError as error:
        print('figures: %s' % error, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
