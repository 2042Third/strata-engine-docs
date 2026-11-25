"""booklib.images: PNG files read and written, PPM images, crops at a picture's own pixels, and the sizes of PNG, WebP,
AVIF and SVG files."""

import os
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402,F401 (helpers puts tools/ on the path)
from booklib import images


def gradient(width, height, channels=3):
    data = bytearray()
    for y in range(height):
        for x in range(width):
            data += bytes([(x * 7 + y) & 255, (y * 5) & 255, (x ^ y) & 255, 200][:channels])
    return images.Image(width, height, channels, data)


def filtered_png(image, filters):
    """A PNG whose rows use the given filter types (the encoder of the tool writes filter 0 only)."""
    stride = image.width * image.channels
    raw = bytearray()
    prior = bytes(stride)
    for y in range(image.height):
        row = image.data[y * stride:(y + 1) * stride]
        kind = filters[y % len(filters)]
        out = bytearray(stride)
        for index in range(stride):
            left = row[index - image.channels] if index >= image.channels else 0
            above = prior[index]
            corner = prior[index - image.channels] if index >= image.channels else 0
            predicted = {0: 0, 1: left, 2: above, 3: (left + above) >> 1, 4: images.predictor(left, above, corner)}[kind]
            out[index] = (row[index] - predicted) & 255
        raw.append(kind)
        raw += out
        prior = row
    color = {1: 0, 2: 4, 3: 2, 4: 6}[image.channels]
    return (images.c_PngSignature + images.chunk(b'IHDR', struct.pack('>IIBBBBB', image.width, image.height, 8, color, 0, 0, 0))
            + images.chunk(b'IDAT', zlib.compress(bytes(raw))) + images.chunk(b'IEND', b''))


def box(kind, body):
    return struct.pack('>I4s', 8 + len(body), kind) + body


def avif(width, height):
    """The boxes of an AVIF file that its size is read from: ftyp, and meta with pitm, iprp (ipco, ipma)."""
    ispe = box(b'ispe', b'\0\0\0\0' + struct.pack('>II', width, height))
    other = box(b'pixi', b'\0\0\0\0\x03\x08\x08\x08')
    ipco = box(b'ipco', other + ispe)
    ipma = box(b'ipma', b'\0\0\0\0' + struct.pack('>I', 1) + struct.pack('>H', 1) + bytes([2, 0x81, 0x02]))
    meta = box(b'meta', b'\0\0\0\0' + box(b'pitm', b'\0\0\0\0' + struct.pack('>H', 1)) + box(b'iprp', ipco + ipma))
    return box(b'ftyp', b'avif\0\0\0\0avifmif1') + meta + box(b'mdat', b'\0' * 8)


class ImageTests(unittest.TestCase):
    def test_png_files_round_trip_through_every_filter(self):
        for channels in (1, 2, 3, 4):
            image = gradient(13, 9, channels)
            for filters in ([0], [1], [2], [3], [4], [0, 1, 2, 3, 4]):
                read = images.read_png(filtered_png(image, filters))
                self.assertEqual((read.width, read.height, read.channels), (13, 9, channels))
                self.assertEqual(read.data, image.data, 'channels %d, filters %s' % (channels, filters))
            data = images.png_bytes(image)
            self.assertEqual(images.read_png(data).data, image.data)
            self.assertEqual(images.size_of(data), (13, 9))
            self.assertEqual(data, images.png_bytes(image))  # the same pixels give the same bytes
        with self.assertRaises(images.ImageError):
            images.read_png(b'not a picture')

    def test_crops_are_cut_at_the_picture_s_own_pixels(self):
        image = gradient(20, 10)
        rect = images.crop_rectangle([0.25, 0.3, 0.75, 0.9], 20, 10)
        self.assertEqual(rect, (5, 3, 15, 9))
        piece = image.crop(*rect)
        self.assertEqual((piece.width, piece.height), (10, 6))
        self.assertEqual(piece.data[:3], image.data[(3 * 20 + 5) * 3:(3 * 20 + 5) * 3 + 3])
        with self.assertRaises(images.ImageError):
            image.crop(15, 0, 25, 5)

    def test_ppm_images_from_a_sketch(self):
        image = images.read_ppm(b'P6\n# made by a sketch\n2 1\n255\n' + bytes([1, 2, 3, 4, 5, 6]))
        self.assertEqual((image.width, image.height, image.channels, bytes(image.data)), (2, 1, 3, bytes([1, 2, 3, 4, 5, 6])))
        for bad in (b'P3\n1 1\n255\n1 2 3', b'P6\n2 1\n65535\n' + bytes(12), b'P6\n2 1\n255\n' + bytes(5)):
            with self.assertRaises(images.ImageError):
                images.read_ppm(bad)
        with self.assertRaises(images.ImageError) as caught:
            images.read_ppm(b'P6\n2 1\n255\n' + bytes(5), 'the output of sketches/core-time-box.cpp')
        self.assertEqual(str(caught.exception), 'the output of sketches/core-time-box.cpp: 5 bytes of pixels, 6 expected for 2 x 1: write three '
                                                'bytes per pixel after the header, and nothing else')

    def test_a_sketch_s_image_as_the_windows_text_mode_wrote_it(self):
        # Pixels with "\n" (10) and "\r\n" (13, 10) in them, as a C++ program writes them on Windows: every "\n" becomes "\r\n".
        pixels = bytes([10, 10, 10, 13, 10, 0, 13, 200, 10])
        written = b'P6\n3 1\n255\n' + pixels
        translated = written.replace(b'\n', b'\r\n')
        image = images.read_sketch_ppm(translated, 'the output', True)
        self.assertEqual((image.width, image.height, bytes(image.data)), (3, 1, pixels))
        # Bytes that are an image as printed are taken as they are, and elsewhere nothing is undone.
        self.assertEqual(bytes(images.read_sketch_ppm(b'P6\n1 1\n255\n\r\n\0', 'the output', True).data), b'\r\n\0')
        with self.assertRaises(images.ImageError):
            images.read_sketch_ppm(translated, 'the output', False)
        # A lone "\n" means the program wrote in binary mode: its bytes are not changed, and the image's own fault is reported.
        with self.assertRaises(images.ImageError) as caught:
            images.read_sketch_ppm(b'P6\r\n2 1\r\n255\n' + bytes(5), 'the output', True)
        self.assertIn('5 bytes of pixels, 6 expected', str(caught.exception))

    def test_sizes_and_formats_of_published_files(self):
        lossless = b'RIFF\0\0\0\0WEBPVP8L' + b'\0\0\0\0' + b'\x2f' + ((1919) | (1079 << 14)).to_bytes(4, 'little') + b'\0' * 8
        self.assertEqual(images.size_of(lossless), (1920, 1080))
        self.assertTrue(images.webp_is_lossless(lossless))
        lossy = b'RIFF\0\0\0\0WEBPVP8 ' + struct.pack('<I', 10) + b'\0\0\0\x9d\x01\x2a' + struct.pack('<HH', 640, 360) + b'\0' * 4
        self.assertEqual(images.size_of(lossy), (640, 360))
        self.assertFalse(images.webp_is_lossless(lossy))
        self.assertEqual(images.size_of(avif(1920, 1080)), (1920, 1080))
        self.assertEqual(images.format_of(avif(4, 4)), 'avif')
        self.assertEqual(images.size_of(b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20"></svg>'), (40, 20))
        self.assertIsNone(images.webp_is_lossless(b'not webp'))
        with self.assertRaises(images.ImageError):
            images.size_of(b'GIF89a')


if __name__ == '__main__':
    unittest.main()
