#! /usr/bin/env python

"""
print_views.py: Prints a two-dimensional view of a 3D bitmap on the console.
"""

import argparse
import fileinput
import re

import numpy as np

__author__ = "Igor Mironov"
__copyright__ = "Copyright 2019, Igor Mironov"
__license__ = "Apache v2.0"

ASPECT_REGEX = '(^[a-z]+)([+-][0-9]+)?$'  # view_name[rotation]

TOP_VIEW = 'top'
FRONT_VIEW = 'front'
RIGHT_VIEW = 'right'
BOTTOM_VIEW = 'bottom'
BACK_VIEW = 'back'
LEFT_VIEW = 'left'

DEFAULT_VIEW = FRONT_VIEW

VIEWS = [FRONT_VIEW, RIGHT_VIEW, TOP_VIEW, BACK_VIEW, LEFT_VIEW, BOTTOM_VIEW]

ROTATE_ACW_2 = '+180'  # rotate the image anticlockwise twice
ROTATE_ACW = '+90'
ROTATE_CW = '-90'
ROTATE_CW_2 = '-180'

ROTATIONS = [ROTATE_CW_2, ROTATE_CW, ROTATE_ACW, ROTATE_ACW_2]

# axes in a 3D bitmap (block array)
X = 2
Y = 1
Z = 0

TRANSPOSE = "transpose"

BOOLEAN_LIST_REGEX = '([01]+)b'  # boolean list literal in q


class StandardViewpoint(object):
    def __init__(self, view_axis, tweaks):
        self.view_axis = view_axis
        self.tweaks = tweaks

    def project(self, block, extra_tweaks=None):
        """Returns a parallel projection of a block along self.view_axis,
        optionally applying postprocessing tweaks (a sequence of flip and
        transpose operations). Because projections are parallel to the block's
        axes, there is no need to use a transform matrix, and the method
        apply_along_axis() does the job fine."""
        view = np.apply_along_axis(np.max, self.view_axis, block)

        if extra_tweaks is not None:
            combined_tweaks = []
            combined_tweaks.extend(self.tweaks)
            combined_tweaks.extend(extra_tweaks)
        else:
            combined_tweaks = self.tweaks

        for tweak in combined_tweaks:
            if tweak == TRANSPOSE:
                view = np.transpose(view)
            else:
                view = np.flip(view, tweak)
        return view


class Projector(object):
    def __init__(self):
        views = {TOP_VIEW: StandardViewpoint(Y, [0]),
                 FRONT_VIEW: StandardViewpoint(Z, []),
                 RIGHT_VIEW: StandardViewpoint(X, [TRANSPOSE, 1]),
                 BOTTOM_VIEW: StandardViewpoint(Y, []),
                 BACK_VIEW: StandardViewpoint(Z, [1]),
                 LEFT_VIEW: StandardViewpoint(X, [TRANSPOSE])}
        self.views = views
        self.aspect_re = re.compile(ASPECT_REGEX)
        self.rotation_tweaks = {ROTATE_CW_2: [0, 1], ROTATE_CW: [TRANSPOSE, 0],
                                ROTATE_ACW: [TRANSPOSE, 1],
                                ROTATE_ACW_2: [0, 1]}

    def get_view(self, view_name):
        if view_name in self.views:
            return self.views[view_name]
        raise RuntimeError(f'Unknown view name: "{view_name}"')

    def parse_aspect(self, aspect):
        if aspect is None:
            raise RuntimeError("No aspect")
        aspect_match = self.aspect_re.fullmatch(aspect)
        if aspect_match is None:
            raise RuntimeError(f"Couldn't parse aspect \"{aspect}\"")
        view_name = aspect_match.group(1)
        rotation = aspect_match.group(2)
        return view_name, rotation

    def project(self, block, aspect):
        view_name, rotation = self.parse_aspect(aspect)
        view = self.get_view(view_name)
        tweaks = self.get_rotation_tweaks(rotation)
        return view.project(block, tweaks)

    def get_images(self, block, view_spec, tiles=None):
        """Yields a flat (two-dimensional) ASCII rendition of the specified
        block, one per each aspect that has been passed in the view
        specifier (a string containing a space-separated list of aspects).
        Also allows the caller to specify custom tiles for blank and filled
        voxels in the block. By default the tiles are '  ' and 'XX',
        respectively."""
        if tiles is None:
            tiles = ['  ', 'XX']
        for aspect in view_spec.split():
            view = self.project(block, aspect)
            rows = np.flip(view, 0)
            yield "\n".join([''.join([tiles[c] for c in r]) for r in rows])

    def get_rotation_tweaks(self, rotation):
        """Obtains a list of primitive numpy operations (flip, transpose) that,
        when applied in order, result in an image that is rotated as indicated
        by the rotation parameter."""
        if rotation in self.rotation_tweaks:
            return self.rotation_tweaks[rotation]
        if rotation is None:
            return None
        raise RuntimeError(f'Unknown rotation: "{rotation}"')


def take_n(n, s):
    """Take n characters from string s"""
    m = len(s)  # the actual number of characters in s
    if m == n:
        return s
    a, b = divmod(n, m)  # repeat s 'a' times and add 'b' chars to get size n
    return s * a + s[:b]


def build_block(bits, dims):
    """Parse a string of 0/1 bits into a n-dimensional list of flags"""
    m = int(np.prod(dims))  # the number of bits required to cover dims
    s = take_n(m, bits)  # gets the string of the right size
    o = ord('0')
    a = np.asarray([ord(c) - o for c in s], dtype=np.uint8)
    return a.reshape(dims)


class BlockBuilder(object):

    def __init__(self, dims=None):
        self.dims = dims
        # a bitmap is a string of '0' and '1' characters ending with a 'b'
        self.bitmap_re = re.compile(BOOLEAN_LIST_REGEX)

    def block_dims(self, bits):
        if self.dims is not None:
            return self.dims
        n = len(bits)  # the number of bits in the bitmap
        # dimensions of the block -- for now assume it is a cube
        m = int(round(n ** (1. / 3)))
        return [m, m, m]

    def parse_blocks(self, line):
        for bitmap_match in self.bitmap_re.finditer(line):
            # the group as defined in re drops the 'b' keeping just the bits
            bits = bitmap_match.group(1)
            dims = self.block_dims(bits)
            yield build_block(bits, dims)


class Printer(object):
    def __init__(self):
        self.builder = BlockBuilder()
        self.projector = Projector()
        self.default_view = DEFAULT_VIEW
        self.image_spacer = "\n\n"

    def print_views(self, file_names, view_specs):
        if view_specs is None:
            view_specs = []  # no "TypeError: 'NoneType' object is not iterable"
        view_iter = iter(view_specs)  # should contain one view_spec per block
        view_spec = self.default_view

        continued = False
        for line in fileinput.input(file_names):
            blocks = self.builder.parse_blocks(line)
            for block in blocks:
                # preserve and use the last view_spec if view_specs is too short
                view_spec = next(view_iter, view_spec)

                for image in self.projector.get_images(block, view_spec):
                    if continued:
                        print(self.image_spacer)
                    else:
                        continued = True
                    print(image)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produces a two-dimensional' +
                                                 ' view of a 3D bitmap' +
                                                 ' on standard output.')
    parser.add_argument('-V', '--views', metavar='"VIEW [VIEW ...]"',
                        action='append',
                        help='draw the specified views' +
                             '; VIEW has the format NAME[ROT]' +
                             ' where NAME is one of ' + str(VIEWS) +
                             ' and ROT is one of ' + str(ROTATIONS) +
                             '; you can use multiple --views options' +
                             ' (one per each 3D bitmap)')
    parser.add_argument('files', nargs='*', metavar='FILE',
                        help='input file to read; use "-" for standard input')
    args = parser.parse_args()
    printer = Printer()
    printer.print_views(args.files, args.views)
