"""Pictures with the standard library only: the size of a PNG, WebP, AVIF or SVG file from its header, PNG files read
and written (8 bits per channel, not interlaced), binary PPM images (what a reference sketch prints), and crops cut at a
picture's own pixels.

Encoding AVIF and WebP is not here: Python's standard library has no encoder for either, so tools/figures.py publish
calls scripts/encode-figures.mjs (sharp) for them (plan/pipelines.md §5.7).
"""

import re
import struct
import zlib

c_PngSignature = b'\x89PNG\r\n\x1a\n'
c_Channels = {0: 1, 2: 3, 4: 2, 6: 4}  # PNG colour type: channels (grey, RGB, grey and alpha, RGBA)


class ImageError(Exception):
    pass


class Image:
    """Pixels as rows of bytes: width, height, channels (1 to 4), data (bytearray, row after row)."""

    def __init__(self, width, height, channels, data=None):
        self.width = width
        self.height = height
        self.channels = channels
        self.data = data if data is not None else bytearray(width * height * channels)
        if len(self.data) != width * height * channels:
            raise ImageError('%d bytes of pixels for a %d x %d picture of %d channels' % (len(self.data), width, height, channels))

    def crop(self, x0, y0, x1, y1):
        """The pixels of [x0, x1) x [y0, y1), copied as they are."""
        if not (0 <= x0 < x1 <= self.width and 0 <= y0 < y1 <= self.height):
            raise ImageError('the rectangle %s is not inside the %d x %d picture' % ((x0, y0, x1, y1), self.width, self.height))
        stride = self.width * self.channels
        out = Image(x1 - x0, y1 - y0, self.channels)
        out_stride = out.width * self.channels
        for y in range(y0, y1):
            start = y * stride + x0 * self.channels
            out.data[(y - y0) * out_stride:(y - y0 + 1) * out_stride] = self.data[start:start + out_stride]
        return out


def crop_rectangle(rect, width, height):
    """The pixel rectangle (x0, y0, x1, y1) of a normalized [x0, y0, x1, y1] crop, cut as the engine's LookDev.py cuts
    its crops: each edge at int(fraction * size)."""
    x0, y0, x1, y1 = rect
    return int(x0 * width), int(y0 * height), int(x1 * width), int(y1 * height)


def predictor(a, b, c):
    """The predictor of PNG filter type 4 (the PNG specification, 9.4): of left, above and upper left, the one nearest
    to left + above - upper left."""
    estimate = a + b - c
    pa, pb, pc = abs(estimate - a), abs(estimate - b), abs(estimate - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def unfilter(kind, raw, prior, bpp):
    row = bytearray(raw)
    length = len(row)
    if kind == 0:
        return row
    if kind == 1:
        for index in range(bpp, length):
            row[index] = (row[index] + row[index - bpp]) & 255
        return row
    if kind == 2:
        return bytearray((value + above) & 255 for value, above in zip(raw, prior))
    if kind == 3:
        for index in range(length):
            left = row[index - bpp] if index >= bpp else 0
            row[index] = (row[index] + ((left + prior[index]) >> 1)) & 255
        return row
    if kind == 4:
        for index in range(length):
            left = row[index - bpp] if index >= bpp else 0
            corner = prior[index - bpp] if index >= bpp else 0
            row[index] = (row[index] + predictor(left, prior[index], corner)) & 255
        return row
    raise ImageError('unknown PNG filter type %d' % kind)


def read_png(data, name='the picture'):
    """An Image from the bytes of a PNG file with 8 bits per channel, not interlaced."""
    if not data.startswith(c_PngSignature):
        raise ImageError('%s is not a PNG file' % name)
    offset = len(c_PngSignature)
    header = None
    compressed = bytearray()
    while offset + 8 <= len(data):
        length, kind = struct.unpack('>I4s', data[offset:offset + 8])
        body = data[offset + 8:offset + 8 + length]
        if len(body) != length:
            raise ImageError('%s: a chunk runs past the end of the file' % name)
        if kind == b'IHDR':
            header = struct.unpack('>IIBBBBB', body)
        elif kind == b'IDAT':
            compressed += body
        elif kind == b'IEND':
            break
        offset += 12 + length
    if header is None:
        raise ImageError('%s: no IHDR chunk' % name)
    width, height, depth, color, _, _, interlace = header
    channels = c_Channels.get(color)
    if depth != 8 or channels is None or interlace != 0:
        raise ImageError('%s: only PNG files of 8 bits per channel (grey, RGB, with or without alpha) without interlacing '
                         'are read; this one has depth %d and colour type %d' % (name, depth, color))
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as error:
        raise ImageError('%s: %s' % (name, error))
    stride = width * channels
    if len(raw) != (stride + 1) * height:
        raise ImageError('%s: %d bytes of image data, %d expected' % (name, len(raw), (stride + 1) * height))
    image = Image(width, height, channels)
    prior = bytes(stride)
    for y in range(height):
        start = y * (stride + 1)
        row = unfilter(raw[start], raw[start + 1:start + 1 + stride], prior, channels)
        image.data[y * stride:(y + 1) * stride] = row
        prior = row
    return image


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)


def png_bytes(image):
    """The bytes of a PNG file of the image (no filter, so the same pixels always give the same bytes)."""
    color = {value: key for key, value in c_Channels.items()}.get(image.channels)
    if color is None:
        raise ImageError('a picture of %d channels cannot be written as PNG' % image.channels)
    stride = image.width * image.channels
    raw = bytearray()
    for y in range(image.height):
        raw.append(0)
        raw += image.data[y * stride:(y + 1) * stride]
    return (c_PngSignature + chunk(b'IHDR', struct.pack('>IIBBBBB', image.width, image.height, 8, color, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def read_ppm(data, name='the image'):
    """An RGB Image from a binary PPM (P6, maximum value 255): what a reference sketch writes to its output."""
    match = re.match(rb'P6(?:\s+|#[^\n]*\n)+(\d+)(?:\s+|#[^\n]*\n)+(\d+)(?:\s+|#[^\n]*\n)+(\d+)\s', data)
    if not match:
        raise ImageError('%s is not a binary PPM image: write "P6", the width, the height and 255, each followed by one space or '
                         'newline, then the pixels' % name)
    width, height, maximum = (int(match.group(number)) for number in (1, 2, 3))
    if maximum != 255:
        raise ImageError('%s: the maximum value is %d: write 255, so that each channel is one byte' % (name, maximum))
    if width < 1 or height < 1:
        raise ImageError('%s: %d x %d is not a picture: write a width and a height of at least 1' % (name, width, height))
    pixels = data[match.end():]
    if len(pixels) != width * height * 3:
        raise ImageError('%s: %d bytes of pixels, %d expected for %d x %d: write three bytes per pixel after the header, and nothing '
                         'else' % (name, len(pixels), width * height * 3, width, height))
    return Image(width, height, 3, bytearray(pixels))


def read_sketch_ppm(data, name, text_mode):
    """The PPM image a reference sketch printed to its standard output. On Windows (text_mode) the C runtime writes
    standard output in text mode and turns every "\\n" into "\\r\\n", which breaks a binary image. That change is undone
    exactly (each "\\r\\n" back to "\\n") when the bytes as printed are no image and every "\\n" follows a "\\r"."""
    try:
        return read_ppm(data, name)
    except ImageError:
        if not text_mode or b'\r\n' not in data or data.count(b'\n') != data.count(b'\r\n'):
            raise
    return read_ppm(data.replace(b'\r\n', b'\n'), name)


def boxes(data, start, end):
    """(type, body start, body end) of the ISO base media boxes in data[start:end]."""
    offset = start
    while offset + 8 <= end:
        size, kind = struct.unpack('>I4s', data[offset:offset + 8])
        header = 8
        if size == 1:
            if offset + 16 > end:
                return
            size = struct.unpack('>Q', data[offset + 8:offset + 16])[0]
            header = 16
        elif size == 0:
            size = end - offset
        if size < header or offset + size > end:
            return
        yield kind.decode('latin-1'), offset + header, offset + size
        offset += size


def avif_size(data):
    """(width, height) of the primary image of an AVIF file: its 'ispe' property, through 'pitm' and 'ipma'."""
    meta = next(((start, end) for kind, start, end in boxes(data, 0, len(data)) if kind == 'meta'), None)
    if meta is None:
        return None
    start, end = meta[0] + 4, meta[1]  # meta is a full box: version and flags first
    primary = None
    properties = []
    associations = {}
    for kind, body, stop in boxes(data, start, end):
        if kind == 'pitm':
            version = data[body]
            primary = struct.unpack('>H' if version == 0 else '>I', data[body + 4:body + (6 if version == 0 else 8)])[0]
        elif kind == 'iprp':
            for inner, inner_body, inner_stop in boxes(data, body, stop):
                if inner == 'ipco':
                    properties = list(boxes(data, inner_body, inner_stop))
                elif inner == 'ipma':
                    version, flags = data[inner_body], int.from_bytes(data[inner_body + 1:inner_body + 4], 'big')
                    position = inner_body + 4
                    count = struct.unpack('>I', data[position:position + 4])[0]
                    position += 4
                    for _ in range(count):
                        if version < 1:
                            item = struct.unpack('>H', data[position:position + 2])[0]
                            position += 2
                        else:
                            item = struct.unpack('>I', data[position:position + 4])[0]
                            position += 4
                        links = data[position]
                        position += 1
                        indexes = []
                        for _ in range(links):
                            if flags & 1:
                                value = struct.unpack('>H', data[position:position + 2])[0] & 0x7FFF
                                position += 2
                            else:
                                value = data[position] & 0x7F
                                position += 1
                            indexes.append(value)
                        associations[item] = indexes
    wanted = associations.get(primary, range(1, len(properties) + 1))
    for index in wanted:
        if 1 <= index <= len(properties):
            kind, body, _ = properties[index - 1]
            if kind == 'ispe':
                return struct.unpack('>II', data[body + 4:body + 12])
    return None


def svg_size(text):
    open_tag = re.search(r'<svg\b[^>]*>', text, re.IGNORECASE)
    if not open_tag:
        return None
    box = re.search(r'\sviewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*["\']', open_tag.group(0), re.IGNORECASE)
    if box:
        return round(float(box.group(1))), round(float(box.group(2)))
    width = re.search(r'\swidth\s*=\s*["\']([\d.]+)(?:px)?["\']', open_tag.group(0))
    height = re.search(r'\sheight\s*=\s*["\']([\d.]+)(?:px)?["\']', open_tag.group(0))
    if width and height:
        return round(float(width.group(1))), round(float(height.group(1)))
    return None


def size_of(data, name='the picture'):
    """(width, height) of a PNG, WebP, AVIF or SVG file's bytes, read from its header."""
    if data.startswith(c_PngSignature) and data[12:16] == b'IHDR':
        return struct.unpack('>II', data[16:24])
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        kind = data[12:16]
        if kind == b'VP8 ' and data[23:26] == b'\x9d\x01\x2a':
            width, height = struct.unpack('<HH', data[26:30])
            return width & 0x3FFF, height & 0x3FFF
        if kind == b'VP8L' and data[20:21] == b'\x2f':
            bits = int.from_bytes(data[21:25], 'little')
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if kind == b'VP8X':
            return int.from_bytes(data[24:27], 'little') + 1, int.from_bytes(data[27:30], 'little') + 1
    if data[4:8] == b'ftyp' and data[8:12] in (b'avif', b'avis'):
        found = avif_size(data)
        if found:
            return found
    if b'<svg' in data[:4096].lower():
        found = svg_size(data[:8192].decode('utf-8', 'replace'))
        if found:
            return found
    raise ImageError('%s is not a PNG, WebP, AVIF or SVG picture whose size can be read' % name)


def format_of(data):
    """'png', 'webp', 'avif', 'svg' or None."""
    if data.startswith(c_PngSignature):
        return 'png'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    if data[4:8] == b'ftyp' and data[8:12] in (b'avif', b'avis'):
        return 'avif'
    if b'<svg' in data[:4096].lower():
        return 'svg'
    return None


def webp_is_lossless(data):
    """True for a WebP file whose image is VP8L (lossless), False for VP8 (lossy), None when it is not a WebP file."""
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        return None
    for kind, _, _ in boxes_riff(data):
        if kind == 'VP8L':
            return True
        if kind == 'VP8 ':
            return False
    return None


def boxes_riff(data):
    offset = 12
    while offset + 8 <= len(data):
        kind = data[offset:offset + 4].decode('latin-1')
        size = struct.unpack('<I', data[offset + 4:offset + 8])[0]
        yield kind, offset + 8, offset + 8 + size
        offset += 8 + size + (size & 1)
