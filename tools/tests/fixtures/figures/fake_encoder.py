"""A stand-in for scripts/encode-figures.mjs in the tests of tools/figures.py publish, which must run without node.

    python fake_encoder.py encode --publish <lossy|lossless> [--quality <n>] --effort <n> <png> <output>
    python fake_encoder.py diff <published file> <published file>

encode writes a tiny file of the right format and size (AVIF boxes or a lossless WebP header) that carries the grey
level of the PNG's first pixel, and prints the settings as encode-figures.mjs does. diff prints a mean of a tenth of the
difference of the two grey levels (and the same for the largest block), so that tests choose a retake below or above
the thresholds by the grey levels they draw.
"""

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from booklib import images  # noqa: E402


def box(kind, body):
    return struct.pack('>I4s', 8 + len(body), kind) + body


def avif(width, height, grey):
    ispe = box(b'ispe', b'\0\0\0\0' + struct.pack('>II', width, height))
    ipma = box(b'ipma', b'\0\0\0\0' + struct.pack('>I', 1) + struct.pack('>H', 1) + bytes([1, 0x81]))
    meta = box(b'meta', b'\0\0\0\0' + box(b'pitm', b'\0\0\0\0' + struct.pack('>H', 1)) + box(b'iprp', box(b'ipco', ispe) + ipma))
    return box(b'ftyp', b'avif\0\0\0\0avifmif1') + meta + box(b'mdat', bytes([grey]) * 8)


def webp(width, height, grey):
    body = b'\x2f' + ((width - 1) | ((height - 1) << 14)).to_bytes(4, 'little') + bytes([grey]) * 8
    return b'RIFF' + struct.pack('<I', 4 + 8 + len(body)) + b'WEBP' + b'VP8L' + struct.pack('<I', len(body)) + body


def grey_of(data):
    return data[-1]


def main(argv):
    command = argv[0]
    if command == 'encode':
        options = {}
        files = []
        index = 1
        while index < len(argv):
            if argv[index].startswith('--'):
                options[argv[index][2:]] = argv[index + 1]
                index += 2
            else:
                files.append(argv[index])
                index += 1
        source, output = files
        with open(source, 'rb') as file:
            image = images.read_png(file.read())
        grey = image.data[0]
        if options['publish'] == 'lossy':
            data = avif(image.width, image.height, grey)
            settings = {'format': 'avif', 'lossless': False, 'quality': int(options.get('quality', 80)), 'chromaSubsampling': '4:4:4'}
        else:
            data = webp(image.width, image.height, grey)
            settings = {'format': 'webp', 'lossless': True}
        settings.update({'effort': int(options['effort']), 'sharp': '0.0.0-test', 'libvips': '0.0.0-test', 'width': image.width,
                         'height': image.height, 'bytes': len(data)})
        with open(output, 'wb') as file:
            file.write(data)
        print(json.dumps(settings))
        return 0
    if command == 'diff':
        with open(argv[1], 'rb') as file:
            first = grey_of(file.read())
        with open(argv[2], 'rb') as file:
            second = grey_of(file.read())
        mean = abs(first - second) / 10
        print(json.dumps({'mean': mean, 'largestBlockMean': mean, 'width': 1, 'height': 1}))
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
